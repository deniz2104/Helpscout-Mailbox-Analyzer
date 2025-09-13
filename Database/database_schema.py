import sqlite3
DB_FILE = "app.db"

def get_connection():
    return sqlite3.connect(database=DB_FILE)

def initialize_database():
    """Initialize the database with required tables."""
    connection : sqlite3.Connection = get_connection()
    if connection is None:
        raise Exception("Failed to connect to the database.")
    cursor : sqlite3.Cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS tags (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT UNIQUE NOT NULL,
                        product_id INTEGER NOT NULL,
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                   )
    ''')
    connection.commit()
    connection.close()
