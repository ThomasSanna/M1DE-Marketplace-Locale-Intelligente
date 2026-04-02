# Sprint 3 - Stack Observabilite Prometheus + Grafana

## Objectif
Mettre en place une supervision centralisee pour:
- suivre la sante technique du backend,
- visualiser les indicateurs SRE (latence, disponibilite, erreurs),
- observer la consommation de l'error budget.

## Livrables implementes
- Stack monitoring ajoutee dans:
  - `docker-compose.yml`
  - `docker-compose.staging.yml`
- Configuration Prometheus:
  - `monitoring/prometheus/prometheus.yml`
- Provisioning Grafana:
  - `monitoring/grafana/provisioning/datasources/prometheus.yml`
  - `monitoring/grafana/provisioning/dashboards/dashboards.yml`
- Dashboards SRE pre-provisionnes:
  - `monitoring/grafana/dashboards/sre_api_overview.json`
  - `monitoring/grafana/dashboards/sre_error_budget.json`
- Workflow staging mis a jour pour copier `monitoring/`:
  - `.github/workflows/deploy-staging.yml`

## Metriques sources
Le backend expose deja `/metrics` avec:
- `http_requests_total`
- `http_requests_success_total`
- `http_requests_error_total`
- `http_request_duration_seconds` (histogram)

## Dashboards fournis
### 1) Marketplace SRE - API Overview
- Disponibilite API (5m)
- Latence p90 `POST /api/v1/orders`
- Taux erreur `POST /api/v1/payments`
- Trafic HTTP par route/status

### 2) Marketplace SRE - Error Budget & SLO
- Consommation error budget (base SLO 99.5%)
- Disponibilite vs SLO cible
- SLO latence commandes (300ms)
- SLO erreurs paiements (0.1%)

## Lancement en local
```bash
docker compose up -d --build
```

Acces:
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`
  - login par defaut: `admin / admin` (modifiable via `.env`)

Variables optionnelles:
```env
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

## Deploiement staging
Le workflow staging copie `monitoring/` sur le serveur et lance les services Prometheus/Grafana via `docker-compose.staging.yml`.

Ports staging attendus:
- `9090` (Prometheus)
- `3001` (Grafana)

## Verification rapide
1. Ouvrir Grafana et verifier la presence du dossier `Marketplace SRE`.
2. Verifier que la datasource Prometheus est `Healthy`.
3. Verifier que Prometheus scrape bien `backend:8000/metrics`.

## Procedure de test recommandee (local)
### 1) Verifier l'etat des services
```powershell
docker compose ps
```
Les services `backend`, `prometheus` et `grafana` doivent etre `Up`.

### 2) Verifier l'exposition des metriques backend
```powershell
Invoke-WebRequest http://localhost:8000/metrics | Select-Object -ExpandProperty Content
```
La sortie doit contenir des metriques comme:
- `http_requests_total`
- `http_requests_success_total`
- `http_request_duration_seconds_bucket`

### 3) Verifier les targets Prometheus
- Ouvrir `http://localhost:9090/targets`
- Les jobs `marketplace-backend` et `prometheus` doivent etre `UP`.

### 4) Generer du trafic pour remplir les dashboards
Sans trafic, certains panneaux restent a `No data` ou retombent a `0%` (fenetre glissante `rate(...[5m])`).

Exemple PowerShell:
```powershell
for ($i=0; $i -lt 20; $i++) {
  try {
    Invoke-WebRequest -Uri "http://localhost:8000/api/v1/data/sales-metrics" -Method GET | Out-Null
  } catch {}
  Start-Sleep -Milliseconds 200
}
```

Pour tester la latence `POST /api/v1/orders`, il faut appeler cette route avec un payload valide.
Pour tester le taux d'erreur `POST /api/v1/payments`, il faut appeler cette route (avec ou sans auth selon le scenario voulu).

### 5) Verifier Grafana
- Ouvrir `http://localhost:3001`
- Dashboard `Marketplace SRE - API Overview`
- Dashboard `Marketplace SRE - Error Budget & SLO`
- Choisir une fenetre recente (`Last 15 minutes`) et rafraichir.

## Interpretation des valeurs
- `No data`: pas assez de points pour la requete (souvent pas de trafic sur la route cible).
- `0%` sur disponibilite/taux erreur: possible quand il n'y a plus de trafic recent.
- Valeurs qui changent vite: normal avec peu de requetes et une fenetre `[5m]`.
- `401` sur `/api/v1/payments`: compte comme erreur metier dans le dashboard actuel (4xx/5xx).

## Depannage rapide
### Dashboards absents dans Grafana
1. Verifier les fichiers JSON dans `monitoring/grafana/dashboards/`.
2. Redemarrer Grafana:
```powershell
docker compose restart grafana
```
3. Verifier les logs:
```powershell
docker compose logs grafana --tail=200
```

### Prometheus ne scrape pas backend
1. Verifier `monitoring/prometheus/prometheus.yml`.
2. Verifier les logs:
```powershell
docker compose logs prometheus --tail=200
```
3. Redemarrer Prometheus:
```powershell
docker compose restart prometheus
```

