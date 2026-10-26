import React from "react";
import Link from "next/link";
import { FiShield, FiTruck, FiRefreshCw, FiHeadphones } from "react-icons/fi";

export default function Footer() {
  return (
    <footer className="bg-slate-950 border-t border-slate-800/80 text-slate-400 pt-16 pb-12 mt-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Value Proposition Badges */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 pb-12 border-b border-slate-800/60 mb-12">
          <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-900/50 border border-slate-800/50">
            <div className="p-3 bg-blue-500/10 text-blue-400 rounded-lg text-xl">
              <FiTruck />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-200">Free Shipping</h4>
              <p className="text-xs text-slate-500">On all orders over $50</p>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-900/50 border border-slate-800/50">
            <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-lg text-xl">
              <FiShield />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-200">Secure Payment</h4>
              <p className="text-xs text-slate-500">100% protected checkout</p>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-900/50 border border-slate-800/50">
            <div className="p-3 bg-purple-500/10 text-purple-400 rounded-lg text-xl">
              <FiRefreshCw />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-200">30 Days Return</h4>
              <p className="text-xs text-slate-500">Hassle-free guarantee</p>
            </div>
          </div>

          <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-900/50 border border-slate-800/50">
            <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg text-xl">
              <FiHeadphones />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-200">24/7 Support</h4>
              <p className="text-xs text-slate-500">Dedicated assistance</p>
            </div>
          </div>
        </div>

        {/* Footer Links Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10 mb-12">
          
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold">
                S
              </div>
              <span className="font-extrabold text-xl text-white">STORE<span className="text-blue-500">X</span></span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Your premier destination for high-end electronics, apparel, and lifestyle products curated for quality and elegance.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Quick Links</h4>
            <ul className="space-y-2.5 text-xs">
              <li><Link href="/" className="hover:text-blue-400 transition-colors">Home</Link></li>
              <li><Link href="/products" className="hover:text-blue-400 transition-colors">Products Catalog</Link></li>
              <li><Link href="/cart" className="hover:text-blue-400 transition-colors">Shopping Cart</Link></li>
              <li><Link href="/orders" className="hover:text-blue-400 transition-colors">Track Orders</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Categories</h4>
            <ul className="space-y-2.5 text-xs">
              <li><Link href="/products?category=electronics" className="hover:text-blue-400 transition-colors">Electronics</Link></li>
              <li><Link href="/products?category=fashion-apparel" className="hover:text-blue-400 transition-colors">Fashion & Apparel</Link></li>
              <li><Link href="/products?category=home-lifestyle" className="hover:text-blue-400 transition-colors">Home & Living</Link></li>
              <li><Link href="/products?category=sports-fitness" className="hover:text-blue-400 transition-colors">Sports & Fitness</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-slate-200 uppercase tracking-wider mb-4">Newsletter</h4>
            <p className="text-xs text-slate-400 mb-3">Subscribe to receive exclusive deals and new release updates.</p>
            <div className="flex gap-2">
              <input
                type="email"
                placeholder="Enter your email"
                className="bg-slate-900 border border-slate-800 text-xs px-3 py-2 rounded-lg text-slate-200 focus:outline-none focus:border-blue-500 flex-1"
              />
              <button className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold px-3 py-2 rounded-lg transition-colors">
                Subscribe
              </button>
            </div>
          </div>

        </div>

        <div className="border-t border-slate-800/80 pt-8 flex flex-col sm:flex-row justify-between items-center text-xs text-slate-500">
          <p>© {new Date().getFullYear()} STOREX Inc. All rights reserved.</p>
          <div className="flex gap-6 mt-4 sm:mt-0">
            <span className="hover:text-slate-400 cursor-pointer">Privacy Policy</span>
            <span className="hover:text-slate-400 cursor-pointer">Terms of Service</span>
            <span className="hover:text-slate-400 cursor-pointer">Cookie Settings</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
