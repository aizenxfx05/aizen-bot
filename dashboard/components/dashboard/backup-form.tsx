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
  Database, 
  ShieldCheck, 
  RefreshCw, 
  Trash2, 
  AlertTriangle, 
  Layers, 
  Hash, 
  Clock, 
  CheckCircle2, 
  Sparkles,
  Download,
  Info
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { BackupInfo } from "@/types/api";

interface BackupFormProps {
  initialBackup: BackupInfo;
  guildId: string;
}

export function BackupForm({ initialBackup, guildId }: BackupFormProps) {
  const [backup, setBackup] = useState<BackupInfo>(initialBackup);
  const [loading, setLoading] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const handleCreateBackup = async () => {
    setLoading(true);
    try {
      const res = await api.createBackup(guildId);
      toast.success("Golden backup snapshot created successfully!");
      // Refresh backup status
      const fresh = await api.getBackup(guildId);
      setBackup(fresh);
    } catch (err: any) {
      console.error(err);
      toast.error(err?.message || "Failed to create backup");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBackup = async () => {
    setLoading(true);
    try {
      await api.deleteBackup(guildId);
      toast.success("Backup deleted successfully");
      setBackup({
        has_backup: false,
        backup_id: null,
        created_at: null,
        guild_name: null,
        roles_count: 0,
        channels_count: 0,
        auto_restore: false,
      });
      setConfirmDelete(false);
    } catch (err: any) {
      console.error(err);
      toast.error("Failed to delete backup");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Policy Notice: 1 Backup Limit */}
      <div className="p-5 rounded-2xl bg-[#EAB308]/[0.04] border border-[#EAB308]/20 backdrop-blur-xl flex items-start gap-4">
        <div className="p-2.5 rounded-xl bg-[#EAB308]/10 text-[#EAB308] mt-0.5">
          <Info className="h-5 w-5" />
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-black uppercase tracking-wider text-[#EAB308]">
              Single Backup Policy Active
            </span>
            <span className="px-2 py-0.5 text-[10px] font-bold bg-[#EAB308]/20 text-[#EAB308] rounded-full">
              1 Per Server
            </span>
          </div>
          <p className="text-xs text-[#78716C] leading-relaxed">
            To prevent database clutter and ensure instant recovery speed, each Discord server maintains exactly one golden snapshot. Creating a new backup automatically replaces your previous snapshot.
          </p>
        </div>
      </div>

      {/* Main Backup Status Card */}
      <div className="p-8 rounded-3xl bg-[#0C0B0F]/90 border border-white/5 backdrop-blur-2xl shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-[#EAB308]/[0.03] blur-[100px] rounded-full pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-8 border-b border-white/5">
          <div className="flex items-center gap-4">
            <div className={cn(
              "h-16 w-16 rounded-2xl flex items-center justify-center border transition-all",
              backup.has_backup
                ? "bg-[#EAB308]/10 border-[#EAB308]/30 shadow-lg shadow-[#EAB308]/10 text-[#EAB308]"
                : "bg-slate-900/50 border-slate-800 text-slate-500"
            )}>
              <Database className="h-8 w-8" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h3 className="text-xl font-bold text-white tracking-tight">
                  {backup.has_backup ? "Server Snapshot Ready" : "No Backup Found"}
                </h3>
                <span className={cn(
                  "px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider",
                  backup.has_backup
                    ? "bg-[#EAB308]/10 text-[#EAB308] border border-[#EAB308]/20"
                    : "bg-slate-800 text-slate-400"
                )}>
                  {backup.has_backup ? "Synchronized" : "Empty"}
                </span>
              </div>
              <p className="text-xs text-[#78716C] mt-1">
                {backup.has_backup 
                  ? `Snapshot ID: ${backup.backup_id}` 
                  : "Create a snapshot to preserve roles, channels, and permissions."}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              onClick={handleCreateBackup}
              disabled={loading}
              className="bg-[#EAB308] hover:bg-[#F59E0B] text-black font-black uppercase tracking-wider rounded-xl px-6 py-5 shadow-lg shadow-[#EAB308]/20 gap-2 transition-all hover:scale-[1.02]"
            >
              {loading ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : backup.has_backup ? (
                <RefreshCw className="h-4 w-4" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              {backup.has_backup ? "Replace Backup" : "Create Backup"}
            </Button>

            {backup.has_backup && (
              <>
                {confirmDelete ? (
                  <div className="flex items-center gap-2">
                    <Button
                      onClick={handleDeleteBackup}
                      disabled={loading}
                      variant="destructive"
                      className="rounded-xl px-4 py-5 text-xs font-bold"
                    >
                      Confirm Delete
                    </Button>
                    <Button
                      onClick={() => setConfirmDelete(false)}
                      variant="outline"
                      className="rounded-xl border-slate-800 px-3 py-5 text-xs text-slate-400"
                    >
                      Cancel
                    </Button>
                  </div>
                ) : (
                  <Button
                    onClick={() => setConfirmDelete(true)}
                    variant="outline"
                    className="rounded-xl border-white/5 bg-white/[0.02] hover:bg-red-500/10 hover:border-red-500/30 text-slate-400 hover:text-red-400 px-4 py-5 transition-all"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </>
            )}
          </div>
        </div>

        {/* Snapshot Metadata Grid */}
        {backup.has_backup ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-8">
            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2">
              <div className="flex items-center gap-2 text-slate-400">
                <Clock className="h-4 w-4 text-[#EAB308]" />
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Captured At</span>
              </div>
              <p className="text-sm font-bold text-white">{backup.created_at || "Just now"}</p>
              <p className="text-[10px] text-[#78716C]">Stored securely on isolated volume</p>
            </div>

            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2">
              <div className="flex items-center gap-2 text-slate-400">
                <Layers className="h-4 w-4 text-[#EAB308]" />
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Roles Saved</span>
              </div>
              <p className="text-2xl font-black text-white font-outfit">{backup.roles_count}</p>
              <p className="text-[10px] text-[#78716C]">Full permissions hierarchy & colors</p>
            </div>

            <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2">
              <div className="flex items-center gap-2 text-slate-400">
                <Hash className="h-4 w-4 text-[#EAB308]" />
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Channels Saved</span>
              </div>
              <p className="text-2xl font-black text-white font-outfit">{backup.channels_count}</p>
              <p className="text-[10px] text-[#78716C]">Text, Voice, Categories & Topics</p>
            </div>
          </div>
        ) : (
          <div className="py-12 flex flex-col items-center justify-center text-center space-y-3">
            <div className="h-12 w-12 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center justify-center text-slate-600">
              <Database className="h-6 w-6" />
            </div>
            <p className="text-sm font-bold text-slate-300">No snapshot recorded for this server</p>
            <p className="text-xs text-[#78716C] max-w-sm">
              Click &quot;Create Backup&quot; to capture your current server configuration and protect against accidental deletions.
            </p>
          </div>
        )}
      </div>

      {/* Disaster Recovery Protection Feature Card */}
      <div className="p-6 rounded-3xl bg-[#0C0B0F]/90 border border-white/5 backdrop-blur-xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="p-3.5 rounded-2xl bg-[#EAB308]/10 border border-[#EAB308]/20 text-[#EAB308]">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="font-bold text-white text-base">Automatic Disaster Recovery Shield</h4>
              <span className="px-2 py-0.5 text-[9px] font-black uppercase tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full">
                Active Guardian
              </span>
            </div>
            <p className="text-xs text-[#78716C] mt-0.5">
              If an unauthorized entity wipes your channels or roles, Aizen automatically initiates restoration from your latest golden backup.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
