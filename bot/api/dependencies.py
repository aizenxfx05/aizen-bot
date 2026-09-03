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
import hmac
import logging
from typing import Optional, TYPE_CHECKING
from fastapi import HTTPException, Depends, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from slowapi import Limiter
from slowapi.util import get_remote_address

if TYPE_CHECKING:
    from core.zyrox import zyrox

auth_logger = logging.getLogger("auth")
if not auth_logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[AUTH] %(asctime)s %(message)s"))
    auth_logger.addHandler(_h)
auth_logger.setLevel(logging.WARNING)

# Initialize rate limiter — stricter defaults
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per minute"])

# Global reference to the bot instance
_bot_instance: Optional["zyrox"] = None

# Security scheme
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Dependency to verify the API key from the Authorization header.
    Expected: Authorization: Bearer <API_KEY>
    Uses hmac.compare_digest for constant-time comparison (prevents timing attacks).
    """
    api_key = os.getenv("DASHBOARD_API_KEY", "")

    # Reject if the server never set a key
    if not api_key:
        auth_logger.error("DASHBOARD_API_KEY is not configured — all requests blocked.")
        raise HTTPException(
            status_code=500,
            detail="Server is misconfigured: DASHBOARD_API_KEY is not set."
        )

    # Constant-time comparison to prevent timing attacks
    provided = credentials.credentials if credentials else ""
    is_valid = hmac.compare_digest(
        provided.encode("utf-8"),
        api_key.encode("utf-8")
    )

    if not is_valid:
        auth_logger.warning("Failed API auth attempt with key starting: %s...", provided[:6] if provided else "(empty)")
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

def set_bot(bot_instance: "zyrox"):
    """
    Sets the global bot instance. 
    This should be called in CodeX.py during startup.
    """
    global _bot_instance
    _bot_instance = bot_instance

def get_bot() -> "zyrox":
    """
    FastAPI dependency to retrieve the Discord bot instance.
    Usage: bot: zyrox = Depends(get_bot)
    """
    if _bot_instance is None:
        raise HTTPException(
            status_code=503, 
            detail="Discord bot instance is not initialized yet."
        )
    return _bot_instance
