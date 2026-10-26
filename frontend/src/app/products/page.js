"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import ProductCard from "@/components/ProductCard";
import { api } from "@/Services/api";
import { FiSearch, FiSliders, FiX, FiFilter } from "react-icons/fi";

const DEFAULT_CATEGORIES = [
  { name: "All Categories", slug: "all" },
  { name: "Dresses", slug: "dresses" },
  { name: "Shirts", slug: "shirts" },
  { name: "T-Shirts", slug: "t-shirts" },
  { name: "Pants", slug: "pants" },
  { name: "Trousers", slug: "trousers" },
  { name: "Suits", slug: "suits" },
  { name: "Kurta Pajama", slug: "kurta-pajama" },
  { name: "Shoes", slug: "shoes" },
];

function ProductsContent() {
  const searchParams = useSearchParams();
  const initialCategory = searchParams.get("category") || "all";
  const initialGender = searchParams.get("gender") || "all";
  const initialSearch = searchParams.get("search") || "";

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState(DEFAULT_CATEGORIES);
  const [selectedGender, setSelectedGender] = useState(initialGender.toUpperCase());
  const [selectedCategory, setSelectedCategory] = useState(initialCategory);
  const [searchQuery, setSearchQuery] = useState(initialSearch);
  const [sortBy, setSortBy] = useState("default");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBackendCategories();
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [selectedGender, selectedCategory, searchQuery, sortBy]);

  const fetchBackendCategories = async () => {
    try {
      const catData = await api.getCategories();
      if (catData && (catData.results || Array.isArray(catData))) {
        const catList = catData.results || catData;
        if (catList.length > 0) {
          setCategories([{ name: "All Categories", slug: "all" }, ...catList]);
        }
      }
    } catch (e) {
      console.warn("Using default category filter list", e);
    }
  };

  const fetchProducts = async () => {
    try {
      setLoading(true);
      let queryParams = [];

      if (selectedGender !== "ALL") {
        queryParams.push(`gender=${selectedGender}`);
      }
      if (selectedCategory !== "all") {
        queryParams.push(`category__slug=${selectedCategory}`);
      }
      if (searchQuery.trim()) {
        queryParams.push(`search=${encodeURIComponent(searchQuery.trim())}`);
      }
      if (sortBy === "price-low") {
        queryParams.push("ordering=price");
      } else if (sortBy === "price-high") {
        queryParams.push("ordering=-price");
      }

      const queryStr = queryParams.length > 0 ? `?${queryParams.join("&")}` : "";
      const data = await api.getProducts(queryStr);

      if (data && (data.results || Array.isArray(data))) {
        const pList = data.results || data;
        setProducts(pList);
      } else {
        setProducts([]);
      }
    } catch (err) {
      console.error("Error fetching products:", err);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const resetAllFilters = () => {
    setSelectedGender("ALL");
    setSelectedCategory("all");
    setSearchQuery("");
    setSortBy("default");
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      
      {/* Page Title */}
      <div className="mb-10 text-center sm:text-left">
        <h1 className="text-4xl font-black text-white">Clothing & Footwear Catalog</h1>
        <p className="text-slate-400 text-sm mt-1">Explore authentic apparel for Men and Women with direct backend filtering.</p>
      </div>

      {/* Main Filter Control Section */}
      <div className="glass-card rounded-3xl p-6 mb-10 space-y-6 border border-slate-800">
        
        {/* Top Controls: Search & Sort */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          
          {/* Search Box */}
          <div className="relative w-full md:w-96">
            <input
              type="text"
              placeholder="Search by product name, e.g. Kurta, Suit, Shoes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2.5 pl-10 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
            />
            <FiSearch className="absolute left-3.5 top-3 text-slate-400" />
            {searchQuery && (
              <button onClick={() => setSearchQuery("")} className="absolute right-3 top-3 text-slate-400 hover:text-white">
                <FiX />
              </button>
            )}
          </div>

          {/* Gender Selector Tabs */}
          <div className="flex items-center gap-2 bg-slate-900/90 p-1.5 rounded-2xl border border-slate-800 w-full md:w-auto justify-center">
            {["ALL", "MEN", "WOMEN"].map((g) => (
              <button
                key={g}
                onClick={() => setSelectedGender(g)}
                className={`px-5 py-2 rounded-xl text-xs font-bold transition-all ${
                  selectedGender === g
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-500/30"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {g === "ALL" ? "All Genders" : g === "MEN" ? "Men" : "Women"}
              </button>
            ))}
          </div>

          {/* Price Sorting Dropdown */}
          <div className="flex items-center gap-2 w-full md:w-auto">
            <FiSliders className="text-slate-400 text-sm" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full md:w-auto bg-slate-900 border border-slate-700/80 text-slate-200 text-xs font-semibold rounded-xl px-4 py-2.5 focus:outline-none focus:border-blue-500"
            >
              <option value="default">Sort by: Default</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
            </select>
          </div>

        </div>

        {/* Dynamic Category Pill Filters */}
        <div className="pt-4 border-t border-slate-800/80">
          <div className="flex items-center gap-2 mb-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
            <FiFilter />
            <span>Product Categories</span>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
            {categories.map((cat) => (
              <button
                key={cat.slug}
                onClick={() => setSelectedCategory(cat.slug)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
                  selectedCategory === cat.slug
                    ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/25"
                    : "bg-slate-900 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800"
                }`}
              >
                {cat.name}
              </button>
            ))}
          </div>
        </div>

      </div>

      {/* Active Filter Chips */}
      {(selectedGender !== "ALL" || selectedCategory !== "all" || searchQuery) && (
        <div className="flex items-center gap-3 mb-8 text-xs">
          <span className="text-slate-400">Active Filters:</span>
          {selectedGender !== "ALL" && (
            <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full font-bold border border-blue-500/30 flex items-center gap-1">
              Gender: {selectedGender}
              <FiX className="cursor-pointer hover:text-white" onClick={() => setSelectedGender("ALL")} />
            </span>
          )}
          {selectedCategory !== "all" && (
            <span className="bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full font-bold border border-purple-500/30 flex items-center gap-1">
              Category: {selectedCategory}
              <FiX className="cursor-pointer hover:text-white" onClick={() => setSelectedCategory("all")} />
            </span>
          )}
          {searchQuery && (
            <span className="bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full font-bold border border-emerald-500/30 flex items-center gap-1">
              Search: "{searchQuery}"
              <FiX className="cursor-pointer hover:text-white" onClick={() => setSearchQuery("")} />
            </span>
          )}
          <button onClick={resetAllFilters} className="text-slate-400 hover:text-red-400 underline font-semibold ml-2">
            Clear All
          </button>
        </div>
      )}

      {/* Products Grid */}
      {loading ? (
        <div className="text-center py-24 glass-card rounded-2xl">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400 text-xs">Loading products from backend API...</p>
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-24 glass-card rounded-3xl border border-slate-800">
          <FiSearch className="text-5xl text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-slate-200">No matching clothing or shoes found</h3>
          <p className="text-xs text-slate-400 mt-1 mb-6">Try adjusting your gender, category, or search filters.</p>
          <button
            onClick={resetAllFilters}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-blue-500/25 transition-all"
          >
            Reset All Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}

    </div>
  );
}

export default function ProductsPage() {
  return (
    <Suspense fallback={<div className="text-center py-20 text-slate-400">Loading catalog...</div>}>
      <ProductsContent />
    </Suspense>
  );
}
