import sqlite3
import psycopg2
import os
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import traceback

load_dotenv()

def create_sqlite_table(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email_verified BOOLEAN DEFAULT FALSE,
        verification_token TEXT UNIQUE
    )
    ''')

def migrate_data():
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    # Connect to SQLite
    try:
        sqlite_conn = sqlite3.connect('instance/users.db')
        sqlite_cursor = sqlite_conn.cursor()
        print("Successfully connected to SQLite")
        
        # Create the users table if it doesn't exist
        create_sqlite_table(sqlite_cursor)
        sqlite_conn.commit()
        
    except Exception as e:
        print(f"Error connecting to SQLite: {str(e)}")
        print(traceback.format_exc())
        return

    # Get PostgreSQL connection string from environment
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    if not DATABASE_URL:
        print("Error: DATABASE_URL environment variable not set")
        return

    try:
        print("Attempting to connect to PostgreSQL...")
        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(DATABASE_URL)
        pg_cursor = pg_conn.cursor()
        print("Successfully connected to PostgreSQL")

        # Create users table in PostgreSQL
        print("Creating users table...")
        pg_cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(120) NOT NULL,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token VARCHAR(120) UNIQUE,
                is_admin BOOLEAN DEFAULT FALSE,
                is_comissoes_admin BOOLEAN DEFAULT FALSE,
                is_financeiro_admin BOOLEAN DEFAULT FALSE
            )
        """)

        # Get all users from SQLite
        print("Fetching users from SQLite...")
        sqlite_cursor.execute("SELECT email, password_hash, email_verified, verification_token FROM users")
        users = sqlite_cursor.fetchall()
        print(f"Found {len(users)} users in SQLite")

        # Insert users into PostgreSQL
        for user in users:
            print(f"Migrating user: {user[0]}")
            pg_cursor.execute("""
                INSERT INTO users (email, password_hash, email_verified, verification_token)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
            """, user)

        # Commit the changes
        pg_conn.commit()
        print(f"Successfully migrated {len(users)} users to PostgreSQL")

    except Exception as e:
        print(f"Error during migration: {str(e)}")
        print(traceback.format_exc())
    finally:
        # Close connections
        sqlite_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == '__main__':
    migrate_data()
