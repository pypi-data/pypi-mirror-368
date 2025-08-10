# xmodules/handlers/type.py

import asyncio
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from telethon import TelegramClient, events


def register_type_handler(client: TelegramClient, admin_id: int):

    async def safe_edit(message, text):
        try:
            return await message.edit(text)
        except MessageNotModifiedError:
            return message
        except Exception:
            return message

    async def typewriter_handler(event):
        if event.sender_id != admin_id:
            return

        text = event.pattern_match.group(1)
        message = event
        typed = ""

        for c in text:
            typed += "▒"
            message = await safe_edit(message, typed)
            await asyncio.sleep(0.04)
            typed = typed[:-1] + c
            message = await safe_edit(message, typed)
            await asyncio.sleep(0.02)

    client.add_event_handler(typewriter_handler, events.NewMessage(outgoing=True, pattern=r'^\.type (.+)'))
    return client
