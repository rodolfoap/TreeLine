#!/usr/bin/env python

#****************************************************************************
# nodeformat.py, provides non-GUI base classes for node formating info
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
import copy
import types
import sys
import os.path
import stat
import time
from xml.sax.saxutils import escape
if not sys.platform.startswith('win'):
    import pwd
import fieldformat
import conditional
import gendate
import gentime
import treedoc
import globalref


class NodeFormat(object):
    """Stores node type field list and line formatting"""
    lineAttrRe = re.compile('line\d+$')
    fieldSplitRe = re.compile(r'({\*(?:\**|\?|!|&|#)[\w_\-.]+\*})', re.U)
    fieldPartRe = re.compile(r'{\*(\**|\?|!|&|#)([\w_\-.]+)\*}', re.U)
    levelFieldRe = re.compile(r'[^0-9]+([0-9]+)$')
    def __init__(self, name, formatAttrs={}, defaultField=''):
        self.name = name
        self.fieldList = []
        self.lineList = []
        self.numEmptyFields = 0
        self.numFullFields = 0
        self.uniqueIDFields = []
        self.childType = formatAttrs.get(u'childtype', '')
        self.genericType = formatAttrs.get(u'generic', '')
        self.conditional = conditional.Conditional(formatAttrs.
                                                   get(u'condition', ''))
        self.sibPrefix = formatAttrs.get(u'sibprefix', '')
        self.sibSuffix = formatAttrs.get(u'sibsuffix', '')
        self.iconName = formatAttrs.get(u'icon', '')
        self.refField = None
        for key in formatAttrs.keys():
            if NodeFormat.lineAttrRe.match(key):
                self.insertLine(formatAttrs.get(key, ''), int(key[4:]))
        if defaultField:
            htmlAttrs = globalref.options.boolData('HtmlNewFields') and \
                        {'html': 'y'} or {}
            self.addNewField(defaultField, htmlAttrs)
            self.addLine(u'{*%s*}' % defaultField)
            self.addLine(u'{*%s*}' % defaultField)

    def duplicateSettings(self, otherFormat):
        """Set parameters to match other node format"""
        self.name = otherFormat.name
        self.fieldList = otherFormat.fieldList
        self.lineList = otherFormat.lineList
        self.childType = otherFormat.childType
        self.genericType = otherFormat.genericType
        self.conditional = otherFormat.conditional
        self.sibPrefix = otherFormat.sibPrefix
        self.sibSuffix = otherFormat.sibSuffix
        self.iconName = otherFormat.iconName
        self.refField = otherFormat.refField

    def __cmp__(self, other):
        """Comparison for equality and sorting"""
        return cmp(self.name, other.name)

    def fieldNames(self):
        """Return list of names of fields"""
        return [field.name for field in self.fieldList]

    def lineFields(self):
        """Return list of first fieldname in each line"""
        result = []
        for line in self.lineList[1:]:
            strippedLine = [part for part in line
                            if type(part) not in types.StringTypes]
            result.append(strippedLine and strippedLine[0].name or '')
        return result

    def findField(self, name):
        """Return field matching name or None"""
        try:
            return self.fieldList[self.fieldNames().index(name)]
        except ValueError:
            return None

    def addNewField(self, name, attrs={}):
        """Add new field with type, format, extra text in attrs dict"""
        typeName = '%sFormat' % attrs.get(u'type', 'Text')
        field = fieldformat.__dict__[typeName](name, attrs)
        self.fieldList.append(field)
        if attrs.get(u'ref', '').startswith('y'):
            self.refField = field
        elif not self.refField:
            self.refField = self.fieldList[0]
        sepName = field.sepName()
        # replace field name with the field
        self.lineList = [[part == sepName and field or part for part in line]
                         for line in self.lineList]

    def addFieldIfNew(self, name, attrs={}):
        """Add new field if it doesn't exist,
           add to generic for a derived type"""
        if name not in self.fieldNames():
            self.addNewField(name, attrs)
            if self.genericType:
                try:
                    genericType = globalref.docRef.\
                                  treeFormats[self.genericType]
                except KeyError:
                    print 'Warning - generic type %s not found' % \
                         self.genericType.encode(globalref.localTextEncoding)
                    self.genericType = ''
                    return
                genericType.addNewField(name, attrs)

    def addLine(self, text):
        """Add format line to end of lineList, line 0 is the title"""
        newLine = self.parseLine(text)
        if newLine:
            self.lineList.append(newLine)

    def insertLine(self, text, pos):
        """Change line at pos of lineList,
           add blanks in earlier positions if req'd, line 0 is the title"""
        newLine = self.parseLine(text)
        if not newLine:
            newLine = ['']
        self.lineList.extend([''] * (pos - len(self.lineList) + 1))
        self.lineList[pos] = newLine

    def changeTitleLine(self, text):
        """Change the title format line"""
        self.insertLine(text, 0)

    def changeOutputLines(self, lines):
        """Replace the output format lines with given list"""
        self.lineList = self.lineList[:1]
        if not self.lineList:
            self.lineList = ['']
        for line in lines:
            self.addLine(line)

    def updateLineFields(self):
        """Re-find fields to update for any changes in the fieldList"""
        self.lineList = [self.parseLine(line) for line in self.getLines()]

    def parseLine(self, text):
        """Parse text format line, return list of field types and text"""
        text = u' '.join(text.split())
        lineList = filter(None, NodeFormat.fieldSplitRe.split(text))
        newLine = []
        for part in lineList:
            fieldMatch = NodeFormat.fieldPartRe.match(part)
            if fieldMatch:
                modifier = fieldMatch.group(1)
                fieldName = fieldMatch.group(2)
                if not modifier:
                    field = self.findField(fieldName)
                    newLine.append(field and field or part)
                elif modifier[0] == '*':
                    newLine.append(fieldformat.ParentFormat(fieldName,
                                                            len(modifier)))
                elif modifier == '?':
                    newLine.append(fieldformat.AncestorFormat(fieldName))
                elif modifier == '&':
                    newLine.append(fieldformat.ChildFormat(fieldName))
                elif modifier == '!':     # file field
                    field = globalref.docRef.fileInfoFormat.\
                               findField(fieldName)
                    newLine.append(field and field or part)
                elif modifier == '#':
                    match = NodeFormat.levelFieldRe.match(fieldName)
                    if match:
                        level = int(match.group(1))
                        if level > 0:
                            newLine.append(fieldformat.CountFormat(fieldName,
                                                                   level))
                    else:
                        newLine.append(part)
                else:
                    newLine.append(part)
            else:
                newLine.append(part)
        return newLine

    def equalPrefix(self, other):
        """Return True if prefix and suffix are equivalent"""
        if self is other:
            return True
        return self.sibPrefix.strip().upper() == \
               other.sibPrefix.strip().upper() and \
               self.sibSuffix.strip().upper() == \
               other.sibSuffix.strip().upper()

    def formatTitle(self, item):
        """Return string with formatted title data"""
        if not self.lineList:
            return ''
        line = u''.join([self.fieldText(text, item, True) for text in
                         self.lineList[0]])
        return line.strip().split('\n', 1)[0]  # truncate to 1st line

    def formatText(self, item, skipEmpty=True, addPrefix=False,
                   addSuffix=False, internal=False):
        """Return list of output strings from formatting data"""
        tagExp = re.compile('.*(<br[ /]*?>|<BR[ /]*?>|<hr[ /]*?>|<HR[ /]*?>)$')
        result = []
        for lineData in self.lineList[1:]:
            self.numEmptyFields = 0
            self.numFullFields = 0
            line = u''.join([self.fieldText(text, item, False, internal)
                             for text in lineData])
            if self.numFullFields or not self.numEmptyFields or not skipEmpty:
                result.append(line.strip())   # add if tags are not empty
            else:
                tagMatch = tagExp.match(line)
                if tagMatch and result and globalref.docRef.formHtml:
                    # html tag at removed line end
                    result[-1] += tagMatch.group(1) # add to prev
        if addPrefix and self.sibPrefix:
            if result:
                result[0] = self.sibPrefix + result[0]
            else:
                result = [self.sibPrefix]
        if addSuffix and self.sibSuffix:
            if result:
                result[-1] += self.sibSuffix
            else:
                result = [self.sibSuffix]
        return result

    def formatAllTextLines(self, item):
        """Return a list of all text lines (title & output), add an empty
           string if a line has empty tags"""
        result = []
        for lineData in self.lineList:
            self.numEmptyFields = 0
            self.numFullFields = 0
            line = u''.join([self.fieldText(text, item, False) for text
                             in lineData])
            if self.numFullFields or not self.numEmptyFields:
                result.append(line.strip())   # add if tags are not empty
            else:
                result.append('')
        return result

    def formatPlainTextLines(self, item):
        """Return a list of all text lines (title & output), using
           plain text (titleMode) for all"""
        result = []
        for lineData in self.lineList:
            self.numEmptyFields = 0
            self.numFullFields = 0
            line = u''.join([self.fieldText(text, item, True, False, True)
                             for text in lineData])
            if not result or (line and \
                              (self.numFullFields or not self.numEmptyFields)):
                result.append(line.strip())   # add if tags are not empty
        return result

    def fieldText(self, field, item, titleMode=False, internal=False,
                  stripFormatTags=False):
        """Return formatted text for field"""
        if type(field) in types.StringTypes:
            text = field
            if not titleMode and not globalref.docRef.formHtml:
                text = escape(text)
            if stripFormatTags and globalref.docRef.formHtml:
                text = fieldformat.TextFormat.stripTagRe.sub('', text)
        else:
            text = field.outputText(item, titleMode, internal)
            if text:
                self.numFullFields += 1
            else:
                self.numEmptyFields += 1
        return text

    def setTitle(self, title, item, addUndo=False):
        """Set data based on title string, add undo item if addUndo,
           return True if changed successfully"""
        fields = []
        pattern = u''
        extraText = u''
        for seg in self.lineList[0]:
            if type(seg) in types.StringTypes:
                pattern += re.escape(seg)
                extraText += seg
            elif seg.parentLevel:
                text = self.fieldText(seg, item, True).split('\n', 1)[0]
                pattern += re.escape(text)
                extraText += text
            else:
                fields.append(seg)
                pattern += '(.*)'
        match = re.match(pattern, title)
        if not match and extraText.strip():
            return False
        if addUndo:
            globalref.docRef.undoStore.addDataUndo(item, True)
        if match:
            for num, field in enumerate(fields):
                item.data[field.name] = match.group(num+1)
        else:       # assign to 1st field if sep is only spaces
            item.data[fields[0].name] = title
            for field in fields[1:]:
                item.data[field.name] = ''
        if addUndo and globalref.pluginInterface:
            globalref.pluginInterface.execCallback(globalref.pluginInterface.
                                                   dataChangeCallbacks, item,
                                                   fields)
        return True

    def formatXml(self):
        """Return text list for use in xml file"""
        result = []
        lines = self.getLines(True)
        for i, line in enumerate(lines):
            if line:
                result.append(u'line%d="%s"' % \
                              (i, escape(line, treedoc.escDict)))
        if self.childType:
            result.append(u'childtype="%s"' % self.childType)
        if self.genericType:
            result.append(u'generic="%s"' % self.genericType)
        if self.conditional:
            result.append(u'condition="%s"' % escape(self.conditional.
                                                     conditionText(),
                                                     treedoc.escDict))
        if self.sibPrefix:
            result.append(u'sibprefix="%s"' % escape(self.sibPrefix,
                                                     treedoc.escDict))
        if self.sibSuffix:
            result.append(u'sibsuffix="%s"' % escape(self.sibSuffix,
                                                     treedoc.escDict))
        if self.iconName:
            result.append(u'icon="%s"' % self.iconName)
        return result

    def getLines(self, englishOnly=False):
        """Return text list of formatting lines"""
        lines = [u''.join([self.fieldName(part, englishOnly)
                           for part in line])
                 for line in self.lineList]
        return lines and lines or ['']

    def fieldName(self, field, englishOnly=False):
        """Return field name with separators or line text part"""
        if type(field) in types.StringTypes:
            return field
        return field.sepName(englishOnly)

    def addTableFields(self, headingList):
        """Set fields based on import table headings"""
        headings = [self.correctFieldName(head) for head in headingList]
        self.addLine(u'{*%s*}' % headings[0])
        for text in headings:
            self.addNewField(text)
            self.addLine(u'{*%s*}' % text)

    def xsltTemplate(self, indent, addAnchors=True):
        """Return list of lines for xslt template"""
        tagExp = re.compile('.*(<br[ /]*>|<BR[ /]*>|<hr[ /]*>|<HR[ /]*>)$')
        brExp = re.compile('<[bB][rR][ /]*>')
        brFormat = u'<br />'
        hrExp = re.compile('<[hH][rR][ /]*>')
        hrFormat = u'<hr />'
        lineList = copy.deepcopy(self.lineList[1:])
        output = [u'', u'<xsl:template match="%s[@item=\'y\']">' % self.name]
        if addAnchors:
            name = self.refField.name
            output.extend([u'<xsl:if test="normalize-space(./%s)">' % name,
                           u'<xsl:for-each select="./%s">' % name,
                           u'<a id="{.}" />', u'</xsl:for-each></xsl:if>'])
        if self.sibPrefix:
            output.append(fieldformat.xslEscape(self.sibPrefix))
        for lineDataRaw in lineList:
            lineData = [(type(field) not in types.StringTypes) and field or
                        hrFormat.join(hrExp.split(brFormat.
                                                  join(brExp.split(field))))
                        for field in lineDataRaw]
            fields = [field for field in lineData if
                      type(field) not in types.StringTypes]
            if fields:
                text = u'<xsl:if test="%s">' % \
                       u' or '.join([field.xslTestText() for field in fields])
                output.append(text)
                tagMatch = tagExp.match(type(lineData[-1]) in
                                        types.StringTypes and
                                        lineData[-1] or '')
                if tagMatch:
                    if len(tagMatch.group(1)) == len(lineData[-1]):
                        del lineData[-1]
                    else:
                        lineData[-1] = lineData[-1][:-len(tagMatch.group(1))]
                line = u''.join([(type(text) in types.StringTypes) and
                                 fieldformat.xslEscape(text) or
                                 text.xslText() for text in lineData])
                output.extend([line + brFormat, u'</xsl:if>'])
                if tagMatch:
                    output.append(tagMatch.group(1))
            else:
                output.append(lineData[0] + brFormat)
        if self.sibSuffix:
            output.append(fieldformat.xslEscape(self.sibSuffix))
        if globalref.docRef.spaceBetween:
            output.append(u'<br/>')
        output.extend([u'<div style="margin-left:%ipx">' % indent,
                       u'<xsl:apply-templates/>', u'</div>',
                       u'</xsl:template>'])
        return output

    def fixImportedFormat(self, defaultFieldName):
        """Add default field if there are no fields, and
           add title and output lines if missing"""
        if not self.lineList:
            if defaultFieldName in self.fieldNames():
                self.addLine(u'{*%s*}' % defaultFieldName)
            else:
                self.addLine(self.name)
            for fieldName in self.fieldNames():
                self.addLine(u'%s="{*%s*}"' % (fieldName, fieldName))
        if not self.fieldList:
            self.addNewField(defaultFieldName)

    def correctFieldName(self, name):
        """Return name with only alphanumerics, underscores, dashes and
           periods allowed"""
        illegalRe = re.compile(r'[^\w_\-.]', re.U)
        name = illegalRe.sub('_', name.strip())
        if not name:
            return u'X'
        if not name[0].isalpha() or name[:3].lower() == 'xml':
            name = u'X' + name
        return name

    def removeField(self, field):
        """Remove all occurances of field from lines
           return False if not found"""
        cnt = 0
        for lineData in self.lineList:
            while field in lineData:
                lineData.remove(field)
                cnt += 1
        self.lineList = filter(None, self.lineList)
        while len(self.lineList) < 2:
            self.lineList.append([''])
        return cnt

    def findLinkField(self):
        """Return most likely field containing a bookmark URL"""
        availFields = [field for field in self.fieldList if \
                       field.typeName == u'URL']
        if len(availFields) == 1:
            return availFields[0]
        if not availFields:
            return None
        for srchTerm in [globalref.docRef.linkFieldName, u'link', u'url',
                         u'href']:
            for field in availFields:
                if field.name.lower() == srchTerm:
                    return field
            for field in availFields:
                if field.name.lower().find(srchTerm) >= 0:
                    return field
        return availFields[0]

    def findAutoChoiceFields(self):
        """Return a list of fields that need to have choices added"""
        return [field for field in self.fieldList if field.autoAddChoices]

    def findUniqueIDFields(self):
        """Set memeber variable and return list of unique ID fields"""
        self.uniqueIDFields = [field for field in self.fieldList
                               if field.typeName == 'UniqueID']
        return self.uniqueIDFields

    def setInitDefaultData(self, data, onlyIfBlank=False):
        """Add initial default data from fields into supplied dict"""
        for field in self.fieldList:
            text = field.getInitDefault()
            if text and (not onlyIfBlank or not data.get(field.name, '')):
                data[field.name] = text

    def updateFromGeneric(self):
        """Update the field names and types in self (a derived type)
           to match generic"""
        if not self.genericType:
            return
        try:
            genericType = globalref.docRef.treeFormats[self.genericType]
        except KeyError:
            print 'Warning - generic type %s not found' % \
                  self.genericType.encode(globalref.localTextEncoding)
            self.genericType = ''
            return
        newFields = []
        for field in genericType.fieldList:
            matchingField = self.findField(field.name)
            if matchingField and field.typeName == matchingField.typeName:
                newFields.append(matchingField)
            else:
                newFields.append(copy.deepcopy(field))
        self.fieldList = newFields
        if self.refField not in self.fieldList:
            self.refField = self.fieldList[0]
        self.updateLineFields()


class FileInfoFormat(NodeFormat):
    """Stores file info type field list and header/footer formatting"""
    name = u'INT_TL_FILE_DATA_FORM'
    fileFieldName = N_('File_Name')
    pathFieldName = N_('File_Path')
    sizeFieldName = N_('File_Size')
    dateFieldName = N_('File_Mod_Date')
    timeFieldName = N_('File_Mod_Time')
    ownerFieldName = N_('File_Owner')
    pageNumFieldName = N_('Page_Number')
    numPagesFieldName = N_('Number_of_Pages')
    def __init__(self):
        NodeFormat.__init__(self, FileInfoFormat.name)
        self.addNewField(FileInfoFormat.fileFieldName)
        self.addNewField(FileInfoFormat.pathFieldName)
        self.addNewField(FileInfoFormat.sizeFieldName, {'type': 'Number'})
        self.addNewField(FileInfoFormat.dateFieldName, {'type': 'Date'})
        self.addNewField(FileInfoFormat.timeFieldName, {'type': 'Time'})
        if not sys.platform.startswith('win'):
            self.addNewField(FileInfoFormat.ownerFieldName)
        # page info only for print header:
        self.addNewField(FileInfoFormat.pageNumFieldName)
        self.fieldList[-1].showInDialog = False
        self.addNewField(FileInfoFormat.numPagesFieldName)
        self.fieldList[-1].showInDialog = False
        for field in self.fieldList:
            field.useFileInfo = True

    def updateFileInfo(self):
        """Update data of file info item"""
        fileName = globalref.docRef.fileName
        item = globalref.docRef.fileInfoItem
        try:
            status = os.stat(fileName)
        except:
            item.data = {}
            return
        item.data[_(FileInfoFormat.fileFieldName)] = os.path.basename(fileName)
        item.data[_(FileInfoFormat.pathFieldName)] = os.path.dirname(fileName)
        item.data[_(FileInfoFormat.sizeFieldName)] = str(status[stat.ST_SIZE])
        modTime = time.localtime(status[stat.ST_MTIME])
        item.data[_(FileInfoFormat.dateFieldName)] = \
                        repr(gendate.GenDate(modTime))
        item.data[_(FileInfoFormat.timeFieldName)] = \
                        repr(gentime.GenTime(modTime))
        if not sys.platform.startswith('win'):
            try:
                item.data[_(FileInfoFormat.ownerFieldName)] = \
                                   pwd.getpwuid(status[stat.ST_UID])[0]
            except KeyError:
                item.data[_(FileInfoFormat.ownerFieldName)] = \
                                   repr(status[stat.ST_UID])

    def getHeaderFooter(self, header=True):
        """Return formatted text for the header or the footer"""
        textLines = self.formatAllTextLines(globalref.docRef.fileInfoItem)
        if header:
            textLines = textLines[:3]
        else:
            textLines = textLines[3:6]
        textLines.extend([''] * (3 - len(textLines)))
        aligns = ['left', 'center', 'right']
        result = ['<table width="100%"><tr>']
        count = 0
        for text, align in zip(textLines, aligns):
            if text:
                result.append('<td align="%s">%s</td>' % (align, text))
                count += 1
        result.append('</tr></table>')
        if count:
            return '\n'.join(result)
        return ''

    def replaceListFormat(self):
        """Copy settings from the treeFormats list to here and
           replace the list's file format object"""
        listFormat = globalref.docRef.treeFormats.get(self.name, None)
        if listFormat:
            for thisField, listField in zip(self.fieldList,
                                            listFormat.fieldList):
                thisField.duplicateSettings(listField)
                thisField.useFileInfo = True
            self.lineList = listFormat.lineList
            globalref.docRef.treeFormats[self.name] = self

    def translateFields(self):
        """Translate field names into the current language,
           called after reading the english version from the file"""
        for field in self.fieldList:
            transName = _(str(field.name))
            if transName != field.name:
                field.enName = field.name
                field.name = transName


class ChildCountFormat(NodeFormat):
    """Placeholder format for child count fields,
       should not show up in main format type list"""
    countFieldName = _('Level', 'child count field')
    def __init__(self):
        NodeFormat.__init__(self, u'CountFormat')
        for level in range(3):
            name = '%s%d' % (ChildCountFormat.countFieldName, level + 1)
            field = fieldformat.CountFormat(name, level + 1)
            self.fieldList.append(field)
