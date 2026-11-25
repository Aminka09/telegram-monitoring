import os
import requests
import hashlib
import telebot

# --- НАСТРОЙКИ (не меняй имена переменных!) ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
URL = os.getenv("CHECK_URL")
CHECK_TEXT = os.getenv("CHECK_TEXT", "")  # Можно оставить пустым, тогда будет проверять весь текст
# ------------------------------------------

bot = telebot.TeleBot(TOKEN)

def get_page_hash(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return hashlib.md5(response.text.encode('utf-8')).hexdigest()
        return None
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return None

def send_alert(message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")
        print("✅ Сообщение отправлено.")
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

# Логика проверки
current_hash = get_page_hash(URL)
if not current_hash:
    print("Не удалось получить страницу. Пропускаем.")
    exit(0)

# GitHub не умеет хранить состояние между запусками, поэтому мы будем сравнивать с "эталоном" в переменной окружения
# Для простоты: если ты хочешь ловить ЛЮБЫЕ изменения — мы не можем хранить last_hash в скрипте.
# Поэтому тут два варианта логики:
# 1) Ловим появление конкретной фразы (CHECK_TEXT) — самый простой и надёжный вариант.
# 2) Если CHECK_TEXT пустой — просто сообщаем, что страница доступна (это не алерт, а тест).

if CHECK_TEXT:
    # Проверяем, есть ли фраза на странице
    try:
        resp_text = requests.get(URL, timeout=10).text
        if CHECK_TEXT in resp_text:
            alert_text = (
                "🚨 <b>Обнаружено изменение!</b>\n\n"
                f"Найдена фраза: <code>{CHECK_TEXT}</code>\n"
                f"Страница: {URL}\n"
                "Проверь прямо сейчас."
            )
            send_alert(alert_text)
        else:
            print(f"Фраза '{CHECK_TEXT}' не найдена. Всё спокойно.")
    except Exception as e:
        print(f"Ошибка при проверке текста: {e}")
else:
    # Если фраза не задана, просто логируем, что скрипт отработал (чтобы видеть в логах GitHub)
    print(f"Скрипт отработал. Хэш страницы: {current_hash}")
