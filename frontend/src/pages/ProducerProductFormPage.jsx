import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Save } from "lucide-react";
import { getProductById, createProduct, updateProduct } from "../api/products";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import ErrorState from "../components/ui/ErrorState";
import Layout from "../components/Layout";
import { getErrorMessage } from "../api/errors";

const CATEGORIES = [
  { value: "fruits", label: "Fruits" },
  { value: "legumes", label: "Légumes" },
  { value: "viandes", label: "Viandes" },
  { value: "poissons", label: "Poissons" },
  { value: "produits_laitiers", label: "Produits laitiers" },
  { value: "epicerie", label: "Épicerie" },
  { value: "boissons", label: "Boissons" },
  { value: "autres", label: "Autres" },
];

const UNITS = [
  { value: "kg", label: "Kilogramme", hint: "Vendu au poids — ex : pommes, viande, légumes" },
  { value: "g", label: "Gramme", hint: "Petits poids — ex : épices, herbes séchées" },
  { value: "piece", label: "Pièce", hint: "Vendu à l'unité — ex : œufs, fromages, salades" },
  { value: "litre", label: "Litre", hint: "Vendu en volume — ex : lait, jus, huile" },
  { value: "bouquet", label: "Bouquet", hint: "Vendu en bouquet — ex : herbes fraîches, fleurs" },
  { value: "boite", label: "Boîte", hint: "Vendu en boîte ou pack — ex : barquette d'œufs, conserves" },
];

// Suggestion d'unité par défaut selon la catégorie
const DEFAULT_UNIT_BY_CATEGORY = {
  fruits: "kg",
  legumes: "kg",
  viandes: "kg",
  poissons: "kg",
  produits_laitiers: "litre",
  epicerie: "piece",
  boissons: "litre",
  autres: "piece",
};

const EMPTY_FORM = {
  name: "",
  description: "",
  category: "fruits",
  price: "",
  stock_quantity: "",
  unit: "piece",
  is_active: true,
};

export default function ProducerProductFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState(EMPTY_FORM);
  const [loading, setLoading] = useState(isEdit);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    if (!isEdit) return;
    setLoading(true);
    getProductById(id)
      .then((res) => {
        const p = res.data;
        setForm({
          name: p.name,
          description: p.description || "",
          category: p.category,
          price: String(p.price),
          stock_quantity: String(p.stock_quantity),
          unit: p.unit,
          is_active: p.is_active,
        });
      })
      .catch((err) => setLoadError(getErrorMessage(err, "Impossible de charger ce produit.")))
      .finally(() => setLoading(false));
  }, [id, isEdit]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => {
      const next = { ...prev, [name]: type === "checkbox" ? checked : value };
      // En création : suggère automatiquement une unité adaptée à la catégorie choisie
      if (!isEdit && name === "category" && DEFAULT_UNIT_BY_CATEGORY[value]) {
        next.unit = DEFAULT_UNIT_BY_CATEGORY[value];
      }
      return next;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const payload = {
        name: form.name.trim(),
        description: form.description.trim() || null,
        category: form.category,
        price: Number(form.price),
        stock_quantity: Number(form.stock_quantity),
        unit: form.unit,
      };
      if (isEdit) {
        payload.is_active = form.is_active;
        await updateProduct(id, payload);
      } else {
        await createProduct(payload);
      }
      navigate("/dashboard");
    } catch (err) {
      setError(getErrorMessage(err, "Impossible d'enregistrer le produit."));
      setSubmitting(false);
    }
  };

  if (loadError) {
    return (
      <Layout>
        <div className="max-w-md mx-auto">
          <ErrorState message={loadError} />
          <div className="text-center">
            <Button variant="outline" onClick={() => navigate("/dashboard")}>
              <ArrowLeft className="h-4 w-4 mr-2" /> Retour au dashboard
            </Button>
          </div>
        </div>
      </Layout>
    );
  }

  if (loading) {
    return (
      <Layout>
        <div className="max-w-2xl mx-auto space-y-4">
          <div className="h-8 bg-gray-200 rounded animate-pulse w-48" />
          <div className="bg-white rounded-2xl border border-gray-200 h-96 animate-pulse" />
        </div>
      </Layout>
    );
  }

  const selectedUnitLabel = (UNITS.find((u) => u.value === form.unit)?.label || form.unit).toLowerCase();

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <button
          onClick={() => navigate("/dashboard")}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-primary-600 mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> Retour au dashboard
        </button>

        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          {isEdit ? "Modifier le produit" : "Ajouter un produit"}
        </h1>

        <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-gray-200 p-6 space-y-5">
          <Input
            label="Nom du produit"
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="Ex : Pommes Golden bio"
            required
            maxLength={200}
          />

          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-gray-700">Description (optionnel)</label>
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              rows={3}
              placeholder="Origine, mode de production, conseils..."
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 resize-none"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-gray-700">Catégorie</label>
              <select
                name="category"
                value={form.category}
                onChange={handleChange}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 bg-white"
              >
                {CATEGORIES.map((c) => (
                  <option key={c.value} value={c.value}>{c.label}</option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-gray-700">Unité de vente</label>
              <select
                name="unit"
                value={form.unit}
                onChange={handleChange}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 bg-white"
              >
                {UNITS.map((u) => (
                  <option key={u.value} value={u.value}>{u.label}</option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-0.5">
                {UNITS.find((u) => u.value === form.unit)?.hint}
              </p>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 text-blue-700 text-xs px-3 py-2 rounded-lg">
            Le prix et le stock sont exprimés dans la même unité que celle sélectionnée ci-dessus ({selectedUnitLabel}).
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label={`Prix par ${selectedUnitLabel} (€)`}
              name="price"
              type="number"
              step="0.01"
              min="0"
              value={form.price}
              onChange={handleChange}
              placeholder="0.00"
              required
            />
            <Input
              label={`Stock disponible (en ${selectedUnitLabel})`}
              name="stock_quantity"
              type="number"
              step={form.unit === "piece" || form.unit === "boite" || form.unit === "bouquet" ? "1" : "0.001"}
              min="0"
              value={form.stock_quantity}
              onChange={handleChange}
              placeholder="0"
              required
            />
          </div>

          {isEdit && (
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                name="is_active"
                checked={form.is_active}
                onChange={handleChange}
                className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">Produit visible au catalogue</span>
            </label>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div className="flex items-center justify-end gap-3 pt-2 border-t border-gray-100">
            <Button type="button" variant="ghost" onClick={() => navigate("/dashboard")}>
              Annuler
            </Button>
            <Button type="submit" disabled={submitting} className="gap-2">
              <Save className="h-4 w-4" />
              {submitting ? "Enregistrement..." : isEdit ? "Enregistrer" : "Créer le produit"}
            </Button>
          </div>
        </form>
      </div>
    </Layout>
  );
}
