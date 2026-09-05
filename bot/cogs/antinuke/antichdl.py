# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║   ░█▀█░▀█▀░▀▀█░█▀▀░█▀█   ░█░█░█▀▀░█░█                         ║
# ║   ░█▀█░░█░░▄▀░░█▀▀░█░█   ░▄▀▄░█▀▀░▄▀▄                         ║
# ║   ░▀░▀░▀▀▀░█▄▄░▀▀▀░▀░▀   ░▀░▀░▀░░░▀░▀                         ║
# ║                                                                  ║
# ║            © 2026 Aizen XFX — All Rights Reserved               ║
# ║                                                                  ║
# ║   discord  ──  https://discord.gg/M8qJ9W7vBb                    ║
# ║   youtube  ──  https://youtube.com/@aizen_xfx                   ║
# ║   github   ──  https://github.com/aizenxfx05                    ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import discord
from discord.ext import commands
import aiosqlite
import asyncio
import datetime
import pytz

class AntiChannelDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_limits = {}
        self.cooldowns = {}
        self._restoring_channels = set()
        self._restored_channels = {}

        if not hasattr(self.bot, "_restored_channel_ids"):
            self.bot._restored_channel_ids = {}

    def _is_recently_restored(self, channel_id: int) -> bool:
        now = datetime.datetime.now()
        # Clean records older than 30s
        self._restored_channels = {
            cid: ts for cid, ts in self._restored_channels.items()
            if (now - ts).total_seconds() < 30
        }
        global_restored = getattr(self.bot, "_restored_channel_ids", {})
        if channel_id in global_restored:
            if (now - global_restored[channel_id]).total_seconds() < 30:
                return True
        return channel_id in self._restoring_channels or channel_id in self._restored_channels

    def _mark_restored(self, channel_id: int):
        now = datetime.datetime.now()
        self._restored_channels[channel_id] = now
        if not hasattr(self.bot, "_restored_channel_ids"):
            self.bot._restored_channel_ids = {}
        self.bot._restored_channel_ids[channel_id] = now

    def can_fetch_audit(self, guild_id, event_name, max_requests=5, interval=10, cooldown_duration=300):
        now = datetime.datetime.now()
        self.event_limits.setdefault(guild_id, {}).setdefault(event_name, []).append(now)

        timestamps = self.event_limits[guild_id][event_name]
        timestamps = [t for t in timestamps if (now - t).total_seconds() <= interval]
        self.event_limits[guild_id][event_name] = timestamps

        if guild_id in self.cooldowns and event_name in self.cooldowns[guild_id]:
            if (now - self.cooldowns[guild_id][event_name]).total_seconds() < cooldown_duration:
                return False
            del self.cooldowns[guild_id][event_name]

        if len(timestamps) > max_requests:
            self.cooldowns.setdefault(guild_id, {})[event_name] = now
            return False
        return True

    async def fetch_audit_logs(self, guild, action, target_id):
        if not guild.me.guild_permissions.ban_members:
            return None
        try:
            async for entry in guild.audit_logs(action=action, limit=1):
                if entry.target.id == target_id:
                    now = datetime.datetime.now(pytz.utc)
                    if (now - entry.created_at).total_seconds() * 1000 >= 3600000:
                        return None
                    return entry
        except Exception:
            pass
        return None

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild

        # Prevent duplicate handling if channel is already being restored or was recently restored
        if self._is_recently_restored(channel.id):
            return

        async with aiosqlite.connect('db/anti.db') as db:
            async with db.execute("SELECT status FROM antinuke WHERE guild_id = ?", (guild.id,)) as cursor:
                antinuke_status = await cursor.fetchone()
            if not antinuke_status or not antinuke_status[0]:
                return

            if not self.can_fetch_audit(guild.id, "channel_delete"):
                return

            logs = await self.fetch_audit_logs(guild, discord.AuditLogAction.channel_delete, channel.id)
            if logs is None:
                return

            executor = logs.user
            if executor.id in {guild.owner_id, self.bot.user.id}:
                return

            async with db.execute("SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?", (guild.id, executor.id)) as cursor:
                if await cursor.fetchone():
                    return

            async with db.execute("SELECT chdl FROM whitelisted_users WHERE guild_id = ? AND user_id = ?", (guild.id, executor.id)) as cursor:
                whitelist_status = await cursor.fetchone()
            if whitelist_status and whitelist_status[0]:
                return

            self._restoring_channels.add(channel.id)
            try:
                await self.recreate_channel_and_ban(channel, executor)
                self._mark_restored(channel.id)
            finally:
                self._restoring_channels.discard(channel.id)

            await asyncio.sleep(3)

    async def recreate_channel_and_ban(self, channel, executor, retries=3):
        # 1. Clone the channel EXACTLY ONCE (do not loop clone on position edit rate limits)
        new_channel = None
        while retries > 0 and not new_channel:
            try:
                new_channel = await channel.clone(reason="Channel Delete | Unwhitelisted User")
                break
            except discord.Forbidden:
                return
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.response.headers.get('Retry-After', 1.0))
                    await asyncio.sleep(retry_after)
                    retries -= 1
                else:
                    break
            except Exception:
                return

        # 2. Position restore in an isolated block (never re-clones channel if position edit is 429'd)
        if new_channel and hasattr(channel, "position"):
            try:
                await new_channel.edit(position=channel.position)
            except Exception:
                pass

        # 3. Ban executor
        ban_retries = 3
        while ban_retries > 0:
            try:
                await channel.guild.ban(executor, reason="Channel Delete | Unwhitelisted User")
                return
            except discord.Forbidden:
                return
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.response.headers.get('Retry-After', 1.0))
                    await asyncio.sleep(retry_after)
                    ban_retries -= 1
                else:
                    break
            except Exception:
                return
