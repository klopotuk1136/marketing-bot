import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_client():
    creds = ServiceAccountCredentials.from_json_keyfile_name("liga_znaniy_credentials.json", scope)
    client = gspread.authorize(creds)
    return client

def get_bots_metadata():
    client = get_client()
    sheet = client.open("Liga znaniy TG Bot tokens").sheet1
    data = sheet.get_all_records()
    return data

