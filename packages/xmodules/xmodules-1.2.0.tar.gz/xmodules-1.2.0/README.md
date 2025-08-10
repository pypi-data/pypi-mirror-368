# XModules haqida

**XModules** – bu Telegram userbotingiz uchun kengaytiriladigan kutubxona.
U yordamida barcha mavjud buyruqlarni ko‘rib chiqishingiz, yangi funksiyalarni ishlatishingiz va doimiy yangilanib boruvchi imkoniyatlardan foydalanishingiz mumkin.

## O‘rnatish
```bash
pip install xmodules
```

## Foydalanish misoli

`main.py` faylida quyidagicha yozing:

```python
from xmodules import run

API_ID = 12345678 # my.telegram.org'dan olingan API_ID
API_HASH = "your_api_hash" # my.telegram.org'dan olingan API_HASH
ADMIN_ID = 1234567890 # Telegram ID raqamingiz

run(API_ID, API_HASH, ADMIN_ID) # Ma'lumotlarni joylash
```

**Foydalanish tartibi:**

Chatda oddiy xabar sifatida quyidagisini yozing:

```bash
.help
```

**Shundan so‘ng userbot sizga quyidagilarni taqdim etadi:**

✅ Barcha mavjud buyruqlar ro‘yxati.  
✅ Har bir buyruqning qisqacha vazifasi va ishlatish usuli.

**Shu tarzda, XModules’dagi imkoniyatlardan xabardor bo‘lib turishingiz va yangi qo‘shilgan funksiyalarni ham oson topishingiz mumkin.**