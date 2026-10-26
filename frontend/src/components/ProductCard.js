"use client";

import React from "react";
import Link from "next/link";
import { FiShoppingBag, FiStar } from "react-icons/fi";
import { useCart } from "@/context/CartContext";

export default function ProductCard({ product }) {
  const { addToCart } = useCart();

  const primaryImage =
    product?.images?.length > 0
      ? product.images[0].image
      : "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&auto=format&fit=crop&q=80";

  const price = Number(product?.price || 0);
  const discountPrice = product?.discount_price ? Number(product.discount_price) : null;
  const currentPrice = discountPrice || price;
  const discountPercent = product?.discount_percentage || (discountPrice ? Math.round(((price - discountPrice) / price) * 100) : 0);

  const genderLabel = product?.gender === "MEN" ? "Men" : product?.gender === "WOMEN" ? "Women" : null;

  return (
    <div className="glass-card rounded-2xl overflow-hidden hover:border-blue-500/40 transition-all duration-300 hover:-translate-y-1.5 flex flex-col group relative">
      
      {/* Top Badges */}
      <div className="absolute top-3 left-3 z-10 flex flex-col gap-1">
        {discountPercent > 0 && (
          <span className="bg-gradient-to-r from-red-500 to-pink-500 text-white text-[10px] font-extrabold px-2.5 py-1 rounded-full uppercase tracking-wider shadow-lg">
            {discountPercent}% OFF
          </span>
        )}
        {product?.is_featured && !discountPercent && (
          <span className="bg-gradient-to-r from-amber-500 to-orange-500 text-white text-[10px] font-extrabold px-2.5 py-1 rounded-full uppercase tracking-wider shadow-lg">
            Featured
          </span>
        )}
      </div>

      {/* Gender Badge */}
      {genderLabel && (
        <span className="absolute top-3 right-3 z-10 bg-slate-900/80 backdrop-blur-md border border-slate-700/80 text-slate-200 text-[10px] font-bold px-2 py-0.5 rounded-md">
          {genderLabel}
        </span>
      )}

      {/* Image Container */}
      <Link href={`/products/${product?.slug || product?.id}`} className="relative aspect-4/5 overflow-hidden bg-slate-900/60 block">
        <img
          src={primaryImage}
          alt={product?.name || "Product"}
          className="w-full h-full object-cover group-hover:scale-108 transition-transform duration-500 ease-out"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      </Link>

      {/* Card Body */}
      <div className="p-5 flex flex-col flex-1 justify-between">
        
        <div>
          <div className="flex justify-between items-center text-xs text-slate-400 mb-1.5 font-medium">
            <span>{product?.category_detail?.name || product?.category || "General"}</span>
            {product?.brand_detail?.name && (
              <span className="text-blue-400 font-semibold">{product.brand_detail.name}</span>
            )}
          </div>

          <Link href={`/products/${product?.slug || product?.id}`}>
            <h3 className="font-bold text-slate-100 text-base line-clamp-1 group-hover:text-blue-400 transition-colors">
              {product?.name}
            </h3>
          </Link>

          {/* Star Rating */}
          <div className="flex items-center gap-1.5 mt-2">
            <div className="flex items-center text-amber-400 text-xs">
              <FiStar className="fill-amber-400" />
              <span className="font-bold ml-1 text-slate-200">{product?.rating || "4.8"}</span>
            </div>
            <span className="text-xs text-slate-500">({product?.num_reviews || 12})</span>
          </div>
        </div>

        {/* Price & Action */}
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-lg font-extrabold text-white">
              Rs. {currentPrice.toLocaleString()}
            </span>
            {discountPrice && (
              <span className="text-xs text-slate-500 line-through">
                Rs. {price.toLocaleString()}
              </span>
            )}
          </div>

          <button
            onClick={() => addToCart(product, 1)}
            className="p-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/30 transition-all duration-200 flex items-center gap-1.5 text-xs font-semibold"
            aria-label="Add to cart"
          >
            <FiShoppingBag className="text-sm" />
            <span className="hidden sm:inline">Add</span>
          </button>
        </div>

      </div>

    </div>
  );
}
