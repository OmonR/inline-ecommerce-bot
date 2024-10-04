from config import MIN_ORDER_PRICE, ADDRESSES, ADMIN_ID, SUPPORT_USERNAME
from aiogram import types, Dispatcher, Bot, F
from aiogram.filters import Command
from keyboards.user_keyboards import (
    main_menu_keyboard,
    go_to_catalogue,
    get_quantity_keyboard,
    user_cart_buttons,
    delivery_method_buttons,
    add_geo_buttons,
    create_order_buttons,
    generate_inline_keyboard,
    decline_order_button,
)
from keyboards.inline_q_catalogue import handle_catalogue_inline_query, show_chosen_result
from utils.user_utils import (
    format_cart,
    get_user_cart,
    product_add,
    product_caption,
    get_cart_message,
    new_order,
    page_nav,
    get_orders,
    add_product_to_cart,
)
from db import products_db, cart_db, users_db, orders_db
from utils.utils import data_splitter, format_order
from states.user_states import AddressForm
from aiogram.fsm.context import FSMContext
from cryptobot_payment.payment import process_payment, check_payment

#Хэндлер для пользователя
def register_user_handlers(dp: Dispatcher, bot: Bot):
    @dp.message(Command("start"))
    async def start_command(message: types.Message):
        markup = main_menu_keyboard()
        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        # if user_id != admin_id for admin_id in ADMIN_ID:
        await users_db.check_and_add_user(user_id, username)
        await message.answer(text="Главное меню:", reply_markup=markup)

    @dp.message(Command("orders"))
    async def cmd_get_orders(message: types.Message):
        await get_orders(message)

    @dp.message(Command("cart"))
    async def cmd_get_cart(message: types.Message):
        await get_user_cart(message)

    @dp.message(lambda message: message.text == "🛒 Корзина")
    async def msg_get_cart(message: types.Message):
        await get_user_cart(message)

    @dp.message(lambda message: message.text == "⚡️ Каталог")
    async def main_menu(message: types.Message):
        markup = await go_to_catalogue()
        await message.answer(text=f"Прямые продажи и поддержка: {SUPPORT_USERNAME}", reply_markup=markup)

    @dp.inline_query(F.query == "catalogue")
    async def catalogue(inline_query: types.InlineQuery):
        await handle_catalogue_inline_query(inline_query)

    @dp.chosen_inline_result()
    async def user_chosen_inline_result(chosen_result: types.ChosenInlineResult):
        await show_chosen_result(bot, chosen_result)

    @dp.callback_query(lambda c: c.data == "cancel_button")
    async def cancel_the_action(callback_query: types.CallbackQuery):
        markup = await go_to_catalogue()
        await callback_query.answer("Действие отменено")
        await bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
        )
        await callback_query.message.answer(
            text=f"Прямые продажи и поддержка: ", reply_markup=markup
        )

    @dp.callback_query(lambda c: c.data.startswith("cart"))
    async def user_add_product_to_cart(callback_query: types.CallbackQuery):
        await add_product_to_cart(bot, callback_query)

    @dp.callback_query(lambda c: c.data.startswith("quantity_"))
    async def handle_quantity_change(callback_query: types.CallbackQuery):
        data = await data_splitter(callback_query.data)

        try:
            product_id = int(data[-3])
            quantity = int(data[-2])
            price = float(data[-1])
        except ValueError:
            return

        if callback_query.data.startswith("quantity_increase"):
            quantity += 1
        elif callback_query.data.startswith("quantity_decrease") and quantity > 1:
            quantity -= 1
        else:
            return

        current_price = str(price * quantity)

        product = await products_db.get_product_by_id(product_id)

        product_name = product["name"]

        new_markup = get_quantity_keyboard(quantity, price, product_id)

        product_caption_text = product_caption(product_name, current_price)

        await bot.edit_message_caption(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            caption=product_caption_text,
            reply_markup=new_markup,
            parse_mode="HTML",
        )

        await callback_query.answer(text=f"⚡️ {quantity} шт")

    @dp.callback_query(lambda c: c.data == "delete_cart")
    async def user_delete_cart(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        deleted_cart = await cart_db.delete_cart(user_id)

        new_message_text = await format_cart(user_id)

        markup = user_cart_buttons()

        if deleted_cart:
            try:
                await bot.edit_message_text(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    text=new_message_text,
                    reply_markup=markup,
                    parse_mode="HTML",
                )
            except Exception:
                await callback_query.answer()
        else:
            await callback_query.answer()

    @dp.callback_query(lambda c: c.data.startswith("order"))
    async def order_menu(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        await product_add(callback_query)
        markup = delivery_method_buttons()
        message_text = await get_cart_message(user_id)
        await bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
        )
        await callback_query.message.answer(
            text="<b>Ваш заказ</b>\n\n"
            + message_text
            + "\n\n<i>Отправить товар доставкой /\nПриготовить для самовывоза</i>",
            reply_markup=markup,
            parse_mode="HTML",
        )

    @dp.callback_query(lambda c: c.data.startswith("listorder"))
    async def user_list_order(callback_query: types.CallbackQuery):
        order_id = int(callback_query.data.split("_")[1])

        order = await orders_db.get_order_by_id(order_id)

        if order:
            formatted_order = await format_order(order)
            order_state = order[6]  # 6 — индекс для order_state

            if order_state == "active":
                markup = decline_order_button(order_id)
                await callback_query.message.answer(
                    formatted_order, reply_markup=markup, parse_mode="HTML"
                )
            else:
                await callback_query.message.answer(formatted_order, parse_mode="HTML")

    @dp.callback_query(lambda c: c.data.startswith("payment"))
    async def payment_start(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        markup = delivery_method_buttons()
        message_text = await get_cart_message(user_id)

        try:
            await bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                text="<b>Ваш заказ</b>\n\n"
                + message_text
                + "\n\n<i>Отправить товар доставкой /\nПриготовить для самовывоза</i>",
                reply_markup=markup,
                parse_mode="HTML",
            )

        except Exception:
            callback_query.answer()
            return

    @dp.callback_query(lambda c: c.data == "cryptobot_payment")
    async def payment(callback_query: types.CallbackQuery):
        await process_payment(callback_query)

    @dp.callback_query(lambda c: c.data == "delivery")
    async def delivery_method(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        user_cart = await cart_db.get_cart(user_id)
        total_price = sum(item["total_price"] for item in user_cart)
        if total_price >= float(MIN_ORDER_PRICE):
            message_text = await get_cart_message(user_id)
            user_status = await users_db.check_and_add_user(
                callback_query.from_user.id, callback_query.from_user.username
            )

            if user_status == "no_geo":
                markup = add_geo_buttons()
                await bot.edit_message_text(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    text="<b>Ваш заказ</b>\n\n"
                    + message_text
                    + "\n\n<i>Ввести адрес доставки</i>",
                    reply_markup=markup,
                    parse_mode="HTML",
                )
            else:
                message_text = await get_cart_message(user_id)
                markup = create_order_buttons()
                user = await users_db.get_user_by_id(user_id)
                await bot.edit_message_text(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.message_id,
                    text="<b>Ваш заказ</b>\n\n"
                    + message_text
                    + f"\n\n<i>Адрес доставки: {str(user['geo'])}</i>",
                    reply_markup=markup,
                    parse_mode="HTML",
                )
        else:
            await callback_query.answer(
                f"Сумма заказа от {MIN_ORDER_PRICE} руб.", show_alert=True
            )

    @dp.callback_query(lambda c: c.data == "pick_up")
    async def pick_up_method(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        message_text = await get_cart_message(user_id)
        buttons = ADDRESSES 
        callbacks = [f"address_{i}" for i in range(len(buttons))]

        markup = generate_inline_keyboard(
            buttons=buttons,
            max_buttons=5,
            callback=callbacks,
            buttons_key="addresses",
            total_buttons_key="addresses",
        )

        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=f"<b>Ваш заказ</b>\n\n{message_text}\n\n<i>Выберите пункт выдачи</i>",
            reply_markup=markup,
            parse_mode="HTML",
        )

    @dp.callback_query(lambda c: c.data == "send_geo")
    async def request_geo(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "Пожалуйста, отправьте вашу геопозицию",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[
                    [
                        types.KeyboardButton(
                            text="📍 Отправить геопозицию", request_location=True
                        )
                    ]
                ],
                resize_keyboard=True,
            ),
        )

    @dp.callback_query(F.data == "enter_address")
    async def user_enter_address(
        callback_query: types.CallbackQuery, state: FSMContext
    ):
        await callback_query.message.answer(
            "Ввести адрес доставки:\n\n<i>Москва, Казакова 3А</i>", parse_mode="HTML"
        )
        await state.set_state(AddressForm.waiting_for_adress)

    @dp.message(AddressForm.waiting_for_adress)
    async def user_save_address(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        address = message.text

        await users_db.update_user_geo(user_id, address)
        await message.answer(f"Ваш адрес сохранён: {address}")
        message_text = await get_cart_message(user_id)
        markup = create_order_buttons()
        user = await users_db.get_user_by_id(user_id)
        await bot.send_message(
            chat_id=message.chat.id,
            text="<b>Ваш заказ</b>\n\n"
            + message_text
            + f"\n\n<i>Адрес доставки: {str(user['geo'])}</i>",
            reply_markup=markup,
            parse_mode="HTML",
        )
        await state.clear()

    @dp.callback_query(lambda c: c.data.startswith("check_payment"))
    async def user_check_payment(callback_query: types.CallbackQuery):
        await check_payment(bot, callback_query)

    @dp.callback_query(lambda c: c.data and c.data.startswith("page"))
    async def process_page_navigation(callback_query: types.CallbackQuery):
        await page_nav(callback_query)

    @dp.callback_query(lambda c: c.data and c.data.startswith("address"))
    async def process_page_navigation(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        adress = str(callback_query.data.split("_")[1])
        order = await new_order(user_id, delivery_method="pick-up", adress=adress)
        if order:
            order_id = order[0]
            markup = decline_order_button(order_id)
            formatted_order = await format_order(order)
            await callback_query.message.answer(
                formatted_order+'\nВаши заказы: /orders', reply_markup=markup, parse_mode="HTML"
            )
        else:
            await callback_query.answer("Предыдущий заказ ещё в обработке")

    @dp.callback_query(lambda c: c.data.startswith("user_decline_order"))
    async def handle_decline_order(callback_query: types.CallbackQuery):
        order_id = int(callback_query.data.split("_")[-1])

        order_cancelled = await orders_db.cancel_order(order_id)

        if order_cancelled:
            updated_order = await orders_db.get_order_by_id(order_id)

            user_id = updated_order[1]

            updated_order_text = await format_order(updated_order)

            await callback_query.message.edit_text(
                updated_order_text, parse_mode="HTML"
            )

            for admin_id in ADMIN_ID:
                await bot.send_message(
                    chat_id=admin_id,
                    text=f"<b>Пользователь отменил заказ #{user_id}{order_id}</b>",
                    parse_mode="HTML",
                )
        else:
            await callback_query.answer(
                "Заказ не найден или уже был отменён.", show_alert=True
            )
