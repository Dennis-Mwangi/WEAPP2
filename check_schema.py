import sqlite3

conn = sqlite3.connect("weather.db")
cursor = conn.cursor()

# Get schema of the users table
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()

print("Users table columns:")
for col in columns:
    print(col)

conn.close()
