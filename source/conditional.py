#!/usr/bin/env python

#****************************************************************************
# conditional.py, provides a class to store comparison functions
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import re


class Conditional(object):
    """Stores & evaluates conditional comparisons for dictionary data"""
    parseRe = re.compile(r'((?:and)|(?:or)) (\S+) (.+?) '
                         r'(?:(?<!\\)"|(?<=\\\\)")(.*?)'
                         r'(?:(?<!\\)"|(?<=\\\\)")')
    def __init__(self, conditionStr=''):
        """Accepts a string in format 'fieldName == "value" and
           otherFieldName > "value"'"""
        self.conditionList = []
        self.formatName = ''   # used only for evaluateType()
        for boolOper, fieldName, oper, value in \
           Conditional.parseRe.findall('and ' + conditionStr):
            value = value.replace('\\"', '"').replace('\\\\', '\\')
            self.conditionList.append(ConditionLine(boolOper, fieldName,
                                                    oper, value))

    def evaluate(self, data):
        """Return the boolean result without checking format type"""
        result = True
        for condition in self.conditionList:
            result = condition.evalFunc(data, result)
        return result

    def evaluateType(self, item):
        """Return the boolean result with a type check"""
        if item.formatName == self.formatName:
            return self.evaluate(item.data)
        return False

    def conditionText(self):
        """Return the condition string for this conditional set"""
        return ' '.join([cond.conditionText() for cond in
                         self.conditionList])[4:]

    def setupFields(self, nodeFormat):
        """Set fieldNames used in lines to field references"""
        for condition in self.conditionList[:]:
            condition.setupFields(nodeFormat)
            if not condition.field:
                self.conditionList.remove(condition)

    def __len__(self):
        """Return number of conditions for truth testing"""
        return len(self.conditionList)

    def __deepcopy__(self, memo):
        """Avoid problems with deepcopy of a ref to instance's own method"""
        return Conditional(self.conditionText())


class ConditionLine(object):
    """Stores & evaluates a portion of a conditional comparison"""
    def __init__(self, boolOper, fieldName, oper, value):
        self.boolOper = boolOper
        self.tmpFieldName = fieldName
        self.field = None
        self.oper = oper
        self.valueStr = value
        self.value = None
        functions = {'==': self.equalFunc, '<': self.lessFunc,
                     '<=': self.lessEqualFunc, '>': self.greaterFunc,
                     '>=': self.greaterEqualFunc, '!=': self.notEqualFunc,
                     'starts with': self.startsWithFunc,
                     'ends with': self.endsWithFunc,
                     'contains': self.containsFunc,
                     'True': self.trueFunc, 'False': self.falseFunc}
                     
        self.compareFunc = functions[self.oper]
        if self.boolOper == 'and':
            self.evalFunc = self.andFunc
        else:
            self.evalFunc = self.orFunc

    def conditionText(self):
        """Return the text line for this condition"""
        value = self.valueStr.replace('\\', '\\\\').replace('"', '\\"')
        return '%s %s %s "%s"' % (self.boolOper, self.field.name,
                                  self.oper, value)

    def setupFields(self, nodeFormat):
        """Set fieldNames used to field references"""
        if not self.tmpFieldName:
            self.tmpFieldName = self.field.name
        self.field = nodeFormat.findField(self.tmpFieldName)
        if self.field:
            self.value = self.field.sortValue({self.field.name: self.valueStr})
        self.tmpFieldName = ''

    def andFunc(self, data, prevResult=True):
        """Evaluates boolean combination"""
        return prevResult and self.compareFunc(data)

    def orFunc(self, data, prevResult=True):
        """Evaluates boolean combination"""
        return prevResult or self.compareFunc(data)

    def equalFunc(self, data):
        """Evaluates main condition (==)"""
        return self.field.sortValue(data) == \
               self.field.adjustedCompareValue(self.value)

    def lessFunc(self, data):
        """Evaluates main condition (<)"""
        return self.field.sortValue(data) < \
               self.field.adjustedCompareValue(self.value)

    def lessEqualFunc(self, data):
        """Evaluates main condition (<=)"""
        return self.field.sortValue(data) <= \
               self.field.adjustedCompareValue(self.value)

    def greaterFunc(self, data):
        """Evaluates main condition (>)"""
        return self.field.sortValue(data) > \
               self.field.adjustedCompareValue(self.value)

    def greaterEqualFunc(self, data):
        """Evaluates main condition (>=)"""
        return self.field.sortValue(data) >= \
               self.field.adjustedCompareValue(self.value)

    def notEqualFunc(self, data):
        """Evaluates main condition (!=)"""
        return self.field.sortValue(data) != \
               self.field.adjustedCompareValue(self.value)

    def startsWithFunc(self, data):
        """Evaluates main condition (starts with)"""
        return unicode(self.field.sortValue(data)).\
                     startswith(unicode(self.value))

    def endsWithFunc(self, data):
        """Evaluates main condition (ends with)"""
        return unicode(self.field.sortValue(data)).\
                     endswith(unicode(self.value))

    def containsFunc(self, data):
        """Evaluates main condition (contains)"""
        return unicode(self.field.sortValue(data)).\
                     find(unicode(self.value)) >= 0

    def trueFunc(self, data):
        """Evaluates main condition (always true)"""
        return True

    def falseFunc(self, data):
        """Evaluates main condition (always false)"""
        return False

