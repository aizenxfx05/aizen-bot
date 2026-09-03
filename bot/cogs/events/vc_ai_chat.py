# ╔══════════════════════════════════════════════════════════════════╗
# ║                                                                  ║
# ║        Aizen XFX — VC AI Chat Module                            ║
# ║                                                                  ║
# ║   Replies with AI when anyone texts in a voice-linked channel.  ║
# ║   Uses Groq API (llama3 model) for ultra-fast AI responses.     ║
# ║                                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import re
import asyncio
import aiohttp
import discord
from discord.ext import commands
from collections import defaultdict, deque
from utils.config import GROQ_API_KEY, BRAND_NAME

# ── Config ────────────────────────────────────────────────────────────────────
GROQ_API_URL     = "https://api.groq.com/openai/v1/chat/completions"
AI_MODEL         = "llama3-8b-8192"
MAX_HISTORY      = 8
MAX_RESPONSE_LEN = 1800
BOT_SYSTEM_PROMPT = (
    f"You are Aizen XFX, an intelligent and elegant AI assistant "
    f"built into the {BRAND_NAME} Discord bot. You are knowledgeable, concise, "
    f"and speak with confidence. You help users in voice-linked text channels. "
    f"Keep responses short and friendly unless the user asks for detail."
)

NSFW_WORDS = [
    "naked", "loli", "hentai", "explicit", "pornography",
    "adult", "XXX", "sex", "erotic",
]

# Per-channel conversation history cache
_history: dict = defaultdict(lambda: deque(maxlen=MAX_HISTORY))


def _is_vc_text_channel(channel) -> bool:
    """Returns True if the channel is a voice-linked text channel."""
    if isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
        return True
    if isinstance(channel, discord.TextChannel):
        name = channel.name.lower()
        if any(name.endswith(s) for s in ("-vc", "-voice", "-text", "-chat", "-talk")):
            if channel.guild:
                vc_names = {
                    re.sub(r"[-_](vc|voice|text|chat|talk)$", "", v.name.lower())
                    for v in channel.guild.voice_channels
                }
                base = re.sub(r"[-_](vc|voice|text|chat|talk)$", "", name)
                if base in vc_names:
                    return True
    return False


def _nsfw_clean(text: str) -> bool:
    lower = text.lower()
    return any(word in lower for word in NSFW_WORDS)


async def _call_groq(channel_id: int, user_message: str) -> str:
    """Calls the Groq chat API with conversation history."""
    if not GROQ_API_KEY:
        return (
            "The AI feature is not configured yet. "
            "Please set `GROQ_API_KEY` in the bot's `.env` file."
        )

    history = list(_history[channel_id])
    messages = [{"role": "system", "content": BOT_SYSTEM_PROMPT}] + history
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.75,
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GROQ_API_URL,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data["choices"][0]["message"]["content"].strip()
                    _history[channel_id].append({"role": "user", "content": user_message})
                    _history[channel_id].append({"role": "assistant", "content": reply})
                    return reply
                elif resp.status == 401:
                    return "Invalid Groq API key. Please update `GROQ_API_KEY` in `.env`."
                elif resp.status == 429:
                    return "AI is rate-limited right now. Please try again in a moment."
                else:
                    return f"AI error (HTTP {resp.status}). Please try again later."
    except asyncio.TimeoutError:
        return "The AI took too long to respond. Please try again."
    except Exception as e:
        return f"Unexpected AI error: `{type(e).__name__}`"


class VCAIChat(commands.Cog):
    """Aizen XFX — AI replies in voice-linked text channels."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._processing: set = set()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        if message.type != discord.MessageType.default:
            return

        channel = message.channel

        if not _is_vc_text_channel(channel):
            return

        if channel.id in self._processing:
            return
        self._processing.add(channel.id)

        try:
            user_input = message.content.strip()
            if not user_input:
                return

            if _nsfw_clean(user_input):
                await message.reply(
                    "That content is not allowed here.",
                    mention_author=False,
                    delete_after=8,
                )
                return

            async with channel.typing():
                reply = await _call_groq(channel.id, user_input)

            if not reply:
                return

            if _nsfw_clean(reply):
                await message.reply(
                    "The AI generated inappropriate content. Message blocked.",
                    mention_author=False,
                )
                return

            if len(reply) > MAX_RESPONSE_LEN:
                reply = reply[:MAX_RESPONSE_LEN] + "..."

            await message.reply(reply, mention_author=False)

        finally:
            self._processing.discard(channel.id)

    @commands.command(name="vc-ai-clear", aliases=["clearvcai"])
    @commands.has_permissions(manage_channels=True)
    async def clear_vc_history(self, ctx: commands.Context):
        """Clears the AI conversation history for the current VC text channel."""
        if ctx.channel.id in _history:
            _history[ctx.channel.id].clear()
        await ctx.send(
            "AI conversation history for this channel has been cleared.",
            delete_after=10,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(VCAIChat(bot))
