import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID: int = int(os.getenv("TELEGRAM_CHAT_ID"))
BASE_URL: str = os.getenv("BASE_URL")