# ⚡ QUICKSTART - Démarrer avec la BD Unifiée

## 3 Étapes Simples

### 1️⃣ Réinitialiser la BD (une seule fois)
```bash
python force_reset_db.py
```
**Résultat attendu:**
```
✅ BD réinitialisée avec 11 tables
```

### 2️⃣ Vérifier que tout fonctionne
```bash
python test_database.py
```
**Résultat attendu:**
```
✅ TOUS LES TESTS RÉUSSIS!
```

### 3️⃣ Lancer l'application
```bash
python run_app.py
```
**Accédez à:** http://localhost:5000

---

## 🔧 Configuration (Optionnel)

### Utiliser MySQL au lieu de SQLite
```bash
# Windows PowerShell
$env:DB_TYPE = "mysql"
$env:DB_HOST = "localhost"
$env:DB_USER = "epi_user"
$env:DB_PASSWORD = "votre_motdepasse"

# Puis relancer
python force_reset_db.py
python run_app.py
```

### Linux/Mac
```bash
export DB_TYPE=mysql
export DB_HOST=localhost
export DB_USER=epi_user
export DB_PASSWORD=votre_motdepasse

python force_reset_db.py
python run_app.py
```

---

## 📊 Vérifier la BD

### Voir les données
```bash
# SQLite
sqlite3 database/epi_detection.db ".tables"

# MySQL
mysql -u epi_user -p epi_detection_db -e "SHOW TABLES;"
```

### Requête simple
```python
python << 'EOF'
from app.database_unified import TrainingResult, Detection, db
from flask import Flask
from config import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
db.init_app(app)

with app.app_context():
    print(f"TrainingResult: {TrainingResult.query.count()}")
    print(f"Detection: {Detection.query.count()}")
EOF
```

---

## ❓ Questions Fréquentes

**Q: Erreur "table already exists"?**  
A: Exécuter `python force_reset_db.py` (supprime et recrée)

**Q: Où se trouve la BD SQLite?**  
A: `database/epi_detection.db`

**Q: Comment changer de BD (SQLite → MySQL)?**  
A: Définir `DB_TYPE=mysql` et relancer

**Q: Peut-on avoir SQLite ET MySQL?**  
A: Non, une seule à la fois (via `DB_TYPE`)

**Q: Les anciennes données sont perdues?**  
A: Oui avec `force_reset_db.py` (c'est intentionnel)

**Q: Comment importer les résultats train.py?**  
A: `python init_unified_db.py` (optionnel)

---

## 🚀 Utilisation de Base

### Uploader une image
```bash
curl -F "image=@photo.jpg" http://localhost:5000/api/detect
```

### Voir les détections
```bash
curl http://localhost:5000/api/stats
```

### Démarrer la simulation IoT
```bash
curl -X POST http://localhost:5000/api/iot/simulation/start
```

---

## 📚 Documentation Complète

Pour plus de détails, voir:
- **[DATABASE_UNIFIED.md](DATABASE_UNIFIED.md)** - Guide technique
- **[UTILISATION_BD_UNIFIEE.md](UTILISATION_BD_UNIFIEE.md)** - Guide utilisateur  
- **[RESUME_VISUEL.md](RESUME_VISUEL.md)** - Architecture visuelle

---

## ✅ Checklist

- [ ] `python force_reset_db.py` ✓
- [ ] `python test_database.py` → Tous ✅
- [ ] `python run_app.py`
- [ ] Accéder à http://localhost:5000
- [ ] Uploader une image
- [ ] Vérifier `database/epi_detection.db` existe
- [ ] Lire documentation si besoin

---

**Vous êtes prêt! 🎉**

Démarrez avec l'étape 1, puis explorez l'interface!
