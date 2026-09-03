<div align="center">

```
  █████╗ ██╗███████╗███████╗███╗   ██╗    ██╗  ██╗███████╗██╗  ██╗
 ██╔══██╗██║╚══███╔╝██╔════╝████╗  ██║    ╚██╗██╔╝██╔════╝╚██╗██╔╝
 ███████║██║  ███╔╝ █████╗  ██╔██╗ ██║     ╚███╔╝ █████╗   ╚███╔╝
 ██╔══██║██║ ███╔╝  ██╔══╝  ██║╚██╗██║     ██╔██╗ ██╔══╝   ██╔██╗
 ██║  ██║██║███████╗███████╗██║ ╚████║    ██╔╝ ██╗██║      ██╔╝ ██╗
 ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝  ╚═╝╚═╝      ╚═╝  ╚═╝
```

<h3>Power. Elegance. Dominance.</h3>
<h4>A feature-rich Discord bot with AI chat, channel restore, and a premium dark-gold dashboard</h4>

<a href="https://nexiohost.in"><img src="https://img.shields.io/badge/⭐%20PREMIUM%20HOSTING-NexioHost-FFD700?style=for-the-badge&labelColor=1a1a2e&color=FFD700&logoColor=FFD700"/></a>

<p>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/></a>
  <a href="https://nextjs.org"><img src="https://img.shields.io/badge/Next.js-14+-000000?style=for-the-badge&logo=nextdotjs&logoColor=white"/></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white"/></a>
  <a href="https://discordpy.readthedocs.io"><img src="https://img.shields.io/badge/Discord.py-v2-5865F2?style=for-the-badge&logo=discord&logoColor=white"/></a>
  <a href="https://console.groq.com"><img src="https://img.shields.io/badge/Groq-AI%20Powered-D4AF37?style=for-the-badge&logoColor=white"/></a>
</p>
<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-D4AF37?style=for-the-badge"/></a>
  <a href="https://discord.gg/M8qJ9W7vBb"><img src="https://img.shields.io/badge/Discord-Join_Server-5865F2?style=for-the-badge&logo=discord&logoColor=white"/></a>
  <a href="https://youtube.com/@aizen_xfx"><img src="https://img.shields.io/badge/YouTube-Aizen_XFX-FF0000?style=for-the-badge&logo=youtube&logoColor=white"/></a>
  <a href="https://github.com/RayExo"><img src="https://img.shields.io/badge/GitHub-RayExo-181717?style=for-the-badge&logo=github&logoColor=white"/></a>
</p>

</div>

---

## ✦ Overview

**Aizen XFX** is a fully-featured Discord bot with a premium dark-gold web dashboard. Built on `discord.py v2`, `FastAPI`, and `Next.js 14` with Tailwind CSS.

New in this release:
- 🤖 **AI Voice Chat** — Groq-powered LLaMA AI replies in voice-linked text channels
- 🔄 **Channel Restore** — Auto-restores deleted voice/text channels (works without antinuke)
- 🔒 **Security v2** — Timing-safe API auth, HTTP security headers, startup validation
- 🎨 **Premium Gold Theme** — Dark obsidian + royal gold dashboard UI

```
Aizen-XFX-With-Dashboard/
├── 🤖  bot/                   Python Discord bot + FastAPI backend
│   ├── api/                   Dashboard REST API (FastAPI)
│   ├── cogs/                  All bot features (commands, events, antinuke, automod…)
│   │   └── events/
│   │       ├── vc_ai_chat.py  🆕 AI replies in voice text channels (Groq)
│   │       └── channel_restore.py  🆕 Independent channel restore system
│   ├── core/                  Bot client, context, cog base
│   ├── utils/                 Shared utilities (emoji, tools, sync, cloudflare tunnel…)
│   ├── games/                 Standalone game modules
│   ├── assets/                Fonts, backgrounds, GIFs
│   └── CodeX.py               Entry point
│
└── 🌐  dashboard/             Next.js frontend (Dark Gold Theme)
    ├── app/                   App Router pages & API routes
    ├── components/            Reusable UI components
    ├── hooks/                 Custom React hooks
    ├── lib/                   API helpers & utilities
    └── types/                 TypeScript type definitions
```

---

## ✦ Features

<table>
<tr>
<td width="50%">

**🛡️ Security v2**
- Antinuke — ban, kick, channel & role flood, webhook abuse, bot adds, prune
- Automod — spam, caps, links, invites, mass mentions, emoji spam
- **Timing-safe API auth** via `hmac.compare_digest` (anti timing attack)
- **HTTP security headers** on every API response
- **Startup key validation** — crashes early if secret is unset
- Whitelist / unwhitelist system
- Emergency lockdown mode

</td>
<td width="50%">

**🤖 AI Voice Chat** _(New)_
- Powered by **Groq API + LLaMA 3** (ultra-fast, free tier)
- Activates in voice-linked text channels automatically
- Per-channel conversation history (context-aware)
- Typing indicator while generating reply
- NSFW content filter on input and output
- `>vc-ai-clear` to reset channel memory
- Requires just one env var: `GROQ_API_KEY`

</td>
</tr>
<tr>
<td>

**🔄 Channel Restore** _(New)_
- Auto-recreates deleted text, voice, or stage channels
- Works **independently** of antinuke — no ban required
- Respects guild owner, extra owners & whitelist
- Rate-limited: max 5 restores per 10 seconds
- Gold embed logs to a configured channel
- `>restore enable/disable/status/logchannel`

</td>
<td>

**🎵 Music**
- Lavalink v4 powered playback
- YouTube, SoundCloud, JioSaavn search
- Queue, loop, autoplay, shuffle
- Seek, rewind, forward controls
- Fully configurable via `.env`

</td>
</tr>
<tr>
<td>

**⚙️ Management**
- Moderation — ban, kick, mute, warn, lock, jail, and more
- Full logging system
- Reaction roles, vanity roles, invite tracker
- Tickets, giveaways, verification
- Join-to-create voice channels

</td>
<td>

**🌐 Dashboard** _(Gold Theme)_
- Discord OAuth2 login
- Per-server settings management
- Live bot stats & metrics
- **Premium dark obsidian + royal gold** UI
- HTTPS via Cloudflare Tunnel (permanent URL)
- Deploys to Vercel in minutes

</td>
</tr>
<tr>
<td>

**🎉 Engagement**
- Leveling & XP system with leaderboard
- Birthday tracker
- 12+ mini-games (chess, battleship, wordle, 2048…)
- AFK system, autorole, autoresponder, sticky messages
- Counting, blackjack, slots, booster perks

</td>
<td>

**🔧 Developer**
- Application emoji auto-sync on startup
- Jishaku eval support
- Slash + prefix commands
- FastAPI backend with API key auth + rate limiting (200 req/min)
- Cloudflare Tunnel — unlimited bandwidth, permanent URL, zero system installs

</td>
</tr>
</table>

---

## ✦ Prerequisites

| Requirement | Version / Notes |
|---|---|
| Python | 3.10 or higher |
| Node.js | 18 or higher |
| Lavalink node | v4 |
| Discord bot token | — |
| Discord OAuth app | for dashboard login |
| Groq API key (free) | for AI voice chat feature |
| Cloudflare account (free) | for HTTPS tunnel |

---

## ✦ Bot Setup

**1 — Clone the repo**

```bash
git clone https://github.com/RayExo/Aizen-XFX-With-Dashboard
cd Aizen-XFX-With-Dashboard/bot
```

**2 — Install dependencies**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

**3 — Configure the environment**

Copy `.env.example` to `.env` and fill in the values:

```env
# ── Core ──────────────────────────────────────────────────────────
TOKEN              = your_discord_bot_token
brand_name         = 'Aizen XFX'

# ── Owner IDs (comma-separated) ───────────────────────────────────
OWNER_IDS          = your_discord_user_id

# ── AI / Groq (for VC AI Chat feature) ───────────────────────────
# Get your free key at: https://console.groq.com
GROQ_API_KEY       = your_groq_api_key

# ── Lavalink ──────────────────────────────────────────────────────
LAVALINK_HOST      = "your-lavalink-host"
LAVALINK_PASSWORD  = "your_password"
LAVALINK_SECURE    = "true"
LAVALINK_PORT      = ""

# ── Emoji Sync ────────────────────────────────────────────────────
EMOJI_SYNC         = "true"

# ── API / Dashboard Backend ───────────────────────────────────────
API_ENABLED        = "true"
API_PORT           = "8000"
DASHBOARD_API_KEY  = "change_this_to_a_VERY_strong_secret"   # ⚠️ required
CORS_ORIGINS       = ""

# ── Cloudflare Tunnel ─────────────────────────────────────────────
TUNNEL_ENABLED     = "true"
CF_TUNNEL_TOKEN    = "your_tunnel_token"
CF_TUNNEL_URL      = "https://aizen-api.yourdomain.com"

# ── Webhooks ──────────────────────────────────────────────────────
WEBHOOK_URL        = "https://discord.com/api/webhooks/..."
```

**4 — Run the bot**

```bash
python CodeX.py
```

The bot will print the Aizen XFX ASCII banner in gold on startup.

---

## ✦ Dashboard Setup

**1 — Install dependencies**

```bash
cd dashboard
npm install
```

**2 — Configure the environment**

Copy `.env.example` to `.env.local`:

```env
NEXT_PUBLIC_API_URL           = https://aizen-api.yourdomain.com/api/v1
NEXT_PUBLIC_DASHBOARD_API_KEY = your_shared_api_key   # Must match bot DASHBOARD_API_KEY

NEXTAUTH_URL                  = http://localhost:3000
NEXTAUTH_SECRET               = a_long_random_string

DISCORD_CLIENT_ID             = your_discord_oauth_client_id
DISCORD_CLIENT_SECRET         = your_discord_oauth_client_secret

NEXT_PUBLIC_ADMIN_IDS         = your_discord_user_id
NEXT_PUBLIC_BRAND_NAME        = "Aizen XFX"
NEXT_PUBLIC_BRAND_NAME_WORD   = "AX"
```

**3 — Run locally**

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## ✦ AI Voice Chat Setup

The AI feature uses **Groq** (free tier, extremely fast LLaMA 3 inference).

1. Go to [console.groq.com](https://console.groq.com) → create a free API key
2. Add to `bot/.env`:
   ```env
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
3. The bot automatically responds in **voice-linked text channels** — no configuration needed.

**Supported channel types:**
- Discord native voice-linked text channels (VoiceChannel, StageChannel)
- Text channels whose name ends with `-vc`, `-voice`, `-text`, `-chat`, `-talk` when a matching voice channel exists

**Commands:**
```
>vc-ai-clear    — Clear the AI conversation history for the current channel
                  (Requires: Manage Channels)
```

---

## ✦ Channel Restore Setup

The channel restore system works **independently of antinuke** — it does not ban anyone, it simply recreates deleted channels.

**Enable in your server:**
```
>restore enable                  — Turn on channel restore
>restore disable                 — Turn off channel restore
>restore status                  — Check if enabled
>restore logchannel #channel     — Set the log channel for restore events
```

**How it works:**
- Listens for `on_guild_channel_delete` events
- Checks audit logs to find the executor
- Skips if executor is: guild owner, extra owner, or whitelisted
- Clones the deleted channel back to its original position
- Sends a gold embed to your configured log channel
- Rate-limited to 5 restores per 10 seconds to prevent abuse

> Requires the bot to have **Manage Channels** and **View Audit Log** permissions.

---

## ✦ Environment Reference

### Bot — `bot/.env`

| Variable | Default | Description |
|---|---|---|
| `TOKEN` | — | Discord bot token |
| `brand_name` | `Aizen XFX` | Bot brand name shown in statuses |
| `OWNER_IDS` | — | Comma-separated owner Discord user IDs |
| `GROQ_API_KEY` | — | Groq API key for AI voice chat (free at console.groq.com) |
| `LAVALINK_HOST` | — | Lavalink server hostname (no protocol) |
| `LAVALINK_PASSWORD` | — | Lavalink password |
| `LAVALINK_SECURE` | `true` | `true` = HTTPS, `false` = HTTP |
| `LAVALINK_PORT` | _(empty)_ | Port — only needed when `LAVALINK_SECURE=false` |
| `EMOJI_SYNC` | `true` | Run application emoji sync on startup |
| `API_ENABLED` | `true` | Start the FastAPI dashboard backend |
| `API_PORT` | `8000` | Port the backend listens on |
| `DASHBOARD_API_KEY` | — | **Required.** Shared secret between bot API and dashboard |
| `CORS_ORIGINS` | _(empty)_ | Extra CORS-allowed origins, comma-separated |
| `WEBHOOK_URL` | — | Discord webhook for command logs |
| `TUNNEL_ENABLED` | `true` | Expose the API over HTTPS via Cloudflare Tunnel |
| `CF_TUNNEL_TOKEN` | — | Token from Cloudflare Zero Trust dashboard |
| `CF_TUNNEL_URL` | — | Your permanent public URL (e.g. `https://aizen-api.yourdomain.com`) |

### Dashboard — `dashboard/.env.local`

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Full URL to the bot's FastAPI backend — use Cloudflare Tunnel URL |
| `NEXT_PUBLIC_DASHBOARD_API_KEY` | Must match `DASHBOARD_API_KEY` in the bot |
| `NEXTAUTH_URL` | Your dashboard's public URL |
| `NEXTAUTH_SECRET` | Random secret for NextAuth session signing |
| `DISCORD_CLIENT_ID` | Discord OAuth2 client ID |
| `DISCORD_CLIENT_SECRET` | Discord OAuth2 client secret |
| `NEXT_PUBLIC_ADMIN_IDS` | Comma-separated Discord user IDs with admin access |
| `NEXT_PUBLIC_BRAND_NAME` | Bot name shown in the dashboard UI (e.g. `Aizen XFX`) |
| `NEXT_PUBLIC_BRAND_NAME_WORD` | Short abbreviation shown in the dashboard (e.g. `AX`) |

---

## ✦ HTTPS Tunnel (Cloudflare)

The bot uses **pycloudflared** — a Python package that downloads the `cloudflared` binary automatically on first run. No CLI installs, no system packages — works on Pterodactyl and any Python host.

**Why Cloudflare over ngrok:**
- ✅ Unlimited bandwidth & requests — no monthly caps
- ✅ Permanent URL that never changes between restarts
- ✅ Free — no paid plan needed
- ✅ Zero system installs — binary downloads via Python

**Setup (browser only, no CLI needed):**

1. Go to [one.dash.cloudflare.com](https://one.dash.cloudflare.com) → **Networks → Tunnels → Create a tunnel**
2. Choose **Cloudflared**, give it a name (e.g. `aizen-api`), save
3. On the **Install connector** step, copy the token from the command shown:
   ```
   cloudflared tunnel run --token <COPY_THIS>
   ```
4. Go to **Public Hostname** tab → add a hostname:
   - Subdomain: `aizen-api` · Domain: `yourdomain.com` · Service: `http://localhost:8000`
5. Add to `bot/.env`:
   ```env
   CF_TUNNEL_TOKEN = "eyJhIjoiXXXX..."
   CF_TUNNEL_URL   = "https://aizen-api.yourdomain.com"
   ```

On every startup the console prints:
```
◈ Tunnel: cloudflared binary ready — starting tunnel on port 8000…
◈ Tunnel: API is live at  https://aizen-api.yourdomain.com
  ↳ NEXT_PUBLIC_API_URL = https://aizen-api.yourdomain.com/api/v1
```

---

## ✦ Deployment

### 🤖 Bot — any Python host

1. Upload the entire `bot/` folder to your host (Pterodactyl, Render, Railway, Fly.io, VPS…)
2. Set the start command to `python CodeX.py`
3. Add all environment variables (including `GROQ_API_KEY` and `DASHBOARD_API_KEY`)
4. `pycloudflared` downloads the binary automatically on first run — no extra steps

> Recommended free/cheap hosts: Render · Railway · Fly.io · VPS
>
> ⭐ **[NexioHost](https://nexiohost.in)** — Premium bot hosting, built for Discord bots. Fast, reliable, and affordable.

### 🌐 Dashboard — Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New Project** → connect your GitHub repo
2. Set root directory to `dashboard/`
3. Add all environment variables under **Settings → Environment Variables**
4. Add the OAuth redirect URI in Discord Developer Portal:
   ```
   https://your-app.vercel.app/api/auth/callback/discord
   ```
5. Hit **Deploy** — done ✓

---

## ✦ Emoji Sync

Runs automatically on startup when `EMOJI_SYNC=true`:

```
★ Starting Application Emoji Sync — 144 unique emojis found in emoji.py
◈ Found 144 templates | Application hosts 202 emojis
↑ Uploading: ztick  (not in application emojis)
✔ Uploaded: ztick  [saved as ID: 1234567890]
✔ emoji.py patched in-place to reflect current API state.
★ Restarting bot to load updated emoji IDs...
```

| Event | Action |
|---|---|
| New emoji found | Uploaded to application, ID written to `emoji.py` |
| Stale ID detected | `emoji.py` patched automatically |
| No changes | Sync completes instantly, no restart |
| After any patch | Bot restarts itself so fresh IDs are live |

---

## ✦ Troubleshooting

| Problem | Fix |
|---|---|
| Bot fails to start | Check `TOKEN` is set and bot has correct gateway intents |
| AI not responding | Verify `GROQ_API_KEY` is set and channel is voice-linked |
| AI replies in wrong channels | Only voice-linked channels or channels ending in `-vc`, `-voice`, `-text`, etc. |
| Channel restore not working | Run `>restore enable` and ensure bot has **Manage Channels** + **View Audit Log** |
| Music not working | Verify `LAVALINK_HOST`, `LAVALINK_SECURE`, and `LAVALINK_PORT` |
| Dashboard auth error | Check Discord OAuth client ID/secret and redirect URI |
| Dashboard can't load data | Confirm `API_ENABLED=true`, bot is running, `NEXT_PUBLIC_API_URL` is correct |
| API returns 401 | `DASHBOARD_API_KEY` in bot `.env` must match `NEXT_PUBLIC_DASHBOARD_API_KEY` in dashboard |
| API returns 500 at startup | `DASHBOARD_API_KEY` is not set — it is now required at startup |
| Emojis showing as plain text | Run with `EMOJI_SYNC=true` once to upload and patch IDs |
| CORS errors from dashboard | Add your Vercel URL to `CORS_ORIGINS` in `bot/.env` |
| Tunnel not starting | Check `CF_TUNNEL_TOKEN` is valid and `pycloudflared` is installed |
| Tunnel URL changed | Set `CF_TUNNEL_URL` — named tunnels always produce the same URL |

---

## ✦ Security

- **Never commit `.env` files** — `.gitignore` already covers them
- Use a **strong, unique** `NEXTAUTH_SECRET` and `DASHBOARD_API_KEY` (32+ random chars)
- The API now uses **timing-safe comparison** — safe against timing attacks
- **HTTP security headers** are injected on every API response automatically
- The bot will **refuse to start** if `DASHBOARD_API_KEY` is not set
- Rotate any secret that gets accidentally exposed

---

<div align="center">

## ✦ Aizen XFX

*Power. Elegance. Dominance.*

<a href="https://discord.gg/M8qJ9W7vBb"><img src="https://discord.com/api/guilds/1301573144817045524/widget.png?style=banner2" alt="CodeX Development Discord Server" width="480"/></a>

<p>
  <a href="https://discord.gg/M8qJ9W7vBb"><img src="https://img.shields.io/badge/Discord-Join_Server-5865F2?style=for-the-badge&logo=discord&logoColor=white"/></a>
  <a href="https://youtube.com/@aizen_xfx"><img src="https://img.shields.io/badge/YouTube-Aizen_XFX-FF0000?style=for-the-badge&logo=youtube&logoColor=white"/></a>
  <a href="https://github.com/RayExo"><img src="https://img.shields.io/badge/GitHub-RayExo-181717?style=for-the-badge&logo=github&logoColor=white"/></a>
  <a href="https://nexiohost.in"><img src="https://img.shields.io/badge/⭐%20PREMIUM%20HOSTING-NexioHost-FFD700?style=for-the-badge&labelColor=1a1a2e&color=FFD700&logoColor=FFD700"/></a>
</p>

© 2026 Aizen XFX — MIT License

</div>
