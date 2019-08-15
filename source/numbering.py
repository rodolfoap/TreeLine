#!/usr/bin/env python

#****************************************************************************
# numbering.py, provides functions to format numbering
#
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import re

def numSeries(start, stop, format):
    """Return a list of formatted numbers"""
    formatText = re.match('(.*)([1AaiI])(.*)', format)
    if not formatText:
        return [format] * (stop - start) # return format if can't number
    if formatText.group(2) == '1':
        getNum = lambda x,y: `x`
    elif formatText.group(2) in 'Ii':
        getNum = writeRoman
    else:
        getNum = writeAlpha
    upperCase = formatText.group(2).isupper()
    return ['%s%s%s' % (formatText.group(1), getNum(num, upperCase),
                        formatText.group(3)) for num in range(start, stop)]

def readAlpha(text):
    """Return integer based on A,B,C...AA,AB order"""
    textList = list(text.upper())
    factor = 1
    result = 0
    while textList:
        result += factor * (ord(textList.pop()) - ord('A') + 1)
        factor *= 26
    return result

def writeAlpha(num, upperCase=1):
    """Return alpha string for integer num"""
    if num <= 0:
        return ''
    result = ''
    while num:
        digit = num % 26
        if digit == 0:
            digit = 26
        result = chr(digit - 1 + ord('A')) + result
        num = (num - digit) / 26
    return upperCase and result or result.lower()

readRomanDict = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500,
                 'M': 1000}

def readRoman(text):
    """Return integer from text roman number, or 0 on error"""
    textList = list(text.upper())
    result = 0
    try:
        while textList:
            num = readRomanDict[textList.pop(0)]
            if textList and num < readRomanDict[textList[0]]:
                result -= num
            else:
                result += num
    except KeyError:
        return 0
    return result

writeRomanDict = {0: '', 1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI',
                  7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X', 20: 'XX', 30: 'XXX',
                  40: 'XL', 50: 'L', 60: 'LX', 70: 'LXX', 80: 'LXXX',
                  90: 'XC', 100: 'C', 200: 'CC', 300: 'CCC', 400: 'CD',
                  500: 'D', 600: 'DC', 700: 'DCC', 800: 'DCCC', 900: 'CM',
                  1000: 'M', 2000: 'MM', 3000: 'MMM'}

def writeRoman(num, upperCase=1):
    """Return roman number text for integer num"""
    if num <= 0 or num >= 4000:
        return ''
    result = ''
    factor = 1000
    while num:
        digit = num - (num % factor)
        result += writeRomanDict[digit]
        factor /= 10
        num -= digit
    return upperCase and result or result.lower()
