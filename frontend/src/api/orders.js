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

// POST /api/v1/payments
export const processPayment = (orderId) =>
  apiClient.post("/api/v1/payments", { order_id: orderId });
