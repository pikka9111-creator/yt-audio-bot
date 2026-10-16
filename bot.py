import os, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot
import yt_dlp

bot = telebot.TeleBot(os.environ["BOT_TOKEN"])

class Ping(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")
    def log_message(self, *args):
        pass

def run_web():
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(("0.0.0.0", port), Ping).serve_forever()

@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m, "Send me a YouTube link and I will send back the audio.")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = (m.text or "").strip()
    if "youtu" not in url:
        bot.reply_to(m, "Please send a YouTube link.")
        return
    bot.reply_to(m, "Downloading, please wait...")
    opts = {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": f"/tmp/{m.chat.id}_%(id)s.%(ext)s",
        "noplaylist": True,
        "max_filesize": 49 * 1024 * 1024,
        "quiet": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as y:
            info = y.extract_info(url, download=True)
            path = y.prepare_filename(info)
        with open(path, "rb") as f:
            bot.send_audio(m.chat.id, f, title=info.get("title"))
        os.remove(path)
    except Exception:
        bot.reply_to(m, "Sorry, I could not download that one.")

threading.Thread(target=run_web, daemon=True).start()
bot.infinity_polling()