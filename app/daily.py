# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi: Server
#
# Daily set of functions to run
# Writes mean, minimum and maximum temperatures of last 24 hours to new table
# Deletes individual readings with date from day before yesterday
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import statistics


# Calculate the mean, minimum and maximum temperatures for the last 24 hours
# Returns these values as a list
def min_max_mean(rows):
    minimum = min(rows, key=lambda x: x[0])[0]
    maximum = max(rows, key=lambda x: x[0])[0]
    temps = []
    for temp, date in rows:
        temps.append(temp)
    mean = float("{0:.1f}".format(statistics.mean(temps)))
    return [minimum, maximum, mean]


def run(db, query_day, delete=False):
    day_str = query_day.strftime('%Y-%m-%d')
    day_row = db.get_day(day_str)

    if day_row:
        return day_row
    else:
        rows = db.get_readings_specific_day(day_str)
        data = list()

        if len(rows) > 1:
            mmm = min_max_mean(rows)
            data = [day_str] + mmm
        elif len(rows) == 1:
            data = [
                day_str,
                rows[0][0],
                rows[0][0],
                rows[0][0]]

        if data:
            success = db.insert_day(data)

            if success and delete:
                db.delete_readings(day_str)

            return [tuple(data)]
        else:
            return [(query_day, 'no data', 'no data', 'no data')]
