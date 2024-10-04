from db import orders_db
from config import ADMIN_ID
from utils.utils import format_order
from keyboards.admin_keyboards import processing_order_buttons, process_order_buttons

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_ID

async def decline_order(bot, message, order_id, decline_reason="не указано"):
    order_declined = await orders_db.cancel_order(order_id)
    if order_declined:
        order = await orders_db.get_order_by_id(order_id)
        user_id = order[1]
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"<b>Заказ #{user_id}{order_id}</b> отменен",
            parse_mode="HTML",
        )

        await bot.send_message(
            chat_id=user_id,
            text=f"<b>Заказ #{user_id}{order_id}</b> отменен.\n\nПричина: {decline_reason}",
            parse_mode="HTML",
        )
    else:
        await message.answer("Заказ не найден или уже был отменён.")


async def accept_order(bot, callback_query):
    order_id = callback_query.data.split("_")[2]
    order = await orders_db.get_order_by_id(order_id)
    user_id = order[1]
    order_accepted = await orders_db.accept_order(order_id)
    if order_accepted:
        markup = processing_order_buttons(order_id)
        formatted_order = await format_order(order)
        await callback_query.message.edit_text(
            text=formatted_order, reply_markup=markup, parse_mode="HTML"
        )
        await bot.send_message(
            chat_id=user_id,
            text=f"<b>Заказ #{user_id}{order_id}</b> принят",
            parse_mode="HTML",
        )


async def order_finished(bot, callback_query):
    order_id = callback_query.data.split("_")[2]
    order = await orders_db.get_order_by_id(order_id)
    user_id = order[1]
    order_finished = await orders_db.finish_order(order_id)
    if order_finished:
        await callback_query.message.edit_text(
            text=f"<b>Заказ #{user_id}{order_id}</b> успешно завершен!",
            parse_mode="HTML",
        )
        await bot.send_message(
            chat_id=user_id,
            text=f"<b>Заказ #{user_id}{order_id}</b> успешно завершен!",
            parse_mode="HTML",
        )


async def list_order(callback_query):
    order_id = callback_query.data.split("_")[2]
    order = await orders_db.get_order_by_id(order_id)
    order_state = order[-1]
    formatted_order = await format_order(order)
    if order_state in ["declined", "finished"]:
        await callback_query.message.answer(formatted_order, parse_mode="HTML")
    elif order_state == "active":
        markup = process_order_buttons(order_id)
        await callback_query.message.answer(
            formatted_order, reply_markup=markup, parse_mode="HTML"
        )
    elif order_state == "accepted":
        markup = processing_order_buttons(order_id)
        await callback_query.message.answer(
            formatted_order, reply_markup=markup, parse_mode="HTML"
        )
