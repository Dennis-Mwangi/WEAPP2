import requests

BASE_URL = "http://127.0.0.1:8000"
USERNAME = "user@example.com"      # change to your user
PASSWORD = "password123"           # change to your password

def get_token():
    login_data = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(f"{BASE_URL}/token", data=login_data)
    if response.status_code != 200:
        raise Exception("Login failed: " + response.text)
    return response.json()["access_token"]

def get_favorites(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/favorites", headers=headers)
    return response.json()

if __name__ == "__main__":
    token = get_token()
    favorites = get_favorites(token)
    print("⭐ Favorite Cities:")
    for fav in favorites:
        print("-", fav["city"])
