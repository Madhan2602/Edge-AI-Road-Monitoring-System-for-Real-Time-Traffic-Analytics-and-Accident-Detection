import bcrypt
from database import get_connection, return_connection

# Role Constants
ROLE_ADMIN = "ADMIN"
ROLE_TRAFFIC_POLICE = "TRAFFIC_POLICE"
ROLE_CITY_PLANNER = "CITY_PLANNER"
VALID_ROLES = [ROLE_ADMIN, ROLE_TRAFFIC_POLICE, ROLE_CITY_PLANNER]

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verifies a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(username: str, password: str, role: str) -> bool:
    """Registers a new user in the database."""
    if role not in VALID_ROLES:
        print(f"Invalid role: {role}")
        return False
        
    hashed_password = hash_password(password)
    
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    (username, hashed_password, role)
                )
            conn.commit()
            return True
        except Exception as e:
            print(f"Registration Error: {e}")
            conn.rollback()
            return False
        finally:
            return_connection(conn)
    return False

def authenticate_user(username: str, password: str):
    """Authenticates a user and returns their role if successful, else None."""
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT password_hash, role FROM users WHERE username = %s",
                    (username,)
                )
                result = cur.fetchone()
                
                if result:
                    stored_hash, role = result
                    if verify_password(password, stored_hash):
                        return role
        except Exception as e:
            print(f"Authentication Error: {e}")
        finally:
            return_connection(conn)
            
    return None

def get_all_users():
    """Fetches all users (for admin management)."""
    conn = get_connection()
    users = []
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, username, role, created_at FROM users ORDER BY created_at DESC")
                columns = [desc[0] for desc in cur.description]
                for row in cur.fetchall():
                    users.append(dict(zip(columns, row)))
        except Exception as e:
            print(f"Fetch Users Error: {e}")
        finally:
            return_connection(conn)
    return users
