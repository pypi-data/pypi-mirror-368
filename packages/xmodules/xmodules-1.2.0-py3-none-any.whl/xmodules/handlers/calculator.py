# xmodules/handlers/calculator.py

import math
from telethon import TelegramClient, events


def register_calculator_handler(client: TelegramClient, admin_id: int):
    async def math_handler(event):
        if event.sender_id != admin_id:
            return

        expr = event.pattern_match.group(1)
        if not expr:
            await event.edit("⚠️ <b>Iltimos, hisoblash uchun ifoda kiriting!</b>", parse_mode="html")
            return

        try:
            allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
            allowed_names.update({"abs": abs, "round": round, "pow": pow})

            result = eval(expr, {"__builtins__": {}}, allowed_names)
            await event.edit(f"🧮 <b>Natija:</b> <code>{expr} = {result}</code>",
                             parse_mode="html")
        except Exception as e:
            await event.edit(f"❌ <b>Xatolik:</b>\n<pre>{e}</pre>", parse_mode="html")

    client.add_event_handler(math_handler, events.NewMessage(outgoing=True, pattern=r'^\.math(?: |$)(.+)?'))
    return client