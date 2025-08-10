# xmodules/handlers/mention.py

from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import PeerFloodError
import asyncio


def register_mention_handler(client: TelegramClient, admin_id: int):

    async def mention_handler(event):
        if event.sender_id != admin_id:
            return

        if not event.is_group:
            await event.edit("❗ <b>Bu buyruq faqat guruhlarda ishlaydi.</b>", parse_mode='html')
            return

        message = event.pattern_match.group(1)
        reply_to = await event.get_reply_message()

        users = []
        async for user in client.iter_participants(event.chat_id):
            if user.bot:
                continue
            full_name = (user.first_name or "") + " " + (user.last_name or "")
            mention = f"<a href='tg://user?id={user.id}'>{full_name.strip()}</a>"
            users.append(mention)

        if not users:
            await event.edit("❗ <b>Hech qanday foydalanuvchi topilmadi.</b>", parse_mode='html')
            return

        await event.delete()

        chunk_size = 10
        for i in range(0, len(users), chunk_size):
            chunk = users[i:i + chunk_size]
            tag_block = "\n".join(chunk)
            text = f"{message}\n\n{tag_block}"
            try:
                if reply_to:
                    await event.respond(text, reply_to=reply_to.id, parse_mode='html')
                else:
                    await event.respond(text, parse_mode='html')
                await asyncio.sleep(2)
            except PeerFloodError:
                await event.respond("⛔ <b>Flood error:</b> <i>Keyinroq urinib ko'ring.</i>", parse_mode='html')
                break
            except Exception as e:
                await event.respond(f"⚠️ <b>Xatolik:</b>\n\n<code>{str(e)}</code>", parse_mode='html')
                break

    client.add_event_handler(mention_handler, events.NewMessage(outgoing=True, pattern=r'^\.mention(?: |$)(.*)'))
    return client