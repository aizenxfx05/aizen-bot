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
import secrets
import datetime
import aiosqlite
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import discord

from api.dependencies import verify_api_key, get_bot
from utils.config import THEME_COLOR, BotName

router = APIRouter(prefix="/guilds/{guild_id}/server-control", tags=["server-control"])


class LockdownRequest(BaseModel):
    locked: bool
    reason: str = "Emergency Lockdown initiated via Web Dashboard"


class AnnounceRequest(BaseModel):
    channel_id: int
    title: str
    message: str


@router.post("/lockdown", dependencies=[Depends(verify_api_key)])
async def trigger_lockdown(guild_id: int, payload: LockdownRequest, bot=Depends(get_bot)):
    """Locks or unlocks public channels for @everyone."""
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    locked_count = 0
    everyone_role = guild.default_role

    for ch in guild.text_channels:
        perms = ch.overwrites_for(everyone_role)
        if payload.locked:
            if perms.send_messages is not False:
                perms.send_messages = False
                try:
                    await ch.set_permissions(everyone_role, overwrite=perms, reason=payload.reason)
                    locked_count += 1
                except Exception:
                    pass
        else:
            if perms.send_messages is False:
                perms.send_messages = None
                try:
                    await ch.set_permissions(everyone_role, overwrite=perms, reason=payload.reason)
                    locked_count += 1
                except Exception:
                    pass

    return {
        "success": True,
        "guild_id": guild_id,
        "locked": payload.locked,
        "affected_channels": locked_count
    }


@router.post("/announce", dependencies=[Depends(verify_api_key)])
async def send_announcement(guild_id: int, payload: AnnounceRequest, bot=Depends(get_bot)):
    """Dispatches a rich announcement embed to a specified channel."""
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    channel = guild.get_channel(payload.channel_id)
    if not channel or not isinstance(channel, discord.TextChannel):
        raise HTTPException(status_code=400, detail="Invalid text channel ID")

    embed = discord.Embed(
        title=f"📢 {payload.title}",
        description=payload.message,
        color=THEME_COLOR,
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"Sent via {BotName} Web Console")

    try:
        msg = await channel.send(embed=embed)
        return {"success": True, "message_id": msg.id}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
