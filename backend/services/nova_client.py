import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("NOVA_API_BASE_URL")
API_KEY = os.getenv("NOVA_API_KEY")


def get_master_data_changes(limit=5):
    url = f"{BASE_URL}/approvals"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }

    response = requests.get(
        url,
        headers=headers,
        params={"limit": limit},
        timeout=30,
    )

    print("Status code:", response.status_code)
    print("Response:")
    print(response.text[:5000])


if __name__ == "__main__":
    get_master_data_changes()