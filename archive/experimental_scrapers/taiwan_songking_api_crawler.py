import requests
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from time import sleep

# 檔案路徑設定
COMPANY_LIST_FILE = "company_list.json"
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# 取得公司清單 API (範例URL，請視實際情況調整)
COMPANY_LIST_API = "https://song.corp.com.tw/api/Song/GetCompanyList"

# 取得歌曲列表 API (範例URL)
SONG_LIST_API = "https://song.corp.com.tw/api/Song/Search"

# 並行數量
MAX_WORKERS = 10

lock = threading.Lock()

def save_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def fetch_company_list():
    print("取得公司清單中...")
    res = requests.get(COMPANY_LIST_API)
    res.raise_for_status()
    data = res.json()
    save_json(data, COMPANY_LIST_FILE)
    print(f"公司清單取得，共 {len(data)} 筆")
    return data

def fetch_songs(company_id, company_name):
    print(f"開始抓取公司：{company_name} ({company_id})")
    page = 1
    page_size = 50
    all_songs = []

    while True:
        params = {
            "company": company_id,
            "keyword": "",
            "page": page,
            "pageSize": page_size
        }
        try:
            res = requests.get(SONG_LIST_API, params=params, timeout=15)
            res.raise_for_status()
            result = res.json()

            songs = result.get("Data", [])
            if not songs:
                print(f"公司 {company_name} 第 {page} 頁無資料，結束抓取")
                break

            all_songs.extend(songs)
            print(f"公司 {company_name} 第 {page} 頁，共 {len(songs)} 首歌")

            page += 1
            sleep(0.1)  # 請求間隔可調整

        except Exception as e:
            print(f"錯誤：{company_name} 第 {page} 頁抓取失敗，錯誤：{e}")
            break

    # 儲存公司歌曲資料
    filename = os.path.join(DATA_DIR, f"{company_id}_{company_name}.json")
    with lock:
        save_json(all_songs, filename)
    print(f"公司 {company_name} 歌曲資料儲存完成，共 {len(all_songs)} 首歌")

def main():
    # 先取得公司清單
    companies = load_json(COMPANY_LIST_FILE)
    if not companies:
        try:
            companies = fetch_company_list()
        except Exception as e:
            print("無法取得公司清單:", e)
            return

    # companies 預期格式為 list of dict，有 "Id" 與 "Name" 欄位
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for comp in companies:
            company_id = comp.get("Id")
            company_name = comp.get("Name")
            if company_id and company_name:
                futures.append(executor.submit(fetch_songs, company_id, company_name))

        for future in futures:
            future.result()  # 等待所有任務完成

    print("所有公司歌曲抓取完成！")

if __name__ == "__main__":
    main()
