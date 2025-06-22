# %%
import requests

url = "http://127.0.0.1:8000/win5"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}

response = requests.get(url,
                        headers=headers,)

print(response.status_code)
print(response.json())

# %%
