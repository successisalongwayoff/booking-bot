import aiosqlite

from database.models import DB_NAME

async def add_services(name: str, price:int, duration:int) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO services(name, price, duration) VALUES (?,?,?)",
                         (name,price,duration))
        await db.commit()

async def get_services() -> list[dict]:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id,name,price,duration FROM services") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
async def delete_service(service_id:int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM services WHERE id = ?",
                         (service_id,))
        await db.commit()

async def add_appointment(user_id, user_name, service_id, master_id, date_time):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
INSERT INTO appointments (user_id, user_name, service_id, master_id, date_time, status) VALUES(?,?,?,?, ?, 'pending')""",
(user_id, user_name, service_id, master_id, date_time)
) 
        await db.commit()
        return cursor.lastrowid
async def get_user_appointment(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        sql = """"
        SELECT
        a.id,
        s.name AS service_name,
        s.price,
        a.data_time,
        a.status
        FROM appointment a
        JOIN services s ON a.service_id = s.id
        WHERE a.user_id = ?
        ORDER BY a.id DESC
        """
        async with db.execute(sql,(user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
async def update_appointment_status(appointment_id:int, status:str) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
UPDATE appointments SET status = ? WHERE id = ?""",
(status,appointment_id))
        await db.commit()

async def get_appointments():
    async with aiosqlite.connect("booking.db") as db:
        async with db.execute("""
SELECT appointments.id, appointments.user_name, services.name, appointments.date_time 
FROM appointments
JOIN services ON appointments.service_id = services.id""") as cursor:
            return await cursor.fetchall()

async def update_appointment_status(app_id:int, status:str):
    async with aiosqlite.connect("booking.db") as db:
        await db.execute(
            "UPDATE appointments SET status = ? WHERE id = ?",
            (status, app_id)
        )
        await db.commit()

async def get_appointments_by_id(app_id:int):
    async with aiosqlite.connect("booking.db") as db:
        async with db.execute("""
SELECT appointments.id, appointments.user_id, appointments.user_name, services.name, appointments.date_time, appointments.status
FROM appointments
JOIN services ON appointments.service_id = services.id
WHERE appointments.id = ?""",
(app_id,)) as cursor:
            return await cursor.fetchone()

async def get_user_appointment(user_id:int):
    async with aiosqlite.connect("booking.db") as db:
        async with db.execute("""
SELECT appointments.id, services.name, appointments.date_time, appointments.status
FROM appointments
JOIN services ON appointments.service_id = services.id
WHERE appointments.user_id = ?
ORDER BY appointments.id DESC""",
(user_id,)
        
        ) as cursor:
            return await cursor.fetchall()
async def delete_service(service_id:int):
    async with aiosqlite.connect("booking.db") as db:
        await db.execute("""DELETE FROM services WHERE id = ?""",
                              (service_id,))
        await db.commit()
async def delete_appointment(app_id:int):
    async with aiosqlite.connect("booking.db") as db:
        await db.execute("DELETE FROM appointments WHERE id = ?", (app_id,))
        await db.commit()
async def get_service_name_by_id(service_id:int):
    async with aiosqlite.connect("booking.db") as db:
        async with db.execute("""SELECT name FROM services WHERE id = ?""",
                         (int(service_id),)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else f"Услуга #{service_id}"
async def get_booked_time_slots(master_id:int) -> list[str]:
    async with aiosqlite.connect("booking.db") as db:
        async with db.execute(
            """
            SELECT date_time FROM appointments
            WHERE master_id = ? AND status IN('pending', 'confirmed')
            """,
            (int(master_id),)
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
async def get_upcoming_appointments():
    async with aiosqlite.connect("booking.db") as db:
        async with db.execute("""SELECT appointments.id, appointments.user_id, services.name, appointments.date_time
        FROM appointments
        JOIN services ON appointments.service_id = services.id
        WHERE appointments.status ='confirmed'""") as cursor:
            return await cursor.fetchall()