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

import React, { useState, useEffect } from "react";
import { AtSign, RefreshCcw } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { TagBotForm } from "@/components/dashboard/tagbot-form";
import { TagBotConfig, DiscordChannel } from "@/types/api";

export default function TagBotPage({ params }: { params: { guildId: string } }) {
  const [loading, setLoading] = useState(true);
  const [channels, setChannels] = useState<DiscordChannel[]>([]);
  const [config, setConfig] = useState<TagBotConfig>({
    guild_id: params.guildId,
    enabled: true,
    trigger_type: "single",
    response_type: "default",
    custom_message: null,
    custom_title: null,
    custom_color: "#A855F7",
    custom_image: null,
    custom_thumbnail: null,
    show_invite: true,
    show_support: true,
    show_dashboard: true,
    auto_delete: 0,
    alert_channel_id: null,
    alert_enabled: false,
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [configData, channelsData] = await Promise.all([
          api.getTagBot(params.guildId).catch((err) => {
            console.warn("Using fallback TagBot config:", err);
            return {
              guild_id: params.guildId,
              enabled: true,
              trigger_type: "single" as const,
              response_type: "default" as const,
              custom_message: null,
              custom_title: null,
              custom_color: "#A855F7",
              custom_image: null,
              custom_thumbnail: null,
              show_invite: true,
              show_support: true,
              show_dashboard: true,
              auto_delete: 0,
              alert_channel_id: null,
              alert_enabled: false,
            };
          }),
          api.getChannels(params.guildId).catch((err) => {
            console.warn("Failed to fetch channels for TagBot:", err);
            return [];
          }),
        ]);

        setConfig(configData);
        setChannels(channelsData);
      } catch (error) {
        console.error("Failed to fetch TagBot data:", error);
        toast.error("Failed to load Tag Bot configuration");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [params.guildId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[450px] space-y-4">
        <div className="h-12 w-12 rounded-2xl bg-[#A855F7]/10 border border-[#A855F7]/20 flex items-center justify-center text-[#A855F7] animate-pulse">
          <AtSign className="h-6 w-6 animate-spin" />
        </div>
        <p className="text-sm font-medium text-[#948BA3]">Loading Tag Bot &amp; Mention Alert settings...</p>
      </div>
    );
  }

  return (
    <TagBotForm
      initialConfig={config}
      channels={channels}
      guildId={params.guildId}
    />
  );
}
