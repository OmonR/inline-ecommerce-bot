from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from config import ADMIN_ID
from aiogram import types, Dispatcher, Bot, F
from db import products_db, orders_db
from keyboards.admin_keyboards import (
    admin_buttons,
    cancel_states_button,
    delete_product_buttons,
)
from states.admin_states import AddProduct, DeleteProduct, CancelOrderReason
from utils.utils import escape_html
from keyboards.user_keyboards import generate_inline_keyboard
from utils.admin_utils import decline_order, accept_order, list_order, order_finished


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_ID


# Хэндлер для админ-панели
def register_admin_handler(dp: Dispatcher, bot: Bot):

    @dp.message(Command("admin"))
    async def admin_command(message: types.Message):
        if is_admin(message.from_user.id):
            markup = await admin_buttons()
            await message.answer("Добро пожаловать!", reply_markup=markup)

    @dp.callback_query(lambda c: c.data == "cancel_states")
    async def admin_cancel_states(
        callback_query: types.CallbackQuery, state: FSMContext
    ):
        await state.clear()  
        await callback_query.message.edit_text("Действие отменено.")
        await callback_query.answer()

    @dp.callback_query(lambda c: c.data == "admin_list_orders")
    async def admin_list_orders(callback_query: types.CallbackQuery):
        orders = await orders_db.admin_get_orders()
        buttons = [
            f"Заказ #{order[1]}{order[0]}" for order in orders
        ]  # order[0] - это order_id
        callback_data = [
            f"admin_listorder_{order[0]}" for order in orders
        ] 
        markup = generate_inline_keyboard(
            buttons,
            max_buttons=5,
            callback=callback_data,
            page=1,
            buttons_key="orders",
            total_buttons_key="orders",
        )

        await bot.edit_message_text(
            "Заказы:",
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=markup,
        )

    @dp.callback_query(lambda c: c.data == "add_product")
    async def admin_add_product(callback_query: types.CallbackQuery, state: FSMContext):
        markup = await cancel_states_button()
        await callback_query.message.answer(
            "Введите название товара:", reply_markup=markup
        )
        await state.set_state(AddProduct.waiting_for_name)

    @dp.message(AddProduct.waiting_for_name, F.text)
    async def name_sent(message: types.Message, state: FSMContext):
        markup = await cancel_states_button()
        await state.update_data(name=message.text)
        await message.answer("Отправьте фотокарточку товара:", reply_markup=markup)
        await state.set_state(AddProduct.waiting_for_photo)

    @dp.message(AddProduct.waiting_for_photo, F.photo[-1].as_("photo"))
    async def photo_sent(
        message: types.Message, photo: types.PhotoSize, state: FSMContext
    ):
        markup = await cancel_states_button()
        await state.update_data(photo=photo.file_id)
        await message.answer(
            "Теперь введите URL для фотографии товара:", reply_markup=markup
        )
        await state.set_state(AddProduct.waiting_for_photo_url)

    @dp.message(AddProduct.waiting_for_photo_url, F.text)
    async def photo_url_sent(message: types.Message, state: FSMContext):
        markup = await cancel_states_button()
        await state.update_data(photo_url=message.text)
        await message.answer("Теперь введите описание товара:", reply_markup=markup)
        await state.set_state(AddProduct.waiting_for_description)

    @dp.message(AddProduct.waiting_for_description, F.text)
    async def description_sent(message: types.Message, state: FSMContext):
        markup = await cancel_states_button()
        await state.update_data(description=message.text)
        await message.answer(
            f"Теперь введите цену\n(например 99):", reply_markup=markup
        )
        await state.set_state(AddProduct.waiting_for_volume_and_price)

    @dp.message(AddProduct.waiting_for_volume_and_price, F.text)
    async def product_price_entered(message: types.Message, state: FSMContext):
        data = await state.get_data()
        price = message.text
        product = await products_db.add_product(data, price)
        if product:
            await message.answer(
                f"<b>Товар успешно добавлен!</b>\n\n"
                + f"{escape_html(data['name'])}\n"
                + f"{escape_html(data['description'])}\n"
                + f"{escape_html("Цена: "+price)}",
                parse_mode="HTML",
            )
        else:
            await message.answer("Произошла ошибка при добавлении товара.")

        await state.clear()

    @dp.callback_query(lambda c: c.data == "delete_product")
    async def admin_delete_product(
        callback_query: types.CallbackQuery, state: FSMContext
    ):
        markup = await cancel_states_button()
        await callback_query.message.answer(
            "Введите ID товара, который хотите удалить", reply_markup=markup
        )
        await state.set_state(DeleteProduct.waiting_for_id)

    @dp.message(DeleteProduct.waiting_for_id, F.text)
    async def id_sent(message: types.Message, state: FSMContext):
        user_input = message.text
        if user_input.isdigit():
            product_id = int(user_input)  # Преобразуем в целое число для запроса в БД
            product = await products_db.get_product_by_id(product_id)

            if product:
                await state.update_data(
                    product_id=product_id
                )  # Устанавливаем product_id в состояние
                markup = await delete_product_buttons()
                await message.answer(
                    f"Вы хотите удалить <b>{product['name']}</b>?",
                    parse_mode="HTML",
                    reply_markup=markup,
                )
                await state.set_state(
                    DeleteProduct.waiting_for_confirmation
                )  # Устанавливаем новое состояние для подтверждения удаления
            else:
                await message.answer(
                    "Товара с указанным ID не существует. Пожалуйста, попробуйте снова."
                )
                markup = await cancel_states_button()
                await message.answer(
                    "Введите ID товара, который хотите удалить", reply_markup=markup
                )
                await state.set_state(DeleteProduct.waiting_for_id)
        else:
            await message.answer(
                "ID должен быть числом, например <b>12</b>", parse_mode="HTML"
            )

    @dp.callback_query(lambda c: c.data == "proceed_deleting")
    async def admin_proceed_deleting(
        callback_query: types.CallbackQuery, state: FSMContext
    ):
        data = await state.get_data() 
        product_id = data.get("product_id")  
        if product_id:
            await products_db.delete_product_by_id(product_id)  
            await callback_query.message.edit_text("Товар удален.")
            await state.clear()
        else:
            await callback_query.message.answer()

    @dp.callback_query(lambda c: c.data.startswith("admin_decline"))
    async def admin_decline_order(
        callback_query: types.CallbackQuery, state: FSMContext
    ):
        order_id = callback_query.data.split("_")[2]
        await state.update_data(order_id=order_id)
        markup = await cancel_states_button()
        await callback_query.message.answer(
            "Укажите причину отмены заказа:", reply_markup=markup
        )
        await state.set_state(CancelOrderReason.waiting_for_text)

    @dp.message(CancelOrderReason.waiting_for_text)
    async def process_declining(message: types.Message, state: FSMContext):
        await state.update_data(decline_reason=message.text)
        data = await state.get_data()
        order_id = data.get("order_id")
        decline_reason = data.get("decline_reason")
        await decline_order(bot, message, order_id, decline_reason)
        await state.clear()

    @dp.callback_query(lambda c: c.data.startswith("admin_listorder"))
    async def admin_list_order(callback_query: types.CallbackQuery):
        await list_order(callback_query)

    @dp.callback_query(lambda c: c.data.startswith("accept_order"))
    async def admin_accept_order(callback_query: types.CallbackQuery):
        await accept_order(bot, callback_query)

    @dp.callback_query(lambda c: c.data.startswith("order_finished"))
    async def admin_finish_order(callback_query: types.CallbackQuery):
        await order_finished(bot, callback_query)
