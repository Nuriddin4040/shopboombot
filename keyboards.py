from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from products import products

# Клавиатура категорий
def categories_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=category, callback_data=f"category:{category}")]
            for category in products.keys()
        ]
    )
    return keyboard

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
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]
        ]
    )
    return keyboard
