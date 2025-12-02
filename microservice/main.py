import asyncio
import logging

from telegram_parser import create_tg_parser_tasks
from vk_parser import create_vk_parser_tasks
from bot_sender import bot_sender, send_message
from utils import create_logger
from llm import get_openai_client

from config import api_id, api_hash, bot_token, openai_api_key, verbose, logging_chat_id, tg_parser_enabled, vk_parser_enabled
if verbose:
    logging_level = logging.INFO
else:
    logging_level = logging.WARN
logger = create_logger('MarketingMsgTracker', level=logging_level)

openai_client = get_openai_client(openai_api_key)

async def main():
    bot = await bot_sender("bot_session", api_id, api_hash, bot_token, logger)
    def send_message_func(m, cid):
        return send_message(bot, logger, m, cid)
    await send_message_func("Starting the parser...",logging_chat_id)

    tasks = []

    if tg_parser_enabled:
        tg_tasks = create_tg_parser_tasks(
            api_id=api_id,
            api_hash=api_hash,
            llm_client=openai_client,
            send_message_func=send_message_func,
            logger=logger
            )
        tasks.extend(tg_tasks)
    else:
        logger.info("TG parsing is disabled")
    
    if vk_parser_enabled:
        vk_tasks = create_vk_parser_tasks(
            llm_client=openai_client,
            send_message_func=send_message_func,
            logger=logger
        )
        tasks.extend(vk_tasks)
    else:
        logger.info("VK parsing is disabled")

    if len(tasks) == 0:
        logger.error("The number of tasks created is zero")
        return

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())