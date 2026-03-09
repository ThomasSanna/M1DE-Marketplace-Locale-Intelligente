import Navbar from "./Navbar";

export default function Layout({ children, fullWidth = false }) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Navbar />
      <main className="flex-1 w-full">
        {fullWidth ? children : (
          <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </div>
        )}
      </main>
      <footer className="bg-white border-t border-gray-200 py-6 mt-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-500">
          © 2026 MarchéLocal – Marketplace Locale Intelligente
        </div>
      </footer>
    </div>
  );
}
