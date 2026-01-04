from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from AviaxMusic import app
from AviaxMusic.utils.database import add_served_chat
from config import LOG_GROUP_ID


async def new_message(chat_id: int, message: str, reply_markup=None):
    await app.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

@app.on_message(filters.new_chat_members, group=5)
async def on_new_chat_members(client: Client, message: Message):
    if app.id in [user.id for user in message.new_chat_members]:
        added_by = message.from_user.mention if message.from_user else "á´œÉ´á´‹É´á´á´¡É´ á´œsá´‡Ê€"
        title = message.chat.title
        username = f"@{message.chat.username}"
        chat_id = message.chat.id
        chat_members = await client.get_chat_members_count(chat_id)
        txt = f"âœ« <b><u>É´á´‡á´¡ É¢Ê€á´á´œá´˜</u></b> :\n\ná´„Êœá´€á´› Éªá´… : {chat_id}\ná´„Êœá´€á´› á´œsá´‡Ê€É´á´€á´á´‡ : {username}\ná´„Êœá´€á´› á´›Éªá´›ÊŸá´‡ : {title}\ná´›á´á´›á´€ÊŸ á´„Êœá´€á´› á´á´‡á´Ê™á´‡Ê€êœ± : {chat_members}\n\ná´€á´…á´…á´‡á´… Ê™Ê : {added_by}"
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    message.from_user.first_name,
                    user_id=message.from_user.id
                )
            ]
        ])
        await add_served_chat(chat_id)
        await new_message(LOG_GROUP_ID, txt, reply_markup)

@app.on_message(filters.left_chat_member, group=6)
async def on_left_chat_member(client: Client, message: Message):
    if app.id == message.left_chat_member.id:
        remove_by = message.from_user.mention if message.from_user else "á´œÉ´á´‹É´á´á´¡É´ á´œsá´‡Ê€"
        title = message.chat.title
        username = f"@{message.chat.username}"
        chat_id = message.chat.id
        txt = f"âœ« <b><u>ÊŸá´‡Ò“á´› É¢Ê€á´á´œá´˜</u></b> :\n\ná´„Êœá´€á´› Éªá´… : {chat_id}\ná´„Êœá´€á´› á´œsá´‡Ê€É´á´€á´á´‡ : {username}\ná´„Êœá´€á´› á´›Éªá´›ÊŸá´‡ : {title}\n\nÊ€á´‡á´á´á´ á´‡á´… Ê™Ê : {remove_by}"
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    message.from_user.first_name,
                    user_id=message.from_user.id
                )
            ]
        ])
        await new_message(LOG_GROUP_ID, txt, reply_markup)
