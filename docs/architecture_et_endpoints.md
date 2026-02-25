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
