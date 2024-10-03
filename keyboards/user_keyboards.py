from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder


def main_menu_keyboard() -> types.ReplyKeyboardMarkup:
    main_menu_buttons = [
        [
            types.KeyboardButton(text="⚡️ Каталог"),
            types.KeyboardButton(text="🛒 Корзина"),
        ],
        [types.KeyboardButton(text="ℹ️ Как сделать заказ?")],
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=main_menu_buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню",
    )


async def go_to_catalogue() -> types.InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder()
    button = InlineKeyboardButton(
        text="ОТКРЫТЬ КАТАЛОГ", switch_inline_query_current_chat="catalogue"
    )
    markup.add(button)
    return markup.as_markup()


def get_quantity_keyboard(
    quantity: int,
    price: float,
    product_id: int = None,
) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{quantity} в корзину 🛒",
                    callback_data=f"cart_{product_id}_{quantity}",
                ),
                InlineKeyboardButton(
                    text="📁", switch_inline_query_current_chat="catalogue"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="➖",
                    callback_data=f"quantity_decrease_{product_id}_{quantity}_{price}",
                ),
                InlineKeyboardButton(text=f"{quantity} шт.", callback_data="_"),
                InlineKeyboardButton(
                    text="➕",
                    callback_data=f"quantity_increase_{product_id}_{quantity}_{price}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"Сделать заказ",
                    callback_data=f"order_{product_id}_{quantity}",
                )
            ],
        ]
    )
    return markup


def user_cart_buttons(current_price: float = 0.00):
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"К оплате ({current_price:.2f}₽) 💳", callback_data=f"payment"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Очистить корзину", callback_data=f"delete_cart"
                )
            ],
        ]
    )
    return markup


def delivery_method_buttons():
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"🚚 Доставка", callback_data=f"delivery"),
                InlineKeyboardButton(text=f"🏠 Самовывоз", callback_data=f"pick_up"),
            ],
            [InlineKeyboardButton(text=f"Отмена", callback_data=f"cancel_button")],
        ]
    )
    return markup


def add_geo_buttons():
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📍 Отправить геопозицию", callback_data="send_geo"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✍️ Ввести адрес вручную", callback_data="enter_address"
                )
            ],
            [InlineKeyboardButton(text=f"Отмена", callback_data=f"cancel_button")],
        ]
    )
    return markup


def create_order_buttons():
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💎 Оплатить (CryptoBot)", callback_data="cryptobot_payment"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✍️ Изменить адрес доставки", callback_data="enter_address"
                )
            ],
            [InlineKeyboardButton(text=f"Отмена", callback_data=f"cancel_button")],
        ]
    )
    return markup


def decline_order_button(order_id: int):
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Отменить заказ",
                    callback_data=f"user_decline_order_{order_id}",
                )
            ]
        ]
    )
    return markup


def generate_inline_keyboard(
    buttons: list[str],
    max_buttons: int,
    callback: list[str],
    buttons_key: str,
    total_buttons_key: str,
    page: int = 1,
) -> types.InlineKeyboardMarkup:
    # Рассчитываем количество страниц
    MAX_BUTTONS_PER_PAGE = max_buttons
    total_pages = (len(buttons) + MAX_BUTTONS_PER_PAGE - 1) // MAX_BUTTONS_PER_PAGE

    buttons = buttons[::-1]  #'переворачиваем кнопки чтобы последний заказ был наверху'
    callback = callback[::-1]

    # Вычисляем индексы кнопок для текущей страницы
    start_index = (page - 1) * MAX_BUTTONS_PER_PAGE
    end_index = start_index + MAX_BUTTONS_PER_PAGE
    current_buttons = buttons[start_index:end_index]
    current_callbacks = callback[start_index:end_index]

    # Создаем основную клавиатуру с текущими кнопками и кастомными callback_data
    inline_keyboard = [
        [InlineKeyboardButton(text=button_text, callback_data=callback_data)]
        for button_text, callback_data in zip(current_buttons, current_callbacks)
    ]

    # Добавляем навигационные кнопки
    if total_pages > 1:
        navigation_buttons = [
            InlineKeyboardButton(
                text="<",
                callback_data=(
                    f"page_{page-1}_{buttons_key}_{total_buttons_key}"
                    if page > 1
                    else f"page_1_{buttons_key}_{total_buttons_key}"
                ),
            ),
            InlineKeyboardButton(
                text=f"{page}/{total_pages}", callback_data="current_page"
            ),
            InlineKeyboardButton(
                text=">",
                callback_data=(
                    f"page_{page+1}_{buttons_key}_{total_buttons_key}"
                    if page < total_pages
                    else f"page_{total_pages}_{buttons_key}_{total_buttons_key}"
                ),
            ),
        ]
        inline_keyboard.append(navigation_buttons)

    # Добавляем кнопку отмены
    inline_keyboard.append(
        [InlineKeyboardButton(text="Отмена", callback_data=f"cancel_button")]
    )

    markup = types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return markup
