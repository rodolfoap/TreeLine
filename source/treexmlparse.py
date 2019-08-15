#!/usr/bin/env python

#****************************************************************************
# treexmlparse.py, provides classes to read XML and HTML files
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
import xml.sax
import HTMLParser
import nodeformat
from treeitem import TreeItem
from treeformats import TreeFormats


class TreeSaxHandler(xml.sax.ContentHandler):
    """Handler to read xml thru sax"""
    def __init__(self, docRef):
        xml.sax.ContentHandler.__init__(self)
        self.docRef = docRef
        self.currentItem = None
        self.bareFormat = None
        self.rootItem = None
        self.formats = {}
        self.dataEntry = ''
        self.text = ''

    def startElement(self, name, attrs):
        """Called by the reader at the open tag of each element"""
        if attrs.get(u'item', ''):  # reading TreeItem or bare format
            format = self.formats.get(name, None)
            if not format:
                format = nodeformat.NodeFormat(name, attrs)
                self.formats[name] = format

            if attrs.get(u'item', '') == 'y':  # reading TreeItem
                newItem = TreeItem(self.currentItem, name)
                if self.currentItem:
                    self.currentItem.childList.append(newItem)
                else:
                    self.rootItem = newItem
                    if attrs.get(u'nospace', '').startswith('y'):
                        self.docRef.spaceBetween = False
                    if attrs.get(u'nobreaks', '').startswith('y'):
                        self.docRef.lineBreaks = False
                    if attrs.get(u'nohtml', '').startswith('y'):
                        self.docRef.formHtml = False
                    if attrs.get(u'childsep', ''):
                        self.docRef.childFieldSep = attrs.get(u'childsep', '')
                    self.docRef.spellChkLang = attrs.get(u'spellchk', '')
                    self.docRef.xslCssLink = attrs.get(u'xslcss', '')
                    self.docRef.tlVersion = attrs.get(u'tlversion', '')
                self.currentItem = newItem
            else:                    # reading bare format
                self.bareFormat = format

        else:                        # reading data
            self.text = ''
            self.dataEntry = name
            if not self.currentItem:
                raise xml.sax.SAXException, 'No valid item'
            currentFormat = self.bareFormat
            if not currentFormat:
                try:
                    currentFormat = self.formats[self.currentItem.formatName]
                except KeyError:
                    raise xml.sax.SAXException, 'Invalid node type'
            if name not in currentFormat.fieldNames(): # add new field to format
                try:
                    currentFormat.addNewField(name, attrs)
                except (NameError, KeyError):
                    raise xml.sax.SAXException, 'Invalid field type'

    def endElement(self, name):
        """Called by the reader at the close tag of each element"""
        if not self.currentItem:
            raise xml.sax.SAXException, 'No valid item'
        if self.dataEntry == name:   # finish data
            # self.simplifyText()
            if self.text:
                self.currentItem.data[name] = self.text
            self.dataEntry = ''
        else:                         # finish TreeItem
            if self.bareFormat:
                assert(self.bareFormat.name == name)
                self.bareFormat = None
            else:
                assert(self.currentItem.formatName == name)
                self.currentItem = self.currentItem.parent

    def characters(self, content):
        """Called by the reader to process text"""
        self.text += content

    def simplifyText(self):
        """Remove extra whitespace from text"""
        self.text = u' '.join(self.text.split())

    def processingInstruction(self, target, data):
        """Recover xlst link from stylesheet instruction"""
        self.docRef.xlstLink = u' '.join((target, data))


class XbelSaxHandler(xml.sax.ContentHandler):
    """Handler to parse XBEL bookmark format"""
    def __init__(self, folderFormat, bookmarkFormat, separatorFormat):
        xml.sax.ContentHandler.__init__(self)
        self.folderFormat = folderFormat
        self.bookmarkFormat = bookmarkFormat
        self.separatorFormat = separatorFormat
        self.currentItem = None
        self.rootItem = None
        self.text = ''

    def startElement(self, name, attrs):
        """Called by the reader at the open tag of each element"""
        if name == u'folder' or name == u'xbel':
            newItem = TreeItem(self.currentItem, self.folderFormat.name)
            if self.currentItem:
                self.currentItem.childList.append(newItem)
            else:
                self.rootItem = newItem
            if attrs.get(u'folded', '') == 'no':
                newItem.open = True
            self.currentItem = newItem
        elif name == u'bookmark':
            newItem = TreeItem(self.currentItem, self.bookmarkFormat.name)
            if self.currentItem:
                self.currentItem.childList.append(newItem)
            else:
                raise xml.sax.SAXException, 'No valid parent folder'
            newItem.data[TreeFormats.linkFieldName] = attrs.get(u'href', '')
            self.currentItem = newItem
        elif name == u'title':
            self.text = ''
        elif name == u'separator':
            newItem = TreeItem(self.currentItem, self.separatorFormat.name)
            if self.currentItem:
                self.currentItem.childList.append(newItem)
            else:
                raise xml.sax.SAXException, 'No valid parent folder'
            self.currentItem = newItem
        else:   # unsupported tags
            pass

    def endElement(self, name):
        """Called by the reader at the close tag of each element"""
        if not self.currentItem:
            raise xml.sax.SAXException, 'No valid item'
        if name in (u'folder', u'xbel', u'bookmark', u'separator'):
            self.currentItem = self.currentItem.parent
        elif name == u'title':
            self.currentItem.data[TreeFormats.fieldDefault] = \
                       u' '.join(self.text.split())
        else:   # unsupported tags
            pass

    def characters(self, content):
        """Called by the reader to process text"""
        self.text += content


class OdfSaxHandler(xml.sax.ContentHandler):
    """Handler to parse Open Document Format (ODF) file"""
    numExp = re.compile(r'.*?(\d+)$')
    def __init__(self, rootItem, defaultFormat):
        xml.sax.ContentHandler.__init__(self)
        self.rootItem = rootItem
        self.defaultFormat = defaultFormat
        self.inTextArea = False
        self.currentItem = rootItem
        self.currentLevel = 0
        self.text = u''

    def startElement(self, name, attrs):
        """Called by the reader at the open tag of each element"""
        if self.inTextArea:
            if name == u'text:h':
                style = attrs.get(u'text:style-name', '')
                try:
                    level = int(OdfSaxHandler.numExp.match(style).group(1))
                except AttributeError:
                    raise xml.sax.SAXException, 'Illegal heading style name'
                if level > self.currentLevel + 1 or level < 1:
                    raise xml.sax.SAXException, 'Invalid heading structure'
                while self.currentLevel >= level:
                    self.currentItem = self.currentItem.parent
                    self.currentLevel -= 1
                self.addItem(level)
                self.text = ''
            elif name == u'text:p':
                if self.currentItem == self.rootItem:
                    self.addItem(1)  # add node for text without heading
                if self.currentItem.data.get(TreeFormats.textFieldName, u''):
                    self.text = u'\n'
                else:
                    self.text = u''
        elif name == u'office:text':
            self.inTextArea = True
            self.text = u''

    def addItem(self, level):
        """Add a child of the current item"""
        item = TreeItem(self.currentItem, self.defaultFormat.name)
        self.currentItem.childList.append(item)
        self.currentItem = item
        self.currentLevel = level

    def addText(self, fieldName):
        """Append text to given field name in current item"""
        if self.text:
            currText = self.currentItem.data.get(fieldName, '')
            self.currentItem.data[fieldName] = currText + self.text
        self.text = u''

    def endElement(self, name):
        """Called by the reader at the close tag of each element"""
        if not self.inTextArea:
            return
        if name == u'office:text':
            self.inTextArea = False
        elif name == u'text:h':
            self.addText(TreeFormats.fieldDefault)
        elif name == u'text:p':
            self.addText(TreeFormats.textFieldName)

    def characters(self, content):
        """Called by the reader to process text"""
        self.text += content


class GenericXmlHandler(xml.sax.ContentHandler):
    """Handler to parse generic XML (non-TreeLine file)"""
    textFieldName = _('Element_Data', 'xml field name')
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.formats = {}
        self.currentItem = None
        self.rootItem = None
        self.text = ''

    def startElement(self, name, attrs):
        """Called by the reader at the open tag of each element"""
        format = self.formats.get(name, None)
        if not format:
            format = nodeformat.NodeFormat(name)
            self.formats[name] = format
        newItem = TreeItem(self.currentItem, name)
        if self.currentItem:
            self.currentItem.childList.append(newItem)
        elif self.rootItem:
            raise xml.sax.SAXException, 'Invalid XML file'
        else:
            self.rootItem = newItem
        self.currentItem = newItem
        for key in attrs.keys():
            format.addFieldIfNew(key)
            newItem.data[key] = attrs[key]

    def endElement(self, name):
        """Called by the reader at the close tag of each element"""
        if not self.currentItem:
            raise xml.sax.SAXException, 'No valid item'
        self.text = self.text.strip()
        if self.text:
            self.formats[self.currentItem.formatName].\
                        addFieldIfNew(GenericXmlHandler.textFieldName)
            self.currentItem.data[GenericXmlHandler.textFieldName] = self.text
            self.text = ''
        self.currentItem = self.currentItem.parent

    def characters(self, content):
        """Called by the reader to process text"""
        self.text += content


class HtmlBookmarkHandler(HTMLParser.HTMLParser):
    """Handler to parse XBEL bookmark format"""
    escDict = {'amp': '&', 'lt': '<', 'gt': '>', 'quot': '"'}
    def __init__(self, folderFormat, bookmarkFormat, separatorFormat):
        HTMLParser.HTMLParser.__init__(self)
        self.folderFormat = folderFormat
        self.bookmarkFormat = bookmarkFormat
        self.separatorFormat = separatorFormat
        self.rootItem = TreeItem(None, self.folderFormat.name)
        self.rootItem.data[TreeFormats.fieldDefault] = _('Bookmarks')
        self.currentItem = self.rootItem
        self.currentParent = None
        self.text = ''

    def handle_starttag(self, tag, attrs):
        """Called by the reader at each open tag"""
        if tag == 'dt' or tag == 'h1':      # start any entry
            self.text = ''
        elif tag == 'dl':    # start indent
            self.currentParent = self.currentItem
            self.currentItem = None
        elif tag == 'h3':    # start folder
            if not self.currentParent:
                raise HtmlParseError, 'No valid parent folder'
            self.currentItem = TreeItem(self.currentParent,
                                        self.folderFormat.name)
            self.currentParent.childList.append(self.currentItem)
        elif tag == 'a':     # start link
            if not self.currentParent:
                raise HtmlParseError, 'No valid parent folder'
            self.currentItem = TreeItem(self.currentParent,
                                        self.bookmarkFormat.name)
            self.currentParent.childList.append(self.currentItem)
            for name, value in attrs:
                if name == 'href':
                    self.currentItem.data[TreeFormats.linkFieldName] = value
        elif tag == 'hr':     # separator
            if not self.currentParent:
                raise HtmlParseError, 'No valid parent folder'
            item = TreeItem(self.currentParent, self.separatorFormat.name)
            self.currentParent.childList.append(item)
            self.currentItem = None

    def handle_endtag(self, tag):
        """Called by the reader at each end tag"""
        if tag == 'dl':      # end indented section
            self.currentParent = self.currentParent.parent
            self.currentItem = None
        elif tag == 'h3' or tag == 'a':    # end folder or link
            if not self.currentItem:
                raise HtmlParseError, 'No valid item'
            self.currentItem.data[TreeFormats.fieldDefault] = self.text
        elif tag == 'h1':    # end main title
            self.rootItem.data[TreeFormats.fieldDefault] = self.text

    def handle_data(self, data):
        """Called by the reader to process text"""
        self.text += data

    def handle_entityref(self, name):
        """Convert escaped entity ref to char"""
        self.text += HtmlBookmarkHandler.escDict.get(name, '')


class HtmlParseError(Exception):
    """Exception class for errors on reading HTML content"""
    pass
