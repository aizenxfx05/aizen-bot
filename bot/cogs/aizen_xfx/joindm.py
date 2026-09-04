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
from utils.emoji import MESSAGE
from discord.ext import commands

class _joindm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    """__Join Dm__"""
    def help_custom(self):
              emoji = MESSAGE
              label = "Joindm"
              description = "Show you Commands of Joindm"
              return emoji, label, description
    @commands.group()
    async def __Joindm__(self, ctx: commands.Context):
        """`joindm enable` , `joindm disable` , `joindm message` , `joindm test`"""