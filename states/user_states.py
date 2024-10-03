from aiogram.fsm.state import StatesGroup, State


class AddressForm(StatesGroup):
    waiting_for_adress = State()
