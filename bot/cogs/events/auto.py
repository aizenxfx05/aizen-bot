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
import asyncio
import logging
import aiosqlite
import discord
from utils.emoji import ARROWRED, ZMODULE
from core import Cog, AizenBot
from utils.config import BotName
from discord.ext import commands
from discord.ui import Button, View

DATABASE_PATH = "db/greeted_guilds.db"

class Autorole(Cog):
    def __init__(self, bot: AizenBot):
        self.bot = bot
        self._recently_greeted = set()
        self._lock = asyncio.Lock()

    async def _is_first_join(self, guild_id: int) -> bool:
        """Atomically checks and marks the guild as greeted in SQLite and memory."""
        async with self._lock:
            if guild_id in self._recently_greeted:
                return False

            os.makedirs("db", exist_ok=True)
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
                        # Already recorded in database by another call or replica
                        self._recently_greeted.add(guild_id)
                        return False

                    self._recently_greeted.add(guild_id)
                    return True
            except Exception as e:
                logging.error(f"Error in greeted_guilds check: {e}")
                if guild_id in self._recently_greeted:
                    return False
                self._recently_greeted.add(guild_id)
                return True

    @commands.Cog.listener(name="on_guild_join")
    async def send_msg_to_adder(self, guild: discord.Guild):
        # 1. Strictly deduplicate: only 1 execution per guild
        is_first = await self._is_first_join(guild.id)
        if not is_first:
            return

        # 2. Wait a brief moment for the Discord audit log entry to propagate
        await asyncio.sleep(1.5)

        adder = None
        try:
            if guild.me and guild.me.guild_permissions.view_audit_log:
                async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.bot_add):
                    if entry.target and entry.target.id == self.bot.user.id:
                        adder = entry.user
                        break  # Stop immediately once the specific adder is found
        except Exception as e:
            logging.debug(f"Audit log check error: {e}")

        # Fallback to guild owner if audit log didn't yield the adder
        if not adder and guild.owner:
            adder = guild.owner

        if not adder or adder.bot:
            return

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
        self._recently_greeted.discard(guild.id)
        try:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute("DELETE FROM greeted_guilds WHERE guild_id = ?", (guild.id,))
                await db.commit()
        except Exception as e:
            logging.debug(f"Error cleaning up greeted_guilds: {e}")
