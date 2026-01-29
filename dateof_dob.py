import sqlite3
import os

DB_PATH = os.path.join("instance", "hospital.db")

def dateof():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'date_of_birth' in columns:
            print(" 'date_of_birth' column already exists. Skipping.")
        else:
            print("Adding 'date_of_birth' column...")
            cursor.execute("ALTER TABLE users ADD COLUMN date_of_birth DATE")
            conn.commit()
            print(" Migration successful!")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    dateof()
