import sqlite3

# Connect to your database
conn = sqlite3.connect("weather.db")
cursor = conn.cursor()

print("Recent Searches:")
for row in cursor.execute("SELECT * FROM search_history ORDER BY timestamp DESC LIMIT 10;"):
    print(row)

print("\nFavorite Cities:")
for row in cursor.execute("SELECT * FROM favorite_cities ORDER BY id DESC;"):
    print(row)

conn.close()
