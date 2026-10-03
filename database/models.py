import aiosqlite

DB_NAME = "booking.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        await db.execute("PRAGMA journal_mode = WAL;")

        await db.execute("""
CREATE TABLE IF NOT EXISTS services(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
price INTEGER NOT NULL,
duration INTEGER NOT NULL)""")
        await db.execute("""
CREATE TABLE IF NOT EXISTS appointments(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
user_name TEXT NOT NULL,
service_id INTEGER NOT NULL,
master_id INTEGER NOT NULL,
date_time TEXT NOT NULL,
status TEXT DEFAULT 'pending',
FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE)""")
        await db.commit()
        try:
            await db.execute("ALTER TABLE appointments ADD COLUMN master_id INTEGER")
        except:
            pass

        await db.commit()