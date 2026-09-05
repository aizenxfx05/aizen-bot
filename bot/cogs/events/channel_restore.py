# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║        Aizen XFX — Channel Restore Module                       ║
# ║                                                                  ║
# ║   Automatically restores deleted text, voice, & stage channels. ║
# ║   Works INDEPENDENTLY of antinuke — no ban, just restore.       ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import os
import discord
import asyncio
import datetime
import logging
import pytz
import aiosqlite
from discord.ext import commands

logger = logging.getLogger("channel_restore")

# ── DB path (robust against any current working directory) ─────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(_BASE_DIR, "db", "anti.db")

# ── Rate-limit guard: max 5 restores per 10 seconds per guild ─────────────────
_RESTORE_MAX    = 5
_RESTORE_WINDOW = 10   # seconds


class ChannelRestore(commands.Cog):
    """
    Aizen XFX Channel Restore — independently restores deleted voice or text
    channels without requiring antinuke to be active, and WITHOUT banning.

    Commands:
        >restore enable   (or >channel restore enable)
        >restore disable  (or >channel restore disable)
        >restore status   (or >channel restore status)
        >restore logchannel #logs
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # { guild_id: [datetime, ...] }
        self._timestamps: dict[int, list] = {}

    async def cog_load(self):
        """Ensure database table exists when the cog is loaded."""
        await self._ensure_table()

    def help_custom(self):
        emoji = "🔄"
        label = "Channel Restore"
        description = "Auto-restores deleted text & voice channels"
        return emoji, label, description

    # ── DB helpers ─────────────────────────────────────────────────────────────

    async def _ensure_table(self):
        """Create the channel_restore table if it does not yet exist."""
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute(
                    """
                    CREATE TABLE IF NOT EXISTS channel_restore (
                        guild_id       INTEGER PRIMARY KEY,
                        status         INTEGER NOT NULL DEFAULT 0,
                        log_channel_id INTEGER
                    )
                    """
                )
                await db.commit()
        except Exception as e:
            logger.error(f"[ChannelRestore] Error creating table in {DB_PATH}: {e}")

    async def _is_enabled(self, guild_id: int) -> bool:
        await self._ensure_table()
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute(
                    "SELECT status FROM channel_restore WHERE guild_id = ?", (guild_id,)
                ) as cur:
                    row = await cur.fetchone()
            return bool(row and row[0])
        except Exception as e:
            logger.error(f"[ChannelRestore] Error checking status: {e}")
            return False

    async def _get_log_channel_id(self, guild_id: int):
        await self._ensure_table()
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute(
                    "SELECT log_channel_id FROM channel_restore WHERE guild_id = ?", (guild_id,)
                ) as cur:
                    row = await cur.fetchone()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"[ChannelRestore] Error getting log channel: {e}")
            return None

    # ── Rate-limit guard ───────────────────────────────────────────────────────

    def _within_rate_limit(self, guild_id: int) -> bool:
        now = datetime.datetime.now()
        ts = self._timestamps.setdefault(guild_id, [])
        ts.append(now)
        # Drop old timestamps outside the window
        self._timestamps[guild_id] = [
            t for t in ts if (now - t).total_seconds() <= _RESTORE_WINDOW
        ]
        return len(self._timestamps[guild_id]) <= _RESTORE_MAX

    # ── Audit log ──────────────────────────────────────────────────────────────

    async def _get_executor(self, guild: discord.Guild, channel_id: int):
        """Returns the audit log executor who deleted the channel, or None."""
        try:
            if not guild.me.guild_permissions.view_audit_log:
                return None
            async for entry in guild.audit_logs(
                action=discord.AuditLogAction.channel_delete, limit=5
            ):
                if entry.target and entry.target.id == channel_id:
                    age = (datetime.datetime.now(pytz.utc) - entry.created_at).total_seconds()
                    if age < 15:
                        return entry.user
        except Exception as e:
            logger.warning(f"[ChannelRestore] Audit log check failed: {e}")
        return None

    async def _is_antinuke_active(self, guild_id: int) -> bool:
        """Check if antinuke is enabled for the guild."""
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute("SELECT status FROM antinuke WHERE guild_id = ?", (guild_id,)) as cur:
                    row = await cur.fetchone()
                return bool(row and row[0])
        except Exception:
            return False

    async def _is_whitelisted_or_owner(self, guild: discord.Guild, user_id: int) -> bool:
        """Check if a user is guild owner, extra owner, or whitelisted for channel deletion."""
        if user_id == guild.owner_id:
            return True
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute(
                    "SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?",
                    (guild.id, user_id),
                ) as cur:
                    if await cur.fetchone():
                        return True
                async with db.execute(
                    "SELECT chdl FROM whitelisted_users WHERE guild_id = ? AND user_id = ?",
                    (guild.id, user_id),
                ) as cur:
                    row = await cur.fetchone()
                    if row and row[0]:
                        return True
        except Exception:
            pass
        return False

    # ── Core restore logic ─────────────────────────────────────────────────────

    async def _restore_channel(self, channel: discord.abc.GuildChannel, executor):
        """Clone the deleted channel back into its original position with fallback."""
        guild = channel.guild
        if not guild.me.guild_permissions.manage_channels:
            logger.warning(f"[ChannelRestore] Bot lacks manage_channels permission in {guild.name} ({guild.id})")
            return None

        executor_str = str(executor) if executor else "Unknown"
        reason = f"Aizen XFX Channel Restore — deleted by {executor_str}"
        new_channel = None

        # Determine if category still exists in guild
        cat = None
        if getattr(channel, "category_id", None):
            cat = guild.get_channel(channel.category_id)
            if not cat:
                # If category was deleted, clear category_id so clone() doesn't send invalid parent_id
                try:
                    channel.category_id = None
                except Exception:
                    pass

        # Attempt 1: Standard clone with category safeguard
        try:
            new_channel = await channel.clone(
                name=channel.name,
                category=cat,
                reason=reason
            )
        except Exception as e:
            logger.warning(f"[ChannelRestore] channel.clone() failed ({e}), attempting recreation fallback...")

        # Attempt 2: Fallback manual channel creation if clone failed
        if not new_channel:
            overwrites = getattr(channel, "overwrites", None)
            try:
                if isinstance(channel, discord.TextChannel):
                    try:
                        new_channel = await guild.create_text_channel(
                            name=channel.name,
                            category=cat,
                            topic=channel.topic,
                            slowmode_delay=channel.slowmode_delay,
                            nsfw=channel.nsfw,
                            overwrites=overwrites,
                            reason=reason
                        )
                    except Exception:
                        new_channel = await guild.create_text_channel(
                            name=channel.name,
                            category=cat,
                            topic=channel.topic,
                            slowmode_delay=channel.slowmode_delay,
                            nsfw=channel.nsfw,
                            reason=reason
                        )
                elif isinstance(channel, discord.VoiceChannel):
                    try:
                        new_channel = await guild.create_voice_channel(
                            name=channel.name,
                            category=cat,
                            bitrate=min(channel.bitrate, guild.bitrate_limit),
                            user_limit=channel.user_limit,
                            overwrites=overwrites,
                            reason=reason
                        )
                    except Exception:
                        new_channel = await guild.create_voice_channel(
                            name=channel.name,
                            category=cat,
                            bitrate=min(channel.bitrate, guild.bitrate_limit),
                            user_limit=channel.user_limit,
                            reason=reason
                        )
                elif isinstance(channel, discord.StageChannel):
                    try:
                        new_channel = await guild.create_stage_channel(
                            name=channel.name,
                            category=cat,
                            topic=channel.topic,
                            overwrites=overwrites,
                            reason=reason
                        )
                    except Exception:
                        new_channel = await guild.create_stage_channel(
                            name=channel.name,
                            category=cat,
                            topic=channel.topic,
                            reason=reason
                        )
            except Exception as e2:
                logger.error(f"[ChannelRestore] Fallback creation failed: {e2}")
                return None

        # Position restore (safe - never fails the restoration)
        if new_channel and hasattr(channel, "position"):
            try:
                await new_channel.edit(position=channel.position)
            except Exception:
                pass

        return new_channel

    async def _send_log(self, guild: discord.Guild, channel, executor, new_channel):
        """Send a restore log embed to the guild log channel if configured."""
        log_ch_id = await self._get_log_channel_id(guild.id)
        if not log_ch_id:
            return
        log_ch = guild.get_channel(log_ch_id)
        if not log_ch:
            return
        try:
            embed = discord.Embed(
                title="🔄 Channel Restored",
                color=0xD4AF37,  # Gold — Aizen XFX brand
                timestamp=discord.utils.utcnow(),
            )
            ch_type = "Voice" if isinstance(channel, discord.VoiceChannel) else "Text"
            embed.add_field(name="Original Channel", value=f"`#{channel.name}`", inline=True)
            embed.add_field(name="Type", value=ch_type, inline=True)
            embed.add_field(name="Restored As", value=new_channel.mention if new_channel else "Failed", inline=True)
            embed.add_field(name="Deleted By", value=f"{executor.mention} (`{executor.id}`)" if executor else "Unknown (Audit log delayed)", inline=False)
            embed.set_footer(text="Aizen XFX — Channel Restore System")
            await log_ch.send(embed=embed)
        except Exception as e:
            logger.warning(f"[ChannelRestore] Failed to send log: {e}")

    # ── Event Listener ─────────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        guild = getattr(channel, "guild", None)
        if not guild:
            return

        # Only handle text, voice, and stage channels
        if not isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.StageChannel)):
            return

        # Check if the restore feature is enabled for this guild
        if not await self._is_enabled(guild.id):
            return

        # Prevent duplicate recreation if channel was already restored
        now = datetime.datetime.now()
        global_restored = getattr(self.bot, "_restored_channel_ids", {})
        if channel.id in global_restored and (now - global_restored[channel.id]).total_seconds() < 30:
            return

        # Rate-limit guard
        if not self._within_rate_limit(guild.id):
            logger.warning(f"[ChannelRestore] Rate limit reached for guild {guild.id}.")
            return

        # Wait briefly for Discord audit log propagation and allow Antinuke to handle nuke attacks first
        await asyncio.sleep(1.0)

        # Check again if Antinuke or another listener already restored this channel
        global_restored = getattr(self.bot, "_restored_channel_ids", {})
        if channel.id in global_restored and (now - global_restored[channel.id]).total_seconds() < 30:
            return

        # Get executor from audit log
        executor = await self._get_executor(guild, channel.id)

        # Only skip if the bot itself deleted the channel to avoid infinite recreation loops
        if executor and executor.id == self.bot.user.id:
            return

        # If Antinuke is active AND executor is an unwhitelisted attacker:
        # Antinuke (antichdl) is responsible for banning and restoring.
        # But if executor is owner, extra-owner, whitelisted, or Antinuke is disabled,
        # Antinuke does NOT restore the channel, so ChannelRestore MUST restore it!
        if executor and await self._is_antinuke_active(guild.id):
            is_authorized = await self._is_whitelisted_or_owner(guild, executor.id)
            if not is_authorized:
                return

        # Mark channel ID as restored to prevent duplicate concurrent executions
        if not hasattr(self.bot, "_restored_channel_ids"):
            self.bot._restored_channel_ids = {}
        self.bot._restored_channel_ids[channel.id] = now

        # Restore the channel
        new_channel = await self._restore_channel(channel, executor)

        # Send log if successful
        if new_channel:
            await self._send_log(guild, channel, executor, new_channel)

    # ── Primary Command Group (>restore, >channelrestore, >cr) ────────────────

    @commands.group(
        name="restore",
        aliases=["channelrestore", "channel-restore", "channel_restore", "cr"],
        invoke_without_command=True
    )
    @commands.has_permissions(administrator=True)
    async def restore_group(self, ctx: commands.Context, *, sub: str = None):
        """Manage the Aizen XFX Channel Restore feature."""
        if sub:
            sub_lower = sub.strip().lower()
            parts = sub.strip().split()
            if parts[0].lower() in ["server", "guild"]:
                autorestore_cmd = self.bot.get_command("autorestore")
                if autorestore_cmd:
                    sub_args = " ".join(parts[1:]) if len(parts) > 1 else None
                    await ctx.invoke(autorestore_cmd, sub=sub_args)
                    return
            if sub_lower in ["enable", "on", "true", "start", "1"]:
                await self.restore_enable(ctx)
                return
            elif sub_lower in ["disable", "off", "false", "stop", "0"]:
                await self.restore_disable(ctx)
                return
            elif sub_lower in ["status", "check", "info"]:
                await self.restore_status(ctx)
                return

        enabled = await self._is_enabled(ctx.guild.id)
        status_badge = "🟢 **Enabled**" if enabled else "🔴 **Disabled**"
        log_ch_id = await self._get_log_channel_id(ctx.guild.id)
        log_str = f"<#{log_ch_id}>" if log_ch_id else "*Not configured*"

        embed = discord.Embed(
            title="🔄 Aizen XFX — Channel Restore",
            description=(
                "Automatically restores any deleted text or voice channel without requiring Antinuke.\n\n"
                f"• **Status:** {status_badge}\n"
                f"• **Log Channel:** {log_str}\n\n"
                "__**Commands:**__\n"
                f"`{ctx.prefix}restore enable` (or `on`) — Enable automatic channel restoration\n"
                f"`{ctx.prefix}restore disable` (or `off`) — Disable automatic channel restoration\n"
                f"`{ctx.prefix}restore status` — Check current configuration status\n"
                f"`{ctx.prefix}restore logchannel <#channel>` — Set channel for restore alerts\n\n"
                f"*Tip: You can also use `{ctx.prefix}channelrestore` or `{ctx.prefix}channel restore`.*"
            ),
            color=0xD4AF37 if enabled else 0x5865F2,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(
            text=f"Requested by {ctx.author.display_name} • Aizen XFX",
            icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else None
        )
        await ctx.send(embed=embed)

    @restore_group.command(name="enable", aliases=["on"])
    @commands.has_permissions(administrator=True)
    async def restore_enable(self, ctx: commands.Context):
        """Enable automatic channel restore for this server."""
        await self._ensure_table()
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO channel_restore (guild_id, status)
                VALUES (?, 1)
                ON CONFLICT(guild_id) DO UPDATE SET status = 1
                """,
                (ctx.guild.id,),
            )
            await db.commit()
        embed = discord.Embed(
            title="✅ Channel Restore Enabled",
            description=(
                "**Aizen XFX** will now automatically restore any deleted text, voice, or stage channels.\n\n"
                "ℹ️ **Testing & Usage Notes:**\n"
                "• Channels deleted by **anyone** (including owner & admins) will be restored automatically.\n"
                "• Requires the bot's **Manage Channels** and **View Audit Log** permissions.\n"
                "• To permanently delete a channel without restoration, use `>restore disable` first."
            ),
            color=0x2ECC71,
        )
        embed.set_footer(text="Aizen XFX — Channel Restore System")
        await ctx.send(embed=embed)

    @restore_group.command(name="disable", aliases=["off"])
    @commands.has_permissions(administrator=True)
    async def restore_disable(self, ctx: commands.Context):
        """Disable automatic channel restore for this server."""
        await self._ensure_table()
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE channel_restore SET status = 0 WHERE guild_id = ?",
                (ctx.guild.id,),
            )
            await db.commit()
        embed = discord.Embed(
            title="🔴 Channel Restore Disabled",
            description="Automatic channel restoration is now **disabled** for this server. Deleted channels will not be recreated.",
            color=0xED4245,
        )
        embed.set_footer(text="Aizen XFX — Channel Restore System")
        await ctx.send(embed=embed)

    @restore_group.command(name="status", aliases=["info"])
    @commands.has_permissions(manage_guild=True)
    async def restore_status(self, ctx: commands.Context):
        """Check if channel restore is enabled for this server."""
        enabled = await self._is_enabled(ctx.guild.id)
        log_ch_id = await self._get_log_channel_id(ctx.guild.id)
        status_str = "🟢 **Enabled**" if enabled else "🔴 **Disabled**"
        log_str = f"<#{log_ch_id}>" if log_ch_id else "*Not configured*"
        color = 0x2ECC71 if enabled else 0xED4245
        has_perm = ctx.guild.me.guild_permissions.manage_channels
        embed = discord.Embed(
            title="Channel Restore Status",
            description=(
                f"• **Status:** {status_str}\n"
                f"• **Log Channel:** {log_str}\n"
                f"• **Manage Channels Permission:** {'✅ Yes' if has_perm else '❌ Missing!'}"
            ),
            color=color,
        )
        embed.set_footer(text="Aizen XFX — Channel Restore System")
        await ctx.send(embed=embed)

    @restore_group.command(name="logchannel", aliases=["log", "logs"])
    @commands.has_permissions(administrator=True)
    async def restore_logchannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the channel where restore logs are sent."""
        await self._ensure_table()
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO channel_restore (guild_id, status, log_channel_id)
                VALUES (?, 1, ?)
                ON CONFLICT(guild_id) DO UPDATE SET log_channel_id = ?
                """,
                (ctx.guild.id, channel.id, channel.id),
            )
            await db.commit()
        embed = discord.Embed(
            title="Channel Restore Log Set",
            description=f"Channel restoration alerts will now be sent to {channel.mention}.",
            color=0xD4AF37,
        )
        embed.set_footer(text="Aizen XFX — Channel Restore System")
        await ctx.send(embed=embed)

    # ── Channel namespace group (>channel restore ...) ────────────────────────

    @commands.group(name="channel", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def channel_cmd(self, ctx: commands.Context, *, sub: str = None):
        """Channel commands group."""
        await self.restore_group(ctx, sub=sub)

    @channel_cmd.group(name="restore", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def channel_restore_cmd(self, ctx: commands.Context, *, sub: str = None):
        """Channel restore command under channel namespace."""
        await self.restore_group(ctx, sub=sub)

    @channel_restore_cmd.command(name="enable", aliases=["on"])
    @commands.has_permissions(administrator=True)
    async def channel_restore_enable_sub(self, ctx: commands.Context):
        await self.restore_enable(ctx)

    @channel_restore_cmd.command(name="disable", aliases=["off"])
    @commands.has_permissions(administrator=True)
    async def channel_restore_disable_sub(self, ctx: commands.Context):
        await self.restore_disable(ctx)

    @channel_restore_cmd.command(name="status")
    @commands.has_permissions(manage_guild=True)
    async def channel_restore_status_sub(self, ctx: commands.Context):
        await self.restore_status(ctx)

    @channel_restore_cmd.command(name="logchannel", aliases=["log", "logs"])
    @commands.has_permissions(administrator=True)
    async def channel_restore_logchannel_sub(self, ctx: commands.Context, channel: discord.TextChannel):
        await self.restore_logchannel(ctx, channel)


async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelRestore(bot))
