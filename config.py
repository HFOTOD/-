import os
from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Переменная окружения {name} не заполнена")
    return value


BOT_TOKEN = _required("BOT_TOKEN")
ADMIN_ID = int(_required("ADMIN_ID"))

# Платёжка (можно оставить пустыми, пока не подключена)
PAY_API_KEY = os.getenv("PAY_API_KEY", "").strip()
PAY_WEBHOOK_SECRET = os.getenv("PAY_WEBHOOK_SECRET", "").strip()
PAY_API_URL = os.getenv("PAY_API_URL", "").strip()

# Адрес бота на Bothost (появится после создания проекта)
PUBLIC_URL = os.getenv("PUBLIC_URL", "").strip().rstrip("/")

PORT = int(os.getenv("PORT", "8080"))
DB_PATH = os.getenv("DB_PATH", "bot.db")
