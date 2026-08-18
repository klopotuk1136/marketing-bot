import logging
import sys
from llm import check_message_relevancy_with_llm, parse_json, parse_bool
from config import verbose, parser_chat_ids, parser_vk_chat_id, parser_chat_all_id, logging_chat_id
from enum import Enum

class RejectionReason(Enum):
    EMPTY = 1
    BLACKLIST = 2
    LLM = 3
    MSG_LENGTH = 4
    OK = 0

def create_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s \n%(message)s \n' + '-'*30)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    #file_handler = logging.FileHandler('info.log')
    #file_handler.setFormatter(formatter)

    logger.addHandler(handler)
    #logger.addHandler(file_handler)
    return logger

def check_msg_len(text):
    if len(text.split(' ')) <= 3:
        return False
    return True

def check_pattern_func(text, whitelist, blacklist, strict_blacklist_check):
    lower_text_words = text.lower().split(' ')

    counter = 0

    for key in whitelist:
        for word in lower_text_words:
            if key in word:
                counter += 3
    for key in blacklist:
        for word in lower_text_words:
            if key in word:
                counter -= 1
    if strict_blacklist_check:
        return counter > 0
    else:
        return counter >= 0

def check_msg_with_llm(client, msg_text, llm_prompt):
    llm_response = check_message_relevancy_with_llm(client, msg_text, llm_prompt)
    result_json = parse_json(llm_response)
    return parse_bool(result_json.get('is_relevant'))

def check_msg(llm_client, msg, whitelist, blacklist, llm_prompt, strict_blacklist_check=True):

    if len(msg) == 0:
        return False, RejectionReason.EMPTY

    if not check_msg_len(msg):
        return False, RejectionReason.MSG_LENGTH
    
    if not check_pattern_func(msg, whitelist, blacklist, strict_blacklist_check):
        return False, RejectionReason.BLACKLIST
    
    is_relevant = check_msg_with_llm(llm_client, msg, llm_prompt)
    if is_relevant is None:
        return True, RejectionReason.OK
    elif is_relevant:
        return is_relevant, RejectionReason.OK
    else:
        return is_relevant, RejectionReason.LLM

our_chats_list_default = parser_chat_ids + [parser_chat_all_id, parser_vk_chat_id, logging_chat_id]

def is_msg_from_our_chat(chat_id, our_chats_list: list = our_chats_list_default):
    for our_chat_id in our_chats_list:
        if str(chat_id) == str(our_chat_id) or '-100'+str(chat_id) == str(our_chat_id):
            return True
    return False


async def compose_and_send_msg(msg_text, chat, event, bot_name, bot_phone, send_chat_id,
                    send_message_func=None, logger=None):
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
    await send_message_func(post, send_chat_id)
    