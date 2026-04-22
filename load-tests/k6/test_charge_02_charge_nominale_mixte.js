import http from "k6/http";
import { check, sleep } from "k6";

// URL cible de l'API (surchargeable via -e BASE_URL=...).
const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

// Scenario nominal: montee en charge, plateau, puis descente.
export const options = {
  stages: [
    { duration: "2m", target: 10 },
    { duration: "6m", target: 25 },
    { duration: "2m", target: 0 },
  ],
  thresholds: {
    // Seuils permissifs pour un test mixte (certains endpoints peuvent repondre 4xx).
    http_req_failed: ["rate<0.20"],
    http_req_duration: ["p(95)<1500"],
  },
};

// Entetes JSON reutilises pour les endpoints POST.
const defaultHeaders = { "Content-Type": "application/json" };

export default function () {
  // Batch pour simuler un trafic mixte representatif de l'app.
  const responses = http.batch([
    ["GET", `${BASE_URL}/`, null, null],
    ["GET", `${BASE_URL}/api/v1/data/sales-metrics`, null, null],
    [
      "POST",
      `${BASE_URL}/api/v1/orders`,
      JSON.stringify({ items: [] }),
      { headers: defaultHeaders },
    ],
    [
      "POST",
      `${BASE_URL}/api/v1/payments`,
      JSON.stringify({
        order_id: "00000000-0000-0000-0000-000000000000",
        simulate_scenario: "auto",
        processing_delay_ms: 100,
      }),
      { headers: defaultHeaders },
    ],
  ]);

  // Verifications minimales: l'API doit repondre sans erreurs serveur massives.
  check(responses[0], { "GET / status < 500": (r) => r.status < 500 });
  check(responses[1], { "GET sales-metrics status < 500": (r) => r.status < 500 });
  check(responses[2], { "POST /orders repond": (r) => r.status >= 200 && r.status < 500 });
  check(responses[3], { "POST /payments repond": (r) => r.status >= 200 && r.status < 500 });

  // Pause courte entre deux iterations utilisateur.
  sleep(0.3);
}
