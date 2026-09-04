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

import os
import json
import secrets
import datetime
import logging
import asyncio
import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ui import View, Button

from core import Context, Cog
from utils.config import THEME_COLOR, BotName, serverLink

logger = logging.getLogger("backup")

# ── DB path (robust against any CWD) ──────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(_BASE_DIR, "db", "backup.db")


class BackupConfirmView(View):
    def __init__(self, author: discord.Member, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.author = author
        self.value = None

    @discord.ui.button(label="Confirm Restore", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("You are not authorized to confirm this.", ephemeral=True)
        self.value = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("You are not authorized to cancel this.", ephemeral=True)
        self.value = False
        self.stop()
        await interaction.response.defer()


class Backup(Cog):
    """
    Aizen XFX 1-Click Server Backup & Automatic Disaster Recovery System
    Allows guild owners to snapshot and automatically restore roles, channels, and structure.
    """

    def __init__(self, bot):
        self.bot = bot
        # Mass deletion guard: { guild_id: [datetime, ...] }
        self._recent_deletions: dict[int, list[datetime.datetime]] = {}
        # Ongoing restoration lock: set of guild_ids currently restoring
        self._is_restoring: set[int] = set()

    async def cog_load(self):
        await self._ensure_tables()
        if not self.auto_snapshot_loop.is_running():
            self.auto_snapshot_loop.start()

    def cog_unload(self):
        if self.auto_snapshot_loop.is_running():
            self.auto_snapshot_loop.cancel()

    def help_custom(self):
        emoji = "💾"
        label = "Server Backup & Auto-Restore"
        description = "1-Click snapshots & automatic disaster recovery protection"
        return emoji, label, description

    # ── Database Helpers ───────────────────────────────────────────────────────

    async def _ensure_tables(self):
        """Create tables for backups and auto-restore configuration."""
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS backups (
                        backup_id   TEXT PRIMARY KEY,
                        guild_id    INTEGER NOT NULL,
                        guild_name  TEXT NOT NULL,
                        created_by  INTEGER NOT NULL,
                        created_at  TEXT NOT NULL,
                        data        TEXT NOT NULL
                    )
                """)
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS auto_restore_config (
                        guild_id            INTEGER PRIMARY KEY,
                        status              INTEGER NOT NULL DEFAULT 0,
                        latest_backup_id    TEXT,
                        last_snapshot       TEXT,
                        log_channel_id      INTEGER,
                        auto_nuke_recovery  INTEGER NOT NULL DEFAULT 1
                    )
                """)
                await db.commit()
        except Exception as e:
            logger.error(f"[Backup] Failed to ensure database tables: {e}")

    async def _get_auto_config(self, guild_id: int) -> dict:
        """Fetch auto-restore configuration for a guild."""
        await self._ensure_tables()
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM auto_restore_config WHERE guild_id = ?", (guild_id,)
                ) as cur:
                    row = await cur.fetchone()
            return dict(row) if row else {}
        except Exception as e:
            logger.error(f"[Backup] Error fetching auto_restore_config: {e}")
            return {}

    async def _create_snapshot_data(self, guild: discord.Guild, creator_id: int) -> str:
        """Captures a snapshot of the guild and stores it in the database. Returns backup_id."""
        roles_data = []
        for role in reversed(guild.roles):
            if role.is_default():
                continue
            roles_data.append({
                "name": role.name,
                "permissions": role.permissions.value,
                "color": role.color.value,
                "hoist": role.hoist,
                "mentionable": role.mentionable
            })

        categories_data = []
        for cat in guild.categories:
            categories_data.append({
                "name": cat.name,
                "position": cat.position
            })

        channels_data = []
        for ch in guild.text_channels:
            channels_data.append({
                "type": "text",
                "name": ch.name,
                "position": ch.position,
                "topic": ch.topic,
                "slowmode_delay": ch.slowmode_delay,
                "nsfw": ch.nsfw,
                "category": ch.category.name if ch.category else None
            })

        for vc in guild.voice_channels:
            channels_data.append({
                "type": "voice",
                "name": vc.name,
                "position": vc.position,
                "bitrate": vc.bitrate,
                "user_limit": vc.user_limit,
                "category": vc.category.name if vc.category else None
            })

        now_utc = datetime.datetime.utcnow()
        now_str = now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")

        snapshot = {
            "guild_name": guild.name,
            "guild_id": guild.id,
            "roles": roles_data,
            "categories": categories_data,
            "channels": channels_data,
            "timestamp": now_utc.isoformat()
        }

        backup_id = f"ax-{secrets.token_hex(4)}"

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO backups (backup_id, guild_id, guild_name, created_by, created_at, data) VALUES (?, ?, ?, ?, ?, ?)",
                (backup_id, guild.id, guild.name, creator_id, now_str, json.dumps(snapshot))
            )
            # Update auto_restore_config latest snapshot reference
            await db.execute(
                """
                INSERT INTO auto_restore_config (guild_id, latest_backup_id, last_snapshot)
                VALUES (?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                    latest_backup_id = excluded.latest_backup_id,
                    last_snapshot = excluded.last_snapshot
                """,
                (guild.id, backup_id, now_str)
            )
            await db.commit()

        return backup_id

    async def _restore_from_snapshot(self, guild: discord.Guild, backup_id: str, reason: str = "Aizen XFX Server Restore") -> dict:
        """Restores missing roles, categories, and channels from a snapshot. Returns stats dictionary."""
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT data FROM backups WHERE backup_id = ?", (backup_id,)) as cursor:
                row = await cursor.fetchone()

        if not row:
            return {"error": "Snapshot not found"}

        snapshot = json.loads(row[0])
        roles_created = 0
        cats_created = 0
        channels_created = 0

        # 1. Recreate missing roles
        existing_roles = {r.name.lower(): r for r in guild.roles}
        for r_data in snapshot.get("roles", []):
            if r_data["name"].lower() not in existing_roles:
                try:
                    await guild.create_role(
                        name=r_data["name"],
                        permissions=discord.Permissions(r_data.get("permissions", 0)),
                        color=discord.Color(r_data.get("color", 0)),
                        hoist=r_data.get("hoist", False),
                        mentionable=r_data.get("mentionable", False),
                        reason=f"{reason} | Role Recovery"
                    )
                    roles_created += 1
                    await asyncio.sleep(0.15)
                except Exception as e:
                    logger.warning(f"[Restore] Failed to recreate role {r_data.get('name')}: {e}")

        # 2. Recreate missing categories
        cat_map = {}
        for cat_data in snapshot.get("categories", []):
            cat = discord.utils.get(guild.categories, name=cat_data["name"])
            if not cat:
                try:
                    cat = await guild.create_category(
                        name=cat_data["name"],
                        position=cat_data.get("position", 0),
                        reason=f"{reason} | Category Recovery"
                    )
                    cats_created += 1
                    await asyncio.sleep(0.15)
                except Exception as e:
                    logger.warning(f"[Restore] Failed to recreate category {cat_data.get('name')}: {e}")
            if cat:
                cat_map[cat_data["name"]] = cat

        # 3. Recreate missing channels
        for ch_data in snapshot.get("channels", []):
            parent_cat = cat_map.get(ch_data.get("category"))
            if ch_data["type"] == "text":
                exists = discord.utils.get(guild.text_channels, name=ch_data["name"])
                if not exists:
                    try:
                        await guild.create_text_channel(
                            name=ch_data["name"],
                            category=parent_cat,
                            topic=ch_data.get("topic"),
                            slowmode_delay=ch_data.get("slowmode_delay", 0),
                            nsfw=ch_data.get("nsfw", False),
                            reason=f"{reason} | Channel Recovery"
                        )
                        channels_created += 1
                        await asyncio.sleep(0.15)
                    except Exception as e:
                        logger.warning(f"[Restore] Failed to recreate text channel {ch_data.get('name')}: {e}")
            elif ch_data["type"] == "voice":
                exists = discord.utils.get(guild.voice_channels, name=ch_data["name"])
                if not exists:
                    try:
                        await guild.create_voice_channel(
                            name=ch_data["name"],
                            category=parent_cat,
                            bitrate=min(ch_data.get("bitrate", 64000), guild.bitrate_limit),
                            user_limit=ch_data.get("user_limit", 0),
                            reason=f"{reason} | Channel Recovery"
                        )
                        channels_created += 1
                        await asyncio.sleep(0.15)
                    except Exception as e:
                        logger.warning(f"[Restore] Failed to recreate voice channel {ch_data.get('name')}: {e}")

        return {
            "roles": roles_created,
            "categories": cats_created,
            "channels": channels_created
        }

    # ── Background Auto-Snapshot Task ──────────────────────────────────────────

    @tasks.loop(hours=12)
    async def auto_snapshot_loop(self):
      """Periodically captures fresh snapshots for servers with auto-restore enabled."""
      await self.bot.wait_until_ready()
      try:
        async with aiosqlite.connect(DB_PATH) as db:
          async with db.execute(
              "SELECT guild_id FROM auto_restore_config WHERE status = 1"
          ) as cursor:
            rows = await cursor.fetchall()
        for (guild_id,) in rows:
          guild = self.bot.get_guild(guild_id)
          if guild:
            try:
              backup_id = await self._create_snapshot_data(
                  guild, self.bot.user.id
              )
              logger.info(
                  f"[AutoRestore] 12h periodic snapshot saved for {guild.name}:"
                  f" {backup_id}"
              )
            except Exception as ge:
              logger.warning(
                  f"[AutoRestore] Failed periodic snapshot for {guild_id}: {ge}"
              )
      except Exception as e:
        logger.error(f"[AutoRestore] Error in auto_snapshot_loop: {e}")

    @auto_snapshot_loop.before_loop
    async def before_auto_snapshot_loop(self):
      await self.bot.wait_until_ready()

    # ── Mass-Destruction Disaster Recovery Listeners ───────────────────────────

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
      guild = channel.guild
      await self._check_mass_damage(guild, "channel")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
      guild = role.guild
      await self._check_mass_damage(guild, "role")

    async def _check_mass_damage(self, guild: discord.Guild, item_type: str):
      """Detects rapid mass-deletions (nuke/raid attack) and triggers automatic disaster recovery."""
      config = await self._get_auto_config(guild.id)
      if not config or not config.get("status"):
        return
      if not config.get("auto_nuke_recovery", 1):
        return
      if guild.id in self._is_restoring:
        return

      now = datetime.datetime.now()
      ts_list = self._recent_deletions.setdefault(guild.id, [])
      ts_list.append(now)

      # 15 second sliding window
      self._recent_deletions[guild.id] = [
          t for t in ts_list if (now - t).total_seconds() <= 15
      ]

      # Threshold: 3+ deletions within 15 seconds triggers automatic disaster recovery
      if len(self._recent_deletions[guild.id]) >= 3:
        self._recent_deletions[guild.id] = []
        backup_id = config.get("latest_backup_id")
        if not backup_id:
          return

        self._is_restoring.add(guild.id)
        try:
          logger.warning(
              f"[AutoRestore] 🚨 Mass deletion detected in {guild.name} ({guild.id})! Triggering automatic restore..."
          )
          # Brief pause for destructive batch to conclude
          await asyncio.sleep(2.0)
          stats = await self._restore_from_snapshot(
              guild,
              backup_id,
              reason="Aizen XFX Auto-Restore: Mass Damage Detected",
          )

          # Send emergency notification
          log_ch_id = config.get("log_channel_id")
          target_ch = (
              guild.get_channel(log_ch_id)
              if log_ch_id
              else (guild.system_channel or guild.text_channels[0])
          )
          if target_ch:
            embed = discord.Embed(
                title="🚨 Automatic Server Disaster Recovery Triggered",
                description=(
                    f"**Mass server destruction was detected!**\n\n"
                    f"**Aizen XFX** Automatic Disaster Recovery has automatically restored missing layout elements from master snapshot `{backup_id}`.\n\n"
                    f"• **Roles Recovered:** `{stats.get('roles', 0)}`\n"
                    f"• **Categories Recovered:** `{stats.get('categories', 0)}`\n"
                    f"• **Channels Recovered:** `{stats.get('channels', 0)}`\n\n"
                    f"🛡️ *Your server structure has been safeguarded.*"
                ),
                color=0xED4245,
                timestamp=discord.utils.utcnow(),
            )
            embed.set_footer(text="Aizen XFX Disaster Recovery Engine")
            try:
              await target_ch.send(embed=embed)
            except Exception:
              pass
        finally:
          self._is_restoring.discard(guild.id)

    # ── Primary Backup Group (>backup, >serverbackup, >sb) ─────────────────────

    @commands.group(
        name="backup",
        aliases=["serverbackup", "server-backup", "server_backup", "sb"],
        invoke_without_command=True
    )
    @commands.has_permissions(administrator=True)
    async def backup_group(self, ctx: Context, *, sub: str = None):
        """Aizen XFX Backup & Auto-Restore command hub."""
        if sub:
            parts = sub.strip().split()
            cmd = parts[0].lower()
            if cmd in ["create", "new", "make", "save"]:
                await self.backup_create(ctx)
                return
            elif cmd in ["list", "all", "show"]:
                await self.backup_list(ctx)
                return
            elif cmd in ["load", "restore", "apply"] and len(parts) > 1:
                await self.backup_load(ctx, parts[1])
                return
            elif cmd in ["info", "view", "details"] and len(parts) > 1:
                await self.backup_info(ctx, parts[1])
                return
            elif cmd in ["delete", "del", "remove"] and len(parts) > 1:
                await self.backup_delete(ctx, parts[1])
                return
            elif cmd in ["autorestore", "auto-restore", "autobackup", "auto"]:
                await self.autorestore_cmd(ctx)
                return

        auto_cfg = await self._get_auto_config(ctx.guild.id)
        auto_status = "🟢 **Active**" if auto_cfg.get("status") else "🔴 **Inactive**"
        latest_id = auto_cfg.get("latest_backup_id", "*None*")

        embed = discord.Embed(
            title=f"💾 {BotName} Server Backup & Auto-Restore",
            description=(
                "**1-Click Server Snapshot & Automatic Disaster Recovery**\n\n"
                f"• **Automatic Server Restore Protection:** {auto_status}\n"
                f"• **Active Master Snapshot:** `{latest_id}`\n\n"
                "__**Manual Backup Commands:**__\n"
                f"`{ctx.prefix}backup create` — Create a fresh server snapshot\n"
                f"`{ctx.prefix}backup list` — View all saved server snapshots\n"
                f"`{ctx.prefix}backup info <id>` — View detailed snapshot contents & stats\n"
                f"`{ctx.prefix}backup load <id>` — Restore a saved snapshot with confirmation\n"
                f"`{ctx.prefix}backup delete <id>` — Delete a saved snapshot\n\n"
                "__**Automatic Restore Commands:**__\n"
                f"`{ctx.prefix}autorestore enable` — Enable 24/7 automatic disaster recovery\n"
                f"`{ctx.prefix}autorestore disable` — Disable automatic recovery\n"
                f"`{ctx.prefix}autorestore restore` — Immediately restore server from master snapshot\n"
                f"`{ctx.prefix}autorestore sync` — Update master snapshot right now\n"
                f"`{ctx.prefix}autorestore status` — View automatic recovery details"
            ),
            color=THEME_COLOR,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"{BotName} Security • Requested by {ctx.author.display_name}")
        await ctx.reply(embed=embed, mention_author=False)

    @backup_group.command(name="create", aliases=["new", "make", "save"])
    @commands.has_permissions(administrator=True)
    async def backup_create(self, ctx: Context):
        """Creates a snapshot of the current server's roles, channels, and structure."""
        progress_msg = await ctx.reply("🟣 *Capturing server state (roles, categories, channels)...*", mention_author=False)
        backup_id = await self._create_snapshot_data(ctx.guild, ctx.author.id)

        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT data FROM backups WHERE backup_id = ?", (backup_id,)) as cursor:
                row = await cursor.fetchone()
        snapshot = json.loads(row[0])

        embed = discord.Embed(
            title="🟣 Server Snapshot Created",
            description=f"Snapshot successfully saved with ID: `{backup_id}`",
            color=THEME_COLOR
        )
        embed.add_field(name="Roles Saved", value=f"`{len(snapshot.get('roles', []))}` roles", inline=True)
        embed.add_field(name="Categories", value=f"`{len(snapshot.get('categories', []))}` categories", inline=True)
        embed.add_field(name="Channels", value=f"`{len(snapshot.get('channels', []))}` channels", inline=True)
        embed.add_field(name="Restore Command", value=f"`{ctx.prefix}backup load {backup_id}`", inline=False)
        embed.set_footer(text=f"Created by {ctx.author} • Keep your ID private")

        await progress_msg.edit(content=None, embed=embed)

    @backup_group.command(name="list", aliases=["all", "show"])
    @commands.has_permissions(administrator=True)
    async def backup_list(self, ctx: Context):
        """Lists all snapshots created for this server."""
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT backup_id, created_at, created_by FROM backups WHERE guild_id = ? ORDER BY created_at DESC LIMIT 10", (ctx.guild.id,)) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            return await ctx.reply("No backups found for this server. Use `>backup create` to create one.", mention_author=False)

        embed = discord.Embed(title=f"🟣 Saved Snapshots for {ctx.guild.name}", color=THEME_COLOR)
        lines = []
        for r in rows:
            lines.append(f"`{r[0]}` — Created on `{r[1]}` by <@{r[2]}>")
        embed.description = "\n".join(lines)
        embed.set_footer(text=f"Use {ctx.prefix}backup load <id> to restore a snapshot.")
        await ctx.reply(embed=embed, mention_author=False)

    @backup_group.command(name="info", aliases=["view", "details"])
    @commands.has_permissions(administrator=True)
    async def backup_info(self, ctx: Context, backup_id: str):
        """View detailed snapshot contents and statistics."""
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT data, guild_name, created_at, created_by FROM backups WHERE backup_id = ?", (backup_id,)) as cursor:
                row = await cursor.fetchone()

        if not row:
            return await ctx.reply(f"❌ Backup with ID `{backup_id}` was not found.", mention_author=False)

        snapshot = json.loads(row[0])
        roles = snapshot.get("roles", [])
        categories = snapshot.get("categories", [])
        channels = snapshot.get("channels", [])
        text_count = sum(1 for c in channels if c.get("type") == "text")
        voice_count = sum(1 for c in channels if c.get("type") == "voice")

        embed = discord.Embed(
            title=f"💾 Snapshot Details: `{backup_id}`",
            description=(
                f"• **Source Server:** {row[1]}\n"
                f"• **Created:** `{row[2]}`\n"
                f"• **Created By:** <@{row[3]}>"
            ),
            color=THEME_COLOR
        )
        embed.add_field(name="🎭 Roles Saved", value=f"`{len(roles)}` roles", inline=True)
        embed.add_field(name="📁 Categories", value=f"`{len(categories)}` categories", inline=True)
        embed.add_field(name="📺 Channels", value=f"`{len(channels)}` total (`{text_count}` text, `{voice_count}` voice)", inline=True)

        if roles:
            role_sample = ", ".join(f"`@{r['name']}`" for r in roles[:6])
            if len(roles) > 6:
                role_sample += f" *(+{len(roles)-6} more)*"
            embed.add_field(name="Sample Roles", value=role_sample, inline=False)

        if channels:
            channel_sample = ", ".join(f"`#{c['name']}`" for c in channels[:6])
            if len(channels) > 6:
                channel_sample += f" *(+{len(channels)-6} more)*"
            embed.add_field(name="Sample Channels", value=channel_sample, inline=False)

        embed.add_field(name="Restore Command", value=f"`{ctx.prefix}backup load {backup_id}`", inline=False)
        embed.set_footer(text=f"{BotName} Backup Engine", icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
        await ctx.reply(embed=embed, mention_author=False)

    @backup_group.command(name="load", aliases=["restore", "apply"])
    @commands.has_permissions(administrator=True)
    async def backup_load(self, ctx: Context, backup_id: str):
        """Restores a server snapshot with confirmation."""
        guild = ctx.guild
        missing_perms = []
        if not guild.me.guild_permissions.manage_roles:
            missing_perms.append("Manage Roles")
        if not guild.me.guild_permissions.manage_channels:
            missing_perms.append("Manage Channels")

        if missing_perms:
            return await ctx.reply(
                f"❌ The bot is missing required permissions to restore: **{', '.join(missing_perms)}**.\n"
                "Please grant these permissions and ensure the bot role is positioned high in Server Settings > Roles.",
                mention_author=False
            )

        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT data, guild_name FROM backups WHERE backup_id = ?", (backup_id,)) as cursor:
                row = await cursor.fetchone()

        if not row:
            return await ctx.reply(f"❌ Backup with ID `{backup_id}` was not found.", mention_author=False)

        snapshot = json.loads(row[0])
        view = BackupConfirmView(ctx.author)

        warning_embed = discord.Embed(
            title="⚠️ Confirm Snapshot Restoration",
            description=(
                f"You are about to restore snapshot `{backup_id}` (`{row[1]}`).\n\n"
                f"**This will recreate:**\n"
                f"• `{len(snapshot.get('roles', []))}` Roles\n"
                f"• `{len(snapshot.get('categories', []))}` Categories\n"
                f"• `{len(snapshot.get('channels', []))}` Channels\n\n"
                f"Click **Confirm Restore** to proceed or **Cancel** to abort."
            ),
            color=0xFBBF24
        )
        msg = await ctx.reply(embed=warning_embed, view=view, mention_author=False)
        await view.wait()

        if not view.value:
            return await msg.edit(content="Restoration cancelled.", embed=None, view=None)

        status_embed = discord.Embed(title="🟣 Restoring Snapshot...", description="Recreating missing roles, categories, and channels, please wait...", color=THEME_COLOR)
        await msg.edit(embed=status_embed, view=None)

        stats = await self._restore_from_snapshot(guild, backup_id, reason=f"Manual Snapshot Restore: {backup_id}")

        done_embed = discord.Embed(
            title="✅ Snapshot Restoration Complete",
            description=(
                f"Snapshot `{backup_id}` has been successfully applied to **{guild.name}**.\n\n"
                f"• Roles Recreated: `{stats.get('roles', 0)}`\n"
                f"• Categories Recreated: `{stats.get('categories', 0)}`\n"
                f"• Channels Recreated: `{stats.get('channels', 0)}`"
            ),
            color=THEME_COLOR
        )
        await msg.edit(embed=done_embed)

    @backup_group.command(name="delete", aliases=["del", "remove"])
    @commands.has_permissions(administrator=True)
    async def backup_delete(self, ctx: Context, backup_id: str):
        """Deletes a saved snapshot."""
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("DELETE FROM backups WHERE backup_id = ? AND guild_id = ?", (backup_id, ctx.guild.id))
            await db.commit()
            rows_affected = cursor.rowcount

        if rows_affected > 0:
            await ctx.reply(f"✅ Snapshot `{backup_id}` deleted successfully.", mention_author=False)
        else:
            await ctx.reply(f"❌ Snapshot `{backup_id}` not found for this guild.", mention_author=False)

    # ── Automatic Server Restore Group (>autorestore, >auto-restore) ───────────

    @commands.group(
        name="autorestore",
        aliases=["auto-restore", "autobackup", "auto_restore"],
        invoke_without_command=True
    )
    @commands.has_permissions(administrator=True)
    async def autorestore_cmd(self, ctx: Context, *, sub: str = None):
        """Automatic server restore command hub."""
        if sub:
            parts = sub.strip().split()
            cmd = parts[0].lower()
            if cmd in ["enable", "on", "true", "start", "1"]:
                await self.autorestore_enable(ctx)
                return
            elif cmd in ["disable", "off", "false", "stop", "0"]:
                await self.autorestore_disable(ctx)
                return
            elif cmd in ["status", "info", "check"]:
                await self.autorestore_status(ctx)
                return
            elif cmd in ["sync", "snapshot", "update"]:
                await self.autorestore_sync(ctx)
                return
            elif cmd in ["restore", "run", "now", "trigger"]:
                await self.autorestore_run(ctx)
                return
            elif cmd in ["logchannel", "log", "logs"] and len(parts) > 1:
                # Try to parse channel
                try:
                    ch = await commands.TextChannelConverter().convert(ctx, parts[1])
                    await self.autorestore_logchannel(ctx, ch)
                    return
                except Exception:
                    pass

        config = await self._get_auto_config(ctx.guild.id)
        is_enabled = bool(config.get("status"))
        status_str = "🟢 **Enabled (Protected)**" if is_enabled else "🔴 **Disabled**"
        latest_id = config.get("latest_backup_id", "*None*")
        last_snap = config.get("last_snapshot", "*Never*")
        log_ch_id = config.get("log_channel_id")
        log_str = f"<#{log_ch_id}>" if log_ch_id else "*Not configured*"

        embed = discord.Embed(
            title="🛡️ Automatic Server Restore Protection",
            description=(
                "**24/7 Server Layout Auto-Recovery & Disaster Protection**\n\n"
                f"• **Status:** {status_str}\n"
                f"• **Master Snapshot ID:** `{latest_id}`\n"
                f"• **Last Auto-Snapshot:** `{last_snap}`\n"
                f"• **Alert Channel:** {log_str}\n\n"
                "__**Features Included:**__\n"
                "• **Auto-Recovery on Nuke:** If rapid mass-deletions occur, missing roles and channels are immediately restored.\n"
                "• **12h Periodic Snapshot:** A fresh master snapshot is automatically maintained in the background.\n"
                "• **1-Click Restore:** Instantly restore all missing elements anytime with `>autorestore restore`.\n\n"
                "__**Commands:**__\n"
                f"`{ctx.prefix}autorestore enable` (or `on`) — Turn on automatic restore protection\n"
                f"`{ctx.prefix}autorestore disable` (or `off`) — Turn off automatic restore protection\n"
                f"`{ctx.prefix}autorestore restore` — 1-click restore from latest master snapshot\n"
                f"`{ctx.prefix}autorestore sync` — Update the master snapshot right now\n"
                f"`{ctx.prefix}autorestore status` — Check current protection status\n"
                f"`{ctx.prefix}autorestore logchannel <#channel>` — Set channel for restore alerts"
            ),
            color=0x2ECC71 if is_enabled else 0x5865F2,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=f"{BotName} Disaster Recovery Engine", icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)
        await ctx.reply(embed=embed, mention_author=False)

    @autorestore_cmd.command(name="enable", aliases=["on"])
    @commands.has_permissions(administrator=True)
    async def autorestore_enable(self, ctx: Context):
        """Enable automatic server restore protection."""
        progress_msg = await ctx.reply("🟣 *Enabling Automatic Server Restore and creating baseline master snapshot...*", mention_author=False)

        # 1. Create fresh baseline snapshot
        backup_id = await self._create_snapshot_data(ctx.guild, ctx.author.id)

        # 2. Update config status = 1
        now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO auto_restore_config (guild_id, status, latest_backup_id, last_snapshot)
                VALUES (?, 1, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                    status = 1,
                    latest_backup_id = excluded.latest_backup_id,
                    last_snapshot = excluded.last_snapshot
                """,
                (ctx.guild.id, backup_id, now_str)
            )
            await db.commit()

        embed = discord.Embed(
            title="🛡️ Automatic Server Restore Enabled",
            description=(
                "**Aizen XFX Automatic Disaster Recovery is now ACTIVE!**\n\n"
                f"• **Baseline Master Snapshot:** `{backup_id}`\n"
                "• **Auto-Recovery on Nuke:** Active (automatically restores missing channels & roles if mass deletions occur)\n"
                "• **12h Auto-Snapshot:** Active (automatically saves fresh daily backups)\n"
                f"• **1-Click Restore:** You can restore missing elements anytime using `{ctx.prefix}autorestore restore`."
            ),
            color=0x2ECC71,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Aizen XFX Disaster Recovery Engine")
        await progress_msg.edit(content=None, embed=embed)

    @autorestore_cmd.command(name="disable", aliases=["off"])
    @commands.has_permissions(administrator=True)
    async def autorestore_disable(self, ctx: Context):
        """Disable automatic server restore protection."""
        await self._ensure_tables()
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE auto_restore_config SET status = 0 WHERE guild_id = ?",
                (ctx.guild.id,)
            )
            await db.commit()

        embed = discord.Embed(
            title="🔴 Automatic Server Restore Disabled",
            description="Automatic server restoration and disaster recovery have been **disabled** for this server.",
            color=0xED4245
        )
        embed.set_footer(text="Aizen XFX Disaster Recovery Engine")
        await ctx.reply(embed=embed, mention_author=False)

    @autorestore_cmd.command(name="status", aliases=["info", "check"])
    @commands.has_permissions(manage_guild=True)
    async def autorestore_status(self, ctx: Context):
        """Check automatic server restore status."""
        config = await self._get_auto_config(ctx.guild.id)
        is_enabled = bool(config.get("status"))
        status_str = "🟢 **Active & Protected**" if is_enabled else "🔴 **Disabled**"
        latest_id = config.get("latest_backup_id", "*None*")
        last_snap = config.get("last_snapshot", "*Never*")
        log_ch_id = config.get("log_channel_id")
        log_str = f"<#{log_ch_id}>" if log_ch_id else "*Not configured*"

        has_roles_perm = ctx.guild.me.guild_permissions.manage_roles
        has_ch_perm = ctx.guild.me.guild_permissions.manage_channels

        embed = discord.Embed(
            title="Automatic Server Restore Status",
            description=(
                f"• **Protection Status:** {status_str}\n"
                f"• **Master Snapshot ID:** `{latest_id}`\n"
                f"• **Last Snapshot Taken:** `{last_snap}`\n"
                f"• **Alert Channel:** {log_str}\n\n"
                "__**Bot Health:**__\n"
                f"• Manage Roles: {'✅ Yes' if has_roles_perm else '❌ Missing'}\n"
                f"• Manage Channels: {'✅ Yes' if has_ch_perm else '❌ Missing'}"
            ),
            color=0x2ECC71 if is_enabled else 0xED4245
        )
        embed.set_footer(text="Aizen XFX Disaster Recovery Engine")
        await ctx.reply(embed=embed, mention_author=False)

    @autorestore_cmd.command(name="sync", aliases=["snapshot", "update"])
    @commands.has_permissions(administrator=True)
    async def autorestore_sync(self, ctx: Context):
        """Immediately captures a fresh master snapshot for auto-restore."""
        progress_msg = await ctx.reply("🟣 *Synchronizing master server snapshot...*", mention_author=False)
        backup_id = await self._create_snapshot_data(ctx.guild, ctx.author.id)

        embed = discord.Embed(
            title="✅ Master Snapshot Synchronized",
            description=f"Fresh baseline snapshot captured and saved as master: `{backup_id}`",
            color=0x2ECC71
        )
        embed.set_footer(text="Aizen XFX Disaster Recovery Engine")
        await progress_msg.edit(content=None, embed=embed)

    @autorestore_cmd.command(name="restore", aliases=["run", "now", "trigger"])
    @commands.has_permissions(administrator=True)
    async def autorestore_run(self, ctx: Context):
        """1-Click manual trigger to restore missing server elements from master snapshot."""
        config = await self._get_auto_config(ctx.guild.id)
        backup_id = config.get("latest_backup_id")

        if not backup_id:
            return await ctx.reply(
                "❌ No master snapshot found for this server. Use `>autorestore sync` or `>autorestore enable` first.",
                mention_author=False
            )

        progress_msg = await ctx.reply(f"🟣 *Restoring missing server elements from master snapshot `{backup_id}`...*", mention_author=False)
        stats = await self._restore_from_snapshot(ctx.guild, backup_id, reason=f"Manual Auto-Restore: {backup_id}")

        embed = discord.Embed(
            title="✅ Server Restoration Complete",
            description=(
                f"Reconstructed missing server structure from master snapshot `{backup_id}`:\n\n"
                f"• **Roles Recreated:** `{stats.get('roles', 0)}`\n"
                f"• **Categories Recreated:** `{stats.get('categories', 0)}`\n"
                f"• **Channels Recreated:** `{stats.get('channels', 0)}`"
            ),
            color=0x2ECC71,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Aizen XFX Disaster Recovery Engine")
        await progress_msg.edit(content=None, embed=embed)

    @autorestore_cmd.command(name="logchannel", aliases=["log", "logs"])
    @commands.has_permissions(administrator=True)
    async def autorestore_logchannel(self, ctx: Context, channel: discord.TextChannel):
        """Set the channel where auto-restore alert logs are sent."""
        await self._ensure_tables()
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO auto_restore_config (guild_id, log_channel_id)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET log_channel_id = excluded.log_channel_id
                """,
                (ctx.guild.id, channel.id)
            )
            await db.commit()

        embed = discord.Embed(
            title="Automatic Restore Log Set",
            description=f"Automatic server disaster alerts will now be sent to {channel.mention}.",
            color=0xD4AF37
        )
        embed.set_footer(text="Aizen XFX Disaster Recovery Engine")
        await ctx.reply(embed=embed, mention_author=False)

    # ── Server namespace group (>server backup ..., >server restore ...) ─────

    @commands.group(name="server", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def server_cmd(self, ctx: Context, *, sub: str = None):
        """Server management commands."""
        await self.backup_group(ctx, sub=sub)

    @server_cmd.group(name="backup", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def server_backup_cmd(self, ctx: Context, *, sub: str = None):
        """Server backup commands under server namespace."""
        await self.backup_group(ctx, sub=sub)

    @server_backup_cmd.command(name="create", aliases=["new", "make", "save"])
    @commands.has_permissions(administrator=True)
    async def server_backup_create(self, ctx: Context):
        await self.backup_create(ctx)

    @server_backup_cmd.command(name="load", aliases=["restore", "apply"])
    @commands.has_permissions(administrator=True)
    async def server_backup_load(self, ctx: Context, backup_id: str):
        await self.backup_load(ctx, backup_id)

    @server_backup_cmd.command(name="list", aliases=["all", "show"])
    @commands.has_permissions(administrator=True)
    async def server_backup_list(self, ctx: Context):
        await self.backup_list(ctx)

    @server_backup_cmd.command(name="info", aliases=["view", "details"])
    @commands.has_permissions(administrator=True)
    async def server_backup_info(self, ctx: Context, backup_id: str):
        await self.backup_info(ctx, backup_id)

    @server_backup_cmd.command(name="delete", aliases=["del", "remove"])
    @commands.has_permissions(administrator=True)
    async def server_backup_delete(self, ctx: Context, backup_id: str):
        await self.backup_delete(ctx, backup_id)

    @server_cmd.group(name="restore", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def server_restore_cmd(self, ctx: Context, *, sub: str = None):
        """Server restore command under server namespace."""
        await self.autorestore_cmd(ctx, sub=sub)


async def setup(bot):
    await bot.add_cog(Backup(bot))
