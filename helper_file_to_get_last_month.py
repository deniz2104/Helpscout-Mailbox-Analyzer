from datetime import datetime

def get_last_month():
    today = datetime.today()
    return today.month - 1 if today.month > 1 else 12