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

def compare_dates(supplied_time, fr='%m/%d/%y %H.%M.%S'):
    # if we pass string convert it to datetime
    if isinstance(supplied_time, str):
        supplied_time = format(supplied_time, fr)

    supplied_obj = supplied_time
    now = datetime.now()

    if supplied_obj == now:
        print ('You a crazy mofo for tracking this jesus')
        return False
    elif supplied_obj > now:
        # shield is active we are gucci
        return True

    print ('Panik. Shield has expired')
    return False

def format(supplied_time, format='%m/%d/%y %H.%M.%S'):
    return datetime.strptime(supplied_time, format)
