__all__ = ['PeriodSet', 'Period']

import re
from .parsers import T, TR, TD


class Period:
    def __init__(self, *args, **kwargs):
        try:
            if 'beg' in kwargs and 'end' in kwargs:
                self.beg, self.end = T(kwargs['beg']), T(kwargs['end'])
            elif len(args) == 1:
                arg = args[0]
                if isinstance(arg, str):
                    self.beg, self.end = self._parse_str(arg)
                else:
                    assert len(arg) == 2
                    self.beg, self.end = T(arg[0]), T(arg[1])
            else:
                assert len(args) == 2
                self.beg, self.end = T(args[0]), T(args[1])
            assert self.beg <= self.end
        except Exception as e:
            raise ValueError(f'Invalid args/kwargs for Period: {args}, {kwargs}')

    @staticmethod
    def _parse_str(s):
        beg, end = re.split(r'[-:]', s, 1)
        return T(beg.strip()), T(end.strip())

    def __str__(self):
        return self.to_str()

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.to_str()}>'

    def to_str(self, sep=':', time_format=None):
        if time_format is None:
            beg_str = self._get_simple_dtstr(self.beg)
            end_str = self._get_simple_dtstr(self.end)
        else:
            beg_str = self.beg.strftime(time_format)
            end_str = self.end.strftime(time_format)
        return beg_str + sep + end_str

    @staticmethod
    def _get_simple_dtstr(dt):
        s = dt.strftime('%Y%m%d%H%M%S')
        while s.endswith('00'):
            s = s[:-2]
        return s


class PeriodSet:
    """PeriodSet
    str format: {BEG}:{END}[,{BEG2}:{END2}[...]]
    """

    def __init__(self, *args):
        periods = []
        for arg in args:
            if arg is None:
                continue
            elif isinstance(arg, PeriodSet):
                periods.extend(arg.periods)
            elif isinstance(arg, Period):
                periods.append(arg)
            elif isinstance(arg, str):
                for part in arg.split(','):
                    periods.append(Period(part))
            else:
                periods.append(Period(arg))
        self.periods = self.straighten_periods(periods)

    @property
    def singular(self):
        return len(self.periods) == 1

    @property
    def beg(self):
        if not self.periods:
            return None
        else:
            return self.periods[0].beg

    @property
    def end(self):
        if not self.periods:
            return None
        else:
            return self.periods[-1].end

    def iter(self, freq):
        delta = TD(freq)
        for period in self.periods:
            yield from iter(TR(period.beg, period.end, delta))

    def __iter__(self):
        return iter(self.periods)

    def __bool__(self):
        return len(self.periods) > 0

    @staticmethod
    def straighten_periods(periods):
        if len(periods) <= 1:
            return periods

        ordered = list(sorted(periods, key=lambda s: s.beg))
        result = []
        current = ordered[0]
        for next in ordered[1:]:
            if next.beg <= current.end:
                current = Period(current.beg, next.end)
            else:
                result.append(current)
                current = next
        result.append(current)

        return result

    def __add__(self, other):
        return self.__class__(*self.periods, *other.periods)

    def to_str(self, sep=':', time_format=None):
        return ','.join([p.to_str(sep=sep, time_format=time_format) for p in self.periods])

    def __str__(self):
        return self.to_str()

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.to_str()}>'
