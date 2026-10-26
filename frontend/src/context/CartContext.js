"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api } from "@/Services/api";

const CartContext = createContext();

const LOCAL_CART_KEY = "storex_local_cart";

// ── Helpers ──────────────────────────────────────────────────────────────────

function loadLocalCart() {
  if (typeof window === "undefined") return { items: [], total_price: 0, total_items: 0 };
  try {
    const raw = localStorage.getItem(LOCAL_CART_KEY);
    return raw ? JSON.parse(raw) : { items: [], total_price: 0, total_items: 0 };
  } catch {
    return { items: [], total_price: 0, total_items: 0 };
  }
}

function saveLocalCart(cart) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(LOCAL_CART_KEY, JSON.stringify(cart));
  } catch { }
}

function recalCart(items) {
  const total_items = items.reduce((acc, item) => acc + item.quantity, 0);
  const total_price = items.reduce((acc, item) => acc + Number(item.subtotal || 0), 0);
  return { items, total_items, total_price };
}

function isLoggedIn() {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("token");
}

// ── Provider ─────────────────────────────────────────────────────────────────

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState({ items: [], total_price: 0, total_items: 0 });
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // Initialize cart on mount
  useEffect(() => {
    if (typeof window === "undefined") return;

    // Ensure session ID exists (used for backend session cart)
    let sessionId = localStorage.getItem("session_id");
    if (!sessionId) {
      sessionId = "sess_" + Math.random().toString(36).substring(2) + Date.now().toString(36);
      localStorage.setItem("session_id", sessionId);
    }

    initCart();
  }, []);

  const initCart = async () => {
    setLoading(true);
    if (isLoggedIn()) {
      // Try to sync with backend; fall back to local
      try {
        const data = await api.getCart();
        if (data && Array.isArray(data.items)) {
          const updated = { ...data };
          setCart(updated);
          saveLocalCart(updated);
        } else {
          setCart(loadLocalCart());
        }
      } catch {
        setCart(loadLocalCart());
      }
    } else {
      // Guest: use only local cart stored on device
      setCart(loadLocalCart());
    }
    setLoading(false);
  };

  const fetchCart = useCallback(async () => {
    await initCart();
  }, []);

  // ── Add to Cart ────────────────────────────────────────────────────────────
  const addToCart = useCallback(async (product, quantity = 1) => {
    const price = Number(product.current_price || product.price || 0);

    // Optimistic local update first
    setCart((prev) => {
      const existingIdx = prev.items.findIndex((item) => item.product?.id === product.id);
      let newItems = [...prev.items];

      if (existingIdx > -1) {
        const newQty = newItems[existingIdx].quantity + quantity;
        newItems[existingIdx] = {
          ...newItems[existingIdx],
          quantity: newQty,
          subtotal: price * newQty,
        };
      } else {
        newItems.push({
          id: `local_${product.id}_${Date.now()}`,
          product: product,
          quantity,
          subtotal: price * quantity,
        });
      }

      const updated = recalCart(newItems);
      saveLocalCart(updated);
      return updated;
    });

    // Background sync with backend if logged in
    if (isLoggedIn() && product.id) {
      try {
        const updatedCart = await api.addToCart(product.id, quantity);
        if (updatedCart && Array.isArray(updatedCart.items)) {
          setCart(updatedCart);
          saveLocalCart(updatedCart);
        }
      } catch (err) {
        console.warn("Backend cart sync failed, keeping local cart:", err);
      }
    }
  }, []);

  // ── Update Quantity ────────────────────────────────────────────────────────
  const updateQuantity = useCallback(async (itemId, quantity) => {
    setCart((prev) => {
      const newItems = prev.items
        .map((item) => {
          if (item.id === itemId) {
            if (quantity <= 0) return null;
            const price = Number(item.product?.current_price || item.product?.price || 0);
            return { ...item, quantity, subtotal: price * quantity };
          }
          return item;
        })
        .filter(Boolean);

      const updated = recalCart(newItems);
      saveLocalCart(updated);
      return updated;
    });

    // Backend sync if logged in (only for non-local IDs)
    if (isLoggedIn() && !String(itemId).startsWith("local_")) {
      try {
        const updatedCart = await api.updateCartItem(itemId, quantity);
        if (updatedCart && Array.isArray(updatedCart.items)) {
          setCart(updatedCart);
          saveLocalCart(updatedCart);
        }
      } catch (err) {
        console.warn("Backend cart update failed:", err);
      }
    }
  }, []);

  // ── Remove from Cart ───────────────────────────────────────────────────────
  const removeFromCart = useCallback(async (itemId) => {
    setCart((prev) => {
      const newItems = prev.items.filter((item) => item.id !== itemId);
      const updated = recalCart(newItems);
      saveLocalCart(updated);
      return updated;
    });

    if (isLoggedIn() && !String(itemId).startsWith("local_")) {
      try {
        const updatedCart = await api.removeCartItem(itemId);
        if (updatedCart && Array.isArray(updatedCart.items)) {
          setCart(updatedCart);
          saveLocalCart(updatedCart);
        }
      } catch (err) {
        console.warn("Backend cart remove failed:", err);
      }
    }
  }, []);

  // ── Clear Cart ─────────────────────────────────────────────────────────────
  const clearCart = useCallback(async () => {
    const empty = { items: [], total_price: 0, total_items: 0 };
    setCart(empty);
    saveLocalCart(empty);

    if (isLoggedIn()) {
      try {
        await api.clearCart();
      } catch (err) {
        console.warn("Backend cart clear failed:", err);
      }
    }
  }, []);

  return (
    <CartContext.Provider
      value={{
        cart,
        cartItems: cart.items || [],
        cartCount: cart.total_items || 0,
        cartTotal: cart.total_price || 0,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
        isCartOpen,
        setIsCartOpen,
        loading,
        fetchCart,
      }}
    >
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => useContext(CartContext);
