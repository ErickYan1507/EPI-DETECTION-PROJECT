# Analyse des nouvelles fonctionnalités et écarts avec le mémoire

Date: 26/02/2026  
Projet: EPI-DETECTION-PROJECT

## 1) Sources utilisées
- Code source principal: `app/main.py`, `app/routes_api.py`, `app/routes_stats.py`, `app/routes_iot.py`, `app/routes_notifications*.py`, `app/routes_physical_devices.py`, `app/multi_model_detector.py`, `app/dual_database.py`, `app/dual_db_manager.py`, `app/pdf_export.py`, `app/powerbi_export.py`, `templates/unified_monitoring.html`, `config.py`.
- Rapport/mémoire textuel disponible dans le projet: `documentation/RAPPORT_PROJET_EPI_DETECTION.md`.
- Document PDF fourni: `C:\Users\ANDRIANAVALONA\Documents\memoire erick.pdf` (lecture structurée directe limitée dans cet environnement, comparaison appuyée sur la version markdown du rapport).

## 2) Nouvelles fonctionnalités identifiées dans le code (non suffisamment couvertes dans le mémoire actuel)

| Fonctionnalité | Preuves code | État dans le mémoire actuel | Action recommandée |
|---|---|---|---|
| Monitoring unifié v2.2 (affichage de toutes les détections, overlay canvas, mode ensemble/single) | `templates/unified_monitoring.html` (`drawDetections`, `simulateDetections`, `overlay-canvas`, `use_ensemble`) | Partiellement couvert (dashboard général) | Ajouter une sous-section dédiée "Monitoring unifié temps réel" + captures |
| Pipeline Attendance + reconnaissance faciale (Face ReID) | `app/main.py` routes `/api/attendance/*`, `app/attendance_service.py`, `app/face_reid.py`, flags `FACE_REID_*` dans `config.py` | Non couvert explicitement | Ajouter chapitre/sous-chapitre "Traçabilité présence & identité" |
| API Attendance (CRUD, impression, export CSV, résumé) | `app/main.py` routes `/api/attendance/persons`, `/records`, `/records/print`, `/records/export/csv`, `/summary` | Non couvert | Ajouter au chapitre API + annexe endpoints |
| Notifications avancées (centre complet, config SMTP, destinataires, historique, envoi rapport PDF) | `app/routes_notifications_center.py`, `app/routes_notifications_api.py`, `app/notification_service.py`, `app/email_notifications.py` | Couvert de façon basique (alertes) | Mettre à jour "Système d’alertes" vers "Notifications multicanal" |
| Intégration Arduino étendue + monitoring équipements physiques | `app/arduino_integration.py`, `app/routes_physical_devices.py`, `app/routes_iot.py`, routes `/api/arduino/*`, `/physical/*` | Partiellement couvert | Ajouter une section architecture IoT/physique + protocole d’échange |
| Multi-modèles / Ensemble de détection | `app/multi_model_detector.py`, `app/routes_api.py` (`/models/list`, `/models/mode`, `/models/compare`), `config.py` (`ENSEMBLE_STRATEGY`) | Mentionné en perspective (9.3.2), pas comme implémenté | Déplacer de "perspectives" vers "fonctionnalités implémentées" |
| Double base SQLite + MySQL avec sync temps réel/migration | `app/dual_database.py`, `app/dual_db_manager.py`, `app/migrate_to_mysql.py`, `app/database_unified.py` | Mention simple de MySQL prod, sans architecture duale | Ajouter section "Architecture de persistance" + stratégie de synchronisation |
| Exports avancés (PDF détection, training, présence, listes présence; Power BI CSV/JSON/template) | `app/pdf_export.py`, `app/powerbi_export.py`, `app/routes_stats.py` (`/export/*`) | Mention export basique PDF/CSV | Détailler les types de rapports et usages métier |

## 3) Parties du mémoire à modifier (avec modifications proposées)

## 3.1 Chapitre 3.6 – Résultats fonctionnels
Référence actuelle: `documentation/RAPPORT_PROJET_EPI_DETECTION.md` lignes ~206-214.

### Remplacer la liste "Fonctionnalités livrées" par:
1. Upload et détection image/vidéo.
2. Détection temps réel webcam avec monitoring unifié (overlay multi-objets).
3. Dashboard statistique en temps réel.
4. Système d’alertes et notifications (manuel, planifié, email SMTP, historique).
5. API REST étendue (détection, stats, modèles, attendance, IoT).
6. Exports multi-formats (PDF détection/training/présence, CSV, JSON Power BI).
7. Gestion présence quotidienne (attendance), impression et export.
8. Intégration Arduino + endpoints équipements physiques.
9. Base de données unifiée (SQLite/MySQL) avec options de synchronisation.

## 3.2 Chapitre 8 – Réalisation technique (architecture et API)

### Ajouter une sous-section "8.x Architecture fonctionnelle étendue"
- Sous-système Vision: YOLOv5 + mode ensemble.
- Sous-système Supervision: monitoring unifié (canvas + liste + statistiques).
- Sous-système Présence: Face ReID + attendance records.
- Sous-système Notifications: SMTP, règles d’envoi, historique.
- Sous-système IoT: Arduino + simulation Tinkercad + périphériques physiques.
- Sous-système Données: SQLite/MySQL + synchronisation.

### Ajouter une sous-section "8.x API ajoutées"
- `/api/attendance/*`.
- `/api/notifications/*` + `/api/notifications-center/*`.
- `/api/models/*` (list, mode, compare).
- `/api/arduino/*` et routes `physical/*`.
- `/api/stats/export/*`.

## 3.3 Chapitre 9.1 – Évaluation
Référence actuelle: précision 85.3% (lignes ~2270 et ~2421).

### Modifier:
- Mettre à jour les métriques avec les valeurs réelles les plus récentes déjà documentées dans le projet (ex: `documentation/FINALISATION_RAPPORT.md`): mAP@0.5 = 97.56%, précision = 91.50%, rappel = 94.94%, F1 = 93.19.
- Conserver les anciennes valeurs comme "version antérieure/phase intermédiaire" pour cohérence historique.

## 3.4 Chapitre 9.3 – Limites et perspectives
Référence actuelle: lignes ~2341+.

### Ajuster le statut de ces points
- "Ensemble de modèles": passer de perspective à fonctionnalité implémentée.
- "Rapports avancés (PowerBI)": passer de perspective à implémenté partiel (exports déjà présents).
- Ajouter limites réelles restantes: CI/CD, sécurité production avancée (JWT, rate-limit), validation grande échelle multi-caméras.

## 4) Parties à ajouter dans le mémoire (ou dans les "livres"/annexes)

## 4.1 Nouvelle annexe: "Inventaire des endpoints"
- Tableau endpoint/méthode/usages/réponse.
- Inclure toutes les familles: détection, stats, modèles, attendance, notifications, IoT, exports.

## 4.2 Nouvelle annexe: "Architecture base de données et synchronisation"
- Schéma conceptuel SQLite/MySQL.
- Modes de sync (`sqlite_primary`, `mysql_primary`).
- Procédure de migration et fallback.

## 4.3 Nouvelle annexe: "Scénarios de tests E2E"
- Détection seule.
- Détection + attendance.
- Détection + alertes email.
- Détection + Arduino.
- Export PDF/Power BI.

## 4.4 Nouvelle annexe: "Paramètres de configuration"
- `ENSEMBLE_STRATEGY`, `MIN_ENSEMBLE_VOTES`, `FACE_REID_*`, `ATTENDANCE_*`, `DB_TYPE`, `SMTP_*`.

## 5) Bibliographie à compléter (académique)

1. Jocher, G., et al. (2020). *YOLOv5 by Ultralytics*.  
2. Deng, J., Guo, J., Xue, N., & Zafeiriou, S. (2019). *ArcFace: Additive Angular Margin Loss for Deep Face Recognition*. CVPR.  
3. Redmon, J., Divvala, S., Girshick, R., & Farhadi, A. (2016). *You Only Look Once: Unified, Real-Time Object Detection*. CVPR.  
4. Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press.  
5. Géron, A. (2019). *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow* (2nd ed.). O’Reilly.

## 6) Webographie à compléter (technique/implémentation)
(Consulté le 26/02/2026)

1. Ultralytics YOLOv5: https://github.com/ultralytics/yolov5  
2. Flask Documentation: https://flask.palletsprojects.com/  
3. Flask-SocketIO Documentation: https://flask-socketio.readthedocs.io/  
4. SQLAlchemy Documentation: https://docs.sqlalchemy.org/  
5. PyTorch Documentation: https://pytorch.org/docs/stable/  
6. OpenCV Documentation: https://docs.opencv.org/  
7. ReportLab Documentation: https://www.reportlab.com/documentation/  
8. PySerial Documentation: https://pyserial.readthedocs.io/  
9. Arduino Documentation: https://docs.arduino.cc/  
10. MySQL Documentation: https://dev.mysql.com/doc/  
11. InsightFace Repository: https://github.com/deepinsight/insightface  
12. Microsoft Power BI Documentation: https://learn.microsoft.com/power-bi/

## 7) Priorité de mise à jour recommandée
1. Mettre à jour les métriques du chapitre Évaluation.  
2. Remplacer la liste des fonctionnalités livrées (Chap. 3.6).  
3. Ajouter les sous-sections architecture/API pour attendance-notifications-IoT-dual DB.  
4. Ajouter annexes endpoints + base de données + tests E2E.  
5. Mettre à jour bibliographie et webographie.

## 8) Résumé court prêt à insérer dans l’introduction du rapport final
"La version actuelle du système dépasse le périmètre initial de détection EPI simple: elle intègre désormais un monitoring unifié temps réel, une gestion de présence par identification, un centre de notifications avancé, une couche IoT/Arduino, un mode multi-modèles et une architecture de persistance duale SQLite/MySQL avec options de synchronisation et d’export métier (PDF/Power BI)."
