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
