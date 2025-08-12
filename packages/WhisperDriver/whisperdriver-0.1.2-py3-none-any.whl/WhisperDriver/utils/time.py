import os

def get_hour_minute_ampm_format():
    """
    Returns the strftime/strptime format string for hour:minute AM/PM (cross-platform, always valid for strptime).
    Use '%I:%M %p' for parsing times with strptime.
    """
    return '%I:%M %p'
