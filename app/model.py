import sqlite3


class Model():
    # Inititalises the database with Readings table
    def __init__(self, db_name):
        self.db_name = db_name
        self.execute_query(
            '''CREATE TABLE IF NOT EXISTS Readings
            (Temp REAL, DateAndTime TIMESTAMP)''',
            commit=True)
        self.execute_query(
            '''CREATE TABLE IF NOT EXISTS Days
               (Day DATE, Min REAL, Max REAL, Mean REAL)''',
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
            elif fetch is 'all':
                return c.fetchall()
            elif fetch is not 'no':
                raise ValueError(fetch)
        finally:
            c.close()

    # Inserts row of data (temperature and timestamp) into Readings table
    def store_temp(self, temp_datetime):
        result = self.execute_query(
            'INSERT INTO Readings VALUES (?, ?)',
            data=temp_datetime,
            commit=True)
        return result

    # Add day values to Days table
    def insert_day(self, data):
        self.execute_query(
            'INSERT INTO Days VALUES (?, ?, ?, ?)',
            data=data,
            commit=True)
        return True

    def get_all_readings(self):
        result = self.execute_query(
            'SELECT * FROM Readings',
            fetch='all')
        return result

    def get_all_days(self):
        result = self.execute_query(
            'SELECT * FROM Days ORDER BY Day',
            fetch='all')
        return result

    def get_last_reading(self):
        result = self.execute_query(
            'SELECT * FROM Readings ORDER BY DateAndTime DESC LIMIT 1',
            fetch='one')
        return result

    def get_last_day(self):
        result = self.execute_query(
            'SELECT * FROM Days ORDER BY Day DESC LIMIT 1',
            fetch='one')
        return result

    # Return Readings within a time window
    def get_readings(self, start, end):
        result = self.execute_query(
            '''SELECT *
               FROM Readings
               WHERE DATETIME(DateAndTime) >= DATETIME(?)
               AND DATETIME(DateAndTime) <= DATETIME(?)
               ORDER BY DateAndTime''',
            data=sorted([start, end]),
            fetch='all')
        return result

    # retrieve single row (or empty list) from Days table
    def get_days(self, start, end):
        result = self.execute_query(
            '''SELECT *
               FROM Days
               WHERE DATE(Day) >= DATE(?)
               AND DATE(Day) <= DATE(?)
               ORDER BY Day''',
            data=sorted([start, end]),
            fetch='all')
        return result

    # Delete Readings within a time window
    def delete_readings(self, start, end):
        result = self.execute_query(
            '''DELETE FROM Readings
               WHERE DATETIME(DateAndTime) >= DATETIME(?)
               AND DATETIME(DateAndTime) <= DATETIME(?)''',
            data=sorted([start, end]),
            commit=True)
        return result

    # def delete_days(self, query_month):
    #     self.execute_query(
    #         '''DELETE FROM Days
    #            WHERE STRFTIME('%Y-%m', Day) = (?)''',
    #         data=(query_month,),
    #         commit=True)
    #     return True

    # Testing only, teardown
    def delete(self):
        self.execute_query(
            'DROP TABLE IF EXISTS Readings',
            commit=True)
        self.execute_query(
            'DROP TABLE IF EXISTS Days',
            commit=True)
        return True
