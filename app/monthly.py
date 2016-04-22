# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi: Server
#
# Monthly set of functions to run
# Writes mean, minimum and maximum temperatures of last month to report
# Deletes individual readings over 1 month old
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import datetime
from datetime import timedelta

this_month_string = datetime.datetime.now().strftime('%B')
last_month = datetime.datetime.now() - timedelta(months=1).strftime('%Y-%m')


def fetch_last_month(db):
    c = db.cursor()
    c.execute(
        '''SELECT *
           FROM Days
           WHERE STRFTIME('%Y-%m', DateAndTime) = (?)''', (last_month,))
    return c.fetchall()


def run(db):
    rows = fetch_last_month(db)
