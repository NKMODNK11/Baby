import re
import asyncio

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
    TopicClosed,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from AviaxMusic import YouTube, app
from AviaxMusic.misc import SUDOERS
from AviaxMusic.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from AviaxMusic.utils.inline import botplaylist_markup
from config import SUPPORT_GROUP, adminlist
from strings import get_string

links = {}
regex = re.compile(r"[\u1000-\u109F\uAA80-\uAADB]+")


def PlayWrapper(command):
    async def wrapper(client, message):
        language = await get_lang(message.chat.id)
        _ = get_string(language)

        if message.sender_chat:
            upl = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="ʜᴏᴡ ᴛᴏ ғɪx ?", callback_data="AnonymousAdmin")]]
            )
            return await message.reply_text(_["general_3"], reply_markup=upl)

        if await is_maintenance() is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, "
                    f"ᴠɪsɪᴛ <a href={SUPPORT_GROUP}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a>",
                    disable_web_page_preview=True,
                )

        try:
            await message.delete()
        except:
            pass

        if bool(regex.search(message.text)):
            return

        audio_telegram = (
            (message.reply_to_message.audio or message.reply_to_message.voice)
            if message.reply_to_message else None
        )
        video_telegram = (
            (message.reply_to_message.video or message.reply_to_message.document)
            if message.reply_to_message else None
        )

        url = await YouTube.url(message)

        # ✅ SAFE BLOCK (Slowmode + TopicClosed proof)
        if audio_telegram is None and video_telegram is None and url is None:
            if len(message.command) < 2:
                if "stream" in message.command:
                    return await message.reply_text(_["str_1"])

                buttons = botplaylist_markup(_)
                try:
                    return await message.reply_text(
                        _["play_18"],
                        reply_markup=InlineKeyboardMarkup(buttons),
                        disable_web_page_preview=True,
                    )
                except TopicClosed:
                    return

        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_7"])
            try:
                chat = await app.get_chat(chat_id)
            except:
                return await message.reply_text(_["cplay_4"])
            channel = chat.title
        else:
            chat_id = message.chat.id
            channel = None

        playmode = await get_playmode(message.chat.id)
        playty = await get_playtype(message.chat.id)

        if playty != "Everyone":
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id)
                if not admins:
                    return await message.reply_text(_["admin_13"])
                if message.from_user.id not in admins:
                    return await message.reply_text(_["play_4"])

        video = True if (
            message.command[0][0] == "v" or "-v" in message.text
        ) else None

        if message.command[0][-1] == "e":
            if not await is_active_chat(chat_id):
                return await message.reply_text(_["play_16"])
            fplay = True
        else:
            fplay = None

        if not await is_active_chat(chat_id):
            userbot = await get_assistant(chat_id)
            try:
                get = await app.get_chat_member(chat_id, userbot.id)
                if get.status in (
                    ChatMemberStatus.BANNED,
                    ChatMemberStatus.RESTRICTED,
                ):
                    return await message.reply_text(
                        _["call_2"].format(
                            app.mention, userbot.id, userbot.name, userbot.username
                        )
                    )
            except ChatAdminRequired:
                return await message.reply_text(_["call_1"])
            except UserNotParticipant:
                try:
                    invitelink = await app.export_chat_invite_link(chat_id)
                except:
                    return await message.reply_text(_["call_1"])

                msg = await message.reply_text(_["call_4"].format(app.mention))
                try:
                    await asyncio.sleep(1)
                    await userbot.join_chat(invitelink)
                    await asyncio.sleep(2)
                    await msg.edit(_["call_5"].format(app.mention))
                except InviteRequestSent:
                    await app.approve_chat_join_request(chat_id, userbot.id)

        return await command(
            client,
            message,
            _,
            chat_id,
            video,
            channel,
            playmode,
            url,
            fplay,
        )

    return wrapper
