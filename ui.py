# UI components and text formatting for ShopBoom bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import MANAGER_PHONE
from products import products

# Emojis for product categories
CATEGORY_EMOJIS = {
    "Одежда": "👗",
    "Обувь": "👟",
}


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown in admin panel."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👑 Статистика", callback_data="subscribers_count")],
            [InlineKeyboardButton(text="📨 Рассылка", callback_data="broadcast")],
            [InlineKeyboardButton(text="📦 Все заказы", callback_data="all_orders")],
        ]
    )


def category_keyboard(category: str) -> InlineKeyboardMarkup:
    """Keyboard with a single category button."""
    emoji = CATEGORY_EMOJIS.get(category, "")
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=f"{emoji} {category}", callback_data=f"category:{category}")]]
    )


def cart_keyboard() -> InlineKeyboardMarkup:
    """Cart button keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")]]
    )


def orders_keyboard() -> InlineKeyboardMarkup:
    """Keyboard linking to user order history."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders")]]
    )


def manager_keyboard() -> InlineKeyboardMarkup:
    """Button with manager phone number."""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📞 Связаться с менеджером", url=f"tel:{MANAGER_PHONE}")]]
    )


def categories_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard with categories and service buttons."""
    buttons = [
        [InlineKeyboardButton(text=f"{CATEGORY_EMOJIS.get(cat, '')} {cat}", callback_data=f"category:{cat}")]
        for cat in products.keys()
    ]
    buttons.append([InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")])
    buttons.append([InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders")])
    buttons.append([InlineKeyboardButton(text="📞 Связаться с менеджером", callback_data="contact_manager")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def subcategories_keyboard(category: str) -> InlineKeyboardMarkup:
    """Keyboard with subcategories for given category."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=subcategory, callback_data=f"subcategory:{category}:{subcategory}")]
            for subcategory in products[category].keys()
        ]
    )
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")])
    return keyboard


def products_keyboard(category: str, subcategory: str) -> InlineKeyboardMarkup:
    """Keyboard with products list."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=product["name"], callback_data=f"product:{product['id']}")]
            for product in products[category][subcategory]
        ]
    )
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_sub:{category}")])
    return keyboard


def buy_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """Keyboard shown on product card."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Купить", callback_data=f"buy:{product_id}")],
            [InlineKeyboardButton(text="ℹ️ Подробнее", callback_data=f"more:{product_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")],
        ]
    )


def format_orders_list(orders: list) -> str:
    """Return formatted text with orders."""
    text = "📋 <b>Все заказы:</b>\n\n"
    for idx, order in enumerate(orders, start=1):
        text += (
            f"#{idx} — {order['product']}\n"
            f"Размер: {order['size']}\n"
            f"Цена: {int(order['final_price']):,} сум\n"
            f"Имя: {order['name']}\n"
            f"Телефон: {order['phone']}\n"
            f"Адрес: {order['address']}\n\n"
        )
    return text


def format_user_history(history: list) -> str:
    """Return formatted text of user order history."""
    text = "📋 <b>Ваши заказы:</b>\n\n"
    for idx, order in enumerate(history, start=1):
        text += (
            f"#{idx} — <b>{order['product']}</b>\n"
            f"Размер: {order['size']}\n"
            f"Цена: {int(order['final_price']):,} сум\n"
            f"Телефон: {order['phone']}\n"
            f"Адрес: {order['address']}\n\n"
        )
    return text
