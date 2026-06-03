# 🎮 GameClub Telegram Bot

## Bot imkoniyatlari
- ✅ Telefon raqam orqali ro'yxatdan o'tish
- 🎮 O'yinlarni hisoblash va tasdiqlatish
- 🎁 Bonus tizimi (10 o'yin = 5000 bonus)
- 📅 Joy bron qilish
- 📨 Talab va takliflar
- 🔐 To'liq admin panel

---

## 1-QADAM: Bot Token olish

1. Telegramda **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring
3. Botga nom bering (masalan: `GameClub Bot`)
4. Username bering (masalan: `mygameclub_bot`)
5. Sizga **TOKEN** beradi — uni saqlang!

---

## 2-QADAM: Admin ID olish

1. Telegramda **@userinfobot** ga yozing
2. `/start` bosing
3. U sizga **ID raqamingizni** beradi — uni saqlang!

---

## 3-QADAM: Railway'ga joylashtirish (24/7 ishlaydi)

### 3.1 GitHub'ga yuklash
1. https://github.com ga kiring (bepul hisob oching)
2. **New repository** bosing
3. Nom bering: `gameclub-bot`
4. Bot fayllarini yuklang (barcha .py va boshqa fayllarni)

### 3.2 Railway'da ishga tushirish
1. https://railway.app ga kiring
2. GitHub bilan kiring
3. **New Project** → **Deploy from GitHub repo** bosing
4. `gameclub-bot` reponi tanlang
5. **Variables** bo'limiga o'ting va quyidagilarni qo'shing:

```
BOT_TOKEN = sizning_bot_tokeningiz
ADMIN_ID = sizning_telegram_id_raqamingiz
```

Masalan:
```
BOT_TOKEN = 7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_ID = 987654321
```

6. **Deploy** tugmasini bosing
7. Bot 24/7 ishlaydi! 🚀

### Narx:
- Railway: $5/oy (Hobby plan) — ishonchli va tez

---

## Admin buyruqlari

Botda `/admin` buyrug'ini yuboring — admin paneli ochiladi.

### Admin nima qila oladi:
- 📋 Kutilayotgan o'yin so'rovlarini ko'rish va tasdiqlash/rad etish
- 📅 Bron so'rovlarini boshqarish
- 👥 Barcha foydalanuvchilarni ko'rish
- 🎁 Bonuslarni qo'shish yoki o'chirish
- 📊 Statistika ko'rish

---

## Bonus tizimi qanday ishlaydi?

1. Mijoz o'ynaydi → "🎮 Mening o'ynaganlarim" → "✅ O'ynadi deb belgilash"
2. Admin bildirishnoma oladi → ✅ Tasdiqlash yoki ❌ Rad etish
3. Tasdiqlansa — o'yin soni +1
4. **10 ta o'yin to'ldirilsa — avtomatik 5000 bonus qo'shiladi!**

---

## Muammo bo'lsa

Quyidagi fayllarni tekshiring:
- `config.py` da BOT_TOKEN va ADMIN_ID to'g'ri ekanini
- Yoki Railway Variables to'g'ri kiritilganini

---

*GameClub Bot — Professional Telegram bot solution*
