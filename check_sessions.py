import sqlite3

conn = sqlite3.connect("weather.db")
c = conn.cursor()

for row in c.execute("SELECT id, user_id, jti, issued_at, expires_at, revoked, client_info FROM user_sessions ORDER BY issued_at DESC;"):
    print(row)

conn.close()
