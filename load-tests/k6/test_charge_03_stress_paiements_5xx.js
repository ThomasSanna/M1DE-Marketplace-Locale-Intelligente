import http from "k6/http";
import { check, sleep } from "k6";

// URL cible de l'API (surchargeable via -e BASE_URL=...).
const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
// Credentials et produit de test (facultatifs mais recommandes pour generer de vrais 5xx).
const EMAIL = __ENV.K6_CLIENT_EMAIL || "";
const PASSWORD = __ENV.K6_CLIENT_PASSWORD || "";
const PRODUCT_ID = __ENV.K6_PRODUCT_ID || "";

// Scenario stress oriente paiements: palier principal de 10 minutes.
export const options = {
  stages: [
    { duration: "2m", target: 5 },
    { duration: "10m", target: 20 },
    { duration: "3m", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.80"],
    http_req_duration: ["p(95)<2500"],
  },
};

// Authentifie un utilisateur client et retourne le header Bearer.
function login(email, password) {
  const payload = `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`;
  const headers = { "Content-Type": "application/x-www-form-urlencoded" };
  const res = http.post(`${BASE_URL}/api/v1/auth/login`, payload, { headers });
  if (res.status !== 200) return null;
  const token = res.json("access_token");
  return token ? `Bearer ${token}` : null;
}

// Cree une commande minimale afin d'avoir un order_id valide pour le paiement.
function createOrder(authHeader, productId) {
  const res = http.post(
    `${BASE_URL}/api/v1/orders`,
    JSON.stringify({
      items: [{ product_id: productId, quantity: 1 }],
    }),
    {
      headers: {
        Authorization: authHeader,
        "Content-Type": "application/json",
      },
    }
  );
  if (res.status !== 201) return null;
  return res.json("id");
}

export default function () {
  // Mode degrade sans credentials: envoie quand meme du trafic, mais souvent en 401.
  if (!EMAIL || !PASSWORD || !PRODUCT_ID) {
    const fallback = http.post(
      `${BASE_URL}/api/v1/payments`,
      JSON.stringify({
        order_id: "00000000-0000-0000-0000-000000000000",
        simulate_scenario: "provider_timeout",
        processing_delay_ms: 300,
      }),
      { headers: { "Content-Type": "application/json" } }
    );
    check(fallback, { "fallback payments repond": (r) => r.status >= 200 && r.status < 500 });
    sleep(0.2);
    return;
  }

  // 1) Login.
  const authHeader = login(EMAIL, PASSWORD);
  if (!authHeader) {
    sleep(0.2);
    return;
  }

  // 2) Creation de commande.
  const orderId = createOrder(authHeader, PRODUCT_ID);
  if (!orderId) {
    sleep(0.2);
    return;
  }

  // 3) Paiement force en erreur technique (503/504) pour tester l'alerte SRE.
  const scenario = Math.random() > 0.5 ? "provider_timeout" : "network_error";
  const payment = http.post(
    `${BASE_URL}/api/v1/payments`,
    JSON.stringify({
      order_id: orderId,
      payment_method: "card",
      idempotency_key: `${__VU}-${__ITER}-${Date.now()}`,
      simulate_scenario: scenario,
      processing_delay_ms: 300,
    }),
    {
      headers: {
        Authorization: authHeader,
        "Content-Type": "application/json",
      },
    }
  );

  // On accepte 200 ou 5xx selon les conditions metier/transitions d'etat.
  check(payment, {
    "payment stress repond": (r) => r.status >= 200 && r.status < 600,
    "payment stress genere 5xx de temps en temps": (r) => r.status === 503 || r.status === 504 || r.status === 200,
  });

  // Pause courte pour maintenir une pression soutenue.
  sleep(0.2);
}
