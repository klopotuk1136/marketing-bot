import asyncio
import logging

from telegram_parser import start_telegram_parser
from vk_parser import start_vk_parser
from bot_sender import bot_sender, send_message
from utils import create_logger
from gdrive_connector import get_tg_bots_metadata, get_vk_bots_metadata
from llm import get_openai_client

from config import api_id, api_hash, bot_token, openai_api_key, verbose, logging_chat_id
if verbose:
    logging_level = logging.INFO
else:
    logging_level = logging.WARN
logger = create_logger('MarketingMsgTracker', level=logging_level)
tele_logger = logger

openai_client = get_openai_client(openai_api_key)

async def main():
    bot = await bot_sender("bot_session", api_id, api_hash, bot_token, tele_logger)
    def send_message_func(m, cid):
        return send_message(bot, tele_logger, m, cid)
    await send_message_func("Starting the parser...",logging_chat_id)

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
                    llm_client=openai_client,
                    send_message_func=send_message_func,
                    logger=tele_logger,
                    verbose=verbose
                )
            ))
        except KeyError as e:
            logger.error(e)
    
    for meta in get_vk_bots_metadata():
        try:
            access_token = meta["AccessToken"].strip()
            bot_name = meta["Name"]
            if bot_name is None or len(bot_name) == 0 or access_token is None or len(access_token) == 0:
                continue
            tasks.append(asyncio.create_task(
                start_vk_parser(
                    token=access_token,
                    bot_name=bot_name,
                    send_message_func=send_message_func,
                    llm_client=openai_client,
                    logger=tele_logger
                )
            ))
        except KeyError as e:
            logger.error(e)
            
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())