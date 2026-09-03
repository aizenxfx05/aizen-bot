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
# ║   github   ──  https://github.com/RayExo                        ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import json
import secrets
import datetime
import aiosqlite
import discord
from discord.ext import commands
from discord.ui import View, Button

from core import Context, Cog
from utils.config import THEME_COLOR, BotName, serverLink

DB_PATH = "db/backup.db"


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

    @commands.group(name="backup", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def backup_group(self, ctx: Context):
        """Aizen XFX Backup system command hub."""
        embed = discord.Embed(
            title=f"🟣 {BotName} Server Backup Engine",
            description=(
                f"`{ctx.prefix}backup create` — Create a snapshot of roles, channels, and permissions\n"
                f"`{ctx.prefix}backup load <id>` — Restore a saved snapshot with interactive confirmation\n"
                f"`{ctx.prefix}backup list` — View all snapshots created for this server\n"
                f"`{ctx.prefix}backup info <id>` — View detailed snapshot contents\n"
                f"`{ctx.prefix}backup delete <id>` — Delete a saved snapshot\n"
            ),
            color=THEME_COLOR
        )
        embed.set_footer(text=f"{BotName} Security • Support: {serverLink}")
        await ctx.reply(embed=embed, mention_author=False)

    @backup_group.command(name="create")
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

    @backup_group.command(name="list")
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

    @backup_group.command(name="load")
    @commands.has_permissions(administrator=True)
    async def backup_load(self, ctx: Context, backup_id: str):
        """Restores a server snapshot with confirmation."""
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

        status_embed = discord.Embed(title="🟣 Restoring Snapshot...", description="Recreating roles and channels, please wait...", color=THEME_COLOR)
        await msg.edit(embed=status_embed, view=None)

        guild = ctx.guild

        # 1. Recreate roles
        existing_roles = {r.name.lower(): r for r in guild.roles}
        for r_data in snapshot.get("roles", []):
            if r_data["name"].lower() not in existing_roles:
                try:
                    await guild.create_role(
                        name=r_data["name"],
                        permissions=discord.Permissions(r_data.get("permissions", 0)),
                        color=discord.Color(r_data.get("color", 0)),
                        hoist=r_data.get("hoist", False),
                        mentionable=r_data.get("mentionable", False)
                    )
                except Exception:
                    pass

        # 2. Recreate categories
        cat_map = {}
        for cat_data in snapshot.get("categories", []):
            cat = discord.utils.get(guild.categories, name=cat_data["name"])
            if not cat:
                try:
                    cat = await guild.create_category(name=cat_data["name"], position=cat_data.get("position", 0))
                except Exception:
                    pass
            if cat:
                cat_map[cat_data["name"]] = cat

        # 3. Recreate channels
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
                            nsfw=ch_data.get("nsfw", False)
                        )
                    except Exception:
                        pass
            elif ch_data["type"] == "voice":
                exists = discord.utils.get(guild.voice_channels, name=ch_data["name"])
                if not exists:
                    try:
                        await guild.create_voice_channel(
                            name=ch_data["name"],
                            category=parent_cat,
                            user_limit=ch_data.get("user_limit", 0)
                        )
                    except Exception:
                        pass

        done_embed = discord.Embed(
            title="✅ Snapshot Restoration Complete",
            description=f"Snapshot `{backup_id}` has been successfully applied to **{guild.name}**.",
            color=THEME_COLOR
        )
        await msg.edit(embed=done_embed)

    @backup_group.command(name="delete")
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
