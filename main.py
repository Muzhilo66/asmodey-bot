
from flask import Flask, request
import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Расширенный список запрещённых слов и фраз
bad_words = [
    'хуй', 'пизд', 'бляд', 'еба', 'мразь', 'ублюдок', 'сука', 'гондон', 'пидор',
    'совок', 'скуф', 'шлюха', 'нацист', 'фашист', 'гомик', 'жид', 'чурка', 'петух'
]
spam_keywords = [
    'ищу парня', 'ищу девушку', 'заработай', 'заработок', '18+', 'секс',
    'вебкам', 'интим', 'наркотики', 'дешёвые деньги', 'переходи по ссылке',
    'деньги без вложений'
]

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv("RENDER_EXTERNAL_URL") + TOKEN)
    return "!", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    msg = message.text.lower()

    if any(word in msg for word in bad_words):
        bot.reply_to(message, "⚠️ Не ругайся и не оскорбляй.")
    elif any(kw in msg for kw in spam_keywords):
        bot.reply_to(message, "🚫 Спам/бот-объявление. Уведомите администратора.")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
