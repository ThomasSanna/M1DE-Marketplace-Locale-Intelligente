import { AlertTriangle, RefreshCw, WifiOff } from "lucide-react";
import { Button } from "./Button";

export default function ErrorState({ message, onRetry, className = "" }) {
  const isNetwork =
    message?.includes("connexion") || message?.includes("contacter le serveur");

  return (
    <div className={`text-center py-16 ${className}`}>
      <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-red-50 mb-4">
        {isNetwork ? (
          <WifiOff className="h-7 w-7 text-red-400" />
        ) : (
          <AlertTriangle className="h-7 w-7 text-red-400" />
        )}
      </div>
      <p className="text-gray-700 font-medium mb-1">
        {isNetwork ? "Connexion impossible" : "Une erreur est survenue"}
      </p>
      <p className="text-sm text-gray-500 mb-6 max-w-xs mx-auto">{message}</p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Réessayer
        </Button>
      )}
    </div>
  );
}
