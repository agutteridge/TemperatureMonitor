import sqlite3
import datetime
from datetime import timedelta


class Model():
    # Inititalises the database with Readings table
    def __init__(self, db_name):
        self.db = sqlite3.connect(
            db_name,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        c = self.db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS Readings
            (Temp REAL, DateAndTime TIMESTAMP)''')
        c.close()
        self.db.commit()

    # Returns reference to the database for testing
    def get_db(self):
        return self.db

    # Returns latest row of Readings table
    def get_last_reading(self):
        c = self.db.cursor()
        c.execute('''
            SELECT * FROM Readings ORDER BY DateAndTime DESC LIMIT 1''')
        result = c.fetchone()
        c.close()
        return result

    def get_last_day(self):
        c = self.db.cursor()
        c.execute('''
            SELECT * FROM Days ORDER BY DateAndTime DESC LIMIT 1''')
        result = c.fetchone()
        c.close()
        return result

    # Inserts row of data (temperature and timestamp) into Readings table
    def store_temp(self, temp_datetime):
        c = self.db.cursor()
        c.execute('''
            INSERT INTO Readings VALUES (?, ?)''', temp_datetime)
        c.close()
        self.db.commit()

    # Returns all rows containing temperature data from the last 24 hours
    def last_24hrs(self):
        c = self.db.cursor()
        c.execute('''
            SELECT *
            FROM Readings
            WHERE DATETIME(DateAndTime) > DATETIME('now', '-1 day')''')
        result = c.fetchall()
        c.close()
        return result

    # Add day values to Days table
    def insert_day(self, data):
        c = self.db.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS Days
               (Date DATE, Min REAL, Max REAL, Mean REAL)''')
        c.execute(
            '''INSERT INTO Days VALUES (?, ?, ?, ?)''', data)
        self.db.commit()
        c.close()
        return 0

    # Deletes all rows with day before yesterday's date from the database
    def remove_dby(self):
        dby = (datetime.datetime.today() - timedelta(days=2)).strftime(
            '%Y-%m-%d')
        c = self.db.cursor()
        c.execute(
            'DELETE FROM Readings WHERE DATE(DateAndTime) = (?)', (dby,))
        self.db.commit()
        c.close()

    # Returns all rows containing temperature data from last month
    def prev_month(self, query_month):
        c = self.db.cursor()
        c.execute(
            '''SELECT *
               FROM Days
               WHERE STRFTIME('%Y-%m', Date) = (?)''', (query_month,))
        result = c.fetchall()
        c.close()
        return result

    # Deletes all rows with month before last's date from the Days table
    def remove_mbl(self, query_month):
        c = self.db.cursor()
        c.execute(
            '''DELETE FROM Days
               WHERE STRFTIME('%Y-%m',Date) = (?)''', (query_month,))
        self.db.commit()
        c.close()
