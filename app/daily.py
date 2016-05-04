# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi: Server
#
# Daily set of functions to run
# Writes mean, minimum and maximum temperatures of last 24 hours to new table
# Deletes individual readings with date from day before yesterday
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
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


def run(db):
    rows = db.last_24hrs()
    if len(rows) > 1:
        day = min_max_mean(rows)
        yesterday = (datetime.datetime.today() - timedelta(days=1)).strftime(
            '%Y-%m-%d')
        data = [yesterday] + day
        return_code = db.insert_day(data)
        if return_code is 0:
            db.remove_dby()
