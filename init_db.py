from database import init_db
from auth import register_user

def seed_admin():
    print("Initializing Database...")
    init_db()
    print("Checking for default admin account...")
    
    # Check if admin exists
    from database import get_connection, return_connection
    conn = get_connection()
    admin_exists = False
    
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE username = 'admin'")
                if cur.fetchone():
                    admin_exists = True
        except Exception as e:
            print(f"Error querying DB: {e}")
        finally:
            return_connection(conn)

    if not admin_exists:
        success = register_user("admin", "admin123", "ADMIN")
        if success:
            print("✅ Default admin created. (Username: admin, Password: admin123)")
        else:
            print("❌ Failed to create default admin.")
    else:
        print("✅ Admin account already exists.")

if __name__ == "__main__":
    seed_admin()
