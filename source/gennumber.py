#!/usr/bin/env python

#****************************************************************************
# gennumber.py, provides a class for number formating
#
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import re
import types
import fpformat
import math

class GenNumber(object):
    """Stores & formats number values"""
    def __init__(self, num=0):
        """Accepts one of the following to initialize:
               1. int value
               2. float value
               3. string in common int or float format
               4. GenNumber instance"""
        self.setNumber(num)

    def setNumber(self, num):
        """Sets the number value from number formats, strings, or a
           GenNumber class"""
        inType = type(num)
        if inType in (types.IntType, types.LongType, types.FloatType):
            self.num = num
        elif inType in (types.StringType, types.UnicodeType):
            try:
                self.num = int(num)
            except ValueError:
                try:
                    self.num = float(num)
                except ValueError:
                    self.setFromStr(num)
        elif inType is type(self):
            self.num = num.num
        else:
            raise GenNumberError('Invalid initialization type')

    def setFromStr(self, numStr, format='#\,###'):
        """Sets the value after removing extra characters found in format and
           using the approriate radix.
           Returns self"""
        radix = _getRadix(format)
        format = _unescapeFormat(radix, format).strip()
        extraChar = re.sub(r'[#0\seE\-\+%s]' % re.escape(radix), '', format)
        if extraChar:
            numStr = re.sub('[%s]' % re.escape(extraChar), '', numStr)
        if radix == ',':
            if '.' in numStr:
                raise GenNumberError('Invalid number string')
            numStr = numStr.replace(',', '.')
        try:
            self.num = int(numStr)
        except ValueError:
            try:
                self.num = float(numStr)
            except ValueError:
                raise GenNumberError('Invalid number string')
        return self

    def numStr(self, format='#.##'):
        """Returns string in given format, including exponents, e=exponent,
           #=optional digit, 0=required digit, -=optional sign, +=required sign
           space=digit or space (external) or thousands sep (internal),
           \, and \. are thousands separators"""
        formMain, formExp = _doubleSplit('eE', format)
        if not formExp:
            return self.basicNumStr(format)
        exp = math.floor(math.log10(abs(self.num)))
        num = float(self.num) / 10**exp
        totPlcs = len(re.findall(r'[#0]', formMain))
        num = round(num, totPlcs > 0 and totPlcs - 1 or 0)
        wholePlcs = len(re.findall(r'[#0]', _doubleSplit('.', formMain)[0]))
        expChg = wholePlcs - int(math.floor(math.log10(abs(num)))) - 1
        num = num * 10**expChg
        exp -= expChg
        c = 'e' in format and 'e' or 'E'
        return '%s%s%s' % (GenNumber(num).basicNumStr(formMain), c,
                           GenNumber(exp).basicNumStr(formExp))

    def basicNumStr(self, format='#.##'):
        """Returns string in given format, without exponent support,
           #=optional digit, 0=required digit, -=optional sign, +=required sign
           space=digit or space (external) or thousands sep (internal),
           \, and \. are thousands separators"""
        radix = _getRadix(format)
        format = _unescapeFormat(radix, format)
        formWhole, formFract = _doubleSplit(radix, format)
        decPlcs = len(re.findall(r'[#0]', formFract))
        numWhole, numFract = _doubleSplit('.', fpformat.fix(self.num, decPlcs))
        while numFract[-1:] == '0':
            numFract = numFract[:-1]
        numWhole, numFract = list(numWhole), list(numFract)
        formWhole, formFract = list(formWhole), list(formFract)
        sign = '+'
        if numWhole[0] == '-':
            sign = numWhole.pop(0)
        result = []
        while numWhole or formWhole:
            c = formWhole and formWhole.pop() or ''
            if c and c not in '#0 +-':
                if numWhole or '0' in formWhole:
                    result.insert(0, c)
            elif numWhole and c != ' ':
                result.insert(0, numWhole.pop())
                if c and c in '+-':
                    formWhole.append(c)
            elif c in '0 ':
                result.insert(0, c)
            elif c in '+-':
                if sign == '-' or c == '+':
                    result.insert(0, sign)
                sign = ''
        if sign == '-':
            if result[0] == ' ':
                result = [re.sub(r'\s(?!\s)', '-', ''.join(result), 1)]
            else:
                result.insert(0, '-')
        if formFract or (format and format[-1] == radix):
            result.append(radix)
        while formFract:
            c = formFract.pop(0)
            if c not in '#0 ':
                if numFract or '0' in formFract:
                    result.append(c)
            elif numFract:
                result.append(numFract.pop(0))
            elif c in '0 ':
                result.append('0')
        return ''.join(result)

    def clone(self):
        """Return cloned instance"""
        return self.__class__(self.num)

    def __repr__(self):
        """Outputs in general string fomat"""
        return repr(self.num)

    def __coerce__(self, other):
        """Allow mixed mode arithmetic"""
        thisType = type(self.num)
        otherType = type(other)
        if thisType == otherType:
            return (self.num, other)
        if types.FloatType in (thisType, otherType):
            return (float(self.num), float(other))
        if  types.LongType in (thisType, otherType) and \
               types.IntType in (thisType, otherType):
            return (long(self.num), long(other))
        return None

    def __int__(self):
        """Return integer repr"""
        return int(self.num)

    def __long__(self):
        """Return long repr"""
        return long(self.num)

    def __float__(self):
        """Return float repr"""
        return float(self.num)

    def __hash__(self):
        """Allow use as dictionary key"""
        return hash(self.num)


class GenNumberError(Exception):
    """Exception class for invalid number data"""
    pass

######### Utility Functions ##########

def _doubleSplit(sepChars, string):
    """Return tuple of two parts of the string, 
       sep by one of chars in sepChars,
       return empty string if no separator found"""
    for sep in sepChars:
        result = string.split(sep, 1)
        if len(result) == 2:
            return result
    return (string, '')

def _getRadix(format):
    """Return the radix character (. or ,) used in format,
       assumes "." if ambiguous"""
    if not '\,' in format and (not '.' in format or '\.' in format) and \
                (',' in format or '\.' in format):
        return ','
    return '.'

def _unescapeFormat(radix, format):
    """Return format with escapes removed form non-radix separators"""
    if radix == '.':
        return format.replace('\,', ',')
    return format.replace('\.', '.')
