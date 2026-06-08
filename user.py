from aiogram import Router, F, Bot
from aiogram.types import (Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import database as db
from keyboards import main_menu, share_contact_kb, cancel_kb
from config import ADMIN_ID, CONTACT_PHONE

user_locks = set()

router = Router()

# ─── STATES ───────────────────────────────────────────────
class Register(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_bonus = State()

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
    args = msg.text.split()

    referrer_id = None

    if len(args) > 1:
        try:
            referrer_id = int(args[1])
        except:
            pass

    user = await db.get_user(msg.from_user.id)

    if user:
        await msg.answer_photo(
            photo="AgACAgIAAxkBAAILtWo1P-ueaAABojXVaEXX_0QsNMkLewACVxxrG7D8KUmVcxHpjuRDUwEAAwIAA3kAAzsE",
            caption=
            f"👋 Xush kelibsiz, <b>{user['full_name']}</b>\n\n"
            "🎮 <b>ULTRA GAME CLUB</b>\n\n",
            parse_mode="HTML"
        )

        await msg.answer(
            "👇 Asosiy menyu",
            reply_markup=main_menu()
        )

    else:
        await msg.answer_photo(
            photo="AgACAgIAAxkBAAILtWo1P-ueaAABojXVaEXX_0QsNMkLewACVxxrG7D8KUmVcxHpjuRDUwEAAwIAA3kAAzsE",
            caption="🎮 <b>ULTRA GAME CLUB</b> botiga xush kelibsiz!\n\nRo'yxatdan o'tish uchun avval ismingizni kiriting:",
            parse_mode="HTML"
        )

        await state.update_data(referrer_id=referrer_id)
        await state.set_state(Register.waiting_name)
        
@router.message(Register.waiting_name)
async def reg_name(msg: Message, state: FSMContext):
    await state.update_data(full_name=msg.text)

    await msg.answer(
        "📱 Telefon raqamingizni yuboring:",
        reply_markup=share_contact_kb()
    )

    await state.set_state(Register.waiting_phone)
       
@router.message(Register.waiting_phone, F.text == "❌ Bekor qilish")
async def cancel_register_phone(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "❌ Bekor qilindi.",
        reply_markup=main_menu()
    )
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
        phone,
        data.get("referrer_id")
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
async def use_bonus_request(call: CallbackQuery):

    user_id = call.from_user.id

    if user_id in user_locks:
        await call.answer("⏳ Kuting...", show_alert=True)
        return

    user_locks.add(user_id)

    try:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="5000", callback_data="bonus_5000")],
                [InlineKeyboardButton(text="10000", callback_data="bonus_10000")]
            ]
        )

        await call.message.answer(
            "💰 Qancha bonus ishlatmoqchisiz?",
            reply_markup=kb
        )

    finally:
        user_locks.discard(user_id)

@router.callback_query(F.data == "bonus_5000")
async def bonus_5000(call: CallbackQuery, bot: Bot):
    user = await db.get_user(call.from_user.id)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="✅ Tasdiqlash",
                callback_data=f"bonus_use_approve:{call.from_user.id}:5000"
            ),
            InlineKeyboardButton(
                text="❌ Rad etish",
                callback_data=f"bonus_use_reject:{call.from_user.id}"
            )
        ]]
    )

    await bot.send_message(
        ADMIN_ID,
        f"💰 Bonus ishlatish so'rovi\n\n👤 {user['full_name']}\n🪙 Bonus: 5000",
        reply_markup=kb
    )

    await call.answer("✅ So'rov yuborildi")

@router.callback_query(F.data == "bonus_10000")
async def bonus_10000(call: CallbackQuery, bot: Bot):
    user = await db.get_user(call.from_user.id)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="✅ Tasdiqlash",
                callback_data=f"bonus_use_approve:{call.from_user.id}:10000"
            ),
            InlineKeyboardButton(
                text="❌ Rad etish",
                callback_data=f"bonus_use_reject:{call.from_user.id}"
            )
        ]]
    )

    await bot.send_message(
        ADMIN_ID,
        f"💰 Bonus ishlatish so'rovi\n\n👤 {user['full_name']}\n🪙 Bonus: 10000",
        reply_markup=kb
    )

    await call.answer("✅ So'rov yuborildi")

@router.callback_query(F.data.startswith("bonus_use_approve:"))
async def bonus_use_approve(call: CallbackQuery, bot: Bot):
    parts = call.data.split(":")
    user_id = int(parts[1])
    bonus = int(parts[2])

    current_bonus = await db.get_bonus(user_id)
    await db.set_bonus(user_id, current_bonus - bonus)

    await call.message.edit_text(
        f"✅ <b>Bonus ishlatish tasdiqlandi!</b>\n💰 {bonus} bonus ayirildi.",
        parse_mode="HTML"
    )

    await call.answer("✅ Tasdiqlandi!")
    try:
       await bot.send_message(
    user_id,
    f"✅ <b>{bonus} bonusingiz muvaffaqiyatli ishlatildi!</b>\n\n💰 Joriy bonuslar: {current_bonus - bonus}",
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

    if room == "❌ Bekor qilish":
        await state.clear()
        await msg.answer(
            "❌ Bekor qilindi.",
            reply_markup=main_menu()
        )
        return

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
    
@router.message(Booking.waiting_name, F.text == "❌ Bekor qilish")
async def cancel_booking_name(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "❌ Bekor qilindi.",
        reply_markup=main_menu()
    )
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
    
    if msg.from_user.id in user_locks:
        await msg.answer("⏳ Kuting, so'rov qayta ishlanmoqda...")
        return

    user_locks.add(msg.from_user.id)

    busy = await db.is_time_busy(
        data["room"],
        msg.text.strip()
    )

    if busy:
        await msg.answer(
            "❌ Bu vaqt band!\n\nBoshqa vaqt tanlang."
        )
        return

    try:
    booking_id = await db.add_booking(
        msg.from_user.id,
        data["full_name"],
        data["phone"],
        data["room"],
        msg.text.strip()
    )

    await state.clear()

    await msg.answer(
        f"✅ <b>Broningiz qabul qilindi!</b>\n\n",
        parse_mode="HTML"
    )

    await bot.send_message(
        ADMIN_ID,
        f"📋 <b>Yangi bron so'rovi #{booking_id}</b>\n\n"
        f"👤 Ism: {data['full_name']}\n"
        f"📱 Tel: {data['phone']}\n"
        f"📅 Vaqt: {msg.text.strip()}\n"
        f"🆔 User ID: {msg.from_user.id}",
        parse_mode="HTML",
        reply_markup=booking_action_kb(booking_id)
    )

except Exception as e:
    print("BOOKING ERROR:", e)

    await msg.answer(
        "❌ Bron saqlashda xatolik yuz berdi. Qayta urinib ko'ring."
    )
    
finally:
    user_locks.discard(msg.from_user.id)
        
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

@router.message(Contact.waiting_name, F.text == "❌ Bekor qilish")
async def cancel_contact_name(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "❌ Bekor qilindi.",
        reply_markup=main_menu()
    )
                
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

@router.message(F.text == "💳 Hisobni to'ldirish")
async def payment_info(msg: Message):
    await msg.answer(
        "💳 To'lov uchun kartalar\n\n"
        "🏦 Uzcard:\n"
        "5614 6827 1546 0525\n\n"
        "👤 Karta egasi: Xalilov Feruz\n\n"
        "📸 To'lov qilgandan so'ng chek rasmini yuboring."
    )

@router.message(F.text == "👥 Referal havolam")
async def referral_link(msg: Message, bot: Bot):
    me = await bot.get_me()

    link = f"https://t.me/{me.username}?start={msg.from_user.id}"

    referal_count = await db.get_referral_count(msg.from_user.id)

    await msg.answer(
        f"👥 Referal havolangiz:\n\n{link}\n\n"
        f"👤 Taklif qilgan do'stlaringiz: {referal_count} ta\n"
        f"🎁 Har bir taklif uchun 1000 bonus beriladi."
    )
