# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from __future__ import unicode_literals

import os, requests, asyncio, time
from pyrogram import filters, Client
from pyrogram.types import Message
from info import CHNL_LNK
from yt_dlp import YoutubeDL

# ─── Cookies Setup ───────────────────────────────────────────────
# Priority 1: cookies.txt file (root folder mein)
# Priority 2: COOKIES_CONTENT environment variable (Render/Heroku)

COOKIES_FILE = None

if os.path.exists("cookies.txt"):
    COOKIES_FILE = "cookies.txt"
elif os.environ.get("COOKIES_CONTENT"):
    # Environment variable se cookies.txt banao
    with open("cookies.txt", "w") as f:
        f.write(os.environ.get("COOKIES_CONTENT"))
    COOKIES_FILE = "cookies.txt"
# ─────────────────────────────────────────────────────────────────
COOKIES_FILE = "cookies.txt" if os.path.exists("cookies.txt") else None

def get_ydl_opts(extra={}):
    """Base yt-dlp options with cookies if available"""
    opts = {
        "quiet": True,
        "noplaylist": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
    }
    if COOKIES_FILE:
        opts["cookiefile"] = COOKIES_FILE
    opts.update(extra)
    return opts


def get_text(message: Message):
    text_to_return = message.text
    if message.text is None:
        return None
    if " " not in text_to_return:
        return None
    try:
        return message.text.split(None, 1)[1]
    except IndexError:
        return None


@Client.on_message(filters.command(['song', 'mp3']) & filters.private)
async def song(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    query = ' '.join(message.command[1:]).strip()
    if not query:
        return await message.reply("**Example: /song Tum Hi Ho**")

    m = await message.reply(f"**🔍 Searching: {query}**")
    audio_file = None
    thumb_name = None

    try:
        # Search
        search_opts = get_ydl_opts({"extract_flat": True})
        with YoutubeDL(search_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if not info or 'entries' not in info or not info['entries']:
                return await m.edit("**❌ No results found. Try another song name.**")
            entry = info['entries'][0]
            link = f"https://youtube.com/watch?v={entry['id']}"
            title = entry.get('title', 'Unknown')[:40]
            duration = entry.get('duration', 0)
            video_id = entry.get('id', '')

        await m.edit("**⬇️ Downloading your song...**")

        # Thumbnail
        thumb_name = f"thumb_{video_id}.jpg"
        try:
            thumb_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            thumb_data = requests.get(thumb_url, timeout=10)
            with open(thumb_name, 'wb') as f:
                f.write(thumb_data.content)
        except:
            thumb_name = None

        # Download audio
        audio_opts = get_ydl_opts({
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": "%(id)s.%(ext)s",
        })
        with YoutubeDL(audio_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            audio_file = ydl.prepare_filename(info_dict)

        cap = f"**BY›› [UPDATE]({CHNL_LNK})**"
        await message.reply_audio(
            audio_file,
            caption=cap,
            quote=False,
            title=title,
            duration=int(duration),
            performer="NETWORKS™",
            thumb=thumb_name
        )
        await m.delete()

    except Exception as e:
        err = str(e)
        if "Sign in" in err or "bot" in err.lower() or "429" in err:
            await m.edit("**❌ YouTube ne block kiya.\n\n`cookies.txt` file bot root mein rakho phir try karo.**")
        else:
            await m.edit(f"**🚫 Error:** `{err[:200]}`")
        print(e)

    finally:
        for f in [audio_file, thumb_name]:
            try:
                if f and os.path.exists(f):
                    os.remove(f)
            except:
                pass


@Client.on_message(filters.command(["video", "mp4"]))
async def vsong(client, message: Message):
    urlissed = get_text(message)
    pablo = await client.send_message(message.chat.id, f"**🔍 Finding:** `{urlissed}`")
    if not urlissed:
        return await pablo.edit("**Example: /video Tum Hi Ho** ya **/video https://youtu.be/xxxxx**")

    # Direct URL ya search
    if urlissed.startswith("http"):
        url = urlissed
    else:
        try:
            search_opts = get_ydl_opts({"extract_flat": True})
            with YoutubeDL(search_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{urlissed}", download=False)
                if not info or 'entries' not in info or not info['entries']:
                    return await pablo.edit("**❌ No results found.**")
                entry = info['entries'][0]
                url = f"https://youtube.com/watch?v={entry['id']}"
        except Exception as e:
            return await pablo.edit(f"**❌ Search failed:** `{str(e)[:200]}`")

    video_opts = get_ydl_opts({
        "format": "best[ext=mp4]/best",
        "addmetadata": True,
        "outtmpl": "%(id)s.mp4",
    })

    await pablo.edit("**⬇️ Downloading video...**")

    try:
        with YoutubeDL(video_opts) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)
    except Exception as e:
        err = str(e)
        if "Sign in" in err or "bot" in err.lower() or "429" in err:
            return await pablo.edit("**❌ YouTube ne block kiya.\n\n`cookies.txt` file bot root mein rakho phir try karo.**")
        return await pablo.edit(f"**❌ Download Failed:** `{err[:200]}`")

    file_stark = f"{ytdl_data['id']}.mp4"
    thum = ytdl_data.get('title', 'Video')

    # Thumbnail
    sedlyf = None
    try:
        kekme = f"https://img.youtube.com/vi/{ytdl_data['id']}/hqdefault.jpg"
        sedlyf = f"thumb_{ytdl_data['id']}.jpg"
        thumb_data = requests.get(kekme, timeout=10)
        with open(sedlyf, 'wb') as f:
            f.write(thumb_data.content)
    except:
        sedlyf = None

    capy = f"**𝚃𝙸𝚃𝙻𝙴 :** [{thum}]({url})\n**𝚁𝙴𝚀𝚄𝙴𝚂𝚃𝙴𝙳 𝙱𝚈 :** {message.from_user.mention}"

    await pablo.edit("**📤 Uploading...**")

    await client.send_video(
        message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data.get("duration", 0)),
        file_name=str(ytdl_data.get("title", "video")),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,
        reply_to_message_id=message.id
    )
    await pablo.delete()

    for files in (sedlyf, file_stark):
        try:
            if files and os.path.exists(files):
                os.remove(files)
        except:
            pass
