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
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import discord

from api.dependencies import verify_api_key, get_bot
from utils.config import THEME_COLOR, BotName

router = APIRouter(prefix="/guilds/{guild_id}/server-control", tags=["server-control"])


# ── Pydantic Request Models ──────────────────────────────────────────────────

class LockdownRequest(BaseModel):
    locked: bool
    reason: str = "Emergency Lockdown initiated via Web Dashboard"


class AnnounceRequest(BaseModel):
    channel_id: int
    title: str
    message: str


class PurgeRequest(BaseModel):
    channel_id: int
    amount: int = Field(default=10, ge=1, le=100)
    bot_only: bool = False


class SlowmodeRequest(BaseModel):
    channel_id: int
    delay: int = Field(default=0, ge=0, le=21600)
    reason: str = "Slowmode updated via Web Dashboard"


class TimeoutRequest(BaseModel):
    user_id: int
    duration_minutes: int = Field(default=5, ge=1, le=40320)
    reason: str = "Timed out via Web Dashboard"


class KickRequest(BaseModel):
    user_id: int
    reason: str = "Kicked via Web Dashboard"


class BanRequest(BaseModel):
    user_id: int
    delete_message_days: int = Field(default=1, ge=0, le=7)
    reason: str = "Banned via Web Dashboard"


class UnbanRequest(BaseModel):
    user_id: int
    reason: str = "Unbanned via Web Dashboard"


class RoleManageRequest(BaseModel):
    user_id: int
    role_id: int
    action: str = "add"  # "add" or "remove"


# ── Server Stats & Lists ──────────────────────────────────────────────────────

@router.get("/stats", dependencies=[Depends(verify_api_key)])
async def get_server_stats(guild_id: int, bot=Depends(get_bot)):
    """Returns high-level live metrics for the server control dashboard."""
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    text_count = len(guild.text_channels)
    voice_count = len(guild.voice_channels)
    category_count = len(guild.categories)

    return {
        "id": str(guild.id),
        "name": guild.name,
        "icon": guild.icon.url if guild.icon else None,
        "banner": guild.banner.url if guild.banner else None,
        "member_count": guild.member_count or 0,
        "channels": {
            "total": len(guild.channels),
            "text": text_count,
            "voice": voice_count,
            "categories": category_count,
        },
        "roles_count": len(guild.roles),
        "boost_count": guild.premium_subscription_count or 0,
        "boost_tier": guild.premium_tier,
        "owner_id": str(guild.owner_id) if guild.owner_id else None,
    }


@router.get("/channels", dependencies=[Depends(verify_api_key)])
async def get_server_channels(guild_id: int, bot=Depends(get_bot)):
    """Returns all text and voice channels for dropdown selections."""
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    channels = []
    for ch in sorted(guild.channels, key=lambda c: c.position):
        ch_type = "text"
        if isinstance(ch, discord.VoiceChannel):
            ch_type = "voice"
        elif isinstance(ch, discord.CategoryChannel):
            ch_type = "category"
        elif isinstance(ch, discord.StageChannel):
            ch_type = "stage"

        channels.append({
            "id": str(ch.id),
            "name": ch.name,
            "type": ch_type,
            "position": ch.position,
            "slowmode": getattr(ch, "slowmode_delay", 0),
            "parent_id": str(ch.category_id) if getattr(ch, "category_id", None) else None,
        })

    return channels


@router.get("/roles", dependencies=[Depends(verify_api_key)])
async def get_server_roles(guild_id: int, bot=Depends(get_bot)):
    """Returns all roles for assignment and management."""
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    roles = []
    for r in sorted(guild.roles, key=lambda role: role.position, reverse=True):
        if r.is_default():
            continue
        hex_color = f"#{r.color.value:06x}" if r.color.value else "#818cf8"
        roles.append({
            "id": str(r.id),
            "name": r.name,
            "color": hex_color,
            "position": r.position,
            "members_count": len(r.members),
            "managed": r.managed,
        })

    return roles


# ── Server Actions ────────────────────────────────────────────────────────────

@router.post("/lockdown", dependencies=[Depends(verify_api_key)])
async def trigger_lockdown(guild_id: int, payload: LockdownRequest, bot=Depends(get_bot)):
    """Locks or unlocks public text channels for @everyone."""
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
        "guild_id": str(guild_id),
        "locked": payload.locked,
        "affected_channels": locked_count,
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
        return {"success": True, "message_id": str(msg.id)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/purge", dependencies=[Depends(verify_api_key)])
async def purge_channel_messages(guild_id: int, payload: PurgeRequest, bot=Depends(get_bot)):
    """Bulk-deletes up to 100 messages from a specified channel."""
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    channel = guild.get_channel(payload.channel_id)
    if not channel or not isinstance(channel, discord.TextChannel):
        raise HTTPException(status_code=400, detail="Invalid text channel ID")

    def check(msg):
        if payload.bot_only:
            return msg.author.bot
        return True

    try:
        deleted = await channel.purge(limit=payload.amount, check=check, bulk=True)
        return {
            "success": True,
            "channel_id": str(channel.id),
            "deleted_count": len(deleted),
        }
    except discord.Forbidden:
        raise HTTPException(status_code=403, detail="Bot lacks 'Manage Messages' permission.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/slowmode", dependencies=[Depends(verify_api_key)])
async def set_channel_slowmode(guild_id: int, payload: SlowmodeRequest, bot=Depends(get_bot)):
    """Sets slowmode delay on a text channel."""
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    channel = guild.get_channel(payload.channel_id)
    if not channel or not isinstance(channel, discord.TextChannel):
        raise HTTPException(status_code=400, detail="Invalid text channel ID")

    try:
        await channel.edit(slowmode_delay=payload.delay, reason=payload.reason)
        return {
            "success": True,
            "channel_id": str(channel.id),
            "slowmode_delay": payload.delay,
        }
    except discord.Forbidden:
        raise HTTPException(status_code=403, detail="Bot lacks 'Manage Channels' permission.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Quick Member Moderation ───────────────────────────────────────────────────

@router.post("/moderation/timeout", dependencies=[Depends(verify_api_key)])
async def timeout_member(guild_id: int, payload: TimeoutRequest, bot=Depends(get_bot)):
    """Times out a server member for a specified duration."""
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    member = guild.get_member(payload.user_id)
    if not member:
        try:
            member = await guild.fetch_member(payload.user_id)
        except discord.NotFound:
            raise HTTPException(status_code=404, detail="Member not found in guild")

    until = discord.utils.utcnow() + timedelta(minutes=payload.duration_minutes)
    try:
        await member.timeout(until, reason=payload.reason)
        return {
            "success": True,
            "action": "timeout",
            "user_id": str(member.id),
            "duration_minutes": payload.duration_minutes,
            "until": until.isoformat(),
        }
    except discord.Forbidden:
        raise HTTPException(status_code=403, detail="Bot hierarchy is lower than member or lacks timeout perms.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/moderation/kick", dependencies=[Depends(verify_api_key)])
async def kick_member(guild_id: int, payload: KickRequest, bot=Depends(get_bot)):
    """Kicks a member from the server."""
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    member = guild.get_member(payload.user_id)
    if not member:
        try:
            member = await guild.fetch_member(payload.user_id)
        except discord.NotFound:
            raise HTTPException(status_code=404, detail="Member not found in guild")

    try:
        await member.kick(reason=payload.reason)
        return {
            "success": True,
            "action": "kick",
            "user_id": str(member.id),
        }
    except discord.Forbidden:
        raise HTTPException(status_code=403, detail="Bot hierarchy is lower than member or lacks kick perms.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/moderation/ban", dependencies=[Depends(verify_api_key)])
async def ban_member(guild_id: int, payload: BanRequest, bot=Depends(get_bot)):
    """Bans a member from the server."""
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    user = discord.Object(id=payload.user_id)
    try:
        await guild.ban(user, delete_message_days=payload.delete_message_days, reason=payload.reason)
        return {
            "success": True,
            "action": "ban",
            "user_id": str(payload.user_id),
        }
    except discord.Forbidden:
        raise HTTPException(status_code=403, detail="Bot lacks 'Ban Members' permission or hierarchy.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/moderation/unban", dependencies=[Depends(verify_api_key)])
async def unban_member(guild_id: int, payload: UnbanRequest, bot=Depends(get_bot)):
    """Unbans a user from the server."""
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    user = discord.Object(id=payload.user_id)
    try:
        await guild.unban(user, reason=payload.reason)
        return {
            "success": True,
            "action": "unban",
            "user_id": str(payload.user_id),
        }
    except discord.NotFound:
        raise HTTPException(status_code=404, detail="User was not banned in this server.")
    except discord.Forbidden:
        raise HTTPException(status_code=403, detail="Bot lacks 'Ban Members' permission.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/roles/manage", dependencies=[Depends(verify_api_key)])
async def manage_member_role(guild_id: int, payload: RoleManageRequest, bot=Depends(get_bot)):
    """Assigns or removes a role from a member."""
    guild = bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    member = guild.get_member(payload.user_id)
    if not member:
        try:
            member = await guild.fetch_member(payload.user_id)
        except discord.NotFound:
            raise HTTPException(status_code=404, detail="Member not found in guild")

    role = guild.get_role(payload.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    try:
        if payload.action.lower() == "add":
            await member.add_roles(role, reason="Role assigned via Web Dashboard")
        else:
            await member.remove_roles(role, reason="Role removed via Web Dashboard")

        return {
            "success": True,
            "user_id": str(member.id),
            "role_id": str(role.id),
            "action": payload.action,
        }
    except discord.Forbidden:
        raise HTTPException(status_code=403, detail="Bot role is lower than target role in hierarchy.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
