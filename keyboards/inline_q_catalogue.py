from aiogram import types
from db import products_db
from utils.utils import hash_it
from utils.user_utils import product_caption
from keyboards.user_keyboards import get_quantity_keyboard

async def handle_catalogue_inline_query(inline_query: types.InlineQuery):
    # Получение списка продуктов из базы данных
    products = await products_db.get_products() 

    # Создание списка объектов InlineQueryResultArticle для каждого продукта
    result = []
    for product in products:
        hashed_name = await hash_it(
            product["name"]
        )  # Правильно вызываем асинхронную функцию
        result.append(
            types.InlineQueryResultArticle(
                id=str(product["id"]),  # id продукта
                title=product["name"],  # название продукта
                input_message_content=types.InputTextMessageContent(
                    message_text=f"<b>{hashed_name}</b>", parse_mode="HTML"
                ),
                description=f"{product['description']}",  # описание для инлайн-результата
                thumbnail_url=f"{product['photo_url']}",  # ссылка на изображение продукта
                thumbnail_height=100,
                thumbnail_width=100,
            )
        )

    # Отправка ответа на inline-запрос
    await inline_query.bot.answer_inline_query(
        inline_query.id, results=result, cache_time=1
    )

async def show_chosen_result(bot, chosen_result):
    try:
        chat_id = chosen_result.from_user.id
        product_id = chosen_result.result_id
        product = await products_db.get_product_by_id(product_id)
        product_price = product["price"]
        product_name = product["name"]
    except Exception:
        return

    markup = get_quantity_keyboard(1, price=product_price, product_id=product["id"])
    product_caption_text = product_caption(product_name, product_price)
    await bot.send_photo(
        chat_id,
        photo=product["photo"],
        caption=product_caption_text,
        reply_markup=markup,
        parse_mode="HTML",
    )