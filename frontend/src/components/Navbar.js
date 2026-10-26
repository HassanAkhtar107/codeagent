"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FiShoppingBag, FiSearch, FiUser, FiMenu, FiX, FiLogOut, FiSettings } from "react-icons/fi";
import { useCart } from "@/context/CartContext";

export default function Navbar() {
  const router = useRouter();
  const { cartCount, setIsCartOpen } = useCart();
  const [searchQuery, setSearchQuery] = useState("");
  const [user, setUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedUser = localStorage.getItem("user");
      const userType = localStorage.getItem("user_type");
      if (storedUser) {
        try {
          const parsed = JSON.parse(storedUser);
          setUser(parsed);
          setIsAdmin(userType === "ADMIN" || parsed?.is_staff);
        } catch (e) { }
      }
    }
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/products?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("user_type");
    setUser(null);
    setIsAdmin(false);
    router.push("/");
  };

  return (
    <header className="sticky top-0 z-50 glass-nav transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">

          {/* Brand Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-blue-500/30 group-hover:scale-105 transition-transform duration-300">
              S
            </div>
            <span className="font-extrabold text-2xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              STORE<span className="text-blue-500">X</span>
            </span>
          </Link>

          {/* Desktop Search Bar */}
          <form onSubmit={handleSearch} className="hidden md:flex flex-1 max-w-md mx-8 relative">
            <input
              type="text"
              placeholder="Search products, brands, categories..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900/80 text-sm text-slate-200 placeholder-slate-400 pl-10 pr-4 py-2.5 rounded-full border border-slate-700/60 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
            />
            <FiSearch className="absolute left-3.5 top-3 text-slate-400 text-lg" />
          </form>

          {/* Nav Links */}
          <nav className="hidden lg:flex items-center gap-4 text-sm font-medium text-slate-300">
            <Link href="/" className="hover:text-blue-400 transition-colors">Home</Link>
            <Link href="/products" className="hover:text-blue-400 transition-colors">Products</Link>
            <Link href="/products?is_featured=true" className="hover:text-blue-400 transition-colors">Featured</Link>
            <Link href="/orders" className="hover:text-blue-400 transition-colors">Orders</Link>

            {/* Cart Icon Button */}
            <button
              onClick={() => setIsCartOpen(true)}
              className="relative p-2 rounded-full bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-slate-200 hover:text-white transition-all duration-200"
              aria-label="View Cart"
            >
              <FiShoppingBag className="text-xl" />
              {cartCount > 0 && (
                <span className="absolute -top-1.5 -right-1.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center animate-bounce">
                  {cartCount}
                </span>
              )}
            </button>

            {/* User Auth Dropdown */}
            {user ? (
              <div className="flex items-center gap-2">
                {isAdmin && (
                  <Link
                    href="/admin/dashboard"
                    className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold text-purple-300 bg-purple-500/10 border border-purple-500/20 hover:bg-purple-500/20 transition-colors"
                  >
                    <FiSettings className="text-xs" />
                    Dashboard
                  </Link>
                )}
                <div className="flex items-center gap-3 bg-slate-800/80 px-3.5 py-1.5 rounded-full border border-slate-700/60">
                  <FiUser className="text-blue-400" />
                  <span className="text-xs font-semibold text-slate-200 max-w-[100px] truncate">
                    {user.name || user.username}
                  </span>
                  <button
                    onClick={handleLogout}
                    title="Logout"
                    className="text-slate-400 hover:text-red-400 transition-colors ml-1"
                  >
                    <FiLogOut className="text-sm" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="hidden sm:flex items-center gap-2">
                <Link
                  href="/login"
                  className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
                >
                  Log In
                </Link>
                <Link
                  href="/signup"
                  className="px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 rounded-full shadow-lg shadow-blue-500/25 transition-all"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </nav>

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden md:flex p-2 text-slate-300 hover:text-white"
          >
            {isMobileMenuOpen ? <FiX className="text-2xl" /> : <FiMenu className="text-2xl" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {isMobileMenuOpen && (
        <div className="lg:hidden bg-slate-900 border-b border-slate-800 px-4 pt-2 pb-6 space-y-3 animate-fade-in">
          <form onSubmit={handleSearch} className="relative my-2">
            <input
              type="text"
              placeholder="Search products..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-800 text-sm text-slate-200 placeholder-slate-400 pl-10 pr-4 py-2 rounded-lg border border-slate-700"
            />
            <FiSearch className="absolute left-3 top-2.5 text-slate-400" />
          </form>

          <Link href="/" className="block py-2 text-slate-300 hover:text-white" onClick={() => setIsMobileMenuOpen(false)}>Home</Link>
          <Link href="/products" className="block py-2 text-slate-300 hover:text-white" onClick={() => setIsMobileMenuOpen(false)}>Products Catalog</Link>
          <Link href="/orders" className="block py-2 text-slate-300 hover:text-white" onClick={() => setIsMobileMenuOpen(false)}>My Orders</Link>
          {isAdmin && (
            <Link href="/admin/dashboard" className="block py-2 text-purple-400 hover:text-purple-300 font-semibold" onClick={() => setIsMobileMenuOpen(false)}>
              ⚙ Admin Dashboard
            </Link>
          )}
          {!user && (
            <div className="flex gap-4 pt-2 border-t border-slate-800">
              <Link href="/login" className="flex-1 text-center py-2 text-sm font-semibold text-slate-300 border border-slate-700 rounded-lg">Log In</Link>
              <Link href="/signup" className="flex-1 text-center py-2 text-sm font-semibold text-white bg-blue-600 rounded-lg">Sign Up</Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
