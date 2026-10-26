"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { FiStar, FiShoppingBag, FiTruck, FiShield, FiRefreshCw, FiPlus, FiMinus, FiCheck, FiZoomIn } from "react-icons/fi";
import { useCart } from "@/context/CartContext";
import { api } from "@/Services/api";

const DEMO_PRODUCT = {
  id: 1,
  name: "Men's Royal Silk Kurta Pajama Set",
  slug: "mens-royal-silk-kurta-pajama-set",
  category: "Kurta Pajama",
  gender: "MEN",
  brand: "Heritage Ethnic",
  price: 120.00,
  discount_price: 95.00,
  discount_percentage: 21,
  stock: 30,
  rating: 4.9,
  num_reviews: 28,
  description: "Handcrafted dupion silk Kurta Pajama set with subtle embroidery on collar and cuffs. Designed for weddings, festivals, and grand celebratory occasions.",
  short_description: "Traditional silk Kurta Pajama set for men.",
  images: [
    { image: "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=1000&auto=format&fit=crop&q=80" },
    { image: "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=1000&auto=format&fit=crop&q=80" }
  ],
  reviews: [
    { id: 1, user_name: "Rohan S.", rating: 5, comment: "Authentic silk feel and perfect fitting! Received many compliments.", created_at: "2026-02-12" }
  ]
};

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { addToCart } = useCart();

  const [product, setProduct] = useState(DEMO_PRODUCT);
  const [selectedImage, setSelectedImage] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [added, setAdded] = useState(false);
  const [zoomStyle, setZoomStyle] = useState({ display: "none", transformOrigin: "0% 0%" });

  useEffect(() => {
    if (params?.slug) {
      fetchProduct(params.slug);
    }
  }, [params?.slug]);

  const fetchProduct = async (slug) => {
    try {
      setLoading(true);
      const data = await api.getProductBySlug(slug);
      if (data && data.name) {
        setProduct(data);
        if (data.images && data.images.length > 0) {
          setSelectedImage(data.images[0].image);
        }
      }
    } catch (err) {
      console.warn("Using demo clothing detail fallback", err);
      setSelectedImage(DEMO_PRODUCT.images[0].image);
    } finally {
      setLoading(false);
    }
  };

  const handleMouseMove = (e) => {
    const { left, top, width, height } = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - left) / width) * 100;
    const y = ((e.clientY - top) / height) * 100;
    setZoomStyle({
      display: "block",
      transformOrigin: `${x}% ${y}%`,
    });
  };

  const handleMouseLeave = () => {
    setZoomStyle({ display: "none", transformOrigin: "0% 0%" });
  };

  const handleAddToCart = () => {
    addToCart(product, quantity);
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  };

  const price = Number(product.price || 0);
  const discountPrice = product.discount_price ? Number(product.discount_price) : null;
  const currentPrice = discountPrice || price;
  const discountPercent = product.discount_percentage || (discountPrice ? Math.round(((price - discountPrice) / price) * 100) : 0);
  const mainImg = selectedImage || (product.images?.[0]?.image) || "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=1000&auto=format&fit=crop&q=80";

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">

      {/* Breadcrumb */}
      <div className="text-xs text-slate-400 mb-8 flex items-center gap-2">
        <span onClick={() => router.push("/")} className="hover:text-white cursor-pointer">Home</span>
        <span>/</span>
        <span onClick={() => router.push("/products")} className="hover:text-white cursor-pointer">Products</span>
        <span>/</span>
        <span className="text-blue-400 font-semibold">{product.name}</span>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">

        {/* Left: Gallery with Image Zoom */}
        <div className="space-y-4">
          <div
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            className="glass-card rounded-3xl p-4 overflow-hidden relative aspect-4/5 bg-slate-900 border border-slate-800 cursor-crosshair group"
          >
            <img
              src={mainImg}
              alt={product.name}
              className="w-full h-full object-cover rounded-2xl transition-transform duration-200"
              style={{
                transform: zoomStyle.display === "block" ? "scale(2.2)" : "scale(1)",
                transformOrigin: zoomStyle.transformOrigin,
              }}
            />

            <div className="absolute top-6 right-6 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-full text-xs text-slate-300 flex items-center gap-1.5 opacity-80 group-hover:opacity-100 transition-opacity">
              <FiZoomIn />
              <span>Hover to Zoom</span>
            </div>
          </div>

          {/* Thumbnails */}
          {product.images && product.images.length > 1 && (
            <div className="flex gap-4 overflow-x-auto pb-2">
              {product.images.map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedImage(img.image)}
                  className={`w-20 h-24 rounded-xl overflow-hidden border-2 transition-all shrink-0 ${selectedImage === img.image ? "border-blue-500 scale-105" : "border-slate-800 opacity-60 hover:opacity-100"
                    }`}
                >
                  <img src={img.image} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right: Product Specs */}
        <div className="space-y-6">

          <div>
            <div className="flex items-center gap-3 text-xs mb-2">
              <span className="px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 font-bold border border-blue-500/20">
                {product.category_detail?.name || product.category || "Apparel"}
              </span>
              <span className="px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 font-bold">
                {product.gender === "MEN" ? "Men's Collection" : product.gender === "WOMEN" ? "Women's Collection" : "Unisex"}
              </span>
              {product.brand_detail?.name && (
                <span className="text-slate-400 font-semibold">{product.brand_detail.name}</span>
              )}
            </div>

            <h1 className="text-3xl sm:text-4xl font-black text-white">{product.name}</h1>

            {/* Rating */}
            <div className="flex items-center gap-2 mt-3 text-xs text-slate-400">
              <div className="flex text-amber-400">
                {[...Array(5)].map((_, i) => (
                  <FiStar key={i} className="fill-amber-400" />
                ))}
              </div>
              <span className="font-bold text-slate-200">{product.rating}</span>
              <span>({product.num_reviews} customer reviews)</span>
            </div>
          </div>

          {/* Pricing Box */}
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 flex items-center gap-4">
            <span className="text-3xl font-black text-white">
              Rs. {currentPrice.toLocaleString()}
            </span>

            {discountPrice && (
              <span className="text-lg text-slate-500 line-through">
                Rs. {price.toLocaleString()}
              </span>
            )}

            {discountPercent > 0 && (
              <span className="text-xs bg-red-500/20 text-red-400 font-bold px-3 py-1 rounded-full border border-red-500/30">
                {discountPercent}% OFF
              </span>
            )}
          </div>

          <p className="text-slate-300 text-sm leading-relaxed">{product.description}</p>

          {/* Quantity and Actions */}
          <div className="pt-4 border-t border-slate-800 space-y-4">
            <div className="flex items-center gap-4">
              <span className="text-xs font-bold text-slate-400">Quantity</span>
              <div className="flex items-center border border-slate-700 rounded-xl bg-slate-900">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="p-2.5 hover:text-blue-400"
                >
                  <FiMinus />
                </button>
                <span className="px-4 font-bold text-sm">{quantity}</span>
                <button
                  onClick={() => setQuantity(quantity + 1)}
                  className="p-2.5 hover:text-blue-400"
                >
                  <FiPlus />
                </button>
              </div>
              <span className="text-xs text-emerald-400 font-semibold">
                In Stock ({product.stock} available)
              </span>
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleAddToCart}
                className={`flex-1 py-4 px-6 rounded-xl font-bold text-sm flex items-center justify-center gap-2 shadow-xl transition-all ${added
                    ? "bg-emerald-600 text-white"
                    : "btn-gradient text-white shadow-blue-500/25"
                  }`}
              >
                {added ? <FiCheck className="text-lg" /> : <FiShoppingBag className="text-lg" />}
                <span>{added ? "Added to Cart!" : "Add to Shopping Cart"}</span>
              </button>
            </div>
          </div>

          {/* Value Props */}
          <div className="grid grid-cols-3 gap-3 pt-4 border-t border-slate-800 text-center">
            <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800">
              <FiTruck className="text-lg text-blue-400 mx-auto mb-1" />
              <span className="text-[10px] font-semibold text-slate-300 block">Cash on Delivery</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800">
              <FiShield className="text-lg text-indigo-400 mx-auto mb-1" />
              <span className="text-[10px] font-semibold text-slate-300 block">Original Quality</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800">
              <FiRefreshCw className="text-lg text-purple-400 mx-auto mb-1" />
              <span className="text-[10px] font-semibold text-slate-300 block">Easy Returns</span>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
