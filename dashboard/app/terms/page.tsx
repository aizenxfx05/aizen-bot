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

import React from "react";
import Link from "next/link";
import { Bot, ChevronLeft, Scale, Terminal, ShieldAlert, Cpu } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-[#050508] text-[#FAFAF9] font-sans">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute bottom-[-10%] left-[-5%] w-[40%] h-[40%] bg-[#EAB308]/[0.025] blur-[120px] rounded-full" />
      </div>

      <nav className="fixed top-0 w-full z-50 border-b border-white/[0.03] bg-[#050508]/80 backdrop-blur-3xl px-6 h-20 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-4 group">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-[#EAB308] to-[#92400E] flex items-center justify-center group-hover:rotate-12 transition-transform">
            <Bot className="h-5 w-5 text-[#050508]" />
          </div>
          <span className="text-xl font-bold text-white font-outfit uppercase tracking-tighter">{process.env.NEXT_PUBLIC_BRAND_NAME || "Aizen XFX"}</span>
        </Link>
        <Link href="/">
          <Button variant="ghost" className="text-slate-400 hover:text-white gap-2">
            <ChevronLeft className="h-4 w-4" />
            Back to Home
          </Button>
        </Link>
      </nav>

      <main className="relative z-10 pt-40 pb-32 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#EAB308]/10 border border-[#EAB308]/20 text-[#EAB308] text-[10px] font-black uppercase tracking-widest mb-8">
            <Scale className="h-3 w-3" />
            Legal Protocol v2.4
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-white font-outfit tracking-tighter uppercase mb-12 italic text-right">
            Terms of <span className="text-amber-gradient not-italic">Service.</span>
          </h1>

          <div className="glass border-white/5 rounded-[40px] p-10 md:p-16 space-y-12 bg-gradient-to-br from-white/[0.01] to-transparent">
            <section className="space-y-6">
              <div className="flex items-center gap-4 text-white">
                <div className="h-10 w-10 rounded-2xl bg-white/5 border border-[#EAB308]/10 flex items-center justify-center text-[#EAB308]">
                   <Terminal className="h-5 w-5" />
                </div>
                <h2 className="text-2xl font-bold font-outfit uppercase tracking-tight">Acceptance of Protocol</h2>
              </div>
              <p className="text-[#78716C] leading-relaxed font-medium">
                By integrating {process.env.NEXT_PUBLIC_BRAND_NAME || "Aizen XFX"} into your Discord server, you agree to abide by these terms. The bot is provided &quot;as is,&quot; and while we strive for 100% uptime through our neural edge clusters, we are not liable for any data loss resulting from third-party API disruptions.
              </p>
            </section>

            <section className="space-y-6">
              <div className="flex items-center gap-4 text-white">
                <div className="h-10 w-10 rounded-2xl bg-white/5 border border-[#EAB308]/10 flex items-center justify-center text-[#EAB308]">
                   <ShieldAlert className="h-5 w-5" />
                </div>
                <h2 className="text-2xl font-bold font-outfit uppercase tracking-tight">Usage Constraints</h2>
              </div>
              <p className="text-[#78716C] leading-relaxed font-medium">
                You may not use {process.env.NEXT_PUBLIC_BRAND_NAME || "Aizen XFX"} for any illicit activities, including but not limited to: automated harassment, token logging, or raid coordination. Violation of these constraints will result in immediate deauthorization and blacklisting from the global network.
              </p>
            </section>

            <section className="space-y-6">
              <div className="flex items-center gap-4 text-white">
                <div className="h-10 w-10 rounded-2xl bg-white/5 border border-[#EAB308]/10 flex items-center justify-center text-[#EAB308]">
                   <Cpu className="h-5 w-5" />
                </div>
                <h2 className="text-2xl font-bold font-outfit uppercase tracking-tight">API & Scaling</h2>
              </div>
              <p className="text-slate-400 leading-relaxed font-medium">
                We reserve the right to throttle or limit API access for guilds that exceed disproportionate resource allocations. High-scale enterprise clusters are available for communities requiring dedicated neural shards.
              </p>
            </section>

            <div className="pt-12 border-t border-white/5">
              <p className="text-[10px] font-black uppercase text-[#57534E] tracking-[0.4em]">
                September 2026 // Distributed via {process.env.NEXT_PUBLIC_BRAND_NAME || "Aizen XFX"} Neural Cloud
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
