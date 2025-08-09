from datetime import datetime, timedelta

def calculate_age(birthdate: str, date_format="%Y-%m-%d") -> int:
    """
    Calculate age in years from birthdate.
    Example: calculate_age("2000-08-10")
    """
    birth = datetime.strptime(birthdate, date_format)
    today = datetime.today()
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))

def date_difference(start: str, end: str, date_format="%Y-%m-%d") -> dict:
    """
    Return difference between two dates in days, weeks, months approx.
    Example: date_difference("2020-01-01", "2025-01-01")
    """
    d1 = datetime.strptime(start, date_format)
    d2 = datetime.strptime(end, date_format)
    delta = abs(d2 - d1)
    return {
        "days": delta.days,
        "weeks": round(delta.days / 7, 2),
        "months": round(delta.days / 30.44, 2), 
        "years": round(delta.days / 365.25, 2)
    }

def get_weekday(date_str: str, date_format="%Y-%m-%d") -> str:
    """
    Return weekday name for a given date.
    Example: get_weekday("2025-08-10") -> "Sunday"
    """
    date = datetime.strptime(date_str, date_format)
    return date.strftime("%A")

def add_days(date_str: str, days: int, date_format="%Y-%m-%d") -> str:
    """
    Add days to a given date and return new date.
    Example: add_days("2025-08-08", 10) -> "2025-08-18"
    """
    date = datetime.strptime(date_str, date_format)
    new_date = date + timedelta(days=days)
    return new_date.strftime(date_format)
