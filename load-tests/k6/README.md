# Tests de charge k6 - Sprint 4

Ce dossier contient des scenarios k6 pour valider:
- la tenue en charge de l'API,
- la qualite des metriques Prometheus,
- le declenchement des alertes SRE.

## Prerequis
- k6 installe localement.
- Stack disponible (local ou staging):
  - API (`:8000`)
  - Prometheus (`:9090`)
  - Grafana (`:3001`)

## Variables utiles
- `BASE_URL` (defaut: `http://localhost:8000`)
- `K6_CLIENT_EMAIL` (optionnel)
- `K6_CLIENT_PASSWORD` (optionnel)
- `K6_PRODUCT_ID` (optionnel)

## Scenarios
1. `test_charge_01_smoke_endpoints_publics.js`
- verification rapide de disponibilite globale.
- cible endpoints publics.

2. `test_charge_02_charge_nominale_mixte.js`
- charge nominale mixte (public + commandes/paiements non authentifies).
- utile pour verifier dashboards et tendances latence.

3. `test_charge_03_stress_paiements_5xx.js`
- scenario orienté erreurs techniques de paiement (`provider_timeout` / `network_error`).
- sert a tester l'alerte `Payments5xxErrorRateAboveSLO`.
- prefere fournir `K6_CLIENT_EMAIL`, `K6_CLIENT_PASSWORD`, `K6_PRODUCT_ID`.

## Exemples de lancement
```bash
# smoke (2 min)
k6 run load-tests/k6/test_charge_01_smoke_endpoints_publics.js

# charge nominale (10 min)
k6 run -e BASE_URL=http://localhost:8000 load-tests/k6/test_charge_02_charge_nominale_mixte.js

# stress paiements techniques (15 min)
k6 run -e BASE_URL=http://localhost:8000 \
  -e K6_CLIENT_EMAIL=client@test.local \
  -e K6_CLIENT_PASSWORD=Test1234! \
  -e K6_PRODUCT_ID=<uuid-produit> \
  load-tests/k6/test_charge_03_stress_paiements_5xx.js
```

## Verification alertes SRE
Pendant le test:
- Prometheus alerts: `http://<host>:9090/alerts`
- Grafana dashboard SRE:
  - `Marketplace SRE - API Overview`
  - `Marketplace SRE - Error Budget & SLO`

Alertes attendues selon scenario:
- `ApiAvailabilityBelowSLO`
- `OrdersLatencyAboveSLO` (si latence commandes degradee)
- `Payments5xxErrorRateAboveSLO` (scenario paiements techniques)
- `ErrorBudgetConsumptionHigh` (si budget depasse)

Note:
- Les alertes ont un `for` (10m/15m) dans Prometheus, donc il faut maintenir la pression suffisamment longtemps.
