import sqlite3


class Pidb():
    # Inititalises the database with Readings table
    def __init__(self, db_name):
        self.db_name = db_name
        self.execute_query(
            '''CREATE TABLE IF NOT EXISTS Readings
            (Temp REAL, DateAndTime TIMESTAMP)''',
            commit=True)

    def execute_query(self, query, data=None, commit=False, fetch='no'):
        db = sqlite3.connect(
            self.db_name,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False)
        c = db.cursor()
        try:
            if data is not None:
                c.execute(query, data)
            else:
                c.execute(query)
            if commit:
                db.commit()
            if fetch is 'one':
                return c.fetchone()
            if fetch is 'all':
                return c.fetchall()
            elif fetch is not 'no':
                raise ValueError(fetch)
        finally:
            c.close()

    def get_all_readings(self):
        exists = self.execute_query(
            '''SELECT NAME
            FROM sqlite_master
            WHERE type='table' AND name='Readings'
            ''',
            fetch='one')

        if exists:
            result = self.execute_query(
                'SELECT * FROM Readings',
                fetch='all')
            return result
        else:
            return []

    # Inserts row of data (temperature and timestamp) into Readings table
    def store_temp(self, temp_datetime):
        result = self.execute_query(
            'INSERT INTO Readings VALUES (?, ?)',
            data=temp_datetime,
            commit=True)
        return result

    def delete(self):
        self.execute_query(
            'DROP TABLE IF EXISTS Readings',
            commit=True)
