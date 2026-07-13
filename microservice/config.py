import os
from dotenv import load_dotenv

load_dotenv()
# Параметры для ботов
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN') # Бот из @BotFather


# parser_chat_id = int(os.environ.get('PARSER_CHAT_ID')) # id канала куда будут сливаться
# parser_chat_id_2 = int(os.environ.get('PARSER_CHAT_ID_2')) # id канала куда будут сливаться
# parser_chat_all_id = int(os.environ.get('PARSER_CHAT_ALL_MESSAGES_ID')) # id канала куда будут сливаться остальные
# parser_vk_chat_id = int(os.environ.get('PARSER_VK_CHAT_ID'))
# logging_chat_id = int(os.environ.get('LOGGING_CHAT_ID'))
parser_chat_ids = [
    -1002903950429,
    -1003516813629
]
parser_chat_all_id = -1003765011762
parser_vk_chat_id = -1003237099041
logging_chat_id = -1003002833000

parser_chat_visa_id = -1003898203212

tg_parser_enabled = True
# VK
vk_api_version = "5.131"

vk_parser_enabled = False

# Параметры для LLM
openai_api_key = os.environ.get("OPENAI_API_KEY")

# Logging parameter
verbose = True
google_credentials_path = "google-credentials.json"
