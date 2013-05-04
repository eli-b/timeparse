"""
Parse strings to time-, date-, datetime- or timedelta-objects of the datetime-module.
"""
import datetime
import re
import subprocess
import shlex
import argparse
import timeparser

import warnings
warnings.simplefilter('default')


LITTLE_ENDIAN = 10
BIG_ENDIAN = 20
MIDDLE_ENDIAN = 30

def set_today(date):
    """
    Calls timeparser.setToday.
    
    Args:
        date (datetime.date-obj):  new date for TODAY

    Raises TypeError if date is not a datetime.date-instance.
    """
    timeparser.setToday(date)

def get_today():
    """
    Returns timeparser.TODAY.
    """
    return timeparser.TODAY

def time_config(*args, **kwargs):
    """
    Calls timeparser.TimeFormats.config.

    Kwargs:
        seps (list):        separators formats are generated with
        figures (list):     list of three boolean that predicts how many
                            digits the formats have.
        allow_no_sep (bool):    allows formats without separators ('%d%m%y')
        microsec (bool):    if True also formats with '%f' for microseconds
                            are produced.
    """
    timeparser.TimeFormats.config(*args, **kwargs)

def date_config(*args, **kwargs):
    """
    Calls timeparser.DateFormats.config.

    Kwargs:
        seps (list):        separators formats are generated with
        figures (list):     list of three boolean that predicts how many
                            digits the formats have.
        allow_no_sep (bool):    allows formats without separators ('%d%m%y')
        allow_month_name (bool):    if True also '%b' and '%B' are used to
                                    produce formats.
        endian (int):               determines the order for dates (s.a.)

    Endianness is the order in which day, month and year constitutes a date.
    This module defines three constants:
    LITTLE_ENDIAN (little first):   day, month, year
    BIG_ENDIAN (biggest first):     year, month, day
    MIDDLE_ENDIAN (middle first):   month, day, year
    Use one of these constants as value for the endian-parameter.
    """
    timeparser.DateFormats.config(*args, **kwargs)

def datetime_config(*args, **kwargs):
    """
    Calls timeparser.DatetimeFormats.config.

    Kwargs:
        seps (list):        separators formats are generated with
        allow_no_sep (bool):    allows formats without separators ('%d%m%y')
    """
    timeparser.DatetimeFormats.config(*args, **kwargs)


class TimeArgsMixin:
    def combine_datetime(self, datestring, timestring):
        date = timeparser.parsedate(datestring)
        time = timeparser.parsetime(timestring)
        return datetime.datetime.combine(date, time)

    def time_or_datetime(self, values):
        if len(values) == 1: return timeparser.parsetime(values[0])
        elif len(values) == 2: return self.combine_datetime(*values)
        else: raise ValueError("'%s' couldn't be parsed as time or datetime" % values)

    def append(self, namespace, obj):
        if getattr(namespace, self.dest):
            getattr(namespace, self.dest).append(obj)
        else:
            setattr(namespace, self.dest, [obj])

    #TODO: use cls.ERR_MSG and raise it on place
    def raiseArgumentError(self, which, args):
        raise argparse.ArgumentError(
            self,
            "'%s' couldn't be parsed as %s" % (' '.join(args), which)
            )



class ParseTime(argparse.Action, TimeArgsMixin):
    """argparse-argument-action to parse cmdline-parameters as time-object.

    usage:
        import argparse
        import timeparse

        parser = argparse.ArgumentParser(prog='PROG')
        parser.add_argument(
            '--time',
            action=timeparse.ParseTime
            )
        parser.parse_args('--time 23:20:33'.split()).time
        #this will be: datetime.time(23, 20, 33)
    """
    def __call__(self, parser, namespace, values, option_string=None):
        value = ' '.join(values) if isinstance(values, list) else values
        try: time = timeparser.parsetime(value)
        except ValueError: self.raiseArgumentError('time', values)
        else: setattr(namespace, self.dest, time)


class ParseDate(argparse.Action, TimeArgsMixin):
    """argparse-argument-action to parse cmdline-parameters as date-object.

    usage:
        import argparse
        import timeparse

        parser = argparse.ArgumentParser(prog='PROG')
        parser.add_argument(
            '--date',
            action=timeparse.ParseDate
            )
        parser.parse_args('--date 24/04/2013'.split()).date
        #this will be: datetime.date(2013, 4, 24)
    """
    def __call__(self, parser, namespace, values, option_string=None):
        value = ' '.join(values) if isinstance(values, list) else values
        try: date = timeparser.parsedate(value)
        except ValueError: self.raiseArgumentError('date', values)
        else: setattr(namespace, self.dest, date)


class ParseTimedelta(argparse.Action, TimeArgsMixin):
    """argparse-argument-action to parse cmdline-parameters as timedelta-object.

    usage:
        import argparse
        import timeparse

        parser = argparse.ArgumentParser(prog='PROG')
        parser.add_argument(
            '--days',
            action=timeparse.ParseTimedelta
            )
        parser.parse_args('--days 20 12 4'.split()).days
        #this will be: datetime.timedelta(20, 43440).

    The dest-property of argparse.Action (which is mostly the literal part of
    the option-string) is passed to parsetimedelta as key. So that in the exemple
    above the values 20, 12 and 4 are interpreted as 20 days, 12 hours and 4 min.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        value = ' '.join(values) if isinstance(values, list) else values
        try: timedelta = timeparser.parsetimedelta(value, self.dest)
        except ValueError: self.raiseArgumentError('timedelta', values)
        else: setattr(namespace, self.dest, timedelta)


class ParseDatetime(argparse.Action, TimeArgsMixin):
    """argparse-argument-action to parse cmdline-parameters as datetime-object.

    usage:
        import argparse
        import timeparse

        parser = argparse.ArgumentParser(prog='PROG')
        parser.add_argument(
            '--datetime',
            action=timeparse.ParseDatetime
            )
        parser.parse_args('--datetime 24/04/2013 23:22'.split()).datetime
        #this will be: datetime.datetime(2013, 4, 24, 23, 22)
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = values if isinstance(values, list) else [values]
        try:
            if len(values) == 2: datetime = self.combine_datetime(*values)
            else: datetime = timeparser.parsedatetime(' '.join(values))
        except ValueError: self.raiseArgumentError('datetime', values)
        else: setattr(namespace, self.dest, datetime)


class ParseTimeOrDatetime(argparse.Action, TimeArgsMixin):
    """argparse-argument-action to parse cmdline-parameters as datetime-object.

    usage:
        import argparse
        import timeparse

        parser = argparse.ArgumentParser(prog='PROG')
        parser.add_argument(
            '--time-or-datetime',
            action=timeparse.ParseTimeOrDatetime
            )
        parser.parse_args('--time-or-datetime 24/04/2013 23:22'.split()).time_or_datetime
        #this will be: datetime.datetime(2013, 4, 24, 23, 22)

        parser.parse_args('--time-or-datetime 23:22'.split()).time_or_datetime
        #and this will just be: datetime.time(23, 22)
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = values if isinstance(values, list) else [values]
        try: obj = self.time_or_datetime(values)
        except ValueError: self.raiseArgumentError('time or datetime', values)
        else: setattr(namespace, self.dest, obj)


class AppendTime(argparse.Action, TimeArgsMixin):
    """
    Like ParseTime with support for multiple use of arguments.

    usage:
        import argparse
        import timeparse

        parser = argparse.ArgumentParser(prog='PROG')
        parser.add_argument(
            '--time',
            action=timeparse.ParseTime
            )
        parser.parse_args('--time 23:20:33 --time 22:20'.split()).time
        #this will be: [datetime.time(23, 20, 33), datetime.time(22, 20)]
    """
    def __call__(self, parser, namespace, values, option_string=None):
        value = ' '.join(values) if isinstance(values, list) else values
        try: time = timeparser.parsetime(value)
        except ValueError: self.raiseArgumentError('time', values)
        else: self.append(namespace, time)


class AppendDate(argparse.Action, TimeArgsMixin):
    """
    Like ParseDate with support for multiple use of arguments.

    usage:
        import argparse
        import timeparse

        parser = argparse.ArgumentParser(prog='PROG')
        parser.add_argument(
            '--date',
            action=timeparse.ParseTime
            )
        parser.parse_args('--date 23.4.13 --date 24.4.13'.split()).date
        #this will be: [datetime.date(2013, 4, 23), datetime.date(2013, 4, 24)]
    """
    def __call__(self, parser, namespace, values, option_string=None):
        value = ' '.join(values) if isinstance(values, list) else values
        try: date = timeparser.parsedate(value)
        except ValueError: self.raiseArgumentError('date', values)
        else: self.append(namespace, date)


class AppendTimedelta(argparse.Action, TimeArgsMixin):
    """
    Like ParseTimedelta with support for multiple use of arguments.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        value = ' '.join(values) if isinstance(values, list) else values
        try: timedelta = timeparser.parsetimedelta(value)
        except ValueError: self.raiseArgumentError('timedelta', values)
        else: self.append(namespace, timedelta)


class AppendDatetime(argparse.Action, TimeArgsMixin):
    """
    Like ParseDatetime with support for multiple use of arguments.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = values if isinstance(values, list) else [values]
        try:
            if len(values) == 2: datetime = self.combine_datetime(*values)
            else: datetime = timeparser.parsedatetime(' '.join(values))
        except ValueError: self.raiseArgumentError('datetime', values)
        else: self.append(namespace, datetime)


class AppendTimeOrDatetime(argparse.Action, TimeArgsMixin):
    """
    Like ParseTimeOrDatetime with support for multiple use of arguments.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        values = values if isinstance(values, list) else [values]
        try: obj = self.time_or_datetime(values)
        except ValueError: self.raiseArgumentError('time or datetime', values)
        else: self.append(namespace, obj)


#These classes are for backward-compatibility:

class DeprecationClasses:
    MSG = "%s is deprecated. Use %s instead."

class ParseTimeDelta(argparse.Action, TimeArgsMixin, DeprecationClasses):
    """
    Like ParseTimedelta with support for multiple use of arguments.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        warnings.warn(self.MSG % (
            'timeparse.ParseTimeDelta',
            'timeparse.ParseTimedelta'
            ), DeprecationWarning)
        value = ' '.join(values) if isinstance(values, list) else values
        try: timedelta = timeparser.parsetimedelta(value, self.dest)
        except ValueError: self.raiseArgumentError('timedelta', values)
        else: setattr(namespace, self.dest, timedelta)


class ParseDateTime(argparse.Action, TimeArgsMixin, DeprecationClasses):
    """
    Like ParseDatetime with support for multiple use of arguments.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        warnings.warn(self.MSG % (
            'timeparse.ParseDateTime',
            'timeparse.ParseDatetime'
            ), DeprecationWarning)
        values = values if isinstance(values, list) else [values]
        try:
            if len(values) == 2: datetime = self.combine_datetime(*values)
            else: datetime = timeparser.parsedatetime(' '.join(values))
        except ValueError: self.raiseArgumentError('datetime', values)
        else: setattr(namespace, self.dest, datetime)


class ParseDateTimeOrTime(argparse.Action, TimeArgsMixin, DeprecationClasses):
    """
    Like ParseTimeOrDatetime with support for multiple use of arguments.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        warnings.warn(self.MSG % (
            'timeparse.ParseDateTimeOrTime',
            'timeparse.ParseTimeOrDatetime'
            ), DeprecationWarning)
        values = values if isinstance(values, list) else [values]
        try: obj = self.time_or_datetime(values)
        except ValueError: self.raiseArgumentError('time or datetime', values)
        else: setattr(namespace, self.dest, obj)


class AppendTimeDelta(argparse.Action, TimeArgsMixin, DeprecationClasses):
    """
    Like ParseTimedelta with support for multiple use of arguments.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        warnings.warn(self.MSG % (
            'timeparse.AppendTimeDelta',
            'timeparse.AppendTimedelta'
            ), DeprecationWarning)
        value = ' '.join(values) if isinstance(values, list) else values
        try: timedelta = timeparser.parsetimedelta(value)
        except ValueError: self.raiseArgumentError('timedelta', values)
        else: self.append(namespace, timedelta)


class AppendDateTime(argparse.Action, TimeArgsMixin, DeprecationClasses):
    """
    Like ParseDatetime with support for multiple use of arguments.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        warnings.warn(self.MSG % (
            'timeparse.AppendDateTime',
            'timeparse.AppendDatetime'
            ), DeprecationWarning)
        values = values if isinstance(values, list) else [values]
        try:
            if len(values) == 2: datetime = self.combine_datetime(*values)
            else: datetime = timeparser.parsedatetime(' '.join(values))
        except ValueError: self.raiseArgumentError('datetime', values)
        else: self.append(namespace, datetime)


class AppendDateTimeOrTime(argparse.Action, TimeArgsMixin, DeprecationClasses):
    """
    Like ParseTimeOrDatetime with support for multiple use of arguments.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        warnings.warn(self.MSG % (
            'timeparse.AppendDateTimeOrTime',
            'timeparse.AppendTimeOrDatetime'
            ), DeprecationWarning)
        values = values if isinstance(values, list) else [values]
        try: obj = self.time_or_datetime(values)
        except ValueError: self.raiseArgumentError('time or datetime', values)
        else: self.append(namespace, obj)




