from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import ADMIN_ID
from database import (
    get_user,
    increment_tasks,
    subscribe_user,
    record_exitpoll,
    exitpoll_stats,
)


task_router = Router()


def get_lang(obj) -> str:
    code = getattr(obj.from_user, "language_code", "ru") or "ru"
    if str(code).startswith("uz"):
        return "uz"
    return "ru"


TEXTS = {
    "task_done": {
        "ru": "📚 Задача решена! Осталось {remain} из 3 бесплатных.",
        "uz": "📚 Vazifa bajarildi! {remain}/3 bepul qoldi.",
    },
    "task_done_unlimited": {
        "ru": "📚 Задача решена! У вас активна подписка.",
        "uz": "📚 Vazifa bajarildi! Sizda obuna faollashtirilgan.",
    },
    "no_more": {
        "ru": "Бесплатные задачи закончились. Хотите купить подписку?",
        "uz": "Bepul vazifalar tugadi. Obuna sotib olasizmi?",
    },
    "subscribed": {
        "ru": "Спасибо за подписку!",
        "uz": "Obuna uchun rahmat!",
    },
    "exit_question": {
        "ru": "😕 Не купил, потому что…",
        "uz": "😕 Nega sotib olmadingiz…",
    },
    "thanks": {
        "ru": "Спасибо за ответ!",
        "uz": "Javob uchun rahmat!",
    },
}

REASONS = {
    "expensive": {"ru": "💸 Дорого", "uz": "💸 Qimmat"},
    "noneed": {"ru": "😐 Не нужно", "uz": "😐 Kerak emas"},
    "card": {"ru": "❌ Карта не проходит", "uz": "❌ Karta o'tmayapti"},
}


def subscribe_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text={"ru": "Купить подписку", "uz": "Obuna sotib olish"}[lang],
                    callback_data="subscribe",
                )
            ],
            [
                InlineKeyboardButton(
                    text={"ru": "Не покупать", "uz": "Sotib olmayman"}[lang],
                    callback_data="no_subscribe",
                )
            ],
        ]
    )


def exitpoll_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=REASONS["expensive"][lang], callback_data="exit_expensive")],
            [InlineKeyboardButton(text=REASONS["noneed"][lang], callback_data="exit_noneed")],
            [InlineKeyboardButton(text=REASONS["card"][lang], callback_data="exit_card")],
        ]
    )


@task_router.message(Command("task"))
async def handle_task(message: Message):
    lang = get_lang(message)
    used, subscribed = get_user(message.from_user.id)
    if subscribed:
        await message.answer(TEXTS["task_done_unlimited"][lang])
        return

    if used < 3:
        new_used = increment_tasks(message.from_user.id)
        remain = max(0, 3 - new_used)
        await message.answer(TEXTS["task_done"][lang].format(remain=remain))
    else:
        await message.answer(TEXTS["no_more"][lang], reply_markup=subscribe_keyboard(lang))


@task_router.callback_query(F.data == "subscribe")
async def cb_subscribe(callback: CallbackQuery):
    lang = get_lang(callback)
    subscribe_user(callback.from_user.id)
    await callback.message.answer(TEXTS["subscribed"][lang])
    await callback.answer()


@task_router.callback_query(F.data == "no_subscribe")
async def cb_no_subscribe(callback: CallbackQuery):
    lang = get_lang(callback)
    await callback.message.answer(
        TEXTS["exit_question"][lang],
        reply_markup=exitpoll_keyboard(lang),
    )
    await callback.answer()


@task_router.callback_query(F.data.startswith("exit_"))
async def cb_exitpoll(callback: CallbackQuery):
    lang = get_lang(callback)
    reason = callback.data.split("_")[1]
    record_exitpoll(callback.from_user.id, reason)
    await callback.message.answer(TEXTS["thanks"][lang])
    await callback.answer()


@task_router.message(Command("exitpoll"))
async def cmd_exitpoll(message: Message):
    if message.from_user.id != int(ADMIN_ID):
        return
    stats = exitpoll_stats()
    if not stats:
        await message.answer("Нет данных за последние сутки.")
        return
    text = "Статистика отказов за 24 часа:\n"
    for key, count in stats.items():
        reason = REASONS.get(key, {}).get("ru", key)
        text += f"{reason}: {count}\n"
    await message.answer(text)
