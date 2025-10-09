import sqlite3

conn = sqlite3.connect("weather.db")
cursor = conn.cursor()

print("Top 5 Most Searched Cities:")
for row in cursor.execute("""
    SELECT city, COUNT(*) AS searches
    FROM search_history
    GROUP BY city
    ORDER BY searches DESC
    LIMIT 5;
"""):
    print(f"{row[0]} → {row[1]} searches")

conn.close()
