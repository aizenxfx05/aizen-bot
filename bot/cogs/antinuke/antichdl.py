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

        if not hasattr(self.bot, "_channel_restore_in_progress"):
            self.bot._channel_restore_in_progress = set()
        if not hasattr(self.bot, "_channel_restored_recently"):
            self.bot._channel_restored_recently = {}

    def _is_channel_in_progress_or_restored(self, channel: discord.abc.GuildChannel) -> bool:
        guild = getattr(channel, "guild", None)
        if not guild:
            return True

        now = datetime.datetime.now()
        channel_id = channel.id
        raw_name = getattr(channel, "name", "").strip().lower()
        name_key = (guild.id, raw_name) if raw_name else None

        if not hasattr(self.bot, "_channel_restore_in_progress"):
            self.bot._channel_restore_in_progress = set()
        if not hasattr(self.bot, "_channel_restored_recently"):
            self.bot._channel_restored_recently = {}

        # Clean entries older than 60s
        self.bot._channel_restored_recently = {
            k: ts for k, ts in self.bot._channel_restored_recently.items()
            if (now - ts).total_seconds() < 60
        }

        # 1. Check in-progress lock across all cogs
        if channel_id in self.bot._channel_restore_in_progress:
            return True
        if name_key and name_key in self.bot._channel_restore_in_progress:
            return True

        # 2. Check recently restored cache across all cogs
        if channel_id in self.bot._channel_restored_recently:
            return True
        if name_key and name_key in self.bot._channel_restored_recently:
            return True

        # 3. Check if guild ALREADY has a channel of this type and name created in last 45s
        now_utc = discord.utils.utcnow()
        for existing in guild.channels:
            if isinstance(existing, type(channel)) and existing.name.strip().lower() == raw_name:
                if (now_utc - existing.created_at).total_seconds() < 45:
                    return True

        return False

    def _acquire_restore_lock(self, channel: discord.abc.GuildChannel):
        guild = getattr(channel, "guild", None)
        if not guild:
            return
        now = datetime.datetime.now()
        channel_id = channel.id
        raw_name = getattr(channel, "name", "").strip().lower()
        name_key = (guild.id, raw_name) if raw_name else None

        if not hasattr(self.bot, "_channel_restore_in_progress"):
            self.bot._channel_restore_in_progress = set()
        if not hasattr(self.bot, "_channel_restored_recently"):
            self.bot._channel_restored_recently = {}

        self.bot._channel_restore_in_progress.add(channel_id)
        self.bot._channel_restored_recently[channel_id] = now
        if name_key:
            self.bot._channel_restore_in_progress.add(name_key)
            self.bot._channel_restored_recently[name_key] = now

    def _release_restore_lock(self, channel: discord.abc.GuildChannel):
        channel_id = channel.id
        raw_name = getattr(channel, "name", "").strip().lower()
        name_key = (channel.guild.id, raw_name) if getattr(channel, "guild", None) and raw_name else None

        if hasattr(self.bot, "_channel_restore_in_progress"):
            self.bot._channel_restore_in_progress.discard(channel_id)
            if name_key:
                self.bot._channel_restore_in_progress.discard(name_key)

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
            async for entry in guild.audit_logs(action=action, limit=5):
                if entry.target and entry.target.id == target_id:
                    now = datetime.datetime.now(pytz.utc)
                    if (now - entry.created_at).total_seconds() * 1000 >= 3600000:
                        return None
                    return entry
        except Exception:
            pass
        return None

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = getattr(channel, "guild", None)
        if not guild:
            return

        # Check in-progress lock, recently restored cache, and guild sibling channels
        if self._is_channel_in_progress_or_restored(channel):
            return

        # Acquire lock immediately so concurrent events or cogs cannot double-restore
        self._acquire_restore_lock(channel)

        try:
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

                await self.recreate_channel_and_ban(channel, executor)
        finally:
            self._release_restore_lock(channel)

    async def recreate_channel_and_ban(self, channel, executor):
        guild = channel.guild

        # Category safeguard: If category was deleted, clear category_id so Discord API doesn't error
        cat = None
        if getattr(channel, "category_id", None):
            cat = guild.get_channel(channel.category_id)
            if not cat:
                try:
                    channel.category_id = None
                except Exception:
                    pass

        # Check once more if channel with same name and type was already created in last 45s
        now_utc = discord.utils.utcnow()
        raw_name = getattr(channel, "name", "").strip().lower()
        for existing in guild.channels:
            if isinstance(existing, type(channel)) and existing.name.strip().lower() == raw_name:
                if (now_utc - existing.created_at).total_seconds() < 45:
                    return

        # 1. Clone the channel EXACTLY ONCE (with fallback if clone fails)
        new_channel = None
        try:
            new_channel = await channel.clone(
                name=channel.name,
                category=cat,
                reason="Channel Delete | Unwhitelisted User"
            )
        except Exception:
            pass

        # Fallback creation if clone was rejected
        if not new_channel:
            overwrites = getattr(channel, "overwrites", None)
            reason = "Channel Delete | Unwhitelisted User"
            try:
                if isinstance(channel, discord.TextChannel):
                    new_channel = await guild.create_text_channel(
                        name=channel.name,
                        category=cat,
                        topic=getattr(channel, "topic", None),
                        slowmode_delay=getattr(channel, "slowmode_delay", 0),
                        nsfw=getattr(channel, "nsfw", False),
                        overwrites=overwrites,
                        reason=reason
                    )
                elif isinstance(channel, discord.VoiceChannel):
                    new_channel = await guild.create_voice_channel(
                        name=channel.name,
                        category=cat,
                        bitrate=min(channel.bitrate, guild.bitrate_limit),
                        user_limit=getattr(channel, "user_limit", 0),
                        overwrites=overwrites,
                        reason=reason
                    )
                elif isinstance(channel, discord.StageChannel):
                    new_channel = await guild.create_stage_channel(
                        name=channel.name,
                        category=cat,
                        topic=getattr(channel, "topic", None),
                        overwrites=overwrites,
                        reason=reason
                    )
            except Exception:
                pass

        # 2. Position restore in an isolated block (never re-clones channel if position edit is 429'd)
        if new_channel and hasattr(channel, "position"):
            try:
                await new_channel.edit(position=channel.position)
            except Exception:
                pass

        # 3. Ban executor (single try / rate limit retry without touching channel)
        ban_retries = 3
        while ban_retries > 0:
            try:
                await guild.ban(executor, reason="Channel Delete | Unwhitelisted User")
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
