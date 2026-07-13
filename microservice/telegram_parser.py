from telethon import TelegramClient, events
from config import parser_chat_ids, logging_chat_id, parser_chat_visa_id
from telethon.errors.rpcerrorlist import AuthKeyUnregisteredError
import asyncio
from gdrive_connector import get_tg_bots_metadata
from utils import is_msg_from_our_chat
from telethon.sessions import StringSession
from intent_identifiers.university_helper import check_and_handle_msg_university

async def get_authorized_client(session, api_id, api_hash, logger, **kwargs):
    try:
        string_session = StringSession(session)
        client = TelegramClient(string_session, api_id, api_hash, **kwargs)
        await client.connect()  # no prompt
        if await client.is_user_authorized():
            #logger.info("Session is authorized — proceeding.")
            return client
        else:
            #logger.warning("Session requires login — skipping this user.")
            await client.disconnect()
            return None
    except AuthKeyUnregisteredError:
        logger.warning("Auth key unregistered/revoked — skipping this user.")
    except ValueError as e:
        logger.warning("Invalid/corrupted StringSession — skipping: %s", e)
    except Exception as e:
        logger.exception("Failed to init client — skipping: %s", e)

    try:
        await client.disconnect()
    except Exception:
        pass
    return None

async def start_telegram_parser(session, api_id, api_hash, bot_phone, bot_name, llm_client, chat_number,
                    send_message_func=None, logger=None, system_version="4.16.30-vxCUSTOM"
                    ):
    '''Телеграм парсер'''
    logger.info(f"Creating client with name {bot_name}")
    
    client = await get_authorized_client(session, api_id, api_hash, logger, system_version=system_version)
    if client is None:
        logger.warn(f"Client with name {bot_name} has some issues")
        message = f"Telegram Client has some issues\nname: {bot_name}\nphone: {bot_phone}\nPlease generate a new Token in the spreadsheet"
        await send_message_func(message, logging_chat_id) # Отправляем лог в канал с логами
        return None
    logger.info(f"Client with name {bot_name} is created")

    university_chat_id = parser_chat_ids[chat_number]

    @client.on(events.NewMessage(chats=None))
    async def handler(event):
        '''Забирает сообщения из телеграмм каналов и посылает их в наш канал'''
        chat = await event.get_chat()

        # if the msg is from our chat -> ignore it
        if is_msg_from_our_chat(chat.id):
            return

        msg_text = event.raw_text
        if msg_text == '':
            return

        # Scan the message if it contains relevant informations for university helper
        await check_and_handle_msg_university(
            msg_text, chat, event, bot_name, bot_phone, university_chat_id, send_message_func, llm_client, logger
        )
        # Scan the message if it contains relevant informations for visa helper
        await check_and_handle_msg_university(
            msg_text, chat, event, bot_name, bot_phone, parser_chat_visa_id, send_message_func, llm_client, logger
        )



    await client.run_until_disconnected()

def create_tg_parser_tasks(api_id, api_hash, llm_client, send_message_func, logger):
    tasks = []

    for i in range(len(parser_chat_ids)):

        for meta in get_tg_bots_metadata(i):
            try:
                session_string = meta["SessionString"].strip()
                bot_phone = meta["Phone"]
                bot_name = meta["Name"]
                if bot_name is None or len(bot_name) == 0 or session_string is None or len(session_string) == 0:
                    continue
                tasks.append(asyncio.create_task(
                    start_telegram_parser(
                        session=session_string,
                        api_id=api_id,
                        api_hash=api_hash,
                        bot_phone=bot_phone,
                        bot_name=bot_name,
                        llm_client=llm_client,
                        chat_number=i,
                        send_message_func=send_message_func,
                        logger=logger
                    )
                ))
            except KeyError as e:
                logger.error(e)
    
    return tasks