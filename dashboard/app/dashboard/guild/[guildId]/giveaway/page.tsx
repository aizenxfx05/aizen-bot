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
import { Gift } from "lucide-react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";

const GiveawayForm = dynamic(() => import("@/components/dashboard/giveaway-form").then(mod => mod.GiveawayForm), {
  loading: () => <div className="h-96 w-full animate-pulse bg-white/[0.02] rounded-[30px] border border-white/5" />
});

export default async function GiveawayPage({ params }: { params: { guildId: string } }) {
  let giveawaysData: any[] = [];
  let channelsData: any[] = [];

  try {
    const [gRes, cRes] = await Promise.all([
      api.getGiveaways(params.guildId),
      api.getChannels(params.guildId)
    ]);
    giveawaysData = gRes || [];
    channelsData = cRes || [];
  } catch {
    giveawaysData = [];
    channelsData = [];
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500 pb-20">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-black text-white flex items-center gap-3 tracking-tight font-outfit uppercase">
            <Gift className="h-7 w-7 text-[#A855F7]" />
            Giveaways &amp; Rewards
          </h2>
          <p className="text-[#948BA3] mt-1 font-medium text-sm">
            Monitor and manage active server giveaways, winner counts, and schedules.
          </p>
        </div>
      </div>

      <GiveawayForm 
        initialGiveaways={giveawaysData} 
        channels={channelsData}
        guildId={params.guildId} 
      />
    </div>
  );
}
