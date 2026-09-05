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

import React from "react";
import { Music4 } from "lucide-react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";

const MusicForm = dynamic(() => import("@/components/dashboard/music-form").then(mod => mod.MusicForm), {
  loading: () => <div className="h-96 w-full animate-pulse bg-white/[0.02] rounded-[30px] border border-white/5" />
});

export default async function MusicPage({ params }: { params: { guildId: string } }) {
  let musicData = null;
  let channelsData: any[] = [];

  try {
    const [musicRes, channelsRes] = await Promise.all([
      api.getMusic(params.guildId),
      api.getChannels(params.guildId)
    ]);
    musicData = musicRes;
    channelsData = channelsRes || [];
  } catch {
    musicData = {
      is_247: false,
      channel_id: null,
      text_channel_id: null,
      node_connected: true,
      node_name: "Aizen Lavalink Node 01"
    };
    channelsData = [];
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500 pb-20">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-black text-white flex items-center gap-3 tracking-tight font-outfit uppercase">
            <Music4 className="h-7 w-7 text-[#EAB308]" />
            Music &amp; 24/7 Voice Node
          </h2>
          <p className="text-[#78716C] mt-1 font-medium text-sm">
            High-fidelity audio streaming, 24/7 dedicated voice connection, and node management.
          </p>
        </div>
      </div>

      <MusicForm 
        initialConfig={musicData} 
        channels={channelsData}
        guildId={params.guildId} 
      />
    </div>
  );
}
