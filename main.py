from flask import Flask, request
import telebot
import os
import logging

# Настройка логирования для Render
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Расширенный список запрещённых слов и фраз
bad_words = [
    'хуй', 'пизд', 'бляд', 'еба', 'мразь', 'ублюдок', 'сука', 'гондон', 'пидор',
    'совок', 'скуф', 'шлюха', 'нацист', 'фашист', 'гомик', 'жид', 'чурка', 'петух'
]

# Ключевые слова, указывающие на спам/ботов
spam_keywords = [
    'ищу парня', 'ищу девушку', 'заработай', 'заработок', '18+', 'секс',
    'вебкам', 'интим', 'наркотики', 'дешёвые деньги', 'переходи по ссылке',
    'деньги без вложений', 'chatgpt', 'openai', 'нейросеть', 'искусственный интеллект',
    'ai girlfriend', 'нейросексуал', 'бот-девушка', 'создай нейросеть', 'gpt бот', 'tg ai bot'
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
    if not message.text:
        return

    msg = message.text.lower()
    user = message.from_user.username or f"id:{message.from_user.id}"
    chat_id = message.chat.id
    full_text = message.text.replace('\n', ' ').strip()

    try:
        if any(word in msg for word in bad_words):
            bot.delete_message(chat_id, message.message_id)
            bot.send_message(chat_id, f"⚠️ Сообщение от @{user} было удалено модератором.")
            logging.info(f"[Мат] Удалено сообщение от @{user} в чате {chat_id}: {full_text}")

        elif any(kw in msg for kw in spam_keywords):
            bot.delete_message(chat_id, message.message_id)
            bot.send_message(chat_id, f"🚫 Сообщение от @{user} было удалено как спам.")
            logging.info(f"[Спам] Удалено сообщение от @{user} в чате {chat_id}: {full_text}")

    except Exception as e:
        logging.error(f"[Ошибка] при удалении сообщения от @{user}: {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
