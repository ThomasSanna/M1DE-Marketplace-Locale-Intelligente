import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Package, Truck, CheckCircle, Clock, XCircle } from "lucide-react";
import { getProducerOrders, updateOrderStatus } from "../api/orders";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import ErrorState from "../components/ui/ErrorState";
import Layout from "../components/Layout";
import { getErrorMessage } from "../api/errors";

const STATUS_MAP = {
  draft:     { label: "Brouillon",  variant: "default",  Icon: Clock },
  confirmed: { label: "Confirmée", variant: "success",  Icon: CheckCircle },
  shipped:   { label: "Expédiée",  variant: "primary",  Icon: Truck },
  delivered: { label: "Livrée",    variant: "success",  Icon: CheckCircle },
  cancelled: { label: "Annulée",   variant: "danger",   Icon: XCircle },
};

const STATUS_FILTERS = [
  { value: "", label: "Toutes" },
  { value: "confirmed", label: "Confirmées" },
  { value: "shipped", label: "Expédiées" },
  { value: "delivered", label: "Livrées" },
  { value: "cancelled", label: "Annulées" },
];

export default function ProducerOrdersPage() {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [updatingId, setUpdatingId] = useState(null);

  const fetchOrders = useCallback(() => {
    setLoading(true);
    setError("");
    getProducerOrders(statusFilter || undefined)
      .then((res) => setOrders(res.data))
      .catch((err) => setError(getErrorMessage(err, "Impossible de charger les commandes.")))
      .finally(() => setLoading(false));
  }, [statusFilter]);

  useEffect(() => { fetchOrders(); }, [fetchOrders]);

  const handleUpdateStatus = async (orderId, newStatus) => {
    setUpdatingId(orderId);
    try {
      const res = await updateOrderStatus(orderId, newStatus);
      setOrders((prev) =>
        prev.map((o) => (o.id === orderId ? res.data : o))
      );
    } catch (err) {
      alert(getErrorMessage(err, "Impossible de mettre à jour le statut."));
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <Layout>
      {/* En-tête */}
      <div className="mb-8">
        <button
          onClick={() => navigate("/dashboard")}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-primary-600 mb-4 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Retour au dashboard
        </button>
        <h1 className="text-3xl font-bold text-gray-900 mb-1">Commandes reçues</h1>
        <p className="text-gray-500">Gérez les commandes de vos clients</p>
      </div>

      {/* Filtres statut */}
      <div className="flex flex-wrap gap-2 mb-6">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setStatusFilter(f.value)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              statusFilter === f.value
                ? "bg-primary-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Contenu */}
      {loading && (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-200 h-28 animate-pulse" />
          ))}
        </div>
      )}

      {error && <ErrorState message={error} onRetry={fetchOrders} />}

      {!loading && !error && orders.length === 0 && (
        <div className="text-center py-16 bg-white rounded-2xl border border-gray-200">
          <Package className="h-16 w-16 text-gray-200 mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-gray-700 mb-2">Aucune commande</h2>
          <p className="text-gray-500">
            {statusFilter
              ? "Aucune commande avec ce statut pour le moment."
              : "Vous n'avez pas encore reçu de commandes."}
          </p>
        </div>
      )}

      {!loading && !error && orders.length > 0 && (
        <div className="space-y-4">
          {orders.map((order) => {
            const statusInfo = STATUS_MAP[order.status] || { label: order.status, variant: "default", Icon: Clock };
            const { Icon: StatusIcon } = statusInfo;
            const canShip = order.status === "confirmed";
            const canDeliver = order.status === "shipped";

            return (
              <div
                key={order.id}
                className="bg-white rounded-2xl border border-gray-200 p-5"
              >
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div className="flex items-center gap-3">
                    <div className="h-12 w-12 bg-primary-50 rounded-xl flex items-center justify-center flex-shrink-0">
                      <Package className="h-6 w-6 text-primary-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 text-sm">
                        Commande #{order.id.slice(0, 8).toUpperCase()}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(order.created_at).toLocaleDateString("fr-FR", {
                          day: "numeric",
                          month: "long",
                          year: "numeric",
                        })}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 flex-wrap">
                    <Badge variant={statusInfo.variant} className="flex items-center gap-1">
                      <StatusIcon className="h-3.5 w-3.5" />
                      {statusInfo.label}
                    </Badge>
                    <span className="font-bold text-primary-700 text-sm">
                      {Number(order.total_amount).toFixed(2)} €
                    </span>
                  </div>
                </div>

                {/* Articles */}
                {order.items && order.items.length > 0 && (
                  <div className="mt-4 border-t border-gray-100 pt-4">
                    <p className="text-xs text-gray-500 mb-2">Articles :</p>
                    <ul className="space-y-1">
                      {order.items.map((item) => (
                        <li key={item.id} className="text-sm text-gray-700 flex justify-between">
                          <span>
                            {item.product?.name || `Produit #${item.product_id.slice(0, 8)}`}
                            {" · "}
                            <span className="text-gray-400">
                              {Number(item.quantity)} {item.product?.unit || ""}
                            </span>
                          </span>
                          <span className="font-medium">
                            {(Number(item.unit_price_snapshot) * Number(item.quantity)).toFixed(2)} €
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Actions */}
                {(canShip || canDeliver) && (
                  <div className="mt-4 flex gap-2 flex-wrap">
                    {canShip && (
                      <Button
                        size="sm"
                        onClick={() => handleUpdateStatus(order.id, "shipped")}
                        disabled={updatingId === order.id}
                        className="gap-1"
                      >
                        <Truck className="h-4 w-4" />
                        Marquer comme expédiée
                      </Button>
                    )}
                    {canDeliver && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleUpdateStatus(order.id, "delivered")}
                        disabled={updatingId === order.id}
                        className="gap-1"
                      >
                        <CheckCircle className="h-4 w-4" />
                        Marquer comme livrée
                      </Button>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Layout>
  );
}
