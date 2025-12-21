import random
import asyncio
from datetime import date
from typing import Dict, List, Union

from AviaxMusic import userbot
from AviaxMusic.core.mongo import mongodb

authdb = mongodb.adminauth
authuserdb = mongodb.authuser
autoenddb = mongodb.autoend
autoleavedb = mongodb.autoleave
assdb = mongodb.assistants
blacklist_chatdb = mongodb.blacklistChat
blockeddb = mongodb.blockedusers
chatsdb = mongodb.chats
chatdb = mongodb.chat
channeldb = mongodb.cplaymode
countdb = mongodb.upcount
gbansdb = mongodb.gban
langdb = mongodb.language
onoffdb = mongodb.onoffper
playmodedb = mongodb.playmode
playtypedb = mongodb.playtypedb
skipdb = mongodb.skipmode
sudoersdb = mongodb.sudoers
usersdb = mongodb.tgusersdb

# In-memory cache
active = []
activevideo = []
assistantdict = {}
autoend = {}
autoleave = {}
count = {}
channelconnect = {}
langm = {}
loop = {}
maintenance = []
nonadmin = {}
pause = {}
playmode = {}
playtype = {}
skipmode = {}


async def get_assistant_number(chat_id: int) -> str:
    return assistantdict.get(chat_id)


async def get_client(assistant: int):
    assistant = int(assistant)
    if assistant == 1:
        return userbot.one
    elif assistant == 2:
        return userbot.two
    elif assistant == 3:
        return userbot.three
    elif assistant == 4:
        return userbot.four
    elif assistant == 5:
        return userbot.five


# ===================== ASSISTANT SAFE FUNCTIONS ===================== #

async def set_assistant_new(chat_id, number):
    number = int(number)
    assistantdict[chat_id] = number
    await assdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": number}},
        upsert=True,
    )


async def set_assistant(chat_id):
    from AviaxMusic.core.userbot import assistants

    if not assistants:
        raise RuntimeError("No assistant is running yet")

    ran_assistant = random.choice(assistants)
    assistantdict[chat_id] = ran_assistant

    await assdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": ran_assistant}},
        upsert=True,
    )

    return await get_client(ran_assistant)


async def get_assistant(chat_id: int):
    from AviaxMusic.core.userbot import assistants

    if not assistants:
        raise RuntimeError("No assistant is running yet")

    assistant = assistantdict.get(chat_id)

    if not assistant:
        dbassistant = await assdb.find_one({"chat_id": chat_id})
        if not dbassistant or dbassistant["assistant"] not in assistants:
            return await set_assistant(chat_id)

        assistantdict[chat_id] = dbassistant["assistant"]
        return await get_client(dbassistant["assistant"])

    if assistant not in assistants:
        return await set_assistant(chat_id)

    return await get_client(assistant)


async def set_calls_assistant(chat_id):
    from AviaxMusic.core.userbot import assistants

    if not assistants:
        raise RuntimeError("No assistant is running yet")

    ran_assistant = random.choice(assistants)
    assistantdict[chat_id] = ran_assistant

    await assdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": ran_assistant}},
        upsert=True,
    )
    return ran_assistant


async def group_assistant(self, chat_id: int):
    from AviaxMusic.core.userbot import assistants

    if not assistants:
        raise RuntimeError("No assistant is running yet")

    assistant = assistantdict.get(chat_id)

    if not assistant:
        dbassistant = await assdb.find_one({"chat_id": chat_id})
        if not dbassistant or dbassistant["assistant"] not in assistants:
            assistant = await set_calls_assistant(chat_id)
        else:
            assistant = dbassistant["assistant"]
            assistantdict[chat_id] = assistant
    else:
        if assistant not in assistants:
            assistant = await set_calls_assistant(chat_id)

    assistant = int(assistant)
    if assistant == 1:
        return self.one
    elif assistant == 2:
        return self.two
    elif assistant == 3:
        return self.three
    elif assistant == 4:
        return self.four
    elif assistant == 5:
        return self.five


# ===================== बाकी DATABASE CODE (UNCHANGED) ===================== #
# (Skip mode, playmode, lang, users, bans, sudo, etc.)
# Tumhara baaki code bilkul safe hai, usme issue nahi tha
