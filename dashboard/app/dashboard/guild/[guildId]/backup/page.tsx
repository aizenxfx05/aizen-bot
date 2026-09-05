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
import { Database } from "lucide-react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";

const BackupForm = dynamic(() => import("@/components/dashboard/backup-form").then(mod => mod.BackupForm), {
  loading: () => <div className="h-96 w-full animate-pulse bg-white/[0.02] rounded-[30px] border border-white/5" />
});

export default async function BackupPage({ params }: { params: { guildId: string } }) {
  let backupData = null;
  try {
    backupData = await api.getBackup(params.guildId);
  } catch {
    backupData = {
      has_backup: false,
      backup_id: null,
      created_at: null,
      guild_name: null,
      roles_count: 0,
      channels_count: 0,
      auto_restore: false,
    };
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-500 pb-20">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-2xl font-black text-white flex items-center gap-3 tracking-tight font-outfit uppercase">
            <Database className="h-7 w-7 text-[#EAB308]" />
            Server Snapshot &amp; Disaster Recovery
          </h2>
          <p className="text-[#78716C] mt-1 font-medium text-sm">
            1-Click golden snapshots with automated disaster recovery protection.
          </p>
        </div>
      </div>

      <BackupForm 
        initialBackup={backupData} 
        guildId={params.guildId} 
      />
    </div>
  );
}
