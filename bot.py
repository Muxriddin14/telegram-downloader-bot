import os
import uuid
import yt_dlp
import warnings
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatAction

warnings.filterwarnings("ignore", category=UserWarning)

TOKEN = os.environ.get("BOT_TOKEN")

def start(update, context):
    user = update.message.from_user.first_name or "foydalanuvchi"
    update.message.reply_text(
        f"👋 Salom, {user}!\n\n"
        "🎬 Menga YouTube, TikTok yoki Instagram videoning linkini yuboring.\n"
        "Men uni siz uchun yuklab beraman 📥"
    )

def download_video(update, context):
    url = update.message.text.strip()
    chat_id = update.message.chat_id

    if not url.startswith("http"):
        update.message.reply_text("❌ Iltimos, to‘g‘ri video link yuboring.")
        return

    temp_id = str(uuid.uuid4())
    file_path = f"{temp_id}.mp4"
    title = "🎬 Video"

    context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VIDEO)
    update.message.reply_text(
        "⏳ *Video yuklab olinmoqda...*\n\n"
        "🕒 Bu jarayon odatda *30 soniya* vaqt oladi.\n"
        "📂 Agar video hajmi katta bo‘lsa, *ko‘proq vaqt* ketishi mumkin.\n",
        parse_mode="Markdown"
    )

    ydl_opts = {
        'outtmpl': file_path,
        'format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'http_chunksize': 1048576,
        'retries': 5,
        'fragment_retries': 5,
        'socket_timeout': 30,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = (
                info.get("fulltitle") or
                info.get("description") or
                info.get("title") or
                "🎬 Video"
            )
            if len(title) > 200:
                title = title[:197] + "..."

        with open(file_path, 'rb') as f:
            context.bot.send_video(chat_id=chat_id, video=f, caption=f"📥 Yuklandi:\n{title}", timeout=180)

        update.message.reply_text("✅ Yuklab berildi! Yana video yubormoqchi bo‘lsangiz, linkni tashlang 🎯")

    except Exception as e:
        update.message.reply_text(f"🚫 Xatolik yuz berdi:\n`{str(e)}`", parse_mode="Markdown")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_video))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
