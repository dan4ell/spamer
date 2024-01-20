import asyncio
from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import GetContactsRequest
from settings import *
from telethon import connection
import aiohttp
import os

send_messages = {}
useless_users = []


async def send_to_dialogs(client, channel_text=message_text, channel_media=None):
    dialogs = await client.get_dialogs()
    send_messages[client] = 0
    sem = asyncio.Semaphore(sema)  # Устанавливаем максимальное количество одновременных отправок
    tasks = []
    for dialog in dialogs:
        task = send_message_to_dialog(client, dialog.id, sem, channel_text, channel_media)  # Передаем семафор
        tasks.append(task)
    await asyncio.gather(*tasks)

async def send_message_to_dialog(client, dialog_id, sem, channel_text=message_text, channel_media=None):
    me = await client.get_me()
    async with sem:  # Используем семафор для ограничения одновременных вызовов
        try:
            if channel_media is not None:
                await client.send_file(dialog_id, channel_media, caption=channel_text)
            else:
                await client.send_message(dialog_id, channel_text)
            useless_users.append(dialog_id)
            send_messages[client] += 1
            if sema == 1:
                print(f'{me.phone} отправлено сообщений: {send_messages[client]}')
            if sema > 1:
                print(f'{me.phone} пачка отправлена: {send_messages[client]}')
            await asyncio.sleep(timeout)
        except Exception as e:
            print(f'{me.phone}, {e}')

async def send_message_to_contact(client, contact, sem, channel_text=message_text, channel_media=None):
    me = await client.get_me()
    async with sem:
        try:
            if channel_media is not None:
                await client.send_file(contact.user_id, channel_media)
            else:
                pass
            await client.send_message(contact.user_id, channel_text)
            send_messages[client] += 1
            if sema == 1:
                print(f'{me.phone} отправлено сообщений: {send_messages[client]}')
            if sema > 1:
                print(f'{me.phone} пачка отправлена: {send_messages[client]}')
            await asyncio.sleep(timeout)
        except Exception as e:
            print(f'{me.phone}, {e}')


async def get_contacts(client, channel_text=message_text, channel_media=None):
        result = await client(GetContactsRequest(0))  # Получение списка контактов
        contacts = result.contacts
        me = await client.get_me()
        print(f'{me.phone} НАЧИНАЮ РАССЫЛАТЬ КОНТАКТЫ')
        tasks = []
        sem = asyncio.Semaphore(sema)
        for contact in contacts:
            if contact.user_id not in useless_users:
                task = send_message_to_contact(client, contact, sem, channel_text, channel_media)
                tasks.append(task)
            else:
                continue
        await asyncio.gather(*tasks)

async def process_session(session_file):
    async with TelegramClient(session_file, api_id=123, api_hash='<KEY>',
                            proxy=proxy) as client:
        await client.start()
        me = await client.get_me()
        print(f'{me.phone} сессия открыта.')
        channel_media = ''
        if channel_link != "":
            channel = await client.get_entity(channel_link)
            async for message in client.iter_messages(channel, reverse=True):
                if message.text and message.media:
                    channel_text = message.text
                    channel_media = message.media

            await asyncio.gather(send_to_dialogs(client, channel_text, channel_media))
            await asyncio.gather(get_contacts(client, channel_text, channel_media))
        else:
            await asyncio.gather(send_to_dialogs(client))
            await asyncio.gather(get_contacts(client))

async def main():
    session_files = [os.path.splitext(f)[0] for f in os.listdir('.') if f.endswith('.session')]
    print(session_files)
    tasks = [process_session(session) for session in session_files]
    await asyncio.gather(*tasks)
    print('Спам завершён.')


if __name__ == '__main__':
    asyncio.run(main())