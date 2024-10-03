from aiogram.fsm.state import StatesGroup, State


class AddProduct(StatesGroup):
    waiting_for_name = State()
    waiting_for_photo = State()
    waiting_for_photo_url = State()
    waiting_for_description = State()
    waiting_for_volume_and_price = State()


class DeleteProduct(StatesGroup):
    waiting_for_id = State()


class CancelOrderReason(StatesGroup):
    waiting_for_text = State()
