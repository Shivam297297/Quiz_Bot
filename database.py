import sqlite3

def initialize_database():
    conn = sqlite3.connect('quiz_bot.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                (user_id INTEGER PRIMARY KEY, 
                 username TEXT,
                 first_name TEXT,
                 last_name TEXT,
                 join_date DATETIME)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS leaderboard
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 category TEXT,
                 score INTEGER,
                 total INTEGER,
                 percentage REAL,
                 timestamp DATETIME,
                 FOREIGN KEY(user_id) REFERENCES users(user_id))''')
    
    c.execute('''CREATE INDEX IF NOT EXISTS idx_leaderboard_category 
                ON leaderboard(category)''')
    c.execute('''CREATE INDEX IF NOT EXISTS idx_leaderboard_user 
                ON leaderboard(user_id)''')
    
    conn.commit()
    conn.close()
    print("✅ DataBase Completely Created")

if __name__ == '__main__':
    initialize_database()

import os
print("📁 DB will be created at:", os.path.abspath("quiz_bot.db"))
