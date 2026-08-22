import sqlite3
import os
path = os.path.join(os.path.dirname(__file__), "DB")
conn = sqlite3.connect(path, check_same_thread=False)
cursor = conn.cursor()

# user table
cursor.execute("CREATE TABLE IF NOT EXISTS USERS(id INTEGER PRIMARY KEY, name VARCHAR(100), email VARCHAR(255) UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")

# datasets
cursor.execute("CREATE TABLE IF NOT EXISTS DATASETS(id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, filename VARCHAR(255) NOT NULL, file_data BYTEA NOT NULL, uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id));")

# class Db as modules

class Db():
    def __init__(self):
        self.user_id = int


    def store_data(self, user_id, filename, file_data):
        try:
            cursor.execute("INSERT INTO DATASETS(user_id, filename, file_data) VALUES(?, ?, ?)",(user_id, filename, file_data))
            conn.commit()
        except Exception as e:
            return {
                "message": str(e)
            }

    def get_data(self, id):
        try:
            cursor.execute("SELECT filename, file_data FROM DATASETS WHERE user_id = ?", (id,))
            return cursor.fetchone()
        except Exception as e:
            return{
                "message": str(e)
            }
