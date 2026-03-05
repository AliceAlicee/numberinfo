import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from flask import Flask
from threading import Thread

API_KEY = "b36513a44a57540575cbdca431ded599"
TELEGRAM_TOKEN = "8111152534:AAEwRiS6If_wpMwjo4Xpn2HumIKnKzRJ_BU"

# ==========================
# Flask сервер для Render 24/7
# ==========================
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# ==========================
# Команда /start
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет 👋\n\n"
        "Отправь номер телефона в формате +79991234567\n"
        "или используй команду:\n"
        "/check +79991234567"
    )

# ==========================
# Команда /check
# ==========================
async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Укажи номер после команды.\nПример:\n/check +79991234567"
        )
        return
    phone = context.args[0]
    await check_phone_logic(update, phone)

# ==========================
# Проверка номера
# ==========================
async def check_phone_logic(update: Update, phone: str):
    url = f"https://apilayer.net/api/validate?access_key={API_KEY}&number={phone}"
    try:
        response = requests.get(url, timeout=10).json()
    except Exception as e:
        await update.message.reply_text(f"Ошибка запроса: {e}")
        return

    if not response.get("valid"):
        await update.message.reply_text("Номер некорректный ❌")
        return

    country = response.get("country_name", "Неизвестно")
    carrier = response.get("carrier", "Неизвестно")
    line_type = response.get("line_type", "Неизвестно")

    msg = (
        f"📱 Номер: {phone}\n"
        f"🌍 Страна: {country}\n"
        f"📡 Оператор: {carrier}\n"
        f"📞 Тип: {line_type}"
    )

    await update.message.reply_text(msg)

# ==========================
# Если пользователь просто отправил текст
# ==========================
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    await check_phone_logic(update, phone)

# ==========================
# Запуск бота
# ==========================
def main():
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("check", check_command))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Бот запущен...")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
