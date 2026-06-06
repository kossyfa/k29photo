# k29photo - Εφαρμογή Διαχείρισης Φωτογραφιών
Εργασία 3 - K29 ΕΚΠΑ Τμήμα Πληροφορικής & Τηλ/νιών

## Δομή Project

### Φάση Ι - Σχεδιασμός Βάσης Δεδομένων
- `schema.sql`      — Δημιουργία πινάκων και constraints/triggers
- `sample_data.sql` — Sample δεδομένα χωρίς εικόνες
- `er-diagram.mwb`  — E/R Διάγραμμα (MySQL Workbench)

### Φάση ΙΙ - Υλοποίηση Εφαρμογής
- `app.py`          — Flask εφαρμογή (routes, SQL queries)
- `load_data.py`    — Φόρτωση πραγματικών δεδομένων με εικόνες
- `templates/`      — HTML templates (Jinja2)
- `static/`         — CSS (style.css)
- `images/`         — Εικόνες για το load_data.py
- `requirements.txt`— Python dependencies

## Εκτέλεση

### Βήμα 1: Δημιουργία βάσης
```bash
psql -U k29 -d k29photo -h localhost -a -f schema.sql
```

### Βήμα 2: Φόρτωση δεδομένων με εικόνες (προτεινόμενο)
```bash
# Βάλε τις εικόνες στον φάκελο images/ και τρέξε:
python3 load_data.py
```

### Εναλλακτικά: Φόρτωση δεδομένων χωρίς εικόνες
```bash
psql -U k29 -d k29photo -h localhost -a -f sample_data.sql
```

### Βήμα 3: Εκκίνηση εφαρμογής
```bash
source myvirenv/bin/activate
python3 app.py
```

### Βήμα 4: Άνοιξε στον browser
```
http://127.0.0.1:5000
```
