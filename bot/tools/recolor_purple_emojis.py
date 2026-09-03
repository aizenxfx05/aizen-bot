import os
import re
import sys
import io
import asyncio
import base64
import colorsys
import urllib.request
import aiohttp
from PIL import Image, ImageSequence
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOT_DIR = os.path.join(ROOT_DIR, "bot") if os.path.exists(os.path.join(ROOT_DIR, "bot")) else ROOT_DIR
ENV_PATH = os.path.join(BOT_DIR, ".env")
EMOJI_PY_PATH = os.path.join(BOT_DIR, "utils", "emoji.py")
HELP_PY_PATH = os.path.join(BOT_DIR, "cogs", "commands", "help.py")
OUTPUT_ASSETS_DIR = os.path.join(BOT_DIR, "assets", "purple_emojis")

load_dotenv(ENV_PATH)
TOKEN = os.getenv("TOKEN")

# Target Purple Hue: 275 degrees (Royal Purple / Violet #A855F7)
TARGET_PURPLE_HUE = 275.0 / 360.0

def recolor_frame(img: Image.Image) -> Image.Image:
    """Recolors red pixels in an RGBA image to glowing royal purple."""
    img = img.convert("RGBA")
    pixels = img.load()
    w, h = img.size

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a < 15:
                continue

            # Convert RGB to HSV
            h_val, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

            # Detect red hue range: 0.0 - 0.08 (~0 - 29 deg) or 0.92 - 1.0 (~331 - 360 deg)
            # with saturation > 0.20 to avoid touching pure grayscale/white/black
            if (h_val < 0.08 or h_val > 0.92) and s > 0.20:
                # Enhance saturation slightly for neon glow effect
                s_new = min(1.0, s * 1.15)
                new_r, new_g, new_b = colorsys.hsv_to_rgb(TARGET_PURPLE_HUE, s_new, v)
                pixels[x, y] = (int(new_r * 255), int(new_g * 255), int(new_b * 255), a)

    return img

def recolor_image_bytes(image_data: bytes, is_animated: bool) -> tuple[bytes, str]:
    """Recolors single-frame or animated GIF/WEBP into royal purple."""
    if is_animated:
        try:
            gif = Image.open(io.BytesIO(image_data))
            frames = []
            durations = []
            for frame in ImageSequence.Iterator(gif):
                durations.append(frame.info.get("duration", 100))
                frames.append(recolor_frame(frame))

            out_buf = io.BytesIO()
            frames[0].save(
                out_buf,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                disposal=2
            )
            return out_buf.getvalue(), "image/gif"
        except Exception:
            pass

    # Static PNG
    img = Image.open(io.BytesIO(image_data))
    recolored = recolor_frame(img)
    out_buf = io.BytesIO()
    recolored.save(out_buf, format="PNG")
    return out_buf.getvalue(), "image/png"

def has_red_pixels(image_data: bytes) -> bool:
    """Checks if the image has significant red pixels."""
    try:
        img = Image.open(io.BytesIO(image_data)).convert("RGBA")
        red_count = 0
        pixels = img.load()
        w, h = img.size
        for y in range(h):
            for x in range(w):
                r, g, b, a = pixels[x, y]
                if a > 30 and r > 110 and r > g * 1.25 and r > b * 1.25:
                    red_count += 1
                    if red_count > 30:
                        return True
    except Exception:
        pass
    return False

async def main(upload_to_discord: bool = True):
    print("==================================================")
    print("✦ Aizen XFX — Discord Emojis Purple Theme Transformer")
    print("==================================================")

    os.makedirs(OUTPUT_ASSETS_DIR, exist_ok=True)

    with open(EMOJI_PY_PATH, "r", encoding="utf-8") as f:
        emoji_py_content = f.read()

    # Find all emoji definitions in emoji.py
    pattern = r'(?P<var>[A-Z0-9_]+)\s*=\s*\"<(?P<anim>a?):(?P<name>\w+):(?P<id>\d+)>\"'
    emojis = [m.groupdict() for m in re.finditer(pattern, emoji_py_content)]
    print(f"Loaded {len(emojis)} custom emojis from emoji.py")

    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        # Fetch Bot ID
        app_id = None
        if upload_to_discord and TOKEN:
            async with session.get("https://discord.com/api/v10/users/@me") as r:
                if r.status == 200:
                    bot_info = await r.json()
                    app_id = bot_info.get("id")
                    print(f"✔ Authenticated as Bot: {bot_info.get('username')} (ID: {app_id})")
                else:
                    print(f"✖ Failed to authenticate with bot token [HTTP {r.status}]. Proceeding with local asset generation only.")
                    upload_to_discord = False

        # Get existing application emojis
        existing_app_emojis = {}
        if upload_to_discord and app_id:
            async with session.get(f"https://discord.com/api/v10/applications/{app_id}/emojis") as r:
                if r.status == 200:
                    data = await r.json()
                    items = data.get("items", []) if isinstance(data, dict) else data
                    for item in items:
                        existing_app_emojis[item["name"]] = item["id"]
                    print(f"✔ Found {len(existing_app_emojis)} existing application emojis on Discord")

        recolored_count = 0
        uploaded_count = 0
        patched_emoji_py = emoji_py_content

        for item in emojis:
            var_name = item["var"]
            emoji_name = item["name"]
            emoji_id = item["id"]
            is_animated = item["anim"] == "a"
            ext = "gif" if is_animated else "png"

            cdn_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"

            try:
                req = urllib.request.Request(cdn_url, headers={"User-Agent": "Mozilla/5.0"})
                raw_data = urllib.request.urlopen(req, timeout=5).read()
            except Exception as e:
                continue

            if not has_red_pixels(raw_data):
                continue

            print(f"\n[🔄 Recoloring] {var_name} ({emoji_name})...")
            purple_bytes, mime = recolor_image_bytes(raw_data, is_animated)

            # Save local asset file
            asset_ext = "gif" if is_animated else "png"
            asset_path = os.path.join(OUTPUT_ASSETS_DIR, f"{emoji_name}_purple.{asset_ext}")
            with open(asset_path, "wb") as af:
                af.write(purple_bytes)
            print(f"  ↳ Saved local asset: {os.path.basename(asset_path)}")
            recolored_count += 1

            # Upload to Discord application emojis
            if upload_to_discord and app_id:
                purple_emoji_name = f"p_{emoji_name}"[:32]
                b64 = base64.b64encode(purple_bytes).decode("utf-8")
                data_uri = f"data:{mime};base64,{b64}"

                # Check if p_emoji already exists
                existing_id = existing_app_emojis.get(purple_emoji_name)
                new_emoji_id = None

                if existing_id:
                    new_emoji_id = existing_id
                    print(f"  ↳ Already exists on Discord as '{purple_emoji_name}' [ID: {new_emoji_id}]")
                else:
                    async with session.post(
                        f"https://discord.com/api/v10/applications/{app_id}/emojis",
                        json={"name": purple_emoji_name, "image": data_uri}
                    ) as upload_res:
                        if upload_res.status in (200, 201):
                            res_json = await upload_res.json()
                            new_emoji_id = res_json["id"]
                            existing_app_emojis[purple_emoji_name] = new_emoji_id
                            uploaded_count += 1
                            print(f"  ↳ ✔ Uploaded to Discord as '{purple_emoji_name}' [ID: {new_emoji_id}]")
                        else:
                            err_txt = await upload_res.text()
                            print(f"  ↳ ✖ Discord upload failed: {err_txt}")

                if new_emoji_id:
                    anim_prefix = "a:" if is_animated else ":"
                    old_tag = f"<{anim_prefix}{emoji_name}:{emoji_id}>"
                    new_tag = f"<{anim_prefix}{purple_emoji_name}:{new_emoji_id}>"
                    patched_emoji_py = patched_emoji_py.replace(old_tag, new_tag)

                await asyncio.sleep(0.4)

    # Save updated emoji.py
    if patched_emoji_py != emoji_py_content:
        with open(EMOJI_PY_PATH, "w", encoding="utf-8") as f:
            f.write(patched_emoji_py)
        print("\n✔ Successfully patched emoji.py with updated purple emoji IDs!")

    print(f"\n==================================================")
    print(f"✦ Finished! Recolored: {recolored_count} emojis | Uploaded to Discord: {uploaded_count}")
    print(f"✦ Local purple assets saved at: {OUTPUT_ASSETS_DIR}")
    print(f"==================================================")

if __name__ == "__main__":
    asyncio.run(main(upload_to_discord=True))
