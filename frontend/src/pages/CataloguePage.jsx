import { useState, useEffect, useCallback } from "react";
import { Search, Filter, ShoppingCart, MapPin } from "lucide-react";
import { getProducts } from "../api/products";
import { useCart } from "../context/CartContext";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import ErrorState from "../components/ui/ErrorState";
import Layout from "../components/Layout";
import { getCategoryImage } from "../lib/categoryImages";
import { getErrorMessage } from "../api/errors";

const CATEGORIES = [
  { value: "", label: "Toutes" },
  { value: "fruits", label: "Fruits" },
  { value: "legumes", label: "Légumes" },
  { value: "viandes", label: "Viandes" },
  { value: "poissons", label: "Poissons" },
  { value: "produits_laitiers", label: "Laitiers" },
  { value: "epicerie", label: "Épicerie" },
  { value: "boissons", label: "Boissons" },
  { value: "autres", label: "Autres" },
];

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
      {/* Image produit */}
      <div className="h-44 overflow-hidden">
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

        {product.producer && (
          <div className="flex items-center gap-1 text-xs text-gray-500 mb-3">
            <MapPin className="h-3 w-3" />
            <span>{product.producer.farm_name || "Producteur local"}</span>
          </div>
        )}

        <div className="flex items-center justify-between mt-auto pt-3 border-t border-gray-100">
          <div>
            <span className="text-lg font-bold text-primary-700">{Number(product.price).toFixed(2)} €</span>
            <span className="text-gray-400 text-xs ml-1">/ {product.unit}</span>
          </div>
          <Button
            size="sm"
            onClick={handleAdd}
            disabled={!product.is_active || product.stock_quantity <= 0}
            className={added ? "bg-green-600 hover:bg-green-700" : ""}
          >
            {added ? "✓ Ajouté" : <><ShoppingCart className="h-3.5 w-3.5 mr-1" />Ajouter</>}
          </Button>
        </div>

        {product.stock_quantity <= 0 && (
          <p className="text-xs text-red-500 mt-1 text-center">Rupture de stock</p>
        )}
      </div>
    </div>
  );
}

export default function CataloguePage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [error, setError] = useState("");

  const fetchProducts = useCallback(() => {
    setLoading(true);
    setError("");
    getProducts()
      .then((res) => setProducts(res.data))
      .catch((err) => setError(getErrorMessage(err, "Impossible de charger les produits.")))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);

  const filtered = products.filter((p) => {
    const matchSearch =
      !search ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.description?.toLowerCase().includes(search.toLowerCase());
    const matchCat = !category || p.category === category;
    return matchSearch && matchCat;
  });

  return (
    <Layout>
      {/* En-tête */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-1">Catalogue</h1>
        <p className="text-gray-500">Découvrez les produits frais de nos producteurs locaux</p>
      </div>

      {/* Filtres */}
      <div className="flex flex-col sm:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher un produit..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
          />
        </div>
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <Filter className="h-4 w-4 text-gray-400 flex-shrink-0" />
          {CATEGORIES.map((cat) => (
            <button
              key={cat.value}
              onClick={() => setCategory(cat.value)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                category === cat.value
                  ? "bg-primary-600 text-white"
                  : "bg-white border border-gray-200 text-gray-600 hover:border-primary-400"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Contenu */}
      {loading && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-200 h-64 animate-pulse" />
          ))}
        </div>
      )}

      {error && <ErrorState message={error} onRetry={fetchProducts} />}

      {!loading && !error && (
        <>
          <p className="text-sm text-gray-500 mb-4">{filtered.length} produit{filtered.length !== 1 ? "s" : ""} trouvé{filtered.length !== 1 ? "s" : ""}</p>
          {filtered.length === 0 ? (
            <div className="text-center py-16 text-gray-500">
              <span className="text-4xl mb-4 block">🔍</span>
              Aucun produit ne correspond à votre recherche
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filtered.map((p) => <ProductCard key={p.id} product={p} />)}
            </div>
          )}
        </>
      )}
    </Layout>
  );
}
