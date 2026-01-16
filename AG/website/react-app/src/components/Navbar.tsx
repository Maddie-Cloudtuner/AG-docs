"use client";
import Link from "next/link";
import { useState } from "react";
import { Menu, X } from "lucide-react";

export default function Navbar() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <nav className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-md border-b border-border">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-20">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded bg-primary flex items-center justify-center text-white font-bold font-heading text-lg">
                            C
                        </div>
                        <span className="font-heading text-xl font-bold text-white">
                            CloudTuner
                        </span>
                    </Link>

                    {/* Desktop Nav */}
                    <div className="hidden md:flex items-center space-x-8">
                        <Link href="/product" className="text-sm font-medium text-slate-300 hover:text-primary transition-colors">Product</Link>
                        <Link href="/solutions" className="text-sm font-medium text-slate-300 hover:text-primary transition-colors">Solutions</Link>
                        <Link href="/pricing" className="text-sm font-medium text-slate-300 hover:text-primary transition-colors">Pricing</Link>
                        <Link href="/resources" className="text-sm font-medium text-slate-300 hover:text-primary transition-colors">Resources</Link>
                    </div>

                    {/* Actions */}
                    <div className="hidden md:flex items-center gap-4">
                        <Link href="https://dev.dashboard.cloudtuner.ai/public" className="text-sm font-medium text-white hover:text-primary transition-colors">
                            Log In
                        </Link>
                        <Link
                            href="/demo"
                            className="px-5 py-2.5 rounded-lg bg-primary hover:bg-primary-hover text-white font-bold text-sm transition-colors"
                        >
                            Get Started
                        </Link>
                    </div>

                    {/* Mobile Toggle */}
                    <div className="md:hidden">
                        <button onClick={() => setIsOpen(!isOpen)} className="text-slate-300 hover:text-white">
                            {isOpen ? <X /> : <Menu />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {isOpen && (
                <div className="md:hidden bg-surface border-b border-border">
                    <div className="px-4 pt-4 pb-6 space-y-2">
                        {["Product", "Solutions", "Pricing", "Resources"].map((item) => (
                            <Link
                                key={item}
                                href={`/${item.toLowerCase()}`}
                                className="block px-3 py-2 text-base font-medium text-slate-300 hover:text-white hover:bg-white/5 rounded-md"
                            >
                                {item}
                            </Link>
                        ))}
                        <div className="pt-4 mt-4 border-t border-border">
                            <Link href="/login" className="block px-3 py-2 text-base font-medium text-slate-300">Log In</Link>
                            <Link href="/demo" className="block px-3 py-2 text-base font-medium text-primary">Get Started</Link>
                        </div>
                    </div>
                </div>
            )}
        </nav>
    );
}
