# Sprint 4 - Tests de charge (k6) et verification des alertes SRE

## Objectif
Valider que:
1. l'API tient sous charge raisonnable,
2. les metriques SRE evoluent correctement,
3. les alertes Prometheus se declenchent de facon attendue.

## Perimetre
- Outil: `k6`
- Cible: API backend (`:8000`)
- Observabilite:
  - Prometheus (`/targets`, `/rules`, `/alerts`)
  - Grafana (`Marketplace SRE - API Overview`, `Marketplace SRE - Error Budget & SLO`)

## Scripts disponibles
- `load-tests/k6/test_charge_01_smoke_endpoints_publics.js`
- `load-tests/k6/test_charge_02_charge_nominale_mixte.js`
- `load-tests/k6/test_charge_03_stress_paiements_5xx.js`

## Prerequis
1. Environnement disponible (local ou staging).
2. Prometheus scrape bien `backend:8000/metrics`.
3. k6 installe.

## Campagne 
### Smoke
```bash
k6 run -e BASE_URL=http://localhost:8000 load-tests/k6/test_charge_01_smoke_endpoints_publics.js
```
Attendu:
- pas d'erreurs massives,
- endpoint `/metrics` repond 200.

### Charge nominale
```bash
k6 run -e BASE_URL=http://localhost:8000 load-tests/k6/test_charge_02_charge_nominale_mixte.js
```
Attendu:
- dashboards Grafana alimentes,
- evolution visible trafic/latence.

### Stress erreurs techniques paiements
```bash
k6 run -e BASE_URL=http://localhost:8000 \
  -e K6_CLIENT_EMAIL=client@test.local \
  -e K6_CLIENT_PASSWORD=Test1234! \
  -e K6_PRODUCT_ID=<uuid-produit> \
  load-tests/k6/test_charge_03_stress_paiements_5xx.js
```
Attendu:
- hausse `sli:payments_error_ratio_1h`,
- alerte `Payments5xxErrorRateAboveSLO` qui passe `pending` puis `firing` si la condition tient > 10m.

## Verification des alertes
Pendant les tests:
1. `http://<host>:9090/alerts`
2. `http://<host>:9090/rules`
3. Grafana dashboard SRE

Alertes cibles:
- `ApiAvailabilityBelowSLO`
- `OrdersLatencyAboveSLO`
- `Payments5xxErrorRateAboveSLO`
- `ErrorBudgetConsumptionHigh`
