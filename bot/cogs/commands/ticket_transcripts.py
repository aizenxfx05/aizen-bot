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

import io
import html
import datetime
import discord
from discord.ext import commands

from core import Context, Cog
from utils.config import THEME_COLOR, BotName


def _escape(text: str) -> str:
    return html.escape(str(text or "")).replace("\n", "<br/>")


async def build_html_transcript(channel: discord.TextChannel, limit: int = 250) -> io.BytesIO:
    """Builds a Discord dark theme HTML transcript of the channel's messages."""
    messages = []
    async for msg in channel.history(limit=limit, oldest_first=True):
        messages.append(msg)

    msg_html_blocks = []
    for msg in messages:
        avatar = msg.author.display_avatar.url
        author_name = _escape(msg.author.display_name)
        time_str = msg.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        bot_badge = '<span class="badge">BOT</span>' if msg.author.bot else ""
        content_html = _escape(msg.content)

        attachments_html = ""
        for att in msg.attachments:
            if any(att.filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]):
                attachments_html += f'<div class="attachment"><img src="{att.url}" alt="{att.filename}" style="max-width:350px; border-radius:8px; margin-top:6px;"/></div>'
            else:
                attachments_html += f'<div class="attachment"><a href="{att.url}" target="_blank" class="file-link">📎 {att.filename}</a></div>'

        embeds_html = ""
        for emb in msg.embeds:
            color_hex = f"#{emb.color.value:06x}" if emb.color else "#A855F7"
            e_title = f'<div class="embed-title">{_escape(emb.title)}</div>' if emb.title else ""
            e_desc = f'<div class="embed-desc">{_escape(emb.description)}</div>' if emb.description else ""
            embeds_html += f'''
            <div class="embed" style="border-left-color: {color_hex};">
                {e_title}
                {e_desc}
            </div>
            '''

        block = f'''
        <div class="message">
            <img src="{avatar}" class="avatar" alt="Avatar"/>
            <div class="message-content">
                <div class="message-header">
                    <span class="author">{author_name}</span>
                    {bot_badge}
                    <span class="timestamp">{time_str}</span>
                </div>
                <div class="text">{content_html}</div>
                {attachments_html}
                {embeds_html}
            </div>
        </div>
        '''
        msg_html_blocks.append(block)

    full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transcript #{channel.name} — {channel.guild.name}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background: #07070D; color: #F3E8FF; padding: 24px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #0D0B18; border-radius: 16px; border: 1px solid rgba(168,85,247,0.2); overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.8); }}
        .header {{ background: rgba(168,85,247,0.08); border-bottom: 1px solid rgba(168,85,247,0.18); padding: 24px; }}
        .header h1 {{ font-size: 22px; color: #fff; margin-bottom: 4px; }}
        .header p {{ font-size: 13px; color: #948BA3; }}
        .messages {{ padding: 20px; }}
        .message {{ display: flex; gap: 16px; margin-bottom: 20px; }}
        .avatar {{ width: 42px; height: 42px; border-radius: 50%; object-fit: cover; flex-shrink: 0; border: 1px solid rgba(168,85,247,0.3); }}
        .message-content {{ flex: 1; min-width: 0; }}
        .message-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }}
        .author {{ font-size: 15px; font-weight: 700; color: #fff; }}
        .badge {{ background: #A855F7; color: #fff; font-size: 10px; font-weight: 800; padding: 1px 5px; border-radius: 4px; text-transform: uppercase; }}
        .timestamp {{ font-size: 12px; color: #6B7280; }}
        .text {{ font-size: 14px; color: #DDD6FE; line-height: 1.5; word-break: break-word; }}
        .embed {{ background: rgba(255,255,255,0.02); border-left: 4px solid #A855F7; border-radius: 4px; padding: 12px 16px; margin-top: 8px; max-width: 520px; }}
        .embed-title {{ font-size: 14px; font-weight: bold; color: #fff; margin-bottom: 6px; }}
        .embed-desc {{ font-size: 13px; color: #C4B5FD; }}
        .file-link {{ color: #C084FC; text-decoration: none; font-size: 13px; display: inline-block; margin-top: 6px; }}
        .footer {{ text-align: center; padding: 16px; font-size: 12px; color: #948BA3; border-top: 1px solid rgba(168,85,247,0.1); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>#{channel.name} — Transcript</h1>
            <p>Server: <strong>{_escape(channel.guild.name)}</strong> • Generated: {datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")} • Total Messages: {len(messages)}</p>
        </div>
        <div class="messages">
            {''.join(msg_html_blocks)}
        </div>
        <div class="footer">
            Generated by {BotName} Security Transcript Engine
        </div>
    </div>
</body>
</html>'''

    buffer = io.BytesIO(full_html.encode("utf-8"))
    buffer.seek(0)
    return buffer


class TicketTranscripts(Cog):
    """
    Aizen XFX HTML Ticket Transcripts System
    Exports chat histories into self-contained Discord-styled HTML archives.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="transcript", aliases=["htmltranscript"])
    @commands.has_permissions(manage_messages=True)
    async def transcript_cmd(self, ctx: Context, limit: int = 150):
        """Generates an HTML transcript file of the current channel."""
        limit = max(1, min(limit, 500))
        progress = await ctx.reply("🟣 *Generating HTML transcript archive...*", mention_author=False)

        try:
            buf = await build_html_transcript(ctx.channel, limit=limit)
            filename = f"transcript-{ctx.channel.name}-{datetime.datetime.utcnow().strftime('%Y%m%d-%H%M')}.html"
            file = discord.File(fp=buf, filename=filename)

            embed = discord.Embed(
                title="📜 Channel Transcript Generated",
                description=f"Exported `{limit}` messages from {ctx.channel.mention} into a standalone interactive HTML file.",
                color=THEME_COLOR
            )
            embed.set_footer(text=f"{BotName} Security • Download and open in any browser")
            await progress.delete()
            await ctx.reply(embed=embed, file=file, mention_author=False)
        except Exception as exc:
            await progress.edit(content=f"❌ Failed to generate transcript: {exc}")
