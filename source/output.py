#!/usr/bin/env python

#****************************************************************************
# output.py, provides non-GUI base classes for output of node info
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
import sys
import globalref

breakRegExp = re.compile('(<br[ /]*?>|<BR[ /]*?>)$')


class OutputItem(object):
    """Tree item rich text output class - stores text, level & height"""
    def __init__(self, textLines, level):
        self.textLines = textLines
        if globalref.docRef.spaceBetween:
            self.textLines.append(u'')
        self.level = level
        self.height = len(self.textLines)
        # Removed for non-continuous selections
        # self.firstSibling = False
        # self.lastSibling = False
        # self.hasChildren = False
        self.prefix = ''
        self.suffix = ''

    def addBreaks(self):
        """Add <br> elements to format lines"""
        self.textLines = [line + u'<br />' for line in self.textLines]

    def addInnerBreaks(self):
        """Add <br> elements to all but last format line"""
        self.textLines[:-1] = [line + u'<br />' for line in
                               self.textLines[:-1]]

    def addIndents(self, prevLevel, nextLevel):
        """Add <div> elements to format indented lines, return this level"""
        for num in range(self.level - prevLevel):
            self.textLines[0] = u'<div>%s' % self.textLines[0]
        for num in range(self.level - nextLevel):
            self.textLines[-1] = u'%s</div>' % self.textLines[-1]
        return self.level

    def addAbsoluteIndents(self, pixels=20):
        """Add tags for individual indent,
           since output view does not support nested <div>"""
        self.textLines[0] = u'<div style="margin-left: %dpx">%s' % \
                            (pixels * self.level, self.textLines[0])
        self.textLines[-1] = u'%s</div>' % self.textLines[-1]

    def equalPrefix(self, other):
        """Return True if prefix and suffix are equivalent"""
        return self.prefix.strip().upper() == other.prefix.strip().upper() and \
               self.suffix.strip().upper() == other.suffix.strip().upper()

    def textList(self, withPrefix=False, withSuffix=False):
        """Return list of text lines, optionally with prefix/suffix"""
        textList = self.textLines[:]
        if not textList:
            textList = ['']
        if withPrefix:
            textList[0] = self.prefix + textList[0]
        if withSuffix:
            textList[-1] += self.suffix
        return textList


class OutputGroup(list):
    """List of OutputItems - splits into segments & adds indentation"""
    def __init__(self, initList=[]):
        list.__init__(self, initList)

    def __getslice__(self, i, j):
        """Modified to copy object with slice"""
        return OutputGroup(list.__getslice__(self, i, j))

    def addBreaks(self):
        """Add <br> elements to format lines"""
        for item in self:
            item.addBreaks()

    def addInnerBreaks(self):
        """Add <br> elements to all but last format line of each item"""
        for item in self:
            item.addInnerBreaks()

    def addIndents(self, prevLevel=0):
        """Add <div> elements to indent items"""
        for num in range(len(self)):
            nextLevel = 0
            if num + 1 < len(self):
                nextLevel = self[num + 1].level
            prevLevel = self[num].addIndents(prevLevel, nextLevel)

    def addPrefix(self):
        """Add prefix and suffix text to group items"""
        closeRqd = None
        for item, next in map(None, self, self[1:]):
            lastSibling = not next or next.level != item.level
            if item.prefix and item.textLines and closeRqd == None:
                item.textLines[0] = item.prefix + item.textLines[0]
                closeRqd = item.suffix
            if closeRqd != None and (lastSibling or
                                     not item.equalPrefix(next)):
                if item.textLines:
                    item.textLines[-1] = item.textLines[-1] + closeRqd
                else:
                    item.textLines = [closeRqd]
                closeRqd = None

    def joinPrefixItems(self):
        """Merges adjacent items with same prefix and level for printing"""
        newList = []
        mergeList = OutputGroup()
        for item in self:
            if mergeList and (item.level != mergeList[0].level or
                              not item.prefix or
                              not item.equalPrefix(mergeList[0])):
                mergeList.mergeGroup()
                newList.append(mergeList[0])
                mergeList[:] = []
            mergeList.append(item)
        if mergeList:
            mergeList.mergeGroup()
            newList.append(mergeList[0])
        self[:] = newList

    def mergeGroup(self):
        """Merge self (group of adjacent items)"""
        if len(self) < 2:
            return
        mainItem = self[0]
        for item in self[1:]:
            mainItem.textLines.extend(item.textLines)
        mainItem.height = reduce(lambda x,y: x+y, [item.height for item in
                                                   self])

    def splitColumns(self, numColumns):
        """Split output into even columns, return list with a group for each"""
        if numColumns < 2:
            return [self]
        if len(self) <= numColumns:
            return [OutputGroup([item]) for item in self]
        groupList = []
        numEach = len(self) // numColumns
        for colNum in range(numColumns - 1):
            groupList.append(self[colNum * numEach : (colNum+1) * numEach])
        groupList.append(self[(numColumns-1) * numEach : ])
        numChanges = 1
        while numChanges:
            numChanges = 0
            for colNum in range(numColumns - 1):
                if groupList[colNum].totalHeight() > groupList[colNum+1].\
                   totalHeight() + groupList[colNum][-1].height:
                    groupList[colNum+1].insert(0, groupList[colNum][-1])
                    groupList[colNum] = groupList[colNum][:-1]
                    numChanges += 1
                if groupList[colNum].totalHeight() + groupList[colNum+1][0].\
                   height <= groupList[colNum+1].totalHeight():
                    groupList[colNum].append(groupList[colNum+1][0])
                    groupList[colNum+1] = groupList[colNum+1][1:]
                    numChanges += 1
        return groupList

    def setHeights(self, textHtFunc, totalWidth, indent):
        """Set item heights after adding prefixes and applying fixes,
           textHtFunc is a callback to get height from text"""
        for prevItem, item in zip([None] + self, self):
            width = totalWidth - indent * item.level
            if not prevItem or item.level != prevItem.level or not item.prefix:
                textList = item.textList(True, True)
                item.height = self.textHeight(textList, textHtFunc, width)
            else:
                prevList = prevItem.textList(True, True)
                prevHeight = self.textHeight(prevList, textHtFunc, width)
                fullList = prevItem.textList(True, False) + \
                           item.textList(False, True)
                fullHeight = self.textHeight(fullList, textHtFunc, width)
                item.height = fullHeight - prevHeight

    def textHeight(self, textList, textHtFunc, width):
        """Return text height after joining"""
        text = u'<br>\n'.join(textList)
        if breakRegExp.search(text):
            text += '&nbsp;'   # add space if ends with break for proper height
        return textHtFunc(text, width)

    def totalHeight(self):
        """Return the combined height of items in the group"""
        return reduce(lambda x, y: x+y, [item.height for item in self])

    def splitPages(self, pageHeight, pageActiveLevels=None,
                   firstChildAdjust=0.2):
        """Split output by pageHeight, return list with a group for each,
           record levels for lines in pageActiveLevels,
           firstChildAdjust is fraction of page left blank to avoid break
           between parent and 1st child"""
        groupList = [OutputGroup()]
        height = 0
        for item in self:
            if height + item.height > pageHeight:
                height = 0
                nextGroup = OutputGroup()
                if firstChildAdjust:
                    lastGroup = groupList[-1][:]
                    tmpItem = item
                    deltaHeight = 0
                    while lastGroup and \
                          tmpItem.level == lastGroup[-1].level + 1:
                        tmpItem = lastGroup.pop()
                        nextGroup.insert(0, tmpItem)
                        deltaHeight += tmpItem.height
                    if nextGroup and \
                           deltaHeight < pageHeight * firstChildAdjust:
                        groupList[-1] = lastGroup
                        height = deltaHeight
                    else:
                        nextGroup = OutputGroup()
                groupList.append(nextGroup)
            height += item.height
            groupList[-1].append(item)
        if pageActiveLevels == []:
            for pageNum in range(len(groupList)):
                levels = []
                minLevel = sys.maxint
                scanPage = pageNum + 1
                while scanPage < len(groupList) and minLevel > 1:
                    for item in groupList[scanPage]:
                        if item.level and item.level < minLevel:
                            minLevel = item.level
                            levels.append(item.level)
                    scanPage += 1
                pageActiveLevels.append(levels)
        return groupList

    def getLines(self):
        """Return full list of text lines from this group"""
        lines = []
        for item in self:
            lines.extend(item.textLines)
        return lines
