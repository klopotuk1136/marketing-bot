from config import parser_vk_chat_id, logging_chat_id, vk_api_version
from utils import check_msg
import aiohttp
import asyncio


async def vk_api_call(method: str, token: str, session: aiohttp.ClientSession, **params):
    params["access_token"] = token
    params["v"] = vk_api_version

    async with session.get(f"https://api.vk.com/method/{method}", params=params) as resp:
        data = await resp.json()
        if "error" in data:
            raise RuntimeError(data["error"])
        return data["response"]


async def get_longpoll_server(token: str, session: aiohttp.ClientSession, logger):
    try:
        return await vk_api_call(
            "messages.getLongPollServer", token, session,
            lp_version=3, need_pts=1
        )
    except Exception as e:
        logger.exception("Failed to init client — skipping: %s", e)


async def get_user_name(user_id: int, token: str, session: aiohttp.ClientSession, logger):
    try:
        user = (await vk_api_call("users.get", token, session, user_ids=user_id))[0]
        return f"{user['first_name']} {user['last_name']}"
    except Exception as e:
        logger.exception("Error while retreaving user name: %s", e)
        return f"User {user_id}"


async def get_chat_title(peer_id: int, token: str, session: aiohttp.ClientSession):
    if peer_id < 2000000000:
        return None  # private dialog
    chat_id = peer_id - 2000000000
    try:
        chat = await vk_api_call("messages.getChat", token, session, chat_id=chat_id)
        return chat.get("title")
    except:
        return None


async def start_vk_parser(token: str, bot_name: str, llm_client, send_message_func=None, logger=None, verbose=False):
    """
    Async longpoll listener for ONE VK user account
    """
    logger.info(f"[{bot_name}] starting VK parser...")

    async with aiohttp.ClientSession() as session:

        lp = await get_longpoll_server(token, session, logger)
        if lp is None:
            logger.warn(f"Client with name {bot_name} has some issues")
            message = f"VK Client has some issues\nname: {bot_name}\nPlease generate a new Token in the spreadsheet"
            await send_message_func(message, logging_chat_id) # Отправляем лог в канал с логами
            return None
        logger.info(f"Client with name {bot_name} is created")
        key = lp["key"]
        server = lp["server"]
        ts = lp["ts"]

        logger.info(f"[{bot_name}] Longpoll connected.")

        while True:
            try:
                async with session.get(
                    f"https://{server}",
                    params={
                        "act": "a_check",
                        "key": key,
                        "ts": ts,
                        "wait": 25,
                        "mode": 2,
                        "version": 3,
                    },
                    timeout=30,
                ) as resp:

                    data = await resp.json()

                    if "failed" in data:
                        if data["failed"] == 1:
                            ts = data["ts"]
                            continue
                        else:
                            lp = await get_longpoll_server(token, session, logger)
                            if lp is None:
                                logger.warn(f"Client with name {bot_name} has some issues")
                                message = f"VK Client has some issues\nname: {bot_name}\nPlease generate a new Token in the spreadsheet"
                                await send_message_func(message, logging_chat_id) # Отправляем лог в канал с логами
                                return None
                            key = lp["key"]
                            server = lp["server"]
                            ts = lp["ts"]
                            continue

                    ts = data["ts"]

                    for upd in data.get("updates", []):
                        if upd[0] == 4:  # message
                            msg_id = upd[1]
                            flags = upd[2]
                            peer_id = upd[3]
                            timestamp = upd[4]
                            msg_text = upd[5]
                            from_id = upd[6] if len(upd) > 6 else None
                            if from_id:
                                from_id = int(from_id['from'])

                            sender_name = await get_user_name(from_id, token, session, logger)
                            chat_title = await get_chat_title(peer_id, token, session)

                            logger.info(f"\n[{bot_name}] NEW MESSAGE")
                            logger.info(f"From: {sender_name} ({from_id})")
                            logger.info(f"Chat: {chat_title} ({peer_id})")
                            logger.info(f"Text: {msg_text}")

                            is_msg_relevant = check_msg(llm_client, msg_text)
        
                            if is_msg_relevant:
                                if verbose:
                                    logger.info(f"Found a relevant message: {msg_text}")
                                msg_header = f'Message in VK Chat\n{chat_title}'
                                
                                acc_info = f'VK account name: {bot_name}'
                                user_info = f'The author of the message: {sender_name}'

                                post = f'{msg_header}\n\n{acc_info}\n\n{user_info}\n\n"{msg_text}"'
                                    
                                # Отправляем в основной канал
                                await send_message_func(post, parser_vk_chat_id)
                            else:
                                if verbose:
                                    logger.info(f"Found an irrelevant message: {msg_text}")

            except Exception as e:
                logger.info(f"[{bot_name}] Error: {e}")
                message = f"VK Client has some issues\nname: {bot_name}\n Error: {e}\n"
                await send_message_func(message, logging_chat_id)
                await asyncio.sleep(3)