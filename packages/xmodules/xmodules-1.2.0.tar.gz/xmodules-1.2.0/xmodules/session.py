# xmodules/session.py

import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

SESSION_FILE = "xmodules.session"


async def create_or_load_session(api_id: int, api_hash: str) -> TelegramClient:
    """
    Session faylini yuklab yoki yangi session yaratib qaytaradi.
    """
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            session_str = f.read().strip()
        client = TelegramClient(StringSession(session_str), api_id, api_hash)
    else:
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            phone = input("📱 Telefon raqamingiz: ")
            await client.send_code_request(phone)
            while True:
                code = input("📩 Kodni kiriting: ")
                try:
                    await client.sign_in(phone=phone, code=code)
                    break
                except SessionPasswordNeededError:
                    while True:
                        password = input("🔑 Parol: ")
                        try:
                            await client.sign_in(password=password)
                            break
                        except Exception:
                            print("❌ Parol xato. Qaytadan kiriting.")
                            continue
                    break
                except Exception:
                    print("❌ Kod xato yoki noto‘g‘ri. Qaytadan urinib ko‘ring.")
                    continue

        session_str = client.session.save()
        with open(SESSION_FILE, "w") as f:
            f.write(session_str)
        try:
            os.chmod(SESSION_FILE, 0o600)
        except:
            pass
        print(f"✅ Session saqlandi: {SESSION_FILE}")

    return client
