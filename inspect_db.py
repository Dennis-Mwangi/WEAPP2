import sqlite3

# Connect to your database
conn = sqlite3.connect("weather.db")
cursor = conn.cursor()

# Show all tables
print("Tables in the database:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

# Example: show data from users table
try:
    cursor.execute("SELECT * FROM users;")
    rows = cursor.fetchall()
    print("\nUsers table:")
    for row in rows:
        print(row)
except Exception as e:
    print("\nNo 'users' table or error:", e)

# Example: show data from searches table
try:
    cursor.execute("SELECT * FROM searches;")
    rows = cursor.fetchall()
    print("\nSearches table:")
    for row in rows:
        print(row)
except Exception as e:
    print("\nNo 'searches' table or error:", e)

conn.close()
