import asyncio
import logging
import warnings

from telegram.warnings import PTBUserWarning
warnings.filterwarnings("ignore", category=PTBUserWarning)

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    PicklePersistence,
    filters,
)

from config import TELEGRAM_TOKEN
from gigachat import GigaChatClient

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

gigachat = GigaChatClient()

# ── Состояния ──────────────────────────────────────────────────────────────
MAIN_MENU, CATALOG_CATEGORY, CATALOG_FLOWER, DELIVERY_OPTION, SELF_PICKUP_TIME, CALLBACK_PHONE, OTHER_REASON = range(7)

# ── Системный промпт ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Ты — вежливый ассистент цветочного магазина Floristio.
Отвечай кратко (2–4 предложения), по-русски, дружелюбно.
Данные магазина:
- Адрес: ул. Цветочная, 12
- Режим: 8:00–20:00 ежедневно
- Доставка: бесплатно от 3000₽, 2–3 часа, срочно +500₽
- Каталог: Розы от 2900₽, Тюльпаны от 3200₽, Пионы от 4500₽, Хризантемы от 2400₽, Авторский букет от 5900₽
- Цветы срезаются каждое утро свежими
- Мастер-классы: актуальное расписание на https://vk.ru/floristio_com
Не добавляй никакую рекламу или призыв к действию в конце ответа."""

# ── Клавиатуры ──────────────────────────────────────────────────────────────
MAIN_KB = ReplyKeyboardMarkup(
    [["🌸 Каталог", "🚚 Доставка", "🎓 Мастер-классы"]],
    resize_keyboard=True,
)

HOME_KB = ReplyKeyboardMarkup([["🏠 Главное меню"]], resize_keyboard=True)

PICKUP_KB = ReplyKeyboardMarkup(
    [["🏃 Заберу сам", "🚚 Доставка"], ["🏠 Главное меню"]],
    resize_keyboard=True,
)


def category_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💑 Жене", callback_data="cat:wife"),
         InlineKeyboardButton("👩‍👧 Маме", callback_data="cat:mother")],
        [InlineKeyboardButton("👭 Подруге", callback_data="cat:friend"),
         InlineKeyboardButton("👨 Папе/Мужчине", callback_data="cat:father")],
        [InlineKeyboardButton("💝 На свидание", callback_data="cat:date"),
         InlineKeyboardButton("🎂 На день рождения", callback_data="cat:birthday")],
        [InlineKeyboardButton("✏️ Другая причина", callback_data="cat:other")],
    ])


def delivery_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Написать менеджеру", url="https://t.me/ocean_sofya")],
        [InlineKeyboardButton("📞 Перезвоните мне", callback_data="delivery:call")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="home")],
    ])


# ── Каталог ─────────────────────────────────────────────────────────────────
CATEGORIES = {
    "wife": {
        "title": "Для жены — классика и нежность:",
        "items": [
            "🌹 *Розы* — от 2 900 ₽\nКлассика любви. Долго стоят, всегда уместны.",
            "🌸 *Пионы* — от 4 500 ₽\nНежные, ароматные — любимые цветы многих женщин.",
            "💐 *Авторский букет* — от 5 900 ₽\nИндивидуальный дизайн флориста под ваш образ.",
        ],
        "flowers": [("🌹 Розы", "flower:roses"), ("🌸 Пионы", "flower:peonies"), ("💐 Авторский", "flower:author")],
    },
    "date": {
        "title": "На свидание — что-то особенное:",
        "items": [
            "🌹 *Розы* — от 2 900 ₽\nНикогда не выходят из моды.",
            "🌸 *Пионы* — от 4 500 ₽\nАроматные и нежные — произведут впечатление.",
            "💐 *Авторский букет* — от 5 900 ₽\nСоздан специально для особого момента.",
        ],
        "flowers": [("🌹 Розы", "flower:roses"), ("🌸 Пионы", "flower:peonies"), ("💐 Авторский", "flower:author")],
    },
    "mother": {
        "title": "Маме — тёплый подарок с душой:",
        "items": [
            "🌷 *Тюльпаны* — от 3 200 ₽\nЯркие, весенние, всегда радуют.",
            "🌼 *Хризантемы* — от 2 400 ₽\nДолговечные и нежные.",
            "🌸 *Пионы* — от 4 500 ₽\nУниверсальный выбор для особого человека.",
        ],
        "flowers": [("🌷 Тюльпаны", "flower:tulips"), ("🌼 Хризантемы", "flower:chrysanthemums"), ("🌸 Пионы", "flower:peonies")],
    },
    "friend": {
        "title": "Подруге — что-то яркое и доброе:",
        "items": [
            "🌷 *Тюльпаны* — от 3 200 ₽\nЯркие и весенние, поднимут настроение.",
            "🌼 *Хризантемы* — от 2 400 ₽\nДолговечные и нежные.",
            "🌸 *Пионы* — от 4 500 ₽\nИдеально для дорогой подруги.",
        ],
        "flowers": [("🌷 Тюльпаны", "flower:tulips"), ("🌼 Хризантемы", "flower:chrysanthemums"), ("🌸 Пионы", "flower:peonies")],
    },
    "birthday": {
        "title": "На день рождения — нужен особенный букет:",
        "items": [
            "💐 *Авторский букет* — от 5 900 ₽\nСоздадим уникальный букет под именинника.",
            "🌹 *Розы (большой букет)* — от 4 500 ₽\n25, 51, 101 роза — под любой бюджет.",
            "🌷 *Яркий микс тюльпанов* — от 3 200 ₽\nПраздник красок!",
        ],
        "flowers": [("💐 Авторский", "flower:author"), ("🌹 Большой букет", "flower:big_roses"), ("🌷 Тюльпаны-микс", "flower:tulips_mix")],
    },
    "father": {
        "title": "Папе/мужчине — строгий и стильный выбор:",
        "items": [
            "🌼 *Монобукет хризантем* — от 2 400 ₽\nЛаконично, мужественно, долго стоит.",
            "🌹 *Розы (строгий букет)* — от 2 900 ₽\nТёмно-красные или белые — элегантно.",
        ],
        "flowers": [("🌼 Хризантемы", "flower:chrysanthemums"), ("🌹 Розы", "flower:roses")],
    },
}

FLOWERS = {
    "roses":          "Розы",
    "peonies":        "Пионы",
    "author":         "Авторский букет",
    "tulips":         "Тюльпаны",
    "chrysanthemums": "Хризантемы",
    "big_roses":      "Большой букет роз",
    "tulips_mix":     "Тюльпаны-микс",
}


# ── Хэндлеры ────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🌸 Привет! Я — демо-бот цветочного магазина *Floristio*.\n\n"
        "Это демонстрационная версия — вы можете:\n"
        "• 🌸 Посмотреть каталог и получить персональные рекомендации\n"
        "• 🚚 Узнать условия доставки\n"
        "• 🎓 Найти расписание мастер-классов\n\n"
        "Также можете просто написать любой вопрос 💬\n\n"
        "Выберите, что вас интересует:",
        parse_mode="Markdown",
        reply_markup=MAIN_KB,
    )
    return MAIN_MENU


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🌸 Каталог":
        await update.message.reply_text("Для кого выбираете цветы?", reply_markup=category_kb())
        return CATALOG_CATEGORY

    if text == "🚚 Доставка":
        await update.message.reply_text(
            "🚚 *Условия доставки Floristio:*\n\n"
            "• Бесплатно от 3 000 ₽\n"
            "• Время: 2–3 часа\n"
            "• Срочная доставка: +500 ₽\n"
            "• Работаем: 8:00–20:00 ежедневно\n"
            "• Самовывоз: ул. Цветочная, 12",
            parse_mode="Markdown",
            reply_markup=delivery_kb(),
        )
        return DELIVERY_OPTION

    if text == "🎓 Мастер-классы":
        await update.message.reply_text(
            "🎓 *Мастер-классы по флористике Floristio*\n\n"
            "Актуальное расписание и запись — в нашей группе ВКонтакте:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 Открыть расписание ВКонтакте", url="https://vk.ru/floristio_com")],
            ]),
        )
        await update.message.reply_text("Что-то ещё?", reply_markup=MAIN_KB)
        return MAIN_MENU

    if text == "🏃 Заберу сам":
        flower_key = context.user_data.get("selected_flower")
        flower_name = FLOWERS.get(flower_key, "букет") if flower_key else "букет"
        context.user_data["flower_name"] = flower_name
        await update.message.reply_text(
            "Укажите удобное время для самовывоза (8:00–20:00):",
            reply_markup=HOME_KB,
        )
        return SELF_PICKUP_TIME

    if text == "🏠 Главное меню":
        await update.message.reply_text("Главное меню:", reply_markup=MAIN_KB)
        return MAIN_MENU

    return await free_text(update, context)


async def on_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat = query.data.split(":", 1)[1]

    if cat == "other":
        await query.edit_message_text(
            "Расскажите, для кого и по какому поводу нужны цветы?\n"
            "Напишите текстом, и я подберу идеальный вариант 🌸"
        )
        return OTHER_REASON

    data = CATEGORIES[cat]
    body = data["title"] + "\n\n" + "\n\n".join(data["items"])
    buttons = [[InlineKeyboardButton(name, callback_data=cb)] for name, cb in data["flowers"]]
    await query.edit_message_text(body, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
    return CATALOG_FLOWER


async def on_flower(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    flower_key = query.data.split(":", 1)[1]
    flower_name = FLOWERS.get(flower_key, "букет")
    context.user_data["selected_flower"] = flower_key

    await query.edit_message_text(
        f"✅ Отличный выбор! *{flower_name}* срезаются каждое утро свежими.\n\n"
        "Как удобнее получить?",
        parse_mode="Markdown",
    )
    await query.message.reply_text("Выберите способ:", reply_markup=PICKUP_KB)
    return MAIN_MENU


async def on_pickup_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🏠 Главное меню":
        await update.message.reply_text("Главное меню:", reply_markup=MAIN_KB)
        return MAIN_MENU

    flower_name = context.user_data.get("flower_name", "букет")
    await update.message.reply_text("⏳ Бронируем...")
    await asyncio.sleep(1.5)
    await update.message.reply_text(
        f"✅ Забронировано! *{flower_name}* будет ждать вас к {text}.\n"
        "Данные переданы флористу 📋\n\n"
        "Хотите такой же бот для вашего бизнеса? → @ocean_sofya",
        parse_mode="Markdown",
        reply_markup=MAIN_KB,
    )
    return MAIN_MENU


async def on_delivery_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "delivery:call":
        await query.message.reply_text(
            "Напишите ваш номер телефона, мы перезвоним в течение 15 минут:",
            reply_markup=HOME_KB,
        )
        return CALLBACK_PHONE

    # home
    await query.message.reply_text("Главное меню:", reply_markup=MAIN_KB)
    return MAIN_MENU


async def on_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🏠 Главное меню":
        await update.message.reply_text("Главное меню:", reply_markup=MAIN_KB)
        return MAIN_MENU

    await update.message.reply_text(
        f"📞 Передали ваш номер *{text}* менеджеру!\n"
        "Перезвоним в течение 15 минут.\n\n"
        "Хотите такой же бот для вашего бизнеса? → @ocean_sofya",
        parse_mode="Markdown",
        reply_markup=MAIN_KB,
    )
    return MAIN_MENU


async def on_other_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Главное меню":
        await update.message.reply_text("Главное меню:", reply_markup=MAIN_KB)
        return MAIN_MENU
    return await free_text(update, context)


async def free_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_chat_action("typing")
    try:
        reply = await gigachat.ask(update.message.text, SYSTEM_PROMPT)
        await update.message.reply_text(reply, reply_markup=MAIN_KB)
    except Exception as e:
        logger.error(f"GigaChat error: {e}")
        await update.message.reply_text(
            "Извините, не смог обработать запрос. Напишите менеджеру: @ocean_sofya",
            reply_markup=MAIN_KB,
        )
    return MAIN_MENU


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Unhandled error: {context.error}")


# ── Запуск ──────────────────────────────────────────────────────────────────

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not set!")
        return

    persistence = PicklePersistence(filepath="bot_data")
    app = Application.builder().token(TELEGRAM_TOKEN).persistence(persistence).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        per_message=False,
        states={
            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu),
            ],
            CATALOG_CATEGORY: [
                CallbackQueryHandler(on_category, pattern="^cat:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu),
            ],
            CATALOG_FLOWER: [
                CallbackQueryHandler(on_flower, pattern="^flower:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu),
            ],
            DELIVERY_OPTION: [
                CallbackQueryHandler(on_delivery_cb, pattern="^(delivery:|home$)"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu),
            ],
            SELF_PICKUP_TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_pickup_time),
            ],
            CALLBACK_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_phone),
            ],
            OTHER_REASON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_other_reason),
            ],
        },
        fallbacks=[CommandHandler("start", cmd_start)],
    )

    app.add_handler(conv)
    app.add_error_handler(error_handler)
    logger.info("Floristio bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    import asyncio
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()
