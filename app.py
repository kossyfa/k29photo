from flask import Flask, request, render_template, redirect, url_for, session, flash
import psycopg2
import psycopg2.extras
import base64

app = Flask(__name__)
app.secret_key = 'k29photo_secret_key'

# Σύνδεση με PostgreSQL
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "k29photo"
DB_USER = "k29"
DB_PASS = "1234"

def get_db():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    return conn

# Home
@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT p.photo_id, p.caption, a.owner_id,
               u.first_name, u.last_name
        FROM photos p
        JOIN albums a ON p.album_id = a.album_id
        JOIN users u ON a.owner_id = u.user_id
        ORDER BY p.photo_id DESC
    """)
    photos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', photos=photos)

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name  = request.form['last_name']
        email      = request.form['email']
        password   = request.form['password']
        hometown   = request.form.get('hometown', '')
        gender     = request.form.get('gender', '')
        dob        = request.form.get('dob') or None

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO users (first_name, last_name, email, password, hometown, gender, dob)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, email, password, hometown, gender, dob))
            conn.commit()
            flash('Εγγραφή επιτυχής! Μπορείς να συνδεθείς.', 'success')
            return redirect(url_for('login'))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash('Το email υπάρχει ήδη!', 'error')
        finally:
            cur.close()
            conn.close()

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s",
                    (email, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['user_id']   = user['user_id']
            session['user_name'] = user['first_name']
            flash(f'Καλωσήρθες, {user["first_name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Λάθος email ή κωδικός!', 'error')

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Αποσυνδέθηκες.', 'info')
    return redirect(url_for('index'))

# Serve Photo (επιστρέφει την εικόνα από τη βάση)
@app.route('/photo/img/<int:photo_id>')
def serve_photo(photo_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT data FROM photos WHERE photo_id = %s", (photo_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        return "Photo not found", 404

    from flask import Response
    return Response(bytes(row[0]), mimetype='image/jpeg')

# View Photo (σελίδα μιας φωτογραφίας)
@app.route('/photo/<int:photo_id>')
def view_photo(photo_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Φωτογραφία + owner
    cur.execute("""
        SELECT p.photo_id, p.caption, a.owner_id,
               u.first_name, u.last_name
        FROM photos p
        JOIN albums a ON p.album_id = a.album_id
        JOIN users u ON a.owner_id = u.user_id
        WHERE p.photo_id = %s
    """, (photo_id,))
    photo = cur.fetchone()

    if photo is None:
        cur.close()
        conn.close()
        return "Photo not found", 404

    # Tags
    cur.execute("""
        SELECT t.name FROM tags t
        JOIN photo_tags pt ON t.tag_id = pt.tag_id
        WHERE pt.photo_id = %s
    """, (photo_id,))
    tags = cur.fetchall()

    # Comments
    cur.execute("""
        SELECT c.text, c.post_date,
               u.first_name, u.last_name
        FROM comments c
        JOIN users u ON c.owner_id = u.user_id
        WHERE c.photo_id = %s
        ORDER BY c.post_date DESC
    """, (photo_id,))
    comments = cur.fetchall()

    # Likes
    cur.execute("""
        SELECT COUNT(*) as cnt FROM likes WHERE photo_id = %s
    """, (photo_id,))
    likes_count = cur.fetchone()['cnt']

    cur.close()
    conn.close()

    return render_template('photo.html',
                           photo=photo,
                           tags=tags,
                           comments=comments,
                           likes_count=likes_count)


# Photos by Tag
@app.route('/tag/<tag_name>')
def photos_by_tag(tag_name):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT p.photo_id, p.caption, u.first_name, u.last_name
        FROM photos p
        JOIN photo_tags pt ON p.photo_id = pt.photo_id
        JOIN tags t ON pt.tag_id = t.tag_id
        JOIN albums a ON p.album_id = a.album_id
        JOIN users u ON a.owner_id = u.user_id
        WHERE t.name = %s
    """, (tag_name,))
    photos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', photos=photos, tag=tag_name)

# Δημιουργία Album
@app.route('/album/new', methods=['GET', 'POST'])
def new_album():
    if 'user_id' not in session:
        flash('Πρέπει να συνδεθείς πρώτα!', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO albums (name, owner_id, date_created)
                VALUES (%s, %s, CURRENT_DATE)
                RETURNING album_id
            """, (name, session['user_id']))
            album_id = cur.fetchone()[0]
            conn.commit()
            flash('Το album δημιουργήθηκε!', 'success')
            return redirect(url_for('view_album', album_id=album_id))
        except Exception as e:
            conn.rollback()
            flash(f'Σφάλμα: {str(e)}', 'error')
        finally:
            cur.close()
            conn.close()

    return render_template('new_album.html')


# Προβολή Album
@app.route('/album/<int:album_id>')
def view_album(album_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT a.album_id, a.name, a.date_created,
               u.first_name, u.last_name, u.user_id
        FROM albums a
        JOIN users u ON a.owner_id = u.user_id
        WHERE a.album_id = %s
    """, (album_id,))
    album = cur.fetchone()

    if album is None:
        return "Album not found", 404

    cur.execute("""
        SELECT photo_id, caption FROM photos
        WHERE album_id = %s
    """, (album_id,))
    photos = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('album.html', album=album, photos=photos)


# Upload Photo
@app.route('/album/<int:album_id>/upload', methods=['GET', 'POST'])
def upload_photo(album_id):
    if 'user_id' not in session:
        flash('Πρέπει να συνδεθείς πρώτα!', 'error')
        return redirect(url_for('login'))

    # Έλεγχος ότι το album ανήκει στον χρήστη
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT owner_id FROM albums WHERE album_id = %s", (album_id,))
    album = cur.fetchone()

    if album is None or album['owner_id'] != session['user_id']:
        flash('Δεν έχεις δικαίωμα!', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        caption = request.form['caption']
        tags_input = request.form.get('tags', '').strip()
        photo_file = request.files['photo']
        photo_data = photo_file.read()

        try:
            cur2 = conn.cursor()
            # Εισαγωγή φωτογραφίας
            cur2.execute("""
                INSERT INTO photos (caption, data, album_id)
                VALUES (%s, %s, %s)
                RETURNING photo_id
            """, (caption, psycopg2.Binary(photo_data), album_id))
            photo_id = cur2.fetchone()[0]

            # Εισαγωγή tags
            if tags_input:
                tags_list = [t.strip().lower() for t in tags_input.split(',') if t.strip()]
                for tag_name in tags_list:
                    # Βρες ή δημιούργησε το tag
                    cur2.execute("""
                        INSERT INTO tags (name) VALUES (%s)
                        ON CONFLICT (name) DO NOTHING
                    """, (tag_name,))
                    cur2.execute("SELECT tag_id FROM tags WHERE name = %s", (tag_name,))
                    tag_id = cur2.fetchone()[0]
                    cur2.execute("""
                        INSERT INTO photo_tags (photo_id, tag_id) VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, (photo_id, tag_id))

            conn.commit()
            flash('Η φωτογραφία ανέβηκε!', 'success')
            return redirect(url_for('view_photo', photo_id=photo_id))
        except Exception as e:
            conn.rollback()
            flash(f'Σφάλμα: {str(e)}', 'error')
        finally:
            cur.close()
            conn.close()

    cur.close()
    conn.close()
    return render_template('upload_photo.html', album_id=album_id)


# Τα Albums μου
@app.route('/my-albums')
def my_albums():
    if 'user_id' not in session:
        flash('Πρέπει να συνδεθείς πρώτα!', 'error')
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT a.album_id, a.name, a.date_created,
               COUNT(p.photo_id) as photo_count
        FROM albums a
        LEFT JOIN photos p ON a.album_id = p.album_id
        WHERE a.owner_id = %s
        GROUP BY a.album_id
        ORDER BY a.date_created DESC
    """, (session['user_id'],))
    albums = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('my_albums.html', albums=albums)


if __name__ == '__main__':
    app.run(debug=True)
