from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from AviaxMusic import app
from AviaxMusic.utils.database import add_served_chat
from config import LOG_GROUP_ID

# ✅ Cache for get_me() (FloodWait FIX)
ME = None


async def new_message(chat_id: int, message: str, reply_markup=None):
    try:
        await app.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
    except Exception:
        # fallback without buttons (extra safe)
        await app.send_message(
            chat_id=chat_id,
            text=message,
            disable_web_page_preview=True,
        )


async def get_me_cached(client: Client):
    global ME
    if not ME:
        ME = await client.get_me()
    return ME


@app.on_message(filters.new_chat_members)
async def on_new_chat_members(client: Client, message: Message):
    me = await get_me_cached(client)

    if not message.new_chat_members:
        return

    if me.id not in [user.id for user in message.new_chat_members]:
        return

    added_by = (
        message.from_user.mention
        if message.from_user
        else "ᴜɴᴋɴᴏᴡɴ / ᴀɴᴏɴʏᴍᴏᴜs"
    )

    title = message.chat.title or "N/A"
    username = f"@{message.chat.username}" if message.chat.username else "N/A"
    chat_id = message.chat.id

    try:
        members = await client.get_chat_members_count(chat_id)
    except Exception:
        members = "N/A"

    text = (
        "✫ <b><u>ɴᴇᴡ ɢʀᴏᴜᴘ</u></b> :\n\n"
        f"ᴄʜᴀᴛ ɪᴅ : <code>{chat_id}</code>\n"
        f"ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ : {username}\n"
        f"ᴄʜᴀᴛ ᴛɪᴛʟᴇ : {title}\n"
        f"ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs : {members}\n\n"
        f"ᴀᴅᴅᴇᴅ ʙʏ : {added_by}"
    )

    reply_markup = None
    if message.from_user and message.from_user.username:
        reply_markup = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    text="👤 Added By",
                    url=f"https://t.me/{message.from_user.username}",
                )
            ]]
        )

    await add_served_chat(chat_id)
    await new_message(LOG_GROUP_ID, text, reply_markup)


@app.on_message(filters.left_chat_member)
async def on_left_chat_member(client: Client, message: Message):
    me = await get_me_cached(client)

    if not message.left_chat_member:
        return

    if me.id != message.left_chat_member.id:
        return

    removed_by = (
        message.from_user.mention
        if message.from_user
        else "ᴜɴᴋɴᴏᴡɴ / ᴀɴᴏɴʏᴍᴏᴜs"
    )

    title = message.chat.title or "N/A"
    username = f"@{message.chat.username}" if message.chat.username else "N/A"
    chat_id = message.chat.id

    text = (
        "✫ <b><u>ʟᴇғᴛ ɢʀᴏᴜᴘ</u></b> :\n\n"
        f"ᴄʜᴀᴛ ɪᴅ : <code>{chat_id}</code>\n"
        f"ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ : {username}\n"
        f"ᴄʜᴀᴛ ᴛɪᴛʟᴇ : {title}\n\n"
        f"ʀᴇᴍᴏᴠᴇᴅ ʙʏ : {removed_by}"
    )

    reply_markup = None
    if message.from_user and message.from_user.username:
        reply_markup = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    text="👤 Removed By",
                    url=f"https://t.me/{message.from_user.username}",
                )
            ]]
        )

    await new_message(LOG_GROUP_ID, text, reply_markup)
