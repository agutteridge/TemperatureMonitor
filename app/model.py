import sqlite3
import datetime
from datetime import timedelta


class Model():
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
            elif fetch is 'all':
                return c.fetchall()
            elif fetch is not 'no':
                raise ValueError(fetch)
        finally:
            c.close()

    def get_all_readings(self):
        result = self.execute_query(
            'SELECT * FROM Readings',
            fetch='all')
        return result

    def get_all_days(self):
        result = self.execute_query(
            'SELECT * FROM Days',
            fetch='all')
        return result

    # Returns latest row of Readings table
    def get_last_reading(self):
        result = self.execute_query(
            'SELECT * FROM Readings ORDER BY DateAndTime DESC LIMIT 1',
            fetch='one')
        return result

    def get_last_day(self):
        exists = self.execute_query(
            '''SELECT NAME 
            FROM sqlite_master 
            WHERE type='table' AND name='Days'
            ''',
            fetch='one')

        if exists:
            result = self.execute_query(
                'SELECT * FROM Days ORDER BY DateAndTime DESC LIMIT 1',
                fetch='one')
            return result
        else:
            return None

    # Inserts row of data (temperature and timestamp) into Readings table
    def store_temp(self, temp_datetime):
        result = self.execute_query(
            'INSERT INTO Readings VALUES (?, ?)',
            data=temp_datetime,
            commit=True)
        return result

    # Returns all rows containing temperature data from the last 24 hours
    def last_24hrs(self):
        result = self.execute_query(
            '''SELECT *
               FROM Readings
               WHERE DATETIME(DateAndTime) > DATETIME('now', '-1 day')''',
            fetch='all')
        return result

    # Add day values to Days table
    def insert_day(self, data):
        self.execute_query(
            '''CREATE TABLE IF NOT EXISTS Days
               (Date DATE, Min REAL, Max REAL, Mean REAL)''',
            commit=True)
        self.execute_query(
            'INSERT INTO Days VALUES (?, ?, ?, ?)',
            data=data,
            commit=True)

    # Deletes all rows with day before yesterday's date from the database
    def remove_dby(self):
        dby = (datetime.datetime.today() - timedelta(days=2)).strftime(
            '%Y-%m-%d')
        self.execute_query(
            'DELETE FROM Readings WHERE DATE(DateAndTime) = (?)',
            data=(dby,),
            commit=True)

    # Returns all rows containing temperature data from last month
    def prev_month(self, query_month):
        result = self.execute_query(
            '''SELECT *
               FROM Days
               WHERE STRFTIME('%Y-%m', Date) = (?)''',
            data=(query_month,),
            fetch='all')
        return result

    # Deletes all rows with month before last's date from the Days table
    def remove_mbl(self, query_month):
        self.execute_query(
            '''DELETE FROM Days
               WHERE STRFTIME('%Y-%m',Date) = (?)''',
            data=(query_month,),
            commit=True)

    # Testing only, teardown
    def delete(self):
        self.execute_query(
            'DROP TABLE IF EXISTS Readings',
            commit=True)
        self.execute_query(
            'DROP TABLE IF EXISTS Days',
            commit=True)
