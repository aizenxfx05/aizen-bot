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
import Image from "next/image";
import Link from "next/link";
import { Users, ShieldCheck, ChevronRight, Hash, Plus, ExternalLink, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";

import { GuildSummary } from "@/types/api";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function GuildsPage() {
  const session = await getServerSession(authOptions);
  
  if (!session || !session.accessToken) {
    redirect("/");
  }

  const clientId = process.env.DISCORD_CLIENT_ID || "1545041086450507856";
  const defaultInviteUrl = `https://discord.com/oauth2/authorize?client_id=${clientId}&permissions=8&integration_type=0&scope=bot+applications.commands`;

  let botGuilds: GuildSummary[] = [];
  let userGuilds: any[] = [];
  let userDiscordError: string | null = null;
  let botError: string | null = null;

  try {
    botGuilds = await api.listGuilds();
  } catch (err: any) {
    console.error("Failed to fetch bot guilds:", err);
    botError = err.message || "Failed to load bot servers.";
  }

  try {
    const res = await fetch("https://discord.com/api/users/@me/guilds", {
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
      },
      next: { revalidate: 300 } // Cache for 5 mins
    });
    
    if (res.ok) {
      userGuilds = await res.json();
    } else {
      userDiscordError = "Failed to fetch your Discord servers.";
    }
  } catch (err) {
    console.error("Discord API Error:", err);
    userDiscordError = "Error connecting to Discord.";
  }

  // Filter out guilds that the user is an admin of (permission flag 0x8 or MANAGE_GUILD 0x20)
  const MANAGE_GUILD = BigInt(0x20);
  const ADMINISTRATOR = BigInt(0x8);
  const adminUserGuilds = userGuilds.filter(g => {
    try {
      const perms = BigInt(g.permissions);
      return (perms & ADMINISTRATOR) === ADMINISTRATOR || 
             (perms & MANAGE_GUILD) === MANAGE_GUILD || 
             g.owner === true;
    } catch {
      return g.owner === true;
    }
  });

  const adminGuildIds = new Set(adminUserGuilds.map(g => String(g.id)));
  const botGuildIds = new Set(botGuilds.map(g => String(g.id)));
  
  // The active guilds (bot is in server & user can manage)
  const activeGuilds = botGuilds.filter(g => adminGuildIds.has(String(g.id)));
  
  // Uninvited guilds (user is admin but bot is not in server yet)
  const uninvitedGuilds = adminUserGuilds.filter(g => !botGuildIds.has(String(g.id)));

  const error = botError || userDiscordError;

  return (
    <div className="space-y-10 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white font-outfit">Your Servers</h1>
          <p className="text-[#948BA3] mt-2">
            Select an active server to configure or invite {process.env.NEXT_PUBLIC_BRAND_NAME || "Aizen XFX"} to new servers.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button 
            className="bg-gradient-to-r from-[#A855F7] to-[#7C3AED] text-white font-bold rounded-xl shadow-lg shadow-[#A855F7]/25 hover:opacity-90 gap-2"
            asChild
          >
            <a href={defaultInviteUrl} target="_blank" rel="noopener noreferrer">
              <Plus className="h-4 w-4" />
              Invite Bot to Server
            </a>
          </Button>
        </div>
      </div>

      {error ? (
        <div className="bg-red-500/10 border border-red-500/20 p-8 rounded-2xl text-center">
          <ShieldCheck className="h-12 w-12 text-red-500 mx-auto mb-4 opacity-50" />
          <h3 className="text-white font-bold text-lg">Connection Notice</h3>
          <p className="text-slate-400 mt-2">{error}</p>
        </div>
      ) : null}

      {/* Section 1: Active Bot Servers */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <h2 className="text-lg font-bold text-white font-outfit">Active Servers</h2>
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#A855F7]/10 text-[#C084FC] border border-[#A855F7]/20">
            {activeGuilds.length}
          </span>
        </div>

        {activeGuilds.length === 0 ? (
          <div className="glass border border-white/5 rounded-3xl p-12 text-center">
            <div className="h-14 w-14 bg-[#A855F7]/10 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-[#A855F7]/20 text-[#A855F7]">
              <Users className="h-7 w-7" />
            </div>
            <h3 className="text-white font-bold text-lg font-outfit">No Active Servers Found</h3>
            <p className="text-[#948BA3] text-sm mt-1 max-w-md mx-auto">
              {process.env.NEXT_PUBLIC_BRAND_NAME || "Aizen XFX"} has not joined your servers yet. Click below to add the bot to your server!
            </p>
            <Button 
              className="mt-6 bg-gradient-to-r from-[#A855F7] to-[#7C3AED] text-white font-bold rounded-xl shadow-lg shadow-[#A855F7]/25 hover:opacity-90 gap-2"
              asChild
            >
              <a href={defaultInviteUrl} target="_blank" rel="noopener noreferrer">
                <Plus className="h-4 w-4" />
                Add Bot to Discord
              </a>
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {activeGuilds.map((guild) => (
              <div 
                key={guild.id} 
                className="glass border border-white/5 rounded-3xl group hover:border-[#A855F7]/40 transition-all duration-300 overflow-hidden shadow-xl shadow-black/20 flex flex-col justify-between"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-6">
                    <div className="relative">
                      {guild.icon_url ? (
                        <Image 
                          src={guild.icon_url} 
                          alt={guild.name}
                          width={60}
                          height={60}
                          className="rounded-2xl border border-white/10 shadow-lg group-hover:scale-105 transition-transform"
                        />
                      ) : (
                        <div className="h-14 w-14 bg-[#A855F7]/20 rounded-2xl flex items-center justify-center border border-[#A855F7]/30 text-[#C084FC] font-bold text-xl shadow-lg group-hover:scale-105 transition-transform">
                          {guild.name.charAt(0)}
                        </div>
                      )}
                      <div className="absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full bg-emerald-500 border-2 border-[#07070D]" title="Bot Online" />
                    </div>
                    
                    <div className="flex flex-col items-end text-right">
                      <span className="text-[9px] uppercase font-black text-[#948BA3] tracking-widest mb-1">Guild ID</span>
                      <span className="text-[11px] font-mono text-slate-300 bg-white/5 px-2 py-0.5 rounded-lg border border-white/5 truncate max-w-[120px]">
                        {guild.id}
                      </span>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-bold text-white truncate group-hover:text-[#C084FC] transition-colors font-outfit">
                      {guild.name}
                    </h3>
                    <div className="flex items-center gap-3 mt-4 text-[#948BA3]">
                      <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1 rounded-xl border border-white/5">
                        <Users className="h-3.5 w-3.5 text-[#A855F7]" />
                        <span className="text-xs font-semibold text-slate-200">{guild.member_count.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1 rounded-xl border border-white/5">
                        <Hash className="h-3.5 w-3.5 text-emerald-400" />
                        <span className="text-xs font-semibold text-emerald-400">Connected</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="px-6 py-4 bg-white/[0.02] border-t border-white/5 group-hover:bg-[#A855F7]/[0.03] transition-colors">
                  <Button className="w-full justify-between group/btn py-5 bg-white/5 hover:bg-[#A855F7]/20 text-white border border-white/10 hover:border-[#A855F7]/40 rounded-xl" asChild>
                    <Link href={`/dashboard/guild/${guild.id}`}>
                      <span>Manage Server</span>
                      <ChevronRight className="h-4 w-4 group-hover/btn:translate-x-1 transition-transform text-[#C084FC]" />
                    </Link>
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Section 2: Other Admin Servers (Bot Not Added) */}
      {uninvitedGuilds.length > 0 && (
        <div className="pt-4 border-t border-white/5">
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-lg font-bold text-white font-outfit">Available to Add</h2>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-white/5 text-slate-400 border border-white/10">
              {uninvitedGuilds.length}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {uninvitedGuilds.map((guild: any) => {
              const iconUrl = guild.icon
                ? `https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png?size=128`
                : null;
              const serverInviteUrl = `https://discord.com/oauth2/authorize?client_id=${clientId}&permissions=8&integration_type=0&scope=bot+applications.commands&guild_id=${guild.id}`;

              return (
                <div 
                  key={guild.id} 
                  className="glass border border-white/5 rounded-3xl opacity-80 hover:opacity-100 hover:border-white/20 transition-all duration-300 overflow-hidden shadow-xl flex flex-col justify-between"
                >
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      {iconUrl ? (
                        <Image 
                          src={iconUrl} 
                          alt={guild.name}
                          width={56}
                          height={56}
                          className="rounded-2xl border border-white/10 grayscale group-hover:grayscale-0 transition-all"
                        />
                      ) : (
                        <div className="h-14 w-14 bg-white/5 rounded-2xl flex items-center justify-center border border-white/10 text-slate-400 font-bold text-xl">
                          {guild.name.charAt(0)}
                        </div>
                      )}
                      <span className="text-[10px] uppercase font-bold text-slate-500 bg-white/5 px-2 py-0.5 rounded-lg">
                        Admin
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-white truncate font-outfit">
                      {guild.name}
                    </h3>
                    <p className="text-xs text-[#948BA3] mt-1">Bot is not currently in this server.</p>
                  </div>

                  <div className="px-6 py-4 bg-white/[0.02] border-t border-white/5">
                    <Button 
                      className="w-full justify-center gap-2 bg-[#A855F7]/20 hover:bg-[#A855F7] text-white hover:text-white border border-[#A855F7]/30 rounded-xl transition-all"
                      asChild
                    >
                      <a href={serverInviteUrl} target="_blank" rel="noopener noreferrer">
                        <Plus className="h-4 w-4" />
                        <span>Invite Bot</span>
                      </a>
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
