# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from __future__ import unicode_literals

import os, requests, asyncio, time
from pyrogram import filters, Client
from pyrogram.types import Message
from info import CHNL_LNK
from yt_dlp import YoutubeDL

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
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    query = query.strip()
    if not query:
        return await message.reply("**Example: /song Tum Hi Ho**")

    m = await message.reply(f"**🔍 Searching: {query}**")

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "outtmpl": "%(id)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
    }

    try:
        # Search on YouTube
        search_opts = {
            "quiet": True,
            "extract_flat": True,
            "default_search": f"ytsearch1:{query}",
        }
        with YoutubeDL(search_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if not info or 'entries' not in info or not info['entries']:
                return await m.edit("**❌ No results found. Try another song name.**")
            entry = info['entries'][0]
            link = entry.get('url') or f"https://youtube.com/watch?v={entry['id']}"
            title = entry.get('title', 'Unknown')[:40]
            duration = entry.get('duration', 0)
            video_id = entry.get('id', '')

        await m.edit("**⬇️ Downloading your song...**")

        # Download thumbnail
        thumb_name = f"thumb_{video_id}.jpg"
        try:
            thumb_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
            thumb_data = requests.get(thumb_url, timeout=10)
            with open(thumb_name, 'wb') as f:
                f.write(thumb_data.content)
        except:
            thumb_name = None

        # Download audio
        with YoutubeDL(ydl_opts) as ydl:
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
        await m.edit(f"**🚫 Error: {str(e)[:200]}**")
        print(e)

    finally:
        for f in [audio_file if 'audio_file' in locals() else None, thumb_name]:
            try:
                if f and os.path.exists(f):
                    os.remove(f)
            except:
                pass


@Client.on_message(filters.command(["video", "mp4"]))
async def vsong(client, message: Message):
    urlissed = get_text(message)
    pablo = await client.send_message(message.chat.id, f"**🔍 Finding your video:** `{urlissed}`")
    if not urlissed:
        return await pablo.edit("**Example: /video Tum Hi Ho song** or **/video https://youtu.be/xxxxx**")

    # Check if direct URL or search query
    if urlissed.startswith("http"):
        url = urlissed
    else:
        # Search for video
        try:
            search_opts = {"quiet": True, "extract_flat": True}
            with YoutubeDL(search_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{urlissed}", download=False)
                if not info or 'entries' not in info or not info['entries']:
                    return await pablo.edit("**❌ No results found.**")
                entry = info['entries'][0]
                url = f"https://youtube.com/watch?v={entry['id']}"
        except Exception as e:
            return await pablo.edit(f"**❌ Search failed:** `{str(e)[:200]}`")

    opts = {
        "format": "best[ext=mp4]/best",
        "addmetadata": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "outtmpl": "%(id)s.mp4",
        "quiet": True,
        "noplaylist": True,
    }

    await pablo.edit("**⬇️ Downloading video...**")

    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)
    except Exception as e:
        return await pablo.edit(f"**❌ Download Failed:** `{str(e)[:200]}`")

    file_stark = f"{ytdl_data['id']}.mp4"
    thum = ytdl_data.get('title', 'Video')
    mo = url

    # Download thumbnail
    sedlyf = None
    try:
        kekme = f"https://img.youtube.com/vi/{ytdl_data['id']}/hqdefault.jpg"
        sedlyf = f"thumb_{ytdl_data['id']}.jpg"
        thumb_data = requests.get(kekme, timeout=10)
        with open(sedlyf, 'wb') as f:
            f.write(thumb_data.content)
    except:
        sedlyf = None

    capy = f"**𝚃𝙸𝚃𝙻𝙴 :** [{thum}]({mo})\n**𝚁𝙴𝚀𝚄𝙴𝚂𝚃𝙴𝙳 𝙱𝚈 :** {message.from_user.mention}"

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
