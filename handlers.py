import uuid

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import database as db
from config import ADMIN_ID
from payments import create_payment_link

router = Router()


class NewTariff(StatesGroup):
    name = State()
    price = State()
    days = State()


# ---------- Админ ----------
@router.message(Command("addtariff"), F.from_user.id == ADMIN_ID)
async def add_start(m: Message, state: FSMContext):
    await state.set_state(NewTariff.name)
    await m.answer("Название тарифа:")


@router.message(StateFilter(NewTariff.name), F.from_user.id == ADMIN_ID)
async def add_name(m: Message, state: FSMContext):
    await state.update_data(name=m.text)
    await state.set_state(NewTariff.price)
    await m.answer("Цена (число):")


@router.message(StateFilter(NewTariff.price), F.from_user.id == ADMIN_ID)
async def add_price(m: Message, state: FSMContext):
    try:
        price = float(m.text.replace(",", "."))
    except (ValueError, AttributeError):
        return await m.answer("Введите число.")
    await state.update_data(price=price)
    await state.set_state(NewTariff.days)
    await m.answer("Срок действия в днях:")


@router.message(StateFilter(NewTariff.days), F.from_user.id == ADMIN_ID)
async def add_days(m: Message, state: FSMContext):
    if not (m.text and m.text.isdigit()):
        return await m.answer("Введите целое число.")
    data = await state.get_data()
    db.add_tariff(data["name"], data["price"], int(m.text))
    await state.clear()
    await m.answer(f"✅ Тариф «{data['name']}» создан.")


@router.message(Command("tariffs"), F.from_user.id == ADMIN_ID)
async def list_tariffs(m: Message):
    rows = db.get_tariffs()
    if not rows:
        return await m.answer("Тарифов нет.")
    await m.answer("\n".join(f"{i}: {n} — {p:g} ₽ / {d} дн." for i, n, p, d in rows))


@router.message(Command("deltariff"), F.from_user.id == ADMIN_ID)
async def del_tariff(m: Message):
    parts = m.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await m.answer("Использование: /deltariff ID")
    db.delete_tariff(int(parts[1]))
    await m.answer("Удалено.")


# ---------- Пользователь ----------
@router.message(Command("start"))
async def start(m: Message):
    rows = db.get_tariffs()
    if not rows:
        return await m.answer("Тарифов пока нет.")
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{n} — {p:g} ₽ / {d} дн.", callback_data=f"buy:{i}")]
            for i, n, p, d in rows
        ]
    )
    await m.answer("Выберите тариф:", reply_markup=kb)


@router.callback_query(F.data.startswith("buy:"))
async def buy(c: CallbackQuery):
    tariff_id = int(c.data.split(":")[1])
    tariff = db.get_tariff(tariff_id)
    if not tariff:
        return await c.answer("Тариф не найден", show_alert=True)
    name, price, _days = tariff

    order_id = uuid.uuid4().hex
    db.create_payment(order_id, c.from_user.id, tariff_id)

    try:
        url = await create_payment_link(order_id, price, f"Тариф {name}")
    except Exception as e:
        await c.message.answer(f"Не удалось создать платёж: {e}")
        return await c.answer()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="💳 Оплатить", url=url)]]
    )
    await c.message.answer(f"Тариф «{name}», {price:g} ₽", reply_markup=kb)
    await c.answer()
