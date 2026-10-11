import telebot
from telebot import types
import os
import requests

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8976604693:AAHAEa97Vg9TpjobX_JuP0juCXU12RneYj4")
VPN_LINK = "https://raw.githubusercontent.com/ivanminakow-code/Chester-Vpn/refs/heads/main/SUBSCRIBE%20(1)%20(1).txt"
CHANNEL = "@ChesterVPNnews"
PROMO_URL = "https://raw.githubusercontent.com/ivanminakow-code/Chester-Vpn/refs/heads/main/c.txt"
PRICE_STARS = 5
# ===============================

bot = telebot.TeleBot(BOT_TOKEN)

USED_CODES_FILE = "used_codes.txt"
PAID_USERS_FILE = "paid_users.txt"


def load_used_codes():
    if not os.path.exists(USED_CODES_FILE):
        return set()
    with open(USED_CODES_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_used_code(code):
    with open(USED_CODES_FILE, "a") as f:
        f.write(code + "\n")


def load_paid_users():
    if not os.path.exists(PAID_USERS_FILE):
        return set()
    with open(PAID_USERS_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_paid_user(user_id):
    with open(PAID_USERS_FILE, "a") as f:
        f.write(str(user_id) + "\n")


def get_promo_codes():
    try:
        r = requests.get(PROMO_URL, timeout=10)
        if r.status_code == 200:
            return set(line.strip() for line in r.text.splitlines() if line.strip())
    except Exception:
        pass
    return set()


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn_channel = types.InlineKeyboardButton(
        text="📢 Подписаться на канал",
        url=f"https://t.me/{CHANNEL.lstrip('@')}"
    )
    btn_check = types.InlineKeyboardButton(
        text="✅ Я подписался",
        callback_data="check_sub"
    )
    markup.add(btn_channel)
    markup.add(btn_check)
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в ChesterVPN!\n\n"
        "Чтобы продолжить, подпишитесь на наш канал и нажмите «Я подписался».",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_sub(call):
    markup = types.InlineKeyboardMarkup()
    btn_buy = types.InlineKeyboardButton(
        text=f"💫 Купить VPN за {PRICE_STARS} звёзд (НАВСЕГДА)",
        callback_data="buy"
    )
    btn_promo = types.InlineKeyboardButton(
        text="🎟 Ввести промокод",
        callback_data="promo"
    )
    markup.add(btn_buy)
    markup.add(btn_promo)
    bot.edit_message_text(
        "✅ Отлично! Выберите действие:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "buy")
def send_invoice(call):
    bot.send_invoice(
        chat_id=call.message.chat.id,
        title="ChesterVPN (НАВСЕГДА)",
        description="Пожизненный доступ к ChesterVPN",
        invoice_payload="chester_payment",
        provider_token="",
        currency="XTR",
        prices=[types.LabeledPrice(label="ChesterVPN", amount=PRICE_STARS)]
    )
    bot.answer_callback_query(call.id)


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    user_id = str(message.from_user.id)
    paid_users = load_paid_users()
    if user_id not in paid_users:
        save_paid_user(user_id)
    bot.send_message(
        message.chat.id,
        f"✅ Оплата прошла! Вот ваша ссылка:\n\n`{VPN_LINK}`",
        parse_mode='Markdown'
    )


@bot.callback_query_handler(func=lambda call: call.data == "promo")
def ask_promo(call):
    bot.send_message(
        call.message.chat.id,
        "🎟 Введите промокод:"
    )
    bot.answer_callback_query(call.id)


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip()

    if text.lower() in ["да", "купил", "куплено", "оплатил"]:
        return

    used_codes = load_used_codes()
    promo_codes = get_promo_codes()

    if text in promo_codes:
        if text in used_codes:
            bot.send_message(message.chat.id, "❌ КОД УЖЕ ВВЕДЕН")
            return

        save_used_code(text)
        bot.send_message(
            message.chat.id,
            f"✅ Промокод принят! Вот ваша ссылка:\n\n`{VPN_LINK}`",
            parse_mode='Markdown'
        )
    else:
        bot.send_message(message.chat.id, "❌ НЕВЕРНЫЙ КОД")


if __name__ == "__main__":
    bot.polling(none_stop=True)
