"use client";

import React from "react";
import Link from "next/link";
import { FiTrash2, FiPlus, FiMinus, FiShoppingBag, FiArrowRight, FiCheckCircle } from "react-icons/fi";
import { useCart } from "@/context/CartContext";

export default function CartPage() {
  const { cartItems, cartTotal, updateQuantity, removeFromCart, clearCart } = useCart();

  const subtotal = Number(cartTotal || 0);
  const shipping = subtotal > 50 || subtotal === 0 ? 0 : 9.99;
  const tax = subtotal * 0.08;
  const grandTotal = subtotal + shipping + tax;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-3xl font-black text-white mb-8">Shopping Cart</h1>

      {cartItems.length === 0 ? (
        <div className="glass-card rounded-3xl p-16 text-center max-w-xl mx-auto my-12 border border-slate-800">
          <FiShoppingBag className="text-6xl text-slate-600 mx-auto mb-4 opacity-50" />
          <h2 className="text-xl font-bold text-slate-200">Your cart is currently empty</h2>
          <p className="text-xs text-slate-400 mt-2 mb-6">
            Looks like you haven&apos;t added anything to your cart yet. Explore our featured products and tech gear!
          </p>
          <Link
            href="/products"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-xs font-bold text-white btn-gradient shadow-lg"
          >
            <span>Start Shopping</span>
            <FiArrowRight />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Cart Items List */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex justify-between items-center pb-4 border-b border-slate-800 text-xs text-slate-400 font-semibold">
              <span>Product Details</span>
              <button
                onClick={clearCart}
                className="text-red-400 hover:text-red-300 flex items-center gap-1 transition-colors"
              >
                <FiTrash2 />
                <span>Clear Cart</span>
              </button>
            </div>

            {cartItems.map((item) => {
              const prod = item.product || {};
              const image = prod.images?.[0]?.image || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80";
              const price = Number(prod.current_price || prod.price || item.subtotal || 0);

              return (
                <div
                  key={item.id}
                  className="glass-card rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4 border border-slate-800"
                >
                  <div className="flex items-center gap-4 w-full sm:w-auto">
                    <img
                      src={image}
                      alt={prod.name || "Item"}
                      className="w-20 h-20 object-cover rounded-xl bg-slate-900 shrink-0"
                    />
                    <div>
                      <h3 className="font-bold text-slate-100 text-base line-clamp-1">{prod.name || "Product Item"}</h3>
                      <span className="text-xs text-blue-400 font-bold">${price.toFixed(2)}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between sm:justify-end gap-6 w-full sm:w-auto">
                    {/* Quantity Controls */}
                    <div className="flex items-center border border-slate-700 rounded-xl bg-slate-900">
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        className="p-2 hover:text-blue-400"
                      >
                        <FiMinus className="text-xs" />
                      </button>
                      <span className="px-3 text-xs font-bold">{item.quantity}</span>
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        className="p-2 hover:text-blue-400"
                      >
                        <FiPlus className="text-xs" />
                      </button>
                    </div>

                    {/* Item Subtotal */}
                    <span className="font-extrabold text-white text-base min-w-[70px] text-right">
                      ${(price * item.quantity).toFixed(2)}
                    </span>

                    {/* Delete button */}
                    <button
                      onClick={() => removeFromCart(item.id)}
                      className="p-2 text-slate-500 hover:text-red-400 transition-colors"
                    >
                      <FiTrash2 className="text-base" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Order Summary Box */}
          <div className="space-y-6">
            <div className="glass-card rounded-3xl p-6 border border-slate-800 space-y-6">
              <h2 className="text-lg font-bold text-white border-b border-slate-800 pb-4">Order Summary</h2>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between text-slate-400">
                  <span>Subtotal</span>
                  <span className="font-semibold text-slate-200">${subtotal.toFixed(2)}</span>
                </div>

                <div className="flex justify-between text-slate-400">
                  <span>Estimated Shipping</span>
                  <span className="font-semibold text-slate-200">
                    {shipping === 0 ? <span className="text-emerald-400">FREE</span> : `$${shipping.toFixed(2)}`}
                  </span>
                </div>

                <div className="flex justify-between text-slate-400">
                  <span>Estimated Tax (8%)</span>
                  <span className="font-semibold text-slate-200">${tax.toFixed(2)}</span>
                </div>
              </div>

              <div className="border-t border-slate-800 pt-4 flex justify-between items-center text-base font-extrabold text-white">
                <span>Total Amount</span>
                <span className="text-2xl text-blue-400">${grandTotal.toFixed(2)}</span>
              </div>

              <Link
                href="/checkout"
                className="w-full py-4 rounded-xl font-bold text-sm text-white btn-gradient flex items-center justify-center gap-2 shadow-xl shadow-blue-500/25 block text-center"
              >
                <span>Proceed to Checkout</span>
                <FiArrowRight />
              </Link>
            </div>

            <div className="p-4 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center gap-3 text-xs text-blue-300">
              <FiCheckCircle className="text-lg shrink-0 text-blue-400" />
              <span>Orders over $50 qualify for free express shipping & 30-day hassle free returns.</span>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
