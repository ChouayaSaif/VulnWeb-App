import sqlite3
import hashlib

def seed_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    
    added_count = 0
    
    try:
        with open('users.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                username, password = line.split(',')
                hashed_password = hashlib.md5(password.encode()).hexdigest()
                
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
                        (username, hashed_password)
                    )
                    added_count += 1
                except sqlite3.Error:
                    continue
    
    except IOError:
        print("Error: Could not open users.txt")
        return
    
    conn.commit()
    conn.close()
    
    print(f"<h2>✅ Seeding Complete</h2>")
    print(f"<p>Added {added_count} users to <code>database.db</code></p>")
    print("<a href='login.py'>🔐 Go to Login Page</a>")

if __name__ == '__main__':
    seed_users()