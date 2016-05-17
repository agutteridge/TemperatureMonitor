# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Temperature Logger for a Raspberry Pi: Server
#
# Monthly set of functions to run
# Writes mean, minimum and maximum temperatures of last month to report
# Deletes individual readings over 1 month old
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import os
import datetime
import app_config


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


# Writes a CSV file with min, max and mean temps for each day from last month
def write_report(data, month):
    filename = month + '.csv'
    with open(os.path.join(app_config.output_path + filename), 'a') as output:
        output.write('Date\tMin\tMax\tMean\n')
        for d in data:
            output.write('\t'.join(str(i) for i in d) + '\n')
        output.close()


def run(db):
    last_month = minus_month(1)
    rows = db.get_month(last_month)
    write_report(rows, last_month)
