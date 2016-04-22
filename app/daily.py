# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi: Server
#
# Daily set of functions to run
# Writes mean, minimum and maximum temperatures of last 24 hours to new table
# Deletes individual readings over 24 hours old
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import model
import statistics
import datetime
from datetime import timedelta


# Calculate the mean, minimum and maximum temperatures for the last 24 hours
# Returns these values as a list
def min_max_mean(rows):
    minimum = min(rows, key=lambda x: x[0])[0]
    maximum = max(rows, key=lambda x: x[0])[0]
    temps = []
    for temp, date in rows:
        temps.append(temp)
    mean = float("{0:.1f}".format(statistics.mean(temps)))
    return [
        minimum,
        maximum,
        mean
    ]


# Add day values to Days table
def insert_day(db, day):
    yesterday = (datetime.datetime.today() - timedelta(days=1)).strftime(
        '%Y-%m-%d')
    data = [yesterday] + day
    c = db.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS Days
           (Date DATE, Min REAL, Max REAL, Mean REAL)''')
    c.execute(
        '''INSERT INTO Days VALUES (?, ?, ?, ?)''', data)
    db.commit()
    c.close()
    return 0


# Deletes all rows with yesterday's date from the database
def remove_yesterday(db):
    yesterday = (datetime.datetime.today() - timedelta(days=1)).strftime(
        '%Y-%m-%d')
    c = db.cursor()
    c.execute(
        'DELETE FROM Readings WHERE DATE(DateAndTime) = (?)', (yesterday,))
    db.commit()
    c.close()


def run(db):
    rows = model.fetch_24hrs(db)
    day = min_max_mean(rows)
    return_code = insert_day(db, day)
    if return_code is 0:
        remove_yesterday(db)
