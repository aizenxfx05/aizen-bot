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
import time
import asyncio
import logging
import aiosqlite
import discord
from utils.emoji import ARROWRED, ZMODULE
from core import Cog, AizenBot
from utils.config import BotName
from discord.ext import commands
from discord.ui import Button, View

# Module-level singletons to ensure deduplication across all instances & reloads
_GREETED_GUILDS = set()
_GREET_LOCK = asyncio.Lock()
_LAST_GREET_TIME = {}

# Absolute database path independent of working directory
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DB_DIR = os.path.join(_BASE_DIR, "db")
os.makedirs(_DB_DIR, exist_ok=True)
DATABASE_PATH = os.path.join(_DB_DIR, "greeted_guilds.db")


class Autorole(Cog):
    def __init__(self, bot: AizenBot):
        self.bot = bot

    async def _is_first_join(self, guild_id: int) -> bool:
        """Atomically checks and marks the guild as greeted in SQLite and module-level memory."""
        now = time.time()
        async with _GREET_LOCK:
            if guild_id in _GREETED_GUILDS:
                return False
            if guild_id in _LAST_GREET_TIME and (now - _LAST_GREET_TIME[guild_id]) < 600:
                return False

            try:
                async with aiosqlite.connect(DATABASE_PATH) as db:
                    await db.execute("""
                        CREATE TABLE IF NOT EXISTS greeted_guilds (
                            guild_id INTEGER PRIMARY KEY,
                            added_at TIMESTAMP
                        )
                    """)
                    cursor = await db.execute(
                        "INSERT OR IGNORE INTO greeted_guilds (guild_id, added_at) VALUES (?, datetime('now'))",
                        (guild_id,)
                    )
                    await db.commit()
                    if cursor.rowcount == 0:
                        _GREETED_GUILDS.add(guild_id)
                        _LAST_GREET_TIME[guild_id] = now
                        return False

                    _GREETED_GUILDS.add(guild_id)
                    _LAST_GREET_TIME[guild_id] = now
                    return True
            except Exception as e:
                logging.error(f"Error in greeted_guilds database check: {e}")
                if guild_id in _GREETED_GUILDS:
                    return False
                _GREETED_GUILDS.add(guild_id)
                _LAST_GREET_TIME[guild_id] = now
                return True

    @commands.Cog.listener(name="on_guild_join")
    async def send_msg_to_adder(self, guild: discord.Guild):
        # 1. Strictly deduplicate: only 1 execution per guild
        is_first = await self._is_first_join(guild.id)
        if not is_first:
            return

        # 2. Wait a moment for the Discord audit log entry to write
        await asyncio.sleep(1.5)

        adder = None
        try:
            if guild.me and guild.me.guild_permissions.view_audit_log:
                async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.bot_add):
                    if entry.target and entry.target.id == self.bot.user.id:
                        adder = entry.user
                        break  # Stop immediately once the adder is found
        except Exception as e:
            logging.debug(f"Audit log check error: {e}")

        # Fallback to guild owner if audit log didn't yield the adder
        if not adder and guild.owner:
            adder = guild.owner

        if not adder or adder.bot:
            return

        # Extra guard: prevent sending duplicate DM to the same user in short window
        user_key = f"{adder.id}_{guild.id}"
        async with _GREET_LOCK:
            if user_key in _LAST_GREET_TIME and (time.time() - _LAST_GREET_TIME[user_key]) < 600:
                return
            _LAST_GREET_TIME[user_key] = time.time()

        embed = discord.Embed(
            description=(
                f"{ZMODULE} **Thanks for adding me.**\n\n"
                f"{ARROWRED} My default prefix is `>`\n"
                f"{ARROWRED}> Use the `>help` command to see a list of commands\n"
                f"{ARROWRED} For detailed guides, FAQ and information, visit our **[Support Server](https://discord.gg/M8qJ9W7vBb)**"
            ),
            color=0xA855F7,
        )

        if adder.avatar:
            embed.set_thumbnail(url=adder.avatar.url)
        elif adder.default_avatar:
            embed.set_thumbnail(url=adder.default_avatar.url)

        embed.set_author(name=f"{guild.name}", icon_url=guild.me.display_avatar.url if guild.me else None)
        if guild.icon:
            embed.set_author(name=guild.name, icon_url=guild.icon.url)

        support_button = Button(
            label="Support",
            style=discord.ButtonStyle.link,
            url="https://discord.gg/M8qJ9W7vBb",
        )
        view = View()
        view.add_item(support_button)

        try:
            await adder.send(embed=embed, view=view)
        except Exception as e:
            logging.warning(f"Could not send join DM to {adder}: {e}")

    @commands.Cog.listener(name="on_guild_remove")
    async def cleanup_guild_greet(self, guild: discord.Guild):
        """Cleans up greeting record when the bot is removed from a server."""
        async with _GREET_LOCK:
            _GREETED_GUILDS.discard(guild.id)
            _LAST_GREET_TIME.pop(guild.id, None)

        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute("DELETE FROM greeted_guilds WHERE guild_id = ?", (guild.id,))
                await db.commit()
        except Exception as e:
            logging.debug(f"Error cleaning up greeted_guilds: {e}")
