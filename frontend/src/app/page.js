"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { FiArrowRight, FiZap, FiTrendingUp, FiShoppingBag, FiStar } from "react-icons/fi";
import ProductCard from "@/components/ProductCard";
import { api } from "@/Services/api";

const DEMO_PRODUCTS = [
  {
    id: 1,
    name: "Nexus Pro Wireless Headphones",
    slug: "nexus-pro-wireless-headphones",
    category: "Electronics",
    price: 199.99,
    discount_price: 149.99,
    rating: 4.8,
    num_reviews: 32,
    is_featured: true,
    images: [{ image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80" }]
  },
  {
    id: 2,
    name: "Urban Minimalist Bomber Jacket",
    slug: "urban-minimalist-bomber-jacket",
    category: "Fashion & Apparel",
    price: 129.00,
    discount_price: 89.00,
    rating: 4.6,
    num_reviews: 19,
    is_featured: true,
    images: [{ image: "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&auto=format&fit=crop&q=80" }]
  },
  {
    id: 3,
    name: "Luxe Ambient Ceramic Desk Lamp",
    slug: "luxe-ambient-ceramic-desk-lamp",
    category: "Home & Lifestyle",
    price: 89.50,
    rating: 4.9,
    num_reviews: 14,
    is_featured: true,
    images: [{ image: "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&auto=format&fit=crop&q=80" }]
  },
  {
    id: 4,
    name: "Smart Fitness Watch Ultra",
    slug: "smart-fitness-watch-ultra",
    category: "Sports & Fitness",
    price: 249.99,
    discount_price: 199.99,
    rating: 4.7,
    num_reviews: 45,
    is_featured: true,
    images: [{ image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=80" }]
  }
];

const CATEGORIES = [
  { name: "Electronics", slug: "electronics", image: "https://images.unsplash.com/photo-1498049860654-af1a5c566876?w=600&auto=format&fit=crop&q=80", count: "120+ Products" },
  { name: "Fashion & Apparel", slug: "fashion-apparel", image: "https://images.unsplash.com/photo-1445205170230-053b83016050?w=600&auto=format&fit=crop&q=80", count: "250+ Products" },
  { name: "Home & Living", slug: "home-lifestyle", image: "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=600&auto=format&fit=crop&q=80", count: "80+ Products" },
  { name: "Sports & Fitness", slug: "sports-fitness", image: "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop&q=80", count: "95+ Products" },
];

export default function Home() {
  const [products, setProducts] = useState(DEMO_PRODUCTS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const data = await api.getProducts("?is_featured=true");
        if (data && data.results && data.results.length > 0) {
          setProducts(data.results);
        } else if (Array.isArray(data) && data.length > 0) {
          setProducts(data);
        }
      } catch (err) {
        console.warn("API offline or empty, rendering demo products", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, []);

  return (
    <div className="space-y-24 pb-16">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 lg:pt-20">
        {/* Glow Effects */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-blue-600/20 rounded-full blur-[140px] pointer-events-none" />
        <div className="absolute top-1/3 right-10 w-[400px] h-[300px] bg-purple-600/15 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            
            <div className="space-y-6 text-center lg:text-left">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold tracking-wide uppercase">
                <FiZap />
                <span>Next Generation Shopping</span>
              </div>

              <h1 className="text-4xl sm:text-6xl font-black text-white tracking-tight leading-[1.1]">
                Elevate Your Style & <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">Tech Gear</span>
              </h1>

              <p className="text-slate-400 text-base sm:text-lg max-w-xl mx-auto lg:mx-0 leading-relaxed font-normal">
                Discover curations of high-performance electronics, modern streetwear apparel, and sleek living items with lightning-fast shipping.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
                <Link
                  href="/products"
                  className="w-full sm:w-auto px-8 py-4 rounded-xl text-sm font-bold text-white btn-gradient flex items-center justify-center gap-3 group shadow-xl shadow-blue-500/20"
                >
                  <span>Explore Catalog</span>
                  <FiArrowRight className="group-hover:translate-x-1 transition-transform" />
                </Link>

                <Link
                  href="/products?is_featured=true"
                  className="w-full sm:w-auto px-8 py-4 rounded-xl text-sm font-bold text-slate-200 btn-secondary flex items-center justify-center gap-2"
                >
                  <FiTrendingUp className="text-blue-400" />
                  <span>Trending Deals</span>
                </Link>
              </div>

              <div className="pt-8 flex items-center justify-center lg:justify-start gap-8 text-slate-400 border-t border-slate-800/80">
                <div>
                  <div className="text-2xl font-black text-white">10K+</div>
                  <div className="text-xs text-slate-500">Happy Customers</div>
                </div>
                <div className="h-8 w-px bg-slate-800" />
                <div>
                  <div className="text-2xl font-black text-white">4.9★</div>
                  <div className="text-xs text-slate-500">Average Rating</div>
                </div>
                <div className="h-8 w-px bg-slate-800" />
                <div>
                  <div className="text-2xl font-black text-white">24h</div>
                  <div className="text-xs text-slate-500">Express Delivery</div>
                </div>
              </div>
            </div>

            {/* Showcase Image */}
            <div className="relative">
              <div className="glass-card rounded-3xl p-4 sm:p-6 shadow-2xl relative z-10 border border-slate-700/50">
                <div className="relative aspect-4/3 rounded-2xl overflow-hidden bg-slate-900">
                  <img
                    src="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1000&auto=format&fit=crop&q=80"
                    alt="Featured Headphone"
                    className="w-full h-full object-cover transform hover:scale-105 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-transparent to-transparent" />
                  
                  <div className="absolute bottom-6 left-6 right-6 flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-blue-400 uppercase tracking-widest">Featured Pick</span>
                      <h3 className="text-xl font-black text-white">Nexus Pro Audio</h3>
                    </div>
                    <span className="text-lg font-black text-white bg-blue-600 px-3 py-1.5 rounded-xl">$149.99</span>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Category Grid Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-10">
          <div>
            <span className="text-xs font-extrabold text-blue-400 uppercase tracking-wider">Browse Collections</span>
            <h2 className="text-3xl font-black text-white mt-1">Shop by Category</h2>
          </div>
          <Link href="/products" className="text-sm font-bold text-blue-400 hover:text-blue-300 flex items-center gap-1.5 mt-2 md:mt-0">
            <span>View All Categories</span>
            <FiArrowRight />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {CATEGORIES.map((cat, idx) => (
            <Link
              key={idx}
              href={`/products?category=${cat.slug}`}
              className="glass-card rounded-2xl p-4 flex flex-col justify-between group hover:border-blue-500/50 transition-all duration-300 relative overflow-hidden"
            >
              <div className="aspect-4/3 rounded-xl overflow-hidden mb-4 bg-slate-900 relative">
                <img
                  src={cat.image}
                  alt={cat.name}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-slate-950/20 group-hover:bg-transparent transition-colors" />
              </div>
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-slate-100 text-lg group-hover:text-blue-400 transition-colors">{cat.name}</h3>
                  <span className="text-xs text-slate-400">{cat.count}</span>
                </div>
                <div className="w-9 h-9 rounded-full bg-slate-800 flex items-center justify-center text-slate-300 group-hover:bg-blue-600 group-hover:text-white transition-all">
                  <FiArrowRight />
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured Products Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-10">
          <div>
            <span className="text-xs font-extrabold text-blue-400 uppercase tracking-wider">Top Rated Gear</span>
            <h2 className="text-3xl font-black text-white mt-1">Featured Products</h2>
          </div>
          <Link href="/products" className="text-sm font-bold text-blue-400 hover:text-blue-300 flex items-center gap-1.5 mt-2 md:mt-0">
            <span>Explore All</span>
            <FiArrowRight />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </section>

      {/* Promo Banner */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative rounded-3xl overflow-hidden bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 border border-blue-500/20 p-8 sm:p-14">
          <div className="max-w-xl space-y-6 relative z-10">
            <span className="px-3 py-1 bg-blue-500/20 text-blue-300 text-xs font-bold rounded-full border border-blue-400/30">
              Limited Time Offer
            </span>
            <h2 className="text-3xl sm:text-5xl font-black text-white leading-tight">
              Get 30% Off Your First Order
            </h2>
            <p className="text-slate-300 text-sm sm:text-base">
              Use promo code <span className="font-extrabold text-blue-400 underline">STOREX30</span> at checkout. Valid on all premium electronics and streetwear.
            </p>
            <Link
              href="/products"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-white text-slate-950 font-bold text-sm hover:bg-slate-200 transition-colors shadow-xl"
            >
              <FiShoppingBag />
              <span>Shop Discount Now</span>
            </Link>
          </div>
        </div>
      </section>

    </div>
  );
}
