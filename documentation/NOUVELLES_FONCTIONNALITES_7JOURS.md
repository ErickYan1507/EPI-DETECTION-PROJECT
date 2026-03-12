# Nouvelles fonctionnalités (7 derniers jours)

Date de génération : 26/02/2026
Projet : EPI‑DETECTION‑PROJECT

Ce document regroupe les ajouts et améliorations implémentés au cours des sept derniers jours. Il a été conçu pour être copié/collé dans le mémoire de stage/rapport de projet.

---

## 1. Contexte
Le système, initialement centré sur la détection d'équipements de protection individuelle (EPI) via YOLO, a été enrichi de plusieurs modules afin de faire évoluer l'application vers une plateforme de supervision globale, d'administration et de traçabilité de présence.

Toutes les références de code citées appartiennent au dépôt `EPI-DETECTION-PROJECT`.

---

## 2. Supervision unifiée temps réel

### 2.1 Vue et interactions
- **Fichier** : `templates/unified_monitoring.html`.
- Affichage en **overlay** de toutes les détections (boîtes colorées, labels, score, index). 
- Mode de détection configurable `single`/`ensemble` (`use_ensemble`), avec possibilité de visualiser les votes de chaque modèle et la méthode d'agrégation (`union_nms`, etc.).
- Compteurs globaux et statistiques instantanées.
- Dashboard Arduino/IoT : réception et affichage des messages `attendance_detected`, `iot_update`, `serial_line` via Socket.IO.
- Module de gestion de présence intégré (CRUD, filtres par date/personne/source, impression, export CSV) accessible directement depuis l'interface de monitoring.
- Overlay de débogage (streak embedding, état update attendance, erreurs pipeline) pour faciliter la mise au point.

### 2.2 Impacts pour le mémoire
Rédiger une sous-section dédiée dans le chapitre 8 (Réalisation technique) intitulée **"Interface de monitoring unifiée"**, illustrant les mécanismes frontend et les flux SSE/Socket.IO.

---

## 3. Notifications temps réel et journalisation

- **Fichier** : `app/notifications.py`.
- Classe `NotificationManager` centralise l'émission des événements : `new_alert`, `detection_result`, `compliance_update`.
- Communications via WebSocket vers le frontend, ce qui permet une diffusion asynchrone des alertes de conformité et des résultats de détection.
- Écriture dans un log local `logs/alerts.log` pour traçabilité.

*À inclure dans le chapitre 8 (service de notifications) et chapitre 9 (évaluation de la latence des notifications).* 

---

## 4. Panneau d'administration étendu

### 4.1 Authentification et espace admin
- **Fichiers** : `templates/admin_login.html`, `app/database_unified.py` (modèle `AdminUser`), `app/routes_admin.py`.
- Espace sécurisé avec identifiants et gestion de session.

### 4.2 CRUD multi‑tables
- **Fichier** : `templates/admin_panel.html`.
- Interface DataTables générée dynamiquement pour chaque table configurée.
- Actions : création, lecture, modification, suppression, export Excel (table courante, toutes tables, par ID) et filtres par période.
- Architecture backend supportant toute nouvelle table via `TABLE_CONFIG`.

### 4.3 Gestion des personnes et de la présence
- Ajout d'onglet **"Présence quotidienne"** : filtres date/personne/source, boutons d'ajout/impression/export.
- Formulaire de création de personne : nom, fonction, adresse, photo (base64), possibilité d'ajouter une présence manuelle le jour même.
- Logique RGPD : suppression conforme, anonymisation.

### 4.4 Intégration au mémoire
Décrire dans le chapitre 8 (conception de l'administration) et mentionner les captures d'écran dans les annexes.

---

## 5. Module de présence et reconnaissance faciale

### 5.1 Pipeline présentiel
- **Routes** : `/api/attendance/*` définies dans `app/main.py`.
- Service `app/attendance_service.py` assure l'**upsert** des enregistrements journaliers : pour chaque personne, un seul enregistrement par date est conservé et mis à jour (`first_seen_at`, `last_seen_at`, taux de conformité, équipements détectés).
- Fiche de présence individu/collective imprimable et exportable en CSV.

> _"Le système implémente une logique d'upsert de présence quotidienne : chaque personne dispose d'un enregistrement consolidé par date, mis à jour au fil des détections. Cette approche réduit les doublons, simplifie l'audit et améliore la qualité des rapports journaliers."_

### 5.2 Reconnaissance faciale et embeddings
- Intégration de **InsightFace** via la classe `InsightFaceReIdentifier` (`app/face_reid.py`).
- Extraction d'embeddings (512 dimensions) à partir des visages détectés pour faire la correspondance avec la base de données des personnes.
- Paramètres configurables dans `config.py` :
  - `FACE_REID_ENABLED`, `FACE_REID_MODEL`, `FACE_REID_DET_W/H`, `FACE_REID_FORCE_EMBEDDING`, `FACE_REID_HYBRID_ENABLED`, `FACE_REID_FALLBACK_AFTER_FRAMES`, `ATTENDANCE_ALLOW_NO_EMBEDDING_FALLBACK`, `FACE_REID_ALLOW_PSEUDO_EMBEDDING`.
- Politique de fallback :
  - **Strict** : présence ignorée si aucun embedding (mode forcé).
  - **Hybride** : après N frames sans embedding, génération d'un **pseudo-embedding déterministe** à partir du crop de la personne (512D, normalisé) pour ne pas bloquer la chaîne.
- Unité de mesure `miss_streak` pour suivre les échecs d'extraction consécutifs, déclenchant éventuellement le fallback.
- Création/actualisation automatique des enregistrements `PersonIdentity` et `AttendanceRecord` lorsque des embeddings sont associés à un individu.
- Cas particulier `AUTO_UNIDENTIFIED` pour les présences sans identité (fallback sans embedding).

### 5.3 Implications pour le mémoire
Chapitres concernés :
- Chapitre 3 : résultats fonctionnels (traçabilité des personnes, détection/identification, manuel et automatique).
- Chapitre 8 : description détaillée de l'algorithme (YOLOv5 + InsightFace, génération d'embed, gestion des échecs, upsert présence).
- Chapitre 9 : évaluation de la robustesse du re-identification et du taux de réussite des fakes embedding.

---

## 6. Envoi de rapports et artefacts complémentaires

- Export automatisé des fiches de présence au format CSV et impression web (via `/api/attendance/records/print` et `/export/csv`).
- Possibilité d'envoyer ces rapports par email ou via notifications (voir `app/notifications.py` et fichiers d'exemples `EMAIL_EXAMPLES.py`).

Ces éléments sont à mentionner dans la partie « Livrables » du mémoire.

---

## 7. Références et documents existants

Certaines notes internes et fichiers .md peuvent servir de base pour compléter le mémoire :
- `documentation/ANALYSE_ECART_MEMOIRE_FONCTIONNALITES_2026.md`
- `documentation/MISE_A_JOUR_MEMOIRE_UNIFIED_NOTIF_ADMIN_ATTENDANCE.md` (consolidé ci‑dessus).
- `documentation/FINALISATION_RAPPORT.md`, `README_FINAL_2026.md`, `VERSION_2_2_COMPLETE.md`, `RAPPORT_PROJET_EPI_DETECTION.md`.

---

## 8. Prochaines étapes pour l'intégration dans le mémoire
1. Copier les sections pertinentes ci‑dessus dans les chapitres indiqués.
2. Ajouter des captures d'écran (unified_monitoring, admin_panel, fiches de présence).
3. Ajouter des extraits de code pour illustrer l'upsert (attendance_service) et la génération d'embeddings (face_reid).
4. Mettre à jour l'annexe des API (`/api/attendance/*`).
5. Vérifier la bibliographie avec les sources YOLO, InsightFace, Flask, Socket.IO.

---

Ce fichier peut être joint directement au mémoire ou utilisé comme guide de rédaction. Il synthétise les changements techniques et fonctionnels apportés durant la dernière semaine.