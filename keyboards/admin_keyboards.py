from aiogram import types


async def admin_buttons() -> types.InlineKeyboardMarkup:

    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Заказы", callback_data="admin_list_orders"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="Добавить товар", callback_data="add_product"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="Удалить товар", callback_data="delete_product"
                )
            ],
            # [types.InlineKeyboardButton(text="Рассылка пользователям", callback_data="")],
        ]
    )
    return markup


async def cancel_states_button() -> types.InlineKeyboardMarkup:

    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="❌ Отмена", callback_data="cancel_states"
                )
            ]
        ]
    )
    return markup


async def delete_product_buttons() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Да, удалить", callback_data="proceed_deleting"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="❌ Отмена", callback_data="cancel_states"
                )
            ],
        ]
    )
    return markup


def process_order_buttons(order_id) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Принять", callback_data=f"accept_order_{order_id}"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="Отменить заказ", callback_data=f"admin_decline_{order_id}"
                )
            ],
        ]
    )
    return markup


def processing_order_buttons(order_id) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Заказ выполнен", callback_data=f"order_finished_{order_id}"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="Отменить заказ", callback_data=f"admin_decline_{order_id}"
                )
            ],
        ]
    )
    return markup
