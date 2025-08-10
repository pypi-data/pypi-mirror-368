# xmodules/handlers/clear.py

from telethon import TelegramClient, events
from telethon.tl.functions.messages import DeleteHistoryRequest


def register_clear_handler(client: TelegramClient, admin_id: int):

    async def clear_handler(event):
        if event.sender_id != admin_id:
            return

        await event.delete()
        try:
            chat = None
            if event.is_reply:
                reply = await event.get_reply_message()
                chat = await reply.get_chat()
            else:
                args = event.raw_text.split(maxsplit=1)
                if len(args) == 2:
                    entity = args[1]
                    chat = await client.get_entity(entity)
                else:
                    chat = await event.get_chat()
            await client(DeleteHistoryRequest(
                peer=chat,
                max_id=0,
                revoke=True
            ))
        except Exception as e:
            await client.send_message(
                "me",
                f"⚠️ <code>.clear</code> buyrug‘ida xatolik:\n\n<code>{str(e)}</code>",
                parse_mode="html"
            )

    async def del_handler(event):
        if event.sender_id != admin_id:
            return

        reply = await event.get_reply_message()
        if not reply:
            await event.edit("⚠️ <b>Xabar topilmadi.</b>", parse_mode="html")
            return

        try:
            await client.delete_messages(
                entity=event.chat_id,
                message_ids=[reply.id],
                revoke=True
            )
            await event.delete()
        except Exception as e:
            await client.send_message(
                "me",
                f"⚠️ <b>.del buyrug‘ida xatolik:</b>\n<code>{str(e)}</code>",
                parse_mode="html"
            )

    client.add_event_handler(clear_handler, events.NewMessage(outgoing=True, pattern=r'^\.clear(?:\s+.+)?$'))
    client.add_event_handler(del_handler, events.NewMessage(outgoing=True, pattern=r'^\.del$'))
    return client
