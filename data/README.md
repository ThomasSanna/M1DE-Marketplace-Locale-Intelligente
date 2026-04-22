# Data — Marketplace Locale Intelligente

Dossier géré par **Daniel**.

## Structure

```
data/
├── schema/
│   ├── schema.sql                      # Schéma PostgreSQL (Sprint 1)
│   ├── 002_clustering_tables.sql       # Tables de clustering (Sprint 2)
│   └── 003_anomaly_tables.sql          # Tables de détection d'anomalies (Sprint 3)
├── mock/
│   ├── seed.py                         # Génération du mock data
│   └── requirements.txt                # Dépendances Python
├── pipeline/
│   ├── db.py                           # Utilitaires de connexion DB
│   ├── etl_customers.py                # Extraction features clients (RFM)
│   ├── etl_producers.py                # Extraction features producteurs
│   ├── etl_anomalies.py                # Extraction features transactionnelles (Sprint 3)
│   ├── clustering_customers.py         # K-Means segmentation clients
│   ├── clustering_producers.py         # K-Means segmentation producteurs
│   ├── anomaly_detection.py            # Isolation Forest détection anomalies (Sprint 3)
│   └── run_pipeline.py                 # Orchestrateur du pipeline
├── notebooks/
│   ├── 01_exploration.ipynb            # Exploration du mock data (Sprint 1)
│   ├── 02_clustering_analysis.ipynb    # Analyse des résultats de clustering (Sprint 2)
│   └── 03_three_analyses.ipynb         # Formalisation des 3 analyses (Sprint 3)
├── outputs/                            # Figures générées (gitignored)
└── README.md
```

## Prérequis

- Docker + Docker Compose
- Python 3.10+
- Un fichier `.env` à la racine (copier `.env.example`)

## Démarrage rapide

```bash
# 1. Configurer l'environnement
cp .env.example .env

# 2. Lancer PostgreSQL
docker compose up -d

# 3. Installer les dépendances Python
pip install -r data/mock/requirements.txt

# 4. Générer le mock data
python data/mock/seed.py

# 5. Re-générer (reset complet)
python data/mock/seed.py --reset
```

## Pipeline data (Sprint 2-3)

```bash
# Exécuter le pipeline complet (clustering + anomalies)
python -m data.pipeline.run_pipeline

# Clustering clients uniquement
python -m data.pipeline.run_pipeline --customers

# Clustering producteurs uniquement
python -m data.pipeline.run_pipeline --producers

# Détection d'anomalies uniquement
python -m data.pipeline.run_pipeline --anomalies

# Reset de tous les résultats puis relance
python -m data.pipeline.run_pipeline --reset
```

### Clustering (Sprint 2)

1. **ETL** — Extraction des features depuis PostgreSQL (requêtes SQL avec CTEs)
   - Clients : RFM (Recency, Frequency, Monetary) + comportement (panier moyen, taux annulation)
   - Producteurs : activité (nb produits, diversité) + performance (CA, commandes)
2. **Clustering** — K-Means avec StandardScaler
   - Recherche automatique du K optimal (score silhouette)
   - Labeling automatique des clusters par analyse des centroïdes
3. **Stockage** — Résultats écrits dans `customer_segments` / `producer_segments`
   - Chaque exécution tracée dans `clustering_runs` (reproductibilité)
   - Vues `v_current_customer_segments` et `v_current_producer_segments` pour consommation

### Détection d'anomalies (Sprint 3)

1. **ETL** — Extraction de 8 features transactionnelles par commande
   - Montant, nb articles, prix moyen, heure, jour, fréquence, ratio panier moyen
   - Statut paiement (échoué / erreur simulée)
2. **Détection** — Isolation Forest (scikit-learn)
   - Contamination ~8% (erreurs simulées 5% + outliers)
   - 200 estimateurs, normalisation StandardScaler
3. **Labeling** — Classification automatique des types d'anomalies
   - Paiement échoué, erreur simulée, montant anormal, fréquence inhabituelle, horaire atypique, panier suspect
4. **Stockage** — Résultats écrits dans `anomalies` + `anomaly_runs`
   - Vue `v_current_anomalies` pour consommation

### Consommation des résultats

- **API** (Thomas) : `GET /api/v1/data/clustering/customers`, `GET /api/v1/data/anomalies`, `GET /api/v1/data/sales-metrics`
- **Power BI** (Manon) : DirectQuery sur les vues `v_current_*` et `v_sales_summary`
- **Notebook** : `03_three_analyses.ipynb` pour la formalisation des 3 analyses

## Volumétrie du mock data

| Table        | Lignes  |
|--------------|---------|
| users        | 1 200   |
| producers    | 200     |
| products     | 2 000   |
| orders       | 5 000   |
| order_items  | ~17 000 |
| payments     | ~4 300  |

## Accès à la base (Read-Replica en prod)

En local : `localhost:5432`
En production : connexion via le Read-Replica provisionné par Yohann (DevOps).

```
Host     : localhost
Port     : 5432
Database : marketplace_db
User     : marketplace_user
```
