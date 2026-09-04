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

import json
import re
import aiohttp
import aiosqlite
import discord
from discord.ext import commands

from core import Context, Cog
from utils.config import GROQ_API_KEY, THEME_COLOR, BotName

DB_PATH = "db/automod.db"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class AIAutoMod(Cog):
    """
    Aizen XFX Neuro-AI Auto-Moderation
    Analyzes messages in real-time with Groq LLaMA 3 to filter toxicity, phishing, and raid attacks.
    """

    def __init__(self, bot):
        self.bot = bot
        self._cache: dict[int, tuple[bool, int | None]] = {}

    async def cog_load(self):
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS ai_automod (
                    guild_id       INTEGER PRIMARY KEY,
                    enabled        INTEGER NOT NULL DEFAULT 0,
                    log_channel_id INTEGER
                )
            """)
            await db.commit()

    async def _get_config(self, guild_id: int) -> tuple[bool, int | None]:
        if guild_id in self._cache:
            return self._cache[guild_id]
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT enabled, log_channel_id FROM ai_automod WHERE guild_id = ?", (guild_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    res = (bool(row[0]), row[1])
                else:
                    res = (False, None)
                self._cache[guild_id] = res
                return res

    @Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        enabled, log_id = await self._get_config(message.guild.id)
        if not enabled or not GROQ_API_KEY:
            return

        # Skip staff and admins
        if message.author.guild_permissions.manage_messages or message.author.guild_permissions.administrator or message.author.id == message.guild.owner_id:
            return

        content = message.content.strip()
        if len(content) < 4:
            return

        # Query Groq AI for fast classification
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an AI automod classifier. Analyze the user's message for: "
                        "severe toxicity, slurs, phishing/token-logging links, or raid coordination. "
                        "Return JSON only: {\"flagged\": true/false, \"reason\": \"short reason\"}"
                    )
                },
                {"role": "user", "content": content}
            ],
            "max_tokens": 50,
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(GROQ_API_URL, headers=headers, json=payload, timeout=2.5) as resp:
                    if resp.status != 200:
                        return
                    data = await resp.json()
                    res_raw = data["choices"][0]["message"]["content"]
                    parsed = json.loads(res_raw)
        except Exception:
            return

        if parsed.get("flagged"):
            reason = parsed.get("reason", "Violated Community Guidelines")
            try:
                await message.delete()
            except discord.Forbidden:
                return

            # Temporary warning in channel
            try:
                alert = await message.channel.send(
                    f"⚠️ {message.author.mention}, your message was removed by **{BotName} Neuro-AI Moderation**.\n*Reason:* `{reason}`",
                    delete_after=6
                )
            except Exception:
                pass

            # Log to staff channel
            if log_id:
                log_ch = message.guild.get_channel(log_id)
                if log_ch:
                    embed = discord.Embed(
                        title="🟣 Neuro-AI Automod Action",
                        description=f"**User:** {message.author.mention} (`{message.author.id}`)\n**Channel:** {message.channel.mention}",
                        color=THEME_COLOR,
                        timestamp=discord.utils.utcnow()
                    )
                    embed.add_field(name="Detected Violation", value=f"`{reason}`", inline=False)
                    embed.add_field(name="Message Content", value=f"```{content[:1000]}```", inline=False)
                    embed.set_footer(text=f"{BotName} Neuro-Security")
                    try:
                        await log_ch.send(embed=embed)
                    except Exception:
                        pass

    @commands.group(name="ai-automod", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def ai_automod_group(self, ctx: Context):
        """Aizen XFX Neuro-AI Auto-Moderation commands."""
        enabled, log_id = await self._get_config(ctx.guild.id)
        status = "ENABLED 🟢" if enabled else "DISABLED 🔴"
        log_ch = f"<#{log_id}>" if log_id else "*Not configured*"

        embed = discord.Embed(
            title=f"🟣 {BotName} Neuro-AI Auto-Moderation",
            description=(
                f"**Status:** {status}\n"
                f"**Audit Channel:** {log_ch}\n\n"
                f"`{ctx.prefix}ai-automod enable` — Activate real-time AI content scanning\n"
                f"`{ctx.prefix}ai-automod disable` — Deactivate AI content scanning\n"
                f"`{ctx.prefix}ai-automod logchannel #channel` — Set where AI alerts are posted\n"
                f"`{ctx.prefix}ai-automod status` — Check current configuration\n"
            ),
            color=THEME_COLOR
        )
        await ctx.reply(embed=embed, mention_author=False)

    @ai_automod_group.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def ai_automod_enable(self, ctx: Context):
        """Enables Neuro-AI auto moderation."""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO ai_automod (guild_id, enabled) VALUES (?, 1) ON CONFLICT(guild_id) DO UPDATE SET enabled = 1",
                (ctx.guild.id,)
            )
            await db.commit()
        self._cache[ctx.guild.id] = (True, (await self._get_config(ctx.guild.id))[1])
        await ctx.reply("✅ **Neuro-AI Auto-Moderation** has been **ENABLED**.", mention_author=False)

    @ai_automod_group.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def ai_automod_disable(self, ctx: Context):
        """Disables Neuro-AI auto moderation."""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO ai_automod (guild_id, enabled) VALUES (?, 0) ON CONFLICT(guild_id) DO UPDATE SET enabled = 0",
                (ctx.guild.id,)
            )
            await db.commit()
        self._cache[ctx.guild.id] = (False, (await self._get_config(ctx.guild.id))[1])
        await ctx.reply("❌ **Neuro-AI Auto-Moderation** has been **DISABLED**.", mention_author=False)

    @ai_automod_group.command(name="logchannel")
    @commands.has_permissions(administrator=True)
    async def ai_automod_log(self, ctx: Context, channel: discord.TextChannel):
        """Sets the log channel for Neuro-AI warnings."""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO ai_automod (guild_id, enabled, log_channel_id) VALUES (?, 1, ?) ON CONFLICT(guild_id) DO UPDATE SET log_channel_id = ?",
                (ctx.guild.id, channel.id, channel.id)
            )
            await db.commit()
        self._cache[ctx.guild.id] = ((await self._get_config(ctx.guild.id))[0], channel.id)
        await ctx.reply(f"✅ Neuro-AI Automod logs will now be sent to {channel.mention}.", mention_author=False)
