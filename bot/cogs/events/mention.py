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

from utils import getConfig
from utils.config import BotName, DASHBOARD_URL
import discord
from utils.emoji import ARROWRED, CODEBASE, HEART3, INDEX, AIZEN_LINKS
from discord.ui import LayoutView, TextDisplay, Separator, Container, ActionRow, Select
from discord.ext import commands
from utils.Tools import get_ignore_data
import aiosqlite


class MentionSelectView(LayoutView):
    def __init__(self, message, bot, prefix):
        super().__init__(timeout=300)
        self.message = message
        self.bot = bot
        self.prefix = prefix

        self.select = Select(
            placeholder=f"Start With {BotName}",
            options=[
                discord.SelectOption(
                    label="Home",
                    emoji=INDEX,
                    description="Go to the main menu",
                ),
                discord.SelectOption(
                    label="Developer Info",
                    emoji=CODEBASE,
                    description="See who created me",
                ),
                discord.SelectOption(
                    label="Links",
                    emoji=AIZEN_LINKS,
                    description="Useful bot links",
                ),
            ],
        )
        self.select.callback = self.on_select

        self.add_item(
            Container(
                TextDisplay(f"**{message.guild.name}**"),
                Separator(visible=True),
                TextDisplay(
                    f"> {HEART3} **Hey {message.author.mention}**\n"
                    f"> {ARROWRED} **Prefix For This Server: `{prefix}`**\n\n"
                    f"___Type `{prefix}help` for more information.___"
                ),
                ActionRow(self.select),
            )
        )

    async def on_select(self, interaction: discord.Interaction):
        if interaction.user.id != self.message.author.id:
            await interaction.response.send_message(
                "This menu is not for you!", ephemeral=True
            )
            return

        selected = interaction.data.get("values", ["Home"])[0]

        if selected == "Home":
            content = (
                f"> {HEART3} **Hey {interaction.user.mention}**\n"
                f"> {ARROWRED} **Prefix For This Server: `{self.prefix}`**\n\n"
                f"___Type `{self.prefix}help` for more information.___"
            )
        elif selected == "Developer Info":
            content = (
                "There are only 2 Founders Who Created Me. Thanks You To Them 💞.\n\n"
                "**The Founder**\n"
                "**[01]. [Ray](https://discord.com/users/870179991462236170)**\n**[02]. [runxking](https://discord.com/users/767979794411028491)**"
            )
        elif selected == "Links":
            bot_id = interaction.client.user.id if interaction.client.user else "1545041086450507856"
            content = (
                f"**[Dashboard]({DASHBOARD_URL})**\n"
                f"**[Invite {BotName}](https://discord.com/oauth2/authorize?client_id={bot_id}&permissions=8&integration_type=0&scope=bot+applications.commands)**\n"
                "**[Join Support Server](https://discord.gg/M8qJ9W7vBb)**"
            )

        new_container = Container(
            TextDisplay(f"**{self.message.guild.name}**"),
            Separator(visible=True),
            TextDisplay(content),
            ActionRow(self.select),
        )

        self.clear_items()
        self.add_item(new_container)

        await interaction.response.edit_message(view=self)


import os
import time
import asyncio
from discord.ui import Button, View


class Mention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xA855F7
        self.bot_name = BotName
        self.db_path = "db/tagbot.db"
        self._cooldowns = {}
        self.bot.loop.create_task(self._ensure_db())

    async def _ensure_db(self):
        os.makedirs("db", exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tagbot_config (
                    guild_id INTEGER PRIMARY KEY,
                    enabled INTEGER DEFAULT 1,
                    trigger_type TEXT DEFAULT 'single',
                    response_type TEXT DEFAULT 'default',
                    custom_message TEXT DEFAULT NULL,
                    custom_title TEXT DEFAULT NULL,
                    custom_color TEXT DEFAULT '#A855F7',
                    custom_image TEXT DEFAULT NULL,
                    custom_thumbnail TEXT DEFAULT NULL,
                    show_invite INTEGER DEFAULT 1,
                    show_support INTEGER DEFAULT 1,
                    show_dashboard INTEGER DEFAULT 1,
                    auto_delete INTEGER DEFAULT 0,
                    alert_channel_id TEXT DEFAULT NULL,
                    alert_enabled INTEGER DEFAULT 0
                )
            """)
            await db.commit()

    async def get_config(self, guild_id: int):
        await self._ensure_db()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM tagbot_config WHERE guild_id = ?", (guild_id,)) as cur:
                row = await cur.fetchone()
                if row:
                    return dict(row)
        return {
            "guild_id": guild_id,
            "enabled": 1,
            "trigger_type": "single",
            "response_type": "default",
            "custom_message": None,
            "custom_title": None,
            "custom_color": "#A855F7",
            "custom_image": None,
            "custom_thumbnail": None,
            "show_invite": 1,
            "show_support": 1,
            "show_dashboard": 1,
            "auto_delete": 0,
            "alert_channel_id": None,
            "alert_enabled": 0
        }

    async def is_blacklisted(self, message):
        async with aiosqlite.connect("db/block.db") as db:
            cursor = await db.execute(
                "SELECT 1 FROM guild_blacklist WHERE guild_id = ?", (message.guild.id,)
            )
            if await cursor.fetchone():
                return True
            cursor = await db.execute(
                "SELECT 1 FROM user_blacklist WHERE user_id = ?", (message.author.id,)
            )
            if await cursor.fetchone():
                return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if not self.bot.user or self.bot.user not in message.mentions:
            return

        if await self.is_blacklisted(message):
            return

        ignore_data = await get_ignore_data(message.guild.id)
        if (
            str(message.author.id) in ignore_data["user"]
            or str(message.channel.id) in ignore_data["channel"]
        ):
            return

        config = await self.get_config(message.guild.id)
        if not config.get("enabled", 1):
            return

        trigger_type = config.get("trigger_type", "single")
        words = message.content.strip().split()
        if trigger_type == "single" and len(words) != 1:
            return

        # Cooldown guard: 4s per channel to prevent flood
        cooldown_key = f"{message.guild.id}_{message.channel.id}"
        now = time.time()
        if cooldown_key in self._cooldowns and (now - self._cooldowns[cooldown_key]) < 4:
            return
        self._cooldowns[cooldown_key] = now

        guild_id = message.guild.id
        data = await getConfig(guild_id)
        prefix = data["prefix"]

        # 1. Mention Alert Logging (if enabled)
        if config.get("alert_enabled") and config.get("alert_channel_id"):
            try:
                alert_ch = self.bot.get_channel(int(config["alert_channel_id"]))
                if alert_ch and alert_ch.permissions_for(alert_ch.guild.me).send_messages:
                    alert_embed = discord.Embed(
                        title="🔔 Bot Mention Alert",
                        description=(
                            f"**Mentioned By:** {message.author.mention} (`{message.author.id}`)\n"
                            f"**Channel:** {message.channel.mention}\n"
                            f"**Message Content:**\n```{message.content[:300]}```\n"
                            f"**Jump to Message:** [Click Here]({message.jump_url})"
                        ),
                        color=0xA855F7,
                        timestamp=discord.utils.utcnow()
                    )
                    if message.author.display_avatar:
                        alert_embed.set_thumbnail(url=message.author.display_avatar.url)
                    alert_embed.set_footer(
                        text=f"Server: {message.guild.name}",
                        icon_url=message.guild.icon.url if message.guild.icon else None
                    )
                    await alert_ch.send(embed=alert_embed)
            except Exception:
                pass

        # 2. Tag Bot Response
        auto_del = int(config.get("auto_delete") or 0)
        sent_msg = None

        if config.get("response_type") == "custom" and (config.get("custom_message") or config.get("custom_title")):
            raw_color = config.get("custom_color") or "#A855F7"
            try:
                embed_color = int(raw_color.lstrip("#"), 16)
            except ValueError:
                embed_color = 0xA855F7

            title = config.get("custom_title")
            desc = config.get("custom_message") or f"Hey {message.author.mention}! My prefix for this server is `{prefix}`."
            desc = (
                desc.replace("{user}", message.author.mention)
                .replace("{user_name}", message.author.name)
                .replace("{server}", message.guild.name)
                .replace("{prefix}", prefix)
            )

            embed = discord.Embed(
                title=title if title else None,
                description=desc,
                color=embed_color
            )
            if config.get("custom_thumbnail"):
                embed.set_thumbnail(url=config["custom_thumbnail"])
            elif self.bot.user and self.bot.user.display_avatar:
                embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            if config.get("custom_image"):
                embed.set_image(url=config["custom_image"])

            embed.set_footer(
                text=f"Powered by {self.bot_name}™",
                icon_url=self.bot.user.display_avatar.url if self.bot.user else None
            )

            # Build action buttons
            view = View()
            bot_id = self.bot.user.id if self.bot.user else "1545041086450507856"
            if config.get("show_invite", 1):
                view.add_item(Button(
                    label=f"Invite {self.bot_name}",
                    style=discord.ButtonStyle.link,
                    url=f"https://discord.com/oauth2/authorize?client_id={bot_id}&permissions=8&integration_type=0&scope=bot+applications.commands"
                ))
            if config.get("show_support", 1):
                view.add_item(Button(
                    label="Support",
                    style=discord.ButtonStyle.link,
                    url="https://discord.gg/M8qJ9W7vBb"
                ))
            if config.get("show_dashboard", 1):
                view.add_item(Button(
                    label="Dashboard",
                    style=discord.ButtonStyle.link,
                    url=DASHBOARD_URL
                ))

            sent_msg = await message.channel.send(embed=embed, view=view if len(view.children) > 0 else None)
        else:
            view = MentionSelectView(message, self.bot, prefix)
            sent_msg = await message.channel.send(view=view)

        # 3. Auto-delete if set
        if sent_msg and auto_del > 0:
            await asyncio.sleep(auto_del)
            try:
                await sent_msg.delete()
            except Exception:
                pass

    @commands.group(name="tagbot", aliases=["mention", "botmention"], invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def tagbot(self, ctx: commands.Context):
        """Displays or manages the Tag Bot & Mention Alert configuration."""
        config = await self.get_config(ctx.guild.id)
        status_str = "Enabled ✅" if config.get("enabled", 1) else "Disabled ❌"
        mode_str = "Single Mention Only (`@Bot`)" if config.get("trigger_type") == "single" else "Any Mention in Message"
        resp_str = "Interactive Menu" if config.get("response_type") == "default" else "Custom Embed"
        alert_ch = f"<#{config['alert_channel_id']}>" if config.get("alert_channel_id") else "None"
        auto_del = f"{config.get('auto_delete')}s" if config.get("auto_delete") else "Disabled"

        embed = discord.Embed(
            title=f"🏷️ Tag Bot & Mention Alert — {ctx.guild.name}",
            description=(
                f"**Status:** {status_str}\n"
                f"**Trigger Mode:** `{mode_str}`\n"
                f"**Response Type:** `{resp_str}`\n"
                f"**Auto Delete:** `{auto_del}`\n"
                f"**Alert Channel:** {alert_ch}\n"
                f"**Alert Logging:** {'Enabled ✅' if config.get('alert_enabled') else 'Disabled ❌'}\n\n"
                f"**Configuration Commands:**\n"
                f"• `{ctx.prefix}tagbot enable` / `disable` — Turn Tag Bot on or off\n"
                f"• `{ctx.prefix}tagbot mode <single|any>` — Set mention detection mode\n"
                f"• `{ctx.prefix}tagbot alertchannel <#channel|none>` — Set mention alert log channel\n"
                f"• `{ctx.prefix}tagbot autodelete <seconds>` — Set auto-delete delay (0 to disable)\n"
                f"• `{ctx.prefix}tagbot reset` — Reset settings to default"
            ),
            color=0xA855F7
        )
        embed.set_footer(text=f"{self.bot_name} Dashboard & Configuration", icon_url=self.bot.user.display_avatar.url if self.bot.user else None)
        await ctx.send(embed=embed)

    @tagbot.command(name="enable")
    @commands.has_permissions(manage_guild=True)
    async def tagbot_enable(self, ctx: commands.Context):
        """Enables Tag Bot for this server."""
        await self._ensure_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO tagbot_config (guild_id, enabled) VALUES (?, 1) ON CONFLICT(guild_id) DO UPDATE SET enabled = 1", (ctx.guild.id,))
            await db.commit()
        await ctx.send("✅ Tag Bot response has been **enabled** for this server.")

    @tagbot.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def tagbot_disable(self, ctx: commands.Context):
        """Disables Tag Bot for this server."""
        await self._ensure_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO tagbot_config (guild_id, enabled) VALUES (?, 0) ON CONFLICT(guild_id) DO UPDATE SET enabled = 0", (ctx.guild.id,))
            await db.commit()
        await ctx.send("❌ Tag Bot response has been **disabled** for this server.")

    @tagbot.command(name="mode")
    @commands.has_permissions(manage_guild=True)
    async def tagbot_mode(self, ctx: commands.Context, mode: str):
        """Sets the trigger mode: 'single' (only lone @Bot ping) or 'any' (bot mention anywhere in message)."""
        mode = mode.lower()
        if mode not in ("single", "any"):
            return await ctx.send("❌ Invalid mode. Choose `single` or `any`.")
        await self._ensure_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO tagbot_config (guild_id, trigger_type) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET trigger_type = ?", (ctx.guild.id, mode, mode))
            await db.commit()
        await ctx.send(f"✅ Tag Bot trigger mode updated to `{mode}`.")

    @tagbot.command(name="alertchannel")
    @commands.has_permissions(manage_guild=True)
    async def tagbot_alertchannel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Sets or removes the mention alert channel."""
        ch_id = str(channel.id) if channel else None
        enabled = 1 if channel else 0
        await self._ensure_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO tagbot_config (guild_id, alert_channel_id, alert_enabled) VALUES (?, ?, ?) ON CONFLICT(guild_id) DO UPDATE SET alert_channel_id = ?, alert_enabled = ?", (ctx.guild.id, ch_id, enabled, ch_id, enabled))
            await db.commit()
        if channel:
            await ctx.send(f"✅ Mention alerts will now be logged in {channel.mention}.")
        else:
            await ctx.send("❌ Mention alert logging has been disabled.")

    @tagbot.command(name="autodelete")
    @commands.has_permissions(manage_guild=True)
    async def tagbot_autodelete(self, ctx: commands.Context, seconds: int):
        """Sets the auto-delete delay in seconds (0 to disable)."""
        if seconds < 0 or seconds > 300:
            return await ctx.send("❌ Please choose a duration between 0 and 300 seconds.")
        await self._ensure_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO tagbot_config (guild_id, auto_delete) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET auto_delete = ?", (ctx.guild.id, seconds, seconds))
            await db.commit()
        await ctx.send(f"✅ Auto-delete set to `{seconds}` seconds.")

    @tagbot.command(name="reset")
    @commands.has_permissions(manage_guild=True)
    async def tagbot_reset(self, ctx: commands.Context):
        """Resets Tag Bot settings to factory defaults."""
        await self._ensure_db()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM tagbot_config WHERE guild_id = ?", (ctx.guild.id,))
            await db.commit()
        await ctx.send("🔄 Tag Bot settings have been reset to default.")


async def setup(bot):
    await bot.add_cog(Mention(bot))

