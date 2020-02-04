import sqlite3


class Database:
    def __init__(self):
        self.cnx = sqlite3.connect('players.db')
        self.cursor = self.cnx.cursor()

    def close(self):
        self.cnx.close()

    def create_player(self, name):
        self.cursor.execute(f"""
            CREATE TABLE {name} (
            id INT PRIMARY KEY NOT NULL,
            date DATETIME NOT NULL,
            quest CHAR(32),
            points JSON,
            bookmark CHAR(256)
            )
            """)
