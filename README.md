# 🌸 Floristio Bot — Telegram-бот для цветочного магазина

Telegram-бот для цветочного магазина, который помогает выбрать и заказать букет прямо в чате. Пользователь выбирает получателя, вид цветов и способ доставки — и получает готовый заказ за несколько шагов. Встроенный AI-консультант на GigaChat отвечает на любые вопросы о магазине в свободной форме.

## Возможности

- **Каталог букетов** — подбор по получателю: жене, маме, подруге, мужчине, на свидание, на день рождения
- **Выбор цветов** — розы (от 2 900 ₽), тюльпаны (от 3 200 ₽), пионы (от 4 500 ₽), хризантемы (от 2 400 ₽), авторский букет (от 5 900 ₽)
- **Оформление заказа** — доставка или самовывоз (ул. Цветочная, 12)
- **Условия доставки** — бесплатно от 3 000 ₽, 2–3 часа; срочная +500 ₽
- **Мастер-классы** — ссылка на актуальное расписание во ВКонтакте
- **AI-консультант** — свободный чат на русском языке через GigaChat API (Сбер)

## Технологии

- Python 3.11
- [python-telegram-bot 21.9](https://github.com/python-telegram-bot/python-telegram-bot)
- [GigaChat API](https://developers.sber.ru/portal/products/gigachat) (Сбер)
- Railway (деплой, конфиг в `railway.toml`)

## Скриншоты

| Главное меню | Каталог | Оформление заказа | AI-консультант |
|:---:|:---:|:---:|:---:|
| ![Главное меню](screenshots/main-menu.png) | ![Каталог](screenshots/catalog.png) | ![Заказ](screenshots/order.png) | ![AI](screenshots/ai-chat.png) |

## Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/arysya/floristio-bot-.git
cd floristio-bot-

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Создать .env из шаблона и заполнить токены
cp .env.example .env

# 4. Запустить
python bot.py
```

### Переменные окружения (`.env`)

```
TELEGRAM_TOKEN=токен_от_BotFather
GIGACHAT_CLIENT_ID=client_id_из_кабинета_Сбер
GIGACHAT_CLIENT_SECRET=client_secret_из_кабинета_Сбер
```

Получить токен бота: [@BotFather](https://t.me/BotFather)  
Получить GigaChat credentials: [developers.sber.ru](https://developers.sber.ru/portal/products/gigachat)

## Структура проекта

```
floristio-bot/
├── bot.py          # Хендлеры, каталог, клавиатуры, system prompt
├── gigachat.py     # Клиент GigaChat API (OAuth + async чат)
├── config.py       # Загрузка переменных окружения
├── requirements.txt
├── Procfile        # Деплой (Heroku/Railway)
└── railway.toml    # Railway конфиг
```

## Деплой на Railway

1. Форкнуть репозиторий
2. Подключить к [Railway](https://railway.app)
3. Добавить переменные окружения в настройках проекта
4. Деплой запустится автоматически через `railway.toml`

## Автор

Проект создан в рамках курса по AI-автоматизации.  
По вопросам бота: [@ocean_sofya](https://t.me/ocean_sofya)
