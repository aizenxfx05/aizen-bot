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
import Image from "next/image";
import { 
  AtSign, 
  BellRing, 
  Sparkles, 
  MessageSquare, 
  Radio, 
  Sliders, 
  Clock, 
  Link as LinkIcon, 
  Save, 
  RefreshCcw, 
  CheckCircle2, 
  AlertCircle,
  Eye,
  Hash,
  ExternalLink,
  Bot
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { TagBotConfig, DiscordChannel } from "@/types/api";

interface TagBotFormProps {
  initialConfig: TagBotConfig;
  channels: DiscordChannel[];
  guildId: string;
}

const PRESET_COLORS = [
  { name: "Royal Purple", value: "#A855F7" },
  { name: "Neon Violet", value: "#8B5CF6" },
  { name: "Electric Cyan", value: "#06B6D4" },
  { name: "Emerald Mint", value: "#10B981" },
  { name: "Rose Crimson", value: "#F43F5E" },
  { name: "Amber Sunset", value: "#F59E0B" },
];

export function TagBotForm({ initialConfig, channels, guildId }: TagBotFormProps) {
  const [config, setConfig] = useState<TagBotConfig>(initialConfig);
  const [saving, setSaving] = useState(false);
  const [previewMode, setPreviewMode] = useState<"response" | "alert">("response");

  const textChannels = channels.filter(
    (c) => c.type === "0" || c.type === "text" || !(c as any).is_voice
  );

  const handleSave = async () => {
    setSaving(true);
    const promise = api.updateTagBot(guildId, config);

    toast.promise(promise, {
      loading: "Saving Tag Bot & Mention Alert settings...",
      success: "Settings saved successfully!",
      error: "Failed to update Tag Bot settings",
    });

    try {
      await promise;
    } catch (err: any) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setConfig({
      guild_id: guildId,
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
    toast.info("Reset settings to default. Click 'Save Changes' to apply.");
  };

  const insertVariable = (variable: string) => {
    setConfig((prev) => ({
      ...prev,
      custom_message: (prev.custom_message || "") + " " + variable,
    }));
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header Banner */}
      <div className="p-8 rounded-3xl bg-[#0D0B18]/90 border border-[#A855F7]/20 backdrop-blur-2xl shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-[#A855F7]/10 blur-[100px] rounded-full pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
          <div className="flex items-center gap-5">
            <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-[#A855F7]/20 to-[#9333EA]/10 border border-[#A855F7]/30 flex items-center justify-center text-[#A855F7] shadow-lg shadow-[#A855F7]/15">
              <AtSign className="h-8 w-8 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-2xl font-black text-white tracking-tight">Tag Bot &amp; Mention Alert</h2>
                <span
                  className={cn(
                    "flex items-center gap-1.5 px-3 py-0.5 rounded-full text-[11px] font-black uppercase tracking-wider border",
                    config.enabled
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                      : "bg-red-500/10 text-red-400 border-red-500/20"
                  )}
                >
                  <span
                    className={cn(
                      "h-1.5 w-1.5 rounded-full",
                      config.enabled ? "bg-emerald-400 animate-pulse" : "bg-red-400"
                    )}
                  />
                  {config.enabled ? "Active" : "Disabled"}
                </span>
              </div>
              <p className="text-sm text-[#948BA3] mt-1">
                Customize the bot&apos;s instant response when tagged in chat, and track mention alerts in your server log channel.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 bg-white/[0.03] px-5 py-3 rounded-2xl border border-white/5 shadow-inner">
              <Label htmlFor="master-toggle" className="text-sm font-bold text-white cursor-pointer">
                {config.enabled ? "System Enabled" : "System Disabled"}
              </Label>
              <Switch
                id="master-toggle"
                checked={config.enabled}
                onCheckedChange={(val) => setConfig((prev) => ({ ...prev, enabled: val }))}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Config Settings on Left, Live Preview on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Form Column (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Section 1: Trigger Mode */}
          <div className="p-7 rounded-3xl bg-[#0D0B18]/90 border border-white/5 backdrop-blur-2xl shadow-xl space-y-6">
            <div className="flex items-center gap-3 pb-4 border-b border-white/5">
              <div className="p-2.5 rounded-xl bg-[#A855F7]/10 text-[#A855F7]">
                <Radio className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Trigger Detection Mode</h3>
                <p className="text-xs text-[#948BA3]">Choose when the bot will trigger its reply</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setConfig((prev) => ({ ...prev, trigger_type: "single" }))}
                className={cn(
                  "p-5 rounded-2xl border text-left transition-all relative overflow-hidden flex flex-col justify-between",
                  config.trigger_type === "single"
                    ? "border-[#A855F7] bg-[#A855F7]/10 shadow-lg shadow-[#A855F7]/10"
                    : "border-white/5 bg-white/[0.02] hover:bg-white/[0.04]"
                )}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold text-white">Solo Ping Only</span>
                    {config.trigger_type === "single" && (
                      <CheckCircle2 className="h-4 w-4 text-[#A855F7]" />
                    )}
                  </div>
                  <p className="text-xs text-[#948BA3] leading-relaxed">
                    Triggers only when a member sends a lone message mentioning the bot: e.g. <code className="text-[#A855F7] bg-[#A855F7]/10 px-1 rounded">@Aizen XFX</code>
                  </p>
                </div>
                <span className="text-[10px] uppercase font-bold text-[#A855F7] mt-4 tracking-wider">
                  Recommended • Cleanest
                </span>
              </button>

              <button
                type="button"
                onClick={() => setConfig((prev) => ({ ...prev, trigger_type: "any" }))}
                className={cn(
                  "p-5 rounded-2xl border text-left transition-all relative overflow-hidden flex flex-col justify-between",
                  config.trigger_type === "any"
                    ? "border-[#A855F7] bg-[#A855F7]/10 shadow-lg shadow-[#A855F7]/10"
                    : "border-white/5 bg-white/[0.02] hover:bg-white/[0.04]"
                )}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-bold text-white">Any Message Mention</span>
                    {config.trigger_type === "any" && (
                      <CheckCircle2 className="h-4 w-4 text-[#A855F7]" />
                    )}
                  </div>
                  <p className="text-xs text-[#948BA3] leading-relaxed">
                    Triggers whenever the bot is tagged anywhere in a conversation message.
                  </p>
                </div>
                <span className="text-[10px] uppercase font-bold text-[#948BA3] mt-4 tracking-wider">
                  Aggressive Mode
                </span>
              </button>
            </div>
          </div>

          {/* Section 2: Response Style */}
          <div className="p-7 rounded-3xl bg-[#0D0B18]/90 border border-white/5 backdrop-blur-2xl shadow-xl space-y-6">
            <div className="flex items-center gap-3 pb-4 border-b border-white/5">
              <div className="p-2.5 rounded-xl bg-[#A855F7]/10 text-[#A855F7]">
                <MessageSquare className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Response Type &amp; Content</h3>
                <p className="text-xs text-[#948BA3]">Select whether to use the interactive menu or a custom embed</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setConfig((prev) => ({ ...prev, response_type: "default" }))}
                className={cn(
                  "p-4 rounded-2xl border text-left transition-all",
                  config.response_type === "default"
                    ? "border-[#A855F7] bg-[#A855F7]/10 shadow-lg shadow-[#A855F7]/10"
                    : "border-white/5 bg-white/[0.02] hover:bg-white/[0.04]"
                )}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-bold text-white">Interactive Menu</span>
                  {config.response_type === "default" && (
                    <CheckCircle2 className="h-4 w-4 text-[#A855F7]" />
                  )}
                </div>
                <p className="text-xs text-[#948BA3]">
                  Built-in menu with dropdown options (Home, Developer Info, Invite &amp; Links).
                </p>
              </button>

              <button
                type="button"
                onClick={() => setConfig((prev) => ({ ...prev, response_type: "custom" }))}
                className={cn(
                  "p-4 rounded-2xl border text-left transition-all",
                  config.response_type === "custom"
                    ? "border-[#A855F7] bg-[#A855F7]/10 shadow-lg shadow-[#A855F7]/10"
                    : "border-white/5 bg-white/[0.02] hover:bg-white/[0.04]"
                )}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-bold text-white">Custom Embed</span>
                  {config.response_type === "custom" && (
                    <CheckCircle2 className="h-4 w-4 text-[#A855F7]" />
                  )}
                </div>
                <p className="text-xs text-[#948BA3]">
                  Your own personalized title, description, accent color, and custom banner image.
                </p>
              </button>
            </div>

            {/* Custom Content Editor (Only when custom is selected) */}
            {config.response_type === "custom" && (
              <div className="space-y-5 pt-4 border-t border-white/5 animate-in fade-in duration-300">
                <div className="space-y-2">
                  <Label className="text-xs font-bold uppercase tracking-wider text-[#948BA3]">
                    Embed Title (Optional)
                  </Label>
                  <Input
                    placeholder="e.g. Thanks for pinging Aizen XFX!"
                    value={config.custom_title || ""}
                    onChange={(e) => setConfig((prev) => ({ ...prev, custom_title: e.target.value }))}
                    className="bg-white/[0.03] border-white/10 text-white"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label className="text-xs font-bold uppercase tracking-wider text-[#948BA3]">
                      Message Description
                    </Label>
                    <div className="flex items-center gap-1.5">
                      {["{user}", "{user_name}", "{server}", "{prefix}"].map((v) => (
                        <button
                          key={v}
                          type="button"
                          onClick={() => insertVariable(v)}
                          className="px-2 py-0.5 rounded-md bg-[#A855F7]/10 hover:bg-[#A855F7]/20 text-[#A855F7] text-[10px] font-mono transition-colors"
                          title="Click to insert"
                        >
                          {v}
                        </button>
                      ))}
                    </div>
                  </div>
                  <Textarea
                    placeholder="Hey {user}! Prefix for {server} is `{prefix}`. Type `{prefix}help` to get started!"
                    rows={4}
                    value={config.custom_message || ""}
                    onChange={(e) => setConfig((prev) => ({ ...prev, custom_message: e.target.value }))}
                    className="bg-white/[0.03] border-white/10 text-white font-mono text-xs leading-relaxed"
                  />
                </div>

                {/* Color Palette Picker */}
                <div className="space-y-2">
                  <Label className="text-xs font-bold uppercase tracking-wider text-[#948BA3]">
                    Embed Accent Color
                  </Label>
                  <div className="flex flex-wrap items-center gap-3">
                    {PRESET_COLORS.map((color) => (
                      <button
                        key={color.value}
                        type="button"
                        onClick={() => setConfig((prev) => ({ ...prev, custom_color: color.value }))}
                        className={cn(
                          "h-8 px-3 rounded-xl text-xs font-bold flex items-center gap-2 border transition-transform",
                          config.custom_color?.toUpperCase() === color.value.toUpperCase()
                            ? "border-white scale-105 shadow-md shadow-black/40"
                            : "border-transparent opacity-80 hover:opacity-100"
                        )}
                        style={{ backgroundColor: `${color.value}25`, color: color.value }}
                      >
                        <span className="h-3 w-3 rounded-full" style={{ backgroundColor: color.value }} />
                        {color.name}
                      </button>
                    ))}
                    <div className="flex items-center gap-2 ml-auto">
                      <input
                        type="color"
                        value={config.custom_color || "#A855F7"}
                        onChange={(e) => setConfig((prev) => ({ ...prev, custom_color: e.target.value }))}
                        className="h-8 w-8 rounded-lg bg-transparent cursor-pointer border border-white/10"
                      />
                      <Input
                        value={config.custom_color || "#A855F7"}
                        onChange={(e) => setConfig((prev) => ({ ...prev, custom_color: e.target.value }))}
                        className="w-24 h-8 text-xs font-mono bg-white/[0.03] border-white/10 text-white"
                      />
                    </div>
                  </div>
                </div>

                {/* Optional Media */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <Label className="text-xs font-bold uppercase tracking-wider text-[#948BA3]">
                      Thumbnail URL (Optional)
                    </Label>
                    <Input
                      placeholder="https://i.imgur.com/thumbnail.png"
                      value={config.custom_thumbnail || ""}
                      onChange={(e) => setConfig((prev) => ({ ...prev, custom_thumbnail: e.target.value }))}
                      className="bg-white/[0.03] border-white/10 text-white text-xs"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label className="text-xs font-bold uppercase tracking-wider text-[#948BA3]">
                      Banner Image URL (Optional)
                    </Label>
                    <Input
                      placeholder="https://i.imgur.com/banner.png"
                      value={config.custom_image || ""}
                      onChange={(e) => setConfig((prev) => ({ ...prev, custom_image: e.target.value }))}
                      className="bg-white/[0.03] border-white/10 text-white text-xs"
                    />
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="space-y-2 pt-2">
                  <Label className="text-xs font-bold uppercase tracking-wider text-[#948BA3]">
                    Action Buttons on Response
                  </Label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="flex items-center justify-between p-3 rounded-xl bg-white/[0.02] border border-white/5">
                      <span className="text-xs font-medium text-slate-300">Show &apos;Invite Bot&apos; Button</span>
                      <Switch
                        checked={config.show_invite}
                        onCheckedChange={(val) => setConfig((prev) => ({ ...prev, show_invite: val }))}
                      />
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-xl bg-white/[0.02] border border-white/5">
                      <span className="text-xs font-medium text-slate-300">Show &apos;Support Server&apos; Button</span>
                      <Switch
                        checked={config.show_support}
                        onCheckedChange={(val) => setConfig((prev) => ({ ...prev, show_support: val }))}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Section 3: Auto-Delete & Anti-Spam */}
          <div className="p-7 rounded-3xl bg-[#0D0B18]/90 border border-white/5 backdrop-blur-2xl shadow-xl space-y-6">
            <div className="flex items-center gap-3 pb-4 border-b border-white/5">
              <div className="p-2.5 rounded-xl bg-[#A855F7]/10 text-[#A855F7]">
                <Clock className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Auto-Delete Delay</h3>
                <p className="text-xs text-[#948BA3]">Automatically delete the bot response to prevent channel clutter</p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <p className="text-sm font-semibold text-white">Delete Bot Response After</p>
                <p className="text-xs text-[#948BA3]">Keeps the channel clean during active conversations</p>
              </div>
              <Select
                value={String(config.auto_delete || 0)}
                onValueChange={(val) => setConfig((prev) => ({ ...prev, auto_delete: parseInt(val, 10) }))}
              >
                <SelectTrigger className="w-48 bg-white/[0.03] border-white/10 text-white">
                  <SelectValue placeholder="Select Delay" />
                </SelectTrigger>
                <SelectContent className="bg-[#141B2D] border-slate-800 text-white">
                  <SelectItem value="0">Never (Keep Permanently)</SelectItem>
                  <SelectItem value="5">5 Seconds</SelectItem>
                  <SelectItem value="10">10 Seconds</SelectItem>
                  <SelectItem value="15">15 Seconds</SelectItem>
                  <SelectItem value="30">30 Seconds</SelectItem>
                  <SelectItem value="60">60 Seconds (1 Min)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Section 4: Mention Alert & Logging Channel */}
          <div className="p-7 rounded-3xl bg-[#0D0B18]/90 border border-[#A855F7]/15 backdrop-blur-2xl shadow-xl space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-white/5">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-[#A855F7]/10 text-[#A855F7]">
                  <BellRing className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Mention Alert &amp; Audit Logging</h3>
                  <p className="text-xs text-[#948BA3]">Send an alert to an admin channel whenever the bot is tagged</p>
                </div>
              </div>
              <Switch
                checked={config.alert_enabled}
                onCheckedChange={(val) => setConfig((prev) => ({ ...prev, alert_enabled: val }))}
              />
            </div>

            {config.alert_enabled ? (
              <div className="space-y-4 animate-in fade-in duration-300">
                <div className="space-y-2">
                  <Label className="text-xs font-bold uppercase tracking-wider text-[#948BA3]">
                    Alert Destination Channel
                  </Label>
                  <Select
                    value={config.alert_channel_id || "none"}
                    onValueChange={(val) =>
                      setConfig((prev) => ({
                        ...prev,
                        alert_channel_id: val === "none" ? null : val,
                      }))
                    }
                  >
                    <SelectTrigger className="bg-white/[0.03] border-white/10 text-white">
                      <SelectValue placeholder="Select an Alert Channel" />
                    </SelectTrigger>
                    <SelectContent className="bg-[#141B2D] border-slate-800 text-white max-h-60">
                      <SelectItem value="none">None (Disabled)</SelectItem>
                      {textChannels.map((channel) => (
                        <SelectItem key={channel.id} value={channel.id}>
                          #{channel.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="p-4 rounded-2xl bg-[#A855F7]/5 border border-[#A855F7]/15 text-xs text-[#948BA3] space-y-2">
                  <p className="font-semibold text-white flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-[#A855F7]" />
                    What gets logged in the alert channel:
                  </p>
                  <ul className="list-disc list-inside space-y-1 pl-1 text-[11px]">
                    <li>User who mentioned the bot with ID &amp; Avatar</li>
                    <li>Channel where the mention occurred</li>
                    <li>Direct jump link to the triggering message</li>
                    <li>Timestamp and exact message snippet</li>
                  </ul>
                </div>
              </div>
            ) : (
              <p className="text-xs text-[#948BA3] italic">
                Enable Mention Alert Logging to have the bot automatically notify moderators whenever someone tags it.
              </p>
            )}
          </div>

          {/* Action Bar */}
          <div className="flex items-center justify-between pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={handleReset}
              disabled={saving}
              className="border-white/10 text-[#948BA3] hover:text-white hover:bg-white/5"
            >
              <RefreshCcw className="h-4 w-4 mr-2" />
              Reset Defaults
            </Button>

            <Button
              type="button"
              onClick={handleSave}
              disabled={saving}
              className="px-8 bg-gradient-to-r from-[#A855F7] to-[#9333EA] hover:from-[#9333EA] hover:to-[#7E22CE] text-white font-bold shadow-lg shadow-[#A855F7]/25"
            >
              {saving ? (
                <>
                  <RefreshCcw className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Right Preview Column (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="sticky top-[140px] space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-white font-bold text-sm">
                <Eye className="h-4 w-4 text-[#A855F7]" />
                Live Discord Message Preview
              </div>

              {config.alert_enabled && (
                <div className="flex rounded-xl bg-white/[0.03] p-1 border border-white/5 text-[11px]">
                  <button
                    type="button"
                    onClick={() => setPreviewMode("response")}
                    className={cn(
                      "px-2.5 py-1 rounded-lg font-bold transition-colors",
                      previewMode === "response"
                        ? "bg-[#A855F7] text-white shadow-md shadow-[#A855F7]/20"
                        : "text-[#948BA3] hover:text-white"
                    )}
                  >
                    Reply
                  </button>
                  <button
                    type="button"
                    onClick={() => setPreviewMode("alert")}
                    className={cn(
                      "px-2.5 py-1 rounded-lg font-bold transition-colors",
                      previewMode === "alert"
                        ? "bg-[#A855F7] text-white shadow-md shadow-[#A855F7]/20"
                        : "text-[#948BA3] hover:text-white"
                    )}
                  >
                    Alert Log
                  </button>
                </div>
              )}
            </div>

            {/* Realistic Discord Message Container */}
            <div className="rounded-3xl bg-[#313338] border border-white/10 p-5 shadow-2xl space-y-4 font-sans text-white select-none">
              {/* Trigger message simulate */}
              <div className="flex items-start gap-3 opacity-80 pb-3 border-b border-[#3F4147]">
                <div className="h-9 w-9 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold text-white shrink-0">
                  U
                </div>
                <div className="text-xs space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white">CommunityMember</span>
                    <span className="text-[10px] text-[#949BA4]">Today at 12:45 PM</span>
                  </div>
                  <p className="text-[#DBDEE1]">
                    <span className="bg-[#5865F2]/20 text-[#C9CDFB] px-1.5 py-0.5 rounded font-medium">
                      @Aizen XFX
                    </span>{" "}
                    {config.trigger_type === "any" ? "what is the prefix here?" : ""}
                  </p>
                </div>
              </div>

              {/* Bot Response Preview */}
              {previewMode === "response" ? (
                <div className="flex items-start gap-3 pt-1">
                  <div className="relative h-10 w-10 shrink-0">
                    <Image
                      src="/logo.png"
                      alt="Aizen XFX"
                      width={40}
                      height={40}
                      className="rounded-full shadow-md bg-purple-950/40"
                    />
                  </div>

                  <div className="flex-1 min-w-0 space-y-2 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-white hover:underline cursor-pointer">Aizen XFX</span>
                      <span className="bg-[#5865F2] text-white text-[9px] font-black uppercase px-1.5 py-0.2 rounded font-mono">
                        BOT
                      </span>
                      <span className="text-[10px] text-[#949BA4]">Today at 12:45 PM</span>
                    </div>

                    {/* Content type */}
                    {config.response_type === "default" ? (
                      /* Default Menu View */
                      <div className="space-y-3">
                        <div className="p-4 rounded-xl bg-[#2B2D31] border border-white/5 space-y-2 max-w-sm">
                          <p className="font-bold text-[#F2F3F5]">Server Dashboard</p>
                          <hr className="border-white/10" />
                          <p className="text-[#DBDEE1] text-[11px] leading-relaxed">
                            &gt; ❤️ **Hey @CommunityMember**<br />
                            &gt; ➔ **Prefix For This Server: `&gt;`**<br /><br />
                            <em className="text-[#949BA4]">Type `&gt;help` for more information.</em>
                          </p>
                        </div>

                        {/* Interactive Dropdown Preview */}
                        <div className="p-2.5 rounded-xl bg-[#2B2D31] border border-white/5 flex items-center justify-between text-[#949BA4] text-xs max-w-sm">
                          <span className="flex items-center gap-2 text-white">
                            <Bot className="h-4 w-4 text-[#A855F7]" />
                            Start With Aizen XFX
                          </span>
                          <span>▼</span>
                        </div>
                      </div>
                    ) : (
                      /* Custom Embed View */
                      <div
                        className="rounded-lg bg-[#2B2D31] p-4 space-y-3 max-w-sm relative overflow-hidden"
                        style={{ borderLeft: `4px solid ${config.custom_color || "#A855F7"}` }}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="space-y-1.5 flex-1 min-w-0">
                            {config.custom_title && (
                              <h4 className="font-bold text-sm text-white">{config.custom_title}</h4>
                            )}
                            <p className="text-[11px] text-[#DBDEE1] leading-relaxed whitespace-pre-wrap">
                              {(config.custom_message || "Hey {user}! Prefix for this server is `{prefix}`.")
                                .replace("{user}", "@CommunityMember")
                                .replace("{user_name}", "CommunityMember")
                                .replace("{server}", "Aizen Realm")
                                .replace("{prefix}", ">")}
                            </p>
                          </div>
                          {config.custom_thumbnail && (
                            <img
                              src={config.custom_thumbnail}
                              alt="Thumbnail"
                              className="h-12 w-12 rounded-lg object-cover shrink-0"
                            />
                          )}
                        </div>

                        {config.custom_image && (
                          <img
                            src={config.custom_image}
                            alt="Banner"
                            className="rounded-lg w-full max-h-36 object-cover"
                          />
                        )}

                        <p className="text-[9px] text-[#949BA4] pt-2 border-t border-white/5">
                          Powered by Aizen XFX™
                        </p>
                      </div>
                    )}

                    {/* Buttons Preview if Custom */}
                    {config.response_type === "custom" && (
                      <div className="flex flex-wrap gap-2 pt-1">
                        {config.show_invite && (
                          <div className="px-3 py-1.5 rounded bg-[#4E5058] hover:bg-[#6D6F78] text-white text-xs font-medium flex items-center gap-1.5 shadow">
                            Invite Aizen XFX
                            <ExternalLink className="h-3 w-3 opacity-60" />
                          </div>
                        )}
                        {config.show_support && (
                          <div className="px-3 py-1.5 rounded bg-[#4E5058] hover:bg-[#6D6F78] text-white text-xs font-medium flex items-center gap-1.5 shadow">
                            Support
                            <ExternalLink className="h-3 w-3 opacity-60" />
                          </div>
                        )}
                      </div>
                    )}

                    {config.auto_delete > 0 && (
                      <div className="flex items-center gap-1 text-[10px] text-[#F38688]">
                        <Clock className="h-3 w-3" />
                        Auto-deletes in {config.auto_delete} seconds
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                /* Mention Alert Preview */
                <div className="flex items-start gap-3 pt-1">
                  <div className="h-10 w-10 shrink-0">
                    <Image
                      src="/logo.png"
                      alt="Aizen XFX"
                      width={40}
                      height={40}
                      className="rounded-full shadow-md bg-purple-950/40"
                    />
                  </div>
                  <div className="flex-1 min-w-0 space-y-2 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-white">Aizen XFX</span>
                      <span className="bg-[#5865F2] text-white text-[9px] font-black uppercase px-1.5 py-0.2 rounded font-mono">
                        BOT
                      </span>
                      <span className="text-[10px] text-[#949BA4]">Today at 12:45 PM</span>
                    </div>

                    <div className="rounded-lg bg-[#2B2D31] p-4 space-y-2 max-w-sm border-l-4 border-[#A855F7]">
                      <h4 className="font-bold text-sm text-white flex items-center gap-1.5">
                        <BellRing className="h-4 w-4 text-[#A855F7]" />
                        Bot Mention Alert
                      </h4>
                      <div className="text-[11px] text-[#DBDEE1] space-y-1">
                        <p><strong>Mentioned By:</strong> @CommunityMember (`123456789`)</p>
                        <p><strong>Channel:</strong> #general</p>
                        <p><strong>Message Snippet:</strong></p>
                        <pre className="bg-[#1E1F22] p-2 rounded text-[10px] text-slate-300 font-mono">
                          @Aizen XFX what is the prefix here?
                        </pre>
                        <p className="text-[#A855F7] hover:underline cursor-pointer">
                          ➔ Jump to Message
                        </p>
                      </div>
                      <p className="text-[9px] text-[#949BA4] pt-1 border-t border-white/5">
                        Logged in #{textChannels.find((c) => c.id === config.alert_channel_id)?.name || "alerts"}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-xs text-[#948BA3] space-y-1.5">
              <p className="font-semibold text-white">💡 Pro Tip</p>
              <p className="text-[11px] leading-relaxed">
                Use Solo Ping Mode with an Auto-Delete timer of 15s to keep member channels clean while always providing fast help.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
