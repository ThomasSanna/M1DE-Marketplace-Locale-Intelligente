import http from "k6/http";
import { check, sleep } from "k6";

// URL cible de l'API.
const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

// Scenario smoke: faible charge, verification rapide de disponibilite.
export const options = {
  vus: 5,
  duration: "2m",
  thresholds: {
    // Moins de 5% d'echecs HTTP au global.
    http_req_failed: ["rate<0.05"],
    // Latence p95 sous 800ms pour un smoke.
    http_req_duration: ["p(95)<800"],
  },
};

export default function () {
  // Endpoint racine de l'API.
  const root = http.get(`${BASE_URL}/`);
  check(root, { "GET / status < 500": (r) => r.status < 500 });

  // Endpoint Prometheus expose par le backend.
  const metrics = http.get(`${BASE_URL}/metrics`);
  check(metrics, { "GET /metrics status 200": (r) => r.status === 200 });

  // Endpoint data public.
  const sales = http.get(`${BASE_URL}/api/v1/data/sales-metrics`);
  check(sales, {
    "GET /api/v1/data/sales-metrics status < 500": (r) => r.status < 500,
  });

  // Petite pause entre deux iterations utilisateur.
  sleep(0.5);
}
