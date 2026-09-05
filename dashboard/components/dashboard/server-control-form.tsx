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

import React, { useState, useEffect, useCallback } from "react";
import { 
  ShieldAlert, 
  Megaphone, 
  Trash2, 
  Clock, 
  Gavel, 
  UserCheck, 
  Shield, 
  Send, 
  RefreshCw,
  AlertTriangle,
  Radio,
  Users,
  Hash,
  Sparkles
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

interface ServerControlFormProps {
  guildId: string;
}

export function ServerControlForm({ guildId }: ServerControlFormProps) {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [channels, setChannels] = useState<any[]>([]);
  const [roles, setRoles] = useState<any[]>([]);

  // Action states
  const [lockdownStatus, setLockdownStatus] = useState<boolean>(false);
  const [lockdownReason, setLockdownReason] = useState("Emergency Lockdown initiated via Web Console");
  const [lockdownLoading, setLockdownLoading] = useState(false);

  // Announce states
  const [announceChannel, setAnnounceChannel] = useState("");
  const [announceTitle, setAnnounceTitle] = useState("");
  const [announceMessage, setAnnounceMessage] = useState("");
  const [announceLoading, setAnnounceLoading] = useState(false);

  // Purge states
  const [purgeChannel, setPurgeChannel] = useState("");
  const [purgeAmount, setPurgeAmount] = useState("20");
  const [purgeBotOnly, setPurgeBotOnly] = useState(false);
  const [purgeLoading, setPurgeLoading] = useState(false);

  // Slowmode states
  const [slowmodeChannel, setSlowmodeChannel] = useState("");
  const [slowmodeDelay, setSlowmodeDelay] = useState("5");
  const [slowmodeLoading, setSlowmodeLoading] = useState(false);

  // Moderation states
  const [modUserId, setModUserId] = useState("");
  const [modAction, setModAction] = useState<"timeout" | "kick" | "ban" | "unban">("timeout");
  const [modDuration, setModDuration] = useState("10");
  const [modReason, setModReason] = useState("Action taken via Web Console");
  const [modLoading, setModLoading] = useState(false);

  // Role manage states
  const [roleUserId, setRoleUserId] = useState("");
  const [selectedRole, setSelectedRole] = useState("");
  const [roleAction, setRoleAction] = useState<"add" | "remove">("add");
  const [roleLoading, setRoleLoading] = useState(false);

  const loadServerData = useCallback(async () => {
    setLoading(true);
    try {
      const [sData, cData, rData] = await Promise.all([
        api.getServerStats(guildId).catch(() => null),
        api.getServerChannels(guildId).catch(() => []),
        api.getServerRoles(guildId).catch(() => []),
      ]);
      setStats(sData);
      setChannels(cData || []);
      setRoles(rData || []);

      const firstTextCh = (cData || []).find((c: any) => c.type === "text");
      if (firstTextCh) {
        if (!announceChannel) setAnnounceChannel(firstTextCh.id);
        if (!purgeChannel) setPurgeChannel(firstTextCh.id);
        if (!slowmodeChannel) setSlowmodeChannel(firstTextCh.id);
      }
      if (rData && rData.length > 0 && !selectedRole) {
        setSelectedRole(rData[0].id);
      }
    } catch (err) {
      console.error(err);
      toast.error("Failed to load server details from bot API");
    } finally {
      setLoading(false);
    }
  }, [guildId]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    loadServerData();
  }, [guildId, loadServerData]);

  // Handlers
  const handleLockdown = async (targetLocked: boolean) => {
    setLockdownLoading(true);
    try {
      const res = await api.triggerLockdown(guildId, {
        locked: targetLocked,
        reason: lockdownReason,
      });
      setLockdownStatus(targetLocked);
      toast.success(
        targetLocked
          ? `Server locked down! ${res.affected_channels} channels secured.`
          : `Server unlocked! ${res.affected_channels} channels restored.`
      );
    } catch (err: any) {
      toast.error(err.message || "Failed to execute server lockdown");
    } finally {
      setLockdownLoading(false);
    }
  };

  const handleAnnounce = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!announceChannel || !announceTitle.trim() || !announceMessage.trim()) {
      toast.error("Please fill in channel, title, and announcement message.");
      return;
    }
    setAnnounceLoading(true);
    try {
      await api.sendAnnouncement(guildId, {
        channel_id: Number(announceChannel),
        title: announceTitle.trim(),
        message: announceMessage.trim(),
      });
      toast.success("Announcement broadcasted successfully!");
      setAnnounceTitle("");
      setAnnounceMessage("");
    } catch (err: any) {
      toast.error(err.message || "Failed to send announcement");
    } finally {
      setAnnounceLoading(false);
    }
  };

  const handlePurge = async (e: React.FormEvent) => {
    e.preventDefault();
    const amountNum = parseInt(purgeAmount, 10);
    if (!purgeChannel || isNaN(amountNum) || amountNum < 1 || amountNum > 100) {
      toast.error("Amount must be a number between 1 and 100.");
      return;
    }
    setPurgeLoading(true);
    try {
      const res = await api.purgeMessages(guildId, {
        channel_id: Number(purgeChannel),
        amount: amountNum,
        bot_only: purgeBotOnly,
      });
      toast.success(`Purged ${res.deleted_count} messages successfully!`);
    } catch (err: any) {
      toast.error(err.message || "Failed to purge messages");
    } finally {
      setPurgeLoading(false);
    }
  };

  const handleSlowmode = async (delaySec: number) => {
    if (!slowmodeChannel) {
      toast.error("Please select a target channel.");
      return;
    }
    setSlowmodeLoading(true);
    try {
      await api.setSlowmode(guildId, {
        channel_id: Number(slowmodeChannel),
        delay: delaySec,
        reason: "Updated via Web Dashboard",
      });
      setSlowmodeDelay(delaySec.toString());
      toast.success(
        delaySec === 0
          ? "Slowmode disabled for channel"
          : `Slowmode set to ${delaySec}s for channel`
      );
    } catch (err: any) {
      toast.error(err.message || "Failed to set slowmode");
    } finally {
      setSlowmodeLoading(false);
    }
  };

  const handleModeration = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!modUserId.trim() || isNaN(Number(modUserId.trim()))) {
      toast.error("Please provide a valid numeric Discord User ID.");
      return;
    }
    const userIdNum = Number(modUserId.trim());
    setModLoading(true);

    try {
      if (modAction === "timeout") {
        const mins = parseInt(modDuration, 10) || 5;
        await api.timeoutMember(guildId, {
          user_id: userIdNum,
          duration_minutes: mins,
          reason: modReason,
        });
        toast.success(`User timed out for ${mins} minutes!`);
      } else if (modAction === "kick") {
        await api.kickMember(guildId, {
          user_id: userIdNum,
          reason: modReason,
        });
        toast.success("User kicked from the server!");
      } else if (modAction === "ban") {
        await api.banMember(guildId, {
          user_id: userIdNum,
          delete_message_days: 1,
          reason: modReason,
        });
        toast.success("User banned from the server!");
      } else if (modAction === "unban") {
        await api.unbanMember(guildId, {
          user_id: userIdNum,
          reason: modReason,
        });
        toast.success("User unbanned!");
      }
      setModUserId("");
    } catch (err: any) {
      toast.error(err.message || "Moderation action failed");
    } finally {
      setModLoading(false);
    }
  };

  const handleRoleManage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!roleUserId.trim() || isNaN(Number(roleUserId.trim()))) {
      toast.error("Please provide a valid numeric User ID.");
      return;
    }
    if (!selectedRole) {
      toast.error("Please select a role.");
      return;
    }
    setRoleLoading(true);
    try {
      await api.manageMemberRole(guildId, {
        user_id: Number(roleUserId.trim()),
        role_id: Number(selectedRole),
        action: roleAction,
      });
      toast.success(
        roleAction === "add"
          ? "Role assigned to member successfully!"
          : "Role removed from member successfully!"
      );
      setRoleUserId("");
    } catch (err: any) {
      toast.error(err.message || "Role assignment failed");
    } finally {
      setRoleLoading(false);
    }
  };

  const textChannelOptions = channels
    .filter((c) => c.type === "text")
    .map((c) => ({ value: c.id, label: `# ${c.name}` }));

  const roleOptions = roles.map((r) => ({
    value: r.id,
    label: `${r.name} (${r.members_count} members)`,
  }));

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Live Server Stats Header */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl shadow-2xl">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-[#A855F7]/10 border border-[#A855F7]/20 text-[#A855F7]">
              <Users className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Members</p>
              <p className="text-xl font-black text-white">{stats.member_count.toLocaleString()}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
              <Hash className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Channels</p>
              <p className="text-xl font-black text-white">{stats.channels.total}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Roles</p>
              <p className="text-xl font-black text-white">{stats.roles_count}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Boost Tier</p>
              <p className="text-xl font-black text-white">Tier {stats.boost_tier} ({stats.boost_count})</p>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Server Control Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* 1. Emergency Lockdown */}
        <div className="p-6 rounded-3xl bg-slate-900/60 border border-red-500/20 backdrop-blur-xl shadow-2xl relative overflow-hidden flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400">
                  <ShieldAlert className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Emergency Lockdown</h3>
                  <p className="text-xs text-slate-400">Lock or unlock all public text channels instantly.</p>
                </div>
              </div>
              <span className={`text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider ${
                lockdownStatus ? "bg-red-500/20 text-red-400 border border-red-500/30" : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
              }`}>
                {lockdownStatus ? "Locked" : "Unlocked"}
              </span>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300">Lockdown Reason</label>
              <Input
                value={lockdownReason}
                onChange={(e) => setLockdownReason(e.target.value)}
                placeholder="Reason for audit log..."
                className="bg-slate-950/60 border-slate-800"
              />
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800/60 flex gap-3">
            <Button
              onClick={() => handleLockdown(true)}
              disabled={lockdownLoading}
              className="flex-1 bg-red-600 hover:bg-red-700 text-white font-bold"
            >
              {lockdownLoading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <AlertTriangle className="h-4 w-4 mr-2" />}
              Initiate Lockdown
            </Button>
            <Button
              onClick={() => handleLockdown(false)}
              disabled={lockdownLoading}
              variant="outline"
              className="flex-1 border-slate-700 hover:bg-slate-800 font-bold"
            >
              Lift Lockdown
            </Button>
          </div>
        </div>

        {/* 2. Bulk Message Purge */}
        <div className="p-6 rounded-3xl bg-slate-900/60 border border-[#A855F7]/20 backdrop-blur-xl shadow-2xl flex flex-col justify-between">
          <form onSubmit={handlePurge} className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-[#A855F7]/10 border border-[#A855F7]/20 text-[#A855F7]">
                <Trash2 className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Channel Message Purge</h3>
                <p className="text-xs text-slate-400">Fast bulk deletion of spam or recent messages.</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Target Channel</label>
                <Select
                  value={purgeChannel}
                  onValueChange={setPurgeChannel}
                  options={textChannelOptions}
                  placeholder="Select channel..."
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300">Amount (1-100)</label>
                  <Input
                    type="number"
                    min="1"
                    max="100"
                    value={purgeAmount}
                    onChange={(e) => setPurgeAmount(e.target.value)}
                    className="bg-slate-950/60 border-slate-800"
                  />
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/40 border border-slate-800 self-end">
                  <span className="text-xs text-slate-300">Bot Only</span>
                  <Switch checked={purgeBotOnly} onCheckedChange={setPurgeBotOnly} />
                </div>
              </div>

              {/* Quick Amount Presets */}
              <div className="flex gap-2">
                {["10", "25", "50", "100"].map((preset) => (
                  <button
                    key={preset}
                    type="button"
                    onClick={() => setPurgeAmount(preset)}
                    className={`px-3 py-1 text-xs rounded-lg font-bold transition-all ${
                      purgeAmount === preset
                        ? "bg-[#A855F7] text-black font-bold"
                        : "bg-slate-800/80 text-slate-400 hover:bg-slate-700"
                    }`}
                  >
                    {preset}
                  </button>
                ))}
              </div>
            </div>

            <Button
              type="submit"
              disabled={purgeLoading}
              className="w-full bg-[#A855F7] hover:bg-[#C084FC] text-black font-bold"
            >
              {purgeLoading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <Trash2 className="h-4 w-4 mr-2" />}
              Purge Messages
            </Button>
          </form>
        </div>

        {/* 3. Announcement Dispatcher */}
        <div className="p-6 rounded-3xl bg-slate-900/60 border border-blue-500/20 backdrop-blur-xl shadow-2xl flex flex-col justify-between">
          <form onSubmit={handleAnnounce} className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
                <Megaphone className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Broadcast Announcement</h3>
                <p className="text-xs text-slate-400">Dispatch formatted bot embeds to any server channel.</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Channel</label>
                <Select
                  value={announceChannel}
                  onValueChange={setAnnounceChannel}
                  options={textChannelOptions}
                  placeholder="Select channel..."
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Title</label>
                <Input
                  value={announceTitle}
                  onChange={(e) => setAnnounceTitle(e.target.value)}
                  placeholder="Announcement title..."
                  className="bg-slate-950/60 border-slate-800"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Message Content</label>
                <Textarea
                  value={announceMessage}
                  onChange={(e) => setAnnounceMessage(e.target.value)}
                  placeholder="Enter markdown announcement message..."
                  className="bg-slate-950/60 border-slate-800 min-h-[90px]"
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={announceLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold"
            >
              {announceLoading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <Send className="h-4 w-4 mr-2" />}
              Send Announcement
            </Button>
          </form>
        </div>

        {/* 4. Channel Slowmode Controller */}
        <div className="p-6 rounded-3xl bg-slate-900/60 border border-amber-500/20 backdrop-blur-xl shadow-2xl flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
                <Clock className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Channel Slowmode</h3>
                <p className="text-xs text-slate-400">Instantly limit chat spam by throttling message rates.</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Target Channel</label>
                <Select
                  value={slowmodeChannel}
                  onValueChange={setSlowmodeChannel}
                  options={textChannelOptions}
                  placeholder="Select channel..."
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Quick Presets</label>
                <div className="grid grid-cols-4 gap-2">
                  {[
                    { label: "Off", sec: 0 },
                    { label: "5s", sec: 5 },
                    { label: "15s", sec: 15 },
                    { label: "30s", sec: 30 },
                    { label: "1m", sec: 60 },
                    { label: "5m", sec: 300 },
                    { label: "15m", sec: 900 },
                    { label: "1h", sec: 3600 },
                  ].map((item) => (
                    <button
                      key={item.label}
                      type="button"
                      onClick={() => handleSlowmode(item.sec)}
                      disabled={slowmodeLoading}
                      className={`p-2 rounded-xl text-xs font-bold border transition-all ${
                        slowmodeDelay === item.sec.toString()
                          ? "bg-amber-500/20 border-amber-500/50 text-amber-300"
                          : "bg-slate-950/60 border-slate-800 text-slate-400 hover:bg-slate-800 hover:text-white"
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800/60 text-xs text-slate-500 flex items-center gap-2">
            <Radio className="h-4 w-4 text-amber-400" />
            Clicking a preset immediately applies it to the channel.
          </div>
        </div>

        {/* 5. Quick Member Moderation */}
        <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl shadow-2xl flex flex-col justify-between">
          <form onSubmit={handleModeration} className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
                <Gavel className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Quick Moderation</h3>
                <p className="text-xs text-slate-400">Timeout, kick, or ban members without opening Discord.</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300">Action</label>
                  <Select
                    value={modAction}
                    onValueChange={(val: any) => setModAction(val)}
                    options={[
                      { value: "timeout", label: "Timeout (Mute)" },
                      { value: "kick", label: "Kick Member" },
                      { value: "ban", label: "Ban Member" },
                      { value: "unban", label: "Unban User" },
                    ]}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300">User ID</label>
                  <Input
                    value={modUserId}
                    onChange={(e) => setModUserId(e.target.value)}
                    placeholder="Discord User ID..."
                    className="bg-slate-950/60 border-slate-800"
                  />
                </div>
              </div>

              {modAction === "timeout" && (
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300">Duration (Minutes)</label>
                  <div className="flex gap-2">
                    {["5", "15", "60", "1440"].map((mins) => (
                      <button
                        key={mins}
                        type="button"
                        onClick={() => setModDuration(mins)}
                        className={`flex-1 py-1 rounded-lg text-xs font-bold transition-all ${
                          modDuration === mins
                            ? "bg-rose-600 text-white"
                            : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                        }`}
                      >
                        {mins === "60" ? "1h" : mins === "1440" ? "24h" : `${mins}m`}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Reason</label>
                <Input
                  value={modReason}
                  onChange={(e) => setModReason(e.target.value)}
                  placeholder="Reason for audit log..."
                  className="bg-slate-950/60 border-slate-800"
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={modLoading}
              className="w-full bg-rose-600 hover:bg-rose-700 text-white font-bold"
            >
              {modLoading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <Gavel className="h-4 w-4 mr-2" />}
              Execute {modAction.toUpperCase()}
            </Button>
          </form>
        </div>

        {/* 6. Role Manager */}
        <div className="p-6 rounded-3xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl shadow-2xl flex flex-col justify-between">
          <form onSubmit={handleRoleManage} className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-2xl bg-[#A855F7]/10 border border-[#A855F7]/20 text-[#A855F7]">
                <UserCheck className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Member Role Assignment</h3>
                <p className="text-xs text-slate-400">Add or remove roles for any server member.</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">User ID</label>
                <Input
                  value={roleUserId}
                  onChange={(e) => setRoleUserId(e.target.value)}
                  placeholder="Discord User ID..."
                  className="bg-slate-950/60 border-slate-800"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Select Role</label>
                <Select
                  value={selectedRole}
                  onValueChange={setSelectedRole}
                  options={roleOptions}
                  placeholder="Select role..."
                />
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setRoleAction("add")}
                  className={`py-2 rounded-xl text-xs font-bold border transition-all ${
                    roleAction === "add"
                      ? "bg-[#A855F7] text-black font-bold border-[#A855F7]"
                      : "bg-slate-950/60 border-slate-800 text-slate-400 hover:bg-slate-800"
                  }`}
                >
                  Assign Role
                </button>
                <button
                  type="button"
                  onClick={() => setRoleAction("remove")}
                  className={`py-2 rounded-xl text-xs font-bold border transition-all ${
                    roleAction === "remove"
                      ? "bg-red-600 text-white border-red-500"
                      : "bg-slate-950/60 border-slate-800 text-slate-400 hover:bg-slate-800"
                  }`}
                >
                  Remove Role
                </button>
              </div>
            </div>

            <Button
              type="submit"
              disabled={roleLoading}
              className="w-full bg-[#A855F7] hover:bg-[#C084FC] text-black font-bold mt-2"
            >
              {roleLoading ? <RefreshCw className="h-4 w-4 animate-spin mr-2" /> : <UserCheck className="h-4 w-4 mr-2" />}
              {roleAction === "add" ? "Assign Role to User" : "Remove Role from User"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
