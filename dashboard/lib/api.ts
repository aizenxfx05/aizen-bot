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

import { 
  BotInfo, 
  BotStatus, 
  GuildSummary, 
  GuildDetails,
  PrefixConfig, 
  AutomodConfig, 
  TicketConfig, 
  LevelingConfig, 
  LoggingConfig,
  PrefixUpdate,
  AutomodUpdate,
  LevelingUpdate,
  LoggingUpdate,
  LeaderboardEntry,
  DiscordChannel,
  DiscordRole,
  AutoRoleConfig,
  AutoRoleUpdate,
  AdminStats,
  AdminConfig,
  AdminConfigUpdate,
  BackupInfo,
  MusicConfig,
  GiveawayItem
} from "@/types/api";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const API_KEY = process.env.NEXT_PUBLIC_DASHBOARD_API_KEY;

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit & { next?: NextFetchRequestConfig } = {}
): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  
  const headers = new Headers(options.headers);
  if (API_KEY) {
    headers.set("Authorization", `Bearer ${API_KEY}`);
  }
  headers.set("Content-Type", "application/json");
  try {
    const response = await fetch(url, {
      ...options,
      headers,
      // CRITICAL: Never cache mutation responses. For GETs, use revalidate: 0
      // to always fetch fresh data from the bot API. Caching was causing
      // saved data to "disappear" on reload because Next.js served stale cache.
      next: options.next || { revalidate: 0 },
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: "An unknown error occurred" };
      }
      console.error(`[API HTTP Error] Status ${response.status} for ${url}:`, errorData);
      throw new ApiError(response.status, errorData.detail || response.statusText);
    }

    return response.json();
  } catch (error) {
    console.error(`[API Network/Fetch Error] Failed to fetch ${url}:`, error);
    throw error;
  }
}

export const api = {
  // Bot 
  getBotStatus: () => request<BotStatus>("/bot/status"),
  getBotInfo: () => request<BotInfo>("/bot/info"),

  // Guilds
  listGuilds: () => request<GuildSummary[]>("/guilds/"),
  getGuildDetails: (guildId: string) => request<any>(`/guilds/${guildId}`),
  getChannels: (guildId: string) => request<DiscordChannel[]>(`/guilds/${guildId}/channels`),
  getRoles: (guildId: string) => request<DiscordRole[]>(`/guilds/${guildId}/roles`),
  
  // Module Configs
  getPrefix: (guildId: string) => request<PrefixConfig>(`/guilds/${guildId}/prefix`),
  updatePrefix: (guildId: string, prefix: string) => 
    request<{ status: string; new_prefix: string }>(`/guilds/${guildId}/prefix`, {
      method: "POST",
      body: JSON.stringify({ prefix }),
    }),

  getAutomod: (guildId: string) => request<AutomodConfig>(`/guilds/${guildId}/automod`),
  updateAutomod: (guildId: string, data: Partial<AutomodConfig>) => 
    request<{ status: string }>(`/guilds/${guildId}/automod`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getTickets: (guildId: string) => request<TicketConfig>(`/guilds/${guildId}/tickets`),
  updateTickets: (guildId: string, data: any) => 
    request<{ status: string }>(`/guilds/${guildId}/tickets`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  
  getLeveling: (guildId: string) => request<LevelingConfig>(`/guilds/${guildId}/leveling`),
  updateLeveling: (guildId: string, data: any) => 
    request<{ status: string }>(`/guilds/${guildId}/leveling`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getLogging: (guildId: string) => request<LoggingConfig>(`/guilds/${guildId}/logging`),
  updateLogging: (guildId: string, data: any) => 
    request<{ status: string }>(`/guilds/${guildId}/logging`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getLeaderboard: (guildId: string) => request<LeaderboardEntry[]>(`/guilds/${guildId}/leveling/leaderboard`),

  getWelcome: (guildId: string) => request<any>(`/guilds/${guildId}/welcome`),
  updateWelcome: (guildId: string, data: any) => 
    request<{ status: string }>(`/guilds/${guildId}/welcome`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getAntiNuke: (guildId: string) => request<any>(`/guilds/${guildId}/antinuke`),
  updateAntiNuke: (guildId: string, data: any) => 
    request<{ status: string }>(`/guilds/${guildId}/antinuke`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getVerification: (guildId: string) => request<any>(`/guilds/${guildId}/verification`),
  updateVerification: (guildId: string, data: any) => 
    request<{ status: string }>(`/guilds/${guildId}/verification`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getVanityRoles: (guildId: string) => request<any[]>(`/guilds/${guildId}/vanityroles`),
  addVanityRole: (guildId: string, data: any) =>
    request<{ status: string }>(`/guilds/${guildId}/vanityroles`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteVanityRole: (guildId: string, vanity: string) =>
    request<{ status: string }>(`/guilds/${guildId}/vanityroles/${vanity}`, {
      method: "DELETE",
    }),

  getAutoRole: (guildId: string) => request<AutoRoleConfig>(`/guilds/${guildId}/autorole`),
  updateAutoRole: (guildId: string, data: AutoRoleUpdate) =>
    request<{ status: string }>(`/guilds/${guildId}/autorole`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getTracking: (guildId: string) => request<any>(`/guilds/${guildId}/tracking`),
  updateTracking: (guildId: string, data: any) =>
    request<{ status: string }>(`/guilds/${guildId}/tracking`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getJ2C: (guildId: string) => request<any>(`/guilds/${guildId}/j2c`),
  updateJ2C: (guildId: string, data: any) =>
    request<{ status: string }>(`/guilds/${guildId}/j2c`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getJoinDM: (guildId: string) => request<any>(`/guilds/${guildId}/joindm`),
  updateJoinDM: (guildId: string, data: any) =>
    request<{ status: string }>(`/guilds/${guildId}/joindm`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getCustomRoles: (guildId: string) => request<any>(`/guilds/${guildId}/customroles`),
  updateCustomRoles: (guildId: string, data: any) =>
    request<{ status: string }>(`/guilds/${guildId}/customroles`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getAutoReact: (guildId: string) => request<any>(`/guilds/${guildId}/autoreact`),
  updateAutoReact: (guildId: string, data: any) =>
    request<{ status: string }>(`/guilds/${guildId}/autoreact`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getInvcRole: (guildId: string) => request<any>(`/guilds/${guildId}/invcrole`),
  updateInvcRole: (guildId: string, data: any) =>
    request<{ status: string }>(`/guilds/${guildId}/invcrole`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  getRR: (guildId: string) => request<any>(`/guilds/${guildId}/reactionroles`),
  updateRR: (guildId: string, data: any) =>
    request<{ status: string }>(`/guilds/${guildId}/reactionroles`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  getInvites: (guildId: string) => request<any>(`/guilds/${guildId}/invites`),
  updateInvites: (guildId: string, data: any) =>
    request<{ status: string }>(`/guilds/${guildId}/invites`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  // Admin
  getAdminStats: () => request<AdminStats>("/admin/stats"),
  getAdminConfig: () => request<AdminConfig>("/admin/config"),
  updateAdminConfig: (data: AdminConfigUpdate) => 
    request<{ status: string }>("/admin/config", {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  // Server Management & Live Control
  getServerStats: (guildId: string) => 
    request<any>(`/guilds/${guildId}/server-control/stats`),

  getServerChannels: (guildId: string) => 
    request<any[]>(`/guilds/${guildId}/server-control/channels`),

  getServerRoles: (guildId: string) => 
    request<any[]>(`/guilds/${guildId}/server-control/roles`),

  triggerLockdown: (guildId: string, data: { locked: boolean; reason?: string }) =>
    request<{ success: boolean; affected_channels: number }>(`/guilds/${guildId}/server-control/lockdown`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  sendAnnouncement: (guildId: string, data: { channel_id: number; title: string; message: string }) =>
    request<{ success: boolean; message_id: string }>(`/guilds/${guildId}/server-control/announce`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  purgeMessages: (guildId: string, data: { channel_id: number; amount: number; bot_only?: boolean }) =>
    request<{ success: boolean; deleted_count: number }>(`/guilds/${guildId}/server-control/purge`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  setSlowmode: (guildId: string, data: { channel_id: number; delay: number; reason?: string }) =>
    request<{ success: boolean; slowmode_delay: number }>(`/guilds/${guildId}/server-control/slowmode`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  timeoutMember: (guildId: string, data: { user_id: number; duration_minutes: number; reason?: string }) =>
    request<{ success: boolean; action: string }>(`/guilds/${guildId}/server-control/moderation/timeout`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  kickMember: (guildId: string, data: { user_id: number; reason?: string }) =>
    request<{ success: boolean; action: string }>(`/guilds/${guildId}/server-control/moderation/kick`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  banMember: (guildId: string, data: { user_id: number; delete_message_days?: number; reason?: string }) =>
    request<{ success: boolean; action: string }>(`/guilds/${guildId}/server-control/moderation/ban`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  unbanMember: (guildId: string, data: { user_id: number; reason?: string }) =>
    request<{ success: boolean; action: string }>(`/guilds/${guildId}/server-control/moderation/unban`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  manageMemberRole: (guildId: string, data: { user_id: number; role_id: number; action: "add" | "remove" }) =>
    request<{ success: boolean; action: string }>(`/guilds/${guildId}/server-control/roles/manage`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Backup System
  getBackup: (guildId: string) => 
    request<BackupInfo>(`/guilds/${guildId}/backup`),
  createBackup: (guildId: string) => 
    request<{ status: string; backup_id: string }>(`/guilds/${guildId}/backup`, {
      method: "POST",
    }),
  deleteBackup: (guildId: string) => 
    request<{ status: string }>(`/guilds/${guildId}/backup`, {
      method: "DELETE",
    }),

  // Music System
  getMusic: (guildId: string) => 
    request<MusicConfig>(`/guilds/${guildId}/music`),
  updateMusic: (guildId: string, data: Partial<MusicConfig>) => 
    request<{ status: string }>(`/guilds/${guildId}/music`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  // Giveaway System
  getGiveaways: (guildId: string) => 
    request<GiveawayItem[]>(`/guilds/${guildId}/giveaways`),
  deleteGiveaway: (guildId: string, messageId: string) => 
    request<{ status: string }>(`/guilds/${guildId}/giveaways/${messageId}`, {
      method: "DELETE",
    }),
};

