from datetime import datetime, timedelta

def get_last_month_dates() -> tuple[str,str]:
    """
    Get the first and last day of the previous month.
    """
    today = datetime.now()
    last_day_of_last_month = today.replace(day=1,hour = 0, minute= 0, second=0)
    first_day_of_last_month = (last_day_of_last_month - timedelta(days=1)).replace(day=1,hour = 23, minute = 59, second = 59)-timedelta(days=1)
    return first_day_of_last_month.strftime("%Y-%m-%d %H:%M:%S").strip(), last_day_of_last_month.strftime("%Y-%m-%d %H:%M:%S").strip()