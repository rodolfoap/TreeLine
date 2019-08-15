#!/usr/bin/env python

#****************************************************************************
# gendate.py, provides a class for date formating
#
# Copyright (C) 2008, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import re
import time
import types


class GenDate(object):
    """Stores & formats date values"""
    monthNames = [_('January'), _('February'), _('March'), _('April'),
                  _('May'), _('June'), _('July'), _('August'),
                  _('September'), _('October'), _('November'), _('December')]
    monthAbbrevs = [N_('Jan'), N_('Feb'), N_('Mar'), N_('Apr'),
                    N_('May', 'abbrev'), N_('Jun'), N_('Jul'), N_('Aug'),
                    N_('Sep'), N_('Oct'), N_('Nov'), N_('Dec')]
    monthChooser = dict([(mon.lower(), i+1) for i, mon in \
                         enumerate(monthAbbrevs)])
    monthAbbrevs = [_(name) for name in monthAbbrevs]
    monthAbbrevLengths = list(set([len(name) for name in monthAbbrevs] + [3]))
    monthAbbrevLengths.sort()
    monthAbbrevLengths.reverse()
    monthChooser.update(dict([(mon.lower(), i+1) for i, mon in \
                              enumerate(monthAbbrevs)]))
    dayOfWeekNames = [_('Sunday'), _('Monday'), _('Tuesday'), _('Wednesday'),
                      _('Thursday'), _('Friday'), _('Saturday')]
    dayOfWeekAbbrevs = [_('Sun'), _('Mon'), _('Tue'), _('Wed'), _('Thu'),
                        _('Fri'), _('Sat')]
    formatChooser = {'yyyy':'year', 'yy':'year2digit', 'mmmm':'monthName',
                     'mmm':'monthAbbrev', 'mm':'month', 'm':'month',
                     'dd':'day', 'd':'day', 'wwww':'dayOfWeekName',
                     'www':'dayOfWeekAbbrev', 'w':'dayOfWeek'}
    daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    daysTo1900 = 693597   # days from Jan 1, 0001 to Jan 1, 1900 baseline
    maxDays = 2958463
    minDays = -4345731
    yearWrap = 35         # assumed wrap point for 2-digit year input
    timeType = type(time.localtime())

    def __init__(self, genDate=None):
        """Accepts one of the following to initialize:
               1. None - sets to current day
               2. int or string in yyyymmdd format
               3. string in y/m/d sequence only with various 
                  separators (.-/,; or spaces) & formats of fields
               4. tuple in (y, m, d) - or localtime/gmtime
               5. GenDate instance"""
        if genDate == None:
            self.setToToday()
        else:
            self.setDate(genDate)

    def setToToday(self):
        """Set date to current values"""
        self.setDate(time.localtime())

    def setDate(self, genDate):
        """Sets the date value from int/str (yyyymmdd), string with various
           separators (.-/,; or spaces) in y/m/d order only, 
           tuple (y, m, d), or GenDate class"""
        inType = type(genDate)
        if inType is types.IntType:
            self.date = genDate
        elif inType in (types.StringType, types.UnicodeType):
            try:
                self.date = int(genDate)
            except ValueError:   # general separated string
                year, month, day = _parseDateStr(genDate)
                self.setFromCompStr(year, month, day)
        elif inType in (types.TupleType, types.ListType, GenDate.timeType):
            self.date = int("%04d%02d%02d" % genDate[:3])
        elif inType is type(self):
            self.date = genDate.date
        else:
            raise GenDateError('Invalid date type')
        self._validate()

    def setFromStr(self, dateStr, format='y/m/d'):
        """Sets the date value from string with seperators (.-/,; or spaces).
           format sets the order only (type of sep. & fields don't matter),
           2-digit year okay (till 2035)
           Returns self"""
        data = {}
        try:
            for pair in map(None, re.findall('y+|m+|d+', format),
                            _parseDateStr(dateStr)):
                data[pair[0][0]] = pair[1]
            self.setFromCompStr(data['y'], data['m'], data['d'])
        except (KeyError, TypeError):
            raise GenDateError('Invalid date string or format')
        return self

    def setFromCompStr(self, yearStr, monthStr, dayStr):
        """Sets the date value from individual strings"""
        try:
            year = int(yearStr)
            if 0 <= year < 100 and len(yearStr) == 2:
                if year < GenDate.yearWrap:
                    year += 2000
                else:
                    year += 1900
            if monthStr.isdigit():
                month = int(monthStr)
            else:
                month = self._monthFromName(monthStr)
            self.setDate((year, month, int(dayStr)))
        except (ValueError, KeyError, AttributeError):
            raise GenDateError('Invalid date string or format')

    def _monthFromName(self, monthStr):
        """Return month number from string abbreviation,
           raise ValueError if not found"""
        monthStr = monthStr.lower()
        for abbrevLength in GenDate.monthAbbrevLengths:
            month = GenDate.monthChooser.get(monthStr[:abbrevLength], 0)
            if month:
                return month
        raise ValueError

    def dateStr(self, format='yyyy/mm/dd'):
        """Return string based on the format, which includes series of
           'y', 'm', 'd', 'w', repeated to indicate length.  Backslashes
           will escape these letters"""
        return ''.join([self._substitute(part) for part in \
                        re.split(r'((?<!\\)y+|(?<!\\)m+|(?<!\\)d+|(?<!\\)w+)',
                        format)])

    def _substitute(self, format):
        """Return string eqivalent of formatItem or return format"""
        try:
            result = unicode(getattr(self, GenDate.formatChooser[format])())
            if len(format) == 2 and len(result) == 1:
                result = '0' + result
            return result
        except KeyError:
            return re.sub(r'\\(?!\\)', '', format)   # remove escape slashes

    def toTuple(self):
        """Return y, m, d tuple"""
        return (self.year(), self.month(), self.day())

    def year(self):
        """Return an int year, BC is negative"""
        return int(repr(self.date)[:-4])

    def year2digit(self):
        """Return int for last two digits of year - use at risk"""
        return int(repr(self.date)[-6:-4])

    def month(self):
        """Return month as int 1-12"""
        return int(repr(self.date)[-4:-2])

    def monthName(self):
        """Return full name of month"""
        return GenDate.monthNames[self.month() - 1]

    def monthAbbrev(self):
        """Return 3-letter month abbreviation"""
        return GenDate.monthAbbrevs[self.month() - 1]

    def day(self):
        """Return day (1-31)"""
        return int(repr(self.date)[-2:])

    def dayOfWeek(self):
        """Return int for day of week, Sunday is 0"""
        y, m, d = self.toTuple()
        if m < 3:
            m += 12
            y -= 1
        return (d + 1 + 2*m + 3*(m+1)/5 + y + y/4 - y/100 + y/400) % 7

    def dayOfWeekName(self):
        """Return the full name for the day of the week"""
        return GenDate.dayOfWeekNames[self.dayOfWeek()]

    def dayOfWeekAbbrev(self):
        """Return the abbreviation for the day of the week"""
        return GenDate.dayOfWeekAbbrevs[self.dayOfWeek()]

    def _validate(self):
        """Verify that the date values work"""
        if type(self.date) is not types.IntType:
            raise GenDateError('Invalid date type')
        try:
            year, month, day = self.toTuple()
        except ValueError:
            raise GenDateError('Invalid date values')
        if year < -9999 or year > 9999 or year == 0:
            raise GenDateError('Invalid year value')
        if month < 1 or month > 12:
            raise GenDateError('Invalid month value')
        if day < 1 or day > GenDate.daysInMonth[month - 1]:
            if month != 2 or day != 29 or not isLeapYear(year):
                raise GenDateError('Invalid day value')
        if year == 1582 and month == 10 and 4 < day < 15:
            raise GenDateError('Invalid day value, 10 days dropped in 1582')

    def baselineDays(self):
        """Days since baseline date of Jan. 1, 1900"""
        year, month, day = self.toTuple()
        days = firstDayOfYear(year)
        for m in range(month - 1):
            days += GenDate.daysInMonth[m]
        if isLeapYear(year) and month > 2:
            days += 1
        if year == 1582 and (month > 10 or (month == 10 and day > 4)):
            days -= 10
        days += day - 1
        return days

    def setFromBaseline(self, days):
        """Set date from days since baseline of Jan. 1, 1900"""
        if not (GenDate.minDays <= days <= GenDate.maxDays):
            raise GenDateError('Invalid day value, limits exceeded')
        year = int(round(days / 365.2425)) + 1900
        if year < 1:
            year -= 1      # adjust for BC & no year 0
        remainDays = days - firstDayOfYear(year) + 1
        while remainDays <= 0:
            year -= 1
            if year == 0:
                year = -1
            remainDays = days - firstDayOfYear(year) + 1
        while remainDays > 366 or (remainDays == 366 and not isLeapYear(year)):
            year += 1
            remainDays = days - firstDayOfYear(year) + 1
        daysInMonth = GenDate.daysInMonth[:]
        if isLeapYear(year):
            daysInMonth[1] = 29
        month = 1
        while remainDays > daysInMonth[month - 1]:
            remainDays -= daysInMonth[month - 1]
            month += 1
        if year == 1582 and (month > 10 or (month == 10 and remainDays > 4)):
            remainDays += 10
            if remainDays > daysInMonth[month - 1]:
                remainDays -= daysInMonth[month - 1]
                month += 1
        self.setDate((year, month, remainDays))

    def clone(self):
        """Return cloned instance"""
        return self.__class__(self.date)

    def __repr__(self):
        """Outputs in format [-]yyyy/mm/dd"""
        if self.date < 0:
            return "%05d/%02d/%02d" % self.toTuple()
        return "%04d/%02d/%02d" % self.toTuple()

    def __int__(self):
        """Return integer repr"""
        return self.date

    def __cmp__(self, other):
        """Compare operator"""
        if other is None or not isinstance(other, GenDate):
            return 1
        return cmp(self.date, other.date)

    def __hash__(self):
        """Allow use as dictionary key"""
        return hash(self.date)

    def __add__(self, days):
        """Addition operator"""
        if not type(days) is types.IntType:
            raise GenDateError('Add operator requires an integer')
        copy = self.clone()
        copy.setFromBaseline(self.baselineDays() + days)
        return copy

    def __radd__(self, days):
        """Addition operator"""
        return self.__add__(days)

    def __sub__(self, other):
        """Subtraction operator for date or int days"""
        if type(other) is types.IntType:
            return self.__add__(-other)
        return self.baselineDays() - other.baselineDays()

    def __rsub__(self, other):
        """Subtraction operator for date"""
        if not isinstance(other, GenDate):
            raise GenDateError('Cannot subtract a date from an integer')
        return other.baselineDays() - self.baselineDays()


class GenDateError(Exception):
    """Exception class for invalid date data"""
    pass


####  Utility Functions  ####

def firstDayOfYear(year):
    """Return the baseline day (based on Jan. 1, 1900) for Jan. 1"""
    if year < 0:   # BC calculation
        days = year * 365 - abs(year)/4 - GenDate.daysTo1900
    else:          # AD calculation
        lastYear = year - 1
        days = lastYear * 365 + lastYear / 4 - GenDate.daysTo1900
        if year > 1582:    # adjust for new rules and 10 days lost in 1582
            days -= abs(lastYear - 1600)/100 - abs(lastYear - 1600)/400 + 10
    return days

def isLeapYear(year):
    """Returns 1 if given year is a leap year"""
    if year % 4 != 0:
        return 0
    if year < 1600 or year % 100 != 0:
        return 1
    if year % 400 != 0:
        return 0
    return 1

def _parseDateStr(dateStr):
    """Split string into three date parts, split by any of .-/,; or spaces.
       Return tuple"""
    try:
        return re.match(r'(.+?)[\s,\.;/-]+(.+?)[\s,\.;/-]+(.+)',
                        dateStr).groups()
    except AttributeError:
        raise GenDateError('Invalid date string')


if __name__ == '__main__':
    gd = GenDate()
    print 'Today is', gd.dateStr('wwww, mmmm dd, yyyy')
    gd.setFromIntStr('12/23/65', 'mm/dd/yy')
    print gd.dateStr('wwww, mmmm dd, yyyy')
