import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

// Products
export const getProducts = () => api.get("/products");
export const getProduct = (id) => api.get(`/products/${id}`);
export const createProduct = (data) => api.post("/products", data);
export const updateProduct = (id, data) => api.put(`/products/${id}`, data);
export const deleteProduct = (id) => api.delete(`/products/${id}`);

// Groups
export const getGroups = (params) => api.get("/groups", { params });
export const getUnmappedGroups = () => api.get("/groups/unmapped");
export const mapProductToGroup = (productId, data) =>
  api.post(`/products/${productId}/map`, data);
export const unmapProduct = (productId) =>
  api.delete(`/products/${productId}/unmap`);
export const removeBotAndDeleteGroup = (telegramGroupId) =>
  api.delete(`/groups/${telegramGroupId}`);
export const sendGroupMessage = (telegramGroupId, text) =>
  api.post(`/groups/${telegramGroupId}/message`, { text });

// Subscriptions
export const getSubscriptions = (params) =>
  api.get("/subscriptions", { params });
export const createSubscription = (data, forceRenew = false) => 
  api.post("/subscribe", data, { params: { force_renew: forceRenew ? 1 : 0 } });
export const cancelSubscription = (id) =>
  api.post(`/subscriptions/${id}/cancel`);

// Users
export const getUsers = () => api.get("/users");

export default api;
