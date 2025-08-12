import datetime
import logging

log = logging.getLogger(__name__)

def next_midnight(tz_info: datetime.tzinfo = None):
    """
    Calculate the datetime of the next midnight based on the provided timezone
    information. The function uses the current time and replaces the time
    components (hour, minute, second) to zero, then adds one day to determine
    the exact datetime of the next midnight.

    :param tz_info: The timezone information to be used for calculating the
        next midnight. Defaults to None, which will use the local timezone.
    :type tz_info: datetime.tzinfo, optional
    :return: A datetime object that represents the next midnight relative to
        the current time and given timezone.
    :rtype: datetime.datetime
    """
    dt = datetime.datetime.now(tz_info)
    dt = dt.replace(hour=0, minute=0, second=0)
    return dt + datetime.timedelta(days=1)



def cache_control_to_dict(cache_control_string: str|None)->dict:
    """
    Converts a cache control string into a dictionary representation.

    This function parses a cache control string and converts it into a dictionary
    object. If the input string is empty or None, an empty dictionary is returned.
    The function supports parsing key-value pairs as well as boolean flags without
    values. It also handles special handling of the 'max-age' directive by
    converting its value to an integer.

    :param cache_control_string: Input cache control string to be parsed.
    :type cache_control_string: str or None
    :return: A dictionary representation of the cache control directives.
    :rtype: dict
    """
    ret = {}
    if cache_control_string is None or len(cache_control_string.strip()) == 0:
        return ret

    comma_separated = [x.strip() for x in cache_control_string.split(",")]
    if len(comma_separated) == 0:
        return ret

    ret = {}
    for s in comma_separated:
        equal_split = [x.strip() for x in s.split("=")]
        key = equal_split[0]
        if len(key.strip()) == 0:
            continue
        elif len(equal_split) == 1:
            ret[key] = True
        else:
            value = equal_split[1]
            if key.lower() == "max-age":
                value = int(value)

            ret[key] = value

    return ret

def cache_control_to_string(cache_control_dict: dict)->str:
    """
    Converts a dictionary representing cache control directives into a string formatted
    according to HTTP headers' rules.

    Each key in the dictionary represents a directive name. If the value is a boolean and
    `True`, the key is included as a standalone directive in the result. If the value is not
    a boolean, the key is appended with an equals sign and its corresponding value, formatted
    as `key=value`.

    :param cache_control_dict: A dictionary where keys are directive names (str) and values
        are either booleans or strings. Boolean `True` values include the corresponding key
        without a value in the output string, while string values are included in key-value
        pairs.
    :type cache_control_dict: dict
    :return: A string representation of cache control directives suitable for HTTP headers.
    :rtype: str
    """
    cache_control_list = []
    for k,v in cache_control_dict.items():
        if isinstance(v, bool):
            if v:
                cache_control_list.append(k)
        else:
            cache_control_list.append(f"{k}={v}")
    return ", ".join(cache_control_list)
