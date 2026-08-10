---
name: floristio-bot
description: Telegram-бот для цветочного магазина Floristio с AI-консультантом на GigaChat. Позволяет выбрать букет по получателю, оформить заказ и получить ответ на любой вопрос о магазине.
---

# Floristio Bot

Telegram-бот для цветочного магазина. Пользователь выбирает получателя → вид цветов → способ получения. Свободные вопросы обрабатывает GigaChat с системным промптом магазина.

## Архитектура

- `bot.py` — основной файл: ConversationHandler (7 состояний), каталог CATEGORIES/FLOWERS, клавиатуры, system prompt для GigaChat
- `gigachat.py` — GigaChatClient: OAuth-авторизация через Сбер, async HTTP через httpx, temperature 0.7
- `config.py` — загрузка .env через python-dotenv

## Запуск

```bash
pip install -r requirements.txt
cp .env.example .env  # заполнить токены
python bot.py
```

## Переменные окружения

```
TELEGRAM_TOKEN       — от @BotFather
GIGACHAT_CLIENT_ID   — из кабинета Сбер
GIGACHAT_CLIENT_SECRET
```

## Состояния бота (ConversationHandler)

| Состояние | Описание |
|-----------|----------|
| MAIN_MENU | Главное меню: Каталог / Доставка / Мастер-классы |
| CATALOG_CATEGORY | Выбор получателя (6 категорий + «Другая причина») |
| CATALOG_FLOWER | Выбор цветка из категории |
| DELIVERY_OPTION | Доставка или самовывоз |
| SELF_PICKUP_TIME | Ввод времени самовывоза |
| CALLBACK_PHONE | Ввод номера для обратного звонка |
| OTHER_REASON | Свободный текст → GigaChat |

## Каталог цветов и цены

| Цветок | Цена от |
|--------|---------|
| Хризантемы | 2 400 ₽ |
| Розы | 2 900 ₽ |
| Тюльпаны | 3 200 ₽ |
| Пионы | 4 500 ₽ |
| Авторский букет | 5 900 ₽ |

## Деплой

Railway: конфиг в `railway.toml` (builder: nixpacks, startCommand: `python bot.py`). Persistence через PicklePersistence (файл `bot_data`).

## Что умеет AI-консультант

GigaChat получает системный промпт с данными магазина (адрес, режим работы, цены, условия доставки) и отвечает кратко (2-4 предложения) на любой свободный вопрос пользователя.
