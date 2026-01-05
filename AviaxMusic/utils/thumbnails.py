import os
import aiofiles
import aiohttp
import textwrap
import asyncio

from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance, ImageChops
from py_yt import VideosSearch

from config import YOUTUBE_IMG_URL

# Fonts load karte waqt try-except lagana behtar hai
try:
    font1 = ImageFont.truetype("AviaxMusic/assets/font2.ttf", 45)
    font2 = ImageFont.truetype("AviaxMusic/assets/font2.ttf", 30)
except:
    font1 = ImageFont.load_default()
    font2 = ImageFont.load_default()

circle = Image.new("RGBA", (1280, 720), 0)

async def gen_thumb(video_id: str, center_crop = 250, img_size = (1280, 720)) -> str:
    out = f"cache/{video_id}.png"
    if os.path.isfile(out):
        return out

    thumbnail = None # Initialize thumbnail to avoid 'referenced before assignment'
    title = "Unsupported Title"
    duration = "Unknown"

    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        results = VideosSearch(url, limit=1)
        res = await results.next()
        
        if res and "result" in res and len(res["result"]) > 0:
            result = res["result"][0]
            title = result.get("title", "Unsupported Title").title()
            duration = result.get("duration", "00:00")
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        else:
            return YOUTUBE_IMG_URL
    except Exception as e:
        print(f"Error fetching video details: {e}")
        return YOUTUBE_IMG_URL

    # Agar thumbnail URL nahi mila toh default return karein
    if not thumbnail:
        return YOUTUBE_IMG_URL

    # SSL aur Timeout settings ke saath download karein
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        try:
            async with session.get(thumbnail, timeout=10) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{video_id}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()
                else:
                    return YOUTUBE_IMG_URL
        except Exception as e:
            print(f"Error downloading thumbnail: {e}")
            return YOUTUBE_IMG_URL

    try:
        thumb = Image.open(f"cache/thumb{video_id}.png").convert("RGBA")
        bg = (
            thumb.resize(img_size)
            .filter(ImageFilter.BoxBlur(30))
        )
        bg = ImageEnhance.Brightness(bg).enhance(0.6)
        bg = Image.alpha_composite(bg, circle)

        w, h = thumb.size
        cx, cy = w // 2, h // 2

        logo = thumb.crop((
            cx - center_crop, cy - center_crop,
            cx + center_crop, cy + center_crop,
        ))
        logo.thumbnail((400, 400), Image.Resampling.LANCZOS)

        size = logo.size
        mask = Image.new("L", (size[0] * 3, size[1] * 3), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, *mask.size), fill=255)
        mask = mask.resize(size, Image.LANCZOS)
        logo.putalpha(ImageChops.darker(mask, logo.split()[-1]))

        bg.paste(logo, ((img_size[0] - logo.width) // 2, 138), logo)
        draw = ImageDraw.Draw(bg)

        draw.text(
            (450, 25),
            "STARTED PLAYING",
            fill="white",
            stroke_width=3,
            stroke_fill="grey",
            font=font1,
        )

        for i, line in enumerate(textwrap.wrap(title, 32)[:2]):
            w_line = draw.textbbox((0, 0), line, font=font1)[2]
            draw.text(
                ((img_size[0] - w_line) // 2, 550 + i * 50),
                line,
                fill="white",
                stroke_width=1,
                stroke_fill="white",
                font=font1,
            )

        draw.text(
            ((img_size[0] - 270) // 2, 675),
            f"Duration: {duration} Mins",
            fill="white",
            font=font2,
        )

        if os.path.exists(f"cache/thumb{video_id}.png"):
            os.remove(f"cache/thumb{video_id}.png")

        bg.save(out)
        return out
    except Exception as e:
        print(f"Image processing error: {e}")
        return YOUTUBE_IMG_URL

