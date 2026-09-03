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
from utils.emoji import GAMES
from discord.ext import commands


class _games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Games commands"""

    def help_custom(self):
        emoji = GAMES
        label = "Games Commands"
        description = "Show you Commands of Games"
        return emoji, label, description

    @commands.group()
    async def __Games__(self, ctx: commands.Context):
        """`blackjack` , `chess` , `tic-tac-toe` , `country-guesser` , `rps` , `lights-out` , `wordle` , `2048` , `memory-game` , `number-slider` , `battleship` , `connect-four` , `slots`, `counting`"""
