import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, Edit2, Trash2, Package, AlertCircle, MapPin } from "lucide-react";
import { getMyProducer, getProducerProducts, deleteProduct } from "../api/products";
import { useAuth } from "../context/AuthContext";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import ErrorState from "../components/ui/ErrorState";
import Layout from "../components/Layout";
import { getCategoryImage } from "../lib/categoryImages";
import { getErrorMessage } from "../api/errors";

export default function ProducerDashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [producer, setProducer] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  const fetchData = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError("");
    try {
      const myProducer = await getMyProducer(user.id);
      if (!myProducer) {
        setError("Aucun profil producteur n'est associé à votre compte. Contactez l'administrateur.");
        setLoading(false);
        return;
      }
      setProducer(myProducer);
      const res = await getProducerProducts(myProducer.id);
      setProducts(res.data);
    } catch (err) {
      setError(getErrorMessage(err, "Impossible de charger votre boutique."));
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleDelete = async (productId) => {
    if (!window.confirm("Voulez-vous vraiment désactiver ce produit ?")) return;
    setDeletingId(productId);
    try {
      await deleteProduct(productId);
      setProducts((prev) => prev.filter((p) => p.id !== productId));
    } catch (err) {
      alert(getErrorMessage(err, "Impossible de supprimer ce produit."));
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="space-y-4">
          <div className="h-10 bg-gray-200 rounded animate-pulse w-64" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="bg-white rounded-2xl border border-gray-200 h-24 animate-pulse" />
            ))}
          </div>
          <div className="bg-white rounded-2xl border border-gray-200 h-64 animate-pulse" />
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <ErrorState message={error} onRetry={fetchData} />
      </Layout>
    );
  }

  const activeCount = products.filter((p) => p.is_active).length;
  const lowStockCount = products.filter((p) => p.is_active && Number(p.stock_quantity) < 5).length;

  return (
    <Layout>
      {/* En-tête */}
      <div className="flex items-start justify-between flex-wrap gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-1">Mon Dashboard</h1>
          {producer && (
            <p className="text-gray-500 flex items-center gap-1 text-sm">
              <MapPin className="h-4 w-4" />
              {producer.farm_name} — {producer.location_city}, {producer.location_region}
            </p>
          )}
        </div>
        <Button onClick={() => navigate("/dashboard/produits/new")} className="gap-2">
          <Plus className="h-4 w-4" /> Ajouter un produit
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-2xl border border-gray-200 p-5">
          <div className="flex items-center gap-3">
            <div className="bg-primary-50 rounded-xl p-2.5">
              <Package className="h-5 w-5 text-primary-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{products.length}</p>
              <p className="text-xs text-gray-500">Produits au catalogue</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 p-5">
          <div className="flex items-center gap-3">
            <div className="bg-green-50 rounded-xl p-2.5">
              <Package className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{activeCount}</p>
              <p className="text-xs text-gray-500">Produits actifs</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-2xl border border-gray-200 p-5">
          <div className="flex items-center gap-3">
            <div className="bg-orange-50 rounded-xl p-2.5">
              <AlertCircle className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{lowStockCount}</p>
              <p className="text-xs text-gray-500">Stock faible (&lt; 5)</p>
            </div>
          </div>
        </div>
      </div>

      {/* Liste produits */}
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Mes produits</h2>

      {products.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-gray-200">
          <Package className="h-16 w-16 text-gray-200 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Aucun produit pour le moment</h3>
          <p className="text-gray-500 mb-6">Commencez par ajouter votre premier produit au catalogue</p>
          <Button onClick={() => navigate("/dashboard/produits/new")} className="gap-2">
            <Plus className="h-4 w-4" /> Ajouter un produit
          </Button>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden">
          <div className="divide-y divide-gray-100">
            {products.map((product) => (
              <div key={product.id} className="p-4 flex items-center gap-4 hover:bg-gray-50 transition-colors">
                <div className="h-14 w-14 rounded-xl overflow-hidden flex-shrink-0">
                  <img
                    src={getCategoryImage(product.category)}
                    alt={product.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <h3 className="font-semibold text-gray-900 text-sm truncate">{product.name}</h3>
                    {!product.is_active && <Badge variant="default">Inactif</Badge>}
                  </div>
                  <p className="text-xs text-gray-500">
                    {product.category} · Stock : {Number(product.stock_quantity)} {product.unit}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-bold text-primary-700">{Number(product.price).toFixed(2)} €</p>
                  <p className="text-xs text-gray-400">/ {product.unit}</p>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => navigate(`/dashboard/produits/${product.id}/edit`)}
                    className="p-2 text-gray-400 hover:text-primary-600 transition-colors"
                    title="Modifier"
                  >
                    <Edit2 className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(product.id)}
                    disabled={deletingId === product.id}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors disabled:opacity-30"
                    title="Désactiver"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </Layout>
  );
}
