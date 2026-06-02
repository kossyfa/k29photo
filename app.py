from flask import Flask, request, render_template, redirect, url_for, session, flash, Response
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = 'k29photo_secret_key'

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

# ─────────────────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name  = request.form['last_name']
        email      = request.form['email']
        password   = request.form['password']
        hometown   = request.form.get('hometown', '')
        gender     = request.form.get('gender', '') or None
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
            cur.close(); conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close(); conn.close()

        if user:
            session['user_id']   = user['user_id']
            session['user_name'] = user['first_name']
            flash(f'Καλωσήρθες, {user["first_name"]}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Λάθος email ή κωδικός!', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Αποσυνδέθηκες.', 'info')
    return redirect(url_for('index'))

# ─────────────────────────────────────────────────────────
# PHOTOS
# ─────────────────────────────────────────────────────────
@app.route('/photo/img/<int:photo_id>')
def serve_photo(photo_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT data FROM photos WHERE photo_id = %s", (photo_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if row is None:
        return "Photo not found", 404
    return Response(bytes(row[0]), mimetype='image/jpeg')


@app.route('/photo/<int:photo_id>')
def view_photo(photo_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT p.photo_id, p.caption, a.owner_id, a.album_id,
               u.first_name, u.last_name
        FROM photos p
        JOIN albums a ON p.album_id = a.album_id
        JOIN users u ON a.owner_id = u.user_id
        WHERE p.photo_id = %s
    """, (photo_id,))
    photo = cur.fetchone()
    if photo is None:
        cur.close(); conn.close()
        return "Photo not found", 404

    cur.execute("""
        SELECT t.name FROM tags t
        JOIN photo_tags pt ON t.tag_id = pt.tag_id
        WHERE pt.photo_id = %s
    """, (photo_id,))
    tags = cur.fetchall()

    # LEFT JOIN για να εμφανίζονται και guest comments (NULL owner)
    cur.execute("""
        SELECT c.comment_id, c.text, c.post_date,
               u.first_name, u.last_name, c.owner_id
        FROM comments c
        LEFT JOIN users u ON c.owner_id = u.user_id
        WHERE c.photo_id = %s
        ORDER BY c.post_date DESC
    """, (photo_id,))
    comments = cur.fetchall()

    cur.execute("SELECT COUNT(*) as cnt FROM likes WHERE photo_id = %s", (photo_id,))
    likes_count = cur.fetchone()['cnt']

    cur.execute("""
        SELECT u.user_id, u.first_name, u.last_name
        FROM likes l JOIN users u ON l.user_id = u.user_id
        WHERE l.photo_id = %s
    """, (photo_id,))
    likers = cur.fetchall()

    user_liked = False
    if session.get('user_id'):
        cur.execute("SELECT 1 FROM likes WHERE user_id=%s AND photo_id=%s",
                    (session['user_id'], photo_id))
        user_liked = cur.fetchone() is not None

    cur.close(); conn.close()
    return render_template('photo.html', photo=photo, tags=tags,
                           comments=comments, likes_count=likes_count,
                           likers=likers, user_liked=user_liked)


@app.route('/photo/<int:photo_id>/delete', methods=['POST'])
def delete_photo(photo_id):
    if 'user_id' not in session:
        flash('Πρέπει να συνδεθείς πρώτα!', 'error')
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT a.owner_id, p.album_id FROM photos p
        JOIN albums a ON p.album_id = a.album_id
        WHERE p.photo_id = %s
    """, (photo_id,))
    row = cur.fetchone()

    if row is None or row['owner_id'] != session['user_id']:
        flash('Δεν έχεις δικαίωμα!', 'error')
        cur.close(); conn.close()
        return redirect(url_for('index'))

    album_id = row['album_id']
    cur2 = conn.cursor()
    cur2.execute("DELETE FROM photos WHERE photo_id = %s", (photo_id,))
    conn.commit()
    cur.close(); cur2.close(); conn.close()
    flash('Η φωτογραφία διαγράφηκε.', 'success')
    return redirect(url_for('view_album', album_id=album_id))

# ─────────────────────────────────────────────────────────
# ALBUMS
# ─────────────────────────────────────────────────────────
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
                VALUES (%s, %s, CURRENT_DATE) RETURNING album_id
            """, (name, session['user_id']))
            album_id = cur.fetchone()[0]
            conn.commit()
            flash('Το album δημιουργήθηκε!', 'success')
            return redirect(url_for('view_album', album_id=album_id))
        except Exception as e:
            conn.rollback()
            flash(f'Σφάλμα: {str(e)}', 'error')
        finally:
            cur.close(); conn.close()

    return render_template('new_album.html')


@app.route('/album/<int:album_id>')
def view_album(album_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT a.album_id, a.name, a.date_created,
               u.first_name, u.last_name, u.user_id
        FROM albums a JOIN users u ON a.owner_id = u.user_id
        WHERE a.album_id = %s
    """, (album_id,))
    album = cur.fetchone()
    if album is None:
        return "Album not found", 404

    cur.execute("SELECT photo_id, caption FROM photos WHERE album_id = %s", (album_id,))
    photos = cur.fetchall()
    cur.close(); conn.close()
    return render_template('album.html', album=album, photos=photos)


@app.route('/album/<int:album_id>/delete', methods=['POST'])
def delete_album(album_id):
    if 'user_id' not in session:
        flash('Πρέπει να συνδεθείς πρώτα!', 'error')
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT owner_id FROM albums WHERE album_id = %s", (album_id,))
    album = cur.fetchone()

    if album is None or album['owner_id'] != session['user_id']:
        flash('Δεν έχεις δικαίωμα!', 'error')
        cur.close(); conn.close()
        return redirect(url_for('index'))

    cur2 = conn.cursor()
    cur2.execute("DELETE FROM albums WHERE album_id = %s", (album_id,))
    conn.commit()
    cur.close(); cur2.close(); conn.close()
    flash('Το album διαγράφηκε.', 'success')
    return redirect(url_for('my_albums'))


@app.route('/album/<int:album_id>/upload', methods=['GET', 'POST'])
def upload_photo(album_id):
    if 'user_id' not in session:
        flash('Πρέπει να συνδεθείς πρώτα!', 'error')
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT owner_id, name FROM albums WHERE album_id = %s", (album_id,))
    album = cur.fetchone()

    if album is None or album['owner_id'] != session['user_id']:
        flash('Δεν έχεις δικαίωμα!', 'error')
        cur.close(); conn.close()
        return redirect(url_for('index'))

    if request.method == 'POST':
        caption    = request.form['caption']
        tags_input = request.form.get('tags', '').strip()
        photo_data = request.files['photo'].read()

        try:
            cur2 = conn.cursor()
            cur2.execute("""
                INSERT INTO photos (caption, data, album_id)
                VALUES (%s, %s, %s) RETURNING photo_id
            """, (caption, psycopg2.Binary(photo_data), album_id))
            photo_id = cur2.fetchone()[0]

            if tags_input:
                for tag_name in [t.strip().lower() for t in tags_input.split(',') if t.strip()]:
                    cur2.execute("INSERT INTO tags (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (tag_name,))
                    cur2.execute("SELECT tag_id FROM tags WHERE name = %s", (tag_name,))
                    tag_id = cur2.fetchone()[0]
                    cur2.execute("INSERT INTO photo_tags (photo_id, tag_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                                 (photo_id, tag_id))

            conn.commit()
            flash('Η φωτογραφία ανέβηκε!', 'success')
            return redirect(url_for('view_photo', photo_id=photo_id))
        except Exception as e:
            conn.rollback()
            flash(f'Σφάλμα: {str(e)}', 'error')
        finally:
            cur.close(); conn.close()
        return redirect(url_for('view_album', album_id=album_id))

    cur.close(); conn.close()
    return render_template('upload_photo.html', album_id=album_id, album_name=album['name'])


@app.route('/my-albums')
def my_albums():
    if 'user_id' not in session:
        flash('Πρέπει να συνδεθείς πρώτα!', 'error')
        return redirect(url_for('login'))

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT a.album_id, a.name, a.date_created,
               COUNT(p.photo_id) as photo_count,
               MIN(p.photo_id) as cover_photo_id
        FROM albums a LEFT JOIN photos p ON a.album_id = p.album_id
        WHERE a.owner_id = %s
        GROUP BY a.album_id ORDER BY a.date_created DESC
    """, (session['user_id'],))
    albums = cur.fetchall()
    cur.close(); conn.close()
    return render_template('my_albums.html', albums=albums)

# ─────────────────────────────────────────────────────────
# TAGS
# ─────────────────────────────────────────────────────────
@app.route('/tag/<tag_name>')
def photos_by_tag(tag_name):
    view_mine = request.args.get('mine', '0')
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if view_mine == '1' and session.get('user_id'):
        cur.execute("""
            SELECT p.photo_id, p.caption, u.first_name, u.last_name
            FROM photos p
            JOIN photo_tags pt ON p.photo_id = pt.photo_id
            JOIN tags t ON pt.tag_id = t.tag_id
            JOIN albums a ON p.album_id = a.album_id
            JOIN users u ON a.owner_id = u.user_id
            WHERE t.name = %s AND a.owner_id = %s
        """, (tag_name, session['user_id']))
    else:
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
    cur.close(); conn.close()
    return render_template('photos_by_tag.html', photos=photos,
                           tag=tag_name, view_mine=view_mine)


@app.route('/tags')
def popular_tags():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT t.name, COUNT(pt.photo_id) as cnt
        FROM tags t JOIN photo_tags pt ON t.tag_id = pt.tag_id
        GROUP BY t.name ORDER BY cnt DESC LIMIT 20
    """)
    tags = cur.fetchall()
    cur.close(); conn.close()
    return render_template('popular_tags.html', tags=tags)

# ─────────────────────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────────────────────
@app.route('/search')
def search():
    query  = request.args.get('q', '').strip()
    photos = []
    if query:
        tag_list = query.lower().split()
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT p.photo_id, p.caption, u.first_name, u.last_name
            FROM photos p
            JOIN albums a ON p.album_id = a.album_id
            JOIN users u ON a.owner_id = u.user_id
            WHERE p.photo_id IN (
                SELECT pt.photo_id FROM photo_tags pt
                JOIN tags t ON pt.tag_id = t.tag_id
                WHERE t.name = ANY(%s)
                GROUP BY pt.photo_id
                HAVING COUNT(DISTINCT t.name) = %s
            )
        """, (tag_list, len(tag_list)))
        photos = cur.fetchall()
        cur.close(); conn.close()
    return render_template('search.html', photos=photos, query=query)

# ─────────────────────────────────────────────────────────
# COMMENTS
# ─────────────────────────────────────────────────────────
@app.route('/photo/<int:photo_id>/comment', methods=['POST'])
def post_comment(photo_id):
    text = request.form.get('text', '').strip()
    if not text:
        flash('Το σχόλιο δεν μπορεί να είναι κενό!', 'error')
        return redirect(url_for('view_photo', photo_id=photo_id))

    owner_id = session.get('user_id')  # None αν είναι guest

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO comments (text, owner_id, photo_id, post_date)
            VALUES (%s, %s, %s, NOW())
        """, (text, owner_id, photo_id))
        conn.commit()
        flash('Το σχόλιο δημοσιεύτηκε!', 'success')
    except Exception as e:
        conn.rollback()
        flash(str(e), 'error')
    finally:
        cur.close(); conn.close()

    return redirect(url_for('view_photo', photo_id=photo_id))


@app.route('/comments/search')
def search_comments():
    query = request.args.get('q', '').strip()
    results = []
    guest_results = []
    if query:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # Registered users με τις φωτό τους
        cur.execute("""
            SELECT u.user_id, u.first_name, u.last_name,
                   COUNT(*) as match_count,
                   array_agg(c.photo_id) as photo_ids,
                   array_agg(p.caption) as captions
            FROM comments c
            JOIN users u ON c.owner_id = u.user_id
            JOIN photos p ON c.photo_id = p.photo_id
            WHERE c.text = %s
            GROUP BY u.user_id, u.first_name, u.last_name
            ORDER BY match_count DESC
        """, (query,))
        results = cur.fetchall()
        # Guest comments με τις φωτό τους
        cur.execute("""
            SELECT c.photo_id, p.caption
            FROM comments c
            JOIN photos p ON c.photo_id = p.photo_id
            WHERE c.text = %s AND c.owner_id IS NULL
        """, (query,))
        guest_results = cur.fetchall()
        cur.close(); conn.close()
    return render_template('search_comments.html', results=results,
                           guest_results=guest_results, query=query)

# ─────────────────────────────────────────────────────────
# LIKES
# ─────────────────────────────────────────────────────────
@app.route('/photo/<int:photo_id>/like', methods=['POST'])
def like_photo(photo_id):
    if 'user_id' not in session:
        flash('Πρέπει να συνδεθείς για να κάνεις like!', 'error')
        return redirect(url_for('view_photo', photo_id=photo_id))

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO likes (user_id, photo_id) VALUES (%s, %s)",
                    (session['user_id'], photo_id))
        conn.commit()
        flash('❤️ Like!', 'success')
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        flash('Έχεις ήδη κάνει like!', 'info')
    except Exception as e:
        conn.rollback()
        flash(str(e), 'error')
    finally:
        cur.close(); conn.close()

    return redirect(url_for('view_photo', photo_id=photo_id))

# ─────────────────────────────────────────────────────────
# FRIENDS
# ─────────────────────────────────────────────────────────
@app.route('/friend/add/<int:friend_id>')
def add_friend(friend_id):
    if 'user_id' not in session:
        flash('Πρέπει να συνδεθείς πρώτα!', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    if user_id == friend_id:
        flash('Δεν μπορείς να προσθέσεις τον εαυτό σου!', 'error')
        return redirect(url_for('profile', user_id=friend_id))

    id1, id2 = min(user_id, friend_id), max(user_id, friend_id)
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO friends (user_id1, user_id2) VALUES (%s, %s)", (id1, id2))
        conn.commit()
        flash('Ο φίλος προστέθηκε!', 'success')
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        flash('Είστε ήδη φίλοι!', 'info')
    except Exception as e:
        conn.rollback()
        flash(str(e), 'error')
    finally:
        cur.close(); conn.close()

    return redirect(url_for('profile', user_id=friend_id))


@app.route('/user/<int:user_id>/friends')
def user_friends(user_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT first_name, last_name FROM users WHERE user_id = %s", (user_id,))
    owner = cur.fetchone()

    cur.execute("""
        SELECT u.user_id, u.first_name, u.last_name, u.hometown
        FROM friends f
        JOIN users u ON (
            CASE WHEN f.user_id1 = %s THEN f.user_id2 ELSE f.user_id1 END = u.user_id
        )
        WHERE f.user_id1 = %s OR f.user_id2 = %s
    """, (user_id, user_id, user_id))
    friends = cur.fetchall()
    cur.close(); conn.close()
    return render_template('friends.html', friends=friends, owner=owner, user_id=user_id)


@app.route('/users/search')
def search_users():
    query   = request.args.get('q', '').strip()
    results = []
    if query:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
            SELECT user_id, first_name, last_name, hometown
            FROM users
            WHERE LOWER(first_name) LIKE %s OR LOWER(last_name) LIKE %s
              OR LOWER(email) LIKE %s
        """, (f'%{query.lower()}%', f'%{query.lower()}%', f'%{query.lower()}%'))
        results = cur.fetchall()
        cur.close(); conn.close()
    return render_template('search_users.html', results=results, query=query)

# ─────────────────────────────────────────────────────────
# PROFILE & TOP USERS
# ─────────────────────────────────────────────────────────
@app.route('/user/<int:user_id>')
def profile(user_id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    if user is None:
        return "User not found", 404

    cur.execute("""
        SELECT a.album_id, a.name, a.date_created,
               COUNT(p.photo_id) as photo_count,
               MIN(p.photo_id) as cover_photo_id
        FROM albums a LEFT JOIN photos p ON a.album_id = p.album_id
        WHERE a.owner_id = %s
        GROUP BY a.album_id ORDER BY a.date_created DESC
    """, (user_id,))
    albums = cur.fetchall()

    cur.execute("""
        SELECT
            (SELECT COUNT(*) FROM photos p JOIN albums a ON p.album_id=a.album_id
             WHERE a.owner_id = %s) +
            (SELECT COUNT(*) FROM comments c
             JOIN photos p ON c.photo_id=p.photo_id
             JOIN albums a ON p.album_id=a.album_id
             WHERE c.owner_id = %s AND a.owner_id != %s)
        AS score
    """, (user_id, user_id, user_id))
    score = cur.fetchone()['score']

    is_friend = False
    if session.get('user_id') and session['user_id'] != user_id:
        id1, id2 = min(session['user_id'], user_id), max(session['user_id'], user_id)
        cur.execute("SELECT 1 FROM friends WHERE user_id1=%s AND user_id2=%s", (id1, id2))
        is_friend = cur.fetchone() is not None

    # Friend recommendations (friends-of-friends)
    recommendations = []
    if session.get('user_id') == user_id:
        cur.execute("""
            WITH my_friends AS (
                SELECT CASE WHEN user_id1=%s THEN user_id2 ELSE user_id1 END as fid
                FROM friends WHERE user_id1=%s OR user_id2=%s
            )
            SELECT u.user_id, u.first_name, u.last_name, COUNT(*) as common
            FROM my_friends mf
            JOIN friends f ON (f.user_id1=mf.fid OR f.user_id2=mf.fid)
            JOIN users u ON (
                CASE WHEN f.user_id1=mf.fid THEN f.user_id2 ELSE f.user_id1 END = u.user_id
            )
            WHERE u.user_id != %s
              AND u.user_id NOT IN (SELECT fid FROM my_friends)
            GROUP BY u.user_id, u.first_name, u.last_name
            ORDER BY common DESC
            LIMIT 5
        """, (user_id, user_id, user_id, user_id))
        recommendations = cur.fetchall()

    # You-may-also-like
    may_also_like = []
    if session.get('user_id') == user_id:
        cur.execute("""
            SELECT t.name FROM photos p
            JOIN albums a ON p.album_id = a.album_id
            JOIN photo_tags pt ON p.photo_id = pt.photo_id
            JOIN tags t ON pt.tag_id = t.tag_id
            WHERE a.owner_id = %s
            GROUP BY t.name ORDER BY COUNT(*) DESC LIMIT 5
        """, (user_id,))
        top_tags = [row['name'] for row in cur.fetchall()]

        if top_tags:
            cur.execute("""
                SELECT p.photo_id, p.caption, u.first_name, u.last_name,
                       COUNT(DISTINCT t.name) as match_count,
                       COUNT(DISTINCT pt_all.tag_id) as total_tags
                FROM photos p
                JOIN albums a ON p.album_id = a.album_id
                JOIN users u ON a.owner_id = u.user_id
                JOIN photo_tags pt ON p.photo_id = pt.photo_id
                JOIN tags t ON pt.tag_id = t.tag_id
                JOIN photo_tags pt_all ON p.photo_id = pt_all.photo_id
                WHERE t.name = ANY(%s) AND a.owner_id != %s
                GROUP BY p.photo_id, p.caption, u.first_name, u.last_name
                ORDER BY match_count DESC, total_tags ASC
                LIMIT 10
            """, (top_tags, user_id))
            may_also_like = cur.fetchall()

    cur.close(); conn.close()
    return render_template('profile.html', user=user, albums=albums, score=score,
                           is_friend=is_friend, recommendations=recommendations,
                           may_also_like=may_also_like)


@app.route('/top-users')
def top_users():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT u.user_id, u.first_name, u.last_name,
            (SELECT COUNT(*) FROM photos p JOIN albums a ON p.album_id=a.album_id
             WHERE a.owner_id = u.user_id) +
            (SELECT COUNT(*) FROM comments c
             JOIN photos p ON c.photo_id=p.photo_id
             JOIN albums a ON p.album_id=a.album_id
             WHERE c.owner_id = u.user_id AND a.owner_id != u.user_id)
        AS score
        FROM users u
        ORDER BY score DESC LIMIT 10
    """)
    users = cur.fetchall()
    cur.close(); conn.close()
    return render_template('top_users.html', users=users)


if __name__ == '__main__':
    app.run(debug=True)