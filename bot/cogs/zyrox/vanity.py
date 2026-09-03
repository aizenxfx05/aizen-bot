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

import discord
from utils.emoji import STAR

from discord.ext import commands

class _vanity(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    """Vanity Roles"""

    def help_custom(self):

              emoji = STAR

              label = "Vanity"

              description = "Show you Commands of Vanity Roles"

              return emoji, label, description

    @commands.group()

    async def __Vanity__(self, ctx: commands.Context):

        """`>vanityroles setup` , `>vanityroles reset `, `>vanityroles show` ,"""