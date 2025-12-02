from telethon import TelegramClient, events
from config import parser_chat_id, logging_chat_id, verbose
from telethon.errors.rpcerrorlist import AuthKeyUnregisteredError
import asyncio
from gdrive_connector import get_tg_bots_metadata
from utils import check_msg
from telethon.sessions import StringSession

async def get_authorized_client(session, api_id, api_hash, logger, **kwargs):
    """
    Return a connected & authorized client or None.
    Never triggers interactive login.
    """
    
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

async def start_telegram_parser(session, api_id, api_hash, bot_phone, bot_name, llm_client,
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

    @client.on(events.NewMessage(chats=None))
    async def handler(event):
        '''Забирает сообщения из телеграмм каналов и посылает их в наш канал'''
        chat = await event.get_chat()
        if str(chat.id) == str(parser_chat_id) or '-100'+str(chat.id) == str(parser_chat_id):
            return

        msg_text = event.raw_text
        if msg_text == '':
            return

        user_name = event.post_author
        # Флаг, показывающий, прошло ли сообщение фильтрацию
        is_msg_relevant = False

        is_msg_relevant = check_msg(llm_client, msg_text)
        
        if is_msg_relevant:
            if verbose:
                logger.info(f"Found a relevant message: {msg_text}")
            source = getattr(chat, "title", "")
            if source.find('t.me') != -1:
                link = f'{source}/{event.message.id}'
                channel = '@' + source.split('/')[-1]
                msg_header = f'<b>{channel}</b>\n{link}'
            else:
                msg_header = f'Message in Private channel\n{source}'
            
            acc_info = f'Telegram account name: {bot_name}, phone: {bot_phone}'
            #user_info = f'The author of the message: {user_name}'

            post = f'{msg_header}\n\n{acc_info}\n\n"{msg_text}"'
                
            # Отправляем в основной канал
            await send_message_func(post, parser_chat_id)
        else:
            if verbose:
                logger.info(f"Found an irrelevant message: {msg_text}")


    await client.run_until_disconnected()

def create_tg_parser_tasks(api_id, api_hash, llm_client, send_message_func, logger):
    tasks = []
    for meta in get_tg_bots_metadata():
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
                    send_message_func=send_message_func,
                    logger=logger
                )
            ))
        except KeyError as e:
            logger.error(e)
    
    return tasks