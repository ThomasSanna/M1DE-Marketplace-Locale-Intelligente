import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Package, ArrowLeft, CheckCircle, Clock, Truck, XCircle } from "lucide-react";
import { getOrderById } from "../api/orders";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import ErrorState from "../components/ui/ErrorState";
import Layout from "../components/Layout";
import { getCategoryImage } from "../lib/categoryImages";
import { getErrorMessage } from "../api/errors";

const STATUS_MAP = {
  draft:     { label: "Brouillon",  variant: "default",  Icon: Clock },
  confirmed: { label: "Confirmée", variant: "success",  Icon: CheckCircle },
  shipped:   { label: "Expédiée",  variant: "primary",  Icon: Truck },
  delivered: { label: "Livrée",    variant: "success",  Icon: CheckCircle },
  cancelled: { label: "Annulée",   variant: "danger",   Icon: XCircle },
};



export default function CommandeDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getOrderById(id)
      .then((res) => setOrder(res.data))
      .catch((err) => setError(getErrorMessage(err, "Impossible de charger la commande.")))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <Layout>
        <div className="space-y-4 max-w-2xl mx-auto">
          <div className="h-8 bg-gray-200 rounded animate-pulse w-48" />
          <div className="bg-white rounded-2xl border border-gray-200 h-48 animate-pulse" />
          <div className="bg-white rounded-2xl border border-gray-200 h-64 animate-pulse" />
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="max-w-md mx-auto">
          <ErrorState message={error} />
          <div className="text-center">
            <Button variant="outline" onClick={() => navigate("/mes-commandes")}>
              <ArrowLeft className="h-4 w-4 mr-2" /> Retour aux commandes
            </Button>
          </div>
        </div>
      </Layout>
    );
  }

  const statusInfo = STATUS_MAP[order.status] || { label: order.status, variant: "default", Icon: Clock };
  const { Icon: StatusIcon } = statusInfo;

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        {/* Navigation */}
        <button
          onClick={() => navigate("/mes-commandes")}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-primary-600 mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Retour aux commandes
        </button>

        {/* En-tête commande */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 mb-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold text-gray-900 mb-1">
                Commande #{order.id.slice(0, 8).toUpperCase()}
              </h1>
              <p className="text-sm text-gray-500">
                Passée le{" "}
                {new Date(order.created_at).toLocaleDateString("fr-FR", {
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>
            <Badge variant={statusInfo.variant} className="flex items-center gap-1">
              <StatusIcon className="h-3.5 w-3.5" />
              {statusInfo.label}
            </Badge>
          </div>

          {order.confirmed_at && (
            <p className="text-xs text-gray-400 mt-3">
              Confirmée le{" "}
              {new Date(order.confirmed_at).toLocaleDateString("fr-FR", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </p>
          )}
        </div>

        {/* Produits commandés */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 mb-4">
          <h2 className="font-semibold text-gray-900 mb-4">Articles commandés</h2>
          <div className="space-y-4">
            {order.items.map((item) => (
              <div key={item.id} className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-xl overflow-hidden flex-shrink-0">
                  <img
                    src={getCategoryImage(item.product?.category)}
                    alt={item.product?.name || "Produit"}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 text-sm truncate">
                    {item.product?.name || `Produit #${item.product_id.slice(0, 8)}`}
                  </p>
                  <p className="text-xs text-gray-500">
                    {Number(item.unit_price_snapshot).toFixed(2)} € ×{" "}
                    {Number(item.quantity)}{" "}
                    {item.product?.unit || ""}
                  </p>
                </div>
                <p className="font-semibold text-gray-900 text-sm whitespace-nowrap">
                  {(Number(item.unit_price_snapshot) * Number(item.quantity)).toFixed(2)} €
                </p>
              </div>
            ))}
          </div>

          {/* Total */}
          <div className="border-t border-gray-100 mt-4 pt-4 flex items-center justify-between">
            <span className="font-semibold text-gray-700">Total</span>
            <span className="text-xl font-bold text-primary-700">
              {Number(order.total_amount).toFixed(2)} €
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => navigate("/catalogue")} className="flex-1">
            Continuer mes achats
          </Button>
        </div>
      </div>
    </Layout>
  );
}
