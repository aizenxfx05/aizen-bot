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
  Music4, 
  Radio, 
  Volume2, 
  Server, 
  Save, 
  RefreshCw, 
  CheckCircle2, 
  Sparkles, 
  Headphones, 
  Activity,
  Sliders,
  Disc3
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { MusicConfig, DiscordChannel } from "@/types/api";

interface MusicFormProps {
  initialConfig: MusicConfig;
  channels: DiscordChannel[];
  guildId: string;
}

export function MusicForm({ initialConfig, channels, guildId }: MusicFormProps) {
  const [config, setConfig] = useState<MusicConfig>(initialConfig);
  const [saving, setSaving] = useState(false);

  // Filter voice and text channels
  const voiceChannels = channels.filter(c => c.type === "2" || c.type === "voice" || (c as any).is_voice);
  const textChannels = channels.filter(c => c.type === "0" || c.type === "text" || !(c as any).is_voice);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.updateMusic(guildId, config);
      toast.success("Music system settings saved successfully!");
    } catch (err: any) {
      console.error(err);
      toast.error("Failed to update music configuration");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Lavalink Node Status Banner */}
      <div className="p-6 rounded-3xl bg-[#0D0B18]/90 border border-[#A855F7]/15 backdrop-blur-2xl shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-[#A855F7]/[0.03] blur-[80px] rounded-full pointer-events-none" />

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="h-14 w-14 rounded-2xl bg-[#A855F7]/10 border border-[#A855F7]/20 flex items-center justify-center text-[#A855F7] shadow-lg shadow-[#A855F7]/10">
              <Disc3 className="h-7 w-7 animate-[spin_8s_linear_infinite]" />
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h3 className="text-lg font-bold text-white tracking-tight">
                  {config.node_name || "Aizen Lavalink Audio Node"}
                </h3>
                <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Operational
                </span>
              </div>
              <p className="text-xs text-[#948BA3] mt-0.5">
                Ultra-low latency audio processing powered by Wavelink &amp; Lavalink cluster.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div className="px-4 py-2 rounded-xl bg-white/[0.02] border border-white/5 text-center">
              <p className="text-[10px] uppercase font-bold text-[#948BA3] tracking-wider">Bitrate</p>
              <p className="text-sm font-black text-white font-outfit">384 kbps</p>
            </div>
            <div className="px-4 py-2 rounded-xl bg-white/[0.02] border border-white/5 text-center">
              <p className="text-[10px] uppercase font-bold text-[#948BA3] tracking-wider">Latency</p>
              <p className="text-sm font-black text-[#A855F7] font-outfit">~12ms</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Configuration Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* 24/7 Mode Card */}
        <div className="p-8 rounded-3xl bg-[#0D0B18]/90 border border-white/5 backdrop-blur-2xl shadow-xl flex flex-col justify-between space-y-6">
          <div className="space-y-6">
            <div className="flex items-center justify-between pb-6 border-b border-white/5">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-2xl bg-[#A855F7]/10 border border-[#A855F7]/20 text-[#A855F7]">
                  <Radio className="h-6 w-6" />
                </div>
                <div>
                  <h4 className="text-lg font-bold text-white">24/7 Voice Presence</h4>
                  <p className="text-xs text-[#948BA3]">Keep the bot permanently stationed in your voice channel.</p>
                </div>
              </div>
              <Switch
                checked={config.is_247}
                onCheckedChange={(checked) => setConfig({ ...config, is_247: checked })}
                className="data-[state=checked]:bg-[#A855F7]"
              />
            </div>

            <div className={cn("space-y-4 transition-all duration-300", !config.is_247 && "opacity-40 pointer-events-none")}>
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <Headphones className="h-3.5 w-3.5 text-[#A855F7]" />
                  Designated Voice Channel
                </label>
                <Select
                  value={config.channel_id || "none"}
                  onValueChange={(val) => setConfig({ ...config, channel_id: val === "none" ? null : val })}
                >
                  <SelectTrigger className="w-full h-12 bg-white/[0.02] border-white/5 rounded-xl font-medium text-white focus:ring-1 focus:ring-[#A855F7]/30">
                    <SelectValue placeholder="Select a voice channel..." />
                  </SelectTrigger>
                  <SelectContent className="bg-[#0D0B18] border-white/10 text-white">
                    <SelectItem value="none" className="text-slate-400">Automatic / Any Channel</SelectItem>
                    {voiceChannels.map((c) => (
                      <SelectItem key={c.id} value={c.id.toString()}>
                        🔊 {c.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <Volume2 className="h-3.5 w-3.5 text-[#A855F7]" />
                  Track Dispatch / Notice Channel
                </label>
                <Select
                  value={config.text_channel_id || "none"}
                  onValueChange={(val) => setConfig({ ...config, text_channel_id: val === "none" ? null : val })}
                >
                  <SelectTrigger className="w-full h-12 bg-white/[0.02] border-white/5 rounded-xl font-medium text-white focus:ring-1 focus:ring-[#A855F7]/30">
                    <SelectValue placeholder="Select a text channel..." />
                  </SelectTrigger>
                  <SelectContent className="bg-[#0D0B18] border-white/10 text-white">
                    <SelectItem value="none" className="text-slate-400">Current / Active Channel</SelectItem>
                    {textChannels.map((c) => (
                      <SelectItem key={c.id} value={c.id.toString()}>
                        # {c.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <Button
            onClick={handleSave}
            disabled={saving}
            className="w-full bg-[#A855F7] hover:bg-[#C084FC] text-black font-black uppercase tracking-wider rounded-xl py-6 shadow-lg shadow-[#A855F7]/20 gap-2 transition-all hover:scale-[1.01]"
          >
            {saving ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Save Music Settings
          </Button>
        </div>

        {/* Audio Engine & Supported Sources Card */}
        <div className="p-8 rounded-3xl bg-[#0D0B18]/90 border border-white/5 backdrop-blur-2xl shadow-xl flex flex-col justify-between space-y-6">
          <div className="space-y-6">
            <div className="flex items-center gap-3 pb-6 border-b border-white/5">
              <div className="p-3 rounded-2xl bg-[#A855F7]/10 border border-[#A855F7]/20 text-[#A855F7]">
                <Music4 className="h-6 w-6" />
              </div>
              <div>
                <h4 className="text-lg font-bold text-white">Multi-Source Audio Engine</h4>
                <p className="text-xs text-[#948BA3]">Stream seamlessly from your preferred platform.</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {[
                { name: "YouTube Music", badge: "Direct Search", icon: "▶️", color: "text-red-400" },
                { name: "Spotify", badge: "Tracks & Playlists", icon: "🟢", color: "text-emerald-400" },
                { name: "SoundCloud", badge: "Hi-Res Streams", icon: "🟠", color: "text-amber-400" },
                { name: "JioSaavn", badge: "Lossless Audio", icon: "🎵", color: "text-blue-400" },
              ].map((platform) => (
                <div key={platform.name} className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-base">{platform.icon}</span>
                    <span className="text-[9px] font-black uppercase tracking-wider text-[#948BA3]">Supported</span>
                  </div>
                  <p className="text-xs font-bold text-white">{platform.name}</p>
                  <p className="text-[10px] text-[#948BA3]">{platform.badge}</p>
                </div>
              ))}
            </div>

            <div className="p-4 rounded-2xl bg-white/[0.01] border border-white/5 space-y-2">
              <p className="text-xs font-bold text-white flex items-center gap-2">
                <Sparkles className="h-3.5 w-3.5 text-[#A855F7]" />
                Interactive Equalizer &amp; Filters
              </p>
              <p className="text-[11px] text-[#948BA3] leading-relaxed">
                Bassboost, 8D audio, Nightcore, Vaporwave, and Karaoke filters can be dynamically toggled in voice chat using bot commands.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
