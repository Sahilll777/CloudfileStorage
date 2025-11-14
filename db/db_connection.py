# db/db_connection.py
import mysql.connector
from config import MYSQL_CONFIG

def get_db_connection():
    return mysql.connector.connect(**{k: v for k, v in MYSQL_CONFIG.items() if v is not None})
