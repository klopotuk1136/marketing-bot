import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import google_credentials_path

# Define scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name(google_credentials_path, scope)
    client = gspread.authorize(creds)
    return client

def get_tg_bots_metadata():
    client = get_client()
    sheet = client.open("Liga znaniy TG Bot tokens").sheet1
    data = sheet.get_all_records()
    return data

def get_vk_bots_metadata():
    client = get_client()
    sheet = client.open("Liga znaniy TG Bot tokens").get_worksheet(1)
    data = sheet.get_all_records()
    return data

