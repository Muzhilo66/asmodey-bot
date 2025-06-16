
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
    WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")

    if not WEBHOOK_HOST:
        return "❌ RENDER_EXTERNAL_URL не задан", 500

    if not WEBHOOK_HOST.endswith('/'):
        WEBHOOK_HOST += '/'

    WEBHOOK_URL = WEBHOOK_HOST + TOKEN
    print(f"📡 Устанавливаем webhook на: {WEBHOOK_URL}")

    bot.remove_webhook()
    success = bot.set_webhook(url=WEBHOOK_URL)

    if success:
        return "✅ Webhook установлен!", 200
    else:
        return "❌ Не удалось установить webhook", 500


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    msg = message.text.lower()

    if any(word in msg for word in bad_words):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, "⚠️ Сообщение удалено: не ругайся и не оскорбляй.")
        except Exception as e:
            print(f"❌ Не удалось удалить сообщение: {e}")
            bot.reply_to(message, "⚠️ Не ругайся и не оскорбляй.")
    elif any(kw in msg for kw in spam_keywords):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, "🚫 Спам удалён. Уведомите администратора, если это ошибка.")
        except Exception as e:
            print(f"❌ Не удалось удалить спам: {e}")
            bot.reply_to(message, "🚫 Спам/бот-объявление. Уведомите администратора.")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
