# xmodules/handlers/countdown.py

import asyncio
from telethon import TelegramClient, events


def register_countdown_handler(client: TelegramClient, admin_id: int):

    async def countdown_handler(event):
        if event.sender_id != admin_id:
            return

        args = event.pattern_match.group(1)
        if not args:
            await event.edit("⚠️ <b>Foydalanish: .countdown «soniya» «matn»</b>", parse_mode='html')
            return

        parts = args.split(" ", 1)
        if len(parts) < 2:
            await event.edit("⚠️ <b>Matn yetarli emas. Masalan: .sleep 5 Hello</b>", parse_mode='html')
            return

        try:
            seconds = int(parts[0])
            message = parts[1]
        except ValueError:
            await event.edit("⚠️ <b>Soniya noto‘g‘ri. Butun son yozing.</b>", parse_mode='html')
            return

        for i in range(seconds, 0, -1):
            try:
                await event.edit(f"⏳ <b>{i} soniya ichida o‘chadi:</b>\n\n{message}", parse_mode='html')
                await asyncio.sleep(1)
            except:
                break

        try:
            await event.delete()
        except:
            pass

    client.add_event_handler(countdown_handler, events.NewMessage(outgoing=True, pattern=r'^\.countdown(?: |$)(.*)'))
    return client