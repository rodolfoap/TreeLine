#!/usr/bin/env python

#****************************************************************************
# gentime.py, provides a class for time formating
#
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import re
import time
import types


class GenTime(object):
    """Stores & formats time values"""
    amStr = _('am')
    pmStr = _('pm')
    ampmRegExp = re.compile('(.+)(%s|%s|a|p)' % (amStr[0], pmStr[0]))
    formatChooser = {'HH':'hour', 'H':'hour', 'hh':'hour12', 'h':'hour12',
                     'MM':'minute', 'M':'minute', 'SS':'intSecond',
                     'S':'intSecond', 'sss':'milliSecond', 'ss':'milliSecond',
                     's':'milliSecond', 'AA':'AMPM', 'A':'AMPM',
                     'aa':'ampm', 'a':'ampm'}
    timeType = type(time.localtime())

    def __init__(self, time=None):
        """Accepts one of the following to initialize:
               1. None - sets to current time
               2. tuple in (h, m, [s]) - or localtime/gmtime
               3. string in (h:m[:s]) format
               4. number of seconds (int or float)
               5. GenTime instance"""
        if time == None:
            self.setToCurrent()
        else:
            self.setTime(time)

    def setToCurrent(self, gmt=0):
        """Set date to current values, local or GMT"""
        if gmt:
            self.setTime(time.gmtime())
        else:
            self.setTime(time.localtime())

    def setTime(self, time):
        """Sets the time value from a tuple (h, m, [s]), a localtime/gmtime
           tuple, a string (h:m[:s]), number of seconds (int or float),
           or a GenTime instance"""
        ampm = ''
        inType = type(time)
        if inType in (types.TupleType, types.ListType, GenTime.timeType):
            if len(time) >= 6:
                self.time = list(time[3:6])
            else:
                self.time = list(time[:3])
        elif inType in (types.StringType, types.UnicodeType):
            self.time = re.split(':', time)[:3]
            ampmMatch = GenTime.ampmRegExp.match(self.time[-1].lower())
            if ampmMatch:
                self.time[-1], ampm = ampmMatch.groups()
        elif inType in (types.IntType, types.FloatType):
            self.time = [0, 0, time]
        elif inType is type(self):
            self.time = time.time
        else:
            raise GenTimeError('Invalid time type')
        self._normalize()
        if (ampm == GenTime.amStr[0] or ampm == 'a') and self.time[0] == 12:
            self.time[0] = 0
        elif (ampm == GenTime.pmStr[0] or ampm == 'p') and self.time[0] < 12:
            self.time[0] += 12

    def timeStr(self, format='HH:MM:SS'):
        """Return string based on the format, which includes series of
           'H' (24 hr), 'h' (12 hr), 'M', 'S' (int), 's' (fract part), 
           'A' (AM/PM), 'a' (am/pm) repeated to indicate length.  
           Backslashes will escape these letters"""
        exp = r'((?<!\\)H+|(?<!\\)h+|(?<!\\)M+|'
        exp += r'(?<!\\)S+|(?<!\\)s+|(?<!\\)A+|(?<!\\)a+)'
        return ''.join([self._substitute(part) for part in
                        re.split(exp, format)])

    def _substitute(self, format):
        """Return string eqivalent of formatItem or return format"""
        try:
            result = str(getattr(self, GenTime.formatChooser[format])())
            if format.startswith('s'):
                while len(result) < 3:
                    result = '0' + result
                result = result[:len(format)]
            elif len(format) == 2 and len(result) == 1:
                result = '0' + result
            elif format in ('a', 'A'):
                result = result[:1]
            return result
        except KeyError:
            return re.sub(r'\\(?!\\)', '', format)   # remove escape slashes

    def hour(self):
        """Return int hour value (24 hour clock)"""
        return self.time[0]
    
    def hour12(self):
        """Return int hour value from 12 hour clock"""
        hour = self.time[0]
        if hour > 12:
            hour -= 12
        elif hour == 0:
            hour = 12
        return hour

    def minute(self):
        """Return int minute value"""
        return self.time[1]

    def second(self):
        """Return float seconds value"""
        return self.time[2]

    def intSecond(self):
        """Return truncated seconds value"""
        return int(self.time[2])

    def milliSecond(self):
        """Return int for 1/1000 of a second"""
        return int((self.time[2] - self.intSecond()) * 1000)

    def AMPM(self):
        """Return string for AM or PM"""
        if self.time[0] < 12:
            return GenTime.amStr.upper()
        return GenTime.pmStr.upper()

    def ampm(self):
        """Return string for am or pm"""
        if self.time[0] < 12:
            return GenTime.amStr
        return GenTime.pmStr

    def toTuple(self):
        """Return (h, m, s) tuple"""
        return self.time

    def totalSeconds(self):
        """Return total number of seconds since midnight as a float"""
        return self.time[0] * 3600 + self.time[1] * 60 + self.time[2]

    def _normalize(self):
        """Adjust time values to normal ranges and verify value formats"""
        while len(self.time) < 3:
            self.time.append(0.0)
        try:
            self.time = [float(value) for value in self.time]
        except ValueError:
            raise GenTimeError('Invalid time format')
        totalSec = self.totalSeconds()
        self.time[2] = totalSec % 60
        self.time[1] = int(totalSec) / 60 % 60
        self.time[0] = int(totalSec) / 3600 % 24

    def clone(self):
        """Return cloned instance"""
        return self.__class__(self.time)

    def __repr__(self):
        """Outputs in format HH:MM:SS"""
        return '%02d:%02d:%02d' % (self.hour(), self.minute(),
                                   self.intSecond())

    def __cmp__(self, other):
        """Compare operator"""
        if other is None or not isinstance(other, GenTime):
            return 1
        return cmp(self.totalSeconds(), other.totalSeconds())

    def __hash__(self):
        """Allow use as dictionary key"""
        return hash(self.totalSeconds())

    def __add__(self, seconds):
        """Addition operator, adds seconds to time
           Caution: no knowledge of date, wrapping will occur"""
        if not type(seconds) in (types.IntType, types.FloatType):
            raise GenTimeError('Add operator requires a number of seconds')
        copy = self.clone()
        copy.time[2] += seconds
        copy._normalize()
        return copy

    def __radd__(self, seconds):
        """Addition operator"""
        return self.__add__(seconds)

    def __sub__(self, other):
        """Subtraction operator for time (returns seconds) or 
           num seconds (returns time)
           Caution: no knowledge of date, wrapping will occur"""
        if type(other) in (types.IntType, types.FloatType):
            return self.__add__(-other)
        return self.totalSeconds() - other.totalSeconds()

    def __rsub__(self, other):
        """Subtraction operator for time, returns num seconds"""
        if not isinstance(other, GenTime):
            raise GenTimeError('Cannot subtract a date from a number')
        return other.totalSeconds() - self.totalSeconds()


class GenTimeError(Exception):
    """Exception class for invalid time data"""
    pass


if __name__ == '__main__':
    gt = GenTime()
    print 'The time is', gt.timeStr('h:MM:SS aa')
