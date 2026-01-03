from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import RPCError # Error handle karne ke liye

from AviaxMusic import app
from AviaxMusic.utils.database import add_served_chat
from config import LOG_GROUP_ID


async def new_message(chat_id: int, message: str, reply_markup=None):
    try:
        await app.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
    except RPCError:
        # Agar button ki wajah se error aaye, toh bina button ke message bhejein
        await app.send_message(chat_id=chat_id, text=message)

@app.on_message(filters.new_chat_members, group=5)
async def on_new_chat_members(client: Client, message: Message):
    if app.id in [user.id for user in message.new_chat_members]:
        added_by = message.from_user.mention if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        title = message.chat.title
        username = f"@{message.chat.username}" if message.chat.username else "Private Chat"
        chat_id = message.chat.id
        
        try:
            chat_members = await client.get_chat_members_count(chat_id)
        except:
            chat_members = "Unknown"

        txt = f"✫ <b><u>ɴᴇᴡ ɢʀᴏᴜᴘ</u></b> :\n\nᴄʜᴀᴛ ɪᴅ : {chat_id}\nᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ : {username}\nᴄʜᴀᴛ ᴛɪᴛʟᴇ : {title}\nᴛᴏᴛᴀʟ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀꜱ : {chat_members}\n\nᴀᴅᴅᴇᴅ ʙʏ : {added_by}"
        
        reply_markup = None
        if message.from_user:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=message.from_user.first_name, user_id=message.from_user.id)]
            ])
            
        await add_served_chat(chat_id)
        await new_message(LOG_GROUP_ID, txt, reply_markup)

@app.on_message(filters.left_chat_member, group=6)
async def on_left_chat_member(client: Client, message: Message):
    if app.id == message.left_chat_member.id:
        remove_by = message.from_user.mention if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        title = message.chat.title
        username = f"@{message.chat.username}" if message.chat.username else "Private Chat"
        chat_id = message.chat.id
        
        txt = f"✫ <b><u>ʟᴇғᴛ ɢʀᴏᴜᴘ</u></b> :\n\nᴄʜᴀᴛ ɪᴅ : {chat_id}\nᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ : {username}\nᴄʜᴀᴛ ᴛɪᴛʟᴇ : {title}\n\nʀᴇᴍᴏᴠᴇᴅ ʙʏ : {remove_by}"
        
        reply_markup = None
        if message.from_user:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=message.from_user.first_name, user_id=message.from_user.id)]
            ])
            
        await new_message(LOG_GROUP_ID, txt, reply_markup)
