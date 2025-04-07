from dateutil.relativedelta import relativedelta

def get_last_day_of_month(date):
    """Returns the last day of the month for a given date."""
    next_month = date.replace(day=28) + relativedelta(days=4)
    return next_month - relativedelta(days=next_month.day)
