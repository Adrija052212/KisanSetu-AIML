import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DATA_GOV_API_KEY")

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"

url = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 1,
    "offset": 0,
}

print("Testing AGMARKNET API...")

try:
    response = requests.get(
        url,
        params=params,
        timeout=(10, 60)
    )

    print("Status:", response.status_code)
    print("URL:", response.url)

    response.raise_for_status()

    data = response.json()

    print("\nTitle:")
    print(data.get("title"))

    print("\nTotal records:")
    print(data.get("total"))

    print("\nRecords:")
    print(data.get("records"))

except requests.exceptions.RequestException as e:
    print("\nREQUEST ERROR:")
    print(e)