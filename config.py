import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Telegram API
API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH", "")

# Bot token
BOT_TOKEN = getenv("BOT_TOKEN", "")

# Mongo
MONGO_DB_URI = getenv("MONGO_DB_URI")

# Duration
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", "60"))

# Log group
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", "0"))
LOGGER_ID = LOG_GROUP_ID   # 🔧 FIX

# Owner
OWNER_ID = int(getenv("OWNER_ID", "0"))

# Heroku
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

# APIs
API_URL = getenv("API_URL", "https://api3.nexgenbots.xyz")

# ❌ DEAD API REMOVED
# VIDEO_API_URL = 'https://api.video.thequickearn.xyz'

# ✅ WORKING / SAFE
VIDEO_API_URL = getenv("VIDEO_API_URL", "https://api3.nexgenbots.xyz")

API_KEY = getenv("API_KEY")

# Git
UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/NKMODNK11/Baby",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv("GIT_TOKEN")

# Support
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/RessoUpdates")
SUPPORT_GROUP = getenv("SUPPORT_GROUP", "https://t.me/DOCTOR_CHATTING_GROUP")

# Auto leave (bool FIX)
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "False").lower() == "true"

# Privacy
PRIVACY_LINK = getenv(
    "PRIVACY_LINK",
    "https://telegra.ph/Privacy-Policy-for-AviaxMusic-08-14"
)

# Spotify
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET")

# Playlist
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "25"))

# Telegram limits
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "104857600"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "2145386496"))

# Assistant sessions
STRING1 = getenv("STRING_SESSION")
STRING2 = getenv("STRING_SESSION2")
STRING3 = getenv("STRING_SESSION3")
STRING4 = getenv("STRING_SESSION4")
STRING5 = getenv("STRING_SESSION5")

# Runtime vars
BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

# Images
START_IMG_URL = getenv("START_IMG_URL", "https://envs.sh/WJ-.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://envs.sh/WJ-.jpg")
PLAYLIST_IMG_URL = "https://envs.sh/WJ-.jpg"
STATS_IMG_URL = "https://envs.sh/WJ-.jpg"

TELEGRAM_AUDIO_URL = "https://graph.org/file/2f7debf856695e0ef0607.png"
TELEGRAM_VIDEO_URL = "https://graph.org/file/2f7debf856695e0ef0607.png"

STREAM_IMG_URL = "https://te.legra.ph/file/bd995b032b6bd263e2cc9.jpg"
SOUNCLOUD_IMG_URL = "https://te.legra.ph/file/bb0ff85f2dd44070ea519.jpg"
YOUTUBE_IMG_URL = "https://graph.org/file/2f7debf856695e0ef0607.png"

SPOTIFY_ARTIST_IMG_URL = "https://te.legra.ph/file/37d163a2f75e0d3b403d6.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://te.legra.ph/file/b35fd1dfca73b950b1b05.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://te.legra.ph/file/95b3ca7993bbfaf993dcb.jpg"


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = time_to_seconds(f"{DURATION_LIMIT_MIN}:00")

# URL validation
if SUPPORT_CHANNEL and not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
    raise SystemExit(
        "[ERROR] - SUPPORT_CHANNEL must start with https://"
    )

if SUPPORT_GROUP and not re.match(r"(?:http|https)://", SUPPORT_GROUP):
    raise SystemExit(
        "[ERROR] - SUPPORT_GROUP must start with https://"
    )
