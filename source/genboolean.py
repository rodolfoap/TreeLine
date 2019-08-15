#!/usr/bin/env python

#****************************************************************************
# genboolean.py, provides a class for boolean formating
#
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import types


class GenBoolean(object):
    """Stores & formats boolean values"""
    formatDict = {N_('true'):1, N_('false'):0, N_('yes'):1, N_('no'):0}
    translateDict = {}
    for key in formatDict.keys():
        value = formatDict[key]
        formatDict[key[0]] = value
        translateDict[_(key)[0]] = value
        translateDict[_(key)] = value
    formatDict.update(translateDict)

    def __init__(self, value=0):
        """Accepts any format from formatDict (not case sensitive)
           to initialize"""
        self.setBool(value)

    def setBool(self, value):
        """Sets the value from any format in formatDict
           (not case sensitive)"""
        if type(value) in (types.StringType, types.UnicodeType):
            value = value.lower()
        try:
            self.value = GenBoolean.formatDict[value]
        except KeyError:
            raise GenBooleanError('Invalid entry')

    def setFromFormat(self, boolStr, format):
        """Set value based on given format only
           Returns self"""
        try:
            self.value = not list(_splitFormat(format)).index(boolStr.lower())
        except ValueError:
            raise GenBooleanError('Invalid entry, no format match')
        return self

    def boolStr(self, format='true/false'):
        """Return string based on the format, which includes a true
           string and a false string separated by a '/'
           Raise exception of format invalid"""
        return _splitFormat(format)[not self.value]

    def clone(self):
        """Return cloned instance"""
        return self.__class__(self.value)

    def __repr__(self):
        """Outputs in format true/false"""
        return self.boolStr()

    def __cmp__(self, other):
        """Compare operator"""
        if other and isinstance(other, GenBoolean):
            return cmp(self.value, other.value)
        if type(other) is types.IntType:
            return cmp(self.value, other)
        return 1

    def __hash__(self):
        """Allow use as dictionary key"""
        return hash(self.value)

    def __nonzero__(self):
        """Allow truth testing"""
        return self.value


class GenBooleanError(Exception):
    """Exception class for invalid boolean data"""
    pass

############# Utility Function ############

def _splitFormat(format):
    """Return tuple of format converted to lower case or raise exception"""
    result = format.lower().split('/', 1)
    if len(result) != 2 or not result[0] or not result[1] or \
       result[0] == result[1]:
        raise GenBooleanError('Invalid boolean format')
    return result
