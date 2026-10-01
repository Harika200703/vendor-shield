import sqlite3

db_path = "backend/vendortust.db"

connection = sqlite3.connect(db_path)

cursor = connection.cursor()

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
)

tables = cursor.fetchall()

print("\n--- TABLES IN DATABASE ---\n")

for table in tables:
    print(table[0])

connection.close()