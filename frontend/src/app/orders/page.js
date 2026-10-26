"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { FiPackage, FiClock, FiCheck, FiTruck, FiShoppingBag } from "react-icons/fi";
import { api } from "@/Services/api";

const DEMO_ORDERS = [
  {
    id: 1,
    order_number: "ORD-98F2A10B",
    created_at: "2026-09-20T14:30:00Z",
    total_amount: "238.99",
    order_status: "DELIVERED",
    payment_status: "PAID",
    items: [
      { id: 1, product: { name: "Nexus Pro Wireless Headphones" }, quantity: 1, price: "149.99" },
      { id: 2, product: { name: "Luxe Ambient Ceramic Desk Lamp" }, quantity: 1, price: "89.00" }
    ]
  },
  {
    id: 2,
    order_number: "ORD-41B9C78E",
    created_at: "2026-09-21T09:15:00Z",
    total_amount: "199.99",
    order_status: "PROCESSING",
    payment_status: "PAID",
    items: [
      { id: 3, product: { name: "Smart Fitness Watch Ultra" }, quantity: 1, price: "199.99" }
    ]
  }
];

export default function OrdersPage() {
  const [orders, setOrders] = useState(DEMO_ORDERS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const data = await api.getOrders();
      if (data && (data.results || Array.isArray(data))) {
        const orderList = data.results || data;
        if (orderList.length > 0) setOrders(orderList);
      }
    } catch (err) {
      console.warn("Using demo orders fallback", err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "DELIVERED":
        return <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-bold rounded-full border border-emerald-500/20 flex items-center gap-1.5"><FiCheck /> Delivered</span>;
      case "SHIPPED":
        return <span className="px-3 py-1 bg-blue-500/10 text-blue-400 text-xs font-bold rounded-full border border-blue-500/20 flex items-center gap-1.5"><FiTruck /> Shipped</span>;
      case "PROCESSING":
      default:
        return <span className="px-3 py-1 bg-amber-500/10 text-amber-400 text-xs font-bold rounded-full border border-amber-500/20 flex items-center gap-1.5"><FiClock /> Processing</span>;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex items-center gap-3 mb-8">
        <FiPackage className="text-3xl text-blue-400" />
        <div>
          <h1 className="text-3xl font-black text-white">Order History</h1>
          <p className="text-slate-400 text-xs">Track and view your recent purchases.</p>
        </div>
      </div>

      {orders.length === 0 ? (
        <div className="glass-card rounded-3xl p-16 text-center max-w-md mx-auto my-12">
          <FiPackage className="text-5xl text-slate-600 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-bold text-slate-200">No orders found</h3>
          <p className="text-xs text-slate-400 mt-1 mb-6">You haven&apos;t placed any orders yet.</p>
          <Link href="/products" className="px-6 py-3 rounded-xl text-xs font-bold text-white btn-gradient inline-flex items-center gap-2">
            <FiShoppingBag />
            <span>Start Shopping</span>
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {orders.map((order) => (
            <div key={order.id} className="glass-card rounded-3xl p-6 border border-slate-800 space-y-4">
              
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
                <div>
                  <span className="text-xs text-slate-400">Order Number</span>
                  <h3 className="font-extrabold text-base text-white">{order.order_number}</h3>
                  <span className="text-xs text-slate-500">
                    Placed on {new Date(order.created_at).toLocaleDateString()}
                  </span>
                </div>

                <div className="flex items-center gap-4">
                  {getStatusBadge(order.order_status)}
                  <div className="text-right">
                    <span className="text-xs text-slate-400 block">Total</span>
                    <span className="text-lg font-black text-white">${Number(order.total_amount).toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {/* Items */}
              <div className="space-y-2">
                {order.items?.map((item, idx) => (
                  <div key={idx} className="flex justify-between items-center text-xs py-1">
                    <span className="text-slate-300">
                      {item.quantity}x {item.product?.name || "Product Item"}
                    </span>
                    <span className="font-bold text-slate-100">${Number(item.price || 0).toFixed(2)}</span>
                  </div>
                ))}
              </div>

            </div>
          ))}
        </div>
      )}
    </div>
  );
}
