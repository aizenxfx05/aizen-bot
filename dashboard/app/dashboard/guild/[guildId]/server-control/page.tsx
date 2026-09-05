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
import { SlidersHorizontal } from "lucide-react";
import dynamic from "next/dynamic";

const ServerControlForm = dynamic(
  () => import("@/components/dashboard/server-control-form").then((mod) => mod.ServerControlForm),
  {
    loading: () => <div className="h-96 w-full animate-pulse bg-slate-800/20 rounded-3xl" />,
  }
);

export default async function ServerControlPage({ params }: { params: { guildId: string } }) {
  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <SlidersHorizontal className="h-6 w-6 text-[#A855F7]" />
            Live Server Control
          </h2>
          <p className="text-slate-400 mt-1">
            Real-time management: emergency lockdown, announcements, bulk message purge, channel slowmode, and instant moderation.
          </p>
        </div>
      </div>

      <ServerControlForm guildId={params.guildId} />
    </div>
  );
}
