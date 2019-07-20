import speedtest
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
import gspread
import datetime

def speedtest_results():
    servers = []
    # If you want to test against a specific server
    # servers = [1234]

    threads = None
    # If you want to use a single threaded test
    # threads = 1

    s = speedtest.Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    s.download(threads=threads)
    s.upload(threads=threads)
    s.results.share()

    results_dict = s.results.dict()

    return results_dict

def get_network_status_data():
    results_dict = speedtest_results()
    upload,download,ping = 0,0,0
    upload=round(results_dict["download"]/(10**6),2)
    download=round(results_dict["upload"]/(10**6),2)
    ping = round(results_dict["ping"],2)
    time = results_dict["timestamp"]
    # print(upload)
    # print(download)
    # print(ping)
    column_list = [download,upload,ping]
    return column_list

def load_spread_sheet():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    json_file = 'raspi-56a886c9c4f1.json'#OAuth用クライアントIDの作成でダウンロードしたjsonファイル
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scopes=scopes)
    http_auth = credentials.authorize(Http())

    # スプレッドシート用クライアントの準備
    doc_id = '1n6MuYkKRViTPGUJQX9V4GIFXZo5j1EvQkYXNqNL3nFM'#これはスプレッドシートのURLのうちhttps://docs.google.com/spreadsheets/d/以下の部分です
    client = gspread.authorize(credentials)
    gfile   = client.open_by_key(doc_id)#読み書きするgoogle spreadsheet
    return gfile

def add_new_sheet(date_today):
    gfile = load_spread_sheet()
    worksheet = gfile.add_worksheet(title=date_today, rows="300", cols="20")
    # write columns
    worksheet.update_acell('A1','time')
    worksheet.update_acell('B1', 'download')
    worksheet.update_acell('C1','upload')
    worksheet.update_acell('D1','ping')

    return worksheet

def load_sheet(date_today):
    gfile = load_spread_sheet()
    worksheet = gfile.worksheet(date_today)
    return worksheet

# 日付のWorksheetがなけらば作成する．あればロードする
def create_or_load_worksheet(date_today):
    try:
        worksheet = add_new_sheet(date_today)
        print("new_sheet")
    except:
        worksheet = load_sheet(date_today)
        print("load_sheet")

    return worksheet

def upload_network_status_data():
    date_today = str(datetime.date.today())
    worksheet = create_or_load_worksheet(date_today)
    now_time = datetime.datetime.now().strftime("%H:%M:%S")

    column_list = get_network_status_data()
    column_list.insert(0,now_time)
    # column_list = [11,22,33,44]
    worksheet.append_row(column_list)

if __name__ == "__main__":
    # selecting_data()
    upload_network_status_data()