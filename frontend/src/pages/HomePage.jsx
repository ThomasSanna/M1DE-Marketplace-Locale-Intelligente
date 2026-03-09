import { Link } from "react-router-dom";
import { ArrowRight, Leaf, ShieldCheck, Truck } from "lucide-react";
import { Button } from "../components/ui/Button";
import Layout from "../components/Layout";

export default function HomePage() {
  return (
    <Layout fullWidth>
      {/* Hero */}
      <section className="bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="text-center py-16 sm:py-24">
        <span className="inline-block bg-primary-100 text-primary-700 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
          🌿 Marketplace Locale Intelligente
        </span>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 leading-tight mb-6">
          Des produits frais,<br />
          <span className="text-primary-600">directement des producteurs</span>
        </h1>
        <p className="text-lg text-gray-500 max-w-xl mx-auto mb-8">
          Achetez en direct auprès des agriculteurs et artisans de votre région.
          Frais, local et responsable.
        </p>
        <div className="flex items-center justify-center gap-4 flex-wrap">
          <Link to="/catalogue">
            <Button size="lg" className="gap-2">
              Explorer le catalogue <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link to="/producteurs">
            <Button size="lg" variant="outline">
              Voir les producteurs
            </Button>
          </Link>
        </div>
      </div>
      </div>
      </section>

      {/* Avantages */}
      <section className="bg-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { icon: <Leaf className="h-7 w-7 text-primary-600" />, title: "100% Local", desc: "Tous nos producteurs sont situés dans votre région pour vous garantir fraîcheur et circuit court." },
          { icon: <ShieldCheck className="h-7 w-7 text-primary-600" />, title: "Paiement sécurisé", desc: "Vos transactions sont protégées. Paiement simulé avec détection d'anomalies intégrée." },
          { icon: <Truck className="h-7 w-7 text-primary-600" />, title: "Livraison rapide", desc: "Vos commandes sont préparées par les producteurs et expédiées dans les meilleurs délais." },
        ].map((item, i) => (
          <div key={i} className="bg-white rounded-2xl border border-gray-200 p-6 text-center hover:shadow-md transition-shadow">
            <div className="flex justify-center mb-4">
              <div className="bg-primary-50 rounded-xl p-3">{item.icon}</div>
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
            <p className="text-sm text-gray-500">{item.desc}</p>
          </div>
        ))}
      </div>
      </div>
      </section>

      {/* CTA producteur */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-700 mt-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center text-white">
        <h2 className="text-2xl font-bold mb-3">Vous êtes producteur ?</h2>
        <p className="text-primary-100 mb-6 max-w-md mx-auto">
          Rejoignez notre marketplace et vendez vos produits directement à des milliers de clients locaux.
        </p>
        <Link to="/register">
          <Button variant="outline" size="lg" className="bg-white text-primary-700 border-white hover:bg-primary-50">
            Devenir producteur
          </Button>
        </Link>
      </div>
      </section>
    </Layout>
  );
}
