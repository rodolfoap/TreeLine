#!/usr/bin/env python

#****************************************************************************
# fieldformat.py, provides non-GUI base classes for field formating
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#****************************************************************************

import re
from xml.sax.saxutils import escape, unescape
from gennumber import GenNumber, GenNumberError
from gendate import GenDate, GenDateError
from gentime import GenTime, GenTimeError
from genboolean import GenBoolean, GenBooleanError
import treedoc
import globalref

_errorStr = '#####'


def xslEscape(text):
    """Encapsulate all literal text in <xsl:text> elements
       and transform/escape some non-XML entities.
       For the moment, only &nbsp; is supported"""
    nonTagRe = re.compile(r'(.*?)(<.*?>)|(.*)')
    escDict = {'&amp;nbsp;': '&#xa0;'}  # escape function does '&' first
    def esc(matchObj):
        """Return escaped replacement text"""
        if matchObj.group(1) == None:   # no tags found
            return u'<xsl:text>%s</xsl:text>' % \
                   escape(matchObj.group(3), escDict)
        if matchObj.group(1):           # leading text and tag
            return u'<xsl:text>%s</xsl:text>%s' % \
                   (escape(matchObj.group(1), escDict), matchObj.group(2))
        return matchObj.group(2)        # tag only
    return nonTagRe.sub(esc, text)


class TextFormat(object):
    """Holds format info for a normal text field"""
    typeName = 'Text'
    sortSequence = 20
    stripTagRe = re.compile('<.*?>')
    defaultNumLines = 1
    #field format edit options:
    defaultFormat = ''
    formatMenuList = []
    htmlOption = True
    hasEditChoices = False
    autoAddChoices = False
    hasFileBrowse = False
    allowAltLinkText = False

    def __init__(self, name, attrs={}):
        """Any prefix, suffix, html info in attrs dict"""
        self.name = name
        self.enName = ''  # used only by fileFormat field for i18n
        self.format = attrs.get(u'format', self.defaultFormat)
        self.prefix = attrs.get(u'prefix', '')
        self.suffix = attrs.get(u'suffix', '')
        # defaults to no html (line breaks preserved)
        self.html = attrs.get(u'html', '').startswith('y') and True or False
        self.isRequired = attrs.get(u'required', '').startswith('y') and \
                          True or False
        self.hidden = attrs.get(u'hidden', '').startswith('y') and \
                      True or False
        try:
            self.numLines = int(attrs.get(u'lines',
                                          repr(self.defaultNumLines)))
        except ValueError:
            self.numLines = 1
        self.initDefault = attrs.get(u'init', '')
        self.linkAltField = attrs.get(u'linkalt', '')
        self.parentLevel = 0
        self.useFileInfo = False
        self.showInDialog = True
        self.initFormat()

    def initFormat(self):
        """Called by base init, after class change or format text change"""
        pass

    def duplicateSettings(self, otherField):
        """Assign other field's parameters to this field"""
        self.name = otherField.name
        self.enName = otherField.enName
        self.format = otherField.format
        self.prefix = otherField.prefix
        self.suffix = otherField.suffix
        self.html = otherField.html
        self.isRequired = otherField.isRequired
        self.hidden = otherField.hidden
        self.numLines = otherField.numLines
        self.initDefault = otherField.initDefault
        self.linkAltField = otherField.linkAltField
        self.parentLevel = otherField.parentLevel
        self.useFileInfo = otherField.useFileInfo
        self.showInDialog = otherField.showInDialog

    def changeType(self, newType):
        """Change this field's type to newType with default format"""
        self.__class__ = globals()[newType + 'Format']
        self.format = self.defaultFormat
        self.initFormat()

    def englishName(self):
        """Returns English name if assigned, o/w name"""
        if self.enName:
            return self.enName
        return self.name

    def sepName(self, englishOnly=False):
        """Return name enclosed with {* *} separators"""
        name = englishOnly and self.enName or self.name
        if not self.useFileInfo:
            return u'{*%s*}' % name
        return u'{*!%s*}' % name

    def labelName(self):
        """Return name used for labels - add * for required fields"""
        if self.isRequired:
            return '%s*' % self.name
        return self.name

    def writeXml(self):
        """Return text for xml attributes"""
        text = u' type="%s"' % self.typeName
        if self.format:
            text += u' format="%s"' % escape(self.format, treedoc.escDict)
        if self.prefix:
            text += u' prefix="%s"' % escape(self.prefix, treedoc.escDict)
        if self.suffix:
            text += u' suffix="%s"' % escape(self.suffix, treedoc.escDict)
        if self.html:
            text += u' html="y"'
        if self.isRequired:
            text += u' required="y"'
        if self.hidden:
            text += u' hidden="y"'
        if self.numLines > 1:
            text += u' lines="%d"' % self.numLines
        if self.initDefault:
            text += u' init="%s"' % escape(self.initDefault, treedoc.escDict)
        if self.linkAltField:
            text += u' linkalt="%s"' % escape(self.linkAltField,
                                              treedoc.escDict)
        return text

    def outputText(self, item, titleMode, internal=False):
        """Return formatted text for this field"""
        if self.useFileInfo:
            item = globalref.docRef.fileInfoItem
        storedText = item.data.get(self.name, '')
        if storedText:
            return self.formatOutput(storedText, titleMode, internal)
        return ''

    def removeMarkup(self, text):
        """Remove HTML Markup and unescape entities"""
        text = TextFormat.stripTagRe.sub('', text)
        return unescape(text)

    def formatOutput(self, storedText, titleMode, internal=False):
        """Return formatted text, properly escaped if not in titleMode"""
        prefix = self.prefix
        suffix = self.suffix
        if titleMode:
            if self.html:
                storedText = self.removeMarkup(storedText)
            if globalref.docRef.formHtml:
                prefix = self.removeMarkup(prefix)
                suffix = self.removeMarkup(suffix)
        else:
            if not self.html:
                storedText = escape(storedText).replace('\n', '<br />')
            if not globalref.docRef.formHtml:
                prefix = escape(prefix)
                suffix = escape(suffix)
        return u'%s%s%s' % (prefix, storedText, suffix)

    def editText(self, item):
        """Return tuple of this field's text in edit format and bool validity,
           using edit format option"""
        storedText = item.data.get(self.name, '')
        result = self.formatEditText(storedText)
        if self.isRequired and not result[0]:
            return (result[0], False)
        return result

    def formatEditText(self, storedText):
        """Return tuple of text in edit format and bool validity,
           using edit format option"""
        return (storedText, True)

    def storedText(self, editText):
        """Return tuple of stored text from edited text and bool validity,
           using edit format option"""
        return (editText, editText or not self.isRequired)

    def getInitDefault(self):
        """Return initial stored value for new nodes"""
        return self.initDefault

    def setInitDefault(self, editText):
        """Set initial value from editor version using edit format option"""
        self.initDefault = self.storedText(editText)[0]

    def getEditInitDefault(self):
        """Return initial value in edit format, found in edit format option"""
        return self.formatEditText(self.initDefault)[0]

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default"""
        return []

    def sortValue(self, data):
        """Return value to be compared for sorting and conditionals"""
        storedText = data.get(self.name, '')
        return storedText.lower()

    def adjustedCompareValue(self, value):
        """Return conditional comparison value with real-time adjustments,
           used for date and time types' 'now' value"""
        return value

    def xslText(self):
        """Return what we need to write into an  XSL file for this type"""
        return u'<xsl:if test="normalize-space(./%s)">%s'\
                '<xsl:value-of select="./%s"/>%s</xsl:if>' % \
                (self.name, xslEscape(self.prefix), self.name,
                 xslEscape(self.suffix))

    def xslTestText(self):
        """Return XSL file test for data existance"""
        return u'normalize-space(./%s)' % self.name


class LongTextFormat(TextFormat):
    """Holds format info for a long text field - Obsolete -
       kept for compatability with old files"""
    # typeName = 'LongText'
    defaultNumLines = 7
    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        TextFormat.__init__(self, name, attrs)


class NumberFormat(TextFormat):
    """Holds format info for a number field"""
    typeName = 'Number'
    sortSequence = 10
    #field format edit options:
    defaultFormat = u'#.##'
    formatMenuList = [(u'%s\t%s' % (_('Optional Digit'), '#'), '#'),
                      (u'%s\t%s' % (_('Required Digit'), '0'), '0'),
                      (u'%s\t%s' % (_('Digit or Space (external)'),
                                    _('<space>')), ' '),
                      None,
                      (u'%s\t%s' % (_('Decimal Point'), '.'), '.'),
                      (u'%s\t%s' % (_('Decimal Comma'), ','), ','),
                      None,
                      (u'%s\t%s' % (_('Comma Separator'), '\,'), '\,'),
                      (u'%s\t%s' % (_('Dot Separator'), '\.'), '\.'),
                      (u'%s\t%s' % (_('Space Separator (internal)'),
                                    _('<space>')), ' '),
                      None,
                      (u'%s\t%s' % (_('Optional Sign'), '-'), '-'),
                      (u'%s\t%s' % (_('Required Sign'), '+'), '+'),
                      None,
                      (u'%s\t%s' % (_('Exponent (capital)'), 'E'), 'E'),
                      (u'%s\t%s' % (_('Exponent (small)'), 'e'), 'e')]

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        TextFormat.__init__(self, name, attrs)

    def formatOutput(self, storedText, titleMode, internal=False):
        """Return formatted text, properly escaped if not in titleMode"""
        try:
            text = GenNumber(storedText).numStr(self.format)
        except GenNumberError:
            text = _errorStr
        return TextFormat.formatOutput(self, text, titleMode, internal)

    def formatEditText(self, storedText):
        """Return tuple of text in edit format and bool validity,
           using self.format"""
        try:
            return (GenNumber(storedText).numStr(self.format), True)
        except GenNumberError:
            return (storedText, not storedText)

    def storedText(self, editText):
        """Return tuple of stored text from edited text and bool validity,
           using self.format"""
        try:
            return (repr(GenNumber().setFromStr(editText, self.format)), True)
        except GenNumberError:
            return (editText, not editText and not self.isRequired)

    def sortValue(self, data):
        """Return value to be compared for sorting and conditionals"""
        storedText = data.get(self.name, '')
        try:
            return GenNumber(storedText).num
        except GenNumberError:
            return ''


class ChoiceFormat(TextFormat):
    """Holds format info for a field with one of several text options"""
    typeName = 'Choice'
    sortSequence = 20
    editSep = '/'
    #field format edit options:
    defaultFormat = '1/2/3/4'
    formatMenuList = [(u'%s\t%s' % (_('Separator'), '/'), '/'), None,
                      (u'%s\t%s' % (_('"/" Character'), '//'), '//'), None,
                      (u'%s\t%s' % (_('Example'), '1/2/3/4'), '1/2/3/4')]
    hasEditChoices = True

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        TextFormat.__init__(self, name, attrs)

    def initFormat(self):
        """Called by base init, after class change or format text change"""
        self.formatList = self.splitText(self.format)

    def formatOutput(self, storedText, titleMode, internal=False):
        """Return formatted text, properly escaped if not in titleMode"""
        if storedText not in self.formatList:
            storedText = _errorStr
        return TextFormat.formatOutput(self, storedText, titleMode, internal)

    def formatEditText(self, storedText):
        """Return tuple of text in edit format and bool validity,
           using edit format option"""
        if storedText in self.formatList:
            return (storedText, True)
        return (storedText, not storedText)

    def storedText(self, editText):
        """Return tuple of stored text from edited text and bool validity,
           using edit format option"""
        if editText in self.formatList:
            return (editText, True)
        return  (editText, not editText and not self.isRequired)

    def getEditChoices(self, currentText=''):
        """Return list of choices for combo box, 
           each a tuple of edit text and any annotation text"""
        return [(text, '') for text in self.formatList]

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default"""
        return [text for text in self.formatList]

    def splitText(self, textStr):
        """Split textStr using editSep, double sep's become char"""
        return [text.strip().replace('\0', self.editSep) for text in
                textStr.replace(self.editSep * 2, '\0').
                split(self.editSep)]


class CombinationFormat(ChoiceFormat):
    """Holds format info for a field of combinations of text options"""
    typeName = 'Combination'
    outputSepList = (',', ';', ':', '|', '/', '\\', '~')

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        ChoiceFormat.__init__(self, name, attrs)

    def initFormat(self):
        """Called by base init, after class change or format text change"""
        ChoiceFormat.initFormat(self)
        fullFormat = ''.join(self.formatList)
        try:
            self.sep = [sep for sep in CombinationFormat.outputSepList
                        if sep not in fullFormat][0] + ' '
        except IndexError:
            self.sep = CombinationFormat.outputSepList[0] + ' '

    def sortedChoices(self, inText):
        """Return tuple of choices from inText sorted like format and
           True if all splits are valid and included"""
        choices = self.splitText(inText)
        sortedChoices = [text for text in self.formatList if text in choices]
        if len(choices) == len(sortedChoices):
            return (sortedChoices, True)
        else:
            return (sortedChoices, False)

    def formatOutput(self, storedText, titleMode, internal=False):
        """Return formatted text, properly escaped if not in titleMode"""
        choices, valid = self.sortedChoices(storedText)
        if valid:
            result = self.sep.join(choices)
        else:
            result = _errorStr
        return TextFormat.formatOutput(self, result, titleMode, internal)

    def formatEditText(self, storedText):
        """Return tuple of text in edit format and bool validity,
           using edit format option"""
        for choice in self.splitText(storedText):
            if choice not in self.formatList:
                return (storedText, not storedText)
        return (storedText, True)

    def storedText(self, editText):
        """Return tuple of stored text from edited text and bool validity,
           using edit format option"""
        choices, valid = self.sortedChoices(editText)
        if valid:
            return (self.editSep.join(choices), True)
        else:
            return (editText, not editText and not self.isRequired)

    def getEditChoices(self, currentText=''):
        """Return list of choices for combo box,
           each a tuple of edit text and any annotation text"""
        currentChoices, valid = self.sortedChoices(currentText)
        nonChoices = [text for text in self.formatList
                      if text not in currentChoices]
        results = []
        for choice in nonChoices:      # menu entries to add a choice
            allChoices = currentChoices + [choice]
            allChoices = [text for text in self.formatList
                          if text in allChoices]
            results.append((self.editSep.join(allChoices),
                            '(%s %s)' % (_('add'), choice)))
        if currentChoices:
            results.append((None, None))   # separator
        for choice in currentChoices:   # menu entries to remove a choice
            allChoices = currentChoices[:]
            allChoices.remove(choice)
            allChoices = [text for text in self.formatList
                          if text in allChoices]
            results.append((self.editSep.join(allChoices),
                            '(%s %s)' % (_('remove'), choice)))
        return results

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default"""
        return [entry[0] for entry in self.getEditChoices()]


class AutoChoiceFormat(ChoiceFormat):
    """Holds format info for a field with one of several text options"""
    typeName = 'AutoChoice'
    #field format edit options:
    defaultFormat = ''
    formatMenuList = ()
    hasEditChoices = True
    autoAddChoices = True

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        TextFormat.__init__(self, name, attrs)

    def initFormat(self):
        """Called by base init, after class change or format text change"""
        self.formatList = []

    def addChoice(self, choice, sort=False):
        """Add choice to edit menu list if not already there"""
        if choice and choice not in self.formatList:
            self.formatList.append(choice)
            if sort:
                self.sortChoices()

    def sortChoices(self):
        """Sort menu list choices"""
        self.formatList.sort()

    def formatOutput(self, storedText, titleMode, internal=False):
        """Return formatted text, properly escaped if not in titleMode"""
        return TextFormat.formatOutput(self, storedText, titleMode, internal)

    def formatEditText(self, storedText):
        """Return tuple of text in edit format and bool validity,
           using edit format option"""
        return (storedText, True)

    def storedText(self, editText):
        """Return tuple of stored text from edited text and bool validity,
           using edit format option"""
        if editText:
            return (editText, True)
        return (editText, not self.isRequired)


class DateFormat(TextFormat):
    """Holds format info for a date field"""
    typeName = 'Date'
    sortSequence = 5
    #field format edit options:
    defaultFormat = u'mmmm d, yyyy'
    dateStampStrings = ('Now', _('Now', 'date stamp setting'))
    formatMenuList = [(u'%s\t%s' % (_('Day (1 or 2 digits)'), 'd'), 'd'),
                      (u'%s\t%s' % (_('Day (2 digits)'), 'dd'), 'dd'),
                      None,
                      (u'%s\t%s' % (_('Month (1 or 2 digits)'), 'm'), 'm'),
                      (u'%s\t%s' % (_('Month (2 digits)'), 'mm'), 'mm'),
                      (u'%s\t%s' % (_('Month Abbreviation'), 'mmm'), 'mmm'),
                      (u'%s\t%s' % (_('Month Name'), 'mmmm'), 'mmmm'),
                      None,
                      (u'%s\t%s' % (_('Year (2 digits)'), 'yy'), 'yy'),
                      (u'%s\t%s' % (_('Year (4 digits)'), 'yyyy'), 'yyyy'),
                      None,
                      (u'%s\t%s' % (_('Weekday (1 digit)'), 'w'), 'w'),
                      (u'%s\t%s' % (_('Weekday Abbreviation'), 'www'), 'www'),
                      (u'%s\t%s' % (_('Weekday Name'), 'wwww'), 'wwww')]
    hasEditChoices = True

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        TextFormat.__init__(self, name, attrs)

    def formatOutput(self, storedText, titleMode, internal=False):
        """Return formatted text, properly escaped if not in titleMode"""
        try:
            text = GenDate(storedText).dateStr(self.format)
        except GenDateError:
            text = _errorStr
        return TextFormat.formatOutput(self, text, titleMode, internal)

    def formatEditText(self, storedText):
        """Return tuple of text in edit format and bool validity,
           using edit format option"""
        format = globalref.options.strData('EditDateFormat', True)
        try:
            return (GenDate(storedText).dateStr(format), True)
        except GenDateError:
            return (storedText, not storedText)

    def storedText(self, editText):
        """Return tuple of stored text from edited text and bool validity,
           using edit format option"""
        format = globalref.options.strData('EditDateFormat', True)
        try:
            return (repr(GenDate().setFromStr(editText, format)), True)
        except GenDateError:
            return (editText, not editText and not self.isRequired)

    def getEditChoices(self, currentText=''):
        """Return list of choices for combo box, 
           each a tuple of edit text and any annotation text"""
        format = globalref.options.strData('EditDateFormat', True)
        today = GenDate().dateStr(format)
        yesterday = (GenDate() - 1).dateStr(format)
        tomorrow = (GenDate() + 1).dateStr(format)
        return [(today, '(%s)' %  _('today')),
                (yesterday, '(%s)' % _('yesterday')),
                (tomorrow, '(%s)' % _('tomorrow'))]

    def getInitDefault(self):
        """Return initial stored value for new nodes"""
        if self.initDefault in DateFormat.dateStampStrings:
            return GenDate().dateStr()
        return TextFormat.getInitDefault(self)

    def setInitDefault(self, editText):
        """Set initial value from editor version using edit format option"""
        if editText in DateFormat.dateStampStrings:
            self.initDefault = DateFormat.dateStampStrings[0]
        else:
            TextFormat.setInitDefault(self, editText)

    def getEditInitDefault(self):
        """Return initial value in edit format, found in edit format option"""
        if self.initDefault in DateFormat.dateStampStrings:
            return DateFormat.dateStampStrings[1]
        return TextFormat.getEditInitDefault(self)

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default"""
        choices = [entry[0] for entry in self.getEditChoices()]
        choices.insert(0, DateFormat.dateStampStrings[1])
        return choices

    def adjustedCompareValue(self, value):
        """Return conditional comparison value with real-time adjustments,
           used for date and time types' 'now' value"""
        if value.startswith('now'):
            return repr(GenDate())
        return value


class TimeFormat(TextFormat):
    """Holds format info for a time field"""
    typeName = 'Time'
    sortSequence = 6
    #field format edit options:
    defaultFormat = u'h:MM:SS aa'
    timeStampStrings = ('Now', _('Now', 'time stamp setting'))
    formatMenuList = [(u'%s\t%s' % (_('Hour (0-23, 1 or 2 digits)'), 'H'),
                       'H'),
                      (u'%s\t%s' % (_('Hour (00-23, 2 digits)'), 'HH'), 'HH'),
                      (u'%s\t%s' % (_('Hour (1-12, 1 or 2 digits)'), 'h'),
                       'h'),
                      (u'%s\t%s' % (_('Hour (01-12, 2 digits)'), 'hh'), 'hh'),
                      None,
                      (u'%s\t%s' % (_('Minute (1 or 2 digits)'), 'M'), 'M'),
                      (u'%s\t%s' % (_('Minute (2 digits)'), 'MM'), 'MM'),
                      None,
                      (u'%s\t%s' % (_('Second (1 or 2 digits)'), 'S'), 'S'),
                      (u'%s\t%s' % (_('Second (2 digits)'), 'SS'), 'SS'),
                      (u'%s\t%s' % (_('Fractional Seconds'), 's'), 's'),
                      None,
                      (u'%s\t%s' % (_('AM/PM'), 'AA'), 'AA'),
                      (u'%s\t%s' % (_('am/pm'), 'aa'),'aa')]
    hasEditChoices = True

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        TextFormat.__init__(self, name, attrs)

    def formatOutput(self, storedText, titleMode, internal=False):
        """Return formatted text, properly escaped if not in titleMode"""
        try:
            text = GenTime(storedText).timeStr(self.format)
        except GenTimeError:
            text = _errorStr
        return TextFormat.formatOutput(self, text, titleMode, internal)

    def formatEditText(self, storedText):
        """Return tuple of text in edit format and bool validity,
           using edit format option"""
        format = globalref.options.strData('EditTimeFormat', True)
        try:
            return (GenTime(storedText).timeStr(format), True)
        except GenTimeError:
            return (storedText, not storedText)

    def storedText(self, editText):
        """Return tuple of stored text from edited text and bool validity,
           using edit format option"""
        try:
            return (repr(GenTime(editText)), True)
        except GenTimeError:
            return (editText, not editText and not self.isRequired)

    def getEditChoices(self, currentText=''):
        """Return list of choices for combo box, 
           each a tuple of edit text and annotated text"""
        format = globalref.options.strData('EditTimeFormat', True)
        now = GenTime().timeStr(format)
        choices = [(now, '(%s)' % _('now'))]
        for hr in (6, 9, 12, 15, 18, 21, 0):
            time = GenTime((hr, 0)).timeStr(format)
            choices.append((time, ''))
        return choices

    def getInitDefault(self):
        """Return initial stored value for new nodes"""
        if self.initDefault in TimeFormat.timeStampStrings:
            return GenTime().timeStr()
        return TextFormat.getInitDefault(self)

    def setInitDefault(self, editText):
        """Set initial value from editor version using edit format option"""
        if editText in TimeFormat.timeStampStrings:
            self.initDefault = TimeFormat.timeStampStrings[0]
        else:
            TextFormat.setInitDefault(self, editText)

    def getEditInitDefault(self):
        """Return initial value in edit format, found in edit format option"""
        if self.initDefault in TimeFormat.timeStampStrings:
            return TimeFormat.timeStampStrings[1]
        return TextFormat.getEditInitDefault(self)

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default"""
        choices = [entry[0] for entry in self.getEditChoices()]
        choices.insert(0, TimeFormat.timeStampStrings[1])
        return choices

    def adjustedCompareValue(self, value):
        """Return conditional comparison value with real-time adjustments,
           used for date and time types' 'now' value"""
        if value.startswith('now'):
            return repr(GenTime())
        return value


class BooleanFormat(ChoiceFormat):
    """Holds format info for a bool field"""
    typeName = 'Boolean'
    sortSequence = 1
    #field format edit options:
    defaultFormat = _('yes/no')
    formatMenuList = [(_('true/false'), _('true/false')),
                      (_('T/F'), _('T/F')), None,
                      (_('yes/no'), _('yes/no')),
                      (_('Y/N'), _('Y/N')), None,
                      ('1/0', '1/0')]
    hasEditChoices = True

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        ChoiceFormat.__init__(self, name, attrs)

    def formatOutput(self, storedText, titleMode, internal=False):
        """Return formatted text, properly escaped if not in titleMode"""
        if storedText not in self.formatList:
            try:
                storedText = GenBoolean(storedText).boolStr(self.format)
            except GenBooleanError:
                storedText = _errorStr
        return TextFormat.formatOutput(self, storedText, titleMode, internal)

    def formatEditText(self, storedText):
        """Return tuple of text in edit format and bool validity,
           using edit format option"""
        if storedText in self.formatList:
            return (storedText, True)
        try:
            return (GenBoolean(storedText).boolStr(self.format), True)
        except GenBooleanError:
            return (storedText, not storedText)

    def storedText(self, editText):
        """Return tuple of stored text from edited text and bool validity,
           using edit format option"""
        try:
            return (repr(GenBoolean(editText)), True)
        except GenBooleanError:
            if editText in self.formatList:
                return (editText, True)
            return (editText, not editText and not self.isRequired)

    def sortValue(self, data):
        """Return value to be compared for sorting and conditionals"""
        storedText = data.get(self.name, '')
        try:
            return repr(GenBoolean(storedText))
        except GenBooleanError:
            return ''


class UniqueIDFormat(TextFormat):
    """An unique ID automatically generated for new nodes"""
    typeName = 'UniqueID'
    sortSequence = 10
    formatRe = re.compile('([^0-9]*)([0-9]+)(.*)')
    #field format edit options:
    defaultFormat = u'0001'
    formatMenuList = [(u'%s\t%s' % (_('Required Digit'), '0'), '0'), None,
                      (u'%s\t%s' % (_('Start Num Example'), '0100'), '0100'),
                      (u'%s\t%s' % (_('Prefix Example'), 'id0100'), 'id0100')]

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        TextFormat.__init__(self, name, attrs)

    def nextValue(self, increment=True):
        """Return the next value for a new node,
           increment format if increment is True"""
        try:
            prefix, numText, suffix = UniqueIDFormat.formatRe.\
                                      match(self.format).groups()
        except AttributeError:
            self.format = UniqueIDFormat.defaultFormat
            return self.nextValue(increment)
        value = self.format
        if increment:
            pattern = u'%%s%%0.%dd%%s' % len(numText)
            num = int(numText) + 1
            self.format = pattern % (prefix, num, suffix)
        return value

    def sortValue(self, data):
        """Return value to be compared for sorting and conditionals"""
        storedText = data.get(self.name, '')
        try:
            return int(UniqueIDFormat.formatRe.match(storedText).group(2))
        except AttributeError:
            return 0


class URLFormat(TextFormat):
    """Holds format info for a field with a URL path"""
    typeName = 'URL'
    sortSequence = 8
    htmlOption = False
    allowAltLinkText = True
    hasMethodRe = re.compile('[a-zA-Z][a-zA-Z]+:|#')
    URLMethod = u'http://'

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        TextFormat.__init__(self, name, attrs)

    def initFormat(self):
        """Called by base init, after class change or format text change"""
        self.html = True

    def outputText(self, item, titleMode, internal=False):
        """Return formatted text for this field"""
        if self.useFileInfo:
            item = globalref.docRef.fileInfoItem
        altText = ''
        if self.linkAltField:
            field = item.nodeFormat().findField(self.linkAltField)
            if field:
                altText = field.outputText(item, titleMode, internal)
        storedText = item.data.get(self.name, '')
        if storedText:
            return self.formatOutput(storedText, titleMode, altText, internal)
        return ''

    def formatOutput(self, storedText, titleMode, altText='', internal=False):
        """Return formatted text, properly escaped and with
           a link reference if not in titleMode"""
        if titleMode:
            return TextFormat.formatOutput(self, storedText, titleMode,
                                           internal)
        paths = storedText.split('\n')
        results = []
        for url in paths:
            path = url
            if not URLFormat.hasMethodRe.match(path):
                path = u'%s%s' % (self.URLMethod, path)
            path = u'<a href="%s">%s</a>' % (escape(path, treedoc.escDict),
                                             altText or url)
            results.append(TextFormat.formatOutput(self, path, titleMode,
                                                   internal))
        return u'<br />'.join(results)

    def xslText(self):
        """Return what we need to write into an  XSL file for this type"""
        return u'<xsl:for-each select = "./%s">%s<xsl:choose>'\
                '<xsl:when test="contains(., \':\')"><a href="{.}">'\
                '<xsl:value-of select="."/></a></xsl:when><xsl:otherwise>'\
                '<a href="%s{.}"><xsl:value-of select="."/></a>'\
                '</xsl:otherwise></xsl:choose>%s</xsl:for-each>' % \
               (self.name, xslEscape(self.prefix), self.URLMethod,
                xslEscape(self.suffix))


class PathFormat(URLFormat):
    """Holds format info for a field with a local path"""
    typeName = 'Path'
    URLMethod = u'file:///'
    hasFileBrowse = True

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        URLFormat.__init__(self, name, attrs)


class EmailFormat(URLFormat):
    """Holds format info for a field with a local path"""
    typeName = 'Email'
    URLMethod = u'mailto:'

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        URLFormat.__init__(self, name, attrs)


class InternalLinkFormat(URLFormat):
    """Holds format info for a field with a local path"""
    typeName = 'InternalLink'
    URLMethod = u'#'

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        URLFormat.__init__(self, name, attrs)


class ExecuteLinkFormat(URLFormat):
    """Holds format info for an executable field"""
    typeName = 'ExecuteLink'
    URLMethod = u'exec:'
    hasFileBrowse = True

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        URLFormat.__init__(self, name, attrs)

    def formatOutput(self, storedText, titleMode, altText='', internal=False):
        """Return formatted text, properly escaped and with
           a link reference if not in titleMode"""
        if titleMode or not internal:
            return TextFormat.formatOutput(self, storedText, titleMode,
                                           internal)
        paths = storedText.split('\n')
        results = []
        for url in paths:
            # add prefix/suffix within the executable path:
            url = TextFormat.formatOutput(self, url, titleMode, internal)
            path = url
            if not URLFormat.hasMethodRe.match(path):
                path = u'%s%s' % (self.URLMethod, path)
            results.append(u'<a href="%s">%s</a>' %
                           (escape(path, treedoc.escDict), altText or url))
        return u'<br />'.join(results)

    def xslText(self):
        """Return what we need to write into an  XSL file for this type"""
        return TextFormat.xslText(self)


class PictureFormat(TextFormat):
    """Holds format info for a field with a link to a picture"""
    typeName = 'Picture'
    sortSequence = 8
    htmlOption = False
    hasFileBrowse = True

    def __init__(self, name, attrs={}):
        """Any format, prefix, suffix, html info in attrs dict"""
        TextFormat.__init__(self, name, attrs)

    def initFormat(self):
        """Called by base init, after class change or format text change"""
        self.html = True

    def formatOutput(self, storedText, titleMode, internal=False):
        """Return formatted text, properly escaped and with
           a link to the picture if not in titleMode"""
        if titleMode:
            return TextFormat.formatOutput(self, storedText, titleMode,
                                           internal)
        paths = storedText.split('\n')
        results = ['<img src="%s">' % escape(url, treedoc.escDict) for url
                   in paths]
        return u'<br />'.join(results)


class ParentFormat(TextFormat):
    """Placeholder format for references to specific parents"""
    typeName = 'Parent'

    def __init__(self, name, parentLevel=1):
        TextFormat.__init__(self, name, {})
        self.parentLevel = parentLevel

    def sepName(self, englishOnly=False):
        """Return name enclosed with {* *} separators"""
        name = englishOnly and self.enName or self.name
        return u'{*%s%s*}' % (self.parentLevel * '*', name)

    def outputText(self, item, titleMode, internal=False):
        """Return formatted text for this field"""
        for num in range(self.parentLevel):
            item = item.parent
            if not item:
                return ''
        field = item.nodeFormat().findField(self.name)
        if not field:
            return ''
        return field.outputText(item, titleMode, internal)

    def xslText(self):
        """Return what we need to write into an  XSL file for this type"""
        return u'<xsl:value-of select="%s%s"/>' % (self.parentLevel * '../',
                                                   self.name)

    def xslTestText(self):
        """Return XSL file test for data existance"""
        return u'normalize-space(%s%s)' % (self.parentLevel * '../', self.name)


class AncestorFormat(TextFormat):
    """Placeholder format for references to any parent with data"""
    typeName = 'Ancestor'

    def __init__(self, name):
        TextFormat.__init__(self, name, {})
        self.parentLevel = 1000

    def sepName(self, englishOnly=False):
        """Return name enclosed with {*? *} separators"""
        name = englishOnly and self.enName or self.name
        return u'{*?%s*}' % (name)

    def outputText(self, item, titleMode, internal=False):
        """Return formatted text for this field"""
        field = None
        while not field:
            item = item.parent
            if item:
                field = item.nodeFormat().findField(self.name)
            else:
                return ''
        return field.outputText(item, titleMode, internal)

    def xslText(self):
        """Return what we need to write into an  XSL file for this type"""
        return u'<xsl:value-of select="ancestor::*/%s"/>' % self.name

    def xslTestText(self):
        """Return XSL file test for data existance"""
        return u'normalize-space(ancestor::*/%s)' % self.name


class ChildFormat(TextFormat):
    """Placeholder format for references to a sequence of child data"""
    typeName = 'Child'

    def __init__(self, name):
        TextFormat.__init__(self, name, {})
        self.parentLevel = -1

    def sepName(self, englishOnly=False):
        """Return name enclosed with {*? *} separators"""
        name = englishOnly and self.enName or self.name
        return u'{*&%s*}' % (name)

    def outputText(self, item, titleMode, internal=False):
        """Return formatted text for this field"""
        result = []
        for child in item.childList:
            field = child.nodeFormat().findField(self.name)
            if field:
                text = field.outputText(child, titleMode, internal)
                if text:
                    result.append(text)
        return globalref.docRef.childFieldSep.join(result)

    def xslText(self):
        """Return what we need to write into an  XSL file for this type"""
        return u'<xsl:value-of select="child::*/%s"/>' % self.name

    def xslTestText(self):
        """Return XSL file test for data existance"""
        return u'normalize-space(child::*/%s)' % self.name


class CountFormat(TextFormat):
    """Placeholder format for a count of children at the given level"""
    typeName = 'Count'

    def __init__(self, name, level):
        TextFormat.__init__(self, name, {})
        self.parentLevel = -level

    def sepName(self, englishOnly=False):
        """Return name enclosed with {*? *} separators"""
        name = englishOnly and self.enName or self.name
        return u'{*#%s*}' % (name)

    def outputText(self, item, titleMode, internal=False):
        """Return formatted text for this field"""
        return repr(len(item.descendLevelList(-self.parentLevel)))
