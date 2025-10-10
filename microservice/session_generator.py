from telethon.sync import TelegramClient
from telethon.sessions import StringSession

from config import api_id, api_hash


with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("SESSION_STRING=", client.session.save())