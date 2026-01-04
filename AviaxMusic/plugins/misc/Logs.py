from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from AviaxMusic import app
from AviaxMusic.utils.database import add_served_chat
from config import LOG_GROUP_ID

# Log message bhejne ka function (Error handling ke saath)
async def new_message(chat_id: int, message: str, reply_markup=None):
    try:
        await app.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
    except Exception:
        pass

@app.on_message(filters.new_chat_members)
async def on_new_chat_members(client: Client, message: Message):
    # FIXED: await client.get_me() ki jagah client.me.id use kiya
    if client.me.id in [user.id for user in message.new_chat_members]:
        added_by = message.from_user.mention if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        title = message.chat.title
        username = f"@{message.chat.username}" if message.chat.username else "Private Group"
        chat_id = message.chat.id
        
        # FIXED: Agar member count fetch na ho toh bot crash na ho
        try:
            chat_members = await client.get_chat_members_count(chat_id)
        except Exception:
            chat_members = "Unknown"

        am = (
            f"✫ <b><u>ɴᴇᴡ ɢʀᴏᴜᴘ</u></b> :\n\n"
            f"ᴄʜᴀᴛ ɪᴅ : {chat_id}\n"
            f"ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ : {username}\n"
            f"ᴄʜᴀᴛ ᴛɪᴛʟᴇ : {title}\n"
            f"ᴛᴏᴛᴀʟ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀꜱ : {chat_members}\n\n"
            f"ᴀᴅᴅᴇᴅ ʙʏ : {added_by}"
        )
        
        reply_markup = None
        if message.from_user:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(message.from_user.first_name, user_id=message.from_user.id)]
            ])

        await add_served_chat(chat_id)
        await new_message(LOG_GROUP_ID, am, reply_markup)

@app.on_message(filters.left_chat_member)
async def on_left_chat_member(client: Client, message: Message):
    # FIXED: client.me.id use kiya
    if client.me.id == message.left_chat_member.id:
        remove_by = message.from_user.mention if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        title = message.chat.title
        username = f"@{message.chat.username}" if message.chat.username else "Private Group"
        chat_id = message.chat.id
        
        ambye = (
            f"✫ <b><u>ʟᴇғᴛ ɢʀᴏᴜᴘ</u></b> :\n\n"
            f"ᴄʜᴀᴛ ɪᴅ : {chat_id}\n"
            f"ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ : {username}\n"
            f"ᴄʜᴀᴛ ᴛɪᴛʟᴇ : {title}\n\n"
            f"ʀᴇᴍᴏᴠᴇᴅ ʙʏ : {remove_by}"
        )
        
        reply_markup = None
        if message.from_user:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(message.from_user.first_name, user_id=message.from_user.id)]
            ])
            
        await new_message(LOG_GROUP_ID, ambye, reply_markup)
