import aiosqlite

DATABASE = "bot.db"


async def create_products_table():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS products ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT,"
            "photo TEXT,"
            "photo_url TEXT,"
            "description TEXT,"
            "price REAL"
            ")"
        )
        await db.commit()


async def add_product(data, price):
    async with aiosqlite.connect(DATABASE) as db:
        try:
            await db.execute(
                "INSERT INTO products (name, photo, photo_url, description, price) VALUES (?, ?, ?, ?, ?)",
                (
                    data["name"],
                    data["photo"],
                    data["photo_url"],
                    data["description"],
                    price,
                ),
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False


async def get_products():
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            "SELECT id, name, photo, photo_url, description, price FROM products"
        )
        rows = await cursor.fetchall()

        # Преобразуем результаты в список словарей
        products = [
            {
                "id": row[0],
                "name": row[1],
                "photo": row[2],
                "photo_url": row[3],
                "description": row[4],
                "price": row[5],
            }
            for row in rows
        ]

        return products


async def get_product_by_id(product_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            "SELECT id, name, photo, photo_url, description, price FROM products WHERE id = ?",
            (product_id,),
        )
        row = await cursor.fetchone()

        if row:
            product = {
                "id": row[0],
                "name": row[1],
                "photo": row[2],
                "photo_url": row[3],
                "description": row[4],
                "price": row[5],
            }
            return product
        else:
            return None


async def delete_product_by_id(product_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        try:
            await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
            await db.commit()
            return True
        except aiosqlite.Error as e:
            return False
