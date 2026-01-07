import sqlite3
import sys

conn = sqlite3.connect('servitec_manager/SERVITEC_TEST_OPTIMIZED.DB')
cursor = conn.cursor()

triggers = cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name").fetchall()

print(f"TRIGGERS ACTIVOS: {len(triggers)}")
for t in triggers:
    print(f"  - {t[0]}")

conn.close()

sys.exit(0)
