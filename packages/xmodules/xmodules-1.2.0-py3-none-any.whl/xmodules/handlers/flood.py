# xmodules/handlers/flood.py

from telethon import TelegramClient, events
import asyncio


def register_flood_handler(client: TelegramClient, admin_id: int):

    async def flood_handler(event):
        if event.sender_id != admin_id:
            return

        args = event.pattern_match.group(1).strip().split(' ', 1)
        count = int(args[0])
        reply = await event.get_reply_message()

        if len(args) > 1:
            text = args[1]
            await event.delete()
            for _ in range(count):
                await client.send_message(
                    event.chat_id,
                    text,
                    reply_to=reply.id if reply else None
                )
                await asyncio.sleep(0.2)
        else:
            if reply:
                await event.delete()
                for _ in range(count):
                    await client.send_message(
                        event.chat_id,
                        reply
                    )
                    await asyncio.sleep(0.2)
            else:
                await event.edit(
                    "⚠️ <b>Xabar matni topilmadi.</b>",
                    parse_mode="html"
                )

    client.add_event_handler(flood_handler, events.NewMessage(outgoing=True, pattern=r'^\.flood (.+)'))
    return client