import html
import base64


def escape_html(text: str) -> str:
    """
    Escapes special characters for Telegram's MarkdownV2.
    """
    return html.escape(text)


async def data_splitter(data):
    """
    Splits dynamicly generated CallbackData
    """
    parts = data.split("_")
    if len(parts) < 3:
        return
    return parts


async def hash_it(data):
    """
    Hash func
    """
    return base64.b16encode(data.encode("utf-8")).decode("utf-8")[2:-1]


async def format_order(order):
    """
    Форматирует данные о заказах для удобного отображения.

    :param order: Список заказов, полученных из базы данных
    :return: Отформатированная строка с информацией о заказах
    """
    if not order:
        return

    order_id, user_id, order_date, order_total, order_type, geo, order_state = order

    # Определяем текст для каждого состояния заказа
    state_mapping = {
        "active": "🟢 Создан",
        "accepted": "🟢 Принят",
        "finished": "✅ Завершен",
        "declined": "🔴 Отменен",
    }

    # Получаем текст для состояния заказа
    state_text = state_mapping.get(order_state, "Неизвестно")

    formatted_order = (
        f"<a href='tg://user?id={user_id}'><b>Заказ #{user_id}{order_id}</b></a>\n"
        f"{state_text}\n\n"
        f"{order_date}\n"
        f"Сумма: <code>{order_total}₽</code>\n"
    )

    # Если доставка, добавляем адрес
    if order_type == "delivery":
        formatted_order += f"\nАдрес доставки: {geo}\n"
    elif order_type == "pick-up":
        formatted_order += f"\nПункт выдачи: {geo}\n"

    return formatted_order
