from datetime import datetime, timedelta

def get_last_month_dates() -> tuple[str,str]:
    """
    Get the first and last day of the previous month.
    """
    today = datetime.now()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)
    return first_day_of_last_month.strftime("%Y-%m-%d"), last_day_of_last_month.strftime("%Y-%m-%d")