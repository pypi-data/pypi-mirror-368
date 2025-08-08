__all__ = ['minimal_timestr', 'simple_timestr', 'TT']

from datetime import date, datetime
from .parsers import T
import numpy as np
from .common import return_as_type


def minimal_timestr(dt):
    if isinstance(dt, (list, tuple)):
        dts = dt
        return_type = 'list'
    elif isinstance(dt, np.ndarray):
        dts = dt
        return_type = 'np_arr'
    else:
        dts = [dt]
        return_type = 'scalar'

    res_list = []
    for dt in dts:
        if dt is None:
            res_list.append(None)
            continue

        if not isinstance(dt, date):
            dt = T(dt)
        timestr = dt.strftime('%Y%m%d%H%M%S')
        while timestr.endswith('00'):
            timestr = timestr[:-2]
        res_list.append(timestr)

    return return_as_type(res_list, return_type)


def simple_timestr(dt, freq=None, minimal=True):
    if isinstance(dt, (list, tuple)):
        dts = dt
        return_type = 'list'
    elif isinstance(dt, np.ndarray):
        dts = dt
        return_type = 'np_arr'
    else:
        dts = [dt]
        return_type = 'scalar'

    if freq is None:
        freq = ''

    if freq.endswith(('T', 'min', 'm')):
        time_format = '%Y%m%d%H%M' if minimal else '%Y-%m-%d %H:%M'
    elif freq.endswith(('H', 'h')):
        time_format = '%Y%m%d%H' if minimal else '%Y-%m-%d %H'
    elif freq.endswith(('D', 'd')):
        time_format = '%Y%m%d' if minimal else '%Y-%m-%d'
    elif freq.endswith(('M', 'MS')):
        time_format = '%Y%m' if minimal else '%Y-%m'
    elif freq.endswith('Y'):
        time_format = '%Y'
    else:
        time_format = '%Y%m%d%H%M%S' if minimal else '%Y-%m-%d %H:%M:%S'

    res_list = []
    for dt in dts:
        if dt is None:
            res_list.append(None)
            continue

        if not isinstance(dt, date):
            dt = T(dt)
        res_list.append(dt.strftime(time_format))

    return return_as_type(res_list, return_type)


# 什么时候加的这个?
def TT(dt):
    if isinstance(dt, (list, tuple)):
        dts = dt
        return_type = 'list'
    elif isinstance(dt, np.ndarray):
        dts = dt
        return_type = 'np_arr'
    else:
        dts = [dt]
        return_type = 'scalar'

    result = []
    for item in dts:
        if item is None:
            result.append(None)
        elif isinstance(item, datetime):
            result.append(item.strftime("%Y-%m-%d %H:%M:%S"))
        elif isinstance(item, date):
            result.append(item.strftime("%Y-%m-%d"))
        else:
            result.append(T(item).strftime("%Y-%m-%d %H:%M:%S"))

    return return_as_type(result, return_type)
