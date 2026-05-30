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


if __name__ == '__main__':
    app.run(debug=True)
