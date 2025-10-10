from telethon import TelegramClient

async def bot_sender(session, api_id, api_hash, bot_token,
               logger=None, loop=None):
    bot = TelegramClient(session, api_id, api_hash,
                        base_logger=logger, loop=loop)
    await bot.start(bot_token=bot_token)
    return bot


async def send_message(bot, logger, text, chat_id):
    '''Отправляет посты в канал через бот'''
    await bot.send_message(entity=chat_id,
                        parse_mode='html', link_preview=False, message=text)

    logger.info(text)
