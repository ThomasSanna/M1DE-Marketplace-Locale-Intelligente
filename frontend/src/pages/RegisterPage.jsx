import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Store } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { getErrorMessage } from "../api/errors";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    phone: "",
    role: "client",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(form);
      navigate("/login");
    } catch (err) {
      setError(getErrorMessage(err, "Erreur lors de l'inscription."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-3">
            <Store className="h-12 w-12 text-primary-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">
            Marché<span className="text-primary-600">Local</span>
          </h1>
          <p className="text-gray-500 mt-1 text-sm">Créez votre compte</p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Prénom"
                name="first_name"
                value={form.first_name}
                onChange={handleChange}
                placeholder="Jean"
                required
              />
              <Input
                label="Nom"
                name="last_name"
                value={form.last_name}
                onChange={handleChange}
                placeholder="Dupont"
                required
              />
            </div>

            <Input
              label="Email"
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="vous@exemple.fr"
              required
            />

            <Input
              label="Téléphone (optionnel)"
              type="tel"
              name="phone"
              value={form.phone}
              onChange={handleChange}
              placeholder="+33 6 00 00 00 00"
            />

            <Input
              label="Mot de passe"
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Minimum 8 caractères"
              required
            />

            {/* Rôle */}
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium text-gray-700">Vous êtes...</label>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { value: "client", label: "🛒 Client", desc: "J'achète des produits" },
                  { value: "producer", label: "🌾 Producteur", desc: "Je vends mes produits" },
                ].map((option) => (
                  <label
                    key={option.value}
                    className={`cursor-pointer border-2 rounded-xl p-3 text-center transition-all ${
                      form.role === option.value
                        ? "border-primary-500 bg-primary-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <input
                      type="radio"
                      name="role"
                      value={option.value}
                      onChange={handleChange}
                      className="sr-only"
                    />
                    <div className="font-medium text-sm">{option.label}</div>
                    <div className="text-xs text-gray-500 mt-0.5">{option.desc}</div>
                  </label>
                ))}
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            <Button type="submit" className="w-full" size="lg" disabled={loading}>
              {loading ? "Création du compte..." : "Créer mon compte"}
            </Button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            Déjà un compte ?{" "}
            <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
              Se connecter
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
