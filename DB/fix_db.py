from sqlalchemy import text
from db import engine

def fix_db():
    print("Connecting to database to fix schema...")
    with engine.connect() as conn:
        try:
            # Drop all potential table names to ensure a clean start
            conn.execute(text("DROP TABLE IF EXISTS audio_records"))
            conn.execute(text("DROP TABLE IF EXISTS translations"))
            conn.execute(text("DROP TABLE IF EXISTS audiofiles"))
            conn.execute(text("DROP TABLE IF EXISTS shlokas"))
            conn.execute(text("DROP TABLE IF EXISTS slokas"))
            conn.commit()
            print("Successfully cleared all tables.")
        except Exception as e:
            print(f"Error while fixing DB: {e}")

if __name__ == "__main__":
    fix_db()
