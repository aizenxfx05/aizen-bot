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

import discord
from utils.emoji import TICK
from discord.ext import commands
import aiosqlite
import asyncio
from datetime import timedelta
import re

class AntiLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.link_pattern = re.compile(r'http[s]?://\S+')
        self.invite_pattern = re.compile(r'(https?://)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com/invite)/\S+')
        self.gif_pattern = re.compile(r'(\.gif$|^https://(tenor\.com|giphy\.com/gifs|cdn\.discordapp\.com|media\.discordapp\.net))')
        self.spotify_pattern = re.compile(r'^https://open\.spotify\.com/track/\S+')
        self.recent_links = {}

    async def remove_user_roles(self, user: discord.Member, guild: discord.Guild, reason: str):
        """Removes all roles from the user that the bot has permission to remove."""
        if not guild.me.guild_permissions.manage_roles:
            return []

        bot_top_role = guild.me.top_role
        roles_to_remove = [
            role for role in user.roles
            if role != guild.default_role
            and not role.managed
            and role.position < bot_top_role.position
        ]
        if not roles_to_remove:
            return []

        try:
            await user.remove_roles(*roles_to_remove, reason=reason)
            return [r.name for r in roles_to_remove]
        except (discord.Forbidden, discord.HTTPException):
            return []

    async def is_automod_enabled(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT enabled FROM automod WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            return result is not None and result[0] == 1

    async def is_anti_link_enabled(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT punishment FROM automod_punishments WHERE guild_id = ? AND event = 'Anti link'", (guild_id,))
            result = await cursor.fetchone()
            return result is not None

    async def get_ignored_channels(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT id FROM automod_ignored WHERE guild_id = ? AND type = 'channel'", (guild_id,))
            return [row[0] for row in await cursor.fetchall()]

    async def get_ignored_roles(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT id FROM automod_ignored WHERE guild_id = ? AND type = 'role'", (guild_id,))
            return [row[0] for row in await cursor.fetchall()]

    async def get_punishment(self, guild_id):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT punishment FROM automod_punishments WHERE guild_id = ? AND event = 'Anti link'", (guild_id,))
            result = await cursor.fetchone()
            return result[0] if result else None

    async def log_action(self, guild, user, channel, action, reason):
        async with aiosqlite.connect("db/automod.db") as db:
            cursor = await db.execute("SELECT log_channel FROM automod_logging WHERE guild_id = ?", (guild.id,))
            log_channel_id = await cursor.fetchone()

        if log_channel_id and log_channel_id[0]:
            log_channel = guild.get_channel(log_channel_id[0])
            if log_channel:
                embed = discord.Embed(title="Automod Log: Anti-Link", color=0xA855F7)
                embed.add_field(name="User", value=user.mention, inline=False)
                embed.add_field(name="Action", value=action, inline=False)
                embed.add_field(name="Channel", value=channel.mention, inline=False)
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.set_footer(text=f"User ID: {user.id}")
                avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
                embed.set_thumbnail(url=avatar_url)
                embed.timestamp=discord.utils.utcnow()
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild = message.guild
        if not guild:
            return

        user = message.author
        channel = message.channel
        guild_id = guild.id

        if not await self.is_automod_enabled(guild_id) or not await self.is_anti_link_enabled(guild_id):
            return

        if user == guild.owner or user == self.bot.user:
            return

        ignored_channels = await self.get_ignored_channels(guild_id)
        if channel.id in ignored_channels:
            return

        ignored_roles = await self.get_ignored_roles(guild_id)
        if any(role.id in ignored_roles for role in user.roles):
            return

        if self.link_pattern.search(message.content):
            if self.invite_pattern.search(message.content):
                return
            if self.gif_pattern.search(message.content): 
                return
            if self.spotify_pattern.search(message.content):
                return

            # 1. Immediately delete the offending link
            try:
                await message.delete()
            except (discord.Forbidden, discord.HTTPException, discord.NotFound):
                pass

            # 2. Track rapid link spamming
            current_time = message.created_at.timestamp()
            user_links = self.recent_links.get(user.id, [])
            user_links = [t for t in user_links if current_time - t < 10]
            user_links.append(current_time)
            self.recent_links[user.id] = user_links

            is_spam = len(user_links) >= 2
            reason = "Spamming links" if is_spam else "Posting a link"

            # 3. Automatically remove user's roles
            removed_roles = await self.remove_user_roles(user, guild, reason=f"Automod Anti-Link: {reason}")
            roles_text = f" & stripped of {len(removed_roles)} role(s)" if removed_roles else ""

            punishment = await self.get_punishment(guild_id)
            punishment_clean = (punishment or "").strip().lower()
            action_taken = None

            try:
                if punishment_clean in ["remove role", "remove_role", "removerole"]:
                    if removed_roles:
                        action_taken = f"stripped of {len(removed_roles)} role(s)"
                    else:
                        action_taken = "warned (no removable roles)"
                elif punishment_clean == "mute":
                    timeout_duration = discord.utils.utcnow() + timedelta(minutes=7)
                    await user.edit(timed_out_until=timeout_duration, reason=reason)
                    action_taken = f"Muted for 7 minutes{roles_text}"
                elif punishment_clean == "kick":
                    await user.kick(reason=reason)
                    action_taken = f"Kicked{roles_text}"
                elif punishment_clean == "ban":
                    await user.ban(reason=reason)
                    action_taken = f"Banned{roles_text}"
                else:
                    if removed_roles:
                        action_taken = f"stripped of {len(removed_roles)} role(s)"
                    else:
                        action_taken = "warned & link deleted"

                simple_embed = discord.Embed(title="Automod Anti-Link", color=0xA855F7)
                simple_embed.description = f"{TICK} | {user.mention} has been successfully **{action_taken}** for **{reason}.**"
                
                avatar_url = self.bot.user.display_avatar.url if self.bot.user else None
                simple_embed.set_footer(text="Use the “automod logging” command to get automod logs if it is not enabled.", icon_url=avatar_url)
                await channel.send(embed=simple_embed, delete_after=30)

                await self.log_action(guild, user, channel, action_taken, reason)

            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_rate_limit(self, message):
        await asyncio.sleep(10)
