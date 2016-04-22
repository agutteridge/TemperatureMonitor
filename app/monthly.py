# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi: Server
#
# Monthly set of functions to run
# Writes mean, minimum and maximum temperatures of last month to report
# Deletes individual readings over 1 month old
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import os
import datetime


# Returns string of year & month from delta arg number of months
# Fails if delta num arg is too high
def minus_month(num):
    if num > 12:
        raise ValueError('Function is not valid for this arg.')

    m_num = datetime.datetime.now().month - num
    y_num = datetime.datetime.now().year

    if m_num < 1:
        m_num += 12
        y_num -= 1

    if m_num < 10:
        m_num = '0' + str(m_num)

    new_date = str(y_num) + '-' + str(m_num)
    return new_date


# Returns all rows containing temperature data from last month
def prev_month(db):
    lm_date = minus_month(1)
    c = db.cursor()
    c.execute(
        '''SELECT *
           FROM Days
           WHERE STRFTIME('%Y-%m', Date) = (?)''', (lm_date,))
    return c.fetchall()


# Writes a CSV file with min, max and mean temps for each day from last month
def write_report(data):
    filename = datetime.datetime.now().strftime('%Y-%m (%B)')
    with open(os.path.join(os.getcwd() + filename + '.csv'), 'a') as output:
        output.write('Date\tMin\tMax\tMean\n')
        for d in data:
            output.write(d.join('\t') + '\n')
        output.close()


# Deletes all rows with month before last's date from the Days table
def remove_mbl(db):
    mbl = minus_month(2)
    c = db.cursor()
    c.execute(
        '''DELETE FROM Days
           WHERE STRFTIME('%Y-%m',Date) = (?)''', (mbl,))
    db.commit()
    c.close()


def run(db):
    rows = prev_month(db)
    write_report(rows)
