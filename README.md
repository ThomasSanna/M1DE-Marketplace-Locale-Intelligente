# Marketplace Locale Intelligente

Projet de Master mêlant ingénierie logicielle, DevOps, cloud, SRE et exploitation de données autour d'une marketplace destinée aux producteurs locaux.

Ce README centralise l'essentiel pour:

- comprendre le périmètre du projet;
- connaître l'architecture et les composants;
- lancer correctement l'application en développement;
- contribuer proprement selon les règles de l'équipe;
- diagnostiquer les problèmes les plus fréquents.

## 1. Objectif du projet

L'application permet de mettre en relation des clients et des producteurs locaux autour d'un catalogue de produits, avec une architecture complète:

- frontend web React;
- backend API FastAPI;
- base de données PostgreSQL;
- conteneurisation Docker;
- intégration continue;
- préparation d'un volet data/BI;
- documentation de travail Scrum / DevOps / architecture.

Le projet est développé en équipe dans un cadre Scrum avec GitFlow, Pull Requests et revue de code.

## 2. Stack technique

### Application

- Frontend: React 18 + Vite
- UI: Tailwind CSS + composants maison
- Backend: FastAPI
- ORM / accès BDD: SQLAlchemy
- Authentification: JWT
- Base de données: PostgreSQL 16

### Industrialisation

- Docker / Docker Compose
- GitHub Actions pour la CI
- Nginx pour servir le frontend conteneurisé

### Data

- Schéma SQL orienté transactionnel + analytique
- Script de seed pour mock data
- Notebook d'exploration initial

## 3. Architecture du dépôt

```text
ProjetBig/
├── backend/                # API FastAPI, auth, routes, modèles, tests
├── frontend/               # Application React/Vite
├── data/                   # Schéma SQL, seed, notebooks
├── docs/                   # Architecture, workflow, Scrum, résultats de sprint
├── docker-compose.yml      # Stack locale conteneurisée
├── .env.example            # Variables d'environnement de référence
└── README.md               # Point d'entrée développeur
```

## 4. Fonctionnalités actuellement présentes (désolé si ça va pas être à jour souvent my bad j'y pense pas toujours)

À date, le dépôt contient déjà les bases suivantes:

- inscription client / producteur;
- authentification et récupération du profil;
- consultation du catalogue produits;
- consultation des producteurs;
- premières bases panier / commandes côté frontend;
- schéma de données couvrant utilisateurs, producteurs, produits, commandes et paiements;
- génération de données mock pour les analyses.

## 5. Prérequis de développement

### Outils requis

- Git
- Docker Desktop ou Docker Engine + Compose
- Python 3.11+
- Node.js 18+
- npm 9+

### Recommandé

- VS Code
- Extension Python
- Extension Docker
- Extension ESLint

## 6. Variables d'environnement

Le projet utilise un fichier `.env` à la racine.

### Initialisation

```powershell
Copy-Item .env.example .env
```

### Valeurs de référence

```env
POSTGRES_DB=marketplace_db
POSTGRES_USER=marketplace_user
POSTGRES_PASSWORD=changeme
POSTGRES_PORT=5432
POSTGRES_HOST=localhost

SECRET_KEY=votre_cle_secrete_super_securisee
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### Règles importantes

- ne jamais committer de secrets réels;
- conserver `.env.example` comme référence de configuration minimale;
- en Docker, `DATABASE_URL` est injectée automatiquement au backend par `docker-compose.yml`;
- en lancement manuel, le backend reconstruit sa connexion PostgreSQL à partir des variables `POSTGRES_*`.

## 7. Démarrage rapide recommandé: mode Docker

Le mode Docker est la façon la plus simple et la plus fiable d'obtenir un environnement cohérent pour toute l'équipe.

### 1. Préparer l'environnement

```powershell
Copy-Item .env.example .env
```

### 2. Construire et lancer la stack

```powershell
docker compose up --build -d
```

### 3. Vérifier les services

```powershell
docker compose ps
docker compose logs backend --tail=100
docker compose logs frontend --tail=100
```

### 4. Accéder aux services

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Metrics Prometheus: <http://localhost:8000/metrics>
- PostgreSQL: localhost:5432

### 5. Arrêter l'environnement

```powershell
docker compose down
```

### 6. Réinitialiser complètement la base si nécessaire

```powershell
docker compose down -v
docker compose up --build -d
```

## 8. Lancement en mode développement local manuel

Ce mode est utile si vous développez activement sur le frontend ou le backend avec rechargement rapide, tout en gardant PostgreSQL dans Docker.

## 8.1. Lancer uniquement PostgreSQL

```powershell
docker compose up -d postgres
```

## 8.2. Backend en local

Depuis la racine du projet:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
Set-Location backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Notes backend

- l'API sera disponible sur <http://localhost:8000>;
- la documentation interactive sera disponible sur <http://localhost:8000/docs>;
- le backend lit `.env` automatiquement;
- si PostgreSQL tourne sur Docker avec les valeurs par défaut, aucune configuration supplémentaire n'est nécessaire.

## 8.3. Frontend en local

Dans un autre terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

### Notes frontend

- le frontend tourne sur <http://localhost:3000>;
- Vite proxy automatiquement les appels `/api` vers `http://localhost:8000`;
- en production conteneurisée, le frontend est servi via Nginx.

## 8.4. Base de données et mock data

Le schéma SQL est monté automatiquement dans le conteneur PostgreSQL au démarrage via `data/schema/schema.sql`.

Pour générer des données de démonstration:

```powershell
pip install -r data/mock/requirements.txt
python data/mock/seed.py
```

Pour régénérer entièrement les données:

```powershell
python data/mock/seed.py --reset
```

### Volumétrie prévue du mock data

- 200 producteurs
- 1 000 clients
- 2 000 produits
- 5 000 commandes
- paiements simulés avec échecs contrôlés

## 9. Commandes utiles au quotidien

### Backend

```powershell
Set-Location backend
pytest -q
python -m compileall .
python -c "import main"
```

### Frontend

```powershell
Set-Location frontend
npm install
npm run dev
npm run build
npm run lint
```

### Docker

```powershell
docker compose up --build -d
docker compose ps
docker compose logs backend --tail=100
docker compose logs frontend --tail=100
docker compose logs postgres --tail=100
docker compose down
```

## 10. Endpoints principaux

### Authentification et utilisateurs

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/me`
- `GET /api/v1/producers`
- `GET /api/v1/producers/{id}/products`

### Produits

- `GET /api/v1/products`
- `GET /api/v1/products/{id}`
- `POST /api/v1/products`
- `PUT /api/v1/products/{id}`
- `DELETE /api/v1/products/{id}`

### Commandes et paiements

- `POST /api/v1/orders`
- `GET /api/v1/orders`
- `GET /api/v1/orders/{id}`
- `POST /api/v1/payments`
- `PATCH /api/v1/orders/{id}/status`

### Endpoints data

- `GET /api/v1/data/sales-metrics`
- `GET /api/v1/data/clustering/customers`
- `GET /api/v1/data/anomalies`

## 11. Workflow Git et règles de contribution

Le dépôt suit une stratégie GitFlow simplifiée.

### Branches

- `main`: branche stable
- `develop`: branche d'intégration
- `feature/<nom>`: développement d'une fonctionnalité
- `hotfix/<nom>`: correctif critique

### Règles de contribution

- ne pas pousser directement sur `main` ou `develop`;
- travailler depuis une branche `feature/*`;
- ouvrir une Pull Request vers `develop`;
- obtenir au moins 1 review avant merge;
- s'assurer que la CI passe au vert;
- supprimer la branche source après merge.

### Exemple de flux recommandé

```powershell
git checkout develop
git pull origin develop
git checkout -b feature/nom-court

# développement

git add .
git commit -m "feat(scope): description courte"
git push -u origin feature/nom-court
```

## 12. Qualité et vérifications attendues avant PR

Avant d'ouvrir une Pull Request, faire au minimum:

### Si vous modifiez le backend

- lancer `pytest -q`;
- vérifier que l'application s'importe correctement;
- valider les endpoints concernés dans `/docs`.

### Si vous modifiez le frontend

- lancer `npm run lint`;
- lancer `npm run build`;
- vérifier le parcours utilisateur impacté dans le navigateur.

### Si vous modifiez le schéma ou la data

- vérifier que `docker compose up` initialise bien PostgreSQL;
- tester `python data/mock/seed.py`;
- documenter tout impact structurel dans `docs/`.

## 13. Définition pratique du Done en dev

Une tâche ne doit pas être considérée comme terminée si elle n'est qu'à moitié intégrée. En pratique, pour ce projet, cela signifie:

- code fusionnable et lisible;
- parcours cohérent côté frontend si la fonctionnalité est visible;
- endpoint cohérent et documenté si la fonctionnalité est backend;
- validation locale minimale rejouée;
- impact éventuel sur Docker, docs ou environnement pris en compte.

## 14. Dépannage

### Le backend ne démarre pas

Vérifier:

- que PostgreSQL tourne bien;
- que `.env` existe à la racine;
- que le port `5432` n'est pas déjà utilisé;
- que les dépendances Python sont installées.

### Le frontend n'appelle pas l'API

Vérifier:

- que le backend tourne bien sur le port `8000`;
- que le frontend tourne via Vite sur le port `3000`;
- que les requêtes passent bien par `/api` en local;
- qu'aucun token expiré ne bloque les appels.

### Les tests backend ne se lancent pas

Vérifier:

- que l'environnement virtuel est activé;
- que `pip install -r backend/requirements.txt` a bien été exécuté;
- que la commande est lancée depuis `backend/`.

### Docker démarre mais l'application ne répond pas

Consulter les logs:

```powershell
docker compose logs postgres --tail=100
docker compose logs backend --tail=100
docker compose logs frontend --tail=100
```

### Le script de seed échoue

Vérifier:

- que PostgreSQL est accessible sur `localhost:5432`;
- que `.env` contient bien les bonnes valeurs;
- que `data/mock/requirements.txt` est installé;
- que la base a bien été initialisée par le schéma SQL.

## 15. Documentation utile du projet

Les documents de référence se trouvent dans `docs/`.

- architecture et endpoints;
- guide DevOps de démarrage;
- règles GitFlow et Pull Requests;
- organisation d'équipe et planification Scrum;
- résultats de sprint;
- sujet de projet.

## 16. Répartition des rôles

- Thomas: Lead Developer et Product Owner
- Yohann: DevOps Engineer, SRE et Scrum Master
- Mohamed: Frontend Developer
- Daniel: Data Engineer / Data Analyst
- Manon: Data Analyst / BI

## 17. Recommandation d'usage pour l'équipe

Pour travailler proprement en dev:

1. démarrer d'abord en mode Docker pour valider l'environnement;
2. basculer ensuite en mode manuel si vous travaillez activement sur le frontend ou le backend;
3. garder PostgreSQL dans Docker pour éviter les écarts entre postes;
4. lancer les vérifications minimales avant chaque PR;
5. documenter tout changement structurel dans `docs/` ou dans ce README si cela impacte l'onboarding.

## 18. État actuel et suite attendue

Le projet dispose déjà d'un socle solide. Les prochaines priorités naturelles en développement sont:

- consolidation du flux panier / commande / paiement;
- élargissement des tests et de la CI;
- poursuite de l'intégration front-back;
- enrichissement du volet observabilité, SRE et data.

Ce README doit rester le point d'entrée développeur principal. Si une information essentielle au démarrage n'y figure pas, elle doit être ajoutée.
