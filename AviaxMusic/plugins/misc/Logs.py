from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from AviaxMusic import app
from AviaxMusic.utils.database import add_served_chat
from config import LOG_GROUP_ID


async def new_message(chat_id: int, message: str, reply_markup=None):
    try:
        await app.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
    except Exception:
        # fallback without buttons (safety)
        await app.send_message(chat_id=chat_id, text=message)


@app.on_message(filters.new_chat_members)
async def on_new_chat_members(client: Client, message: Message):
    me = await client.get_me()

    if me.id not in [user.id for user in message.new_chat_members]:
        return

    added_by = (
        message.from_user.mention
        if message.from_user
        else "ᴜɴᴋɴᴏᴡɴ / ᴀɴᴏɴʏᴍᴏᴜs"
    )

    title = message.chat.title
    username = f"@{message.chat.username}" if message.chat.username else "N/A"
    chat_id = message.chat.id
    members = await client.get_chat_members_count(chat_id)

    text = (
        "✫ <b><u>ɴᴇᴡ ɢʀᴏᴜᴘ</u></b> :\n\n"
        f"ᴄʜᴀᴛ ɪᴅ : <code>{chat_id}</code>\n"
        f"ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ : {username}\n"
        f"ᴄʜᴀᴛ ᴛɪᴛʟᴇ : {title}\n"
        f"ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs : {members}\n\n"
        f"ᴀᴅᴅᴇᴅ ʙʏ : {added_by}"
    )

    # ✅ SAFE BUTTON (URL only, no user_id)
    reply_markup = None
    if message.from_user and message.from_user.username:
        reply_markup = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    "👤 Added By",
                    url=f"https://t.me/{message.from_user.username}"
                )
            ]]
        )

    await add_served_chat(chat_id)
    await new_message(LOG_GROUP_ID, text, reply_markup)


@app.on_message(filters.left_chat_member)
async def on_left_chat_member(client: Client, message: Message):
    me = await client.get_me()

    if not message.left_chat_member or me.id != message.left_chat_member.id:
        return

    removed_by = (
        message.from_user.mention
        if message.from_user
        else "ᴜɴᴋɴᴏᴡɴ / ᴀɴᴏɴʏᴍᴏᴜs"
    )

    title = message.chat.title
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
                    "👤 Removed By",
                    url=f"https://t.me/{message.from_user.username}"
                )
            ]]
        )

    await new_message(LOG_GROUP_ID, text, reply_markup)
