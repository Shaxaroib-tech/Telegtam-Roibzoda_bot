import os
import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient, events

logging.basicConfig(level=logging.INFO)

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
BOT_TOKEN = os.environ['BOT_TOKEN']

client = TelegramClient('user_session', API_ID, API_HASH)
bot = TelegramClient('bot_session', API_ID, API_HASH)

MESSAGE_CACHE = {}

@client.on(events.NewMessage(incoming=True))
async def save_incoming(event):
    if event.out:
        return
    msg = event.message
    chat = await event.get_chat()
    sender = await event.get_sender()
    sender_name = sender.first_name or 'Неизвестный'

    MESSAGE_CACHE[msg.id] = {
        'text': msg.text or '',
        'sender': sender_name,
        'date': msg.date,
        'chat_title': getattr(chat, 'title', 'личка')
    }

    # Одноразовые медиа
    if msg.media and hasattr(msg.media, 'ttl_seconds') and msg.media.ttl_seconds:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"disappearing_{timestamp}_{sender_name}"
        file_path = await msg.download_media(file=filename)
        await bot.send_file('me', file_path, caption=f"🔥 Одноразовое от {sender_name}")
        os.remove(file_path)
        logging.info(f'Сохранено одноразовое от {sender_name}')

@client.on(events.MessageDeleted)
async def deleted_handler(event):
    for msg_id in event.deleted_ids:
        if msg_id in MESSAGE_CACHE:
            data = MESSAGE_CACHE.pop(msg_id)
            text = data['text'] or '[медиа]'
            await bot.send_message(
                'me',
                f"🗑️ Удалено сообщение от {data['sender']} из {data['chat_title']}:\n{text}"
            )
            logging.info(f'Перехвачено удалённое: {text[:30]}...')

async def main():
    await client.start()
    await bot.start(bot_token=BOT_TOKEN)
    logging.info("Бот-перехватчик запущен")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
