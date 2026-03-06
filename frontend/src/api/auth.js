import apiClient from "./client";

// POST /api/v1/auth/register
export const register = (userData) =>
  apiClient.post("/api/v1/auth/register", userData);

// POST /api/v1/auth/login  (form-urlencoded pour FastAPI OAuth2)
export const login = (email, password) => {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);
  return apiClient.post("/api/v1/auth/login", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
};

// GET /api/v1/users/me
export const getMe = () => apiClient.get("/api/v1/users/me");
