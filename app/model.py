from flask import g
import sqlite3

DATABASE = 'pi_temps.db'


# Inititalises the database with Readings table
def init_db(db_name):
    db = sqlite3.connect(
        db_name,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    c = db.cursor()
    c.execute('''CREATE TABLE Readings (Temp REAL, DateAndTime TIMESTAMP)''')
    db.commit()
    return db


# Returns a reference to an initialised database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = init_db(DATABASE)
    return db


# Inserts row of data (temperature and timestamp) into Readings table
def store_temp(db, temp_datetime):
    c = db.cursor()
    c.execute('''
        INSERT INTO Readings VALUES (?, ?)''', temp_datetime)
    db.commit()


# Returns all rows containing temperature data from the last 24 hours
def fetch_24hrs(db):
    c = db.cursor()
    c.execute('''
        SELECT *
        FROM Readings
        WHERE datetime("DateAndTime [TIMESTAMP]") >
            (datetime("now [TIMESTAMP]") - datetime('-1 day'))''')
    return c.fetchall()
