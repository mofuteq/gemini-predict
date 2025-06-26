# %%
import requests

url = "http://127.0.0.1:8000/prediction"

params = {
    "place": "小倉",
    "number": 11,
    "name": "佐世保S"
}

headers = {
    "accept": "application/json"
}

response = requests.get(url, params=params, headers=headers)

print(response.status_code)
print(response.json())

# %%
