-- =====================================================
-- k29photo Database Schema
-- =====================================================

-- 1. Users
CREATE TABLE users (
    user_id    SERIAL PRIMARY KEY,
    first_name VARCHAR(50)  NOT NULL,
    last_name  VARCHAR(50)  NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    dob        DATE,                        -- προαιρετικό
    hometown   VARCHAR(100),
    gender     CHAR(1) CHECK (gender IN ('M','F','O')),
    password   VARCHAR(255) NOT NULL
);

-- 2. Friends (αμφίδρομη, χωρίς διπλότυπα)
CREATE TABLE friends (
    user_id1 INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    user_id2 INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id1, user_id2),
    CHECK (user_id1 < user_id2)             -- αποτρέπει (A,B) και (B,A) μαζί
);

-- 3. Albums
CREATE TABLE albums (
    album_id     SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    owner_id     INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    date_created DATE NOT NULL DEFAULT CURRENT_DATE
);

-- 4. Photos
CREATE TABLE photos (
    photo_id SERIAL PRIMARY KEY,
    caption  VARCHAR(255),
    data     BYTEA NOT NULL,                -- δυαδικά δεδομένα εικόνας
    album_id INT NOT NULL REFERENCES albums(album_id) ON DELETE CASCADE
);

-- 5. Tags
CREATE TABLE tags (
    tag_id SERIAL PRIMARY KEY,
    name   VARCHAR(100) NOT NULL UNIQUE,
    CHECK (name = LOWER(name)),             -- πάντα lowercase
    CHECK (name NOT LIKE '% %')             -- χωρίς κενά
);

-- 6. Photo_Tags (M:N μεταξύ photos και tags)
CREATE TABLE photo_tags (
    photo_id INT NOT NULL REFERENCES photos(photo_id) ON DELETE CASCADE,
    tag_id   INT NOT NULL REFERENCES tags(tag_id)     ON DELETE CASCADE,
    PRIMARY KEY (photo_id, tag_id)
);

-- 7. Comments
-- owner_id είναι NULL για guest σχόλια (επισκέπτες χωρίς λογαριασμό)
CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    text       TEXT NOT NULL,
    owner_id   INT REFERENCES users(user_id) ON DELETE CASCADE,  -- NULL για guests
    photo_id   INT NOT NULL REFERENCES photos(photo_id) ON DELETE CASCADE,
    post_date  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 8. Likes (M:N μεταξύ users και photos)
CREATE TABLE likes (
    user_id  INT NOT NULL REFERENCES users(user_id)   ON DELETE CASCADE,
    photo_id INT NOT NULL REFERENCES photos(photo_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, photo_id)
);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger 1: Χρήστης δεν μπορεί να σχολιάσει τη δική του φωτογραφία
-- (NULL owner_id = guest, επιτρέπεται)
CREATE OR REPLACE FUNCTION check_comment_owner()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.owner_id IS NULL THEN
        RETURN NEW;
    END IF;
    IF NEW.owner_id = (
        SELECT a.owner_id
        FROM photos p
        JOIN albums a ON p.album_id = a.album_id
        WHERE p.photo_id = NEW.photo_id
    ) THEN
        RAISE EXCEPTION 'Δεν μπορείς να σχολιάσεις τη δική σου φωτογραφία!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_comment_owner
BEFORE INSERT ON comments
FOR EACH ROW
EXECUTE FUNCTION check_comment_owner();

-- Trigger 2: Χρήστης δεν μπορεί να κάνει like στη δική του φωτογραφία
CREATE OR REPLACE FUNCTION check_like_owner()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.user_id = (
        SELECT a.owner_id
        FROM photos p
        JOIN albums a ON p.album_id = a.album_id
        WHERE p.photo_id = NEW.photo_id
    ) THEN
        RAISE EXCEPTION 'Δεν μπορείς να κάνεις like στη δική σου φωτογραφία!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_like_owner
BEFORE INSERT ON likes
FOR EACH ROW
EXECUTE FUNCTION check_like_owner();

-- Trigger 3: Χρήστης δεν μπορεί να προσθέσει τον εαυτό του ως φίλο
CREATE OR REPLACE FUNCTION check_self_friend()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.user_id1 = NEW.user_id2 THEN
        RAISE EXCEPTION 'Δεν μπορείς να προσθέσεις τον εαυτό σου ως φίλο!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_self_friend
BEFORE INSERT ON friends
FOR EACH ROW
EXECUTE FUNCTION check_self_friend();

-- Trigger 4: Δεν επιτρέπεται διπλή φιλία
CREATE OR REPLACE FUNCTION check_duplicate_friend()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM friends
        WHERE (user_id1 = NEW.user_id1 AND user_id2 = NEW.user_id2)
           OR (user_id1 = NEW.user_id2 AND user_id2 = NEW.user_id1)
    ) THEN
        RAISE EXCEPTION 'Η φιλία αυτή υπάρχει ήδη!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_duplicate_friend
BEFORE INSERT ON friends
FOR EACH ROW
EXECUTE FUNCTION check_duplicate_friend();

-- Trigger 5: Έλεγχος ύπαρξης album κατά την εισαγωγή φωτογραφίας
CREATE OR REPLACE FUNCTION check_photo_album_owner()
RETURNS TRIGGER AS $$
DECLARE
    v_album_owner INT;
BEGIN
    SELECT owner_id INTO v_album_owner
    FROM albums
    WHERE album_id = NEW.album_id;

    IF v_album_owner IS NULL THEN
        RAISE EXCEPTION 'Το album δεν υπάρχει!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_photo_album_owner
BEFORE INSERT ON photos
FOR EACH ROW
EXECUTE FUNCTION check_photo_album_owner();

-- Trigger 6: Δεν επιτρέπεται διπλό like
CREATE OR REPLACE FUNCTION check_duplicate_like()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM likes
        WHERE user_id = NEW.user_id AND photo_id = NEW.photo_id
    ) THEN
        RAISE EXCEPTION 'Έχεις ήδη κάνει like σε αυτή τη φωτογραφία!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_duplicate_like
BEFORE INSERT ON likes
FOR EACH ROW
EXECUTE FUNCTION check_duplicate_like();

-- Trigger 7: Auto-lowercase και validation του tag name
CREATE OR REPLACE FUNCTION normalize_tag_name()
RETURNS TRIGGER AS $$
BEGIN
    NEW.name := LOWER(TRIM(NEW.name));
    IF NEW.name LIKE '% %' THEN
        RAISE EXCEPTION 'Το tag δεν μπορεί να περιέχει κενά!';
    END IF;
    IF NEW.name = '' THEN
        RAISE EXCEPTION 'Το tag δεν μπορεί να είναι κενό!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_normalize_tag_name
BEFORE INSERT OR UPDATE ON tags
FOR EACH ROW
EXECUTE FUNCTION normalize_tag_name();