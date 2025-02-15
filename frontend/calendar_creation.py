import calendar
from calendar import month_name
from datetime import datetime

def generate_calendar():
    """
    Generate the calendar for the current month with year and current day.
    Returns dictionary containing:
        - year: current year
        - month: current month (as an int)
        - day: today's date
        - calendar: list of weeks for the current month
    """
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    current_day = now.day

    cal = calendar.monthcalendar(current_year, current_month)

    return {
        "year": current_year,
        "month": current_month,
        "day": current_day,
        "calendar": cal
    }

def get_month_name():
    return month_name

import calendar
from datetime import datetime

def generate_dashboard_calendar(year=None, month=None):
    """
    Generate the calendar for the specified month and year.
    Returns:
        - year: specified year
        - month: specified month
        - calendar: list of weeks for the month
    """
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    cal = calendar.monthcalendar(year, month)

    return {
        "year": year,
        "month": month,
        "calendar": cal,
    }
