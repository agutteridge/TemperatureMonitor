# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi: Server
#
# Monthly set of functions to run
# Writes mean, minimum and maximum temperatures of last month to report
# Deletes individual readings over 1 month old
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import datetime
from datetime import timedelta

import day_data


class Month_data():
    def __init__(self, year_month):
        self.string = year_month
        year_month_list = year_month.split('-')
        self.year = int(year_month_list[0])
        self.month = int(year_month_list[1])
        self.num_days = self._rhyme()
        # Datetime objects for start and end of the month
        (self.start, self.end) = day_data.first_last(
            datetime.datetime(self.year,
                              self.month,
                              1),
            datetime.datetime(self.year,
                              self.month,
                              self.num_days))

    # Deletes all Readings from this month from the database
    def spring_clean(self, db):
        db.delete_readings(self.start, self.end)

    # Returns month_obj relative to self
    # maximum timedelta is 12 months
    def timedelta(self, num_months):
        if num_months > 12:
            raise ValueError('Function is not valid for this arg.')

        new_month = self.month - num_months
        new_year = self.year

        if new_month < 1:
            new_month += 12
            new_year -= 1

        if new_month < 10:
            return Month_data(str(new_year) + '-0' + str(new_month))
        else:
            return Month_data(str(new_year) + '-' + str(new_month))

    # 30 days have September, April, June and November!
    def _rhyme(self):
        if self.month == 12:
            next_month = 1
            the_year = self.year + 1
        else:
            next_month = self.month + 1
            the_year = self.year

        first_day = datetime.date(the_year, next_month, 1)
        last_day = first_day - timedelta(days=1)
        return last_day.day

    def _check_days(self, db):
        result = list()
        any_data = False

        for d in range(1, self.num_days + 1):
            d_date = datetime.date(self.year, self.month, d)
            (day_start, day_end) = day_data.first_last(d_date, d_date)
            day_row = db.get_days(day_start, day_end)

            if not day_row:
                day_row = day_data.condense(db, d_date)
                if 'no data' not in day_row[0]:
                    any_data = True
            else:
                any_data = True

            result.extend(day_row)

        if any_data:
            return result
        else:  # If there are no readings for this month, return empty list
            return list()

    # change format of days to e.g. 01 (Sat)
    def _pretty_format(self, rows):
        pretty = list()
        for r in rows:
            new_row = list()
            new_row.append(r[0].strftime('%d (%a)'))
            new_row.extend(r[1:])
            pretty.append(new_row)

        return pretty

    def get_days(self, db):
        rows = db.get_days(self.start.date(), self.end.date())
        if len(rows) != self.num_days:
            rows = self._check_days(db)

        pretty_rows = self._pretty_format(rows)
        return pretty_rows
