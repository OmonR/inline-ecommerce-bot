import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN
from handlers import user, admin
from db import orders_db, users_db, products_db, cart_db

logging.basicConfig(level=logging.DEBUG)  #

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


def reg_handlers():
    admin.register_admin_handler(dp, bot)
    user.register_user_handlers(dp, bot)


async def activate_database():
    await orders_db.create_orders_table()
    await users_db.create_users_table()
    await products_db.create_products_table()
    await cart_db.create_cart_table()


reg_handlers()


async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await activate_database()
        await dp.start_polling(bot)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
