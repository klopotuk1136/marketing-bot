import logging
import sys
from llm import check_message_relevancy_with_llm, parse_json, parse_bool
from config import words_whitelist, words_blacklist
from enum import Enum

class RejectionReason(Enum):
    EMPTY = 1
    BLACKLIST = 2
    LLM = 3
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

def check_pattern_func(text):
    lower_text_words = text.lower().split(' ')

    counter = 0

    for key in words_whitelist:
        for word in lower_text_words:
            if key in word:
                counter += 3
    for key in words_blacklist:
        for word in lower_text_words:
            if key in word:
                counter -= 1
    return counter > 0

def check_msg_with_llm(client, msg_text):
    llm_response = check_message_relevancy_with_llm(client, msg_text)
    result_json = parse_json(llm_response)
    return parse_bool(result_json.get('is_relevant'))

def check_msg(llm_client, msg):

    if len(msg) == 0:
        return False, RejectionReason.EMPTY
    
    if not check_pattern_func(msg):
        return False, RejectionReason.BLACKLIST
    
    is_relevant = check_msg_with_llm(llm_client, msg)
    if is_relevant is None:
        return True, RejectionReason.OK
    elif is_relevant:
        return is_relevant, RejectionReason.OK
    else:
        return is_relevant, RejectionReason.LLM
    