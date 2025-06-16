from flask import Flask, request
import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Список плохих слов
bad_words = ['хуй', 'пизд', 'бляд', 'еба', 'совок', 'скуф', 'шлюха', 'нацист', 'фашист', 'гомик']
shlyuhobot_keywords = ['ищу парня', 'ищу девушку', 'заработай', '18+', 'ищу секс', 'перейди по ссылке']

# Простейший псевдо-ИИ: ключевые слова и ответы
pseudo_ai = {
    "кто ты": "Я Асмодей 👹, страж чата и борец с неадекватами.",
    "что ты умеешь": "Я фильтрую оскорбления и реагирую на базовые команды.",
    "как дела": "У меня всё отлично! У тебя как?",
    "зачем ты здесь": "Я защищаю чат от флуда и нецензурщины."
}

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
    user_mentioned_bot = (
        message.chat.type == 'private' or
        ('асмодей' in msg or '@' + bot.get_me().username.lower() in msg)
    )

    # Фильтрация плохих слов — реагирует всегда
    if any(bad in msg for bad in bad_words):
        bot.reply_to(message, "Пожалуйста, не используй оскорбления 🙏")
        return

    # Фильтрация ботов/спама — реагирует всегда
    if any(kw in msg for kw in shlyuhobot_keywords):
        bot.reply_to(message, "Обнаружен подозрительный бот. Сообщите админам.")
        return

    # Остальное — только если бот упомянут или это личное сообщение
    if user_mentioned_bot:
        for key_phrase in pseudo_ai:
            if key_phrase in msg:
                bot.reply_to(message, pseudo_ai[key_phrase])
                return

        if "привет" in msg or "здравствуй" in msg:
            bot.reply_to(message, f"Привет, {message.from_user.first_name}! Я бот Асмодей 👹")
        elif "помощь" in msg or "/help" in msg:
            bot.reply_to(message, "Я умею фильтровать чат от мата, оскорблений, спама и могу отвечать на приветствия. В будущем научусь большему!")
        else:
            bot.reply_to(message, "Интересно... Я подумаю над этим 🤔")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
