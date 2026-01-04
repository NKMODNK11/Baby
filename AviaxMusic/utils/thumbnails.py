import os
import aiofiles
import aiohttp
import textwrap

from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance, ImageChops
from py_yt import VideosSearch

from config import YOUTUBE_IMG_URL

font1 = ImageFont.truetype("AviaxMusic/assets/font2.ttf", 45)
font2 = ImageFont.truetype("AviaxMusic/assets/font2.ttf", 30)
circle = Image.new("RGBA", (1280, 720), 0)

async def gen_thumb(video_id: str, center_crop = 250, img_size = (1280, 720)) -> str:
    out = f"cache/{video_id}.png"
    if os.path.isfile(out):
        return out

    url = f"https://www.youtube.com/watch?v={video_id}"
    results = VideosSearch(url, limit=1)
    for result in (await results.next())["result"]:
        title = result.get("title", "Unsupported Title")
        title = title.title()
        duration = result.get("duration", "00:00")
        try:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        except Exception:
            return YOUTUBE_IMG_URL

    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open(f"cache/thumb{video_id}.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

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
        w = draw.textbbox((0, 0), line, font=font1)[2]
        draw.text(
            ((img_size[0] - w) // 2, 550 + i * 50),
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

    try:
        os.remove(f"cache/thumb{video_id}.png")
    except Exception:
        pass

    try:
        bg.save(out)
        return out
    except Exception:
        return YOUTUBE_IMG_URL
