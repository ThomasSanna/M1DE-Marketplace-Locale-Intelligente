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


# Planification Scrum, Rituels et Calendrier

La réalisation du projet de **Marketplace Locale Intelligente** se fera de manière itérative et incrémentale. L'organisation s'appuie sur des Sprints de durée fixe, rythmés par l'ensemble des rituels Scrum animés par notre Scrum Master (Yohann).

## 1. Calendrier des Sprints (Rushs)

Le projet est découpé en **4 Sprints** logiques (d'une durée estimative de 2 à 3 semaines chacun, selon le calendrier académique d'ici la soutenance finale de 2026).

### 🎯 Sprint 1 : Base de l'Architecture & Fondations (Semaine 1-3)
**Objectif :** Mettre en place l'environnement de développement, la structure des bases de données et les premières fondements API.
* **Thomas (Lead Dev / PO) :** 
  * Définit le backlog initial.
  * Modélisation de la base de données relationnelle (PostgreSQL).
  * Initialise le projet Backend et crée les API CRUD minimales de base (produits, utilisateurs).
* **Yohann (DevOps / SM) :** 
  * Setup du dépôt Git et paramétrage du GitFlow (protection des branches, règles de PR).
  * Écriture des premiers `Dockerfile` et `.github/workflows` de base.
* **Mohamed (Front) :** 
  * Initialisation du projet Frontend (React/Vue).
  * Mise en place l'architecture des composants et intégration d'une librairie UI (Material/Tailwind).
* **Daniel (Data Engineer) & Manon (Data BI) :** 
  * Définition des besoins finaux en reporting avec le PO.
  * Génération d'un dataset "factice" volumineux (Mock Data) de commandes et profils pour commencer à expérimenter pendant que le vrai code se construit.

### 🎯 Sprint 2 : Logique Métier & Déploiement Cloud (Semaine 4-6)
**Objectif :** Apporter la logique métier centrale de la marketplace, lier le Front au Back et sortir la v1.0 sur le Cloud.
* **Thomas :** Développement des endpoints complexes : Gestion des stocks et cycle de vie des Commandes. Simulation de paiement.
* **Mohamed :** Développement du parcours d'achat (Panier, validation de commande, vue catalogue) et appel des API du backend.
* **Yohann :** Conteneurisation complète (docker-compose avancé). Provisionnement du Cloud (AWS/GCP), déploiement via CI/CD. Mise en place du Kubernetes (Cluster de dev).
* **Daniel :** Première exploration sur les données (Mock Data + premières données de dev). Développement des scripts de clustering (segmentation producteurs/clients).
* **Manon :** Connexion de Power BI aux données de tests de Daniel. Prototypage des premiers graphiques analytiques.

### 🎯 Sprint 3 : Monitoring, Fiabilisation SRE & Pipeline Data (Semaine 7-9)
**Objectif :** Rendre l'application résiliente, observable, et finaliser le pipeline Data.
* **Yohann (SRE) :** Implémentation de Prometheus pour le scraping des métriques applicatives. Création des dashboards Grafana. Définition technique des SLO/SLI dans le code.
* **Thomas :** Instrumentalisation du code Backend pour exposer des métriques à Prometheus (temps de réponse, compteurs d'erreur). Résolution de la dette technique.
* **Mohamed :** Finalisation de l'UX/UI, gestion fine des cas d'erreur (HTTP 500, Timeouts) pour l'utilisateur.
* **Daniel :** Finalisation du script de traitement des anomalies (détection d'anomalies sur les comportements d'achat simulés). Injection en base des résultats.
* **Manon :** Intégration des modèles de Daniel dans le PowerBI final. Création du Dashboard métier de la Marketplace.

### 🎯 Sprint 4 : Répétitions, Tests de charge & Polish Final (Semaine 10-12)
**Objectif :** Préparation à la soutenance, validation des SLA et des livrables.
* **Thomas & Mohamed :** Aucune nouvelle feature majeure. Correction de bugs critiques exclusifs.
* **Yohann :** Lancement de tests de charge (ex: JMeter ou K6) pour voir si l'application déclenche les alertes SRE. Ajustement du scaling Kubernetes.
* **Daniel & Manon :** Finalisation du Dashboard analytique. Vérification de l'intégrité des données à partir des événements des tests de charge.
* **Toute l'équipe :** Rédaction des documents d'architecture, vérification des livrables, et répétitions de la soutenance orale (20 min).

---

## 2. Rituels Agiles Implémentés

Chaque sprint sera ponctué rigoureusement par les cérémonies Agiles officielles, orchestrées par **Yohann (Scrum Master)**.

| Rituel | Fréquence | Durée | Rôle des Membres | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Sprint Planning** | Début de chaque Sprint | 2h | **PO (Thomas)** propose les stories. **Équipe** estime via Planning Poker. | Sélection des User Stories du backlog à inclure dans le Sprint. Attribution estimative des points de complexité. |
| **Daily Scrum** | Quotidiennement (ou 3x/semaine en simu) | 15 min | **Tous** (debout/Discord) | Chacun répond à : 1. Qu'est-ce que j'ai fait hier ? 2. Que vais-je faire aujourd'hui ? 3. Ai-je des points bloquants ? |
| **Dev Sync & Code Review** | Continue | Asynchrone | **Thomas, Mohamed, Yohann** principalement | Aucune Pull Request n'est fusionnée sur `develop` sans l'approbation (review) d'un autre membre technique. |
| **Sprint Review** | Fin du Sprint | 1h | **Tous** + Professeurs (Clients fictifs) | Démonstration (Démo) du code qui a été testé, validé et déployé sur l'environnement Cloud. Validation du PO. |
| **Rétrospective** | Après la Review | 45 min | **Tous**, animé par **Yohann (SM)** | Analyse du Sprint écoulé : *Ce qui s'est bien passé*, *Ce qui a moins bien marché*, *Actions d'amélioration* (Stop/Keep/Start). |

# Architecture Technique et Contrats d'API (Endpoints)

Ce document décrit les choix d'architecture technique et les systèmes de communication back-to-front (Endpoints) de notre Marketplace Locale Intelligente.

## 1. Stack Technique Choisie Justifiée

L'architecture s'oriente vers des micro-services ou un monolithe modulaire robuste orienté cloud-native.

* **Front-end : React.js (ou paramétré via Next.js)**
  * *Justification :* Bibliothèque standard robuste, grand écosystème facilitant la création de dashboards producteurs fluides et de vues clients interactives.
* **Back-end : Node.js avec NestJS (ou Express) / Alternative Python (FastAPI)**
  * *Justification :* Les deux sont légers et s'intègrent excellemment dans des conteneurs Docker. Nous privilégierons **FastAPI (Python)** ou **Node.js** pour sa forte synergie avec le monde de la Data logicielle, tout en exposant à merveille un JSON structuré (OpenAPI) dès la conception.
* **Base de données Principale : PostgreSQL**
  * *Justification :* Forte intégrité référentielle, vitale pour une Marketplace (Commandes, Stocks, factures). Parfait pour l'extraction de requêtes analytiques massives requises par l'équipe Data.
* **Infrastructure CI/CD et Cloud et SRE:**
  * **Docker & Kubernetes :** Orchestration professionnelle.
  * **GitHub Actions / GitLab CI :** Pour les pipelines d'intégration continue.
  * **Prometheus + Grafana :** Scraping natif d'une application conteneurisée.
  * **Cloud : AWS (Amazon EKS et Amazon RDS)** pour assurer les SLAs.

---

## 2. Liste Exhaustive des Endpoints API REST (Core Buisness)

Ces endpoints sont exposés par le Backend développé par Thomas à destination du Front (Mohamed). Le format d'échange est strictement **JSON**.

### 🍏 Gestion des Produits (Stocks)
* `GET /api/v1/products` : Liste les produits de la marketplace (avec pagination et filtres géographiques/prix).
* `GET /api/v1/products/{id}` : Récupère les détails spécifiques d'un produit.
* `POST /api/v1/products` : *[Auth Producer]* Ajoute un nouveau produit au catalogue.
* `PUT /api/v1/products/{id}` : *[Auth Producer]* Modifie un produit existant ou ajuste le stock (ex: `- 5 kg de pommes`).
* `DELETE /api/v1/products/{id}` : *[Auth Producer]* Supprime/Désactive un produit.

### 🧑‍🌾 Gestion des Utilisateurs et Producteurs
* `POST /api/v1/auth/register` : Inscription d'un nouveau client ou producteur.
* `POST /api/v1/auth/login` : Authentification (Retourne un JWT Token).
* `GET /api/v1/users/me` : Récupération du profil.
* `GET /api/v1/producers` : Liste tous les producteurs locaux.
* `GET /api/v1/producers/{id}/products` : Récupère la vitrine/boutique d'un producteur spécifique.

### 🛒 Gestion des Commandes et Paiements Simulé
* `POST /api/v1/orders` : Transforme le panier Front-end en Commande (Brouillon). Réserve temporairement les stocks.
* `GET /api/v1/orders` : *[Auth]* Récupération de l'historique des commandes d'un utilisateur.
* `GET /api/v1/orders/{id}` : Détail d'une commande.
* `POST /api/v1/payments` : **Simulateur de Paiement**. Reçoit l'ID de la commande, simule l'autorisation bancaire (5% d'erreur simulée volontairement pour générer des anomalies), valide la commande et prélève les stocks définitivement.
* `PATCH /api/v1/orders/{id}/status` : *[Auth Producer]* Mise à jour d'expédition (Validée -> Expédiée).

---

## 3. Architecture d'Accès aux Données (Équipe Data Daniel & Manon)

Pour éviter que les requêtes analytiques lourdes de Power BI (Manon) et des scripts de Machine Learning (Daniel) n'impactent la stabilité de l'API de production, voici l'organisation :

### 1. Accès SQL (Read-Replica)
Yohann (DevOps) provisionnera un **Read-Replica PostgreSQL**. Daniel (Data) et Manon (Viz) utiliseront leurs requêtes d'exploration sur cette instance clonée en temps réel.
* Cela empêche de consommer l'Error Budget sur l'application live en cas de requête SQL gourmande (Deadlocks CPU).

### 2. Endpoints Analytiques Dédiés (Data API)
Certains modèles calculés par Daniel seront ré-exposés par l'API pour être potentiellement affichés sur le Front, ou mis à disposition de PowerBI via des WebHooks/API :
* `GET /api/v1/data/sales-metrics` : Renvoie les ventes totales agrégées, le panier moyen.
* `GET /api/v1/data/clustering/customers` : Renvoie le segment "Clientèle" (ex: "Acheteurs impulsifs", "Fidèles Bio") calculé en asynchrone par les scripts de Daniel.
* `GET /api/v1/data/anomalies` : Renvoie les transactions flaguées comme potentiellement frauduleuses par l'algorithme d'analyse comportemental.

L'accès pour PowerBI se fera soit par **DirectQuery PostgreSQL** vers le Read-Replica, soit par l'ingestion d'un flux d'API OData branché sur l'API Backend.


# Workflow DevOps et Stratégie SRE

L'assurance qualité logicielle et la fiabilité du déploiement sont garanties par Yohann (DevOps/SRE) avec le soutien de l'ensemble de l'équipe (Thomas, Mohamed).

## 1. GitFlow et Stratégie de Collaboration Git

Afin de travailler sans conflit et de garantir un code sain, nous appliquerons une stratégie de branching stricte **GitFlow** modifiée.
* `main` : Reflète l'état de la Production applicative. Déployé sur Kubernetes en Prod.
* `develop` : Reflète le code de test actuel. Déployé sur l'environnement Staging.
* `feature/XXX` : Branche de travail (ex: `feature/cart-management`).
* `hotfix/XXX` : Seule branche acceptée à bifurquer directement depuis `main` pour un correctif critique.

**Conditions Absolues des Pull Requests (PR) :**
1. Chaque PR d'une feature vers `develop` doit être approuvée par **au moins 1 autre développeur** (Code Review systématique).
2. Le pipeline CI **doit obligatoirement passer au vert** (Tests unitaires valides, Build Docker fonctionnel) pour autoriser le bouton de merge ("Branch protection rules" sur GitHub/GitLab).

---

## 2. Pipeline CI/CD (Intégration et Déploiement Continus)

Le workflow `ci-cd.yml` comportera les jobs automatisés suivants :

1. **Phase de CI (sur chaque push sur une PR) :**
   * **Lint & Formatting :** Vérification de la syntaxe du code (ex: ESLint/Prettier/Flake8).
   * **Unit Tests :** Exécution de la suite de tests (Jest / PyTest).
   * **Security Scan :** Analyse des vulnérabilités des dépendances (ex: Trivy ou SonarQube).
2. **Phase de Build (sur merge vers `develop` / `main`) :**
   * Build de l'image Docker du Front-end et du Backend.
   * Push de l'image vers une Container Registry sécurisée (GitHub Packages, AWS ECR, ou Docker Hub).
3. **Phase de CD (Déploiement) :**
   * Mise à jour des manifestes Kubernetes ou du `docker-compose.yml` du serveur.
   * Redémarrage "Zero Downtime" de l'application (Rolling Update).

---

## 3. Démarche SRE (Site Reliability Engineering)

Le monitoring est centré sur l'utilisateur final pour garantir le niveau de service. Yohann définira les métriques en concertation avec Thomas (Lead Dev) et Mohamed (Product Owner Frontend).

### Nos SLIs (Service Level Indicators)
Les métriques extraites en temps réel par Prometheus :
1. **Disponibilité (Availability) :** Taux de requêtes HTTP réussies (`HTTP 200/201/300` vs `HTTP 5xx`) sur tous les endpoints critiques.
2. **Latence (Latency) :** Temps de réponse en millisecondes pour l'endpoint `POST /api/v1/orders`.
3. **Taux d'erreur métier :** Pourcentage d'échecs rencontrés sur l'endpoint de paiement final `POST /api/v1/payments`.

### Nos SLOs (Service Level Objectives) ciblés
Les promesses réalistes que l'équipe ingénierie fait au métier (aux producteurs/clients) :
* **SLO 1 :** 99.5% des requêtes vers l'API globale aboutissent avec succès (Code Http < 500) sur une période de 30 jours consécutifs.
* **SLO 2 :** 90% des appels API de création de commande s'exécutent en moins de 300 millisecondes.
* **SLO 3 :** Le service de paiement simulé ne doit jamais échouer (0 erreur technique inattendue) sur 99.9% des tentatives.

### Notre SLA (Service Level Agreement)
C'est le contrat "commercial" qui repose sur nos SLO.
* L'application s'engage sur un taux de disponibilité de **99.0%** par mois (soit env. 7,3 heures d'indisponibilité autorisées par mois maximum).

### Politique d'Error Budget 
L'Error Budget représente l'écart entre un temps de fonctionnement de 100% et notre SLO défini (0.5% d'erreur pour notre SLO 1).
* **Si le budget est positif** : Thomas et Mohamed (Développeurs) ont l'autorisation par Yohann et le CA (Continuous Approval) de déployer de nouvelles features librement (Risque accepté).
* **Si le budget est épuisé (SLO non respecté)** : **Freezing des déploiements majeurs.** Tous les membres techniques de l'équipe travaillent de concert sur des tâches de stabilité et résolution de dette technique et SRE, afin de remonter le niveau de garantie. Mohamed et Thomas ne font plus que du *bug fix* jusqu'à rétablissement du budget.

---

## 4. Orcherstration, Conteneurisation et Monitoring

* **Conteneurisation (Docker) :** Chaque brique logique (Front, Back, DB, Scripts Data) sera isolée dans un `Dockerfile` optimisé multi-stage. L'orchestration ciblée sera **Kubernetes** pour permettre de garantir nos SLO via la montée en charge automatique (HPA - Horizontal Pod Autoscaler). Si le contexte Cloud le limite, nous utiliserons `docker-compose` de façon stricte.
* **Monitoring & Observabilité :**
  * **Prometheus :** Collectera via Scraping automatique toutes les données d'application (node-exporter, cAdvisor, custom metrics).
  * **Grafana :** Lira les données depuis Prometheus pour afficher les graphes. Nous concevrons 2 Dashboards d'observabilité : un **Dashboard Système applicatif** (CPU/RAM des pods, Load HTTP), et un **Dashboard SRE** affichant explicitement le décalage avec le SLO et la consommation de l'Error Budget.
  * Les alertes seront déclenchées (ex: Discord/Slack Webhook) si le seuil critique est franchi concernant l'Error Budget.
