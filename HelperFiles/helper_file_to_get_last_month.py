from datetime import datetime

def get_last_month() -> int:
    """Return the last month as an integer (1-12) used for naming the csv."""
    today = datetime.today()
    return today.month - 1 if today.month > 1 else 12