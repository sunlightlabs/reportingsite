from datetime import date
from calendar import Calendar
from itertools import dropwhile

def election_cycle(dt):
    """Takes a datetime.date object and returns the election 
    cycle year (as an integer) for that date."""
    if dt.year % 2 == 0:
        if dt.month == 11:
            cal = Calendar()
            november_calendar = cal.itermonthdays2(dt.year, 11)
            is_october_day = lambda (dayofmonth, weekday): dayofmonth == 0
            november_days = dropwhile(is_october_day, november_calendar)
            is_monday = lambda (dayofmonth, weekday): weekday == 0
            is_not_monday = lambda daytuple: not is_monday(daytuple)
            election_tuesday = next(dropwhile(is_monday,
                                              dropwhile(is_not_monday, 
                                                        november_days)))
            election_date = date(dt.year, 11, election_tuesday[0])
            print election_tuesday
            print election_date
            if dt > election_date:
                return dt.year + 2
            else:
                return dt.year
        else:
            return dt.year
    else:
        return dt.year + 1

def current_election_cycle():
    """Returns the election cycle year (as an integer) for today's date."""
    return election_cycle(date.today())

