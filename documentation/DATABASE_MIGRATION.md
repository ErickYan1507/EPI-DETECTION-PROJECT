Migration SQLite → MySQL
=========================

1) Installer les dépendances (dans votre venv):

```bash
pip install pymysql python-dotenv
```

2) Préparer les variables d'environnement (ex: `.env`) :

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=epi_user
MYSQL_PASSWORD=yourpassword
MYSQL_DB=epi_detection_db
```

3) (Optionnel) créer le schéma MySQL depuis `sql/01_create_database.sql` lors de l'import :

```bash
python sqlite_to_mysql.py --sqlite database/epi_detection.db --create-schema --env .env
```

4) Ou juste importer les données (sous-entend que la BD et les tables existent) :

```bash
python sqlite_to_mysql.py --sqlite database/epi_detection.db --env .env
```

Notes:
- Le script copie toutes les tables présentes dans le fichier SQLite vers MySQL.
- Assurez-vous que les noms de tables/colonnes soient compatibles avec le schéma MySQL.
- Certaines conversions de types complexes (BLOB, JSON) peuvent nécessiter des ajustements manuels.
