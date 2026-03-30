import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Trash2, Plus, Minus, ShoppingCart } from "lucide-react";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { createOrder, processPayment } from "../api/orders";
import { Button } from "../components/ui/Button";
import Layout from "../components/Layout";
import { getCategoryImage } from "../lib/categoryImages";

export default function PanierPage() {
  const { items, removeItem, updateQuantity, clearCart, totalPrice } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleCheckout = async () => {
    if (!user) return navigate("/login");
    setError("");
    setLoading(true);
    try {
      // Construit le payload de la commande
      const orderPayload = {
        items: items.map((i) => ({
          product_id: i.product.id,
          quantity: i.quantity,
          unit_price: i.product.price,
        })),
      };

      // 1. Crée la commande (brouillon)
      const orderRes = await createOrder(orderPayload);
      const order = orderRes.data;

      // 2. Simulation du paiement
      const payRes = await processPayment(order.id);
      const payment = payRes.data;

      if (payment.status === "success") {
        setSuccess("✅ Commande validée ! Votre paiement a été accepté.");
        clearCart();
        setTimeout(() => navigate("/mes-commandes"), 2500);
      } else {
        setError("❌ Le paiement a été refusé. Veuillez réessayer.");
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Une erreur est survenue lors du paiement.");
    } finally {
      setLoading(false);
    }
  };

  if (items.length === 0 && !success) {
    return (
      <Layout>
        <div className="text-center py-24">
          <ShoppingCart className="h-20 w-20 text-gray-200 mx-auto mb-5" />
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Votre panier est vide</h2>
          <p className="text-gray-500 mb-6">Ajoutez des produits depuis le catalogue</p>
          <Button onClick={() => navigate("/catalogue")}>Voir le catalogue</Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Mon Panier</h1>
        <p className="text-gray-500 mt-1">{items.length} article{items.length !== 1 ? "s" : ""}</p>
      </div>

      {success && (
        <div className="bg-green-50 border border-green-300 text-green-800 px-6 py-4 rounded-xl mb-6 text-center font-medium">
          {success}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Liste des articles */}
        <div className="lg:col-span-2 space-y-4">
          {items.map(({ product, quantity }) => (
            <div key={product.id} className="bg-white rounded-2xl border border-gray-200 p-4 flex items-center gap-4">
              {/* Image catégorie */}
              <div className="h-16 w-16 rounded-xl overflow-hidden flex-shrink-0">
                <img
                  src={getCategoryImage(product.category)}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Infos produit */}
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 truncate">{product.name}</h3>
                <p className="text-sm text-gray-500">{Number(product.price).toFixed(2)} € / {product.unit}</p>
              </div>

              {/* Contrôle quantité */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => updateQuantity(product.id, quantity - 1)}
                  className="h-8 w-8 rounded-full border border-gray-200 flex items-center justify-center hover:bg-gray-50 transition-colors"
                >
                  <Minus className="h-3.5 w-3.5" />
                </button>
                <span className="w-8 text-center font-semibold text-sm">{quantity}</span>
                <button
                  onClick={() => updateQuantity(product.id, quantity + 1)}
                  className="h-8 w-8 rounded-full border border-gray-200 flex items-center justify-center hover:bg-gray-50 transition-colors"
                >
                  <Plus className="h-3.5 w-3.5" />
                </button>
              </div>

              {/* Sous-total */}
              <div className="text-right min-w-16">
                <p className="font-bold text-primary-700">{(product.price * quantity).toFixed(2)} €</p>
              </div>

              {/* Supprimer */}
              <button
                onClick={() => removeItem(product.id)}
                className="p-2 text-gray-400 hover:text-red-500 transition-colors"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>

        {/* Récapitulatif */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-2xl border border-gray-200 p-6 sticky top-24">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Récapitulatif</h2>
            
            <div className="space-y-2 mb-4">
              {items.map(({ product, quantity }) => (
                <div key={product.id} className="flex justify-between text-sm text-gray-600">
                  <span className="truncate mr-2">{product.name} × {quantity}</span>
                  <span className="font-medium flex-shrink-0">{(product.price * quantity).toFixed(2)} €</span>
                </div>
              ))}
            </div>

            <div className="border-t border-gray-200 pt-4 mb-6">
              <div className="flex justify-between font-bold text-lg">
                <span>Total</span>
                <span className="text-primary-700">{totalPrice.toFixed(2)} €</span>
              </div>
              <p className="text-xs text-gray-400 mt-1">Paiement simulé (données fictives)</p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg mb-4">
                {error}
              </div>
            )}

            <Button className="w-full" size="lg" onClick={handleCheckout} disabled={loading}>
              {loading ? "Traitement en cours..." : "Commander & Payer"}
            </Button>

            <Button
              variant="ghost"
              className="w-full mt-2"
              onClick={() => navigate("/catalogue")}
            >
              Continuer mes achats
            </Button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
