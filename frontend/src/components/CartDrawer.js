"use client";

import React from "react";
import Link from "next/link";
import { FiX, FiTrash2, FiPlus, FiMinus, FiShoppingBag, FiArrowRight } from "react-icons/fi";
import { useCart } from "@/context/CartContext";

export default function CartDrawer() {
  const { cartItems, cartTotal, isCartOpen, setIsCartOpen, updateQuantity, removeFromCart } = useCart();

  if (!isCartOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden animate-fade-in">
      {/* Backdrop */}
      <div
        onClick={() => setIsCartOpen(false)}
        className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm transition-opacity"
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-slate-900 border-l border-slate-800 text-slate-100 flex flex-col shadow-2xl">
          
          {/* Drawer Header */}
          <div className="p-6 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FiShoppingBag className="text-xl text-blue-400" />
              <h2 className="text-lg font-bold">Your Shopping Cart</h2>
              <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full font-semibold">
                {cartItems.length} items
              </span>
            </div>
            <button
              onClick={() => setIsCartOpen(false)}
              className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            >
              <FiX className="text-xl" />
            </button>
          </div>

          {/* Drawer Items List */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {cartItems.length === 0 ? (
              <div className="text-center py-16 text-slate-500">
                <FiShoppingBag className="text-5xl mx-auto mb-4 opacity-40" />
                <p className="text-base font-semibold text-slate-300">Your cart is empty</p>
                <p className="text-xs mt-1 text-slate-400">Add products to your cart to checkout.</p>
              </div>
            ) : (
              cartItems.map((item) => {
                const prod = item.product || {};
                const image = prod.images?.[0]?.image || "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80";
                const price = Number(prod.current_price || prod.price || item.subtotal || 0);

                return (
                  <div key={item.id} className="flex gap-4 p-3 rounded-xl bg-slate-800/50 border border-slate-800">
                    <img
                      src={image}
                      alt={prod.name || "Product"}
                      className="w-20 h-20 object-cover rounded-lg bg-slate-900"
                    />
                    <div className="flex-1 flex flex-col justify-between">
                      <div>
                        <h4 className="text-sm font-semibold text-slate-100 line-clamp-1">{prod.name || "Item"}</h4>
                        <span className="text-xs text-blue-400 font-bold">${price.toFixed(2)}</span>
                      </div>

                      <div className="flex items-center justify-between mt-2">
                        {/* Quantity Counter */}
                        <div className="flex items-center border border-slate-700 rounded-lg bg-slate-900">
                          <button
                            onClick={() => updateQuantity(item.id, item.quantity - 1)}
                            className="p-1 hover:text-blue-400"
                          >
                            <FiMinus className="text-xs" />
                          </button>
                          <span className="px-3 text-xs font-bold">{item.quantity}</span>
                          <button
                            onClick={() => updateQuantity(item.id, item.quantity + 1)}
                            className="p-1 hover:text-blue-400"
                          >
                            <FiPlus className="text-xs" />
                          </button>
                        </div>

                        {/* Remove */}
                        <button
                          onClick={() => removeFromCart(item.id)}
                          className="text-slate-500 hover:text-red-400 p-1 transition-colors"
                        >
                          <FiTrash2 className="text-sm" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Drawer Footer / Checkout button */}
          {cartItems.length > 0 && (
            <div className="p-6 border-t border-slate-800 bg-slate-950/60 space-y-4">
              <div className="flex justify-between items-center text-sm font-semibold">
                <span className="text-slate-400">Subtotal</span>
                <span className="text-xl font-extrabold text-white">${Number(cartTotal).toFixed(2)}</span>
              </div>
              <p className="text-xs text-slate-500">Shipping and taxes calculated at checkout.</p>

              <div className="flex gap-3">
                <Link
                  href="/cart"
                  onClick={() => setIsCartOpen(false)}
                  className="flex-1 text-center py-3 px-4 rounded-xl text-xs font-bold btn-secondary"
                >
                  View Cart
                </Link>
                <Link
                  href="/checkout"
                  onClick={() => setIsCartOpen(false)}
                  className="flex-1 text-center py-3 px-4 rounded-xl text-xs font-bold text-white btn-gradient flex items-center justify-center gap-2"
                >
                  <span>Checkout</span>
                  <FiArrowRight />
                </Link>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
