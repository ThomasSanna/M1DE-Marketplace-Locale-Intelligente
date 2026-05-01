// Images réelles par catégorie (Unsplash — libres de droit, optimisées en taille)
const CATEGORY_IMAGES = {
  fruits: "https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=400&h=300&fit=crop",
  legumes: "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=300&fit=crop",
  viandes: "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=400&h=300&fit=crop",
  poissons: "https://images.unsplash.com/photo-1510130113-83a4ce8f8c14?w=400&h=300&fit=crop",
  produits_laitiers: "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400&h=300&fit=crop",
  epicerie: "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400&h=300&fit=crop",
  boissons: "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop",
  autres: "https://images.unsplash.com/photo-1488459716781-31db52582fe9?w=400&h=300&fit=crop",
};

const CATEGORY_LABELS = {
  fruits: "Fruits",
  legumes: "Légumes",
  viandes: "Viandes",
  poissons: "Poissons",
  produits_laitiers: "Laitiers",
  epicerie: "Épicerie",
  boissons: "Boissons",
  autres: "Autres",
};

export function getCategoryImage(category) {
  return CATEGORY_IMAGES[category] || CATEGORY_IMAGES.autres;
}

export function getCategoryLabel(category) {
  return CATEGORY_LABELS[category] || category;
}

export default CATEGORY_IMAGES;
