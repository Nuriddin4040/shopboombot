from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from products import products
from config import MANAGER_PHONE

# Emojis for categories
CATEGORY_EMOJIS = {
    "Одежда": "👗",
    "Обувь": "👟"
}


def category_keyboard(category: str) -> InlineKeyboardMarkup:
    """Keyboard with a single category button."""
    emoji = CATEGORY_EMOJIS.get(category, "")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{emoji} {category}", callback_data=f"category:{category}")]
        ]
    )


def cart_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🛒 Корзина", callback_data="cart")]]
    )


def orders_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders")]]
    )


def manager_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📞 Связаться с менеджером", url=f"tel:{MANAGER_PHONE}")]]
    )

# Клавиатура категорий
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

# Клавиатура подкатегорий
def subcategories_keyboard(category):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=subcategory, callback_data=f"subcategory:{category}:{subcategory}")]
            for subcategory in products[category].keys()
        ]
    )
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")])
    return keyboard

# Клавиатура товаров
def products_keyboard(category, subcategory):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=product["name"], callback_data=f"product:{product['id']}")]
            for product in products[category][subcategory]
        ]
    )
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_sub:{category}")])
    return keyboard

# Клавиатура «Купить»
def buy_keyboard(product_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Купить", callback_data=f"buy:{product_id}")],
            [InlineKeyboardButton(text="ℹ️ Подробнее", callback_data=f"more:{product_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
        ]
    )
    return keyboard
