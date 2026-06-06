#!/usr/bin/env python3
"""
Script για φόρτωση πραγματικών δεδομένων στη βάση k29photo.
python3 load_data.py
Οι εικόνες πρέπει να βρίσκονται στον φάκελο images/
"""
import psycopg2
import psycopg2.extras
import os

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "k29photo"
DB_USER = "k29"
DB_PASS = "1234"

PHOTOS = [
    # Ταξίδια & Φύση / Sunset
    ("mountain-camping.jpg", "Camping στα βουνά",         ["nature", "mountain", "camping", "sunset", "travel"]),  
    ("sunset.jpg",           "Ηλιοβασίλεμα στη θάλασσα", ["sunset", "sea", "nature", "travel"]),                  
    ("car-sunset.jpg",       "Road trip sunset",          ["sunset", "travel", "roadtrip", "car"]),               
    ("airplane.jpg",         "Πτήση στα σύννεφα",         ["travel", "airplane", "sunset", "sky"]),               
    ("photography.jpg",      "Photography moment",        ["photography", "nature", "travel", "sunset"]),         
    ("road-trip.jpg",        "Road trip με χάρτη",        ["travel", "roadtrip", "friends", "adventure"]),        
    # City Life / Music
    ("metro.jpg",            "Metro rush",                ["city", "travel", "night", "urban"]),                  
    ("city-people.jpg",      "City crossing",             ["city", "urban", "travel", "people"]),                 
    ("concert.jpg",          "Concert night",             ["music", "concert", "friends", "night"]),              
    # Animals
    ("cat.jpg",              "Γάτα στο φως",              ["cat", "animals", "golden", "aesthetic"]),            
    ("cat-shadow.jpg",       "Γάτα σκιά",                 ["cat", "animals", "aesthetic", "cozy"]),               
    # City Vibes
    ("iced-coffee.jpg",      "Iced coffee downtown",      ["coffee", "city", "aesthetic", "urban"]),              
    ("work-coffee.jpg",      "Work & coffee",             ["coffee", "city", "work", "aesthetic"]),               
    # Study & Coffee
    ("study-outdoors.jpg",   "Study session outdoors",    ["study", "aesthetic", "nature", "coffee"]),            
    ("workspace.jpg",        "Cozy workspace",            ["aesthetic", "study", "cozy", "interior"]),            
    ("study-coffee.jpg",     "Study cafe vibes",          ["study", "coffee", "aesthetic", "city"]),              
]

# Users: (first_name, last_name, email, password, hometown, gender)
USERS = [
    ("Θεοδώρα", "Κόσσυφα",       "kossyfatheo@uoa.gr",  "pass1", "Αθήνα",         "F"),
    ("Νίκος",   "Αντωνίου",      "antoniounik@uoa.gr",      "pass2", "Θεσσαλονίκη",   "M"),
    ("Μαρία",   "Γεωργίου",      "georgioum@uoa.gr",      "pass3", "Πάτρα",         "F"),
    ("Κώστας",  "Δημητρίου",     "dimitriouk@uoa.gr",     "pass4", "Ηράκλειο",      "M"),
    ("Ελένη",   "Παπαγεωργίου",  "elenipapageorgiou@uoa.gr",  "pass5", "Βόλος",         "F"),
    ("Γιώργος", "Κωνσταντίνου",  "konstantinou@uoa.gr",  "pass6", "Αθήνα",         "M"),
]

# Albums: (name, owner_index, photo_indices)
ALBUMS = [
    ("Ταξίδια & Φύση",    0, [0, 1, 3, 4, 5]),  # Θεοδώρα
    ("Sunset Collection", 0, [2]),               # Θεοδώρα
    ("City Life",         1, [6, 7]),            # Νίκος
    ("Music & Friends",   1, [8]),               # Νίκος
    ("Animals",           2, [9, 10]),           # Μαρία
    ("City Vibes",        2, [11, 12]),          # Μαρία
    ("Study & Coffee",    3, [13, 14, 15]),      # Κώστας
    ("Road Adventures",   4, [5]),               # Ελένη
]

# Friends: (user_index1, user_index2)
FRIENDSHIPS = [
    (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (1, 2)
]

# Comments: (commenter_index, photo_index, text)
COMMENTS = [
    (1, 0,  "Απίστευτη θέα! Πού είναι αυτό;"),
    (2, 0,  "Ονειρεμένο camping!"),
    (3, 1,  "Τέλειο ηλιοβασίλεμα 😍"),
    (0, 8,  "Τι συναυλία ήταν αυτή;"),
    (2, 3,  "Θέλω να ταξιδέψω τώρα!"),
    (4, 2,  "Road trip goals!"),
    (1, 13, "Study inspo!"),
    (0, 6,  "Woww!"),
    (3, 9,  "Πόσο όμορφη γάτα!"),
    (5, 10, "Aesthetic vibes 🧡"),
    (0, 7,  "Shibuya crossing!"),
    (2, 14, "Cozy setup!"),
    (1, 11, "Best coffee spot!"),
    (4, 15, "Study cafe goals ☕"),
]

# Likes: (user_index, photo_index)
LIKES = [
    (1, 0), (2, 0), (3, 0),   # camping - owner 0
    (0, 8), (2, 8), (3, 8),   # concert - owner 1
    (0, 6), (3, 6), (4, 6),   # metro - owner 1
    (1, 9), (4, 9),            # cat - owner 2
    (0, 11),(3, 11),(5, 11),   # coffee - owner 2
    (2, 13),(5, 13),           # study - owner 3
    (1, 14),(2, 14),           # workspace - owner 3
    (0, 7), (1, 7), (2, 7),   # city crossing - owner 1
]

def load_image(filename):
    # Ψάξε στον φάκελο images/
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', filename)
    if not os.path.exists(path):
        # Fallback: ψάξε στον ίδιο φάκελο
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if not os.path.exists(path):
        print(f"Δεν βρέθηκε: {filename}")
        return None
    with open(path, 'rb') as f:
        return f.read()

def main():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    cur = conn.cursor()

    print("🗑  Καθαρισμός παλιών δεδομένων...")
    cur.execute("TRUNCATE TABLE likes, comments, photo_tags, photos, tags, albums, friends, users RESTART IDENTITY CASCADE")
    conn.commit()

    # Users
    print("Εισαγωγή users...")
    user_ids = []
    for fn, ln, email, pw, hometown, gender in USERS:
        cur.execute("""
            INSERT INTO users (first_name, last_name, email, password, hometown, gender)
            VALUES (%s,%s,%s,%s,%s,%s) RETURNING user_id
        """, (fn, ln, email, pw, hometown, gender))
        user_ids.append(cur.fetchone()[0])
    conn.commit()
    print(f"{len(user_ids)} users")

    # Friends
    print("Εισαγωγή friendships...")
    for i, j in FRIENDSHIPS:
        id1 = min(user_ids[i], user_ids[j])
        id2 = max(user_ids[i], user_ids[j])
        cur.execute("INSERT INTO friends (user_id1, user_id2) VALUES (%s,%s) ON CONFLICT DO NOTHING", (id1, id2))
    conn.commit()
    print(f"{len(FRIENDSHIPS)} friendships")

    # Albums + Photos
    print("Εισαγωγή albums και φωτογραφιών...")
    photo_ids = [None] * len(PHOTOS)

    for album_name, owner_idx, photo_indices in ALBUMS:
        owner_id = user_ids[owner_idx]
        cur.execute("""
            INSERT INTO albums (name, owner_id, date_created)
            VALUES (%s,%s,CURRENT_DATE) RETURNING album_id
        """, (album_name, owner_id))
        album_id = cur.fetchone()[0]
        print(f"Album '{album_name}' (owner: {USERS[owner_idx][0]} {USERS[owner_idx][1]})")

        for photo_idx in photo_indices:
            if photo_ids[photo_idx] is not None:
                print(f"    ⏭  Παράλειψη duplicate photo index {photo_idx}")
                continue

            filename, caption, tags = PHOTOS[photo_idx]
            data = load_image(filename)
            if data is None:
                continue

            cur.execute("""
                INSERT INTO photos (caption, data, album_id)
                VALUES (%s,%s,%s) RETURNING photo_id
            """, (caption, psycopg2.Binary(data), album_id))
            photo_id = cur.fetchone()[0]
            photo_ids[photo_idx] = photo_id

            for tag_name in tags:
                cur.execute("INSERT INTO tags (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (tag_name,))
                cur.execute("SELECT tag_id FROM tags WHERE name=%s", (tag_name,))
                tag_id = cur.fetchone()[0]
                cur.execute("INSERT INTO photo_tags (photo_id, tag_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                            (photo_id, tag_id))

            print(f"    🖼  '{caption}' [{', '.join(tags)}]")

    conn.commit()
    loaded = sum(1 for pid in photo_ids if pid is not None)
    print(f"{loaded} φωτογραφίες")

    # Comments
    print("Εισαγωγή comments...")
    count = 0
    for commenter_idx, photo_idx, text in COMMENTS:
        if photo_ids[photo_idx] is None:
            continue
        try:
            cur.execute("""
                INSERT INTO comments (text, owner_id, photo_id, post_date)
                VALUES (%s,%s,%s,NOW())
            """, (text, user_ids[commenter_idx], photo_ids[photo_idx]))
            conn.commit()
            count += 1
        except Exception as e:
            conn.rollback()
            print(f"Comment skip: {e}")
    print(f"{count} comments")

    # Likes
    print("Εισαγωγή likes...")
    count = 0
    for user_idx, photo_idx in LIKES:
        if photo_ids[photo_idx] is None:
            continue
        try:
            cur.execute("INSERT INTO likes (user_id, photo_id) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                        (user_ids[user_idx], photo_ids[photo_idx]))
            conn.commit()
            count += 1
        except Exception as e:
            conn.rollback()
            print(f"Like skip: {e}")
    print(f"{count} likes")

    cur.close()
    conn.close()
    print("\nΈτοιμο! Τρέξε python3 app.py και άνοιξε http://127.0.0.1:5000")

if __name__ == '__main__':
    main()