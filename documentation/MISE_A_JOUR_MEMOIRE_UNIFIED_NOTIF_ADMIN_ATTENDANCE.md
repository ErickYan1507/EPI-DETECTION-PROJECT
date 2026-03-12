# Plan de mise a jour du memoire - fonctionnalités nouvelles (version consolidée)

Date: 26/02/2026
Projet: EPI-DETECTION-PROJECT

## 1. Objet du document
Ce document consolide les nouveautés à intégrer dans le mémoire, en se concentrant sur:
- `templates/unified_monitoring.html`
- `app/notifications.py`
- `templates/admin_panel.html`
- la gestion de présence (fiche présence, unicité par jour, ajout nouvelles personnes)
- les modèles utilisés et les embeddings

Il inclut aussi les propositions de mise à jour déjà préparées dans les rapports internes du projet.

## 2. Fonctionnalités nouvelles à intégrer dans le mémoire

## 2.1 `unified_monitoring.html` (supervision unifiée)
Références code:
- `templates/unified_monitoring.html` (overlay/drawing): fonctions `drawDetections`, `simulateDetections`
- `templates/unified_monitoring.html` (attendance): bloc `Attendance (DataTables + Modals)`
- `templates/unified_monitoring.html` (Socket.IO/IoT): événements `attendance_detected`, `iot_update`, `serial_line`

Nouveautés:
1. Affichage temps réel avancé de toutes les détections (boites colorées, labels, score, index, compteur global).
2. Mode de détection configurable (single/ensemble) via `use_ensemble`.
3. Module présence intégré dans la même interface (CRUD, filtres, impression, export CSV).
4. Intégration temps réel Arduino/IoT (envoi conformité/détection + flux SSE/Socket.IO).
5. Overlay debug opérationnel (streak embeddings, état update attendance, erreurs pipeline).

## 2.2 `notifications.py` (notifications temps réel)
Références code:
- `app/notifications.py`

Nouveautés:
1. Gestionnaire central `NotificationManager`.
2. Emission WebSocket des alertes (`new_alert`) et conformité (`compliance_update`).
3. Diffusion de résultat de détection (`detection_result`).
4. Traçabilité locale par log fichier (`logs/alerts.log`).

## 2.3 `admin_panel.html` (admin CRUD étendu)
Références code:
- `templates/admin_panel.html` (CRUD générique)
- `templates/admin_panel.html` (module présence admin)

Nouveautés:
1. CRUD générique multi-tables (affichage DataTables, view/edit/delete/create).
2. Export Excel: table courante, toutes les tables, export par ID, filtre date.
3. Espace "Présence Quotidienne" dans l'admin:
   - filtres par date/personne/source,
   - ajout présence manuelle,
   - impression fiche/liste,
   - export CSV.
4. Ajout de nouvelles personnes avec informations d'identité et photo (base64).

## 3. Présence quotidienne: detection unique par jour et création de personnes

Références backend:
- `app/attendance_service.py` (upsert quotidien)
- `app/main.py` routes `/api/attendance/*`

Éléments à documenter:
1. Unicité logique présence/jour: pour une personne donnée, la présence est consolidée (upsert) au lieu de créer des doublons multiples dans la journée.
2. Fiche de présence:
   - fiche individuelle imprimable,
   - liste imprimable,
   - export CSV.
3. Ajout nouvelle personne:
   - nom, fonction, adresse,
   - option présence manuelle du jour,
   - photo d'identité.

Texte prêt à insérer:
"Le système implémente une logique d'upsert de présence quotidienne: chaque personne dispose d'un enregistrement consolidé par date, mis à jour au fil des détections. Cette approche réduit les doublons, simplifie l'audit et améliore la qualité des rapports journaliers."

## 4. Modèles utilisés et embeddings (à insérer dans la partie technique)

Références code:
- `config.py`
- `app/face_reid.py`
- `app/detection.py`
- `app/multi_model_detector.py`
- `app/main.py`

## 4.1 Détection EPI
1. Modèle principal: YOLOv5 avec poids `models/best.pt`.
2. Mode multi-modèles possible (ensemble) avec stratégies d'agrégation (`union_nms`, etc.).
3. Classes EPI supportées: `helmet`, `glasses`, `person`, `vest`, `boots`.

## 4.2 Identification / présence
1. Modèle de re-identification faciale: InsightFace (`FaceAnalysis`) avec modèle `buffalo_l`.
2. Extraction d'embeddings faciaux pour l'association identité-présence.
3. Fallback si visage non exploitable:
   - pseudo-embedding déterministe (512 dimensions) à partir du crop personne,
   - politique configurable (strict/hybride) via:
     - `FACE_REID_FORCE_EMBEDDING`
     - `FACE_REID_HYBRID_ENABLED`
     - `FACE_REID_FALLBACK_AFTER_FRAMES`
     - `ATTENDANCE_ALLOW_NO_EMBEDDING_FALLBACK`

Texte prêt à insérer:
"La détection EPI s'appuie sur YOLOv5 (`best.pt`) avec option d'ensemble multi-modèles. Le suivi de présence utilise InsightFace (`buffalo_l`) pour extraire des embeddings faciaux. En cas d'échec d'extraction, un fallback génère un pseudo-embedding déterministe (512D) selon une politique hybride configurable."

## 5. Placement dans le mémoire (chapitres respectifs)

## 5.1 Chapitre 3 - Objectifs / Résultats fonctionnels
Ajouter/mettre à jour "Fonctionnalités livrées":
1. Supervision unifiée temps réel enrichie.
2. Notifications temps réel + journalisation.
3. Administration CRUD avancée.
4. Module présence journalière (unicité par jour, impression, CSV, ajout personnes).

## 5.2 Chapitre 8 - Réalisation technique
Ajouter des sous-sections:
1. "Interface de monitoring unifiée" (frontend, overlay, modes, IoT).
2. "Service de notifications" (`NotificationManager`, WebSocket, logs).
3. "Panneau d'administration CRUD" (DataTables, exports, sécurité d'usage).
4. "Pipeline présence et identité" (attendance API, modèle face re-id, embeddings, fallback).

## 5.3 Chapitre 9 - Évaluation
Ajouter des critères spécifiques:
1. Latence overlay et stabilité FPS en mode unifié.
2. Délai de propagation alertes WebSocket.
3. Temps moyen CRUD/admin et export.
4. Qualité de la consolidation présence quotidienne (absence de doublons par personne/jour).

## 6. Rapports déjà ajoutés à relier dans le mémoire

Documents du projet à citer en annexe / source interne:
1. `documentation/FINALISATION_RAPPORT.md`
2. `documentation/README_FINAL_2026.md`
3. `documentation/VERSION_2_2_COMPLETE.md`
4. `documentation/RAPPORT_PROJET_EPI_DETECTION.md`
5. `documentation/ANALYSE_ECART_MEMOIRE_FONCTIONNALITES_2026.md`

Suggestion d'usage:
- utiliser `RAPPORT_PROJET_EPI_DETECTION.md` comme trame principale,
- utiliser les autres comme preuves de version et d'évolution.

## 7. Bibliographie et webographie (selon ce périmètre)

## 7.1 Bibliographie
1. Redmon, J., et al. (2016). You Only Look Once: Unified, Real-Time Object Detection.
2. Jocher, G., et al. YOLOv5 (Ultralytics).
3. Deng, J., et al. (2019). ArcFace: Additive Angular Margin Loss for Deep Face Recognition.

## 7.2 Webographie (consultation: 26/02/2026)
1. https://github.com/ultralytics/yolov5
2. https://flask.palletsprojects.com/
3. https://flask-socketio.readthedocs.io/
4. https://docs.sqlalchemy.org/
5. https://docs.opencv.org/
6. https://pytorch.org/docs/stable/
7. https://github.com/deepinsight/insightface
8. https://datatables.net/

## 8. Bloc synthèse prêt à copier dans la conclusion du mémoire
"L'extension récente du système a fait évoluer la solution d'un simple module de détection EPI vers une plateforme intégrée: supervision unifiée temps réel, notifications WebSocket tracées, administration CRUD multi-domaines, et gestion de présence quotidienne avec logique d'unicité par jour. Sur le plan algorithmique, le couplage YOLOv5 + InsightFace, complété par un mécanisme d'embedding de secours, améliore la robustesse opérationnelle dans des conditions terrain variables."
