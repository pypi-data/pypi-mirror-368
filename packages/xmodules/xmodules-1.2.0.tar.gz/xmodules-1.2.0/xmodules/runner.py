# xmodules/runner.py

import asyncio
from xmodules.session import create_or_load_session
from xmodules.handlers import handlers


def run(api_id: int, api_hash: str, admin_id: int):
    """
    XModulesni ishga tushirish.
    """

    async def main():
        client = await create_or_load_session(api_id, api_hash)

        for handler in handlers:
            handler(client, admin_id=admin_id)

        await client.start()
        await client.send_message("me", "✅ <b>XModules ishga tushdi.</b>\n\n@XModules", parse_mode='html')
        await client.run_until_disconnected()

    asyncio.run(main())
