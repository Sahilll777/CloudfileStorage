# database.py
import sqlite3
import os

DB_PATH = "cloudfiles.db"


# ---------------------------------------------------------
# Create table if not exists
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            s3_key TEXT NOT NULL UNIQUE,
            size INTEGER NOT NULL,
            uploaded_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Save a file record
# ---------------------------------------------------------
def save_file_record(user_id, filename, s3_key, size, uploaded_at):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO files (user_id, filename, s3_key, size, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, filename, s3_key, size, uploaded_at))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# List all files for a user
# ---------------------------------------------------------
def list_user_files(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT filename, s3_key, size, uploaded_at
        FROM files
        WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    files = []
    for r in rows:
        files.append({
            "filename": r[0],
            "s3_key": r[1],
            "size": r[2],
            "uploaded_at": r[3]
        })
    return files


# ---------------------------------------------------------
# Get file record by S3 key
# ---------------------------------------------------------
def get_file_record(s3_key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT filename, user_id, size, uploaded_at
        FROM files
        WHERE s3_key = ?
    """, (s3_key,))

    result = cursor.fetchone()
    conn.close()
    return result


# ---------------------------------------------------------
# Delete record by S3 key
# ---------------------------------------------------------
def delete_file_record(s3_key):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM files WHERE s3_key = ?", (s3_key,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------
# Initialize DB when imported
# ---------------------------------------------------------
init_db()
