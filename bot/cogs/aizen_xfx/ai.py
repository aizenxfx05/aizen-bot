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
from utils.emoji import ZAI
from discord .ext import commands 

class _ai (commands .Cog ):
    def __init__ (self ,bot ):
        self .bot =bot 

    """AI commands"""

    def help_custom (self ):
        emoji =ZAI
        label ="AI Commands"
        description ="Show you the commands of AI"
        return emoji ,label ,description 

    @commands .group ()
    async def __AI__ (self ,ctx :commands .Context ):
        """`ai activate`, `ai deactivate`, `ai analyze`, `ai analyse`, `ai code`, `ai explain`, `ai conversation-clear`, `ai mood-analyzer`, `ai personality`, `ai conversation-stats`, `ai summarize`, `ai ask`, `ai fact`, `ai database-clear`, `ai roleplay-enable`, `ai roleplay-disable`"""
        pass 
