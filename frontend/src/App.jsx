import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import CataloguePage from './pages/CataloguePage';
import PanierPage from './pages/PanierPage';
import ProducteursPage from './pages/ProducteursPage';
import CommandesPage from './pages/CommandesPage';
import CommandeDetailPage from './pages/CommandeDetailPage';

// Route protégée : redirige vers /login si non connecté
function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="animate-spin h-8 w-8 border-4 border-primary-600 border-t-transparent rounded-full" /></div>;
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Pages publiques */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/catalogue" element={<CataloguePage />} />
        <Route path="/producteurs" element={<ProducteursPage />} />

        {/* Pages protégées */}
        <Route path="/panier" element={<PrivateRoute><PanierPage /></PrivateRoute>} />
        <Route path="/mes-commandes" element={<PrivateRoute><CommandesPage /></PrivateRoute>} />
        <Route path="/commandes/:id" element={<PrivateRoute><CommandeDetailPage /></PrivateRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
