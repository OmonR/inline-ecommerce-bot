from aiogram import types
from config import ADDRESSES
from db import cart_db, orders_db, users_db, products_db
from keyboards.user_keyboards import user_cart_buttons, generate_inline_keyboard, get_quantity_keyboard
from utils.utils import escape_html, data_splitter


def product_caption(product_name, product_price):
    return f"<b>{escape_html(product_name)}</b>\n\n› <code>{escape_html(str(product_price))}₽</code>\n› <i>Добавить товар в корзину / Сделать заказ</i>"


async def get_cart_message(user_id: int):
    cart = await cart_db.get_cart(user_id)
    if not cart:
        return
    cart_lines = [
        f"› {item['name']} {item['quantity']}шт. <code>{escape_html(str(item['price'] * item['quantity']))}₽</code>"
        for item in cart
    ]
    cart_summary = "\n".join(cart_lines)

    total_price = sum(item["total_price"] for item in cart)

    cart_message = (
        cart_summary + f"\n\nИтого: <code>{escape_html(str(total_price))}₽</code>"
    )
    return cart_message


async def format_cart(user_id: int):
    cart = await cart_db.get_cart(user_id)
    user = await users_db.get_user_by_id(user_id)

    if not user:
        return

    message = f"<b>🛒 Корзина</b>\n\n"
    if not cart:
        return message + "пусто"

    cart_message = await get_cart_message(user_id)

    return message + cart_message


async def get_user_cart(message: types.Message):
    user_id = message.from_user.id
    cart = await cart_db.get_cart(user_id)
    current_price = sum(item["total_price"] for item in cart)
    markup = user_cart_buttons(current_price)
    profile_message = await format_cart(user_id)

    await message.answer(profile_message, reply_markup=markup, parse_mode="HTML")


async def product_add(callback_query: types.CallbackQuery):
    data = await data_splitter(callback_query.data)

    try:
        product_id = int(data[-2])
        quantity = int(data[-1])
    except ValueError:
        return

    product = await products_db.get_product_by_id(product_id)

    if product:
        user_id = callback_query.from_user.id
        await cart_db.add_product_to_cart(user_id, product_id, quantity)
        return {
            "product_name": product["name"],
            "product_price": product["price"],
            "product_quantity": quantity,
            "product_id": product_id,
        }


async def new_order(user_id: int, delivery_method: str, adress: str = None):

    active_order = await orders_db.get_active_order(user_id)
    if active_order:
        return None

    user = await users_db.get_user_by_id(user_id)

    if adress:
        user_geo = adress
    else:
        user_geo = user["geo"]  # Используем адрес пользователя, если не указан новый

    cart = await cart_db.get_cart(user_id)
    total_price = sum(item["total_price"] for item in cart)

    await orders_db.add_order(
        user_id, order_total=total_price, order_type=delivery_method, geo=user_geo
    )

    order = await orders_db.get_last_order_by_user(user_id)
    return order

async def get_orders(message):
    user_id = message.from_user.id
    orders = await orders_db.get_orders_by_user(user_id)
    buttons = [f"Заказ #{order[1]}{order[0]}" for order in orders]
    callback_data = [f"listorder_{order[0]}" for order in orders]
    markup = generate_inline_keyboard(
            buttons,
            max_buttons=5,
            callback=callback_data,
            page=1,
            buttons_key="orders",
            total_buttons_key="orders",
        )
    if markup:
        await message.answer("Ваши заказы:", reply_markup=markup)
    else:
        await message.answer("У вас ещё нет заказов")

async def add_product_to_cart(bot, callback_query):
    product_added = await product_add(callback_query)

    try:
        product_name = product_added["product_name"]
        product_price = product_added["product_price"]
        product_quantity = product_added["product_quantity"]
        product_id = product_added["product_id"]

    except Exception:
        return

    message_text = (
        f"✅ Товар {product_name} {product_quantity}шт. добавлен в корзину!"
    )
    await callback_query.answer(text=message_text)
    await callback_query.message.answer(text=message_text + "\n\nПросмотр: /cart")

    quantity = 1

    current_price = str(product_price * quantity)

    markup = get_quantity_keyboard(quantity, product_price, product_id)

    product_caption_text = product_caption(product_name, current_price)

    await bot.edit_message_caption(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        caption=product_caption_text,
        reply_markup=markup,
        parse_mode="HTML",
    )

async def page_nav(callback_query):
    user_id = callback_query.from_user.id
    orders = await orders_db.get_orders_by_user(user_id)
    BUTTON_SETS = {
        "addresses": ADDRESSES,
        "orders": [f"Заказ #{user_id}{order[0]}" for order in orders],  # Пример заказов
    }

    CALLBACK_SETS = {
        "addresses": [f"address_{address}" for address in ADDRESSES],
        "orders": [f"listorder_{order[0]}" for order in orders],
        "orders": [f"admin_listorder_{order[0]}" for order in orders],
    }
    callback_data_parts = callback_query.data.split("_")
    page = int(callback_data_parts[1])
    buttons_key = callback_data_parts[
        2
    ]  # Уникальный ключ для идентификации набора кнопок
    total_buttons_key = callback_data_parts[3]  # Ключ для получения списка всех кнопок

    buttons = BUTTON_SETS[
        buttons_key
    ]  # Предположим, что BUTTON_SETS содержит все наборы кнопок
    callbacks = CALLBACK_SETS[total_buttons_key]  # Сохраняем все callback'и

    markup = generate_inline_keyboard(
        buttons=buttons,  # Кнопки, которые ты извлекаешь из BUTTON_SETS
        max_buttons=5,  # Количество кнопок на странице
        callback=callbacks,  # Callback для кнопок
        buttons_key=buttons_key,  # Динамически переданный ключ
        total_buttons_key=total_buttons_key,  # Динамически переданный ключ
        page=page,  # Текущая страница
    )

    await callback_query.message.edit_reply_markup(reply_markup=markup)
    await callback_query.answer()
