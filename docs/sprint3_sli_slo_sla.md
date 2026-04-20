# Sprint 3 - Definition et suivi SLI/SLO/SLA

## Objectif
Formaliser une politique SRE exploitable pour la prise de decision en exploitation:
- definition claire des SLI,
- objectifs SLO mesurables,
- cadre SLA,
- regles de pilotage par error budget.

## SLI retenus
1. **Disponibilite API**
- Definition: part des requetes considerees en succes applicatif.
- Metrique: `http_requests_success_total / http_requests_total`
- Fenetres de suivi:
  - court terme: 1h
  - budget: 24h

2. **Latence commandes**
- Definition: p90 de `POST /api/v1/orders`.
- Metrique: `http_request_duration_seconds_bucket` (histogram).
- Fenetre de suivi: 1h.

3. **Taux d'erreurs techniques paiements**
- Definition: taux de `5xx` sur `POST /api/v1/payments`.
- Metrique: `http_requests_total{status_code=~"5.."}` / total paiements.
- Fenetre de suivi: 1h.

## SLO cibles
1. Disponibilite API >= **99.5%**
2. Latence p90 commandes <= **300 ms**
3. Taux d'erreurs techniques paiements <= **0.1%**

## SLA (cadre equipe/projet)
SLA interne aligne au sujet:
- engagement de fiabilite fonde sur les SLO,
- suivi continu via dashboards Grafana et alertes Prometheus,
- arbitrage release pilote par error budget.

## Error budget et regles de release
Error budget API:
- Budget autorise = `1 - SLO` = `0.5%` d'indisponibilite.
- Indicateur: `error_budget:api_consumed_ratio_24h`.

Politique d'exploitation:
1. **< 50% budget consomme**
- cadence normale de livraison.
2. **50% a 100%**
- releases prudentes (petits lots, surveillance renforcee).
3. **> 100%**
- freeze des releases de fonctionnalites,
- priorite aux correctifs de stabilite et reduction de dette technique.

## Mise en oeuvre technique
### Regles Prometheus
Fichier:
- `monitoring/prometheus/sli_slo_rules.yml`

Contenu:
- recording rules:
  - `sli:api_availability_ratio_1h`
  - `sli:api_availability_ratio_24h`
  - `sli:orders_latency_p90_seconds_1h`
  - `sli:payments_error_ratio_1h`
  - `error_budget:api_consumed_ratio_24h`
- alerting rules:
  - `ApiAvailabilityBelowSLO`
  - `OrdersLatencyAboveSLO`
  - `Payments5xxErrorRateAboveSLO`
  - `ErrorBudgetConsumptionHigh`

### Config Prometheus
- `monitoring/prometheus/prometheus.yml` charge:
  - `/etc/prometheus/rules/sli_slo_rules.yml`

### Compose local et staging
Le fichier de regles est monte dans:
- `docker-compose.yml`
- `docker-compose.staging.yml`
