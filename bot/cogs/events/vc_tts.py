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
import io
import asyncio
import tempfile
import discord
from discord.ext import commands
from gtts import gTTS

from core import Context, Cog
from utils.config import THEME_COLOR, BotName

# Toggle for AI voice speech per guild
_ai_voice_enabled: dict[int, bool] = {}


class VCAITTS(Cog):
    """
    Aizen XFX Voice Channel TTS & Vocal AI Module
    Speaks text aloud and vocalizes AI responses in voice channels.
    """

    def __init__(self, bot):
        self.bot = bot
        self._queues: dict[int, asyncio.Queue] = {}
        self._is_playing: dict[int, bool] = {}

    async def _get_voice_client(self, channel: discord.VoiceChannel) -> discord.VoiceClient | None:
        """Connects or moves to the target voice channel."""
        vc = discord.utils.get(self.bot.voice_clients, guild=channel.guild)
        if vc and vc.is_connected():
            if vc.channel.id != channel.id:
                await vc.move_to(channel)
            return vc
        try:
            return await channel.connect(reconnect=True, timeout=15)
        except Exception:
            return None

    def _play_next(self, guild_id: int, vc: discord.VoiceClient):
        """Plays the next audio in queue."""
        if guild_id not in self._queues or self._queues[guild_id].empty():
            self._is_playing[guild_id] = False
            return

        self._is_playing[guild_id] = True
        file_path = self._queues[guild_id].get_nowait()

        def after_play(err):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
            self._play_next(guild_id, vc)

        try:
            audio_source = discord.FFmpegPCMAudio(file_path)
            vc.play(audio_source, after=after_play)
        except Exception:
            after_play(None)

    async def speak_text(self, channel: discord.VoiceChannel, text: str):
        """Synthesizes text and queues it for voice playback."""
        vc = await self._get_voice_client(channel)
        if not vc:
            return False

        # Clean text
        clean = text[:350].strip()
        if not clean:
            return False

        loop = asyncio.get_running_loop()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_path = temp_file.name
        temp_file.close()

        def generate_audio():
            tts = gTTS(text=clean, lang="en", tld="com")
            tts.save(temp_path)

        await loop.run_in_executor(None, generate_audio)

        guild_id = channel.guild.id
        if guild_id not in self._queues:
            self._queues[guild_id] = asyncio.Queue()

        await self._queues[guild_id].put(temp_path)

        if not self._is_playing.get(guild_id, False) and not vc.is_playing():
            self._play_next(guild_id, vc)

        return True

    @commands.command(name="speak", aliases=["tts"])
    async def speak_cmd(self, ctx: Context, *, text: str):
        """Vocalizes text in your current voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply("❌ You must be connected to a voice channel to use TTS.", mention_author=False)

        voice_channel = ctx.author.voice.channel
        permissions = voice_channel.permissions_for(ctx.guild.me)
        if not permissions.connect or not permissions.speak:
            return await ctx.reply("❌ I lack permissions to connect or speak in your voice channel.", mention_author=False)

        await ctx.message.add_reaction("🎙️")
        success = await self.speak_text(voice_channel, text)
        if not success:
            await ctx.reply("Could not play TTS audio in voice channel.", mention_author=False)

    @commands.command(name="vc-join")
    async def vc_join(self, ctx: Context):
        """Connects the bot to your current voice channel."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.reply("❌ Connect to a voice channel first.", mention_author=False)

        vc = await self._get_voice_client(ctx.author.voice.channel)
        if vc:
            await ctx.reply(f"Connected to **{ctx.author.voice.channel.name}** 🎙️", mention_author=False)
        else:
            await ctx.reply("Failed to connect to voice channel.", mention_author=False)

    @commands.command(name="vc-leave")
    async def vc_leave(self, ctx: Context):
        """Disconnects the bot from voice."""
        vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if vc and vc.is_connected():
            await vc.disconnect(force=True)
            self._is_playing[ctx.guild.id] = False
            await ctx.reply("Disconnected from voice channel.", mention_author=False)
        else:
            await ctx.reply("I am not in a voice channel.", mention_author=False)

    @commands.command(name="vc-ai-voice")
    @commands.has_permissions(manage_channels=True)
    async def toggle_ai_voice(self, ctx: Context, toggle: str = None):
        """Toggles whether the bot speaks AI responses in voice channels."""
        guild_id = ctx.guild.id
        if toggle is None:
            current = _ai_voice_enabled.get(guild_id, False)
            status = "ENABLED" if current else "DISABLED"
            return await ctx.reply(f"Vocal AI Voice responses are currently **{status}** for this server. Use `>vc-ai-voice on` or `>vc-ai-voice off`.", mention_author=False)

        val = toggle.lower() in ("on", "enable", "true", "yes")
        _ai_voice_enabled[guild_id] = val
        status_text = "ENABLED 🎙️ (Bot will now speak AI replies in VC)" if val else "DISABLED (Text-only replies)"
        embed = discord.Embed(
            title="🟣 Vocal AI Voice Config",
            description=f"AI Voice Responses are now **{status_text}**.",
            color=THEME_COLOR
        )
        await ctx.reply(embed=embed, mention_author=False)
