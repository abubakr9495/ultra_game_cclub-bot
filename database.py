import aiosqlite
import os

DB_PATH = "gameclub.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT,
                phone TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referrer_id INTEGER DEFAULT NULL,
ref_count INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS play_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bonuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
               user_id INTEGER UNIQUE NOT NULL,
                amount INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
               full_name TEXT,
phone TEXT,
room TEXT,
date_time TEXT,
status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                full_name TEXT,
                phone TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id)
            )
        """)
        await db.commit()

# ─── USERS ────────────────────────────────────────────────
async def get_user(telegram_id: int):
    print("SEARCH USER:", telegram_id)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute(
            "SELECT * FROM users WHERE telegram_id=?",
            (telegram_id,)
        ) as cur:

            user = await cur.fetchone()
            print("FOUND:", user)

            return user
            
async def create_user(telegram_id: int, full_name: str, phone: str, referrer_id=None):
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, full_name, phone, referrer_id) VALUES (?,?,?,?)",
            (telegram_id, full_name, phone, referrer_id)
        )

        await db.execute(
            "INSERT OR IGNORE INTO bonuses (user_id, amount) VALUES (?,0)",
            (telegram_id,)
        )

        if referrer_id and referrer_id != telegram_id:
            await db.execute(
                "UPDATE bonuses SET amount = amount + 1000 WHERE user_id = ?",
                (referrer_id,)
            )

        await db.commit()
        
       async def get_referral_count(user_id: int):
async with aiosqlite.connect(DB_PATH) as db:
    async with db.execute(
            "SELECT COUNT(*) FROM users WHERE referrer_id=?",
            (user_id,)
        ) as cur:
            result = await cur.fetchone()
            return result[0]
            
async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY registered_at DESC") as cur:
            return await cur.fetchall()

# ─── PLAY REQUESTS ────────────────────────────────────────
async def add_play_request(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO play_requests (user_id) VALUES (?)", (user_id,)
        )
        await db.commit()
        return cur.lastrowid

async def get_play_count(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM play_requests WHERE user_id=? AND status='approved'", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0

async def get_pending_plays():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT pr.id, pr.user_id, pr.created_at, u.full_name, u.phone
            FROM play_requests pr
            JOIN users u ON u.telegram_id = pr.user_id
            WHERE pr.status='pending'
            ORDER BY pr.created_at ASC
        """) as cur:
            return await cur.fetchall()

async def update_play_status(req_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE play_requests SET status=? WHERE id=?", (status, req_id)
        )
        await db.commit()

async def get_play_request(req_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM play_requests WHERE id=?", (req_id,)) as cur:
            return await cur.fetchone()

# ─── BONUSES ──────────────────────────────────────────────
async def get_bonus(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT amount FROM bonuses WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0

async def add_bonus(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO bonuses (user_id, amount) VALUES (?,?) ON CONFLICT(user_id) DO UPDATE SET amount=amount+?",
            (user_id, amount, amount)
        )
        await db.commit()

async def set_bonus(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO bonuses (user_id, amount) VALUES (?,?) ON CONFLICT(user_id) DO UPDATE SET amount=?",
            (user_id, amount, amount)
        )
        await db.commit()

async def get_all_bonuses():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT u.telegram_id, u.full_name, u.phone, b.amount
            FROM bonuses b JOIN users u ON u.telegram_id=b.user_id
            ORDER BY b.amount DESC
        """) as cur:
            return await cur.fetchall()

# ─── BOOKINGS ─────────────────────────────────────────────
async def add_booking(user_id: int, full_name: str, phone: str, room: str, date_time: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO bookings (user_id, full_name, phone, room, date_time) VALUES (?,?,?,?,?)",
            (user_id, full_name, phone, room, date_time)
        )
        await db.commit()
        return cur.lastrowid
        
async def is_time_busy(room: str, date_time: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT id FROM bookings
            WHERE room=? AND date_time=? AND status IN ('pending','approved')
            """,
            (room, date_time)
        ) as cur:
            return await cur.fetchone() is not None
async def get_pending_bookings():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM bookings WHERE status='pending' ORDER BY created_at ASC"
        ) as cur:
            return await cur.fetchall()

async def update_booking_status(booking_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
        await db.commit()
        
async def get_booking(booking_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM bookings WHERE id=?",
            (booking_id,)
        ) as cur:
            return await cur.fetchone()
# ─── CONTACTS ─────────────────────────────────────────────
async def add_contact(user_id: int, full_name: str, phone: str, message: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO contacts (user_id, full_name, phone, message) VALUES (?,?,?,?)",
            (user_id, full_name, phone, message)
        )
        await db.commit()
