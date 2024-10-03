import aiosqlite

DATABASE = "bot.db"


async def create_users_table():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "username TEXT NOT NULL UNIQUE,"
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "order_count INT NULL,"
            "cart INT None,"
            "geo TEXT NULL" 
            ")"
        )
        await db.commit()


async def check_and_add_user(user_id: int, username: str):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute(
            "SELECT id, geo FROM users WHERE id = ?", (user_id,)
        ) as cursor:
            user = await cursor.fetchone()

        if user is None:
            await db.execute(
                "INSERT INTO users (id, username, created_at, order_count, geo) VALUES (?, ?, CURRENT_TIMESTAMP, 0, NULL)",
                (user_id, username),
            )
            await db.commit()

        elif user[1] is None:
            return (
                "no_geo"  
            )

    return "exists" 


async def get_user_by_id(user_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            user = await cursor.fetchone()

    return dict(user) if user else None


async def update_user_geo(user_id: int, geo: str):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "UPDATE users SET geo = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (geo, user_id),
        )
        await db.commit()
