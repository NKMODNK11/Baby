import time
from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import (
 from youtube_search_python.__future__ import VideosSearch
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
)
from youtube_search_python.__future__ import VideosSearch

import config
from AnonXMusic import app
from AnonXMusic.misc import _boot_
from AnonXMusic.plugins.sudo.sudoers import sudoers_list
from AnonXMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from AnonXMusic.utils import bot_sys_stats
from AnonXMusic.utils.decorators.language import LanguageStart
from AnonXMusic.utils.formatters import get_readable_time
from AnonXMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            keyboard = help_pannel(_)
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                protect_content=True,
                reply_markup=keyboard,
            )

        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=(
                        f"{message.from_user.mention} ᴄʜᴇᴄᴋᴇᴅ <b>sᴜᴅᴏ ʟɪsᴛ</b>.\n\n"
                        f"<b>ᴜsᴇʀ ɪᴅ:</b> <code>{message.from_user.id}</code>\n"
                        f"<b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username}"
                    ),
                )
            return

        if name.startswith("inf"):
            m = await message.reply_text("🔎")
            query = name.replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            
            res = (await results.next())["result"]
            if res:
                result = res[0]
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]

                searched_text = _["start_6"].format(
                    title, duration, views, published, channellink, channel, app.mention
                )

                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text=_["S_B_8"], url=link),
                            InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                        ]
                    ]
                )

                await m.delete()
                return await app.send_photo(
                    chat_id=message.chat.id,
                    photo=thumbnail,
                    caption=searched_text,
                    reply_markup=key,
                )
            else:
                return await m.edit("ɴᴏ ɪɴғᴏ ғᴏᴜɴᴅ.")

    out = private_panel(_)
    UP, CPU, RAM, DISK = await bot_sys_stats()

    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_2"].format(
            message.from_user.mention,
            app.mention,
            UP,
            DISK,
            CPU,
            RAM,
        ),
        reply_markup=InlineKeyboardMarkup(out),
    )

    if await is_on_off(2):
        await app.send_message(
            chat_id=config.LOGGER_ID,
            text=(
                f"{message.from_user.mention} sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n"
                f"<b>ᴜsᴇʀ ɪᴅ:</b> <code>{message.from_user.id}</code>\n"
                f"<b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username}"
            ),
        )


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - _boot_)

    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    await add_served_chat(message.chat.id)


@app.on_callback_query(filters.regex("^api_console$"))
async def api_console_cb(client, query: CallbackQuery):
    await query.message.edit_caption(
        caption="""
🚀 **NEXGENBOTS API Console**

Fast, reliable & developer-friendly API access.

━━━━━━━━━━━━━━
💰 **Pricing (Monthly)**

🔓 **Free** : 5,000 requests / day
🚀 **Starter** : ₹1 | 10k requests
⚡ **Standard** : ₹2 | 15k requests
🔥 **Pro** : ₹3 | 25k requests
🏆 **Enterprise** : ₹5 | 100k requests

━━━━━━━━━━━━━━
🛒 **Buy / Manage API**
Use the console below 👇""",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🛒 Open API Console", url="https://console.nexgenbots.xyz")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
            ]
        ),
    )
    await query.answer()

@app.on_callback_query(filters.regex("^back_to_start$"))
async def back_to_start_cb(client, query: CallbackQuery):
    language = await get_lang(query.message.chat.id)
    _ = get_string(language)
    out = private_panel(_)
    UP, CPU, RAM, DISK = await bot_sys_stats()

    await query.message.edit_caption(
        caption=_["start_2"].format(query.from_user.mention, app.mention, UP, DISK, CPU, RAM),
        reply_markup=InlineKeyboardMarkup(out),
    )
    await query.answer()

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if await is_banned_user(member.id):
                await message.chat.ban_member(member.id)
                return
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(_["start_5"].format(app.mention, f"https://t.me/{app.username}?start=sudolist", config.SUPPORT_CHAT))
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=_["start_3"].format(message.from_user.first_name, app.mention, message.chat.title, app.mention),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)


