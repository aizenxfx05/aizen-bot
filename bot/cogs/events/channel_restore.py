# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║        Aizen XFX — Channel Restore Module                       ║
# ║                                                                  ║
# ║   Automatically restores deleted text/voice channels.           ║
# ║   Works INDEPENDENTLY of antinuke — no ban, just restore.       ║
# ║   Respects guild owner, bot, and extra-owner exemptions.        ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import discord
import asyncio
import datetime
import pytz
import aiosqlite
from discord.ext import commands

# ── DB path ───────────────────────────────────────────────────────────────────
DB_PATH = "db/anti.db"

# ── Rate-limit guard: max 5 restores per 10 seconds per guild ─────────────────
_RESTORE_MAX    = 5
_RESTORE_WINDOW = 10   # seconds


class ChannelRestore(commands.Cog):
    """
    Aizen XFX Channel Restore — independently restores deleted voice or text
    channels without requiring antinuke to be active, and WITHOUT banning.

    How to enable per-guild:
        The cog checks the `channel_restore` table in anti.db.
        If no row exists the feature is OFF by default.

    Commands:
        >restore enable   — enable channel restore for this server
        >restore disable  — disable channel restore for this server
        >restore status   — show current restore status
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # { guild_id: [datetime, ...] }
        self._timestamps: dict[int, list] = {}

    # ── DB helpers ─────────────────────────────────────────────────────────────

    async def _ensure_table(self):
        """Create the channel_restore table if it does not yet exist."""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS channel_restore (
                    guild_id      INTEGER PRIMARY KEY,
                    status        INTEGER NOT NULL DEFAULT 0,
                    log_channel_id INTEGER
                )
                """
            )
            await db.commit()

    async def _is_enabled(self, guild_id: int) -> bool:
        await self._ensure_table()
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT status FROM channel_restore WHERE guild_id = ?", (guild_id,)
            ) as cur:
                row = await cur.fetchone()
        return bool(row and row[0])

    async def _get_log_channel_id(self, guild_id: int):
        await self._ensure_table()
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT log_channel_id FROM channel_restore WHERE guild_id = ?", (guild_id,)
            ) as cur:
                row = await cur.fetchone()
        return row[0] if row else None

    async def _is_extra_owner(self, guild_id: int, user_id: int) -> bool:
        """Check if user is in the extra owners list (reuse antinuke DB)."""
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute(
                    "SELECT owner_id FROM extraowners WHERE guild_id = ? AND owner_id = ?",
                    (guild_id, user_id),
                ) as cur:
                    return await cur.fetchone() is not None
        except Exception:
            return False

    async def _is_whitelisted(self, guild_id: int, user_id: int) -> bool:
        """Check if user is whitelisted for channel delete in antinuke DB."""
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                async with db.execute(
                    "SELECT chdl FROM whitelisted_users WHERE guild_id = ? AND user_id = ?",
                    (guild_id, user_id),
                ) as cur:
                    row = await cur.fetchone()
            return bool(row and row[0])
        except Exception:
            return False

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
                action=discord.AuditLogAction.channel_delete, limit=3
            ):
                if entry.target and entry.target.id == channel_id:
                    age = (datetime.datetime.now(pytz.utc) - entry.created_at).total_seconds()
                    if age < 10:
                        return entry.user
        except Exception:
            pass
        return None

    # ── Core restore logic ─────────────────────────────────────────────────────

    async def _restore_channel(self, channel: discord.abc.GuildChannel, executor):
        """Clone the deleted channel back into its original position."""
        retries = 3
        new_channel = None
        while retries > 0:
            try:
                new_channel = await channel.clone(
                    reason=f"Aizen XFX Channel Restore — deleted by {executor}"
                )
                await new_channel.edit(position=channel.position)
                break
            except discord.Forbidden:
                return None
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = e.response.headers.get("Retry-After", 1)
                    await asyncio.sleep(float(retry_after))
                    retries -= 1
                else:
                    return None
            except Exception:
                return None
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
                title="Channel Restored",
                color=0xD4AF37,  # Gold — Aizen XFX brand
                timestamp=discord.utils.utcnow(),
            )
            ch_type = "Voice" if isinstance(channel, discord.VoiceChannel) else "Text"
            embed.add_field(name="Original Channel", value=f"`#{channel.name}`", inline=True)
            embed.add_field(name="Type", value=ch_type, inline=True)
            embed.add_field(name="Restored As", value=new_channel.mention if new_channel else "Failed", inline=True)
            embed.add_field(name="Deleted By", value=f"{executor.mention} (`{executor.id}`)" if executor else "Unknown", inline=False)
            embed.set_footer(text="Aizen XFX — Channel Restore System")
            await log_ch.send(embed=embed)
        except Exception:
            pass

    # ── Event Listener ─────────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        guild = channel.guild

        # Only handle text and voice channels
        if not isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.StageChannel)):
            return

        # Check if the restore feature is enabled for this guild
        if not await self._is_enabled(guild.id):
            return

        # Rate-limit guard
        if not self._within_rate_limit(guild.id):
            return

        # Get executor from audit log
        executor = await self._get_executor(guild, channel.id)

        # If the executor is the bot itself, guild owner, or a whitelisted/extra owner — skip
        if executor:
            if executor.id == self.bot.user.id:
                return
            if executor.id == guild.owner_id:
                return
            if await self._is_extra_owner(guild.id, executor.id):
                return
            if await self._is_whitelisted(guild.id, executor.id):
                return

        # Small delay to let Discord settle before cloning
        await asyncio.sleep(1)

        # Restore the channel
        new_channel = await self._restore_channel(channel, executor)

        # Send log
        await self._send_log(guild, channel, executor, new_channel)

    # ── Commands ───────────────────────────────────────────────────────────────

    @commands.group(name="restore", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def restore_group(self, ctx: commands.Context):
        """Manage the Aizen XFX Channel Restore feature."""
        await ctx.send_help(ctx.command)

    @restore_group.command(name="enable")
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
            title="Channel Restore Enabled",
            description=(
                "**Aizen XFX** will now automatically restore any deleted text or voice channel.\n\n"
                "The bot's **Manage Channels** permission is required for this to work."
            ),
            color=0xD4AF37,
        )
        embed.set_footer(text="Aizen XFX — Channel Restore System")
        await ctx.send(embed=embed)

    @restore_group.command(name="disable")
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
        await ctx.send("Channel Restore has been **disabled** for this server.")

    @restore_group.command(name="status")
    @commands.has_permissions(manage_guild=True)
    async def restore_status(self, ctx: commands.Context):
        """Check if channel restore is enabled for this server."""
        enabled = await self._is_enabled(ctx.guild.id)
        status_str = "**Enabled**" if enabled else "**Disabled**"
        color = 0xD4AF37 if enabled else 0x444444
        embed = discord.Embed(
            title="Channel Restore Status",
            description=f"Channel Restore is currently {status_str} on this server.",
            color=color,
        )
        embed.set_footer(text="Aizen XFX — Channel Restore System")
        await ctx.send(embed=embed)

    @restore_group.command(name="logchannel")
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
        await ctx.send(f"Restore logs will now be sent to {channel.mention}.")


async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelRestore(bot))
