__all__ = ['get_latest_neat_time', 'get_nearest_neat_time', 'get_neat_beg_end']

import re
from datetime import datetime, timedelta
from .parsers import TD


def _get_n(s):
    return 1 if s == '' else int(s)


def get_latest_neat_time(time=None, freq='1H'):
    """获取最新的一个整齐时点
    :param time: 不提供时, 默认从当前时间算起
    :param freq:
    :return:
    """
    result = None
    if time is None:
        time = datetime.now()

    if m := re.match(r'^(\d*)(T|m|min)$', freq):
        n = _get_n(m.group(1))
        minute = (time.minute // n) * n
        result = time.replace(minute=minute, second=0, microsecond=0)
    elif m := re.match(r'^(\d*)([Hh])$', freq):
        n = _get_n(m.group(1))
        hour = (time.hour // n) * n
        result = time.replace(hour=hour, minute=0, second=0, microsecond=0)
    elif freq in ('d', 'D', '1d', '1D'):
        result = time.replace(hour=0, minute=0, second=0, microsecond=0)
    elif m := re.match(r'^(\d*)M$', freq):
        n = _get_n(m.group(1))
        month = ((time.month - 1) // n) * n + 1
        result = time.replace(month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif m := re.match(r'^(\d*)Y$', freq):
        n = _get_n(m.group(1))
        year = (time.year // n) * n
        result = time.replace(year=year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    if result is None:
        raise NotImplementedError(f"get_latest_neat_time of freq {freq} not implemented!")

    return result


def get_nearest_neat_time(time=None, freq='1H'):
    """获取距离最近的一个整齐时点
    :param time: 不提供时, 默认从当前时间算起
    :param freq:
    """
    if time is None:
        time = datetime.now()

    result = get_latest_neat_time(time=time, freq=freq)
    if m := re.match(r'^(\d*)M$', freq):
        n = _get_n(m.group(1))
        half_days = timedelta(days=int(31 * n / 2))
        if time - result >= half_days:
            result = result + TD(freq)
    elif m := re.match(r'^(\d*)Y$', freq):
        n = _get_n(m.group(1))
        half_days = timedelta(days=int(365 * n / 2))
        if time - result >= half_days:
            result = result + TD(freq)
    else:
        tdelta = TD(freq)
        if time - result > tdelta / 2:
            result = result + tdelta

    return result


def get_neat_beg_end(beg=None, end=None, freq='1H', offset=0, periods=1):
    """获取整齐的起止时间
    :param beg:
    :param end:
    :param freq:
    :param offset: 将结果平移几个周期
    :param periods: 当没有提供beg时, 给出时长为几个周期的时段
    """
    t_delta = TD(freq)
    neat_end = get_latest_neat_time(end, freq)
    neat_beg = neat_end - t_delta * periods if beg is None else get_latest_neat_time(beg, freq)
    if offset != 0:
        neat_beg += t_delta * offset
        neat_end += t_delta * offset
    return neat_beg, neat_end
