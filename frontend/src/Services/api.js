const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api").replace(/\/+$/, "");

const getHeaders = () => {
  const headers = {
    "Content-Type": "application/json",
  };
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      headers["Authorization"] = `Token ${token}`;
    }
    const sessionId = localStorage.getItem("session_id");
    if (sessionId) {
      headers["X-Session-ID"] = sessionId;
    }
  }
  return headers;
};

// Generic fetch handler
const request = async (endpoint, options = {}) => {
  const formattedEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${API_BASE_URL}${formattedEndpoint}`;
  const config = {
    ...options,
    headers: {
      ...getHeaders(),
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail ||
        errorData.error ||
        errorData.non_field_errors?.[0] ||
        `HTTP error! status: ${response.status}`
      );
    }
    return await response.json();
  } catch (err) {
    console.error(`API Request Error [${endpoint}]:`, err);
    throw err;
  }
};

export const api = {
  // ─── Auth APIs ────────────────────────────────────────────────────────────────
  login: (credentials) =>
    request(`/login/`, { method: "POST", body: JSON.stringify(credentials) }),
  signup: (userData) =>
    request(`/signup/`, { method: "POST", body: JSON.stringify(userData) }),
  getUserProfile: () => request(`/users/me/`),

  // ─── Public / User-Facing Product APIs ───────────────────────────────────────
  // /api/products/ always returns ONLY is_available=True products.
  // This endpoint is read-only and safe for all users (logged in or not).
  getProducts: (params = "") => request(`/products/${params}`),
  getProductBySlug: (slug) => request(`/products/${slug}/`),
  getCategories: () => request(`/categories/`),
  getBrands: () => request(`/brands/`),
  addReview: (productSlug, reviewData) =>
    request(`/products/${productSlug}/add_review/`, {
      method: "POST",
      body: JSON.stringify(reviewData),
    }),

  // ─── Cart APIs ────────────────────────────────────────────────────────────────
  getCart: () => request(`/cart/`),
  addToCart: (productId, quantity = 1) =>
    request(`/cart/add_item/`, {
      method: "POST",
      body: JSON.stringify({ product_id: productId, quantity }),
    }),
  updateCartItem: (itemId, quantity) =>
    request(`/cart/update_item/`, {
      method: "POST",
      body: JSON.stringify({ item_id: itemId, quantity }),
    }),
  removeCartItem: (itemId) =>
    request(`/cart/remove_item/`, {
      method: "POST",
      body: JSON.stringify({ item_id: itemId }),
    }),
  clearCart: () => request(`/cart/clear/`, { method: "POST" }),

  // ─── Orders & Checkout APIs ───────────────────────────────────────────────────
  createOrder: (orderData) =>
    request(`/orders/create_order/`, {
      method: "POST",
      body: JSON.stringify(orderData),
    }),
  getOrders: () => request(`/orders/`),
  getDashboardStats: () => request(`/orders/dashboard_stats/`),
  createPaymentIntent: (orderNumber) =>
    request(`/payments/create-intent/`, {
      method: "POST",
      body: JSON.stringify({ order_number: orderNumber }),
    }),

  // ─── Admin-Only APIs (/api/admin/...) ─────────────────────────────────────────
  //
  // These hit a COMPLETELY SEPARATE backend endpoint from /api/products/.
  // The public /api/products/ endpoint NEVER returns inactive products,
  // regardless of who is logged in. Admin management goes through /api/admin/products/.
  //
  // All admin endpoints require IsAdminUser permission on the backend.

  // Admin: Products management
  adminGetAllProducts: (params = "") => request(`/admin/products/${params}`),
  adminCreateProduct: (data) =>
    request(`/admin/products/`, { method: "POST", body: JSON.stringify(data) }),
  adminUpdateProduct: (slug, data) =>
    request(`/admin/products/${slug}/`, { method: "PATCH", body: JSON.stringify(data) }),
  adminDeleteProduct: (slug) =>
    request(`/admin/products/${slug}/`, { method: "DELETE" }),
  // Dedicated toggle action — atomically flips is_available without needing current value
  adminToggleProductAvailability: (slug) =>
    request(`/admin/products/${slug}/toggle_availability/`, { method: "PATCH" }),

  // Admin: Users management
  adminGetUsers: () => request(`/users/`),
  adminGetUserById: (id) => request(`/users/${id}/`),
  adminUpdateUser: (id, data) =>
    request(`/users/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),

  // Admin: Orders management
  adminGetOrders: () => request(`/orders/`),
  adminGetOrderById: (id) => request(`/orders/${id}/`),
  adminUpdateOrderStatus: (id, orderStatus) =>
    request(`/orders/${id}/`, {
      method: "PATCH",
      body: JSON.stringify({ order_status: orderStatus }),
    }),

  // Admin: Categories & Brands management
  adminCreateCategory: (data) =>
    request(`/categories/`, { method: "POST", body: JSON.stringify(data) }),
  adminUpdateCategory: (slug, data) =>
    request(`/categories/${slug}/`, { method: "PATCH", body: JSON.stringify(data) }),
  adminDeleteCategory: (slug) =>
    request(`/categories/${slug}/`, { method: "DELETE" }),
};
