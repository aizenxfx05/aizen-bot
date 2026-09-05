/**
 * ╔══════════════════════════════════════════════════════════════════╗
 * ║                                                                  ║
 * ║         Aizen XFX — Premium Discord Bot Dashboard               ║
 * ║         Landing Page  •  Dark Obsidian + Royal Gold Theme       ║
 * ║                                                                  ║
 * ╚══════════════════════════════════════════════════════════════════╝
 */

"use client";

import React from "react";
import Link from "next/link";
import { signIn } from "next-auth/react";
import {
  ShieldCheck,
  Zap,
  BarChart4,
  MessageSquare,
  ChevronRight,
  LayoutDashboard,
  LogIn,
  Layers,
  Sparkles,
  Bot,
  Activity,
  History,
  CheckCircle2,
  ShieldAlert,
  Globe,
  Terminal,
  Cpu,
  Users2,
  Lock,
  Radio,
  Gamepad2,
  Music4,
  User,
  Brain,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const BRAND = process.env.NEXT_PUBLIC_BRAND_NAME || "Aizen XFX";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#07070D] text-[#F3E8FF] selection:bg-[#A855F7]/30 font-sans overflow-x-hidden">

      {/* ── Dynamic Gold Background ──────────────────────────── */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[70%] h-[70%] bg-[#A855F7]/[0.03] blur-[180px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-[#7C3AED]/[0.025] blur-[150px] rounded-full animate-pulse [animation-delay:2.5s]" />
        <div className="absolute top-[40%] left-[40%] w-[40%] h-[40%] bg-[#A855F7]/[0.015] blur-[120px] rounded-full animate-pulse [animation-delay:5s]" />
      </div>

      {/* ── Navigation ───────────────────────────────────────── */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/[0.03] bg-[#07070D]/80 backdrop-blur-3xl transition-all duration-500">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-4 group cursor-pointer">
            <div className="h-11 w-11 rounded-2xl bg-gradient-to-br from-[#A855F7] to-[#7C3AED] flex items-center justify-center shadow-lg shadow-[#A855F7]/20 border border-white/10 group-hover:scale-110 group-hover:rotate-6 transition-all duration-500 overflow-hidden relative">
              <img 
                src="/logo.png" 
                alt="Logo" 
                className="h-full w-full object-cover relative z-10" 
                onError={(e) => {
                  e.currentTarget.style.display = "none";
                }} 
              />
              <Bot className="h-6 w-6 text-white absolute z-0" />
            </div>
            <div className="flex flex-col">
              <h1 className="text-lg font-bold tracking-tight text-white font-outfit leading-none">{BRAND}</h1>
              <span className="text-[9px] font-black uppercase tracking-[0.25em] text-[#A855F7]/80 mt-1">Dashboard</span>
            </div>
          </div>

          <div className="hidden lg:flex items-center gap-10 text-[11px] font-black uppercase tracking-widest text-[#948BA3]">
            <Link href="#features" className="hover:text-[#A855F7] transition-colors">Features</Link>
            <Link href="#architecture" className="hover:text-[#A855F7] transition-colors">Architecture</Link>
            <Link href="#modules" className="hover:text-[#A855F7] transition-colors">Modules</Link>
            <Link href="#network" className="hover:text-[#A855F7] transition-colors">Network</Link>
          </div>

          <Button
            onClick={() => signIn("discord", { callbackUrl: "/dashboard" })}
            className="rounded-xl px-7 h-11 font-black uppercase tracking-widest text-[10px] gap-2.5 shadow-2xl shadow-[#A855F7]/20 hover:scale-[1.05] active:scale-95 transition-all bg-gradient-to-r from-[#A855F7] to-[#6D28D9] text-[#07070D] border-none"
          >
            <LogIn className="h-3.5 w-3.5" />
            Initialize Console
          </Button>
        </div>
      </nav>

      {/* ── Hero Section ─────────────────────────────────────── */}
      <header className="relative z-10 pt-56 pb-32 px-6">
        <div className="max-w-7xl mx-auto text-center">

          {/* Status Badge */}
          <div className="inline-flex items-center gap-3 px-6 py-2.5 rounded-2xl bg-[#A855F7]/[0.04] border border-[#A855F7]/15 text-[#A855F7] text-[10px] font-black uppercase tracking-[0.3em] mb-16 animate-in fade-in slide-in-from-bottom-8 duration-1000 backdrop-blur-md">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#A855F7] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#A855F7]"></span>
            </span>
            Aizen Core v2 Active • All Systems Operational
          </div>

          <h1 className="text-6xl sm:text-8xl md:text-[10rem] font-bold text-white tracking-tighter leading-[0.8] mb-12 font-outfit animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-100 uppercase">
            Power &amp; <br />
            <span className="purple-shimmer italic font-black">Dominance.</span>
          </h1>

          <p className="text-lg md:text-2xl text-[#948BA3] max-w-3xl mx-auto leading-relaxed mb-20 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200 font-medium">
            {BRAND} — The hyper-performance Discord security engine.
            AI-powered chat, bulletproof antinuke, and precision tools for elite communities.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300">
            <Button
              onClick={() => signIn("discord", { callbackUrl: "/dashboard" })}
              className="w-full sm:w-auto rounded-2xl px-14 py-9 text-lg font-black uppercase gap-4 group shadow-[0_0_50px_rgba(168,85,247,0.2)] bg-gradient-to-r from-[#A855F7] to-[#6D28D9] text-[#07070D] border-none transition-all hover:scale-105 hover:shadow-[0_0_70px_rgba(168,85,247,0.3)]"
            >
              <LayoutDashboard className="h-6 w-6 group-hover:rotate-12 transition-transform" />
              Open Dashboard
            </Button>
            <Button
              variant="outline"
              className="w-full sm:w-auto rounded-2xl px-14 py-9 text-lg font-bold border-white/5 bg-white/[0.02] backdrop-blur-3xl hover:bg-[#A855F7]/[0.05] hover:border-[#A855F7]/20 gap-3 text-[#F3E8FF] transition-all"
            >
              Add to Server
              <ChevronRight className="h-5 w-5 opacity-40" />
            </Button>
          </div>
        </div>

        {/* Dashboard Mockup */}
        <div className="max-w-6xl mx-auto mt-40 relative group animate-in fade-in zoom-in-95 duration-1000 delay-500">
          <div className="absolute -inset-4 bg-gradient-to-r from-[#A855F7]/15 to-transparent rounded-[60px] blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
          <div className="relative bg-[#0D0B18] border border-[#A855F7]/10 rounded-[50px] overflow-hidden shadow-[0_30px_100px_rgba(0,0,0,0.8)]">
            <div className="h-16 border-b border-white/[0.03] flex items-center justify-between px-10 bg-white/[0.01]">
              <div className="flex items-center gap-3">
                <div className="h-3 w-3 rounded-full bg-[#A855F7]/40" />
                <div className="h-3 w-3 rounded-full bg-white/10" />
                <div className="h-3 w-3 rounded-full bg-white/5" />
              </div>
              <div className="px-6 py-2 rounded-2xl bg-[#A855F7]/[0.04] border border-[#A855F7]/10 text-[10px] font-black text-[#948BA3] tracking-[0.2em] uppercase">
                aizen.core // guardian_node_01
              </div>
              <div className="w-12" />
            </div>
            <div className="aspect-[16/10] p-16 flex flex-col gap-16 relative overflow-hidden bg-gradient-to-br from-[#0D0B18] to-[#111420]">
              <div className="flex items-center justify-between z-10 relative">
                <div className="space-y-6">
                  <div className="h-12 w-64 bg-[#A855F7]/[0.08] rounded-[20px] border border-[#A855F7]/15" />
                  <div className="h-6 w-[500px] bg-white/[0.02] rounded-xl" />
                </div>
                <div className="h-20 w-20 rounded-[30px] bg-[#A855F7]/[0.08] border border-[#A855F7]/20 flex items-center justify-center shadow-[0_0_30px_rgba(168,85,247,0.15)]">
                  <Activity className="h-8 w-8 text-[#A855F7] animate-pulse" />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-10 z-10">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-40 bg-white/[0.02] border border-[#A855F7]/[0.06] rounded-[40px] p-8 space-y-6 hover:border-[#A855F7]/20 transition-colors">
                    <div className="h-10 w-10 rounded-2xl bg-[#A855F7]/[0.08] border border-[#A855F7]/15" />
                    <div className="h-4 w-2/3 bg-white/5 rounded-lg" />
                    <div className="h-3 w-1/2 bg-white/[0.02] rounded-lg" />
                  </div>
                ))}
              </div>
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90%] h-[90%] bg-[#A855F7]/[0.015] blur-[150px] pointer-events-none" />
            </div>
          </div>
        </div>
      </header>

      {/* ── Features Section ─────────────────────────────────── */}
      <section id="features" className="py-48 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-32 gap-12 px-4">
            <div className="max-w-3xl">
              <h2 className="text-6xl md:text-8xl font-bold text-white tracking-tighter font-outfit mb-8 uppercase italic leading-none">
                Elite-Scale <br /><span className="text-purple-gradient not-italic">Infrastructure.</span>
              </h2>
              <p className="text-2xl text-[#948BA3] font-medium leading-relaxed">
                Military-grade security meets AI intelligence. Sub-millisecond dispatch across global edge nodes.
              </p>
            </div>
            <div className="flex items-center gap-10 pb-4">
              <div className="text-right">
                <p className="text-[10px] font-black uppercase text-[#948BA3] tracking-[0.3em] mb-3">Ping Latency</p>
                <p className="text-5xl font-black text-[#A855F7] font-outfit">12ms</p>
              </div>
              <div className="h-16 w-[1px] bg-white/5" />
              <div className="text-right">
                <p className="text-[10px] font-black uppercase text-[#948BA3] tracking-[0.3em] mb-3">Global Uptime</p>
                <p className="text-5xl font-black text-white font-outfit">99.9<span className="text-[#3A3020]">9</span>%</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { title: "Neuro-Security", desc: "Contextual AI analysis detects raids and token-logging attempts in real-time.", icon: ShieldCheck, color: "bg-[#A855F7]/10 border-[#A855F7]/20 text-[#A855F7]" },
              { title: "AI Voice Chat", desc: "Replies intelligently in voice-linked text channels using Groq-powered LLaMA AI.", icon: Brain, color: "bg-amber-500/10 border-amber-500/20 text-amber-400" },
              { title: "Channel Guardian", desc: "Automatically restores deleted channels instantly — independent of antinuke.", icon: RefreshCw, color: "bg-yellow-600/10 border-yellow-600/20 text-yellow-500" },
              { title: "Threaded Support", desc: "High-volume ticket systems with enterprise encryption and lifetime transcripts.", icon: MessageSquare, color: "bg-white/10 border-white/20 text-slate-400" },
              { title: "Real-time Flux", desc: "Watch server events live with zero-latency WebSocket data streaming.", icon: Activity, color: "bg-[#A855F7]/5 border-[#A855F7]/10 text-[#A855F7]/70" },
              { title: "Cloud Integrity", desc: "Encrypted backups of all server configurations stored in off-site neural vaults.", icon: Layers, color: "bg-amber-900/10 border-amber-900/20 text-amber-700" },
            ].map((feature, i) => (
              <div key={i} className="group glass border-white/5 p-12 rounded-[50px] hover:border-[#A855F7]/25 transition-all duration-700 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-12 opacity-0 group-hover:opacity-5 scale-50 group-hover:scale-110 transition-all duration-1000">
                  <feature.icon className="h-64 w-64 text-[#A855F7]" />
                </div>
                <div className={cn("h-20 w-20 rounded-3xl flex items-center justify-center mb-10 border transition-all duration-700 group-hover:scale-110 group-hover:rotate-6 shadow-2xl shadow-black/40", feature.color)}>
                  <feature.icon className="h-10 w-10 shadow-lg" />
                </div>
                <h3 className="text-3xl font-bold text-white mb-6 tracking-tight font-outfit relative z-10">{feature.title}</h3>
                <p className="text-[#948BA3] leading-relaxed font-bold relative z-10 group-hover:text-[#A09060] transition-colors uppercase text-[10px] tracking-[0.2em]">{feature.desc}</p>
                <div className="mt-8 h-[2px] w-0 bg-gradient-to-r from-[#A855F7] to-[#6D28D9] group-hover:w-full transition-all duration-700" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Architecture Section ──────────────────────────────── */}
      <section id="architecture" className="py-48 px-6 bg-white/[0.008]">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-24 items-center">
          <div className="space-y-12">
            <div className="inline-flex px-4 py-1.5 rounded-full bg-[#A855F7]/10 border border-[#A855F7]/20 text-[#A855F7] text-[10px] font-black uppercase tracking-[0.3em]">
              The Stack
            </div>
            <h2 className="text-6xl md:text-7xl font-bold text-white tracking-tighter font-outfit uppercase">
              Aizen Core <br /><span className="text-[#3A3020] italic">Technology.</span>
            </h2>
            <p className="text-xl text-[#948BA3] leading-relaxed font-medium">
              Proprietary async architecture handling millions of events with sub-millisecond response times. Zero lag, zero compromise.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 pt-8">
              {[
                { icon: Terminal, title: "Custom Engine", desc: "Aizen XFX scripting for advanced server automation logic." },
                { icon: Cpu, title: "FPGA Ready", desc: "Hardware-accelerated pattern matching for instant threat detection." },
                { icon: Lock, title: "Zero Trust", desc: "Every command is sandboxed and cryptographically verified." },
                { icon: Radio, title: "Low Entropy", desc: "Optimized for minimal CPU jitter and maximum reliability." },
              ].map((item, i) => (
                <div key={i} className="space-y-4 p-6 rounded-[30px] border border-[#A855F7]/[0.06] hover:bg-[#A855F7]/[0.02] hover:border-[#A855F7]/15 transition-colors">
                  <item.icon className="h-6 w-6 text-[#A855F7]" />
                  <h4 className="text-lg font-bold text-white font-outfit uppercase tracking-tight">{item.title}</h4>
                  <p className="text-sm text-[#3A3020] font-bold leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="relative aspect-square flex items-center justify-center group">
            <div className="absolute inset-0 bg-[#A855F7]/5 blur-[120px] rounded-full animate-pulse" />
            <div className="h-[80%] w-[80%] border-2 border-[#A855F7]/[0.08] rounded-full animate-[spin_60s_linear_infinite] flex items-center justify-center relative">
              <div className="absolute top-0 left-1/2 -translate-x-1/2 h-4 w-4 rounded-full bg-[#A855F7] shadow-[0_0_20px_rgba(168,85,247,0.6)] animate-purple-pulse" />
              <div className="h-[70%] w-[70%] border border-[#A855F7]/[0.06] rounded-full animate-[spin_40s_linear_infinite_reverse] flex items-center justify-center">
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 h-3 w-3 rounded-full bg-white/20 shadow-[0_0_20px_rgba(255,255,255,0.2)]" />
                <div className="h-[60%] w-[60%] border border-[#A855F7]/[0.04] rounded-full animate-[spin_20s_linear_infinite] flex items-center justify-center">
                  <Bot className="h-20 w-20 text-[#A855F7]/30 group-hover:text-[#A855F7] transition-all duration-700 group-hover:scale-125" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Modules Grid ─────────────────────────────────────── */}
      <section id="modules" className="py-48 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-32 space-y-6">
            <h2 className="text-6xl md:text-8xl font-bold text-white tracking-tighter font-outfit uppercase">
              The Arsenal <br /><span className="purple-shimmer italic">Complete.</span>
            </h2>
            <p className="text-2xl text-[#948BA3] max-w-3xl mx-auto font-medium lowercase">Every module you need. Redefined for the modern era.</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {[
              { name: "Anti-Nuke", desc: "Absolute server lockdown.", icon: ShieldAlert },
              { name: "Verification", desc: "Bot-free onboarding.", icon: CheckCircle2 },
              { name: "Welcome", desc: "Cinematic entries.", icon: Sparkles },
              { name: "Vanity Roles", desc: "Custom server identity.", icon: Gamepad2 },
              { name: "Auto Role", desc: "Instant rank assignment.", icon: User },
              { name: "Join to Create", desc: "Self-service voice channels.", icon: Music4 },
              { name: "Tracking", desc: "Predictive user metrics.", icon: Activity },
              { name: "Invites", desc: "Advanced growth tracking.", icon: Globe },
              { name: "Custom Roles", desc: "User-defined permissions.", icon: Lock },
              { name: "Reaction Roles", desc: "Interactive role menus.", icon: Layers },
              { name: "Tickets", desc: "Support at lightspeed.", icon: MessageSquare },
              { name: "VC AI Chat", desc: "AI replies in voice text.", icon: Brain },
            ].map((mod, i) => (
              <div key={i} className="group p-8 rounded-[40px] bg-white/[0.01] border border-white/[0.03] hover:bg-[#A855F7]/[0.02] hover:border-[#A855F7]/15 transition-all duration-500">
                <div className="h-14 w-14 rounded-2xl bg-white/[0.03] flex items-center justify-center mb-6 group-hover:bg-[#A855F7]/10 transition-colors">
                  <mod.icon className="h-6 w-6 text-[#948BA3] group-hover:text-[#A855F7] transition-colors" />
                </div>
                <h4 className="text-xl font-bold text-white font-outfit mb-2 tracking-tight">{mod.name}</h4>
                <p className="text-xs text-[#3A3020] font-bold uppercase tracking-widest">{mod.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Network Section ───────────────────────────────────── */}
      <section id="network" className="py-48 px-6 bg-[#A855F7]/[0.008] relative overflow-hidden">
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="flex flex-col lg:flex-row items-center gap-24">
            <div className="flex-1 space-y-12">
              <h2 className="text-6xl md:text-8xl font-bold text-white tracking-tighter font-outfit uppercase">
                Global <br /><span className="text-[#A855F7]">Reach.</span>
              </h2>
              <p className="text-2xl text-[#948BA3] leading-relaxed font-medium">
                Powering servers with millions of combined users. Our network spans every continent, bringing your community elite-level protection.
              </p>
              <div className="space-y-8">
                {[
                  { stat: "12M+", label: "Users Protected" },
                  { stat: "24", label: "Edge Clusters" },
                  { stat: "5.2K", label: "Verified Communities" },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-8">
                    <div className="text-5xl font-black text-white font-outfit">{item.stat}</div>
                    <div className="h-[1px] flex-1 bg-[#A855F7]/10" />
                    <div className="text-[11px] font-black uppercase text-[#A855F7] tracking-[0.3em]">{item.label}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="flex-1 relative group">
              <div className="absolute inset-0 bg-[#A855F7]/10 blur-[150px] opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
              <div className="aspect-square bg-[#0D0B18] border border-[#A855F7]/10 rounded-[60px] p-12 relative overflow-hidden flex items-center justify-center">
                <Globe className="h-64 w-64 text-[#A855F7]/10 animate-pulse" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-32 w-32 bg-[#A855F7]/15 blur-[60px] rounded-full" />
                </div>
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                  <Bot className="h-20 w-20 text-[#A855F7] shadow-[0_0_50px_rgba(168,85,247,0.4)] bg-[#0D0B18] rounded-3xl p-4 border border-[#A855F7]/30" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── FAQ Section ────────────────────────────────────────── */}
      <section className="py-48 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-24">
            <h2 className="text-5xl md:text-6xl font-black text-white font-outfit tracking-tighter uppercase mb-6">Knowledge Base</h2>
            <p className="text-[#948BA3] font-bold uppercase tracking-widest text-xs">Frequently Asked Questions</p>
          </div>
          <div className="space-y-6">
            {[
              { q: `Is ${BRAND} free to use?`, a: "The core engine is 100% free for all communities. Premium clusters are available for ultra-high-scale enterprise servers." },
              { q: "How does the AI Voice Chat work?", a: "The bot detects messages in voice-linked text channels and replies intelligently using the Groq LLaMA AI. It maintains per-channel conversation history for context-aware replies." },
              { q: "What is Channel Restore?", a: "An independent protection layer that automatically recreates deleted voice or text channels within seconds — even when antinuke is disabled." },
              { q: "How secure is my server data?", a: "Every byte of configuration data is secured. API keys use constant-time comparison to prevent timing attacks. We never store personal user data beyond Discord's standard requirements." },
            ].map((item, i) => (
              <div key={i} className="p-10 rounded-[40px] border border-white/[0.03] hover:border-[#A855F7]/15 transition-all bg-white/[0.01] group">
                <h4 className="text-xl font-bold text-white mb-6 font-outfit uppercase tracking-tight flex items-center gap-4">
                  <div className="h-2 w-2 rounded-full bg-[#A855F7] opacity-20 group-hover:opacity-100 transition-all animate-purple-pulse" />
                  {item.q}
                </h4>
                <p className="text-[#948BA3] font-bold leading-relaxed">{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Section ────────────────────────────────────────── */}
      <section className="py-48 px-6">
        <div className="max-w-6xl mx-auto relative rounded-[80px] p-24 md:p-32 overflow-hidden text-center shadow-[0_40px_100px_rgba(0,0,0,0.7)]"
          style={{ background: "linear-gradient(135deg, #1A1500 0%, #2A1F00 40%, #1A1200 100%)", border: "1px solid rgba(168,85,247,0.2)" }}>
          <div className="absolute inset-0 opacity-10"
            style={{ background: "radial-gradient(ellipse at 50% 0%, rgba(168,85,247,0.4) 0%, transparent 70%)" }} />
          <div className="relative z-10">
            <h2 className="text-7xl md:text-[9rem] font-bold text-white tracking-tighter font-outfit mb-12 uppercase leading-[0.8] italic">
              Ready to <br />Ascend?
            </h2>
            <p className="text-2xl text-[#F3E8FF]/60 max-w-3xl mx-auto mb-20 font-medium">
              Join 5,000+ elite communities powered by {BRAND}. Setup takes less than 30 seconds.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-8 tracking-widest uppercase text-xs font-black">
              <Button
                onClick={() => signIn("discord", { callbackUrl: "/dashboard" })}
                className="w-full sm:w-auto rounded-3xl px-16 py-10 bg-gradient-to-r from-[#A855F7] to-[#6D28D9] text-[#07070D] hover:from-[#C084FC] hover:to-[#A855F7] border-none shadow-[0_20px_50px_rgba(168,85,247,0.3)] font-black text-lg transition-all hover:scale-105 active:scale-95"
              >
                Get Started Free
              </Button>
              <div className="flex items-center gap-3 text-[#A855F7]">
                <div className="h-3 w-3 rounded-full bg-[#A855F7] animate-pulse shadow-[0_0_10px_rgba(168,85,247,0.5)]" />
                Aizen Core: Active
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────────── */}
      <footer className="py-32 border-t border-[#A855F7]/[0.06] bg-[#07070D] relative z-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-20 mb-32">
            <div className="col-span-1 md:col-span-2 space-y-12">
              <div className="flex items-center gap-4 group">
                <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-[#A855F7] to-[#6D28D9] flex items-center justify-center border border-white/10">
                  <Bot className="h-5 w-5 text-[#07070D]" />
                </div>
                <span className="text-2xl font-bold text-white font-outfit uppercase tracking-tighter">{BRAND}</span>
              </div>
              <p className="text-[#3A3020] max-w-sm font-bold leading-relaxed uppercase text-xs tracking-widest">
                The high-performance Discord security engine for communities that demand excellence. Secure, intelligent, and infinitely scalable.
              </p>
            </div>
            <div className="space-y-8">
              <h4 className="text-[10px] font-black uppercase tracking-[0.4em] text-white opacity-40">System</h4>
              <ul className="space-y-5 text-[11px] font-black uppercase tracking-widest text-[#3A3020]">
                <li><Link href="#" className="hover:text-[#A855F7] transition-colors">GitHub Repository</Link></li>
                <li><Link href="/docs" className="hover:text-[#A855F7] transition-colors">Documentation</Link></li>
                <li><Link href="#" className="hover:text-[#A855F7] transition-colors">API References</Link></li>
              </ul>
            </div>
            <div className="space-y-8">
              <h4 className="text-[10px] font-black uppercase tracking-[0.4em] text-white opacity-40">Identity</h4>
              <ul className="space-y-5 text-[11px] font-black uppercase tracking-widest text-[#3A3020]">
                <li><Link href="/privacy" className="hover:text-[#A855F7] transition-colors">Privacy Shield</Link></li>
                <li><Link href="/terms" className="hover:text-[#A855F7] transition-colors">Terms of Service</Link></li>
                <li><Link href="https://discord.gg/M8qJ9W7vBb" target="_blank" rel="noopener noreferrer" className="hover:text-[#A855F7] transition-colors">Discord Server</Link></li>
              </ul>
            </div>
          </div>
          <div className="pt-12 border-t border-[#A855F7]/[0.06] flex flex-col md:flex-row items-center justify-between gap-6 opacity-40">
            <p className="text-[#3A3020] text-[10px] font-black uppercase tracking-[0.4em]">
              © 2026 {BRAND} — All Rights Reserved
            </p>
            <div className="flex items-center gap-3 text-[10px] font-black text-[#A855F7] uppercase tracking-[0.3em]">
              <div className="h-2 w-2 rounded-full bg-[#A855F7] animate-pulse" />
              All Nodes Operational
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
