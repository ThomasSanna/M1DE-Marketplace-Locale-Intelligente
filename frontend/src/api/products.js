import apiClient from "./client";

// GET /api/v1/products
export const getProducts = (params = {}) =>
  apiClient.get("/api/v1/products", { params });

// GET /api/v1/products/:id
export const getProductById = (id) =>
  apiClient.get(`/api/v1/products/${id}`);

// POST /api/v1/products  [Auth Producer]
export const createProduct = (productData) =>
  apiClient.post("/api/v1/products", productData);

// PUT /api/v1/products/:id  [Auth Producer]
export const updateProduct = (id, productData) =>
  apiClient.put(`/api/v1/products/${id}`, productData);

// DELETE /api/v1/products/:id  [Auth Producer]
export const deleteProduct = (id) =>
  apiClient.delete(`/api/v1/products/${id}`);

// GET /api/v1/producers
export const getProducers = (params = {}) =>
  apiClient.get("/api/v1/producers", { params });

// GET /api/v1/producers/:id/products
export const getProducerProducts = (producerId) =>
  apiClient.get(`/api/v1/producers/${producerId}/products`);

// POST /api/v1/producers  [Auth Producer]
export const createProducerProfile = (producerData) =>
  apiClient.post("/api/v1/producers", producerData);

// Helper : retrouve le producteur lié au user connecté (via user_id)
export const getMyProducer = async (userId) => {
  const res = await getProducers({ limit: 1000 });
  return res.data.find((p) => p.user_id === userId) || null;
};
