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
import aiosqlite
import discord
from discord.ext import commands
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
    Aizen XFX 1-Click Server Backup & Snapshot System
    Allows guild owners to snapshot and restore roles, channels, and permissions.
    """

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
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
                await db.commit()
        except Exception as e:
            logger.error(f"[Backup] Failed to ensure database table: {e}")

    def help_custom(self):
        emoji = "💾"
        label = "Server Backup"
        description = "1-Click server backup & snapshot system"
        return emoji, label, description

    # ── Primary Backup Group (>backup, >serverbackup, >sb) ─────────────────────

    @commands.group(
        name="backup",
        aliases=["serverbackup", "server-backup", "server_backup", "sb"],
        invoke_without_command=True
    )
    @commands.has_permissions(administrator=True)
    async def backup_group(self, ctx: Context, *, sub: str = None):
        """Aizen XFX Backup system command hub."""
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

        embed = discord.Embed(
            title=f"💾 {BotName} Server Backup Engine",
            description=(
                "**1-Click Server Snapshot & Disaster Recovery**\n\n"
                "Save your entire server layout (roles, channels, categories, and settings) and restore it anytime.\n\n"
                "__**Commands:**__\n"
                f"`{ctx.prefix}backup create` — Create a snapshot of roles, channels, and categories\n"
                f"`{ctx.prefix}backup list` — View all snapshots saved for this server\n"
                f"`{ctx.prefix}backup info <id>` — View detailed snapshot contents & stats\n"
                f"`{ctx.prefix}backup load <id>` — Restore a saved snapshot (interactive confirmation)\n"
                f"`{ctx.prefix}backup delete <id>` — Delete a saved snapshot\n\n"
                f"*Tip: You can also use `{ctx.prefix}server backup` or `{ctx.prefix}serverbackup`.*"
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
        guild = ctx.guild
        progress_msg = await ctx.reply("🟣 *Capturing server state (roles, categories, channels)...*", mention_author=False)

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

        snapshot = {
            "guild_name": guild.name,
            "guild_id": guild.id,
            "roles": roles_data,
            "categories": categories_data,
            "channels": channels_data,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        backup_id = f"ax-{secrets.token_hex(4)}"

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO backups (backup_id, guild_id, guild_name, created_by, created_at, data) VALUES (?, ?, ?, ?, ?, ?)",
                (backup_id, guild.id, guild.name, ctx.author.id, datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"), json.dumps(snapshot))
            )
            await db.commit()

        embed = discord.Embed(
            title="🟣 Server Snapshot Created",
            description=f"Snapshot successfully saved with ID: `{backup_id}`",
            color=THEME_COLOR
        )
        embed.add_field(name="Roles Saved", value=f"`{len(roles_data)}` roles", inline=True)
        embed.add_field(name="Categories", value=f"`{len(categories_data)}` categories", inline=True)
        embed.add_field(name="Channels", value=f"`{len(channels_data)}` channels", inline=True)
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
        # Check permissions first
        guild = ctx.guild
        missing_perms = []
        if not guild.me.guild_permissions.manage_roles:
            missing_perms.append("Manage Roles")
        if not guild.me.guild_permissions.manage_channels:
            missing_perms.append("Manage Channels")

        if missing_perms:
            return await ctx.reply(
                f"❌ The bot is missing required permissions to restore: **{', '.join(missing_perms)}**.\n"
                "Please grant these permissions and make sure the bot's role is positioned high in Server Settings > Roles.",
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

        status_embed = discord.Embed(title="🟣 Restoring Snapshot...", description="Recreating roles, categories, and channels, please wait...", color=THEME_COLOR)
        await msg.edit(embed=status_embed, view=None)

        # 1. Recreate roles
        existing_roles = {r.name.lower(): r for r in guild.roles}
        roles_created = 0
        for r_data in snapshot.get("roles", []):
            if r_data["name"].lower() not in existing_roles:
                try:
                    await guild.create_role(
                        name=r_data["name"],
                        permissions=discord.Permissions(r_data.get("permissions", 0)),
                        color=discord.Color(r_data.get("color", 0)),
                        hoist=r_data.get("hoist", False),
                        mentionable=r_data.get("mentionable", False),
                        reason=f"Aizen XFX Snapshot Restore: {backup_id}"
                    )
                    roles_created += 1
                except Exception as e:
                    logger.warning(f"[Backup] Failed to recreate role {r_data.get('name')}: {e}")

        # 2. Recreate categories
        cat_map = {}
        cats_created = 0
        for cat_data in snapshot.get("categories", []):
            cat = discord.utils.get(guild.categories, name=cat_data["name"])
            if not cat:
                try:
                    cat = await guild.create_category(
                        name=cat_data["name"],
                        position=cat_data.get("position", 0),
                        reason=f"Aizen XFX Snapshot Restore: {backup_id}"
                    )
                    cats_created += 1
                except Exception as e:
                    logger.warning(f"[Backup] Failed to recreate category {cat_data.get('name')}: {e}")
            if cat:
                cat_map[cat_data["name"]] = cat

        # 3. Recreate channels
        channels_created = 0
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
                            reason=f"Aizen XFX Snapshot Restore: {backup_id}"
                        )
                        channels_created += 1
                    except Exception as e:
                        logger.warning(f"[Backup] Failed to recreate text channel {ch_data.get('name')}: {e}")
            elif ch_data["type"] == "voice":
                exists = discord.utils.get(guild.voice_channels, name=ch_data["name"])
                if not exists:
                    try:
                        await guild.create_voice_channel(
                            name=ch_data["name"],
                            category=parent_cat,
                            bitrate=min(ch_data.get("bitrate", 64000), guild.bitrate_limit),
                            user_limit=ch_data.get("user_limit", 0),
                            reason=f"Aizen XFX Snapshot Restore: {backup_id}"
                        )
                        channels_created += 1
                    except Exception as e:
                        logger.warning(f"[Backup] Failed to recreate voice channel {ch_data.get('name')}: {e}")

        done_embed = discord.Embed(
            title="✅ Snapshot Restoration Complete",
            description=(
                f"Snapshot `{backup_id}` has been successfully applied to **{guild.name}**.\n\n"
                f"• Roles Recreated: `{roles_created}`\n"
                f"• Categories Recreated: `{cats_created}`\n"
                f"• Channels Recreated: `{channels_created}`"
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

    # ── Server namespace group (>server backup ...) ───────────────────────────

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


async def setup(bot):
    await bot.add_cog(Backup(bot))
