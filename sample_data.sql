-- =====================
-- USERS
-- =====================
BEGIN;

INSERT INTO users (first_name, last_name, email, dob, hometown, gender, password) VALUES
('Θεοδώρα', 'Παπαδοπούλου', 'theodora@uoa.gr', '2001-03-15', 'Αθήνα',         'F', 'pass1'),
('Νίκος',   'Αντωνίου',     'nikos@uoa.gr',    '1999-07-22', 'Θεσσαλονίκη',   'M', 'pass2'),
('Μαρία',   'Γεωργίου',     'maria@uoa.gr',    '2000-11-05', 'Πάτρα',          'F', 'pass3'),
('Κώστας',  'Δημητρίου',    'kostas@uoa.gr',   '1998-04-18', 'Ηράκλειο',       'M', 'pass4'),
('Ελένη',   'Παπαγεωργίου', 'eleni@uoa.gr',    '2002-09-30', 'Βόλος',          'F', 'pass5'),
('Γιώργος', 'Κωνσταντίνου', 'giorgos@uoa.gr',  NULL,         'Αθήνα',          'M', 'pass6');

-- =====================
-- FRIENDS
-- =====================
INSERT INTO friends (user_id1, user_id2) VALUES
(1, 2),
(1, 3),
(2, 4),
(3, 5),
(4, 6),
(2, 3);

-- =====================
-- ALBUMS
-- owner_id αντιστοιχεί στους παραπάνω users
-- =====================
INSERT INTO albums (name, owner_id, date_created) VALUES
('Καλοκαίρι 2024',     1, '2024-08-01'),  -- album_id=1, owner=1
('Ταξίδι Ναύπλιο',    1, '2024-09-10'),  -- album_id=2, owner=1
('Χριστούγεννα 2024',  2, '2024-12-25'),  -- album_id=3, owner=2
('Φίλοι',              3, '2024-06-15'),  -- album_id=4, owner=3
('Φύση',               4, '2024-05-20'),  -- album_id=5, owner=4
('Πόλη',               5, '2025-01-10');  -- album_id=6, owner=5

-- =====================
-- PHOTOS
-- photo 1-4 → owner 1
-- photo 5   → owner 2
-- photo 6   → owner 3
-- photo 7-8 → owner 4
-- photo 9-10→ owner 5
-- =====================
INSERT INTO photos (caption, data, album_id) VALUES
('Παραλία Μύκονος',    '\x89504e47', 1),  -- photo_id=1,  owner=1
('Ηλιοβασίλεμα',       '\x89504e47', 1),  -- photo_id=2,  owner=1
('Παλαμήδι',           '\x89504e47', 2),  -- photo_id=3,  owner=1
('Λιμάνι Ναύπλιο',    '\x89504e47', 2),  -- photo_id=4,  owner=1
('Χριστουγεννιάτικο',  '\x89504e47', 3),  -- photo_id=5,  owner=2
('Παρέα στην πλατεία', '\x89504e47', 4),  -- photo_id=6,  owner=3
('Δάσος',              '\x89504e47', 5),  -- photo_id=7,  owner=4
('Βουνό',              '\x89504e47', 5),  -- photo_id=8,  owner=4
('Σύνταγμα',           '\x89504e47', 6),  -- photo_id=9,  owner=5
('Μοναστηράκι',        '\x89504e47', 6);  -- photo_id=10, owner=5

-- =====================
-- TAGS
-- =====================
INSERT INTO tags (name) VALUES
('summer'),     -- tag_id=1
('nafplion'),   -- tag_id=2
('friends'),    -- tag_id=3
('nature'),     -- tag_id=4
('athens'),     -- tag_id=5
('christmas'),  -- tag_id=6
('sea'),        -- tag_id=7
('mountain'),   -- tag_id=8
('travel'),     -- tag_id=9
('sunset');     -- tag_id=10

-- =====================
-- PHOTO_TAGS
-- =====================
INSERT INTO photo_tags (photo_id, tag_id) VALUES
(1, 1), (1, 7), (1, 9),   -- Παραλία: summer, sea, travel
(2, 1), (2, 10),           -- Ηλιοβασίλεμα: summer, sunset
(3, 2), (3, 9),            -- Παλαμήδι: nafplion, travel
(4, 2), (4, 7),            -- Λιμάνι: nafplion, sea
(5, 6),                    -- Χριστούγεννα: christmas
(6, 3),                    -- Παρέα: friends
(7, 4),                    -- Δάσος: nature
(8, 4), (8, 8),            -- Βουνό: nature, mountain
(9, 5), (9, 3),            -- Σύνταγμα: athens, friends
(10, 5);                   -- Μοναστηράκι: athens

-- =====================
-- COMMENTS
-- Κανόνας: owner_id != owner της φωτογραφίας
-- photo 1-4 owner=1, photo 5 owner=2,
-- photo 6 owner=3, photo 7-8 owner=4, photo 9-10 owner=5
-- =====================
INSERT INTO comments (text, owner_id, photo_id, post_date) VALUES
('Τι ωραία παραλία!',      2, 1,  '2024-08-05 10:00:00'),  -- user2 → photo1 (owner1) ✓
('Μαγευτικό!',             3, 1,  '2024-08-06 11:00:00'),  -- user3 → photo1 (owner1) ✓
('Θέλω να πάω κι εγώ!',   4, 2,  '2024-08-07 12:00:00'),  -- user4 → photo2 (owner1) ✓
('Όμορφη πόλη!',           3, 3,  '2024-09-12 09:00:00'),  -- user3 → photo3 (owner1) ✓
('Πολύ ωραίο λιμάνι!',    5, 4,  '2024-09-13 14:00:00'),  -- user5 → photo4 (owner1) ✓
('Καλά Χριστούγεννα!',    1, 5,  '2024-12-26 10:00:00'),  -- user1 → photo5 (owner2) ✓
('Ωραία παρέα!',           2, 6,  '2024-06-16 15:00:00'),  -- user2 → photo6 (owner3) ✓
('Φανταστικό δάσος!',      1, 7,  '2024-05-21 08:00:00'),  -- user1 → photo7 (owner4) ✓
('Μπράβο για τη φωτό!',   2, 8,  '2024-05-22 09:00:00'),  -- user2 → photo8 (owner4) ✓
('Αγαπημένη γειτονιά!',   3, 9,  '2025-01-11 16:00:00'),  -- user3 → photo9 (owner5) ✓
('Πανέμορφο!',             4, 9,  '2025-01-12 10:00:00'),  -- user4 → photo9 (owner5) ✓
('Πολύ καλή λήψη!',        6, 10, '2025-01-13 11:00:00');  -- user6 → photo10(owner5) ✓

-- =====================
-- LIKES
-- Κανόνας: user_id != owner της φωτογραφίας
-- =====================
INSERT INTO likes (user_id, photo_id) VALUES
(2, 1), (3, 1), (4, 1),   -- photo1(owner1): liked by 2,3,4 ✓
(1, 5), (3, 5), (4, 5),   -- photo5(owner2): liked by 1,3,4 ✓
(1, 6), (2, 6), (4, 6),   -- photo6(owner3): liked by 1,2,4 ✓
(1, 7), (2, 7), (5, 7),   -- photo7(owner4): liked by 1,2,5 ✓
(1, 8), (3, 8), (6, 8),   -- photo8(owner4): liked by 1,3,6 ✓
(3, 9), (4, 9), (6, 9),   -- photo9(owner5): liked by 3,4,6 ✓
(5, 3), (2, 3);            -- photo3(owner1): liked by 5,2 ✓

COMMIT;

-- =====================
-- ΔΟΚΙΜΗ TRIGGERS (σχολιασμένα - ξεσχολίασε για να δεις τα errors)
-- =====================

-- Trigger 1: user 1 σχολιάζει τη δική της φωτό → ERROR
-- INSERT INTO comments (text, owner_id, photo_id, post_date)
-- VALUES ('Δική μου φωτό!', 1, 1, NOW());

-- Trigger 2: user 1 like στη δική της φωτό → ERROR  
-- INSERT INTO likes (user_id, photo_id) VALUES (1, 1);

-- Trigger 3: self-friend → ERROR
-- INSERT INTO friends (user_id1, user_id2) VALUES (1, 1);

-- Trigger 4: duplicate friend → ERROR
-- INSERT INTO friends (user_id1, user_id2) VALUES (1, 2);

-- Trigger 7: tag με κεφαλαία → auto-lowercase
-- INSERT INTO tags (name) VALUES ('BEACH');
-- SELECT * FROM tags WHERE name = 'beach';
