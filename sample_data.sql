-- =====================================================
-- Αυτό το αρχείο περιέχει δεδομένα χωρίς
-- πραγματικές εικόνες (placeholder binary data).
-- Για πλήρη φόρτωση με πραγματικές εικόνες χρησιμοποίησα:
--   python3 load_data.py
-- =====================================================

BEGIN;

-- =====================
-- USERS
-- =====================
INSERT INTO users (first_name, last_name, email, dob, hometown, gender, password) VALUES
('Θεοδώρα', 'Κόσσυφα',       'kossyfatheo@uoa.gr', '2001-03-15', 'Αθήνα',        'F', 'pass1'),
('Νίκος',   'Αντωνίου',      'antoniounik@uoa.gr',     '1999-07-22', 'Θεσσαλονίκη',  'M', 'pass2'),
('Μαρία',   'Γεωργίου',      'georgioum@uoa.gr',     '2000-11-05', 'Πάτρα',        'F', 'pass3'),
('Κώστας',  'Δημητρίου',     'dimitriouk@uoa.gr',    '1998-04-18', 'Ηράκλειο',     'M', 'pass4'),
('Ελένη',   'Παπαγεωργίου',  'elenipapageorgiou@uoa.gr', '2002-09-30', 'Βόλος',        'F', 'pass5'),
('Γιώργος', 'Κωνσταντίνου',  'konstantinou@uoa.gr', NULL,         'Αθήνα',        'M', 'pass6');

-- =====================
-- FRIENDS
-- =====================
INSERT INTO friends (user_id1, user_id2) VALUES
(1, 2),
(1, 3),
(2, 3),
(2, 4),
(3, 5),
(4, 6);

-- =====================
-- ALBUMS
-- =====================
INSERT INTO albums (name, owner_id, date_created) VALUES
('Ταξίδια & Φύση',    1, '2026-06-01'),  -- album_id=1, owner=1 (Θεοδώρα)
('Sunset Collection', 1, '2026-06-01'),  -- album_id=2, owner=1 (Θεοδώρα)
('City Life',         2, '2026-06-01'),  -- album_id=3, owner=2 (Νίκος)
('Music & Friends',   2, '2026-06-01'),  -- album_id=4, owner=2 (Νίκος)
('Animals',           3, '2026-06-01'),  -- album_id=5, owner=3 (Μαρία)
('City Vibes',        3, '2026-06-01'),  -- album_id=6, owner=3 (Μαρία)
('Study & Coffee',    4, '2026-06-01'),  -- album_id=7, owner=4 (Κώστας)
('Road Adventures',   5, '2026-06-01');  -- album_id=8, owner=5 (Ελένη)

-- =====================
-- PHOTOS (placeholder binary data)
-- =====================
INSERT INTO photos (caption, data, album_id) VALUES
('Camping στα βουνά',         '\x89504e47', 1),  -- photo_id=1,  owner=1
('Ηλιοβασίλεμα στη θάλασσα', '\x89504e47', 1),  -- photo_id=2,  owner=1
('Πτήση στα σύννεφα',         '\x89504e47', 1),  -- photo_id=3,  owner=1
('Photography moment',        '\x89504e47', 1),  -- photo_id=4,  owner=1
('Road trip με χάρτη',        '\x89504e47', 1),  -- photo_id=5,  owner=1
('Road trip sunset',          '\x89504e47', 2),  -- photo_id=6,  owner=1
('Metro rush',                '\x89504e47', 3),  -- photo_id=7,  owner=2
('City crossing',             '\x89504e47', 3),  -- photo_id=8,  owner=2
('Concert night',             '\x89504e47', 4),  -- photo_id=9,  owner=2
('Γάτα στο φως',              '\x89504e47', 5),  -- photo_id=10, owner=3
('Γάτα σκιά',                 '\x89504e47', 5),  -- photo_id=11, owner=3
('Iced coffee downtown',      '\x89504e47', 6),  -- photo_id=12, owner=3
('Work & coffee',             '\x89504e47', 6),  -- photo_id=13, owner=3
('Study session outdoors',    '\x89504e47', 7),  -- photo_id=14, owner=4
('Cozy workspace',            '\x89504e47', 7),  -- photo_id=15, owner=4
('Study cafe vibes',          '\x89504e47', 7);  -- photo_id=16, owner=4

-- =====================
-- TAGS
-- =====================
INSERT INTO tags (name) VALUES
('nature'),
('mountain'),
('camping'),
('sunset'),
('travel'),
('sea'),
('airplane'),
('sky'),
('photography'),
('roadtrip'),
('car'),
('friends'),
('adventure'),
('city'),
('night'),
('urban'),
('people'),
('music'),
('concert'),
('cat'),
('animals'),
('golden'),
('aesthetic'),
('cozy'),
('coffee'),
('work'),
('study'),
('interior');

-- =====================
-- PHOTO_TAGS
-- =====================
INSERT INTO photo_tags (photo_id, tag_id) VALUES
(1,  1), (1,  2), (1,  3), (1,  4), (1,  5),   -- camping: nature,mountain,camping,sunset,travel
(2,  4), (2,  6), (2,  1), (2,  5),             -- sunset: sunset,sea,nature,travel
(3,  5), (3,  7), (3,  4), (3,  8),             -- airplane: travel,airplane,sunset,sky
(4,  9), (4,  1), (4,  5), (4,  4),             -- photography: photography,nature,travel,sunset
(5,  5), (5, 10), (5, 12), (5, 13),             -- road trip: travel,roadtrip,friends,adventure
(6,  4), (6,  5), (6, 10), (6, 11),             -- car sunset: sunset,travel,roadtrip,car
(7, 14), (7,  5), (7, 15), (7, 16),             -- metro: city,travel,night,urban
(8, 14), (8, 16), (8,  5), (8, 17),             -- city crossing: city,urban,travel,people
(9, 18), (9, 19), (9, 12), (9, 15),             -- concert: music,concert,friends,night
(10, 20),(10, 21),(10, 22),(10, 23),             -- cat: cat,animals,golden,aesthetic
(11, 20),(11, 21),(11, 23),(11, 24),             -- cat shadow: cat,animals,aesthetic,cozy
(12, 25),(12, 14),(12, 23),(12, 16),             -- iced coffee: coffee,city,aesthetic,urban
(13, 25),(13, 14),(13, 26),(13, 23),             -- work coffee: coffee,city,work,aesthetic
(14, 27),(14, 23),(14,  1),(14, 25),             -- study outdoors: study,aesthetic,nature,coffee
(15, 23),(15, 27),(15, 24),(15, 28),             -- workspace: aesthetic,study,cozy,interior
(16, 27),(16, 25),(16, 23),(16, 14);             -- study cafe: study,coffee,aesthetic,city

-- =====================
-- COMMENTS
-- Κανόνας: owner_id != owner της φωτογραφίας
-- =====================
INSERT INTO comments (text, owner_id, photo_id, post_date) VALUES
('Απίστευτη θέα! Πού είναι αυτό;',  2, 1,  NOW()),  -- Νίκος → photo1 (owner Θεοδώρα)
('Ονειρεμένο camping!',              3, 1,  NOW()),  -- Μαρία → photo1
('Τέλειο ηλιοβασίλεμα 😍',          4, 2,  NOW()),  -- Κώστας → photo2
('Τι συναυλία ήταν αυτή;',          1, 9,  NOW()),  -- Θεοδώρα → photo9 (owner Νίκος)
('Θέλω να ταξιδέψω τώρα!',          3, 3,  NOW()),  -- Μαρία → photo3
('Road trip goals!',                 5, 6,  NOW()),  -- Ελένη → photo6
('Study inspo!',                     2, 14, NOW()),  -- Νίκος → photo14 (owner Κώστας)
('Αγαπημένη γειτονιά!',             1, 7,  NOW()),  -- Θεοδώρα → photo7 (owner Νίκος)
('Πόσο όμορφη γάτα!',               4, 10, NOW()),  -- Κώστας → photo10 (owner Μαρία)
('Aesthetic vibes 🧡',               6, 11, NOW()),  -- Γιώργος → photo11
('Shibuya crossing!',                1, 8,  NOW()),  -- Θεοδώρα → photo8
('Cozy setup!',                      3, 15, NOW()),  -- Μαρία → photo15
('Best coffee spot!',                2, 12, NOW()),  -- Νίκος → photo12
('Study cafe goals ☕',              5, 16, NOW());  -- Ελένη → photo16

-- =====================
-- LIKES
-- Κανόνας: user_id != owner της φωτογραφίας
-- =====================
INSERT INTO likes (user_id, photo_id) VALUES
(2, 1), (3, 1), (4, 1),    -- photo1 (owner=1): liked by 2,3,4
(1, 9), (3, 9), (4, 9),    -- photo9 (owner=2): liked by 1,3,4
(1, 7), (4, 7), (5, 7),    -- photo7 (owner=2): liked by 1,4,5
(2, 10),(5, 10),            -- photo10(owner=3): liked by 2,5
(1, 12),(4, 12),(6, 12),   -- photo12(owner=3): liked by 1,4,6
(3, 14),(6, 14),            -- photo14(owner=4): liked by 3,6
(2, 15),(3, 15),            -- photo15(owner=4): liked by 2,3
(1, 8), (2, 8), (3, 8);    -- photo8 (owner=2): liked by 1,2,3 ✗ user2=owner2!

COMMIT;

-- =====================
-- ΔΟΚΙΜΗ TRIGGERS (αποσχολιασμός για να δούμε τα errors)
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