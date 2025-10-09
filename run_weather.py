import sys
from weather_helper import login, get_weather, get_forecast, get_favorites, add_favorite

def main():
    if len(sys.argv) != 4:
        print("Usage: python run_weather.py <username> <password> <city>")
        return

    USERNAME = sys.argv[1]
    PASSWORD = sys.argv[2]
    CITY = sys.argv[3]

    print(f"🔑 Logging in as {USERNAME}...")
    resp = login(USERNAME, PASSWORD)

    if not resp.get("success"):
        print("❌ Login failed:", resp.get("error"))
        return

    token = resp["access_token"]
    print("✅ Login successful!\n")

    print(f"🌤 Fetching weather for {CITY}...")
    weather = get_weather(CITY, token)
    print(weather, "\n")

    print(f"📅 Fetching forecast for {CITY}...")
    forecast = get_forecast(CITY, token)
    print(forecast, "\n")

    print("⭐ Getting favorites...")
    favorites = get_favorites(token)
    print(favorites, "\n")

    print(f"➕ Adding {CITY} to favorites...")
    add_favorite(CITY, token)

    print("✅ Done! Favorites updated.\n")

if __name__ == "__main__":
    main()
