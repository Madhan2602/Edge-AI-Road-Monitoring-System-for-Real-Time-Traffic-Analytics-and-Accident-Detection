import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

# Global connection pool
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10,
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "eairms")
    )
    if db_pool:
        print("✅ PostgreSQL Connection Pool created successfully")
except Exception as e:
    print(f"❌ Error while connecting to PostgreSQL: {e}")
    db_pool = None

def get_connection():
    """Get a connection from the pool."""
    if db_pool:
        return db_pool.getconn()
    return None

def return_connection(conn):
    """Return a connection to the pool."""
    if db_pool and conn:
        db_pool.putconn(conn)

def init_db():
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(20) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS license_plates (
                        id SERIAL PRIMARY KEY,
                        plate_text VARCHAR(50) NOT NULL,
                        confidence FLOAT NOT NULL,
                        location VARCHAR(100) NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            conn.commit()
            print("✅ Database tables initialized.")
        except Exception as e:
            print(f"❌ Error initializing DB: {e}")
        finally:
            return_connection(conn)

def log_plate_transaction(plate_text, confidence, location):
    """Insert a new ALPR transaction into the license_plates table."""
    conn = get_connection()
    success = False
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO license_plates (plate_text, confidence, location) VALUES (%s, %s, %s)",
                    (plate_text, confidence, location)
                )
            conn.commit()
            print(f"✅ DB Insert Success: Logged plate {plate_text} at {location}")
            success = True
        except Exception as e:
            conn.rollback()
            print(f"❌ DB Insert Error logging plate {plate_text}: {e}")
        finally:
            return_connection(conn)
    else:
        print("❌ DB Insert Error: No database connection available.")
    return success
