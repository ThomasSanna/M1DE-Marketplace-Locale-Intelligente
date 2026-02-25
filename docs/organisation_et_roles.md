# Organisation de l'Équipe et Répartition des Rôles

Ce document définit la structure organisationnelle de notre équipe pour la réalisation du projet de **Marketplace locale intelligente**. Notre équipe fonctionnera selon les principes de la méthodologie Agile (Scrum).

## 1. Composition de l'Équipe et Répartition Officielle

L'équipe est composée de 5 membres : **Manon, Yohann, Mohamed, Daniel et Thomas**. Conformément à la répartition initiale des périmètres d'action, les rôles officiels exigés par le cahier des charges ont été distribués de la façon suivante :

| Membre | Rôle(s) Officiel(s) | Périmètre Principal |
| :--- | :--- | :--- |
| **Manon** | Data Analyst (Visualisation) | Dashboard analytique (Power BI). |
| **Mohamed** | Front-end Developer | Conception et développement de l'interface utilisateur. |
| **Daniel** | Data Engineer / Data Analyst | Traitement des données, modèles prédictifs, clustering. |
| **Thomas** | Lead Developer & Product Owner (PO) | Architecture logicielle, développement Backend, Base de données, vision du produit. |
| **Yohann** | DevOps Engineer, SRE & Scrum Master | Pipeline CI/CD, Conteneurisation, Cloud, Monitoring, animation de l'équipe. |

---

## 2. Description Détaillée des Rôles et Responsabilités

### 👩‍💻 Thomas - Lead Developer & Product Owner (PO)
En tant que **Lead Developer**, Thomas est le garant technique du code applicatif. En tant que **Product Owner**, il porte la vision du produit et la priorisation des fonctionnalités (Marketplace).
* **Responsabilités PO :**
  * Rédiger et maintenir le Product Backlog (Epics, User Stories pour la Marketplace).
  * Définir les critères d'acceptation et prioriser les tâches pour chaque Sprint avec l'équipe.
  * Valider les fonctionnalités développées par Mohamed (Front) et par lui-même (Back).
* **Responsabilités Lead Developer :**
  * Définir l'architecture logicielle globale du Backend (API REST).
  * Concevoir le schéma de la base de données (postgreSQL) pour répondre aux besoins transactionnels (commandes, stocks) et analytiques (pour Daniel et Manon).
  * Développer les composants critiques du Backend (Gestion des commandes, paiements, stocks applicatifs).
  * Assurer la qualité du code (Code Review systématique sur les Pull Requests de Mohamed et l'intégration continue).

### 🛠️ Yohann - Scrum Master, DevOps Engineer & SRE
Yohann est à la fois l'animateur de la méthode Agile et l'architecte de l'infrastructure, s'assurant que le code de Thomas et Mohamed se déploie de manière fluide et fiable, tout en garantissant sa disponibilité.
* **Responsabilités Scrum Master :**
  * Organiser et animer les rituels Scrum : Sprint Planning, Daily Scrum, Sprint Review, et Rétrospective.
  * S'assurer que les obstacles (bloquants techniques ou organisationnels) soient levés rapidement.
  * Garantir le respect des méthodes Agiles et de l'utilisation des outils de suivi (Jira / Trello / GitHub Projects).
* **Responsabilités DevOps / SRE :**
  * Concevoir et maintenir le pipeline CI/CD (GitHub Actions / GitLab CI) pour les tests, builds et déploiements automatisés de toute l'application.
  * Gérer la conteneurisation de l'application via Docker et l'orchestrer avec Kubernetes (ou Docker-compose).
  * Déployer l'infrastructure sur le Cloud (AWS / GCP / Azure).
  * Implémenter les outils de Monitoring (Prometheus, Grafana) et définir la démarche SRE (SLI, SLO, SLA, Error budgets).

### 🖥️ Mohamed - Front-end Developer
Mohamed est responsable de la création de l'interface de notre Marketplace locale. Il est l'artisan de l'expérience utilisateur (UX) et de l'interface utilisateur (UI).
* **Responsabilités :**
  * Développer les interfaces de la Marketplace (catalogue producteurs, panier d'achat, dashboard producteur, etc.) avec un framework moderne (React / Vue.js).
  * Assurer une intégration parfaite avec le Backend développé par Thomas.
  * Mettre en œuvre le design responsive et veiller à l'accessibilité de l'application.
  * Formuler les besoins en Endpoints auprès de Thomas (Lead Dev) lors des Daily Scrums.
  * Écrire les tests unitaires et composants de la partie Front-end.

### 📊 Daniel - Data Engineer & Data Analyst
Daniel s'occupe de la branche "Intelligence" du projet. Il transforme les données brutes générées par la Marketplace en informations actionnables.
* **Responsabilités :**
  * Récupérer et nettoyer les données (Extraction via connexion SQL directe ou API développée par Thomas).
  * Concevoir et exécuter des algorithmes d'analyse (ex: segmentation client/clustering k-means, analyse comportementale, modèle prédictif des ventes).
  * Transformer et stocker les données consolidées pour faciliter la visualisation.
  * Automatiser les scripts de traitement de données de telle sorte qu'ils s'exécutent de façon reproductible.

### 📈 Manon - Data Analyst (Dashboard BI)
Manon clôture la chaîne de valeur des données en concevant l'interactivité métier pour les parties prenantes.
* **Responsabilités :**
  * Concevoir le Dashboard analytique Business Intelligence avec Power BI.
  * Se connecter aux sources préparées par Daniel ou directement sur la base en mode Read-Only pour construire les KPI.
  * Créer les visualisations répondant au cahier des charges (Comportement utilisateur, détection d'anomalies, segmentation).
  * Communiquer activement avec Daniel (pour s'assurer que les données et modèles sont bien formatés) et avec Thomas (pour demander des vues SQL spécifiques ou des accès API).

---

## 3. Flux d'Interactions et Communication

La réussite du projet repose sur la fluidité des interactions entre les profils techniques.
1. **Lien Front / Back (Mohamed & Thomas) :** Thomas crée les contrats d'API (OpenAPI/Swagger). Mohamed s'appuie sur ces contrats pour développer ses vues. Les modifications d'Endpoints se discutent et s'ajustent lors des Code Reviews et planifications.
2. **Lien App / Devops (Thomas, Mohamed & Yohann) :** Yohann configure les environnements Cloud. Yohann fournit à Thomas et Mohamed les processus de linting/tests automatisés qui tournent sous CI/CD. Les erreurs de pipeline sont résolues en commun, guidé par Yohann.
3. **Lien Ops / Data (Yohann & Daniel) :** Yohann instancie des bases de données répliquées (Read-Replicas) dans le Cloud pour éviter que les requêtes analytiques lourdes de Daniel fassent chuter la base de production applicative (protégeant ainsi le SLO défini par Yohann).
4. **Lien Dev / Data (Thomas & Daniel) :** Thomas documente la structure de la BDD et fournit les accès. S'il manque des logs d'événement ("tel utilisateur a cliqué ici"), Daniel exprime ce besoin métier (en accord avec Thomas qui l'ajoutera au backlog).
5. **Lien Data / Viz (Daniel & Manon) :** Pipeline de bout-en-bout. Daniel s'occupe de l'ETL (Extract Transform Load) et de l'intelligence algorithmique, tandis que Manon exploite les tables "Gold" issues des modèles de Daniel pour développer les graphiques PowerBI.
