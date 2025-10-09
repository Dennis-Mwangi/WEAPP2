import requests
from datetime import timedelta


# ===== CONFIG =====
BASE_URL = "http://127.0.0.1:8000"
USERNAME = "admin@example.com"
PASSWORD = "admin123"

# ==================

def get_token():
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(f"{BASE_URL}/token", data=login_data)
    if response.status_code != 200:
        print("❌ Login failed:", response.text)
        return None
    token = response.json().get("access_token")
    print(f"✅ Logged in as {USERNAME}")
    print("Token:", token)
    print("Last login:", response.json().get("last_login"))
    return token


def get_logins(token):
    headers = {"Authorization": f"Bearer {token}"}

    # 🔹 CHANGED: Use /logins/all instead of /logins to get all usernames
    response = requests.get(f"{BASE_URL}/logins/all", headers=headers)

    if response.status_code != 200:
        print("❌ Failed to fetch logins:", response.text)
        return

    print("\n📜 All Logins:")

    # 🔹 CHANGED: Updated loop to match backend list format
    for login in response.json().get("logins", []):
        print(f" - {login['username']} → {login['last_login']}")


if __name__ == "__main__":
    token = get_token()
    if token:
        get_logins(token)
