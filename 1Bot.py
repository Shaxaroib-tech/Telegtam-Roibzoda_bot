import os, logging, asyncio
from datetime import datetime
from telethon import TelegramClient, events

logging.basicConfig(level=logging.INFO)

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
BOT_TOKEN = os.environ['BOT_TOKEN']

client = TelegramClient('user_session', API_ID, API_HASH)
bot = TelegramClient('bot_session', API_ID, API_HASH)
cache = {}

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if event.out: return
    msg = event.message
    sender = await event.get_sender()
    name = sender.first_name or 'Unknown'
    chat = await event.get_chat()
    title = getattr(chat, 'title', 'личка')

    cache[msg.id] = {'text': msg.text or '', 'sender': name, 'chat': title}

    if msg.media and hasattr(msg.media, 'ttl_seconds') and msg.media.ttl_seconds:
        fname = f"disappearing_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}"
        path = await msg.download_media(file=fname)
        await bot.send_file('me', path, caption=f"🔥 Одноразовое от {name}")
        os.remove(path)
        logging.info(f'Сохранено одноразовое от {name}')

@client.on(events.MessageDeleted)
async def del_handler(event):
    for mid in event.deleted_ids:
        if mid in cache:
            data = cache.pop(mid)
            await bot.send_message('me', f"🗑️ Удалено от {data['sender']} из {data['chat']}:\n{data['text'] or '[медиа]'}")

async def main():
    await client.start()
    await bot.start(bot_token=BOT_TOKEN)
    logging.info("Бот-перехватчик активирован")
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
