
import sqlite3

conn = sqlite3.connect("weather.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT NOT NULL,
    keys TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Database initialized with subscriptions table.")
