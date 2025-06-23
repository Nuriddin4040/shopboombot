from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from ui import (
    categories_keyboard,
    subcategories_keyboard,
    products_keyboard,
    buy_keyboard,
    category_keyboard,
    cart_keyboard,
    orders_keyboard,
    manager_keyboard,
    admin_panel_keyboard,
    format_orders_list,
    format_user_history,
    CATEGORY_EMOJIS,
)
from products import products
from config import ADMIN_ID, MANAGER_PHONE

router = Router()

user_orders = {}
subscribers = set()
orders = []
user_order_history = {}

PROMOCODES = {
    "BOOM10": 0.10,  # Промокод на 10% скидку
}

# ✅ /start
@router.message(Command("start"))
async def start(message: Message):
    """Greet user and show main menu."""
    subscribers.add(message.from_user.id)
    await message.answer("Добро пожаловать в 🛍️ <b>ShopBoom!</b>", parse_mode="HTML")
    for category in products.keys():
        await message.answer(
            f"{CATEGORY_EMOJIS.get(category, '')} <b>{category}</b>",
            reply_markup=category_keyboard(category),
            parse_mode="HTML",
        )
    await message.answer("🛒 <b>Корзина</b>", reply_markup=cart_keyboard(), parse_mode="HTML")
    await message.answer("📦 <b>Мои заказы</b>", reply_markup=orders_keyboard(), parse_mode="HTML")
    await message.answer("📞 <b>Связаться с менеджером</b>", reply_markup=manager_keyboard(), parse_mode="HTML")

# ✅ /myorders
@router.message(Command("myorders"))
async def my_orders(message: Message):
    """Send list of user orders."""
    history = user_order_history.get(message.from_user.id, [])
    if not history:
        await message.answer("🛒 У вас пока нет оформленных заказов.")
        return

    text = format_user_history(history)
    await message.answer(text, parse_mode="HTML")


@router.callback_query(F.data == "my_orders")
async def my_orders_cb(callback: CallbackQuery):
    """Callback handler for order history button."""
    history = user_order_history.get(callback.from_user.id, [])
    if not history:
        await callback.message.answer("🛒 У вас пока нет оформленных заказов.")
        return

    text = format_user_history(history)
    await callback.message.answer(text, parse_mode="HTML")

# ✅ Назад к категориям
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.answer(
        "🔙 Выберите категорию товара:",
        reply_markup=categories_keyboard(),
        parse_mode="HTML"
    )

# ✅ Показ подкатегорий
@router.callback_query(F.data.startswith("category:"))
async def show_subcategories(callback: CallbackQuery):
    category = callback.data.split(":")[1]
    await callback.message.answer(
        f"<b>Выберите подкатегорию в категории:</b> {category}",
        reply_markup=subcategories_keyboard(category),
        parse_mode="HTML"
    )

# ✅ Назад к подкатегориям
@router.callback_query(F.data.startswith("back_to_sub:"))
async def back_to_subcategory(callback: CallbackQuery):
    category = callback.data.split(":")[1]
    await callback.message.answer(
        f"🔙 Выберите подкатегорию в категории: {category}",
        reply_markup=subcategories_keyboard(category),
        parse_mode="HTML"
    )

# ✅ Показ товаров
@router.callback_query(F.data.startswith("subcategory:"))
async def show_products(callback: CallbackQuery):
    _, category, subcategory = callback.data.split(":")
    await callback.message.answer(
        f"<b>Товары в подкатегории:</b> {subcategory}",
        reply_markup=products_keyboard(category, subcategory),
        parse_mode="HTML"
    )

# ✅ Показ карточки товара
@router.callback_query(F.data.startswith("product:"))
async def show_product(callback: CallbackQuery):
    product_id = int(callback.data.split(":")[1])

    for category_name, subcats in products.items():
        for subcat_name, items in subcats.items():
            for item in items:
                if item["id"] == product_id:
                    photo = FSInputFile(item["photo"])
                    await callback.message.answer_photo(
                        photo=photo,
                        caption=(
                            f"🛍️ <b>{item['name']}</b>\n"
                            f"💸 <b>Цена:</b> <code>{item['price']:,} сум</code>\n"
                            "📏 <b>Размеры:</b> S, M, L, XL\n"
                            f"📄 <b>Описание:</b> {item['description']}"
                        ),
                        reply_markup=buy_keyboard(product_id),
                        parse_mode="HTML",
                    )
                    return

# ✅ Начало оформления заказа -> имя
@router.callback_query(F.data.startswith("buy:"))
async def start_order(callback: CallbackQuery):
    try:
        product_id = int(callback.data.split(":")[1])
        user_orders[callback.from_user.id] = {"product_id": product_id}
        print(
            f"Buy callback from {callback.from_user.id}, product {product_id}"
        )
        await callback.message.answer(
            "👤 Введите ваше <b>имя</b>:",
            parse_mode="HTML",
        )
    except Exception as e:
        print(f"❗ Error in start_order: {e}")
        await callback.message.answer(
            "Произошла ошибка. Попробуйте ещё раз или обратитесь к менеджеру."
        )

# ✅ Отмена заказа
@router.callback_query(F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery):
    user_orders.pop(callback.from_user.id, None)
    await callback.message.answer("❌ Ваш заказ был отменён.")


@router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    await callback.message.answer("🛒 Ваша корзина пока пуста.")


@router.callback_query(F.data == "contact_manager")
async def contact_manager(callback: CallbackQuery):
    await callback.message.answer(
        f"<b>Телефон менеджера:</b> {MANAGER_PHONE}", parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("more:"))
async def show_more(callback: CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    for cat in products.values():
        for subcat in cat.values():
            for item in subcat:
                if item["id"] == product_id:
                    await callback.message.answer(
                        f"📄 <b>Описание товара:</b> {item['description']}",
                        parse_mode="HTML",
                    )
                    return

# ✅ Выбор размера → Промокод
@router.callback_query(F.data.startswith("size:"))
async def ask_promocode(callback: CallbackQuery):
    size = callback.data.split(":")[1]
    if callback.from_user.id in user_orders:
        user_orders[callback.from_user.id]["size"] = size
        print(f"Size selected by {callback.from_user.id}: {size}")
        await callback.message.answer(
            "Если у вас есть промокод, отправьте его сейчас 🎟️.\n\n"
            "Или введите любое сообщение, чтобы продолжить без скидки."
        )

# ✅ Проверка промокода
@router.message(
    lambda message: (
        message.from_user.id in user_orders
        and "size" in user_orders[message.from_user.id]
        and "promocode_checked" not in user_orders[message.from_user.id]
    )
)
async def check_promocode(message: Message):
    promocode = message.text.strip()
    print(f"Promocode received from {message.from_user.id}: {promocode}")
    user_orders[message.from_user.id]["promocode_checked"] = True

    if promocode.upper() in PROMOCODES:
        user_orders[message.from_user.id]["discount"] = PROMOCODES[promocode.upper()]
        await message.answer(
            f"🎁 <b>Ваш промокод активен:</b> <code>{promocode.upper()}</code> — скидка {int(PROMOCODES[promocode.upper()] * 100)}%!",
            parse_mode="HTML",
        )
    else:
        user_orders[message.from_user.id]["discount"] = 0

    await finalize_order(message)

# ✅ Имя → Телефон → Адрес
@router.message(
    lambda message: (
        message.from_user.id in user_orders
        and "name" not in user_orders[message.from_user.id]
    )
)
async def ask_phone(message: Message):
    user_orders[message.from_user.id]["name"] = message.text
    print(f"Name received from {message.from_user.id}: {message.text}")
    await message.answer(
        "Введите ваш <b>номер телефона</b>:", parse_mode="HTML"
    )

@router.message(
    lambda message: (
        message.from_user.id in user_orders
        and "name" in user_orders[message.from_user.id]
        and "phone" not in user_orders[message.from_user.id]
    )
)
async def ask_address(message: Message):
    user_orders[message.from_user.id]["phone"] = message.text
    print(f"Phone received from {message.from_user.id}: {message.text}")
    await message.answer(
        "Введите ваш <b>адрес доставки</b>:", parse_mode="HTML"
    )

@router.message(
    lambda message: (
        message.from_user.id in user_orders
        and "name" in user_orders[message.from_user.id]
        and "phone" in user_orders[message.from_user.id]
        and "address" not in user_orders[message.from_user.id]
    )
)
async def ask_size(message: Message):
    user_orders[message.from_user.id]["address"] = message.text
    print(f"Address received from {message.from_user.id}: {message.text}")
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="S", callback_data="size:S"),
                InlineKeyboardButton(text="M", callback_data="size:M"),
                InlineKeyboardButton(text="L", callback_data="size:L"),
                InlineKeyboardButton(text="XL", callback_data="size:XL"),
            ],
            [InlineKeyboardButton(text="❌ Отменить заказ", callback_data="cancel_order")],
        ]
    )
    await message.answer("🧵 Выберите размер:", reply_markup=kb)

# ✅ Завершение заказа + автосохранение
async def finalize_order(message: Message):
    order = user_orders.pop(message.from_user.id)
    print(f"Finalizing order for {message.from_user.id}: {order}")

    product = None
    for cat in products.values():
        for subcat in cat.values():
            for prod in subcat:
                if prod["id"] == order["product_id"]:
                    product = prod
                    break

    if product:
        price = product['price']
        discount = order.get("discount", 0)
        final_price = price * (1 - discount)

        full_order = {
            "user_id": message.from_user.id,
            "product": product["name"],
            "size": order.get("size", "Не выбран"),
            "name": order["name"],
            "phone": order["phone"],
            "address": order["address"],
            "final_price": final_price
        }
        orders.append(full_order)

        if message.from_user.id not in user_order_history:
            user_order_history[message.from_user.id] = []
        user_order_history[message.from_user.id].append(full_order)

        # Сообщение клиенту
        await message.answer(
            f"🎉 <b>Заказ оформлен!</b>\n\n"
            f"📦 <b>Товар:</b> {product['name']}\n"
            f"📏 <b>Размер:</b> {order.get('size', 'Не выбран')}\n"
            f"💵 <b>Цена со скидкой:</b> {int(final_price):,} сум\n\n"
            "Посмотреть ваши заказы можно по кнопке ниже.",
            reply_markup=orders_keyboard(),
            parse_mode="HTML",
        )

        # Сообщение админу
        await message.bot.send_message(
            chat_id=int(ADMIN_ID),
            text=(
                f"🚨 <b>Новый заказ!</b>\n\n"
                f"📦 <b>Товар:</b> {product['name']}\n"
                f"📏 <b>Размер:</b> {order.get('size', 'Не выбран')}\n"
                f"💵 <b>Цена со скидкой:</b> {int(final_price):,} сум\n"
                f"👤 <b>Имя:</b> {order['name']}\n"
                f"📞 <b>Телефон:</b> {order['phone']}\n"
                f"🏠 <b>Адрес:</b> {order['address']}"
            ),
            parse_mode="HTML"
        )

        # ✅ Сохраняем заказ в файл
        try:
            with open("data/orders.txt", "a", encoding="utf-8") as file:
                file.write(
                    f"Заказ №{len(orders)}\n"
                    f"Товар: {product['name']}\n"
                    f"Размер: {order.get('size', 'Не выбран')}\n"
                    f"Цена со скидкой: {int(final_price):,} сум\n"
                    f"Имя: {order['name']}\n"
                    f"Телефон: {order['phone']}\n"
                    f"Адрес: {order['address']}\n"
                    f"---\n\n"
                )
        except Exception as e:
            print(f"❗ Ошибка при записи заказа в файл: {e}")

# ✅ /admin
@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Display admin menu with management actions."""
    if message.from_user.id != int(ADMIN_ID):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return

    # Show admin panel with modern buttons
    await message.answer(
        "👑 <b>Админ-панель:</b>",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )

# ✅ Кнопки админ-панели
@router.callback_query(F.data == "subscribers_count")
async def show_subscribers(callback: CallbackQuery):
    """Show total subscribers in a popup message."""
    count = len(subscribers)
    await callback.answer(f"👥 Подписчиков: {count}", show_alert=True)

@router.callback_query(F.data == "all_orders")
async def show_all_orders(callback: CallbackQuery):
    """Send list of all orders to admin."""
    if not orders:
        await callback.answer("📭 Заказов пока нет", show_alert=True)
        return

    text = format_orders_list(orders)
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer("✅ Готово")

@router.callback_query(F.data == "broadcast")
async def start_broadcast(callback: CallbackQuery):
    """Ask admin to send broadcast text."""
    await callback.answer("Введите текст рассылки", show_alert=True)
    await callback.message.answer("✍️ Напишите текст для рассылки:")

@router.message(lambda message: message.from_user.id == int(ADMIN_ID))
async def send_broadcast(message: Message):
    """Send broadcast message to all subscribers."""
    text = message.text
    for user_id in subscribers:
        try:
            await message.bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            print(f"❗ Не удалось отправить сообщение пользователю {user_id}: {e}")

    await message.answer("✅ Рассылка завершена.", reply_markup=admin_panel_keyboard())


# ✅ Фолбэк для незавершённых заказов
@router.message(lambda message: message.from_user.id in user_orders)
async def order_error(message: Message):
    """Handle unexpected messages during the order flow."""
    print(f"Unexpected message from {message.from_user.id}: {message.text}")
    await message.answer(
        "⚠️ Произошла ошибка при оформлении заказа. Попробуйте ещё раз!"
    )
