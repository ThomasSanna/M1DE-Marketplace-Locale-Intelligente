const PAYMENT_ERROR_MESSAGES = {
  INSUFFICIENT_FUNDS: "Paiement refusé : fonds insuffisants.",
  FRAUD_SUSPECTED: "Transaction bloquée pour suspicion de fraude.",
  PROVIDER_TIMEOUT: "Le fournisseur de paiement ne répond pas. Veuillez réessayer.",
  NETWORK_ERROR: "Erreur réseau temporaire. Veuillez réessayer dans quelques instants.",
  INSUFFICIENT_STOCK: "Stock insuffisant pour un ou plusieurs produits.",
};

export function getErrorMessage(error, fallback = "Une erreur est survenue.") {
  if (!error) return fallback;

  // Timeout axios
  if (error.code === "ECONNABORTED" || error.message?.includes("timeout")) {
    return "Le serveur ne répond pas. Vérifiez votre connexion et réessayez.";
  }

  // Pas de réponse (réseau coupé)
  if (!error.response) {
    return "Impossible de contacter le serveur. Vérifiez votre connexion internet.";
  }

  const status = error.response.status;
  const detail = error.response.data?.detail;

  // Erreurs paiement structurées
  if (detail && typeof detail === "object" && detail.error_code) {
    return PAYMENT_ERROR_MESSAGES[detail.error_code] || detail.message || fallback;
  }

  // Erreurs paiement dans le body direct
  if (detail && typeof detail === "string") {
    if (PAYMENT_ERROR_MESSAGES[detail]) return PAYMENT_ERROR_MESSAGES[detail];
    return detail;
  }

  switch (status) {
    case 400: return "Requête invalide. Vérifiez les informations saisies.";
    case 403: return "Vous n'avez pas accès à cette ressource.";
    case 404: return "Ressource introuvable.";
    case 409: return detail?.message || "Conflit : cette action n'est plus possible.";
    case 422: return "Données invalides. Vérifiez votre saisie.";
    case 500: return "Erreur interne du serveur. Réessayez dans quelques instants.";
    case 502:
    case 503:
    case 504: return "Service temporairement indisponible. Réessayez dans quelques instants.";
    default:  return fallback;
  }
}

export function isRetryable(error) {
  if (!error) return false;
  if (error.code === "ECONNABORTED") return true;
  if (!error.response) return true;
  const status = error.response.status;
  if ([500, 502, 503, 504].includes(status)) return true;
  const errorCode = error.response.data?.detail?.error_code;
  return errorCode === "PROVIDER_TIMEOUT" || errorCode === "NETWORK_ERROR";
}
