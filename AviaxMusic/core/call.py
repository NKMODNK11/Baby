import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from ntgcalls import ConnectionNotFound, TelegramServerError
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, exceptions, types

import config
from AviaxMusic import LOGGER, YouTube, app
from AviaxMusic.misc import db
from AviaxMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from AviaxMusic.utils.exceptions import AssistantErr
from AviaxMusic.utils.formatters import check_duration, seconds_to_min, speed_converter
from AviaxMusic.utils.inline.play import stream_markup
from AviaxMusic.utils.stream.autoclear import auto_clean
from AviaxMusic.utils.thumbnails import gen_thumb
from strings import get_string

autoend = {}
counter = {}

async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

class Call(PyTgCalls):
    def __init__(self):
        self.clients = []
        self.userbot1 = Client(name="AviaxAss1", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING1))
        self.one = PyTgCalls(self.userbot1, cache_duration=100)
        self.userbot2 = Client(name="AviaxAss2", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING2))
        self.two = PyTgCalls(self.userbot2, cache_duration=100)
        self.userbot3 = Client(name="AviaxAss3", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING3))
        self.three = PyTgCalls(self.userbot3, cache_duration=100)
        self.userbot4 = Client(name="AviaxAss4", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING4))
        self.four = PyTgCalls(self.userbot4, cache_duration=100)
        self.userbot5 = Client(name="AviaxAss5", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING5))
        self.five = PyTgCalls(self.userbot5, cache_duration=100)

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_call(chat_id)
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        for client in self.clients:
            try:
                await client.leave_call(chat_id)
            except:
                pass
        try:
            await _clear_(chat_id)
        except:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != "1.0":
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                vs = 2.0 if str(speed) == "0.5" else 1.35 if str(speed) == "0.75" else 0.68 if str(speed) == "1.5" else 0.5
                proc = await asyncio.create_subprocess_shell(
                    cmd=f"ffmpeg -i {file_path} -filter:v setpts={vs}*PTS -filter:a atempo={speed} {out}",
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
        else:
            out = file_path
        
        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        stream = types.MediaStream(
            media_path=out,
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
            ffmpeg_parameters=f"-ss {played} -to {duration}",
        )
        await assistant.play(chat_id, stream)

    async def join_call(self, chat_id: int, original_chat_id: int, link, video: Union[bool, str] = None, image: Union[bool, str] = None):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        stream = types.MediaStream(
            media_path=link,
            audio_parameters=types.AudioQuality.HIGH,
            video_parameters=types.VideoQuality.HD_720p,
            video_flags=types.MediaStream.Flags.AUTO_DETECT if video else types.MediaStream.Flags.IGNORE,
        )
        try:
            # FIX: join_group_call ko hata kar play use kiya jo purane version ke liye hai
            await assistant.play(chat_id, stream)
        except exceptions.NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except (ConnectionNotFound, TelegramServerError):
            raise AssistantErr(_["call_10"])
        except Exception as e:
            raise AssistantErr(f"Assistant Error: {e}")
            
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)

    async def change_stream(self, chat_id):
        client = await group_assistant(self, chat_id)
        check = db.get(chat_id)
        if not check:
            return
        
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)
            await auto_clean(popped)
            if not check:
                await _clear_(chat_id)
                return await client.leave_call(chat_id)
        except:
            await _clear_(chat_id)
            try: return await client.leave_call(chat_id)
            except: return

        # Naya Gaana Play Logic
        try:
            queued = check[0]["file"]
            videoid = check[0]["vidid"]
            streamtype = str(check[0]["streamtype"])
            video = streamtype == "video"

            stream = types.MediaStream(
                media_path=queued,
                audio_parameters=types.AudioQuality.HIGH,
                video_parameters=types.VideoQuality.HD_720p,
                video_flags=types.MediaStream.Flags.AUTO_DETECT if video else types.MediaStream.Flags.IGNORE,
            )
            await client.play(chat_id, stream)
        except Exception as e:
            LOGGER(__name__).error(f"Error in change_stream: {e}")

    async def start(self):
        LOGGER(__name__).info("Starting Assistants...\n")
        if config.STRING1:
            await self.one.start()
            self.clients.append(self.one)
        if config.STRING2:
            await self.two.start()
            self.clients.append(self.two)
        if config.STRING3:
            await self.three.start()
            self.clients.append(self.three)
        if config.STRING4:
            await self.four.start()
            self.clients.append(self.four)
        if config.STRING5:
            await self.five.start()
            self.clients.append(self.five)

    async def decorators(self):
        for client in self.clients:
            @client.on_update()
            async def update_handler(_, update: types.Update) -> None:
                if isinstance(update, types.StreamEnded):
                    await self.change_stream(update.chat_id)

Aviax = Call()

