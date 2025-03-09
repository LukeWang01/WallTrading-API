import datetime
import pytz


def is_market_hours():
    # current_time = datetime.datetime.now().time()
    # market_open_time = datetime.time(9, 30)  # Regular market open time (9:30 AM)
    # market_close_time = datetime.time(16, 0)  # Regular market close time (4:00 PM)
    #
    # if market_open_time <= current_time <= market_close_time:
    #     return True
    # else:
    #     return False

    # Sync the time zone with US Eastern Time.
    # Define the US Eastern Time zone
    # Get US Eastern timezone
    et_tz = pytz.timezone('America/New_York')

    # Get current time in ET
    current_et = datetime.datetime.now(et_tz)
    current_et_time = current_et.time()

    # Define market hours in ET
    market_open_time = datetime.datetime.strptime('09:30', '%H:%M').time()
    market_close_time = datetime.datetime.strptime('16:00', '%H:%M').time()

    # Check if within market hours
    return market_open_time <= current_et_time <= market_close_time


def is_market_and_extended_hours():
    # Get US Eastern timezone
    et_tz = pytz.timezone('America/New_York')

    # Get current time in ET
    current_et = datetime.datetime.now(et_tz)
    current_et_time = current_et.time()

    trade_open_time = datetime.time(4, 0)  # Regular market open time (4:00 AM)
    trade_close_time = datetime.time(20, 0)  # Regular market close time (20:00 PM)

    if trade_open_time <= current_et_time <= trade_close_time:
        return True
    return False


def get_current_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + f'{current_time.microsecond // 1000:03d} ms'
    return formatted_time
