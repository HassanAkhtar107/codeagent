"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { FiLock, FiUser, FiArrowRight, FiAlertCircle, FiShield } from "react-icons/fi";
import { api } from "@/Services/api";

export default function AdminLoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  // If already logged in as admin, redirect to dashboard
  useEffect(() => {
    const token = localStorage.getItem("token");
    const userType = localStorage.getItem("user_type");
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    if (token && (userType === "ADMIN" || user?.is_staff)) {
      router.replace("/admin/dashboard");
    }
  }, [router]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (errorMsg) setErrorMsg("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    if (!formData.username.trim() || !formData.password.trim()) {
      setErrorMsg("Please enter both username and password.");
      return;
    }
    try {
      setLoading(true);
      const res = await api.login(formData);
      const userType = res.user?.user_type;
      const isStaff = res.user?.is_staff;

      if (userType !== "ADMIN" && !isStaff) {
        setErrorMsg("Access denied. This portal is for administrators only.");
        return;
      }

      // Admin login success
      localStorage.setItem("token", res.token);
      localStorage.setItem("user", JSON.stringify(res.user));
      localStorage.setItem("user_type", userType || "ADMIN");

      router.push("/admin/dashboard");
    } catch (err) {
      const msg = err?.message || "";
      if (msg.includes("401") || msg.includes("403") || msg.toLowerCase().includes("invalid") || msg.toLowerCase().includes("credentials")) {
        setErrorMsg("Invalid admin credentials. Please try again.");
      } else if (msg.includes("fetch") || msg.includes("network") || msg.includes("Failed")) {
        setErrorMsg("Cannot connect to server. Please check your connection.");
      } else {
        setErrorMsg(msg || "Login failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-16 relative">
      {/* Background glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-purple-600/15 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-2/3 right-1/4 w-[300px] h-[200px] bg-blue-600/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-3 group">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold text-2xl shadow-lg shadow-blue-500/30">
              S
            </div>
            <span className="font-extrabold text-2xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              STORE<span className="text-blue-500">X</span>
            </span>
          </Link>
        </div>

        <div className="glass-card rounded-3xl p-8 border border-slate-700/50 space-y-6">
          {/* Header */}
          <div className="text-center space-y-3">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-600/20 to-blue-600/20 border border-purple-500/30 flex items-center justify-center mx-auto">
              <FiShield className="text-2xl text-purple-400" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-white">Admin Portal</h1>
              <p className="text-xs text-slate-400 mt-1">Sign in to access the admin control panel.</p>
            </div>
          </div>

          {errorMsg && (
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-semibold flex items-center gap-2">
              <FiAlertCircle className="shrink-0 text-sm" />
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Admin Username
              </label>
              <div className="relative">
                <input
                  type="text"
                  name="username"
                  required
                  placeholder="Enter admin username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2.5 pl-10 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500/30 transition-all"
                  autoComplete="username"
                />
                <FiUser className="absolute left-3.5 top-3 text-slate-400" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  type="password"
                  name="password"
                  required
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2.5 pl-10 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500/30 transition-all"
                  autoComplete="current-password"
                />
                <FiLock className="absolute left-3.5 top-3 text-slate-400" />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 flex items-center justify-center gap-2 shadow-lg shadow-purple-500/25 mt-2 disabled:opacity-60 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <FiShield />
                  <span>Access Admin Panel</span>
                </>
              )}
            </button>
          </form>

          <div className="text-center text-xs text-slate-500 pt-2 border-t border-slate-800">
            Not an admin?{" "}
            <Link href="/login" className="text-blue-400 font-bold hover:underline">
              User Login
            </Link>
            {" · "}
            <Link href="/" className="text-slate-400 hover:text-white">
              Go to Store
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
