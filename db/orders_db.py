import aiosqlite
from datetime import datetime

DATABASE = "bot.db"


async def create_orders_table():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            order_total REAL NOT NULL,
            order_type TEXT NOT NULL CHECK (order_type IN ('delivery', 'pick-up')),
            geo TEXT,
            order_state TEXT NOT NULL CHECK (order_state IN ('active', 'accepted', 'finished', 'declined')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        )
        await db.commit()


async def add_order(user_id: int, order_total: float, order_type: str, geo: str = None):
    async with aiosqlite.connect(DATABASE) as db:
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Форматируем дату
        order_state = "active"  # Начальное состояние заказа
        await db.execute(
            """
            INSERT INTO orders (user_id, order_date, order_total, order_type, geo, order_state)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (user_id, order_date, order_total, order_type, geo, order_state),
        )
        await db.commit()


async def admin_get_orders():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute("SELECT * FROM orders") as cursor:
            orders = await cursor.fetchall()
        return orders if orders else []


async def get_order_by_id(order_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(
            "SELECT * FROM orders WHERE id = ?", (order_id,)
        ) as cursor:
            order = await cursor.fetchone()
    return order  # Вернёт заказ или None, если не найден


async def get_active_order(user_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            """
            SELECT * FROM orders
            WHERE user_id = ? AND order_state = 'active'
            ORDER BY id DESC
            LIMIT 1
        """,
            (user_id,),
        )
        active_order = await cursor.fetchone()
    return active_order


async def update_order_state(order_id: int, new_state: str):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            """
            UPDATE orders
            SET order_state = ?
            WHERE id = ?
        """,
            (new_state, order_id),
        )
        await db.commit()


async def get_orders_by_user(user_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(
            "SELECT * FROM orders WHERE user_id = ?", (user_id,)
        ) as cursor:
            orders = await cursor.fetchall()  # Получаем все заказы пользователя
    return orders


async def get_last_order_by_user(user_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(
            """
            SELECT * FROM orders 
            WHERE user_id = ? 
            ORDER BY order_date DESC 
            LIMIT 1
        """,
            (user_id,),
        ) as cursor:
            order = await cursor.fetchone()
    return order


async def accept_order(order_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        # Проверяем, что заказ активен
        async with db.execute(
            """
            SELECT * FROM orders
            WHERE id = ? AND order_state = 'active'
        """,
            (order_id,),
        ) as cursor:
            active_order = await cursor.fetchone()

        if active_order:
            await db.execute(
                """
                UPDATE orders
                SET order_state = 'accepted'
                WHERE id = ?
            """,
                (order_id,),
            )
            await db.commit()
            return True  # Заказ успешно принят
        else:
            return False  # Нет активного заказа


async def finish_order(order_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(
            """
            SELECT * FROM orders
            WHERE id = ? AND order_state = 'accepted'
        """,
            (order_id,),
        ) as cursor:
            active_order = await cursor.fetchone()

        if active_order:
            await db.execute(
                """
                UPDATE orders
                SET order_state = 'finished'
                WHERE id = ?
            """,
                (order_id,),
            )
            await db.commit()
            return True 
        else:
            return False


async def cancel_order(order_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(
            """
            SELECT * FROM orders
            WHERE id = ? AND order_state = 'active'
        """,
            (order_id,),
        ) as cursor:
            active_order = await cursor.fetchone()

        if active_order:
            await db.execute(
                """
                UPDATE orders
                SET order_state = 'declined'
                WHERE id = ?
            """,
                (order_id,),
            )
            await db.commit()
            return True 
        else:
            return False 
