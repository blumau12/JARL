import sqlite3
from os import makedirs
from os.path import dirname

from exceptions import assert_person


class Logs:
    LOG_STRUCTURE = {
        'timestamp': 'CHAR(32)',
        'quest_id': 'CHAR(12)',
        'action': 'CHAR(32)',
        'points': 'JSON',
        'bookmark': 'CHAR(256)',
        }

    def __init__(self, logs_path):
        # log example: (timestamp, quest_name, action, points, bookmark)
        makedirs(dirname(logs_path), exist_ok=True)

        self.cnx = sqlite3.connect(logs_path)
        self.cursor = self.cnx.cursor()

        fields = (f'{f} {typ}' for f, typ in self.LOG_STRUCTURE.items())
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS logs (
            {', '.join(fields)}
            )
        """)

    def get_logs(self, select=None, where='1'):
        if select is None:
            select = '*'
        else:
            assert_person(all(s in self.LOG_STRUCTURE for s in select),
                          f'fields "{(k for k in select if k not in self.LOG_STRUCTURE)}" are not allowed')
            select = ', '.join(select)
        self.cursor.execute(f"""
            SELECT {select}
            FROM logs
            WHERE {where}
        """)
        res = self.cursor.fetchall()
        return res

    def log(self, **kwargs):
        assert_person(all(k in self.LOG_STRUCTURE.keys() for k in kwargs),
                      f'fields "{(k for k in kwargs if k not in self.LOG_STRUCTURE)}" are not allowed')
        values = []
        for k, v in kwargs.items():
            if isinstance(k, str):
                values.append(f'"{v}"')
            else:
                values.append(f'{v}')
        self.cursor.execute(f"""
            INSERT INTO logs
            VALUES ({', '.join(values)})
        """)
        self.cnx.commit()

    def close(self):
        self.cnx.close()
