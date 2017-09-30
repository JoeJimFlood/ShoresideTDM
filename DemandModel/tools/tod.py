from __future__ import division

def convert_time_format(t):
    '''
    Converts time from a decimal hour format to hh:mm

    Parameters
    ----------
    t (float):
        Time of day in decimal hours

    Returns
    -------
    hhmm (str):
        Time of day in hh:mm format
    '''
    minute_map = {0: '00', 0.25: '15', 0.5: '30', 0.75: '45'}
    hour = str(int(t // 1) % 24)
    hour = (2 - len(hour))*'0' + hour
    minute = minute_map[t % 1]
    return "'{0}:{1}".format(hour, minute)

def quarterhourize(minute):
    '''
    Converts a minute since midnight to a quarter hour since midnight. Rounds down.

    Parameters
    ----------
    minute (int):
        Number of minutes since midnight

    Returns
    -------
    quarter_hour (float):
        Time of day to the nearest quarter-hour (0.0, 0.25, 0.5, 0.75, 1.0, ..., 23.5, 23.75)
    '''
    hour = (minute // 60) % 24
    minute_in_hour = minute % 60
    proportion_of_hour = (minute_in_hour // 15) / 4
    quarter_hour = hour + proportion_of_hour
    
    return quarter_hour