import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    cursor.execute("DELETE FROM users")
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin')")
    cursor.execute("INSERT INTO users (username, password) VALUES ('user', 'test')")
    
    conn.commit()
    conn.close()
    print("Database initialized with users.")

if __name__ == "__main__":
    init_db()