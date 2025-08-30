"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";
import Link from "next/link";
import "./style.css";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  const routes = [
    { id: 0, name: "Companies", href: "/" },
    { id: 1, name: "Write a review", href: "/review" },
    { id: 2, name: "About", href: "/about" },
    { id: 3, name: "Docs", href: "/docs" },
  ];

  return (
    <div className="navbar">
      {/* Brand */}
      <div className="nav-name">
        <Link href="/">
          <h1>Anondoor</h1>
        </Link>
      </div>

      {/* Desktop nav */}
      <nav className="nav-links">
        {routes.map((route) => (
          <div key={route.id}>
            <Link href={route.href}>
              <p>{route.name}</p>
            </Link>
          </div>
        ))}
      </nav>

      {/* Desktop CTAs */}
      <div className="nav-cta">
        <button className="secondary-button-nav">Sign in</button>
      </div>

      {/* Mobile toggle */}
      <button
        className="menu-toggle"
        onClick={() => setIsOpen((prev) => !prev)}
      >
        {isOpen ? <X className="icon" /> : <Menu className="icon" />}
      </button>

      {/* Mobile dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            key="dropdown"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="mobile-menu"
          >
            <nav className="mobile-nav">
              {routes.map((route) => (
                <Link key={route.id} href={route.href} className="mobile-link">
                  <p>{route.name}</p>
                </Link>
              ))}
            </nav>
            <div className="mobile-cta">
              <button className="secondary-button-nav">Sign in</button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
