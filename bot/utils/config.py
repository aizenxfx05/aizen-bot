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

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN      = os.environ.get("TOKEN")
BRAND_NAME = os.environ.get("brand_name", "Aizen XFX")
NAME       = BRAND_NAME
BotName    = BRAND_NAME

server     = "https://discord.gg/M8qJ9W7vBb"
serverLink = "https://discord.gg/M8qJ9W7vBb"
ch         = "https://discord.com/channels/699587669059174461/1271825678710476911"

# AI / Groq config
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

CMD_WEBHOOK_URL = os.getenv("CMD_WEBHOOK_URL")

# ── Owner / Staff IDs ─────────────────────────────────────────────────────────
# Edit OWNER_IDS in .env — comma-separated, no spaces needed.
# Example:  OWNER_IDS = 870179991462236170,767979794411028491,1432771000629596225

def _parse_ids(env_key: str, defaults: list[int]) -> list[int]:
    raw = os.getenv(env_key, "").strip()
    if not raw:
        return defaults
    ids = [int(p.strip()) for p in raw.split(",") if p.strip().isdigit()]
    return ids or defaults

OWNER_IDS:     list[int] = _parse_ids("OWNER_IDS",     [870179991462236170])
OWNER_IDS_STR: list[str] = [str(i) for i in OWNER_IDS]

# Aliases kept for backwards compatibility with files that import these names
BOT_OWNER_IDS     = OWNER_IDS
BOT_OWNER_IDS_STR = OWNER_IDS_STR
STAFF_IDS         = OWNER_IDS
STAFF_IDS_STR     = OWNER_IDS_STR