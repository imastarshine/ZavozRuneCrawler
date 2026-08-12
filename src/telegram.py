import telebot
import src.shared


def send_message(text: str):
    if not src.shared.TELEGRAM_TOKEN or not src.shared.TELEGRAM_CHAT_ID:
        return
    try:
        bot = telebot.TeleBot(token=src.shared.TELEGRAM_TOKEN)
        bot.send_message(chat_id=src.shared.TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        print(f"Failed to send telegram message: {e}")
