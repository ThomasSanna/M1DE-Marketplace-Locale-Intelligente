import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Store, ArrowRight } from "lucide-react";
import { createProducerProfile } from "../api/products";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import Layout from "../components/Layout";
import { getErrorMessage } from "../api/errors";

const REGIONS = [
  "Île-de-France", "Auvergne-Rhône-Alpes", "Nouvelle-Aquitaine", "Occitanie",
  "Hauts-de-France", "Grand Est", "Provence-Alpes-Côte d'Azur", "Pays de la Loire",
  "Bretagne", "Normandie", "Bourgogne-Franche-Comté", "Centre-Val de Loire",
  "Corse", "Guadeloupe", "Martinique", "Guyane", "La Réunion", "Mayotte",
];

export default function ProducerSetupPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    farm_name: "",
    location_city: "",
    location_region: "Île-de-France",
    description: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await createProducerProfile({
        farm_name: form.farm_name.trim(),
        location_city: form.location_city.trim(),
        location_region: form.location_region,
        description: form.description.trim() || null,
      });
      navigate("/dashboard");
    } catch (err) {
      setError(getErrorMessage(err, "Impossible de créer votre profil producteur."));
      setSubmitting(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-xl mx-auto">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-primary-100 mb-4">
            <Store className="h-8 w-8 text-primary-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Bienvenue sur MarchéLocal !
          </h1>
          <p className="text-gray-500">
            Avant de commencer à vendre, complétez votre profil de producteur.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-gray-200 p-6 space-y-5">
          <Input
            label="Nom de votre exploitation / boutique"
            name="farm_name"
            value={form.farm_name}
            onChange={handleChange}
            placeholder="Ex : Ferme des Tilleuls"
            required
            maxLength={200}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Ville"
              name="location_city"
              value={form.location_city}
              onChange={handleChange}
              placeholder="Ex : Lyon"
              required
              maxLength={100}
            />
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-gray-700">Région</label>
              <select
                name="location_region"
                value={form.location_region}
                onChange={handleChange}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 bg-white"
              >
                {REGIONS.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-gray-700">Description (optionnel)</label>
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              rows={3}
              placeholder="Présentez votre ferme, vos méthodes de production, vos spécialités..."
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 resize-none"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <Button type="submit" disabled={submitting} className="w-full gap-2" size="lg">
            {submitting ? "Création..." : <>Créer mon profil <ArrowRight className="h-4 w-4" /></>}
          </Button>
        </form>
      </div>
    </Layout>
  );
}
