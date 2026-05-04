import sqlite3


class Database:
    def __init__(self, db_name="game.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT,
                score INTEGER
            )
        """)
        self.conn.commit()

    def save_score(self, nickname, score):
        self.cursor.execute(
            "INSERT INTO players (nickname, score) VALUES (?, ?)",
            (nickname, score)
        )
        self.conn.commit()

    def get_top_players(self):
        self.cursor.execute("""
            SELECT nickname, score
            FROM players
            ORDER BY score DESC
            LIMIT 5
        """)
        return self.cursor.fetchall()