"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  FiBox, FiShoppingBag, FiClock, FiCheckCircle, FiUsers,
  FiTrendingUp, FiEdit2, FiTrash2, FiToggleLeft, FiToggleRight,
  FiRefreshCw, FiLogOut, FiPackage, FiAlertCircle, FiGrid,
  FiChevronRight, FiEye, FiEyeOff,
} from "react-icons/fi";
import { api } from "@/Services/api";

// ─── Auth Guard ───────────────────────────────────────────────────────────────
function useAdminGuard() {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const userType = localStorage.getItem("user_type");
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    if (!token || (userType !== "ADMIN" && !user?.is_staff)) {
      router.replace("/admin");
    } else {
      setAuthorized(true);
    }
  }, [router]);

  return authorized;
}

// ─── Tabs ─────────────────────────────────────────────────────────────────────
const TABS = [
  { id: "overview", label: "Overview", icon: FiGrid },
  { id: "products", label: "Products", icon: FiBox },
  { id: "orders", label: "Orders", icon: FiShoppingBag },
  { id: "users", label: "Users", icon: FiUsers },
];

// ─── Status badge ─────────────────────────────────────────────────────────────
function StatusBadge({ status }) {
  const map = {
    DELIVERED: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    PENDING: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    PROCESSING: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    CANCELLED: "bg-red-500/20 text-red-400 border-red-500/30",
    SHIPPED: "bg-purple-500/20 text-purple-400 border-purple-500/30",
  };
  return (
    <span className={`px-2.5 py-1 rounded-full font-bold text-[10px] border ${map[status] || "bg-slate-700 text-slate-300"}`}>
      {status}
    </span>
  );
}

// ─── Overview Panel ───────────────────────────────────────────────────────────
function OverviewPanel({ stats, loading }) {
  if (loading) return <LoadingSpinner />;

  const cards = [
    { label: "Total Products", value: stats.total_products ?? "—", icon: FiBox, color: "blue" },
    { label: "Total Orders", value: stats.total_orders ?? "—", icon: FiShoppingBag, color: "purple" },
    { label: "Pending Orders", value: stats.pending_orders ?? "—", icon: FiClock, color: "amber" },
    { label: "Completed", value: stats.completed_orders ?? "—", icon: FiCheckCircle, color: "emerald" },
    { label: "Registered Users", value: stats.total_customers ?? "—", icon: FiUsers, color: "indigo" },
  ];

  const colorMap = {
    blue: "bg-blue-500/10 text-blue-400",
    purple: "bg-purple-500/10 text-purple-400",
    amber: "bg-amber-500/10 text-amber-400 text-amber-400",
    emerald: "bg-emerald-500/10 text-emerald-400",
    indigo: "bg-indigo-500/10 text-indigo-400",
  };

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        {cards.map((c) => (
          <div key={c.label} className="glass-card rounded-2xl p-5 border border-slate-800 space-y-3">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-xl ${colorMap[c.color]}`}>
              <c.icon />
            </div>
            <div>
              <span className="text-xs text-slate-400 font-semibold block">{c.label}</span>
              <span className="text-3xl font-black text-white">{c.value}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Orders */}
      <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-base font-bold text-white">Recent Orders</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-slate-300">
            <thead className="bg-slate-900/60 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                {["Order ID", "Customer", "Payment", "Total", "Status", "Date"].map((h) => (
                  <th key={h} className="py-3 px-4 text-left">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {(stats.recent_orders || []).map((ord) => (
                <tr key={ord.id} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-3 px-4 font-bold text-white">{ord.order_number}</td>
                  <td className="py-3 px-4">{ord.full_name || "Guest"}</td>
                  <td className="py-3 px-4 text-blue-400 font-semibold">{ord.payment_method || "COD"}</td>
                  <td className="py-3 px-4 font-extrabold text-white">Rs. {Number(ord.total_amount).toLocaleString()}</td>
                  <td className="py-3 px-4"><StatusBadge status={ord.order_status} /></td>
                  <td className="py-3 px-4 text-slate-500">{new Date(ord.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
              {!stats.recent_orders?.length && (
                <tr><td colSpan={6} className="py-8 text-center text-slate-500">No orders yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─── Products Panel ───────────────────────────────────────────────────────────
function ProductsPanel() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState(null); // product slug being toggled
  const [error, setError] = useState("");

  useEffect(() => { fetchProducts(); }, []);

  const fetchProducts = async () => {
    setLoading(true);
    setError("");
    try {
      // Fetch ALL products (need admin view — backend returns is_available=true only by default)
      // We request without filter to get all; admin token allows full access
      const data = await api.adminGetAllProducts();
      const list = data?.results || (Array.isArray(data) ? data : []);
      setProducts(list);
    } catch (e) {
      setError("Failed to load products: " + (e.message || "Unknown error"));
    } finally {
      setLoading(false);
    }
  };

  const toggleAvailability = async (product) => {
    setToggling(product.slug);
    try {
      await api.adminToggleProductAvailability(product.slug);
      setProducts((prev) =>
        prev.map((p) => p.id === product.id ? { ...p, is_available: !p.is_available } : p)
      );
    } catch (e) {
      alert("Failed to update product: " + (e.message || "Unknown error"));
    } finally {
      setToggling(null);
    }
  };

  if (loading) return <LoadingSpinner label="Loading products..." />;

  return (
    <div className="space-y-4">
      {error && (
        <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
          <FiAlertCircle /> {error}
        </div>
      )}

      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-white">Products Management</h2>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block" /> Active
          <span className="w-3 h-3 rounded-full bg-slate-600 inline-block ml-2" /> Inactive
        </div>
      </div>

      <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-slate-300">
            <thead className="bg-slate-900/60 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                {["Product", "Category", "Price", "Stock", "Status", "Toggle Active"].map((h) => (
                  <th key={h} className="py-3 px-4 text-left">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {products.map((p) => (
                <tr key={p.id} className={`hover:bg-slate-900/40 transition-colors ${!p.is_available ? "opacity-60" : ""}`}>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      {p.images?.[0]?.image && (
                        <img src={p.images[0].image} alt={p.name} className="w-10 h-10 rounded-lg object-cover bg-slate-800" />
                      )}
                      <div>
                        <div className="font-semibold text-white line-clamp-1 max-w-[180px]">{p.name}</div>
                        <div className="text-slate-500 text-[10px]">{p.sku || p.slug}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4">{p.category_detail?.name || p.category || "—"}</td>
                  <td className="py-3 px-4 font-bold text-white">
                    Rs. {Number(p.current_price || p.price).toLocaleString()}
                    {p.discount_price && (
                      <span className="ml-1 text-slate-500 line-through text-[10px]">
                        Rs. {Number(p.price).toLocaleString()}
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`font-bold ${p.stock < 5 ? "text-red-400" : "text-emerald-400"}`}>
                      {p.stock}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-[10px] font-bold border ${p.is_available ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" : "bg-slate-700/40 text-slate-400 border-slate-700"}`}>
                      {p.is_available ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <button
                      onClick={() => toggleAvailability(p)}
                      disabled={toggling === p.slug}
                      title={p.is_available ? "Deactivate listing" : "Activate listing"}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-bold transition-all disabled:opacity-50 ${
                        p.is_available
                          ? "bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30"
                          : "bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/30"
                      }`}
                    >
                      {toggling === p.slug ? (
                        <div className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin" />
                      ) : p.is_available ? (
                        <><FiEyeOff className="text-xs" /> Deactivate</>
                      ) : (
                        <><FiEye className="text-xs" /> Activate</>
                      )}
                    </button>
                  </td>
                </tr>
              ))}
              {!products.length && (
                <tr><td colSpan={6} className="py-10 text-center text-slate-500">No products found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─── Orders Panel ─────────────────────────────────────────────────────────────
function OrdersPanel() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => { fetchOrders(); }, []);

  const fetchOrders = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.adminGetOrders();
      const list = data?.results || (Array.isArray(data) ? data : []);
      setOrders(list);
    } catch (e) {
      setError("Failed to load orders: " + (e.message || "Unknown error"));
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner label="Loading orders..." />;

  return (
    <div className="space-y-4">
      {error && (
        <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
          <FiAlertCircle /> {error}
        </div>
      )}

      <h2 className="text-lg font-bold text-white">Orders Management</h2>

      <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-slate-300">
            <thead className="bg-slate-900/60 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                {["Order ID", "Customer", "Items", "Total", "Payment", "Status", "Date"].map((h) => (
                  <th key={h} className="py-3 px-4 text-left">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {orders.map((ord) => (
                <tr key={ord.id} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-3 px-4 font-bold text-white">{ord.order_number}</td>
                  <td className="py-3 px-4">
                    <div className="font-semibold">{ord.full_name || "Guest"}</div>
                    <div className="text-slate-500 text-[10px]">{ord.email || ""}</div>
                  </td>
                  <td className="py-3 px-4">{ord.items?.length ?? ord.total_items ?? "—"}</td>
                  <td className="py-3 px-4 font-extrabold text-white">Rs. {Number(ord.total_amount).toLocaleString()}</td>
                  <td className="py-3 px-4 text-blue-400 font-semibold">{ord.payment_method || "COD"}</td>
                  <td className="py-3 px-4"><StatusBadge status={ord.order_status} /></td>
                  <td className="py-3 px-4 text-slate-500">{new Date(ord.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
              {!orders.length && (
                <tr><td colSpan={7} className="py-10 text-center text-slate-500">No orders found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─── Users Panel ──────────────────────────────────────────────────────────────
function UsersPanel() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => { fetchUsers(); }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.adminGetUsers();
      const list = data?.results || (Array.isArray(data) ? data : []);
      setUsers(list);
    } catch (e) {
      setError("Failed to load users: " + (e.message || "Unknown error"));
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner label="Loading users..." />;

  return (
    <div className="space-y-4">
      {error && (
        <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
          <FiAlertCircle /> {error}
        </div>
      )}

      <h2 className="text-lg font-bold text-white">Registered Users</h2>

      <div className="glass-card rounded-2xl border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-slate-300">
            <thead className="bg-slate-900/60 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                {["#", "Name / Username", "Email", "Type", "Verified"].map((h) => (
                  <th key={h} className="py-3 px-4 text-left">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {users.map((u, i) => (
                <tr key={u.id} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-3 px-4 text-slate-500">{i + 1}</td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-white">{u.name || u.username}</div>
                    <div className="text-slate-500 text-[10px]">@{u.username}</div>
                  </td>
                  <td className="py-3 px-4">{u.email}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-[10px] font-bold border ${u.user_type === "ADMIN" ? "bg-purple-500/20 text-purple-400 border-purple-500/30" : "bg-slate-700/40 text-slate-400 border-slate-700"}`}>
                      {u.user_type || "USER"}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    {u.is_verified ? (
                      <FiCheckCircle className="text-emerald-400" />
                    ) : (
                      <FiAlertCircle className="text-slate-600" />
                    )}
                  </td>
                </tr>
              ))}
              {!users.length && (
                <tr><td colSpan={5} className="py-10 text-center text-slate-500">No users found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─── Loading Spinner ──────────────────────────────────────────────────────────
function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="text-center py-20">
      <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
      <p className="text-slate-400 text-xs">{label}</p>
    </div>
  );
}

// ─── Main Admin Dashboard ─────────────────────────────────────────────────────
export default function AdminDashboardPage() {
  const router = useRouter();
  const authorized = useAdminGuard();
  const [activeTab, setActiveTab] = useState("overview");
  const [stats, setStats] = useState({});
  const [statsLoading, setStatsLoading] = useState(true);
  const [adminUser, setAdminUser] = useState(null);

  useEffect(() => {
    if (authorized) {
      const u = JSON.parse(localStorage.getItem("user") || "{}");
      setAdminUser(u);
      fetchStats();
    }
  }, [authorized]);

  const fetchStats = async () => {
    setStatsLoading(true);
    try {
      const data = await api.getDashboardStats();
      if (data) setStats(data);
    } catch (e) {
      console.warn("Dashboard stats error:", e);
    } finally {
      setStatsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("user_type");
    router.push("/admin");
  };

  if (!authorized) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Top Bar */}
      <div className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-purple-600 flex items-center justify-center text-white font-bold">
                S
              </div>
              <span className="font-black text-white">STOREX</span>
              <FiChevronRight className="text-slate-600" />
              <span className="text-xs font-bold text-blue-400 uppercase tracking-widest">Admin Panel</span>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/" className="text-xs text-slate-400 hover:text-white transition-colors">
                ← View Store
              </Link>
              <div className="flex items-center gap-2 text-xs text-slate-300">
                <div className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-[10px]">
                  {(adminUser?.name || adminUser?.username || "A")[0].toUpperCase()}
                </div>
                <span className="hidden sm:block">{adminUser?.name || adminUser?.username || "Admin"}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-red-400 hover:bg-red-500/10 border border-red-500/20 transition-all"
              >
                <FiLogOut />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Title */}
        <div className="mb-8">
          <span className="text-xs font-bold text-blue-400 uppercase tracking-widest">Admin Control Portal</span>
          <h1 className="text-3xl font-black text-white mt-1">Store Overview Dashboard</h1>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 mb-8 bg-slate-900/50 p-1.5 rounded-2xl border border-slate-800 w-fit">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === tab.id
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-500/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <tab.icon />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === "overview" && <OverviewPanel stats={stats} loading={statsLoading} />}
        {activeTab === "products" && <ProductsPanel />}
        {activeTab === "orders" && <OrdersPanel />}
        {activeTab === "users" && <UsersPanel />}
      </div>
    </div>
  );
}
