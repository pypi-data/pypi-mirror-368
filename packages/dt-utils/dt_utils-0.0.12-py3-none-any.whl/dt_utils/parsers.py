# -*- coding:utf-8 -*-

import six
import re
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import numpy as np
from .common import return_as_type

__all__ = ['parse_datetime', 'parse_timedelta', 'datetime_range', 'T', 'TD', 'TR', 'datetime', 'timedelta', 'date', 'relativedelta']


def parse_datetime(timestr, force_datetime=True):
    """Try parse timestr or integer or list of str/integer into datetimes
    timestr: single value or seq of:
                int/str: YYYYMMDD[HH[MM[SS]]] , delimiters are also allowed,
                    e.g.: YYYY-MM-DD HH:MM:SS.
                    Julian Days, e.g., YYYYJJJ[...] is also OK.
                datetime/date
    force_datetime:
                if True: return datetime even if input is date.
                if False: return date if input is date.
    """
    numonly_pattern = re.compile(r'\D*')
    jfmtstr_all = '%Y%j%H%M%S'
    gfmtstr_all = '%Y%m%d%H%M%S'

    if isinstance(timestr, (list, tuple)):
        timestrs = timestr
        return_type = 'list'
    elif isinstance(timestr, np.ndarray):
        timestrs = timestr
        return_type = 'np_arr'
    else:
        timestrs = [timestr]
        return_type = 'scalar'

    res_list = []
    for timestr in timestrs:
        if isinstance(timestr, (datetime, )):
            res_list.append(timestr)
            continue
        if isinstance(timestr, (date, )):
            if force_datetime == True:
                res_list.append(datetime.fromordinal(timestr.toordinal()))
            else:
                res_list.append(timestr)
            continue
        if isinstance(timestr, six.integer_types + (np.integer, )):
            timestr = str(timestr)

        # handle year or year-month format like YYYY, YYYY-mm etc
        if re.match(r'^\d{4}$', timestr):  # year
            timestr = timestr + '0101'
        else:
            month_m = re.match(r'^(\d{4})([\t\n\r\f-/]*)(\d{2})$', timestr)
            if month_m:
                timestr = '{}{}01'.format(month_m.group(1), month_m.group(3))

        if len(timestr) == 10:
            if re.match(r'^\d{10}$', timestr):
                timestr = timestr + '00'
            elif re.match(r'^\d{4}.\d{2}.\d{2}$', timestr):
                timestr = timestr + ' 00:00:00'

        try:
            res = parse(timestr)
        except ValueError:
            try:
                numonly_str = re.sub(numonly_pattern, '', timestr)
                nl = len(numonly_str)
                if nl >= 7:
                    if nl % 2 == 1:   #YYYYJJJ[...]
                        fmtstr = jfmtstr_all[:4+nl-7]
                    else:             #YYYYMMDD[...]
                        fmtstr = gfmtstr_all[:6+nl-8]
                    res = datetime.strptime(numonly_str, fmtstr)
                else:
                    res = parse(numonly_str)
            except Exception:
                res = None
        res_list.append(res)

    return return_as_type(res_list, return_type)


_tdelta_dict = {
    'd': 'days', 'h': 'hours', 'm': 'minutes', 's': 'seconds',  # legacy formats
    # pandas freq compatible
    'T': 'minutes', 'min': 'minutes',
    'H': 'hours', 'D': 'days', 'S': 'seconds',
}
_rel_tdelta_dict = {'Y': 'years', 'M': 'months', 'W': 'weeks'}
def parse_timedelta(timestr):
    """Try parse single value or seq of timestr/integer/timedelta into timedeltas.
    e.g. parse_timedelta(['30m', '2h', '1d', '15s', '2:30', '1:12:25']).
    Y: years
    M: months
    W: weeks
    d, D: days
    h, H: hours
    m, min, T: minutes
    s, S: seconds (default)
    """
    if isinstance(timestr, (list, tuple)):
        timestrs = timestr
        return_type = 'list'
    elif isinstance(timestr, np.ndarray):
        timestrs = timestr
        return_type = 'np_arr'
    else:
        timestrs = [timestr]
        return_type = 'scalar'

    res_list = []
    for timestr in timestrs:
        if timestr is None:
            res_list.append(None)
            continue
        if isinstance(timestr, (timedelta, relativedelta)):
            res_list.append(timestr)
            continue
        if isinstance(timestr, six.integer_types + (np.integer, )):
            timestr = str(timestr)
        timestr = timestr.strip()

        if ':' in timestr:
            tokens = timestr.split(':')
            seconds = 0
            for i, tk in enumerate(reversed(tokens)):
                seconds += int(tk) * (60 ** i)
            res = timedelta(seconds=seconds)
            res_list.append(res)
            continue

        m = re.match(r'([-+0-9]*)([A-Za-z]*)', timestr)
        if not m:
            res = None
        else:
            if m.group(1) == '':
                value = 1
            else:
                value = int(m.group(1))
            symbol = m.group(2)
            if symbol in _rel_tdelta_dict:
                res = relativedelta(**{_rel_tdelta_dict[symbol]: value})
            else:
                if symbol == '':
                    symbol = 's'
                key = _tdelta_dict.get(symbol)
                if key is None:
                    res = None
                else:
                    res = timedelta(**{key: value})
        res_list.append(res)

    return return_as_type(res_list, return_type)


def datetime_range(beg, end=None, tdelta='1h'):
    """Returns a list of datetimes from beg to end with tdelta.
    """
    if end is None:
        tokens = beg.split(':')
        beg = tokens[0]
        end = tokens[1]
        if len(tokens) >= 3:  # beg:end:td
            tdelta = tokens[2]

    if not isinstance(beg, datetime):
        beg = parse_datetime(beg)
    if not isinstance(end, datetime):
        end = parse_datetime(end)
    if not isinstance(tdelta, (timedelta, relativedelta)):
        tdelta = parse_timedelta(tdelta)
    result = []
    now = beg
    while now < end:
        result.append(now)
        now = now + tdelta
    return result


T = parse_datetime
TD = parse_timedelta
TR = datetime_range
