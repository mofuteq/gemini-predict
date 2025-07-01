# %%
import os
import requests
from dotenv import load_dotenv

# .env読み込み
load_dotenv("../../.env")

API_END_POINT = os.getenv("API_END_POINT")

url = f"{API_END_POINT}/win5"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

response = requests.get(url,
                        headers=headers,)

print(response.status_code)
print(response.json())

# %%
