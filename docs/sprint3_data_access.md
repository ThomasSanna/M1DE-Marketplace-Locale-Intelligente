# Sprint 3 - Mise a disposition des donnees (SQL read-only + API)

## Objectif
Fournir un acces aux donnees via:
1. SQL en lecture seule (pour Power BI / analyses ad hoc)
2. API analytique (pour integration applicative / scripts)

## Livrables implementes
- Script SQL read-only: `data/schema/004_readonly_access.sql`
- Compose local/staging mis a jour pour charger ce script au bootstrap postgres
- Workflow staging mis a jour pour copier tous les scripts schema (01 a 04)

## 1) Acces SQL read-only

### Role SQL cree
- Role: `data_readonly`
- Type: `LOGIN` + lecture seule
- Permissions:
  - `CONNECT` sur `marketplace_db`
  - `USAGE` schema `public`
  - `SELECT` sur toutes les tables et vues existantes
  - `USAGE, SELECT` sur sequences
  - `ALTER DEFAULT PRIVILEGES` pour conserver la lecture seule sur les futurs objets

### Test rapide SQL
```sql
-- Connexion avec data_readonly
SELECT current_user;

-- Lecture OK
SELECT COUNT(*) FROM users;
SELECT * FROM v_sales_summary LIMIT 10;

-- Ecriture KO (attendu)
INSERT INTO users (email, password_hash, role, first_name, last_name)
VALUES ('test@example.com', 'x', 'client', 'A', 'B');
```

## 2) Acces API analytique

Endpoints exposes par le backend:
- `GET /api/v1/data/sales-metrics`
- `GET /api/v1/data/clustering/customers?limit=200`
- `GET /api/v1/data/anomalies?limit=100`

### Exemples
```bash
curl http://localhost:8000/api/v1/data/sales-metrics
curl "http://localhost:8000/api/v1/data/clustering/customers?limit=50"
curl "http://localhost:8000/api/v1/data/anomalies?limit=50"
```

## 3) Notes d'exploitation
- Le script SQL read-only est execute au premier demarrage postgres du volume.
- Si le volume postgres existe deja, il faut appliquer le script manuellement ou recreer le volume:
```bash
docker compose down -v
docker compose up -d
```
- En staging, les scripts schema sont copies par `deploy-staging.yml` dans `${STAGING_APP_DIR}/data/schema/`.
