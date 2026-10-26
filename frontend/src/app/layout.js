"use client";

import React from "react";
import "./globals.css";
import { CartProvider } from "@/context/CartContext";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import CartDrawer from "@/components/CartDrawer";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { usePathname } from "next/navigation";

function AppShell({ children }) {
  const pathname = usePathname();
  // Admin dashboard has its own full-page layout — no shared navbar/footer
  const isAdminDashboard = pathname?.startsWith("/admin/dashboard");

  if (isAdminDashboard) {
    return <>{children}</>;
  }

  return (
    <>
      <Navbar />
      <CartDrawer />
      <main className="flex-1">{children}</main>
      <Footer />
    </>
  );
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <title>STOREX — Modern E-Commerce Store</title>
        <meta name="description" content="Discover premium electronics, apparel, and lifestyle gear with fast shipping." />
      </head>
      <body className="bg-slate-950 text-slate-100 min-h-screen flex flex-col antialiased">
        <CartProvider>
          <AppShell>{children}</AppShell>
          <ToastContainer
            position="bottom-right"
            autoClose={3000}
            theme="dark"
            hideProgressBar={false}
          />
        </CartProvider>
      </body>
    </html>
  );
}
