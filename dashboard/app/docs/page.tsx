/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║                                                                  ║
 * ║   ░█▀█░▀█▀░▀▀█░█▀▀░█▀█   ░█░█░█▀▀░█░█                         ║
 * ║   ░█▀█░░█░░▄▀░░█▀▀░█░█   ░▄▀▄░█▀▀░▄▀▄                         ║
 * ║   ░▀░▀░▀▀▀░█▄▄░▀▀▀░▀░▀   ░▀░▀░▀░░░▀░▀                         ║
 * ║                                                                  ║
 * ║           © 2026 Aizen XFX — All Rights Reserved                ║
 * ║                                                                  ║
 * ║   discord  ──  https://discord.gg/M8qJ9W7vBb                    ║
 * ║   youtube  ──  https://youtube.com/@aizen_xfx                   ║
 * ║   github   ──  https://github.com/aizenxfx05                    ║
 * ║                                                                  ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

"use client";

import React, { useState } from "react";
import Link from "next/link";
import { 
  Bot, 
  ChevronLeft, 
  Search, 
  ShieldCheck, 
  Zap, 
  Activity, 
  Layers, 
  Sparkles,
  Search as SearchIcon,
  BookOpen,
  Menu,
  X
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const DOCS_NAV = [
  {
    title: "Getting Started",
    items: [
      { name: "Introduction", description: "Learn about the Neural Core." },
      { name: "Quick Start", description: "Deploy in 30 seconds." },
      { name: "Architecture", description: "Deep dive into our engine." }
    ]
  },
  {
    title: "Security Modules",
    items: [
      { name: "Anti-Nuke", description: "Absolute lockdown protocols." },
      { name: "Verification", description: "Captcha & Neural checks." },
      { name: "Automod", description: "Context-aware AI filtering." }
    ]
  },
  {
    title: "Management",
    items: [
      { name: "Join to Create", description: "Dynamic voice channels." },
      { name: "Leveling", description: "Cinematic rank generation." },
      { name: "Tickets", description: "Enterprise helpdesk." }
    ]
  }
];

export default function DocsPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("Introduction");

  return (
    <div className="min-h-screen bg-[#07070D] text-[#F3E8FF] font-sans">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-[#A855F7]/[0.02] blur-[150px] rounded-full" />
      </div>

      {/* Nav */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/[0.03] bg-[#07070D]/80 backdrop-blur-3xl px-6 h-20 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-4 group">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-[#A855F7] to-[#7C3AED] flex items-center justify-center mr-3 overflow-hidden relative">
              <img 
                src="/logo.png" 
                alt="Logo" 
                className="h-full w-full object-cover relative z-10" 
                onError={(e) => {
                  e.currentTarget.style.display = "none";
                }} 
              />
              <Bot className="h-5 w-5 text-white absolute z-0" />
            </div>
            <span className="text-xl font-bold text-white font-outfit uppercase tracking-tighter hidden md:block">{process.env.NEXT_PUBLIC_BRAND_NAME || "Aizen XFX"} Docs</span>
          </Link>
          
          <div className="hidden lg:flex items-center w-80 relative group">
            <SearchIcon className="absolute left-4 h-4 w-4 text-[#57534E] group-focus-within:text-[#A855F7] transition-colors" />
            <input
              type="text"
              placeholder="Search documentation..."
              className="w-full bg-white/[0.03] border border-white/5 rounded-2xl py-2.5 pl-12 pr-4 text-xs font-bold text-[#F3E8FF] focus:outline-none focus:ring-1 focus:ring-[#A855F7]/30 focus:bg-white/[0.05] transition-all"
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
           <button 
             className="lg:hidden p-2 text-slate-400"
             onClick={() => setIsSidebarOpen(!isSidebarOpen)}
           >
             {isSidebarOpen ? <X /> : <Menu />}
           </button>
           <Link href="/">
            <Button variant="ghost" className="text-slate-400 hover:text-white gap-2 text-xs font-black uppercase tracking-widest">
              Exit Docs
            </Button>
          </Link>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto flex pt-20">
        {/* Sidebar */}
        <aside className={cn(
          "fixed inset-y-0 left-0 z-40 w-80 bg-[#07070D] border-r border-[#A855F7]/[0.06] pt-20 transition-transform lg:translate-x-0 lg:static lg:bg-transparent",
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}>
          <div className="h-full p-8 overflow-y-auto no-scrollbar">
            {DOCS_NAV.map((section) => (
              <div key={section.title} className="mb-10">
                <h4 className="text-[10px] font-black uppercase tracking-[0.4em] text-slate-600 mb-6">{section.title}</h4>
                <div className="space-y-1">
                  {section.items.map((item) => (
                    <button
                      key={item.name}
                      onClick={() => {
                        setActiveTab(item.name);
                        setIsSidebarOpen(false);
                      }}
                      className={cn(
                        "w-full flex flex-col items-start gap-1 p-4 rounded-2xl transition-all text-left",
                        activeTab === item.name
                          ? "bg-[#A855F7]/[0.08] border border-[#A855F7]/20 shadow-[0_0_20px_rgba(168,85,247,0.05)]"
                          : "hover:bg-white/[0.02] border border-transparent"
                      )}
                    >
                      <span className={cn("text-sm font-bold", activeTab === item.name ? "text-[#A855F7]" : "text-[#F3E8FF]")}>{item.name}</span>
                      <span className="text-[10px] text-slate-600 font-bold uppercase tracking-tight">{item.description}</span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* Content */}
        <main className="flex-1 p-8 lg:p-16 relative z-10 max-w-4xl">
           <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#A855F7]/10 border border-[#A855F7]/20 text-[#A855F7] text-[10px] font-black uppercase tracking-widest mb-8">
            <BookOpen className="h-3 w-3" />
            V2.4 Runtime Environment
          </div>

          <h1 className="text-6xl font-bold text-white font-outfit tracking-tighter uppercase mb-8 italic">
            {activeTab}<span className="text-purple-gradient not-italic">.</span>
          </h1>

          <div className="prose prose-invert max-w-none">
             <p className="text-lg text-[#948BA3] mb-12 leading-relaxed">
               Welcome to the {activeTab} section of the {process.env.NEXT_PUBLIC_BRAND_NAME || "Aizen XFX"} documentation. Our bot is designed for communities that demand absolute performance and elite management tools.
             </p>

             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-8 rounded-[32px] glass border-white/5 space-y-4">
                   <Zap className="h-6 w-6 text-[#A855F7]" />
                   <h3 className="text-xl font-bold text-white font-outfit uppercase">Fast Dispatch</h3>
                   <p className="text-sm text-slate-500 font-bold uppercase tracking-tight">Commands are dispatched via our global edge network in under 12ms.</p>
                </div>
                <div className="p-8 rounded-[32px] glass border-white/5 space-y-4">
                   <ShieldCheck className="h-6 w-6 text-emerald-500" />
                   <h3 className="text-xl font-bold text-white font-outfit uppercase">Secure Node</h3>
                   <p className="text-sm text-slate-500 font-bold uppercase tracking-tight">Every module runs in a dedicated neural sandbox with AES-256 encryption.</p>
                </div>
             </div>

              <div className="p-8 rounded-[40px] bg-[#A855F7]/[0.02] border border-[#A855F7]/10 relative overflow-hidden">
                 <div className="absolute top-0 right-0 p-8 opacity-10">
                    <Layers className="h-32 w-32 text-[#A855F7]" />
                 </div>
                <h2 className="text-2xl font-bold text-white font-outfit uppercase tracking-tight mb-4">Neural Architecture</h2>
                  <h3 className="text-white font-bold">Protocol Overview</h3>
                 <p className="text-[#948BA3] font-bold leading-relaxed mb-8">
                   {process.env.NEXT_PUBLIC_BRAND_NAME || "Aizen XFX"} utilizes a decentralized event stream processing model. When a Discord event is received, it is instantly routed to the nearest edge cluster.
                 </p>
                 <div className="bg-black/40 p-6 rounded-2xl border border-white/5 font-mono text-sm text-[#A855F7] mb-8">
                   $ aizen initialize --cluster-shard [neural_07] --mode enterprise
                 </div>
             </div>
          </div>

          <div className="mt-20 pt-12 border-t border-white/5 flex items-center justify-between">
             <div>
                <p className="text-[10px] font-black uppercase text-slate-600 tracking-[0.4em] mb-2">Internal Ref</p>
                <p className="text-sm font-bold text-slate-400">DOC-ID: CX_7749_B</p>
             </div>
             <div className="flex items-center gap-2">
                 <div className="h-2 w-2 rounded-full bg-[#A855F7] animate-pulse" />
                 <span className="text-[10px] font-black uppercase text-[#A855F7] tracking-[0.2em]">Live Stream Active</span>
              </div>
          </div>
        </main>
      </div>
    </div>
  );
}
