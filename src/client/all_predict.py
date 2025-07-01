# %%
import os
import time
import requests
import schedule
from dotenv import load_dotenv
from datetime import datetime

# .envファイルの読み込み
load_dotenv("../../.env")

API_ENDPOINT = os.getenv("API_END_POINT")
if not API_ENDPOINT:
    raise ValueError("API_END_POINT が .env に定義されていません。")

PREDICTION_URL = f"{API_ENDPOINT}/prediction"
WIN5_URL = f"{API_ENDPOINT}/win5"

HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json"
}


def fetch_predictions():
    print(f"\n=== {datetime.now()} - /prediction 実行開始 ===")
    requests_data = [
        {"place": "函館", "number": 11, "name": "TVh杯"},
        {"place": "小倉", "number": 11, "name": "マレーシアC"},
        {"place": "福島", "number": 11, "name": "TUF杯"}
    ]

    with requests.Session() as session:
        session.headers.update({"accept": "application/json"})

        for data in requests_data:
            try:
                response = session.get(PREDICTION_URL, params=data)
                response.raise_for_status()
                print(f"{data['name']} の予測:")
                print(response.json())
            except requests.RequestException as e:
                print(f"❌ {data['name']} の取得に失敗:", e)


def fetch_win5():
    print(f"\n=== {datetime.now()} - /win5 実行開始 ===")

    try:
        with requests.Session() as session:
            response = session.get(WIN5_URL, headers=HEADERS)
            response.raise_for_status()
            print("✅ /win5 結果:")
            print(response.json())
    except requests.RequestException as e:
        print("❌ /win5 の取得に失敗:", e)


def run_all():
    fetch_predictions()
    fetch_win5()


# 毎日15:00に両方のAPIを実行
schedule.every().day.at("14:45").do(run_all)

print("スケジューラーを起動しました。毎日15:00に /prediction と /win5 を実行します。")

# スケジューラーのループ
while True:
    schedule.run_pending()
    time.sleep(1)
# %%


