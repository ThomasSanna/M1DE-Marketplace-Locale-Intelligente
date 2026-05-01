import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { MapPin, ArrowLeft, ShoppingCart } from "lucide-react";
import { getProducers, getProducerProducts } from "../api/products";
import { useCart } from "../context/CartContext";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import ErrorState from "../components/ui/ErrorState";
import Layout from "../components/Layout";
import { getCategoryImage } from "../lib/categoryImages";
import { getErrorMessage } from "../api/errors";

function ProductCard({ product }) {
  const { addItem } = useCart();
  const [added, setAdded] = useState(false);

  const handleAdd = () => {
    addItem(product, 1);
    setAdded(true);
    setTimeout(() => setAdded(false), 1500);
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden hover:shadow-md transition-shadow flex flex-col">
      <div className="h-36 overflow-hidden">
        <img
          src={getCategoryImage(product.category)}
          alt={product.name}
          className="w-full h-full object-cover"
          loading="lazy"
        />
      </div>
      <div className="p-4 flex flex-col flex-1">
        <div className="flex items-start justify-between gap-2 mb-1">
          <h3 className="font-semibold text-gray-900 text-sm leading-tight">{product.name}</h3>
          <Badge variant="primary">{product.category}</Badge>
        </div>
        {product.description && (
          <p className="text-gray-500 text-xs line-clamp-2 mb-2">{product.description}</p>
        )}
        <div className="flex items-center justify-between mt-auto pt-3 border-t border-gray-100">
          <div>
            <span className="text-base font-bold text-primary-700">{Number(product.price).toFixed(2)} €</span>
            <span className="text-gray-400 text-xs ml-1">/ {product.unit}</span>
          </div>
          <Button
            size="sm"
            onClick={handleAdd}
            disabled={!product.is_active || product.stock_quantity <= 0}
            className={added ? "bg-green-600 hover:bg-green-700" : ""}
          >
            {added ? "Ajouté" : <><ShoppingCart className="h-3.5 w-3.5 mr-1" />Ajouter</>}
          </Button>
        </div>
        {product.stock_quantity <= 0 && (
          <p className="text-xs text-red-500 mt-1 text-center">Rupture de stock</p>
        )}
      </div>
    </div>
  );
}

export default function ProducerDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [producer, setProducer] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");

    Promise.all([getProducers(), getProducerProducts(id)])
      .then(([producersRes, productsRes]) => {
        const found = producersRes.data.find((p) => p.id === id);
        if (!found) {
          setError("Producteur introuvable.");
          return;
        }
        setProducer(found);
        setProducts(productsRes.data.filter((p) => p.is_active));
      })
      .catch((err) => setError(getErrorMessage(err, "Impossible de charger ce producteur.")))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto space-y-4">
          <div className="h-8 bg-gray-200 rounded animate-pulse w-48" />
          <div className="bg-white rounded-2xl border border-gray-200 h-32 animate-pulse" />
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="bg-white rounded-2xl border border-gray-200 h-52 animate-pulse" />
            ))}
          </div>
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
            <Button variant="outline" onClick={() => navigate("/producteurs")}>
              <ArrowLeft className="h-4 w-4 mr-2" /> Retour aux producteurs
            </Button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => navigate("/producteurs")}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-primary-600 mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> Retour aux producteurs
        </button>

        {/* En-tête producteur */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 mb-8 flex items-start gap-5">
          <div className="h-16 w-16 bg-primary-100 rounded-2xl flex items-center justify-center text-3xl flex-shrink-0">
            🌾
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl font-bold text-gray-900 mb-1">{producer.farm_name}</h1>
            <div className="flex items-center gap-1 text-sm text-gray-500 mb-2">
              <MapPin className="h-4 w-4" />
              {producer.location_city}, {producer.location_region}
            </div>
            {producer.description && (
              <p className="text-sm text-gray-600">{producer.description}</p>
            )}
            {producer.user && (
              <p className="text-xs text-gray-400 mt-2">
                Géré par {producer.user.first_name} {producer.user.last_name}
              </p>
            )}
          </div>
          <Badge variant="success" className="flex-shrink-0">
            {products.length} produit{products.length !== 1 ? "s" : ""}
          </Badge>
        </div>

        {/* Produits */}
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Produits disponibles</h2>

        {products.length === 0 ? (
          <div className="text-center py-16 text-gray-500 bg-white rounded-2xl border border-gray-200">
            <span className="text-4xl mb-4 block">📦</span>
            Aucun produit disponible pour ce producteur
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {products.map((p) => <ProductCard key={p.id} product={p} />)}
          </div>
        )}
      </div>
    </Layout>
  );
}
