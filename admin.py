from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

import database as db
from keyboards import admin_menu, main_menu, bonus_user_kb
from config import ADMIN_ID

router = Router()

# ─── ADMIN FILTER ─────────────────────────────────────────
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

# ─── STATES ───────────────────────────────────────────────
class BonusAdd(StatesGroup):
    waiting_amount = State()

# ─── ADMIN COMMANDS ───────────────────────────────────────
@router.message(Command("admin"))
async def admin_panel(msg: Message):
    if not is_admin(msg.from_user.id):
        await msg.answer("❌ Sizda admin huquqi yo'q!")
        return
    await msg.answer(
        "🔐 <b>Admin paneli</b>\n\nXush kelibsiz, Admin!",
        parse_mode="HTML",
        reply_markup=admin_menu()
    )

@router.message(F.text == "🏠 Asosiy menyu")
async def back_to_main(msg: Message):
    if not is_admin(msg.from_user.id): return
    await msg.answer("🏠 Asosiy menyu", reply_markup=main_menu())

# ─── PENDING PLAYS ────────────────────────────────────────
@router.message(F.text == "📋 Kutilayotgan o'yinlar")
async def pending_plays(msg: Message):
    if not is_admin(msg.from_user.id): return
    plays = await db.get_pending_plays()
    if not plays:
        await msg.answer("✅ Kutilayotgan o'yin so'rovlari yo'q.")
        return
    await msg.answer(f"📋 <b>Kutilayotgan so'rovlar: {len(plays)} ta</b>", parse_mode="HTML")
    from keyboards import play_action_kb
    for p in plays:
        await msg.answer(
            f"🎮 <b>O'yin so'rovi #{p['id']}</b>\n\n"
            f"👤 Ism: {p['full_name']}\n"
            f"📱 Tel: {p['phone']}\n"
            f"🆔 ID: {p['user_id']}\n"
            f"📅 Vaqt: {p['created_at']}",
            parse_mode="HTML",
            reply_markup=play_action_kb(p['id'])
        )

@router.callback_query(F.data.startswith("play_approve:"))
async def approve_play(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    req_id = int(call.data.split(":")[1])
    req = await db.get_play_request(req_id)
    if not req:
        await call.answer("So'rov topilmadi!", show_alert=True)
        return

    await db.update_play_status(req_id, "approved")

    # 10 ta o'yin = 5000 bonus
    play_count = await db.get_play_count(req["user_id"])
    bonus_msg = ""
    if play_count % 10 == 0 and play_count > 0:
        await db.add_bonus(req["user_id"], 5000)
        bonus_msg = "\n\n🎉 <b>Tabriklaymiz! 5000 bonus qo'shildi!</b>"

    await call.message.edit_text(
        f"✅ <b>Tasdiqlandi</b> - So'rov #{req_id}",
        parse_mode="HTML"
    )
    await call.answer("✅ Tasdiqlandi!")

    try:
        await bot.send_message(
            req["user_id"],
            f"✅ <b>O'yiningiz tasdiqlandi!</b>\n\n"
            f"🎮 Jami tasdiqlangan o'yinlar: <b>{play_count} ta</b>{bonus_msg}",
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.callback_query(F.data.startswith("play_reject:"))
async def reject_play(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    req_id = int(call.data.split(":")[1])
    req = await db.get_play_request(req_id)
    if not req:
        await call.answer("So'rov topilmadi!", show_alert=True)
        return

    await db.update_play_status(req_id, "rejected")
    await call.message.edit_text(f"❌ <b>Rad etildi</b> - So'rov #{req_id}", parse_mode="HTML")
    await call.answer("❌ Rad etildi!")

    try:
        await bot.send_message(
            req["user_id"],
            "❌ <b>So'rovingiz rad etildi.</b>\n\nQo'shimcha ma'lumot uchun admin bilan bog'laning.",
            parse_mode="HTML"
        )
    except Exception:
        pass

# ─── PENDING BOOKINGS ─────────────────────────────────────
@router.message(F.text == "📅 Kutilayotgan bronlar")
async def pending_bookings(msg: Message):
    if not is_admin(msg.from_user.id): return
    bookings = await db.get_pending_bookings()
    if not bookings:
        await msg.answer("✅ Kutilayotgan bron so'rovlari yo'q.")
        return
    await msg.answer(f"📅 <b>Kutilayotgan bronlar: {len(bookings)} ta</b>", parse_mode="HTML")
    from keyboards import booking_action_kb
    for b in bookings:
        await msg.answer(
            f"📅 <b>Bron #{b['id']}</b>\n\n"
            f"👤 Ism: {b['full_name']}\n"
            f"📱 Tel: {b['phone']}\n"
            f"📆 Vaqt: {b['date_time']}\n"
            f"🆔 User ID: {b['user_id']}",
            parse_mode="HTML",
            reply_markup=booking_action_kb(b['id'])
        )

@router.callback_query(F.data.startswith("book_approve:"))
@router.callback_query(F.data.startswith("book_approve:"))
async def approve_booking(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    parts = call.data.split(":")
    booking_id = int(parts[1])
    booking = await db.get_booking(booking_id)

    if not booking:
        await call.answer("Bron topilmadi!", show_alert=True)
        return

    await db.update_booking_status(booking_id, "approved")
    await call.message.edit_text(
        f"✅ <b>Bron #{booking_id} tasdiqlandi</b>",
        parse_mode="HTML"
    )
    await call.answer("✅ Tasdiqlandi!")
        await bot.send_message(
            booking["user_id"],
            f"✅ <b>Broningiz tasdiqlandi!</b>\n\n"
            f"📆 Vaqt: {booking['date_time']}\n\n"
            f"Sizni kutamiz! 🎮",
            parse_mode="HTML"
        )
    except Exception:
        pass

@router.callback_query(F.data.startswith("book_reject:"))
async def reject_booking(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    parts = call.data.split(":")
    booking_id = int(parts[1])
    booking = await db.get_booking(booking_id)
    if not booking:
        await call.answer("Bron topilmadi!", show_alert=True)
        return
    await db.update_booking_status(booking_id, "rejected")
    await call.message.edit_text(f"❌ <b>Bron #{booking_id} rad etildi</b>", parse_mode="HTML")
    await call.answer("❌ Rad etildi!")
    try:
        await bot.send_message(
            booking["user_id"],
            "❌ <b>Broningiz rad etildi.</b>\n\nQo'shimcha ma'lumot uchun bog'laning: +998996862274",
            parse_mode="HTML"
        )
    except Exception:
        pass

# ─── USERS LIST ───────────────────────────────────────────
@router.message(F.text == "👥 Foydalanuvchilar")
async def users_list(msg: Message):
    if not is_admin(msg.from_user.id): return
    users = await db.get_all_users()
    if not users:
        await msg.answer("👥 Hali foydalanuvchilar yo'q.")
        return
    text = f"👥 <b>Foydalanuvchilar: {len(users)} ta</b>\n\n"
    for i, u in enumerate(users[:20], 1):
        text += f"{i}. {u['full_name']} | {u['phone']} | ID: {u['telegram_id']}\n"
    if len(users) > 20:
        text += f"\n...va yana {len(users)-20} ta"
    await msg.answer(text, parse_mode="HTML")

# ─── BONUS MANAGEMENT ─────────────────────────────────────
@router.message(F.text == "🎁 Bonuslarni boshqarish")
async def manage_bonuses(msg: Message):
    if not is_admin(msg.from_user.id): return
    bonuses = await db.get_all_bonuses()
    if not bonuses:
        await msg.answer("🎁 Hali foydalanuvchilar yo'q.")
        return
    for b in bonuses[:15]:
        await msg.answer(
            f"👤 <b>{b['full_name']}</b>\n"
            f"📱 {b['phone']}\n"
            f"💰 Bonus: <b>{b['amount']}</b>",
            parse_mode="HTML",
            reply_markup=bonus_user_kb(b['telegram_id'], b['amount'])
        )

@router.callback_query(F.data.startswith("bonus_clear:"))
async def bonus_clear(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    user_id = int(call.data.split(":")[1])
    await db.set_bonus(user_id, 0)
    await call.message.edit_text(
        call.message.text + "\n\n✅ <b>Bonus o'chirildi!</b>",
        parse_mode="HTML"
    )
    await call.answer("🗑 Bonus o'chirildi!")

@router.callback_query(F.data.startswith("bonus_add:"))
async def bonus_add_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    user_id = int(call.data.split(":")[1])
    await state.update_data(target_user_id=user_id)
    await call.message.answer("➕ Qancha bonus qo'shilsin? (Raqam kiriting):")
    await state.set_state(BonusAdd.waiting_amount)
    await call.answer()

@router.message(BonusAdd.waiting_amount)
async def bonus_add_amount(msg: Message, state: FSMContext, bot: Bot):
    if not is_admin(msg.from_user.id):
        await state.clear()
        return
    try:
        amount = int(msg.text.strip())
    except ValueError:
        await msg.answer("❌ Raqam kiriting:")
        return
    data = await state.get_data()
    user_id = data["target_user_id"]
    await db.add_bonus(user_id, amount)
    new_bonus = await db.get_bonus(user_id)
    await state.clear()
    await msg.answer(
        f"✅ <b>{amount} bonus qo'shildi!</b>\nJami: <b>{new_bonus}</b>",
        parse_mode="HTML",
        reply_markup=admin_menu()
    )
    try:
        await bot.send_message(
            user_id,
            f"🎁 <b>Sizga {amount} bonus qo'shildi!</b>\n\n💰 Jami bonuslar: <b>{new_bonus}</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

# ─── STATISTICS ───────────────────────────────────────────
@router.message(F.text == "📊 Statistika")
async def statistics(msg: Message):
    if not is_admin(msg.from_user.id): return
    users = await db.get_all_users()
    bonuses = await db.get_all_bonuses()
    bookings = await db.get_pending_bookings()

    total_bonus = sum(b['amount'] for b in bonuses)

    await msg.answer(
        f"📊 <b>Bot statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{len(users)}</b>\n"
        f"📅 Kutilayotgan bronlar: <b>{len(bookings)}</b>\n"
        f"💰 Jami bonuslar: <b>{total_bonus}</b>",
        parse_mode="HTML"
    )
