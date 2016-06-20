# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi: Server
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import statistics
import datetime


def first_last(first, last):
    start = datetime.datetime(
        first.year,
        first.month,
        first.day,
        0, 0, 0, 0)
    end = datetime.datetime(
        last.year,
        last.month,
        last.day,
        23, 59, 59, 999)
    return (start, end)


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


# query_day is datetime.date object
def condense(db, query_day):
    (start, end) = first_last(query_day, query_day)
    day_row = db.get_days(start.date(), end.date())

    if day_row:
        return day_row
    else:
        rows = db.get_readings(start, end)
        data = list()

        if len(rows) > 1:
            mmm = min_max_mean(rows)
            data = [query_day] + mmm
        elif len(rows) == 1:
            data = [
                query_day,
                rows[0][0],
                rows[0][0],
                rows[0][0]]

        if data and query_day is not datetime.date.today():
            db.insert_day(data)

            return [tuple(data)]
        else:
            return [(query_day, 'no data', 'no data', 'no data')]
