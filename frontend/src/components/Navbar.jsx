import { Link, useNavigate } from "react-router-dom";
import { ShoppingCart, User, LogOut, Store } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { Button } from "./ui/Button";

export default function Navbar() {
  const { user, logout } = useAuth();
  const { totalItems } = useCart();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <Store className="h-7 w-7 text-primary-600" />
            <span className="font-bold text-lg text-gray-900">
              Marché<span className="text-primary-600">Local</span>
            </span>
          </Link>

          {/* Navigation centrale */}
          <nav className="hidden md:flex items-center gap-6">
            <Link to="/catalogue" className="text-sm text-gray-600 hover:text-primary-600 font-medium transition-colors">
              Catalogue
            </Link>
            <Link to="/producteurs" className="text-sm text-gray-600 hover:text-primary-600 font-medium transition-colors">
              Producteurs
            </Link>
            {user?.role === "producer" && (
              <Link to="/dashboard" className="text-sm text-gray-600 hover:text-primary-600 font-medium transition-colors">
                Mon Dashboard
              </Link>
            )}
          </nav>

          {/* Actions droite */}
          <div className="flex items-center gap-3">
            {/* Panier */}
            <Link to="/panier" className="relative p-2 text-gray-600 hover:text-primary-600 transition-colors">
              <ShoppingCart className="h-5 w-5" />
              {totalItems > 0 && (
                <span className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold">
                  {totalItems}
                </span>
              )}
            </Link>

            {user ? (
              <div className="flex items-center gap-2">
                <Link to="/profil" className="flex items-center gap-1 text-sm text-gray-700 hover:text-primary-600">
                  <User className="h-4 w-4" />
                  <span className="hidden sm:inline">{user.first_name}</span>
                </Link>
                <button
                  onClick={handleLogout}
                  className="p-2 text-gray-500 hover:text-red-600 transition-colors"
                  title="Se déconnecter"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" onClick={() => navigate("/login")}>
                  Connexion
                </Button>
                <Button size="sm" onClick={() => navigate("/register")}>
                  S'inscrire
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
