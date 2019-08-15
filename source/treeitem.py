#!/usr/bin/env python

#****************************************************************************
# treeitem.py, provides non-GUI base classes for tree items
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that i has with empty titles.t will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#****************************************************************************

import os
import sys
import codecs
import copy
import re
from xml.sax.saxutils import escape
import treedoc
import nodeformat
import numbering
import output
import globalref
try:
    from __main__ import __version__
except ImportError:
    __version__ = ''

_defaultTitle = _('New')

class TreeItem(object):
    """Data storage item for tree structure"""
    blankTitle = _('[BLANK TITLE]')
    maxLevel = 0  # for ODF export
    dirExportLinkRe = re.compile(r'<a href="#(.+)">')
    dirExportDirRe = re.compile(r'[/\\"*?|<>:]')
    def __init__(self, parent, formatName, initText='', addDefaultData=False):
        self.parent = parent
        self.formatName = formatName
        self.data = {}
        self.childList = []
        if initText:
            self.setTitle(initText)
        if addDefaultData:
            self.nodeFormat().setInitDefaultData(self.data)
        self.open = False
        self.viewData = None
        self.level = 0    # updated only by numbered descend list

    def setInitDefaultData(self):
        """Set initial default data to fields if any"""
        self.nodeFormat().setInitDefaultData(self.data)

    def nodeFormat(self):
        """Return this node's format object"""
        return globalref.docRef.treeFormats[self.formatName]

    def title(self):
        """Return title text"""
        text = self.nodeFormat().formatTitle(self)
        if not text:
            text = TreeItem.blankTitle
        return text

    def setTitle(self, title, addUndo=False):
        """Set title text, return True if changed successfully"""
        title = u' '.join(title.split())
        if title:
            if self.nodeFormat().setTitle(title, self, addUndo):
                globalref.docRef.modified = True
                return True
        return False

    def changeType(self, newFormatName):
        """Change nodeFormat to new, update title fields if they'd be blank"""
        origTitle = self.nodeFormat().formatTitle(self)
        self.formatName = newFormatName
        format = self.nodeFormat()
        format.setInitDefaultData(self.data, True)
        if not format.formatTitle(self):
            format.setTitle(origTitle, self, False)

    def formatText(self, skipEmpty=True, addPrefix=False, addSuffix=False,
                   internal=False):
        """Return list of formatted text lines"""
        return self.nodeFormat().formatText(self, skipEmpty, addPrefix,
                                            addSuffix, internal)

    def formatChildText(self, skipEmpty=True, internal=False):
        """Return list of all children's formatted text lines"""
        return self.formatTextItems(self.childList, skipEmpty, internal)

    def formatTextItems(self, itemList, skipEmpty=True, internal=False):
        """Return list of formatted text lines for items in list"""
        if not itemList:
            return []
        result = []
        sep = []
        prefixAdded = False
        for item, next in map(None, itemList, itemList[1:]):
            addPrefix = not prefixAdded
            prefixAdded = True
            addSuffix = False
            if not next or not item.nodeFormat().\
                               equalPrefix(next.nodeFormat()):
                addSuffix = True
                prefixAdded = False
            result.extend(sep + item.formatText(skipEmpty, addPrefix,
                                                addSuffix, internal))
            sep = globalref.docRef.spaceBetween and [u''] or []
        return result

    def duplicateNode(self):
        """Return a copy of self with its children and uniqueIDs adjusted"""
        newNode = copy.deepcopy(self)
        newNode.setDescendantUniqueID(True)
        return newNode

    def refFieldText(self):
        """Return text from ref field"""
        return self.data.get(self.nodeFormat().refField.name, '')

    def outputItemList(self, includeRoot=True, openOnly=False,
                       addAnchors=False, level=0):
        """Return list of OutputItems for all descendants"""
        outList = output.OutputGroup()
        if includeRoot:
            outList.append(self.outputItem(addAnchors, level))
        else:
            level -= 1
        if self.open or not openOnly:
            for child in self.childList:
                outList.extend(child.outputItemList(True, openOnly,
                               addAnchors, level + 1))
        return outList

    def outputItem(self, addAnchors=False, level=0):
        """Return OutputItem for self"""
        lines = self.formatText()
        if not lines:
            lines = ['']
        if addAnchors:
            for anchor in filter(None, self.refFieldText().split('\n')):
                lines[0] = u'<a id="%s" />%s' % (anchor, lines[0])
        outItem = output.OutputItem(lines, level)
        outItem.prefix = self.nodeFormat().sibPrefix
        outItem.suffix = self.nodeFormat().sibSuffix
        return outItem

    def branchXml(self, typeList=None, writeOptions=False):
        """Return list of xml lines, include format info if not in typeList"""
        nodeFormat = self.nodeFormat()
        if typeList == None:  # default writes no format info
            typeList = globalref.docRef.treeFormats.values()
        xmlList = [u'<%s item="y"' % escape(nodeFormat.name,
                                            treedoc.escDict)]
        if writeOptions:
            if not globalref.docRef.spaceBetween:
                xmlList[0] += u' nospace="y"'
            if not globalref.docRef.lineBreaks:
                xmlList[0] += u' nobreaks="y"'
            if not globalref.docRef.formHtml:
                xmlList[0] += u' nohtml="y"'
            if globalref.docRef.childFieldSep != \
                                treedoc.TreeDoc.childFieldSepDflt:
                xmlList[0] += u' childsep="%s"' % \
                              escape(globalref.docRef.childFieldSep,
                                     treedoc.escDict)
            if globalref.docRef.spellChkLang:
                xmlList[0] += u' spellchk="%s"' % \
                              escape(globalref.docRef.spellChkLang,
                                     treedoc.escDict)
            if globalref.docRef.xslCssLink:
                xmlList[0] += u' xslcss="%s"' % globalref.docRef.xslCssLink
            if __version__:
                xmlList[0] += u' tlversion="%s"' % \
                              escape(__version__, treedoc.escDict)
        addFormat = nodeFormat not in typeList  # writes format on 1st only
        if addFormat:
            xmlList.extend(nodeFormat.formatXml())
            typeList.append(nodeFormat)
        xmlList[-1] += u'>'
        for field in nodeFormat.fieldList:
            text = self.data.get(field.name, '')
            if text or addFormat:
                escKey = escape(field.englishName(), treedoc.escDict)
                fieldFormat = ''
                if addFormat:
                    fieldFormat = field.writeXml()
                    if field == nodeFormat.refField:
                        fieldFormat += u' ref="y"'
                xmlList.append(u'<%s%s>%s</%s>' %
                               (escKey, fieldFormat,
                                escape(text, treedoc.escDict), escKey))
        for child in self.childList:
            xmlList.extend(child.branchXml(typeList))
        if writeOptions:      # write format info for any unused formats
            for format in globalref.docRef.treeFormats.values():
                if format not in typeList:
                    name =  escape(format.name, treedoc.escDict)
                    xmlList.append(u'<%s item="n"' % name)
                    xmlList.extend(format.formatXml())
                    xmlList[-1] += u'>'
                    for field in format.fieldList:
                        escKey = escape(field.englishName(), treedoc.escDict)
                        fieldFormat = field.writeXml()
                        if field == format.refField:
                            fieldFormat += u' ref="y"'
                        xmlList.append(u'<%s%s></%s>' % (escKey, fieldFormat,
                                                         escKey))
                    xmlList.append(u'</%s>' % name)
        xmlList.append(u'</%s>' % escape(nodeFormat.name, treedoc.escDict))
        return xmlList

    def exportToText(self, level=0, openOnly=False):
        """Write tabbed list of descendants titles"""
        textList = [u'\t' * level + self.title()]
        if self.open or not openOnly:
            for child in self.childList:
                textList.extend(child.exportToText(level + 1, openOnly))
        return textList

    def exportDirTable(self, linkDict, parentTitle=None, header='', footer=''):
        """Write dir structure with html tables"""
        if not self.childList:
            return
        try:
            dirName = self.exportDirName(True)
            if not os.access(dirName, os.R_OK):
                os.mkdir(dirName, 0755)
            os.chdir(dirName)
        except (OSError, ValueError, UnicodeError):
            print 'Error - cannot create directory', dirName
            raise IOError(_('Error - cannot create directory %s') % dirName)
        title = self.title()
        lines = [u'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 '\
                 'Transitional//EN">', u'<html>', u'<head>',
                 u'<meta http-equiv="Content-Type" content="text/html; '\
                 'charset=utf-8">', u'<title>%s</title>' % title,
                 u'</head>', u'<body>']
        if header:
            lines.append(header)
        lines.append(u'<h1 align="center">%s</h1>' % title)
        if parentTitle:
            label = _('Parent: ')
            lines.append(u'<p align="center">%s'
                          '<a href="../index.html">%s</a></p>' %
                         (label, parentTitle))
        lines.extend([u'<table cellpadding="10">', u'<tr>'])
        ### headings kludge????
        headings = self.childList[0].nodeFormat().lineFields()
        lines.extend([u'<th><u>%s</u></th>' % cell for cell in headings])
        lines.append(u'</tr><tr>')
        for child in self.childList:
            textList = []
            for line in child.formatText(False):
                for match in TreeItem.dirExportLinkRe.finditer(line):
                    anchor = match.group(1)
                    absPath = linkDict.get(anchor, '')
                    if absPath:
                        curPath = unicode(dirName, sys.getfilesystemencoding())
                        relPath = treedoc.relativePath(curPath, absPath)
                        relPath = os.path.join(relPath, 'index.html')
                        if os.sep != '/':
                            relPath = relPath.replace(os.sep, '/')
                        link = '<a href="%s#%s">' % (relPath, anchor)
                        line = TreeItem.dirExportLinkRe.sub(link, line)
                textList.append(line)
            childDir = child.exportDirName(False)
            if child.childList:
                textList[0] = u'<a href="%s/index.html">%s</a>' % \
                              (childDir, textList[0])
            for anchor in filter(None, child.refFieldText().split('\n')):
                textList[0] = u'<a id="%s" />%s' % (anchor, textList[0])
            lines.extend([u'<td>%s</td>' % cell for cell in textList])
            lines.append(u'</tr><tr>')
        lines.extend([u'</tr>', u'</table>'])
        if footer:
            lines.append(footer)
        lines.extend([u'</body>', u'</html>'])
        try:
            f = codecs.open('index.html', 'w', 'utf-8')
            f.writelines([line + '\n' for line in lines])
        except IOError:
            print 'Error - could not write file to', dirName
            raise IOError(_('Error - cannot write file to %s') % dirName)
        f.close()
        for child in self.childList:
            child.exportDirTable(linkDict, title, header, footer)
        os.chdir('..')

    def createDirTableLinkDict(self, linkDict, path):
        """Create dict to store parent directories for internal links"""
        for anchor in filter(None, self.refFieldText().split('\n')):
            linkDict[anchor] = path
        path = os.path.join(path, self.exportDirName(False))
        for child in self.childList:
            child.createDirTableLinkDict(linkDict, path)

    def exportDirPage(self, linkDict, level=0):
        """Write directory structure with navigation bar and full pages"""
        title = self.title()
        lines = [u'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 '\
                  'Transitional//EN">', u'<html>', u'<head>',
                 u'<meta http-equiv="Content-Type" content="text/html; '\
                  'charset=utf-8">',
                 u'<link rel="stylesheet" type="text/css" '\
                   'href="%sdefault.css" />' % ('../' * level),
                 u'<title>%s</title>' % title,
                 u'</head>', u'<body>', u'<div id="sidebar">']
        links = []
        for item in self.childList:
            links.append(u'&nbsp; &nbsp; &nbsp; &nbsp; &bull; '\
                          '<a href="%s/%s.html">%s</a><br />' %
                         (self.exportDirName(False), item.exportDirName(False),
                          item.title()))
        uncleList = []
        if self.parent and level > 0:
            siblingList = self.parent.childList
            if self.parent.parent and level > 1:
                uncleList = self.parent.parent.childList
            else:
                uncleList = [self.parent]
        else:
            siblingList = [self]
        pos = 0
        for item in siblingList:
            if item is self:
                links.insert(pos, u'&nbsp; &nbsp; &bull; <b>%s</b><br />' %
                             self.title())
                pos = len(links)
            else:
                links.insert(pos,
                             u'&nbsp; &nbsp; &bull; '\
                              '<a href="%s.html">%s</a><br />' %
                             (item.exportDirName(False), item.title()))
            pos += 1
        pos = 0
        for item in uncleList:
            links.insert(pos,
                         u'&bull; <a href="../%s.html">%s</a><br />' %
                         (item.exportDirName(False), item.title()))
            if item is self.parent:
                pos = len(links)
            pos += 1
        lines.extend(links)
        lines.append('</div>')
        textList = []
        for line in self.formatText(True, True, True):
            for match in TreeItem.dirExportLinkRe.finditer(line):
                anchor = match.group(1)
                absPath = linkDict.get(anchor, '')
                if absPath:
                    curPath = unicode(os.getcwd(), sys.getfilesystemencoding())
                    relPath = treedoc.relativePath(curPath, absPath)
                    if os.sep != '/':
                        relPath = relPath.replace(os.sep, '/')
                    link = '<a href="%s">' % relPath
                    line = TreeItem.dirExportLinkRe.sub(link, line)
            textList.append(line)
        sep = globalref.docRef.lineBreaks and u'<br />\n' or u'\n'
        lines.append(sep.join(textList))
        lines.extend([u'</body>', u'</html>'])
        dirName = self.exportDirName(True)
        fileName = '%s.html' % dirName
        try:
            f = codecs.open(fileName, 'w', 'utf-8')
            f.writelines([line + '\n' for line in lines])
        except (IOError, UnicodeError):
            print 'Error - could not write file to %s', fileName
            raise IOError(_('Error - cannot write file to %s') % fileName)
        f.close()
        if self.childList:
            try:
                if not os.access(dirName, os.R_OK):
                    os.mkdir(dirName, 0755)
                os.chdir(dirName)
            except (OSError, ValueError, UnicodeError):
                print 'Error - cannot create directory', dirName
                raise IOError(_('Error - cannot create directory %s')
                              % dirName)
            for child in self.childList:
                child.exportDirPage(linkDict, level + 1)
            os.chdir('..')

    def createDirPageLinkDict(self, linkDict, path):
        """Create dict to store parent directories for internal links"""
        dirName = self.exportDirName(False)
        for anchor in filter(None, self.refFieldText().split('\n')):
            linkDict[anchor] = os.path.join(path, '%s.html' % dirName)
        path = os.path.join(path, dirName)
        for child in self.childList:
            child.createDirPageLinkDict(linkDict, path)

    def exportDirName(self, encode=False):
        """Return legal directory name for exporting to directories"""
        try:
            dirName = filter(None, self.refFieldText().split('\n'))[0]
        except IndexError:
            dirName = ''
        dirName = dirName.encode(sys.getfilesystemencoding(), 'replace')
        if not encode:
            dirName = unicode(dirName, sys.getfilesystemencoding())
        dirName = TreeItem.dirExportDirRe.sub('', dirName)
        if not dirName:
            dirName = '___'
        return dirName

    def exportXbelBookmarks(self, level=0, addBranch=True):
        """Return text list with descendant bookmarks in XBEL format"""
        indentsPerLevel = 3
        indent = ' ' * (indentsPerLevel * level)
        nextIndent = ' ' * (indentsPerLevel * (level + 1))
        title = escape(self.title(), treedoc.escDict)
        if not self.childList and level > 0:
            nodeFormat = self.nodeFormat()
            field = nodeFormat.findLinkField()
            if field:
                link = escape(self.data.get(field.name, ''), treedoc.escDict)
                if link:
                    return [u'%s<bookmark href="%s">' % (indent, link),
                            u'%s<title>%s</title>' % (nextIndent, title),
                            u'%s</bookmark>' % indent]
            elif not nodeFormat.fieldList or \
                 (len(nodeFormat.fieldList) == 1 and
                  not self.data.get(nodeFormat.fieldList[0].name, '')):
                return [u'%s<separator/>' % indent]
        result = []
        if level > 0:
            result = [u'%s<folder>' % indent]
            result.append(u'%s<title>%s</title>' % (nextIndent, title))
        if addBranch:
            for child in self.childList:
                result.extend(child.exportXbelBookmarks(level + 1))
        if level > 0:
            result.append(u'%s</folder>' % indent)
        return result

    def exportHtmlBookmarks(self, level=0, addBranch=True):
        """Return text list with descendant bookmarks in Mozilla format"""
        indentsPerLevel = 4
        indent = ' ' * (indentsPerLevel * level)
        title = escape(self.title())
        if not self.childList and level > 0:
            nodeFormat = self.nodeFormat()
            field = nodeFormat.findLinkField()
            if field:
                link = self.data.get(field.name, '')
                if link:
                    return [u'%s<DT><A HREF="%s">%s</A>' % (indent, link,
                                                            title)]
            elif not nodeFormat.fieldList or \
                 (len(nodeFormat.fieldList) == 1 and
                  not self.data.get(nodeFormat.fieldList[0].name, '')):
                return [u'%s<HR>' % indent]
        result = []
        if level > 0:
            result = [u'%s<DT><H3>%s</H3>' % (indent, title)]
        if addBranch and self.childList:
            result.append(u'%s<DL><p>' % indent)
            for child in self.childList:
                result.extend(child.exportHtmlBookmarks(level + 1))
            result.append(u'%s</DL><p>' % indent)
        return result

    def exportGenericXml(self, textFieldName, level=0, addBranch=True):
        """Return text list with descendant nodes in generic XML format"""
        indentsPerLevel = 3
        indent = ' ' * (indentsPerLevel * level)
        nodeFormat = self.nodeFormat()
        result = u'%s<%s' % (indent, self.formatName)
        for fieldName in nodeFormat.fieldNames():
            text = self.data.get(fieldName, '')
            if text and fieldName != textFieldName:
                result = u'%s %s="%s"' % (result, fieldName,
                                          escape(text, treedoc.escDict))
        result += u'>'
        if textFieldName in nodeFormat.fieldNames():
            text = self.data.get(textFieldName, '')
            if text:
                result += escape(text, treedoc.escDict)
        if not addBranch or not self.childList:
            return [u'%s</%s>' % (result, self.formatName)]
        result = [result]
        for child in self.childList:
            result.extend(child.exportGenericXml(textFieldName, level+1))
        result.append(u'%s</%s>' % (indent, self.formatName))
        return result

    def exportOdf(self, level=0, addBranch=True, includeRoot=True,
                  openOnly=False):
        """Return text list with descendant nodes in an ODF format text file"""
        result = []
        if includeRoot:
            TreeItem.maxLevel = max(level, TreeItem.maxLevel)
            lines = self.nodeFormat().formatPlainTextLines(self)
            title = lines[0]
            if not title:
                title = TreeItem.blankTitle
            output = lines[1:]
            result = [u'<text:h text:outline-level="%d" '\
                       'text:style-name="Heading_20_%d">%s</text:h>' %
                      (level, level, escape(title, treedoc.escDict))]
            if output and title == output[0]:
                del output[0]     # remove first line if same as title
            if output:
                for line in '\n'.join(output).split('\n'):
                    result.append(u'<text:p text:outline-level="%d" '\
                                   'text:style-name="Text_20_body">%s'\
                                   '</text:p>' %
                                  (level, escape(line, treedoc.escDict)))
        else:
            level -= 1
        if addBranch and self.childList and (self.open or not openOnly):
            for child in self.childList:
                result.extend(child.exportOdf(level + 1, addBranch, True,
                              openOnly))
        return result

    def loadTabbedChildren(self, bufList, level=0):
        """Recursive read of TreeItems from tabbed buffer"""
        while bufList:
            if bufList[0][0] == level + 1:
                buf = bufList.pop(0)
                child = TreeItem(self, self.formatName, buf[1])
                self.childList.append(child)
                if not child.loadTabbedChildren(bufList, level + 1):
                    return False
            elif 0 < bufList[0][0] <= level:
                return True
            else:
                return False
        return True

    def editChildList(self, textList):
        """Update child names and order from textList, update undos and view"""
        if len(textList) == len(self.childList):
            # assume rename if length is same
            for child, text in zip(self.childList, textList):
                if child.title() != text:
                    child.setTitle(text, True)
                    globalref.updateViewItem(child)
        else:                # find new child positions if length differs
            oldLen = len(self.childList)
            nodeFormat = self.nodeFormat()
            newType = globalref.docRef.treeFormats.get(nodeFormat.childType,
                                                       None)
            if not newType:
                newType = oldLen and self.childList[0].nodeFormat() or \
                          nodeFormat
            globalref.docRef.undoStore.addChildListUndo(self)
            newChildList = []
            for text in textList:
                try:
                    newChildList.append(self.childList.pop(\
                     [child.title() for child in self.childList].index(text)))
                except ValueError:
                    newItem = TreeItem(self, newType.name)
                    newItem.setInitDefaultData()
                    newItem.setTitle(text)
                    newItem.setUniqueID(True)
                    newChildList.append(newItem)
            if oldLen == 0 and newChildList:
                self.open = True
            for child in self.childList:
                child.parent = None
            self.childList = newChildList
            globalref.updateLeftView()
            globalref.docRef.modified = True

    def descendantList(self, inclClosed=False, level=0):
        """Recursive list of TreeItems, default to open only, sets level num,
           returns list"""
        descendList = [self]
        self.level = level
        if self.open or inclClosed:
            for child in self.childList:
                descendList.extend(child.descendantList(inclClosed, level+1))
        return descendList

    def descendantGen(self):
        """Return generator to step thru all descendants (including closed),
           include self"""
        yield self
        for child in self.childList:
            for item in child.descendantGen():
                yield item

    def descendantGenNoRoot(self):
        """Return generator to step thru all descendants (including closed),
           do not include self"""
        for child in self.childList:
            yield child
            for item in child.descendantGenNoRoot():
                yield item

    def ancestorList(self):
        """Return list all parents and grandparents of self"""
        item = self.parent
        result = []
        while item:
            result.append(item)
            item = item.parent
        return result

    def allAncestorsOpen(self):
        """Returns True if all ancestors are set open"""
        closeList = [item for item in self.ancestorList() if not item.open]
        if closeList:
            return False
        return True

    def hasDescendant(self, child):
        """Return True if self has descendant child"""
        for item in self.descendantGen():
            if item is child:
                return True
        return False

    def lastDescendant(self, inclClosed=False):
        """Return self's last descendant,
           required to be open if not inclClosed"""
        item = self
        while True:
            if item.childList and (item.open or inclClosed):
                item = item.childList[-1]
            else:
                return item

    def usesType(self, formatName):
        """Return True if dataType is used by self or descendants"""
        for item in self.descendantGen():
            if item.formatName == formatName:
                return True
        return False

    def isValid(self):
        """Return True if self has root as an ancestor"""
        item = self
        while item.parent:
            item = item.parent
        return item == globalref.docRef.root

    def numChildren(self):
        """Return number of children"""
        return len(self.childList)

    def childPos(self, child):
        """Return the number of the referenced child or -1"""
        for num, item in enumerate(self.childList):
            if item is child:
                return num
        return -1

    def childText(self):
        """Return list of child item strings (not recursive)"""
        return [child.title() for child in self.childList]

    def maxDescendLevel(self, thisLevel=0):
        """Return max number of levels below this node"""
        if not self.childList:
            return thisLevel
        return max([child.maxDescendLevel(thisLevel + 1) for child
                    in self.childList])

    def descendLevelList(self, level=1):
        """Return a list of descendants at the given level"""
        newList = [self]
        for i in range(level):
            oldList = newList
            newList = []
            for item in oldList:
                newList.extend(item.childList)
        return newList

    def prevSibling(self):
        """Return nearest older sibling or None"""
        if self.parent:
            i = self.parent.childPos(self)
            if i > 0:
                return self.parent.childList[i-1]
        return None

    def nextSibling(self):
        """Return next younger sibling or None"""
        if self.parent:
            i = self.parent.childPos(self) + 1
            if i < len(self.parent.childList):
                return self.parent.childList[i]
        return None

    def prevItem(self, inclClosed=False):
        """Return previous sibling or parent or None"""
        sib = self.prevSibling()
        if sib:
            while sib.numChildren() and (sib.open or inclClosed):
                sib = sib.childList[-1]
            return sib
        return self.parent

    def nextItem(self, inclClosed=False):
        """Return first child, next sibling or ancestors next sibling
           or None"""
        if self.childList and (self.open or inclClosed):
            return self.childList[0]
        ancestor = self
        while ancestor:
            sib = ancestor.nextSibling()
            if sib:
                return sib
            ancestor = ancestor.parent
        return None

    def delete(self):
        """Remove self from the tree structure - return parent on success"""
        parent = self.parent
        if not parent:
            return None
        parent.childList.remove(self)
        self.parent = None
        globalref.docRef.modified = True
        return parent

    def addChild(self, text=_defaultTitle, pos=-1):
        """Add new child before position, -1 is at end - return new item"""
        if pos < 0:
            pos = len(self.childList)
        newFormat = self.nodeFormat().childType
        if newFormat not in globalref.docRef.treeFormats:
            newFormat = self.childList and self.childList[0].formatName or \
                        self.formatName
        newItem = TreeItem(self, newFormat, text, True)
        newItem.setUniqueID(True)
        self.childList.insert(pos, newItem)
        globalref.docRef.modified = True
        return newItem

    def insertSibling(self, text=_defaultTitle, inAfter=False):
        """Add new sibling before or after self - return new item on success"""
        if not self.parent:
            return None
        pos = self.parent.childPos(self)
        if inAfter:
            pos += 1
        newFormat = self.parent.nodeFormat().childType
        if newFormat not in globalref.docRef.treeFormats:
            newFormat = self.formatName
        newItem = TreeItem(self.parent, newFormat, text, True)
        newItem.setUniqueID(True)
        self.parent.childList.insert(pos, newItem)
        globalref.docRef.modified = True
        return newItem

    def addTree(self, rootItem, pos=-1):
        """Add new tree as a child before position, -1 is at end
           return item"""
        if pos < 0:
            pos = len(self.childList)
        self.childList.insert(pos, rootItem)
        rootItem.parent = self
        globalref.docRef.modified = True
        return rootItem

    def insertTree(self, rootItem, inAfter=False):
        """Add new tree before or after self - return item on success"""
        if not self.parent:
            return None
        pos = self.parent.childPos(self)
        if inAfter:
            pos += 1
        self.parent.childList.insert(pos, rootItem)
        rootItem.parent = self.parent
        globalref.docRef.modified = True
        return rootItem

    def indent(self):
        """Becomes a child of the previous sibling - return self on success"""
        newParent = self.prevSibling()
        if not newParent:
            return None
        self.delete()
        newParent.addTree(self, -1)
        globalref.docRef.modified = True
        return self

    def unindent(self):
        """Becomes its parents next sibling - return self on success"""
        sibling = self.parent
        if not sibling or not sibling.parent:
            return None
        self.delete()
        sibling.insertTree(self, True)
        globalref.docRef.modified = True
        return self

    def move(self, amount=-1):
        """Switch self with sibling, -1=up, 1=down, return self on success"""
        if self.parent:
            i = self.parent.childPos(self)
            j = i + amount
            if 0 <= j < len(self.parent.childList):
                self.parent.childList[i], self.parent.childList[j] = \
                                          self.parent.childList[j], self
                globalref.docRef.modified = True
                return self
        return None

    def moveFirst(self):
        """Move self to be first child of parent"""
        if self.parent:
            self.parent.childList.remove(self)
            self.parent.childList.insert(0, self)
            globalref.docRef.modified = True

    def moveLast(self):
        """Move self to be last child of parent"""
        if self.parent:
            self.parent.childList.remove(self)
            self.parent.childList.append(self)
            globalref.docRef.modified = True

    def openBranch(self, setOpen=True):
        """Recursive open/close of all descendants, close if setOpen=False"""
        self.open = setOpen
        for child in self.childList:
            child.openBranch(setOpen)

    def openParents(self, openSelf=True):
        """Open self's ancestors and self if openSelf, 
           return list of changed items"""
        openList = []
        item = openSelf and self or self.parent
        while item:
            if not item.open and item.childList:
                item.open = True
                openList.append(item)
            item = item.parent
        return openList

    def cmpItems(self, item1, item2):
        """Compare function for sorting, not case sensitive"""
        if not globalref.docRef.sortFields[0][0]:
            factor = globalref.docRef.sortFields[0][1] and 1 or -1
            return factor * cmp(item1.title().lower(), item2.title().lower())
        for field, direction in globalref.docRef.sortFields:
            field1 = item1.nodeFormat().findField(field)
            field2 = item2.nodeFormat().findField(field)
            factor = direction and 1 or -1
            if field1.sortSequence == field2.sortSequence:
                result = cmp(field1.sortValue(item1.data),
                             field2.sortValue(item2.data))
                if result != 0:
                    return factor * result
            else:
                return factor * cmp(field1.sortSequence, field2.sortSequence)
        return 0

    def sortChildren(self):
        """Sort item children, not case sensitive"""
        self.childList.sort(self.cmpItems)

    def sortBranch(self):
        """Sort item descendants, not case sensitive"""
        self.childList.sort(self.cmpItems)
        for child in self.childList:
            child.sortBranch()

    def sortTypeChildren(self, formatNames):
        """Sort item children of the given formats"""
        childOfTypeList = [child for child in self.childList
                           if child.formatName in formatNames]
        if childOfTypeList:
            childOfTypeList.sort(self.cmpItems)
            if len(childOfTypeList) < len(self.childList):
                childOfTypeList.extend([child for child in self.childList
                                       if child.formatName not in formatNames])
            self.childList = childOfTypeList

    def sortTypeBranch(self, formatNames):
        """Sort item descendants of a given format type"""
        self.sortTypeChildren(formatNames)
        for child in self.childList:
            child.sortTypeBranch(formatNames)

    def matchWords(self, wordList):
        """Return True if all words are in data fields, not case sensitive"""
        dataStr = u' '.join(self.data.values()).lower()
        for word in wordList:
            if dataStr.find(word) == -1:
                return False
        return True

    def matchRefText(self, searchStr):
        """Return True if searchStr matches a line in ref field data"""
        lines = self.data.get(self.nodeFormat().refField.name, '').split('\n')
        if searchStr in lines:
            return True
        return False

    def cmpFields(self, fieldNames, item):
        """Return True if listed fields are the same in item and self"""
        for field in fieldNames:
            if self.data.get(field, '') != item.data.get(field, ''):
                return False
        return True

    def findEquivFields(self, fieldNames, itemList):
        """Return first item from list with same listed fields or None"""
        for item in itemList:
            if self.cmpFields(fieldNames, item):
                return item
        return None

    def editFields(self, valueDict):
        """Set values for fields based on dictionary"""
        for fieldName, value in valueDict.iteritems():
            field = self.nodeFormat().findField(fieldName)
            if field:
                newValue, ok = field.storedText(value)
                if ok:
                    value = newValue
            self.data[fieldName] = value
        globalref.docRef.modified = True

    def childTypes(self):
        """Return list of all type names found in children"""
        types = []
        for item in self.childList:
            if item.formatName not in types:
                types.append(item.formatName)
        return types

    def descendTypes(self):
        """Return list of all type names found in descendants"""
        types = []
        for item in self.descendantGenNoRoot():
            if item.formatName not in types:
                types.append(item.formatName)
        return types

    def branchFields(self):
        """Return names of all fields found in self and descendents"""
        types = []
        for item in self.descendantGen():
            if item.formatName not in types:
                types.append(item.formatName)
        fieldNames = []
        for type in types:
            for field in globalref.docRef.treeFormats[type].fieldNames():
                if field not in fieldNames:
                    fieldNames.append(field)
        return fieldNames

    def setConditionalType(self):
        """Set self to type based on auto condtional settings"""
        itemFormat = self.nodeFormat()
        genericName = itemFormat.genericType
        if not genericName:
            genericName = self.formatName
        formatList = globalref.docRef.treeFormats.derivedDict.\
                     get(genericName, [])[:]
        if not formatList:
            return
        formatList.remove(itemFormat)
        formatList.insert(0, itemFormat)  # reorder to give priority
        neutralResult = None
        for format in formatList:
            if format.conditional:
                if format.conditional.evaluate(self.data):
                    self.formatName = format.name
                    return
            elif not neutralResult:
                neutralResult = format.name
        if neutralResult:
            self.formatName = neutralResult

    def setDescendantCondTypes(self):
        """Set children recursively to type based on condtional settings"""
        self.setConditionalType()
        for child in self.childList:
            child.setDescendantCondTypes()

    def setUniqueID(self, replaceExist=False):
        """Add a unique ID to UID fields if empty"""
        for field in self.nodeFormat().uniqueIDFields:
            if not self.data.get(field.name, '') or replaceExist:
                self.data[field.name] = field.nextValue()

    def setDescendantUniqueID(self, replaceExist=False):
        """Add a unique ID to descendant UID fields if empty"""
        self.setUniqueID(replaceExist)
        for child in self.childList:
            child.setDescendantUniqueID(replaceExist)

    def filterDescendants(self, typeName, expr):
        """Remove children of given type recursively if expr is false"""
        for child in self.childList[:]:
            if child.formatName != typeName or expr(child.data):
                child.filterDescendants(typeName, expr)
            else:
                self.childList.remove(child)
                child.parent = None
                globalref.docRef.modified = True

    def addChildCat(self, catList):
        """Add child's category items as a new child level to expand data"""
        catSuffix = _('TYPE', 'child category suffix')
        newType = u'%s_%s' % (catList[0], catSuffix)
        num = 1
        while newType in globalref.docRef.treeFormats and \
              globalref.docRef.treeFormats[newType].fieldNames() != catList:
            newType = u'%s_%s_%d' % (catList[0], catSuffix, num)
            num += 1
        newFormat = nodeformat.NodeFormat(newType, {}, catList[0])
        globalref.docRef.treeFormats[newType] = newFormat
        for field in catList[1:]:
            newFormat.addNewField(field)
        newItems = []
        for child in self.childList:
            newParent = child.findEquivFields(catList, newItems)
            if not newParent:
                newParent = TreeItem(self, newType)
                newParent.setUniqueID(True)
                for field in catList:
                    newParent.data[field] = child.data.get(field, '')
                newItems.append(newParent)
            newParent.childList.append(child)
            child.parent = newParent
        self.childList = newItems
        globalref.docRef.modified = True

    def flatChildCat(self):
        """Collapse data by merging fields"""
        origTreeFormats = copy.deepcopy(globalref.docRef.treeFormats)
        self.childList = [item for item in self.descendantGen() if not
                          item.childList]
        for item in self.childList:
            origFields = origTreeFormats[item.formatName].fieldNames()
            addedFields = []
            oldParent = item.parent
            while oldParent != self:
                for field in origTreeFormats[oldParent.formatName].\
                             fieldNames():
                    newField = field
                    num = 1
                    while newField in origFields or newField in addedFields:
                        newField = u'%s_%d' % (field, num)
                        num += 1
                    item.data[newField] = oldParent.data.get(field, '')
                    addedFields.append(newField)
                    item.nodeFormat().addFieldIfNew(newField)
                oldParent = oldParent.parent
            item.parent = self
        globalref.docRef.modified = True

    def arrangeByRef(self, refField):
        """Arrange data using parent references"""
        descendList = self.descendantList(True)[1:]
        for item in descendList:
            item.childList = []
        self.childList = []
        for item in descendList:
            refText = item.data.get(refField, '')
            parentList = [parent for parent in descendList if
                          parent.refFieldText() == refText]
            if len(parentList) > 1:   # pick nearest parent above the item
                itemPos = descendList.index(item)
                while len(parentList) > 1 and \
                      descendList.index(parentList[1]) < itemPos:
                    del parentList[0]
            if not parentList or parentList[0] == item:
                item.parent = self
            else:
                item.parent = parentList[0]
            item.parent.childList.append(item)
        globalref.docRef.modified = True

    def flatByRef(self, refField):
        """Collapse data after adding references to parents"""
        descendList = self.descendantList(True)[1:]
        self.childList = descendList
        for item in descendList:
            item.childList = []
            item.data[refField] = item.parent.refFieldText()
            item.parent = self
            item.nodeFormat().addFieldIfNew(refField)
        globalref.docRef.modified = True

    def updateByRef(self, refRoot):
        """Update with new fields from reference file with matched ref field
           Return a tuple describing changes"""
        refData = {}
        for item in refRoot.descendantGen():
            refData[item.refFieldText()] = item
        formatChgs = {}
        numNewEntries = 0
        for item in self.descendantGen():
            itemFormat = item.nodeFormat()
            fields = itemFormat.fieldNames()
            try:
                ref = refData[item.data[itemFormat.refField.name]]
                for field in ref.data.keys():
                    if field not in fields:
                        item.data[field] = ref.data[field]
                        numNewEntries += 1
                        formatChgs.setdefault(itemFormat.name, {}).\
                                 setdefault(field,
                                            ref.nodeFormat().findField(field))
            except KeyError:
                pass
        numChgTypes = 0
        numNewFields = 0
        for typeName in formatChgs.keys():
            type = globalref.docRef.treeFormats[typeName]
            ref = formatChgs[typeName]
            numChgTypes += 1
            for field in ref.values():
                type.fieldList.append(field)
                numNewFields += 1
        if numNewEntries:
            globalref.docRef.modified = True
        return (numNewEntries, numNewFields, numChgTypes)

    def addNumbering(self, field, format, rootIncluded, appendToParent,
                     addField=True, singleLevel=False, startNum=1,
                     currentLevel=0):
        """Add number field to this node and descendants"""
        if rootIncluded:
            if addField or self.nodeFormat().findField(field):
                self.data[field] = numbering.numSeries(startNum, startNum + 1,
                                                       format[currentLevel])[0]
                self.nodeFormat().addFieldIfNew(field)
                globalref.docRef.modified = True
            currentLevel += 1
            startNum = 1
        if not self.childList:
            return
        globalref.docRef.modified = True
        numList = numbering.numSeries(startNum,
                                      len(self.childList) + startNum,
                                      format[currentLevel])
        if appendToParent and currentLevel:
            numList = [self.data.get(field, '') + numText for numText
                       in numList]
        for item in self.childList:
            if addField or item.nodeFormat().findField(field):
                item.data[field] = numList.pop(0)
                item.nodeFormat().addFieldIfNew(field)
        if not singleLevel:
            for item in self.childList:
                item.addNumbering(field, format, False, appendToParent,
                                  addField, False, 1, currentLevel + 1)

