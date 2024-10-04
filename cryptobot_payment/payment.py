from aiogram import types
from cryptobot_payment.cryptobot_api import CryptoPayAPI
from config import API_CRYPTO_TOKEN, ADMIN_ID

from db import cart_db
from utils.user_utils import new_order
from utils.utils import format_order
from keyboards.user_keyboards import decline_order_button
from keyboards.admin_keyboards import process_order_buttons

crypto_api = CryptoPayAPI(api_token=API_CRYPTO_TOKEN)


async def process_payment(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    cart = await cart_db.get_cart(user_id)
    total_price = sum(item["total_price"] for item in cart)
    try:

        invoice = crypto_api.create_invoice(
            asset="TON",
            amount=total_price,
            allow_comments=True,
            allow_anonymous=False,
            expires_in=600,  # Счет истекает через 10 минут
        )

        pay_url = invoice["result"]["bot_invoice_url"]
        invoice_id = invoice["result"]["invoice_id"]

        markup = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Оплата", url=pay_url)],
                [
                    types.InlineKeyboardButton(
                        text="♻️ Проверить статус платежа ♻️",
                        callback_data=f"check_payment:{invoice_id}",
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="Отмена", callback_data=f"cancel_button"
                    )
                ],
            ]
        )

        await callback_query.message.edit_text(
            text=f"<b>#{invoice['result']['hash'][:2]}{ invoice['result']['invoice_id']}</b>\n\n<b>You are sending:</b> {invoice['result']['amount']} {invoice['result']['asset']} (${invoice['result']['amount']})",
            reply_markup=markup,
            parse_mode="HTML",
        )

    except Exception as e:
        await callback_query.message.answer(f"Error: {e}")


async def check_payment(bot, callback_query: types.CallbackQuery):
    invoice_id = callback_query.data.split(":")[1]

    invoices = crypto_api.get_invoices(invoice_ids=[invoice_id])
    invoice_status = invoices["result"]["items"][0]["status"]

    if invoice_status == "paid":
        user_id = callback_query.from_user.id
        order = await new_order(user_id, delivery_method="delivery")
        if order:
            order_id = order[0]
            formatted_order = await format_order(order)
            markup = decline_order_button(order_id)
            admin_markup = process_order_buttons(order_id)
            await callback_query.message.answer(
                formatted_order+'\nВаши заказы: /orders', reply_markup=markup, parse_mode="HTML"
            )
            for admin_id in ADMIN_ID:
                await bot.send_message(
                    chat_id=admin_id,
                    text="У вас новый заказ\n\n" + formatted_order,
                    reply_markup=admin_markup,
                    parse_mode="HTML",
                )
        else:
            await callback_query.message.answer("У вас уже есть активный заказ.")
        return True
