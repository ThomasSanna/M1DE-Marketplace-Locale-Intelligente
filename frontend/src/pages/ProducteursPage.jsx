import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { MapPin, ArrowRight } from "lucide-react";
import { getProducers } from "../api/products";
import ErrorState from "../components/ui/ErrorState";
import Layout from "../components/Layout";
import { getErrorMessage } from "../api/errors";

export default function ProducteursPage() {
  const [producers, setProducers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchProducers = useCallback(() => {
    setLoading(true);
    setError("");
    getProducers()
      .then((res) => setProducers(res.data))
      .catch((err) => setError(getErrorMessage(err, "Impossible de charger les producteurs.")))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchProducers(); }, [fetchProducers]);

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-1">Nos Producteurs</h1>
        <p className="text-gray-500">Découvrez les artisans et agriculteurs partenaires</p>
      </div>

      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-200 h-48 animate-pulse" />
          ))}
        </div>
      )}

      {error && <ErrorState message={error} onRetry={fetchProducers} />}

      {!loading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {producers.map((producer) => (
            <Link
              key={producer.id}
              to={`/producteurs/${producer.id}`}
              className="block bg-white rounded-2xl border border-gray-200 p-6 hover:shadow-md transition-all hover:border-primary-300 group"
            >
              <div className="h-14 w-14 bg-primary-100 rounded-2xl flex items-center justify-center text-2xl mb-4">
                🌾
              </div>
              <h3 className="font-bold text-gray-900 text-lg mb-1 group-hover:text-primary-600 transition-colors">
                {producer.farm_name}
              </h3>
              <div className="flex items-center gap-1 text-sm text-gray-500 mb-2">
                <MapPin className="h-3.5 w-3.5" />
                {producer.location_city}, {producer.location_region}
              </div>
              {producer.description && (
                <p className="text-sm text-gray-500 line-clamp-2 mb-4">{producer.description}</p>
              )}
              <div className="flex items-center text-primary-600 text-sm font-medium">
                Voir la boutique <ArrowRight className="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          ))}
        </div>
      )}

      {!loading && !error && producers.length === 0 && (
        <div className="text-center py-16 text-gray-500">
          <span className="text-4xl mb-4 block">🌾</span>
          Aucun producteur pour le moment
        </div>
      )}
    </Layout>
  );
}
