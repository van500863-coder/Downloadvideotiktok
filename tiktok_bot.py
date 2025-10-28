import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
from dotenv import load_dotenv

# Load .env file (optional)
load_dotenv()

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN") or "7668584253:AAH9K8aSpcUINeHKT8GB4DdZMf0irqc2wmg"  # Replace with your token
# ==============

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# yt-dlp options: download best video ≤720p, no watermark
ydl_opts = {
    'format': 'best[height<=720][ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}

# Ensure download folder exists
os.makedirs("downloads", exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me a TikTok link and I'll download the video for you! (No watermark)\n\n"
        "Example:\nhttps://www.tiktok.com/@username/video/1234567890"
    )


async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id

    # Validate TikTok URL
    if "tiktok.com" not in url and "vm.tiktok.com" not in url:
        await update.message.reply_text("Please send a valid TikTok link.")
        return

    status_msg = await update.message.reply_text("Downloading video...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            ext = info['ext']
            file_path = f"downloads/{video_id}.{ext}"

        # Send video
        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption=f"@{info.get('uploader', 'Unknown')} | #{video_id}\nDownloaded by your bot",
                supports_streaming=True
            )

        # Cleanup
        os.remove(file_path)
        await status_msg.edit_text("Video sent!")

    except Exception as e:
        logger.error(f"Error: {e}")
        await status_msg.edit_text(f"Failed to download: {str(e)[:100]}")
        # Cleanup on failure
        for ext in ['mp4', 'webm', 'mkv']:
            path = f"downloads/{video_id}.{ext}" if 'video_id' in locals() else None
            if path and os.path.exists(path):
                os.remove(path)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send))

    print("Bot is running... Send a TikTok link!")
    app.run_polling()


if __name__ == '__main__':
    main()