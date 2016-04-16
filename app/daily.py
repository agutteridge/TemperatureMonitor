# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi
# Daily set of functions to run
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import model
import statistics


# Calculate the mean, minimum and maximum temperatures for the last 24 hours
# Returns these values as a list
def min_max_mean(db):
    results = model.fetch_24hrs(db)
    temps = []
    for row in results:
        temps.append(row[0])
    return [
        min(temps),
        max(temps),
        statistics.mean(temps)
    ]


# Add day values to Days table
def insert_day(db, day):
    c = db.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS Days (Mean REAL, Min REAL, Max REAL)''')
    c.execute(
        '''INSERT INTO Days VALUES (?, ?, ?)''', day)
    c.commit()
    c.close()
    return 0


# Deletes all rows > 24 hours ago from the database
def remove_24hrs(db):
    c = db.cursor()
    c.execute(
        '''DELETE FROM Readings
           WHERE datetime("DateAndTime [TIMESTAMP]") <
               (datetime("now [TIMESTAMP]") - datetime('-1 day'))''')
    c.commit()
    c.close()


def run(db):
    day = min_max_mean(db)
    return_code = insert_day(db, day)
    if return_code is 0:
        remove_24hrs(db)
