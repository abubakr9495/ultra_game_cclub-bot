from aiogram import Router, F, Bot
from aiogram.types import (Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart

import database as db
from keyboards import main_menu, share_contact_kb, cancel_kb
from config import ADMIN_ID, CONTACT_PHONE

router = Router()

# ─── STATES ───────────────────────────────────────────────
class Register(StatesGroup):
    waiting_name = State()
    waiting_phone = State()

class Booking(StatesGroup):
    waiting_room = State()
    waiting_name = State()
    waiting_phone = State()
    waiting_datetime = State()

class Contact(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_message = State()

# ─── START / REGISTRATION ─────────────────────────────────
@router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    user = await db.get_user(msg.from_user.id)
    if user:
        
        await msg.answer_photo(
            photo="AgACAgIAAxkBAAIJDWokGjVQYZAopjXjokFrrJIdegABMgACbhhrG7D8IUnsPI0eUCE4gQEAAwIAA3kAAzsE",
            caption=
            f"👏 Xush kelibsiz, <b>{user['full_name']}</b>\n\n"
            "🎮 <b>ULTRA GAME CLUB</b>\n\n"
            "🔥 Kuchli Gaming PC lar\n"
            "📅 Joy bron qilish\n"
            "🎁 Bonus tizimi\n"
            "🏆 Turnirlar va musobaqalar\n\n"
            "📍 Qarshi tumani, Beshket shahri,\n"
            "Navoiy MFY 75-uy\n\n"
            "📞 +998996862274\n"
            "🤖 @ultra_game_cclubbot",
            parse_mode="HTML"
        )

        await msg.answer(
            "👇 Asosiy menyu",
            reply_markup=main_menu()
        )

        else:
        await msg.answer(
            "🎮 <b>GameClub</b> botiga xush kelibsiz!\n\n"
            "Ro'yxatdan o'tish uchun avval ismingizni kiriting:",
            parse_mode="HTML"
        )

        await state.set_state(Register.waiting_name)

        await state.set_state(Register.waiting_name)
    else:
        await msg.answer(
            "🎮 <b>GameClub</b> botiga xush kelibsiz!\n\n"
            "Ro'yxatdan o'tish uchun avval ismingizni kiriting:",
            parse_mode="HTML"
        )
        await state.set_state(Register.waiting_name)

@router.message(Register.waiting_name)
async def reg_name(msg: Message, state: FSMContext):
    if len(msg.text.strip()) < 2:
        await msg.answer("❌ Ism juda qisqa. Qaytadan kiriting:")
        return
    await state.update_data(full_name=msg.text.strip())
    await msg.answer(
        "📱 Telefon raqamingizni yuboring:",
        reply_markup=share_contact_kb()
    )
    await state.set_state(Register.waiting_phone)

@router.message(Register.waiting_phone,F.contact)
async def reg_phone_contact(msg: Message, state: FSMContext):
    if not msg.contact:
        await msg.answer(
            "📱 Iltimos, tugma orqali telefon raqamingizni yuboring:",
            reply_markup=share_contact_kb()
        )
        return

    data = await state.get_data()

    phone = msg.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone

    await db.create_user(
        msg.from_user.id,
        data["full_name"],
        phone
    )

    await state.clear()

    await msg.answer(
        f"✅ <b>Ro'yxatdan o'tdingiz!</b>\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"📱 Tel: {phone}\n\n"
        f"🎮 Asosiy menyuga xush kelibsiz!",
        parse_mode="HTML",
        reply_markup=main_menu()
    )
@router.message(Register.waiting_phone)
async def reg_phone_text(msg: Message):
    await msg.answer("📱 Iltimos, tugma orqali telefon raqamingizni yuboring:", reply_markup=share_contact_kb())

# ─── CHECK REGISTRATION ───────────────────────────────────
async def check_reg(msg: Message):
    user = await db.get_user(msg.from_user.id)
    if not user:
        await msg.answer("❗ Avval /start buyrug'ini bosing va ro'yxatdan o'ting.")
        return False
    return True

# ─── PANEL 1: O'YNAGANLARIM ───────────────────────────────
@router.message(F.text == "🎮 Mening o'ynaganlarim")
async def my_plays(msg: Message, bot: Bot):
    if not await check_reg(msg): return
    count = await db.get_play_count(msg.from_user.id)
    bonus = await db.get_bonus(msg.from_user.id)
    remaining = 10 - (count % 10)

    progress_bar = "🟩" * (count % 10) + "⬜" * (10 - (count % 10))

    await msg.answer(
        f"🎮 <b>Mening o'ynaganlarim</b>\n\n"
        f"📊 Jami o'yinlar: <b>{count} marta</b>\n"
        f"🎁 Bonuslar: <b>{bonus}</b>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{progress_bar}\n"
        f"🏆 Keyingi bonusgacha: <b>{remaining} ta</b>\n\n"
        f"👇 O'yin o'ynagandan so'ng tugmani bosing:",
        parse_mode="HTML"
    )
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ O'ynadi deb belgilash", callback_data="i_played")
    ]])
    await msg.answer("⬇️ O'yndingizmi?", reply_markup=kb)

@router.callback_query(F.data == "i_played")
async def i_played(call: CallbackQuery, bot: Bot):
    user = await db.get_user(call.from_user.id)
    if not user:
        await call.answer("Ro'yxatdan o'ting!", show_alert=True)
        return
    req_id = await db.add_play_request(call.from_user.id)
    await call.answer("✅ So'rovingiz adminga yuborildi!", show_alert=True)
    await call.message.edit_text("⏳ <b>So'rovingiz admin tomonidan ko'rib chiqilmoqda...</b>", parse_mode="HTML")

    from keyboards import play_action_kb
    await bot.send_message(
        ADMIN_ID,
        f"🎮 <b>O'yin tasdiqlash so'rovi</b>\n\n"
        f"👤 Ism: {user['full_name']}\n"
        f"📱 Tel: {user['phone']}\n"
        f"🆔 ID: {call.from_user.id}\n"
        f"📋 So'rov #{req_id}",
        parse_mode="HTML",
        reply_markup=play_action_kb(req_id)
    )
@router.message(F.text == "👤 Profil")
async def profile(msg: Message):
    if not await check_reg(msg):
        return

    user = await db.get_user(msg.from_user.id)
    count = await db.get_play_count(msg.from_user.id)
    bonus = await db.get_bonus(msg.from_user.id)

    if count >= 250:
        status = "💎 Platinum"
    elif count >= 100:
        status = "🥇 Gold"
    elif count >= 50:
        status = "🥈 Silver"
    else:
        status = "⭐ Oddiy"

    await msg.answer(
        f"👤 <b>Profil</b>\n\n"
        f"🧑 Ism: <b>{user['full_name']}</b>\n"
        f"📱 Telefon: <b>{user['phone']}</b>\n\n"
        f"🎮 Jami o'yinlar: <b>{count}</b>\n"
        f"🎁 Bonuslar: <b>{bonus}</b>\n"
        f"🏆 Status: <b>{status}</b>",
        parse_mode="HTML"
    )

# ─── PANEL 2: BONUSLARIM ─────────────────────────
@router.message(F.text == "🎁 Mening bonuslarim")

# ─── PANEL 2: BONUSLARIM ──────────────────────────────────
@router.message(F.text == "🎁 Mening bonuslarim")
async def my_bonuses(msg: Message):
    if not await check_reg(msg): return
    count = await db.get_play_count(msg.from_user.id)
    bonus = await db.get_bonus(msg.from_user.id)

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = None
    if bonus > 0:
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="💳 Bonusni ishlatish", callback_data="use_bonus")
        ]])

    await msg.answer(
        f"🎁 <b>Mening bonuslarim</b>\n\n"
        f"💰 Joriy bonuslar: <b>{bonus}</b>\n"
        f"🎮 Jami o'yinlar: <b>{count}</b>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏆 <b>Aksiya:</b>\n"
        f"10 marta to'ldiring — <b>5000 bonus</b>ga ega bo'ling!\n\n"
        f"📊 Joriy holat: {count % 10}/10\n"
        f"{'🟩' * (count % 10)}{'⬜' * (10 - count % 10)}",
        parse_mode="HTML",
        reply_markup=kb if kb else main_menu()
    )

@router.callback_query(F.data == "use_bonus")
async def use_bonus_request(call: CallbackQuery, bot: Bot):
    user = await db.get_user(call.from_user.id)
    bonus = await db.get_bonus(call.from_user.id)
    if bonus <= 0:
        await call.answer("❌ Bonusingiz yo'q!", show_alert=True)
        return
    await call.answer("✅ So'rovingiz adminga yuborildi!", show_alert=True)
    await call.message.edit_text(
        f"🎁 <b>Mening bonuslarim</b>\n\n"
        f"💰 Joriy bonuslar: <b>{bonus}</b>\n\n"
        f"⏳ Bonus ishlatish so'rovi adminga yuborildi...",
        parse_mode="HTML"
    )
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"bonus_use_approve:{call.from_user.id}:{bonus}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"bonus_use_reject:{call.from_user.id}"),
    ]])
    await bot.send_message(
        ADMIN_ID,
        f"💳 <b>Bonus ishlatish so'rovi</b>\n\n"
        f"👤 Ism: {user['full_name']}\n"
        f"📱 Tel: {user['phone']}\n"
        f"💰 Bonus: <b>{bonus}</b>\n"
        f"🆔 ID: {call.from_user.id}",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.callback_query(F.data.startswith("bonus_use_approve:"))
async def bonus_use_approve(call: CallbackQuery, bot: Bot):
    parts = call.data.split(":")
    user_id = int(parts[1])
    bonus = int(parts[2])
    await db.set_bonus(user_id, 0)
    await call.message.edit_text(
        f"✅ <b>Bonus ishlatish tasdiqlandi!</b>\n💰 {bonus} bonus ayirildi.",
        parse_mode="HTML"
    )
    await call.answer("✅ Tasdiqlandi!")
    try:
        await bot.send_message(
            user_id,
            f"✅ <b>{bonus} bonusingiz muvaffaqiyatli ishlatildi!</b>\n\n💰 Joriy bonuslar: 0",
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.callback_query(F.data.startswith("bonus_use_reject:"))
async def bonus_use_reject(call: CallbackQuery, bot: Bot):
    user_id = int(call.data.split(":")[1])
    await call.message.edit_text("❌ <b>Bonus ishlatish rad etildi.</b>", parse_mode="HTML")
    await call.answer("❌ Rad etildi!")
    try:
        await bot.send_message(
            user_id,
            "❌ <b>Bonus ishlatish so'rovingiz rad etildi.</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

# ─── PANEL 3: JOY BRON QILISH ─────────────────────────────
@router.message(F.text == "📅 Joy bron qilish")
async def booking_start(msg: Message, state: FSMContext):
    if not await check_reg(msg):
        return

    room_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1️⃣ Chap xona")],
            [KeyboardButton(text="2️⃣ O'ng xona")],
            [KeyboardButton(text="3️⃣ Zal")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )

    await msg.answer(
        "🏠 Xonani tanlang:",
        reply_markup=room_kb
    )

    await state.set_state(Booking.waiting_room)

@router.message(Booking.waiting_room)
async def booking_room(msg: Message, state: FSMContext):
    room = msg.text.strip()

    if room not in [
        "Chap xona",
        "O'ng xona",
        "Zal",
        "1",
        "2",
        "3",
        "1️⃣ Chap xona",
        "2️⃣ O'ng xona",
        "3️⃣ Zal"
    ]:
        await msg.answer(
            "🏠 Xonani tanlang:\nChap xona\nO'ng xona\nZal"
        )
        return

    if room == "1️⃣ Chap xona":
        room = "Chap xona"
    elif room == "2️⃣ O'ng xona":
        room = "O'ng xona"
    elif room == "3️⃣ Zal":
        room = "Zal"

    await state.update_data(room=room)

    await msg.answer("👤 Ismingizni kiriting:")

    await state.set_state(Booking.waiting_name)
    
@router.message(Booking.waiting_name)
async def booking_name(msg: Message, state: FSMContext):
    await state.update_data(full_name=msg.text.strip())
    await msg.answer("📱 Telefon raqamingizni kiriting (masalan: +998901234567):")
    await state.set_state(Booking.waiting_phone)

@router.message(Booking.waiting_phone, F.text == "❌ Bekor qilish")
async def cancel_booking_phone(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Bekor qilindi.", reply_markup=main_menu())

@router.message(Booking.waiting_phone)
async def booking_phone(msg: Message, state: FSMContext):
    await state.update_data(phone=msg.text.strip())
    await msg.answer("📆 Sana va vaqtni kiriting\n(masalan: 15-iyun, soat 14:00):")
    await state.set_state(Booking.waiting_datetime)

@router.message(Booking.waiting_datetime, F.text == "❌ Bekor qilish")
async def cancel_booking_dt(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Bekor qilindi.", reply_markup=main_menu())

@router.message(Booking.waiting_datetime)
async def booking_datetime(msg: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()

    busy = await db.is_time_busy(
        data["room"],
        msg.text.strip()
    )

    if busy:
        await msg.answer(
            "❌ Bu vaqt band!\n\nBoshqa vaqt tanlang."
        )
        return

    booking_id = await db.add_booking(
        msg.from_user.id,
        data["full_name"],
        data["phone"],
        data["room"],
        msg.text.strip()
    )
    await state.clear()
    
    await msg.answer(
    f"✅ <b>Broningiz qabul qilindi!</b>\n\n"
    f"🏠 Xona: {data['room']}\n"
    f"👤 Ism: {data['full_name']}\n"
    f"📱 Tel: {data['phone']}\n"
    f"📅 Vaqt: {msg.text.strip()}\n\n"
    f"⏳ <b>Hurmatli mijoz, sizga 5-10 daqiqa ichida javob kelmasa,\n"
    f"quyidagi raqamga murojaat qiling:</b>\n📞 {CONTACT_PHONE}",
    parse_mode="HTML",
    reply_markup=main_menu()
    )
    from keyboards import booking_action_kb
    await bot.send_message(
        ADMIN_ID,
        f"📅 <b>Yangi bron so'rovi #{booking_id}</b>\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"📱 Tel: {data['phone']}\n"
        f"📆 Vaqt: {msg.text.strip()}\n"
        f"🆔 User ID: {msg.from_user.id}",
        parse_mode="HTML",
        reply_markup=booking_action_kb(booking_id)
    )

# ─── PANEL 4: MUROJAT ─────────────────────────────────────
@router.message(F.text == "📨 Murojat uchun")
async def contact_start(msg: Message, state: FSMContext):
    if not await check_reg(msg): return
    await msg.answer(
        "📨 <b>Talab va takliflar uchun murojaat</b>\n\n"
        "Ism sharifingizni kiriting:",
        parse_mode="HTML",
        reply_markup=cancel_kb()
    )
    await state.set_state(Contact.waiting_name)

@router.message(Contact.waiting_name)
async def contact_name(msg: Message, state: FSMContext):
    await state.update_data(full_name=msg.text.strip())
    await msg.answer("📱 Telefon raqamingizni kiriting:")
    await state.set_state(Contact.waiting_phone)

@router.message(Contact.waiting_phone, F.text == "❌ Bekor qilish")
async def cancel_contact_phone(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Bekor qilindi.", reply_markup=main_menu())

@router.message(Contact.waiting_phone)
async def contact_phone(msg: Message, state: FSMContext):
    await state.update_data(phone=msg.text.strip())
    await msg.answer("💬 Talab yoki taklifingizni yozing:")
    await state.set_state(Contact.waiting_message)

class Contact2(StatesGroup):
    waiting_message = State()

@router.message(Contact.waiting_message, F.text == "❌ Bekor qilish")
async def cancel_contact_msg(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Bekor qilindi.", reply_markup=main_menu())

@router.message(Contact.waiting_message)
async def contact_message(msg: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await db.add_contact(msg.from_user.id, data["full_name"], data["phone"], msg.text.strip())
    await state.clear()
    await msg.answer(
        "✅ <b>Murojatingiz qabul qilindi!</b>\n\n"
        "Tez orada siz bilan bog'lanamiz. Rahmat! 🙏",
        parse_mode="HTML",
        reply_markup=main_menu()
    )
    await bot.send_message(
        ADMIN_ID,
        f"📨 <b>Yangi murojat</b>\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"📱 Tel: {data['phone']}\n"
        f"💬 Xabar: {msg.text.strip()}\n"
        f"🆔 User ID: {msg.from_user.id}",
        parse_mode="HTML"
    )
@router.message(F.photo)
async def get_file_id(msg: Message):
    await msg.answer(msg.photo[-1].file_id)
