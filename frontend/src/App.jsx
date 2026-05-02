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
import ProducerDetailPage from './pages/ProducerDetailPage';
import ProducerDashboardPage from './pages/ProducerDashboardPage';
import ProducerProductFormPage from './pages/ProducerProductFormPage';

function FullPageSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin h-8 w-8 border-4 border-primary-600 border-t-transparent rounded-full" />
    </div>
  );
}

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <FullPageSpinner />;
  return user ? children : <Navigate to="/login" replace />;
}

function ProducerRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <FullPageSpinner />;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "producer") return <Navigate to="/catalogue" replace />;
  return children;
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
        <Route path="/producteurs/:id" element={<ProducerDetailPage />} />

        {/* Pages protégées (utilisateur connecté) */}
        <Route path="/panier" element={<PrivateRoute><PanierPage /></PrivateRoute>} />
        <Route path="/mes-commandes" element={<PrivateRoute><CommandesPage /></PrivateRoute>} />
        <Route path="/commandes/:id" element={<PrivateRoute><CommandeDetailPage /></PrivateRoute>} />

        {/* Pages producteur */}
        <Route path="/dashboard" element={<ProducerRoute><ProducerDashboardPage /></ProducerRoute>} />
        <Route path="/dashboard/produits/new" element={<ProducerRoute><ProducerProductFormPage /></ProducerRoute>} />
        <Route path="/dashboard/produits/:id/edit" element={<ProducerRoute><ProducerProductFormPage /></ProducerRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
