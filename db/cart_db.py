import asyncio
import aiosqlite

DATABASE = "bot.db"


async def create_cart_table():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS carts ("
            "user_id INTEGER,"
            "product_id INTEGER,"
            "quantity INTEGER,"
            "last_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,"
            "PRIMARY KEY (user_id, product_id)"
            ")"
        )
        await db.commit()


async def delete_cart(user_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute("DELETE FROM carts WHERE user_id = ?", (user_id,))
        await db.commit()
        return True


async def get_cart(user_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            "SELECT carts.product_id, products.name, products.price, carts.quantity "
            "FROM carts "
            "JOIN products ON carts.product_id = products.id "
            "WHERE carts.user_id = ?",
            (user_id,),
        )
        cart_items = await cursor.fetchall()

        cart = [
            {
                "product_id": item[0],
                "name": item[1],
                "price": item[2],
                "quantity": item[3],
                "total_price": item[2] * item[3],
            }
            for item in cart_items
        ]

        return cart


async def add_product_to_cart(user_id: int, product_id: int, quantity: int = 1):
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            "SELECT quantity FROM carts WHERE user_id = ? AND product_id = ?",
            (user_id, product_id),
        )
        result = await cursor.fetchone()

        if result:
            new_quantity = result[0] + quantity
            await db.execute(
                "UPDATE carts SET quantity = ?, last_updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND product_id = ?",
                (new_quantity, user_id, product_id),
            )
        else:
            await db.execute(
                "INSERT INTO carts (user_id, product_id, quantity, last_updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                (user_id, product_id, quantity),
            )
        await db.commit()

    # Планируем удаление всей корзины через 24 часа после последнего изменения
    asyncio.create_task(schedule_cart_deletion(user_id))


async def schedule_cart_deletion(user_id: int):
    await asyncio.sleep(24 * 60 * 60)  # Ждём 24 часа

    async with aiosqlite.connect(DATABASE) as db:
        # Проверяем, не пустая ли корзина
        cursor = await db.execute(
            "SELECT COUNT(*) FROM carts WHERE user_id = ?", (user_id,)
        )
        cart_count = await cursor.fetchone()

        if cart_count[0] > 0:
            # Если корзина не пуста, удаляем её
            await delete_cart(user_id)
