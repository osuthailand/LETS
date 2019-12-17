def zingonify(d):
    """
    Zingonifies a string

    :param d: input dict
    :return: zingonified dict as str
    """
    return "|".join(f"{k}:{v}" for k, v in d.items())

def clamp(x, min_, max_):
    return max(min(x, max_), min_)

def toDotTicks(unixTime):
    '''
    Thanks to osukurikku's LETS
    Commit ID: 0a8236463242ea56ddb93c1f7823a5e39cd69911

    :param unixTime: unixTimeStamp
    '''
    unixStamp = datetime.datetime.fromtimestamp(unixTime)
    base = datetime.datetime(1, 1, 1, 0, 0, 0)
    delt = unixStamp-base
    return int(delt.total_seconds())*10000000
