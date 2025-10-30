import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
from dotenv import load_dotenv

# Load .env file (optional)
load_dotenv()

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN") or "7668584253:AAH9K8aSpcUINeHKT8GB4DdZMf0irqc2wmg"  # សូមប្រាកដថាអ្នកបានដាក់ Token ត្រឹមត្រូវ
# ==============

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# yt-dlp options នេះអាចប្រើបានជាមួយគ្រប់ Platform (TikTok, YouTube, Facebook)
ydl_opts = {
    'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}

# Ensure download folder exists
os.makedirs("downloads", exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # <--- កែប្រែសារต้อนรับ
    await update.message.reply_text(
        "Send me a link from TikTok, YouTube, or Facebook and I'll download the video for you!\n\n"
        "Examples:\n"
        "https://www.tiktok.com/@user/video/123\n"
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
        "https://fb.watch/somevideo/"
    )


async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id

    # <--- កែប្រែការตรวจสอบ Link ឱ្យទទួលស្គាល់ Platform ច្រើន
    valid_domains = ["tiktok.com", "youtube.com", "youtu.be", "facebook.com", "fb.watch"]
    if not any(domain in url for domain in valid_domains):
        await update.message.reply_text("Please send a valid TikTok, YouTube, or Facebook link.")
        return

    status_msg = await update.message.reply_text("Downloading video...")
    
    video_id = None # កំណត់អញ្ញត្តិ video_id ជាមុន

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            ext = info.get('ext', 'mp4')
            file_path = f"downloads/{video_id}.{ext}"

        # Send video
        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption=f"From: {info.get('uploader', 'Unknown')}\nDownloaded by your bot",
                supports_streaming=True,
                read_timeout=180, # បង្កើន Timeout សម្រាប់ File ធំ
                write_timeout=180,
            )

        # Cleanup
        os.remove(file_path)
        await status_msg.edit_text("Video sent!")

    except Exception as e:
        logger.error(f"Error: {e}")
        await status_msg.edit_text(f"Failed to download: {str(e)[:200]}") # បង្ហាញ Error បានវែងជាងមុន
        # Cleanup on failure
        if video_id:
            for ext_try in ['mp4', 'webm', 'mkv', 'm4a']:
                path_to_remove = f"downloads/{video_id}.{ext_try}"
                if os.path.exists(path_to_remove):
                    os.remove(path_to_remove)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send))

    print("Bot is running...")
    app.run_polling()


if __name__ == '__main__':
    main()
