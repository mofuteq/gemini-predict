# %%
import os
import requests
from dotenv import load_dotenv

# .env ファイルの読み込み
load_dotenv("../../.env")

API_ENDPOINT = os.getenv("API_END_POINT")
if not API_ENDPOINT:
    raise ValueError("API_END_POINT が .env に定義されていません。")

url = f"{API_ENDPOINT}/prediction"

requests_datas = [
    {"place": "函館", "number": 11, "name": "函館記念"},
    {"place": "小倉", "number": 11, "name": "佐世保S"},
    {"place": "福島", "number": 11, "name": "ラジオNIKKEI賞"}
]

for request_data in requests_datas:
    res = requests.get(url=url,
                       params=request_data)
    print(res)
