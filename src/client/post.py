# %%
import requests

url = "http://127.0.0.1:8000/predict"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

data = {
    "place": "函館",
    "number": 11,
    "name": "UHB杯"
}

response = requests.post(url,
                         headers=headers,
                         json=data)

print(response.status_code)
print(response.json())
