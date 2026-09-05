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
import { 
  Gift, 
  Trash2, 
  Clock, 
  Trophy, 
  Hash, 
  Sparkles, 
  Terminal, 
  RefreshCw,
  AlertCircle
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { GiveawayItem, DiscordChannel } from "@/types/api";

interface GiveawayFormProps {
  initialGiveaways: GiveawayItem[];
  channels: DiscordChannel[];
  guildId: string;
}

export function GiveawayForm({ initialGiveaways, channels, guildId }: GiveawayFormProps) {
  const [giveaways, setGiveaways] = useState<GiveawayItem[]>(initialGiveaways);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const getChannelName = (channelId: string) => {
    const ch = channels.find(c => c.id.toString() === channelId);
    return ch ? `#${ch.name}` : `Channel ${channelId}`;
  };

  const formatTimestamp = (timestamp: number) => {
    if (!timestamp) return "Soon";
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  };

  const handleDelete = async (messageId: string) => {
    setDeletingId(messageId);
    try {
      await api.deleteGiveaway(guildId, messageId);
      toast.success("Giveaway ended and removed");
      setGiveaways(prev => prev.filter(g => g.message_id !== messageId));
    } catch (err: any) {
      console.error(err);
      toast.error("Failed to delete giveaway");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-6 rounded-3xl bg-[#0C0B0F]/90 border border-white/5 backdrop-blur-2xl shadow-xl flex items-center gap-4">
          <div className="p-3 rounded-2xl bg-[#EAB308]/10 border border-[#EAB308]/20 text-[#EAB308]">
            <Gift className="h-6 w-6" />
          </div>
          <div>
            <p className="text-[10px] font-black uppercase tracking-wider text-[#78716C]">Active Giveaways</p>
            <p className="text-2xl font-black text-white font-outfit">{giveaways.length}</p>
          </div>
        </div>

        <div className="p-6 rounded-3xl bg-[#0C0B0F]/90 border border-white/5 backdrop-blur-2xl shadow-xl flex items-center gap-4">
          <div className="p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <Trophy className="h-6 w-6" />
          </div>
          <div>
            <p className="text-[10px] font-black uppercase tracking-wider text-[#78716C]">Total Winners</p>
            <p className="text-2xl font-black text-white font-outfit">
              {giveaways.reduce((acc, g) => acc + (g.winners || 1), 0)}
            </p>
          </div>
        </div>

        <div className="p-6 rounded-3xl bg-[#0C0B0F]/90 border border-white/5 backdrop-blur-2xl shadow-xl flex items-center gap-4">
          <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
            <Sparkles className="h-6 w-6" />
          </div>
          <div>
            <p className="text-[10px] font-black uppercase tracking-wider text-[#78716C]">Verification Engine</p>
            <p className="text-sm font-bold text-white">Bot-Protected</p>
          </div>
        </div>
      </div>

      {/* Giveaways List */}
      <div className="p-8 rounded-3xl bg-[#0C0B0F]/90 border border-white/5 backdrop-blur-2xl shadow-2xl relative overflow-hidden space-y-6">
        <div className="flex items-center justify-between pb-6 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-[#EAB308]/10 text-[#EAB308]">
              <Gift className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Live Giveaways</h3>
              <p className="text-xs text-[#78716C]">Manage ongoing community prize draws.</p>
            </div>
          </div>
        </div>

        {giveaways.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {giveaways.map((g) => (
              <div 
                key={g.message_id}
                className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-[#EAB308]/20 transition-all space-y-4 group"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h4 className="text-base font-bold text-white tracking-tight">{g.prize}</h4>
                    <p className="text-xs text-[#EAB308] mt-0.5 flex items-center gap-1.5">
                      <Hash className="h-3.5 w-3.5" />
                      {getChannelName(g.channel_id)}
                    </p>
                  </div>
                  <Button
                    onClick={() => handleDelete(g.message_id)}
                    disabled={deletingId === g.message_id}
                    variant="outline"
                    className="border-white/5 bg-white/[0.02] hover:bg-red-500/10 hover:border-red-500/30 text-slate-400 hover:text-red-400 rounded-xl p-2.5 h-auto transition-all"
                  >
                    {deletingId === g.message_id ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                  </Button>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-2 border-t border-white/5 text-xs">
                  <div>
                    <span className="text-[10px] uppercase font-bold text-[#78716C] tracking-wider block">Winners</span>
                    <span className="font-bold text-white">{g.winners} {g.winners === 1 ? 'member' : 'members'}</span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-[#78716C] tracking-wider block">Ends At</span>
                    <span className="font-bold text-slate-300">{formatTimestamp(g.ends_at)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-16 flex flex-col items-center justify-center text-center space-y-3">
            <div className="h-12 w-12 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center justify-center text-slate-600">
              <Gift className="h-6 w-6" />
            </div>
            <p className="text-sm font-bold text-slate-300">No active giveaways</p>
            <p className="text-xs text-[#78716C] max-w-sm">
              Use Discord commands to host a giveaway. They will automatically appear and synchronize here in real-time.
            </p>
          </div>
        )}
      </div>

      {/* Command Guide */}
      <div className="p-8 rounded-3xl bg-[#0C0B0F]/90 border border-white/5 backdrop-blur-2xl shadow-xl space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-[#EAB308]/10 text-[#EAB308]">
            <Terminal className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-base font-bold text-white">Giveaway Command Cheatsheet</h4>
            <p className="text-xs text-[#78716C]">Quick commands to launch or manage giveaways directly in Discord.</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 space-y-1">
            <code className="text-xs font-mono font-bold text-[#EAB308]">&gt;gstart 10m 1 Nitro</code>
            <p className="text-[11px] text-[#78716C]">Starts a 10-minute giveaway with 1 winner for Discord Nitro.</p>
          </div>
          <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 space-y-1">
            <code className="text-xs font-mono font-bold text-[#EAB308]">&gt;greroll &lt;msg_id&gt;</code>
            <p className="text-[11px] text-[#78716C]">Rerolls a new winner for an already completed giveaway.</p>
          </div>
          <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 space-y-1">
            <code className="text-xs font-mono font-bold text-[#EAB308]">&gt;gend &lt;msg_id&gt;</code>
            <p className="text-[11px] text-[#78716C]">Immediately ends an active giveaway and picks winners.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
