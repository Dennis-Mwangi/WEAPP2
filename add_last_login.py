import sqlite3

conn = sqlite3.connect("weather.db")
cursor = conn.cursor()

# Add last_login column if it doesn't exist
cursor.execute("PRAGMA table_info(users);")
columns = [col[1] for col in cursor.fetchall()]

if "last_login" not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME;")
    conn.commit()
    print("✅ Added 'last_login' column to users table.")
else:
    print("ℹ️ 'last_login' column already exists.")

conn.close()
