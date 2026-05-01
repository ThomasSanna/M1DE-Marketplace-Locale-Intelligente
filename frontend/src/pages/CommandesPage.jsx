import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Package, ChevronRight } from "lucide-react";
import { getOrders } from "../api/orders";
import { useAuth } from "../context/AuthContext";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import ErrorState from "../components/ui/ErrorState";
import Layout from "../components/Layout";
import { getErrorMessage } from "../api/errors";

const STATUS_MAP = {
  draft:     { label: "Brouillon",  variant: "default" },
  confirmed: { label: "Confirmée", variant: "success" },
  shipped:   { label: "Expédiée",  variant: "primary" },
  delivered: { label: "Livrée",    variant: "success" },
  cancelled: { label: "Annulée",   variant: "danger" },
};

export default function CommandesPage() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchOrders = useCallback(() => {
    setLoading(true);
    setError("");
    getOrders()
      .then((res) => setOrders(res.data))
      .catch((err) => setError(getErrorMessage(err, "Impossible de charger vos commandes.")))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!authLoading && !user) { navigate("/login"); return; }
    if (!authLoading && user) fetchOrders();
  }, [user, authLoading, navigate, fetchOrders]);

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-1">Mes Commandes</h1>
        <p className="text-gray-500">Historique de vos achats</p>
      </div>

      {loading && (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-200 h-24 animate-pulse" />
          ))}
        </div>
      )}

      {error && <ErrorState message={error} onRetry={fetchOrders} />}

      {!loading && !error && orders.length === 0 && (
        <div className="text-center py-16">
          <Package className="h-16 w-16 text-gray-200 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-gray-700 mb-2">Aucune commande</h2>
          <p className="text-gray-500 mb-6">Vous n&apos;avez pas encore passé de commande</p>
          <Button onClick={() => navigate("/catalogue")}>Commencer mes achats</Button>
        </div>
      )}

      {!loading && !error && orders.length > 0 && (
        <div className="space-y-4">
          {orders.map((order) => {
            const statusInfo = STATUS_MAP[order.status] || { label: order.status, variant: "default" };
            return (
              <div
                key={order.id}
                className="bg-white rounded-2xl border border-gray-200 p-5 flex items-center justify-between hover:shadow-sm transition-shadow cursor-pointer"
                onClick={() => navigate(`/commandes/${order.id}`)}
              >
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 bg-primary-50 rounded-xl flex items-center justify-center">
                    <Package className="h-6 w-6 text-primary-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 text-sm">
                      Commande #{order.id.slice(0, 8).toUpperCase()}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(order.created_at).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>
                  {order.total_amount && (
                    <span className="font-bold text-primary-700 text-sm">
                      {Number(order.total_amount).toFixed(2)} €
                    </span>
                  )}
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Layout>
  );
}
