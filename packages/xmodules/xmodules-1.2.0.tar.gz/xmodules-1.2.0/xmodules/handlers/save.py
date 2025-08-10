# xmodules/handlers/save.py

import os
from telethon import TelegramClient, events


def register_save_handler(client: TelegramClient, admin_id: int):
    """
    View-once media-ni saqlab qo‘yadigan handler.
    """

    async def save_handler(event):
        if event.sender_id != admin_id:
            return

        reply = await event.get_reply_message()
        await event.delete()

        if not reply or not reply.media:
            await client.send_message(
                "me",
                "⚠️ <b>Vaqtinchalik media faylga reply qilinmagan yoki media fayl mavjud emas.</b>",
                parse_mode="html",
            )
            return

        try:
            folder = "media"
            os.makedirs(folder, exist_ok=True)
            file_path = await client.download_media(reply.media, file=f"{folder}/")
            await client.send_file("me", file_path)
            os.remove(file_path)
        except Exception as e:
            await client.send_message(
                "me",
                f"⚠️ <b>Xatolik:</b>\n\n<code>{str(e)}</code>",
                parse_mode="html",
            )

    client.add_event_handler(save_handler, events.NewMessage(outgoing=True, pattern=r'^\.ok$'))
    return client