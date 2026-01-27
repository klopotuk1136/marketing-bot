import logging
import sys
from llm import check_message_relevancy_with_llm, parse_json
from config import words_whitelist, words_blacklist

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
    return result_json.get('is_relevant')

def check_msg(llm_client, msg):

    if len(msg) == 0:
        return False
    
    if not check_pattern_func(msg):
        return False
    
    # is_relevant = check_msg_with_llm(llm_client, msg)
    # if is_relevant is not None:
    #     return is_relevant
    else:
        return True
    