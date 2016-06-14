# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi: Server
#
# Monthly set of functions to run
# Writes mean, minimum and maximum temperatures of last month to report
# Deletes individual readings over 1 month old
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import datetime
from datetime import timedelta

import daily


class Month_data():
    def __init__(self, year_month):
        self.string = year_month
        year_month_list = year_month.split('-')
        self.year = int(year_month_list[0])
        self.month = int(year_month_list[1])
        self.num_days = self._rhyme()

    # 30 days have September, April, June and November!
    def _rhyme(self):
        if self.month == 12:
            next_month = 1
        else:
            next_month = self.month + 1

        first_day = datetime.date(self.year, next_month, 1)
        last_day = first_day - timedelta(days=1)
        return last_day.day

    # month_date in str format '%Y-%m'
    def _check_days(self, db):
        result = list()
        for d in range(1, self.num_days + 1):
            day_row = db.get_day(
                datetime.date(self.year, self.month, d).strftime('%Y-%m-%d'))
            if not day_row:
                day_row = daily.run(
                    db, (datetime.date(self.year, self.month, d)))
            result.extend(day_row)
        return result

    # change format of days to e.g. 01 (Sat)
    def _pretty_format(self, rows):
        pretty = list()
        for r in rows:
            new_row = list()
            new_row.append(r[0].strftime('%d (%a)'))
            new_row.extend(r[1:])
            pretty.append(new_row)

        return pretty

    # month_date in str format '%Y-%m'
    def get_days(self, db):
        rows = db.get_month(self.string)

        if len(rows) != self.num_days:
            rows = self._check_days(db)

        pretty_rows = self._pretty_format(rows)
        return pretty_rows
