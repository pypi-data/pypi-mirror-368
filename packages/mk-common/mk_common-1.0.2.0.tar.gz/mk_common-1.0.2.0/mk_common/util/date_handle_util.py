
from datetime import datetime, timedelta


def add_date(date_str, add_count=1):
    date = datetime.strptime(date_str, '%Y-%m-%d')
    new_date = date + timedelta(days=add_count)

    new_str_day = new_date.strftime('%Y-%m-%d')
    return new_str_day


def add_date_day(date_str, add_count=1):
    date = datetime.strptime(date_str, '%Y%m%d')
    new_date = date + timedelta(days=add_count)
    return new_date


def str_to_date(date_str, for_mart):
    date_time = datetime.strptime(date_str, for_mart)
    return date_time


def lash_date(date_str):
    date_time_begin = datetime.strptime(date_str, '%Y%m%d')
    date_str = date_time_begin.strftime('%Y-%m-%d')
    return date_str


def no_slash_date(date='-'):
    date = str(date)
    date = date.replace('-', '')
    return date


def calculate_mouth(date):
    return date.month


def calculate_year(date):
    return date.year


def last_day_of_week(date):
    return date.weekday() == 4


def last_day_month(date):
    month = date.month
    day = date.day
    if month in [1, 3, 5, 7, 8, 10, 12] and day == 31:
        return True
    elif month in [4, 6, 9, 11] and day == 30:
        return True
    elif run_nian(date) and month == 2 and day == 29:
        return True
    elif bool(1 - run_nian(date)) and month == 2 and day == 28:
        return True
    return False


def run_nian(date):
    year = date.year
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


def days_diff(d1, d2):
    return (d1 - d2).days
