# xmodules/handlers/online.py

import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateStatusRequest

status = False
online_task = None


async def stay_online_loop(client: TelegramClient):
    while status:
        await client(UpdateStatusRequest(offline=False))
        await asyncio.sleep(30)


def register_online_handler(client: TelegramClient, admin_id: int):

    async def online_handler(event):
        global online_task, status

        if event.sender_id != admin_id:
            return

        args = event.pattern_match.group(1).strip().split(" ", 1)

        if args[0] == "on":
            if not status:
                status = True
                online_task = asyncio.create_task(stay_online_loop(client))
                await event.edit("✅ <b>24/7 online yoqildi.</b>", parse_mode="html")
            else:
                await event.edit("ℹ️ <b>Allaqachon yoqilgan.</b>", parse_mode="html")

        elif args[0] == "off":
            if status:
                status = False
                if online_task:
                    online_task.cancel()
                    try:
                        await online_task
                    except asyncio.CancelledError:
                        pass
                    online_task = None
                await event.edit("✅ <b>24/7 online o'chirildi.</b>", parse_mode="html")
            else:
                await event.edit("ℹ️ <b>Allaqachon o'chirilgan.</b>", parse_mode="html")

        else:
            await event.edit("⚠️ <b>Buyruq topilmadi.</b>", parse_mode="html")

    client.add_event_handler(online_handler, events.NewMessage(outgoing=True, pattern=r'^\.online\s*(.*)'))
    return client