import os
import mysql.connector
from mysql.connector import Error

# ---- CHANGE THESE AS PER YOUR MYSQL SETUP ----
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Password"),
    "database": os.getenv("DB_NAME", "college_complaint_portal")
}
# -----------------------------------------------

def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None
