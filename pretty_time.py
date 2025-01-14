from datetime import date, datetime

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.now()
    diff = now - datetime.fromtimestamp(time)
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff // 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff // 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff // 30) + " months ago"
    return str(day_diff // 365) + " years ago"

def shield_time(supplied_time):
    # if no time return immediatelly
    if supplied_time is None:
        return False
    
    # Get the current timestamp
    now = datetime.now()
    
    # Calculate the absolute difference in seconds
    time_difference = abs(now - supplied_time)  # Difference in seconds

    # Check if the difference is less than 4 hours (4 * 3600 seconds)
    return time_difference < 4 * 3600

def compare_dates(supplied_time, fr='%m/%d/%y %H.%M.%S'):
    supplied_obj = format(supplied_time, fr)
    now = datetime.now()

    if supplied_obj == now:
        print ('You a crazy mofo for tracking this jesus')
        return False
    elif supplied_obj > now:
        print ('We are still shielded, life is good')
        return True

    print ('Panik. Shield has expired')
    return False

def format(supplied_time, format='%m/%d/%y %H.%M.%S'):
    return datetime.strptime(supplied_time, format)
