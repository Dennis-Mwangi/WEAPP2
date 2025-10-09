import requests

BASE_URL = "http://127.0.0.1:8000"

def login(username: str, password: str) -> dict:
    """
    Logs in a user and returns a dict with access_token and status.
    """
    try:
        res = requests.post(
            f"{BASE_URL}/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=f"username={username}&password={password}"
        )
        if res.ok:
            return {"success": True, "access_token": res.json().get("access_token")}
        return {"success": False, "error": res.json().get("detail", "Login failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def register(username: str, password: str) -> dict:
    """
    Registers a new user.
    """
    try:
        res = requests.post(
            f"{BASE_URL}/register",
            json={"username": username, "password": password}
        )
        if res.ok:
            return {"success": True, "message": res.json().get("message")}
        return {"success": False, "error": res.json().get("detail", "Registration failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_weather(city: str, token: str) -> dict:
    """
    Fetches current weather for a city.
    """
    try:
        res = requests.get(
            f"{BASE_URL}/weather?city={city}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if res.ok:
            return res.json()
        return {"error": res.json().get("detail", "Could not fetch weather")}
    except Exception as e:
        return {"error": str(e)}

def get_forecast(city: str, token: str) -> dict:
    """
    Fetches forecast for a city.
    """
    try:
        res = requests.get(
            f"{BASE_URL}/forecast?city={city}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if res.ok:
            return res.json()
        return {"error": res.json().get("detail", "Could not fetch forecast")}
    except Exception as e:
        return {"error": str(e)}

def get_favorites(token: str) -> dict:
    """
    Gets favorite cities for the logged-in user.
    """
    try:
        res = requests.get(
            f"{BASE_URL}/favorites",
            headers={"Authorization": f"Bearer {token}"}
        )
        if res.ok:
            return res.json()
        return {"error": res.json().get("detail", "Could not fetch favorites")}
    except Exception as e:
        return {"error": str(e)}

def add_favorite(city: str, token: str) -> dict:
    """
    Adds a city to favorites.
    """
    try:
        res = requests.post(
            f"{BASE_URL}/favorites",
            json={"city": city},
            headers={"Authorization": f"Bearer {token}"}
        )
        if res.ok:
            return {"success": True, "message": "Added to favorites"}
        return {"success": False, "error": res.json().get("detail", "Could not add favorite")}
    except Exception as e:
        return {"success": False, "error": str(e)}
