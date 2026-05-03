import apiClient from "./client";

// POST /api/v1/orders
export const createOrder = (orderData) =>
  apiClient.post("/api/v1/orders", orderData);

// GET /api/v1/orders
export const getOrders = () => apiClient.get("/api/v1/orders");

// GET /api/v1/orders/:id
export const getOrderById = (id) => apiClient.get(`/api/v1/orders/${id}`);

// PATCH /api/v1/orders/:id/status  [Auth Producer]
export const updateOrderStatus = (id, status) =>
  apiClient.patch(`/api/v1/orders/${id}/status`, { status });

// GET /api/v1/orders/producer  [Auth Producer]
export const getProducerOrders = (status) => {
  const params = status ? { status } : {};
  return apiClient.get("/api/v1/orders/producer", { params });
};

// POST /api/v1/payments
export const processPayment = (orderId) =>
  apiClient.post("/api/v1/payments", { order_id: orderId });
