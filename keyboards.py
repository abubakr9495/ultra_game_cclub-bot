from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ─── MAIN MENU ────────────────────────────────────────────
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 Mening o'ynaganlarim"),
 KeyboardButton(text="🎁 Mening bonuslarim")],

[KeyboardButton(text="👤 Profil"),
 KeyboardButton(text="📅 Joy bron qilish")],

[KeyboardButton(text="💳 Hisobni to'ldirish"),
 KeyboardButton(text="📨 Murojat uchun")],
        ],
        resize_keyboard=True
    )

# ─── SHARE CONTACT ────────────────────────────────────────
def share_contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# ─── CANCEL ───────────────────────────────────────────────
def cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    )

# ─── ADMIN PANEL ──────────────────────────────────────────
def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Kutilayotgan o'yinlar"),
             KeyboardButton(text="📅 Kutilayotgan bronlar")],
            [KeyboardButton(text="👥 Foydalanuvchilar"),
             KeyboardButton(text="🎁 Bonuslarni boshqarish")],
            [KeyboardButton(text="📊 Statistika"),
             KeyboardButton(text="📢 E'lon yuborish")],
            [KeyboardButton(text="🏠 Asosiy menyu")],
        ],
        resize_keyboard=True
    )

# ─── PLAY APPROVE/REJECT ──────────────────────────────────
def play_action_kb(req_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"play_approve:{req_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"play_reject:{req_id}"),
        ]
    ])

# ─── BOOKING APPROVE/REJECT ───────────────────────────────
def booking_action_kb(booking_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"book_approve:{booking_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"book_reject:{booking_id}"),
        ]
    ])

# ─── BONUS MANAGEMENT ─────────────────────────────────────
def bonus_user_kb(user_id: int, current: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Bonus qo'shish", callback_data=f"bonus_add:{user_id}"),
            InlineKeyboardButton(text="🗑 Bonusni o'chirish", callback_data=f"bonus_clear:{user_id}"),
        ]
    ])
