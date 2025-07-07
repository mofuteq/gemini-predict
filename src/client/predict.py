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
    {"place": "函館", "number": 11, "name": "大沼S"},
    {"place": "小倉", "number": 11, "name": "北九州記念"},
    {"place": "福島", "number": 11, "name": "ジュライS"}
]

for request_data in requests_datas:
    res = requests.get(url=url,
                       params=request_data)
    print(res)
