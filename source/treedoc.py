#!/usr/bin/env python

#****************************************************************************
# treedoc.py, provides non-GUI base classes for document data
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#****************************************************************************

import sys
import os.path
import xml.sax.saxutils
import codecs
import gzip
import zipfile
import StringIO
import p3
import nodeformat
from treeformats import TreeFormats
from treeitem import TreeItem
import treeselection
import treexmlparse
import undo
import optiondefaults
import globalref
try:
    from __main__ import __version__
except ImportError:
    __version__ = '??'

escDict = {'"': '&quot;', chr(12): ''}   # added quotes
for c in range(9) + range(11, 13) + range(14, 32):
    escDict[chr(c)] = ''                 # ignore low ascii chars
unEscDict = {'&quot;': '"'}
encryptPrefix = '>>TL+enc'

tabbedImport = 'readTabbed'
tableImport = 'readTable'
textLineImport = 'readLines'
textParaImport = 'readPara'
treepadImport = 'readTreepad'
xbelImport = 'readXbel'
mozillaImport = 'readMozilla'
xmlImport = 'readXml'
odfImport = 'readOdf'

class TreeDoc(object):
    """Tree document class - stores root and has tree utilities"""
    passwordDict = {}
    childFieldSepDflt = ', '
    rootTitleDefault = _('Main', 'default root title')
    folderName = _('FOLDER', 'bookmark format folder name')
    bookmarkName = _('BOOKMARK', 'bookmark format name')
    separatorName = _('SEPARATOR', 'bookmark format separator name')
    bookmarkRootTitle = _('Bookmarks')
    copyFormat = None
    def __init__(self, filePath=None, setNewDefaults=False, importType=None):
        """Open filePath (can also be file ref) if given,
           setNewDefaults uses user defaults for compression & encryption,
           importType gives an import method to read the file"""
        globalref.docRef = self
        self.root = None
        self.treeFormats = TreeFormats()
        self.fileInfoItem = TreeItem(None, nodeformat.FileInfoFormat.name)
        self.fileInfoFormat = None
        TreeDoc.copyFormat = nodeformat.NodeFormat('_DUMMY__ROOT_', {},
                                                   TreeFormats.fieldDefault)
        self.undoStore = undo.UndoRedoStore()
        self.redoStore =  undo.UndoRedoStore()
        self.sortFields = ['']
        self.fileName = ''
        self.spaceBetween = True
        self.lineBreaks = True
        self.formHtml = True
        self.childFieldSep = TreeDoc.childFieldSepDflt
        self.spellChkLang = ''
        self.xlstLink = ''
        self.xslCssLink = ''
        self.tlVersion = __version__
        self.fileInfoFormat = nodeformat.FileInfoFormat()
        if filePath:
            if importType:
                getattr(self, importType)(filePath)
            else:
                self.readFile(filePath)
        else:
            self.treeFormats = TreeFormats({}, True)
            self.root = TreeItem(None, TreeFormats.rootFormatDefault)
            self.root.setTitle(TreeDoc.rootTitleDefault)
        self.modified = False
        if setNewDefaults or not hasattr(self, 'compressFile'):
            self.compressFile = globalref.options.boolData('CompressNewFiles')
            self.encryptFile = globalref.options.boolData('EncryptNewFiles')
        elif not hasattr(self, 'encryptFile'):
            self.encryptFile = False
        self.selection = treeselection.TreeSelection([self.root])
        self.fileInfoFormat.translateFields()
        self.fileInfoFormat.updateFileInfo()

    def hasPassword(self, filePath):
        """Return True if a password is available for filePath"""
        key = filePath.encode(sys.getfilesystemencoding())
        return TreeDoc.passwordDict.has_key(key)

    def setPassword(self, filePath, password):
        """Set encrytion password for the filePath"""
        key = filePath.encode(sys.getfilesystemencoding())
        TreeDoc.passwordDict[key] = password.encode('utf-8')

    def clearPassword(self, filePath):
        """Remove password for filePath if present"""
        key = filePath.encode(sys.getfilesystemencoding())
        try:
            del TreeDoc.passwordDict[key]
        except KeyError:
            pass

    def getReadFileObj(self, fileRef):
        """Return file object and set self.compressFile to False/True,
           fileRef is either file path or file object"""
        if not hasattr(fileRef, 'read'):
            fileRef = file(fileRef.encode(sys.getfilesystemencoding()), 'rb')
            # binary mode req'd for encryption
        if hasattr(fileRef, 'seek'):
            fileRef.seek(0)
        prefix = fileRef.read(2)
        if hasattr(fileRef, 'seek'):
            fileRef.seek(0)
        else:
            oldFileRef = fileRef
            fileRef = StringIO.StringIO(prefix + oldFileRef.read())
            fileRef.name = oldFileRef.name
            oldFileRef.close()
        if prefix == '\037\213':
            name = fileRef.name
            fileRef = gzip.GzipFile(fileobj=fileRef)
            fileRef.name = name
        # may already be a gzip object from before password prompt
        self.compressFile = isinstance(fileRef, gzip.GzipFile)
        return fileRef

    def decryptFile(self, fileObj):
        """Decrypt file if was encrypted"""
        name = fileObj.name
        prefix = fileObj.read(len(encryptPrefix))
        self.encryptFile = prefix == encryptPrefix
        if self.encryptFile:
            password = TreeDoc.passwordDict.get(fileObj.name, '')
            if not password:
                fileObj.close()
                raise PasswordError, 'Missing password'
            try:
                text = p3.p3_decrypt(fileObj.read(), password)
            except p3.CryptError:
                fileObj.close()
                raise PasswordError, 'Incorrect password'
            fileObj.close()
            fileObj = StringIO.StringIO(text)
            fileObj.name = name
        else:
            fileObj.seek(0)
        return fileObj

    def getEncodedFileObj(self, fileRef, encoding, errors):
        """Return open file object with specified encoding"""
        return codecs.getreader(encoding)(self.getReadFileObj(fileRef), errors)

    def getWriteFileObj(self, fileRef, forceCompress):
        """Return write file object, compressed or not based on forceCompress,
           but always compress if has .gz extension,
           fileRef is either file path or file object"""
        if not hasattr(fileRef, 'read'):
            fileRef = file(fileRef.encode(sys.getfilesystemencoding()), 'wb')
        if fileRef.name.endswith('.gz') or forceCompress:
            name = fileRef.name
            fileRef = gzip.GzipFile(fileobj=fileRef)
            fileRef.name = name
        return fileRef

    def readFile(self, fileRef):
        """Open and read file - raise exception on failure,
           fileRef is either file path or file object"""
        filePath = hasattr(fileRef, 'read') and \
                   unicode(fileRef.name, sys.getfilesystemencoding()) or \
                   fileRef
        try:
            f = self.getReadFileObj(fileRef)
            f = self.decryptFile(f)
            handler = treexmlparse.TreeSaxHandler(self)
            input = xml.sax.InputSource()
            input.setByteStream(f)
            input.setEncoding('utf-8')
            reader = xml.sax.make_parser()
            reader.setContentHandler(handler)
            reader.setFeature(xml.sax.handler.feature_external_ges, 0)
            reader.parse(input)
        except IOError:
            print 'Error - could not read file', \
                  filePath.encode(globalref.localTextEncoding)
            raise
        except UnicodeError:
            print 'Error - bad Unicode in file', \
                  filePath.encode(globalref.localTextEncoding)
            f.close()
            raise
        except xml.sax.SAXException:
            f.close()
            raise ReadFileError(_('Could not open as treeline file'))
        f.close()
        self.root = handler.rootItem
        self.fileName = filePath
        self.treeFormats = TreeFormats(handler.formats)
        self.fileInfoFormat.replaceListFormat()
        self.treeFormats.updateAutoChoices()
        self.treeFormats.updateUniqueID()
        self.treeFormats.updateDerivedTypes()
        if not self.tlVersion:  # file from before 0.12.80, fix number format
            for format in self.treeFormats.values():
                for field in format.fieldList:
                    if field.typeName == 'Number':
                        field.format = field.format.replace(',', '\,')

    def readTabbed(self, fileRef, errors='strict'):
        """Import tabbed data into a flat tree - raise exception on failure"""
        try:
            f = self.getEncodedFileObj(fileRef, globalref.localTextEncoding,
                                       errors)
            filePath = unicode(f.name, sys.getfilesystemencoding())
            textList = f.readlines()
        except UnicodeError:
            print 'Warning - bad unicode characters were replaced'
            if errors == 'strict':
                self.readTabbed(fileRef, 'replace')
            else:
                f.close()
            return
        f.close()
        bufList = [(text.count('\t', 0, len(text) - len(text.lstrip())),
                    text.strip()) for text in textList if text.strip()]
        if bufList:
            buf = bufList.pop(0)
            if buf[0] == 0:
                # set default formats ROOT & DEFAULT
                self.treeFormats = TreeFormats({}, True)
                newRoot = TreeItem(None, TreeFormats.rootFormatDefault)
                newRoot.setTitle(buf[1])
                if newRoot.loadTabbedChildren(bufList):
                    self.root = newRoot
                    self.fileName = filePath
                    return
        raise ReadFileError(_('Error in tabbed list'))

    def readTable(self, fileRef, errors='strict'):
        """Import table data into a flat tree - raise exception on failure"""
        try:
            f = self.getEncodedFileObj(fileRef, globalref.localTextEncoding,
                                       errors)
            filePath = unicode(f.name, sys.getfilesystemencoding())
            textList = f.readlines()
        except UnicodeError:
            print 'Warning - bad unicode characters were replaced'
            if errors == 'strict':
                self.readTable(fileRef, 'replace')
            else:
                f.close()
            return
        f.close()
        self.treeFormats = TreeFormats({}, True)  # set defaults ROOT & DEFAULT
        newRoot = TreeItem(None, TreeFormats.rootFormatDefault)
        defaultFormat = self.treeFormats[TreeFormats.formatDefault]
        defaultFormat.fieldList = []
        defaultFormat.lineList = []
        defaultFormat.addTableFields(textList.pop(0).strip().split('\t'))
        newRoot.setTitle(TreeDoc.rootTitleDefault)
        for line in textList:
            newItem = TreeItem(newRoot, TreeFormats.formatDefault)
            newRoot.childList.append(newItem)
            lineList = line.strip().split('\t')
            try:
                for num in range(len(lineList)):
                    newItem.data[self.treeFormats[TreeFormats.formatDefault].
                            fieldList[num].name] = lineList[num].strip()
            except IndexError:
                print 'Too few headings to read data as a table'
                raise ReadFileError(_('Too few headings to read data as table'))
        self.root = newRoot
        self.fileName = filePath

    def readLines(self, fileRef, errors='strict'):
        """Import plain text, node per line"""
        try:
            f = self.getEncodedFileObj(fileRef, globalref.localTextEncoding,
                                       errors)
            filePath = unicode(f.name, sys.getfilesystemencoding())
            textList = f.readlines()
        except UnicodeError:
            print 'Warning - bad unicode characters were replaced'
            if errors == 'strict':
                self.readLines(fileRef, 'replace')
            else:
                f.close()
            return
        f.close()
        self.treeFormats = TreeFormats({}, True)  # set defaults ROOT & DEFAULT
        newRoot = TreeItem(None, TreeFormats.rootFormatDefault)
        defaultFormat = self.treeFormats[TreeFormats.formatDefault]
        defaultFormat.fieldList = []
        defaultFormat.lineList = []
        defaultFormat.addTableFields([TreeFormats.textFieldName])
        newRoot.setTitle(TreeDoc.rootTitleDefault)
        for line in textList:
            line = line.strip()
            if line:
                newItem = TreeItem(newRoot, TreeFormats.formatDefault)
                newRoot.childList.append(newItem)
                newItem.data[TreeFormats.textFieldName] = line
        self.root = newRoot
        self.fileName = filePath

    def readPara(self, fileRef, errors='strict'):
        """Import plain text, blank line delimitted"""
        try:
            f = self.getEncodedFileObj(fileRef, globalref.localTextEncoding,
                                       errors)
            filePath = unicode(f.name, sys.getfilesystemencoding())
            fullText = f.read().replace('\r', '')
        except UnicodeError:
            print 'Warning - bad unicode characters were replaced'
            if errors == 'strict':
                self.readPara(fileRef, 'replace')
            else:
                f.close()
            return
        textList = fullText.split('\n\n')
        f.close()
        self.treeFormats = TreeFormats({}, True)  # set defaults ROOT & DEFAULT
        newRoot = TreeItem(None, TreeFormats.rootFormatDefault)
        defaultFormat = self.treeFormats[TreeFormats.formatDefault]
        defaultFormat.fieldList = []
        defaultFormat.lineList = []
        defaultFormat.iconName = 'doc'
        defaultFormat.addTableFields([TreeFormats.textFieldName])
        defaultFormat.fieldList[0].numLines = globalref.options.\
                                               intData('MaxEditLines', 1,
                                                    optiondefaults.maxNumLines)
        newRoot.setTitle(TreeDoc.rootTitleDefault)
        for line in textList:
            line = line.strip()
            if line:
                newItem = TreeItem(newRoot, TreeFormats.formatDefault)
                newRoot.childList.append(newItem)
                newItem.data[TreeFormats.textFieldName] = line
        self.root = newRoot
        self.fileName = filePath

    def readTreepad(self, fileRef, errors='strict'):
        """Read Treepad text-node file"""
        try:
            f = self.getEncodedFileObj(fileRef, globalref.localTextEncoding,
                                       errors)
            filePath = unicode(f.name, sys.getfilesystemencoding())
            textList = f.read().split('<end node> 5P9i0s8y19Z')
            f.close()
        except UnicodeError:  # error common - broken unicode on windows
            print 'Warning - bad unicode characters were replaced'
            if errors == 'strict':
                self.readTreepad(fileRef, 'replace')
            else:
                f.close()
            return
        self.treeFormats = TreeFormats()
        format = nodeformat.NodeFormat(TreeFormats.formatDefault)
        titleFieldName = _('Title', 'title field name')
        format.addNewField(titleFieldName)
        format.addLine(u'{*%s*}' % titleFieldName)
        numLines = globalref.options.intData('MaxEditLines', 1,
                                             optiondefaults.maxNumLines)
        format.addNewField(TreeFormats.textFieldName,
                           {'lines': repr(numLines)})
        format.addLine(u'{*%s*}' % TreeFormats.textFieldName)
        self.treeFormats[format.name] = format
        itemList = []
        for text in textList:
            text = text.strip()
            if text:
                try:
                    text = text.split('<node>', 1)[1].lstrip()
                    lines = text.split('\n')
                    title = lines[0]
                    level = int(lines[1])
                    lines = lines[2:]
                except (ValueError, IndexError):
                    print 'Error - bad file format in %s' % \
                          filePath.encode(globalref.localTextEncoding)
                    raise ReadFileError(_('Bad file format in %s') % filePath)
                item = TreeItem(None, format.name)
                item.data[titleFieldName] = title
                item.data[TreeFormats.textFieldName] = '\n'.join(lines)
                item.level = level
                itemList.append(item)
        self.root = itemList[0]
        parentList = []
        for item in itemList:
            if item.level != 0:
                parentList = parentList[:item.level]
                item.parent = parentList[-1]
                parentList[-1].childList.append(item)
            parentList.append(item)
        self.root = itemList[0]
        self.fileName = filePath

    def createBookmarkFormat(self):
        """Return a set of formats for bookmark imports"""
        treeFormats = TreeFormats()
        format = nodeformat.NodeFormat(TreeDoc.folderName)
        format.addNewField(TreeFormats.fieldDefault)
        format.addLine(u'{*%s*}' % TreeFormats.fieldDefault)
        format.addLine(u'{*%s*}' % TreeFormats.fieldDefault)
        format.iconName = 'folder_3'
        treeFormats[format.name] = format
        format = nodeformat.NodeFormat(TreeDoc.bookmarkName)
        format.addNewField(TreeFormats.fieldDefault)
        format.addLine(u'{*%s*}' % TreeFormats.fieldDefault)
        format.addLine(u'{*%s*}' % TreeFormats.fieldDefault)
        format.addNewField(TreeFormats.linkFieldName, {'type': 'URL'})
        format.addLine(u'{*%s*}' % TreeFormats.linkFieldName)
        format.iconName = 'bookmark'
        treeFormats[format.name] = format
        format = nodeformat.NodeFormat(TreeDoc.separatorName)
        format.addNewField(TreeFormats.fieldDefault)
        format.addLine(u'------------------')
        format.addLine(u'<hr>')
        treeFormats[format.name] = format
        return treeFormats

    def readXbel(self, fileRef):
        """Read XBEL format bookmarks"""
        formats = self.createBookmarkFormat()
        try:
            f = self.getReadFileObj(fileRef)
            filePath = unicode(f.name, sys.getfilesystemencoding())
            handler = treexmlparse.\
                      XbelSaxHandler(formats[TreeDoc.folderName],
                                     formats[TreeDoc.bookmarkName],
                                     formats[TreeDoc.separatorName])
            input = xml.sax.InputSource()
            input.setByteStream(f)
            input.setEncoding('utf-8')
            reader = xml.sax.make_parser()
            reader.setContentHandler(handler)
            reader.setFeature(xml.sax.handler.feature_external_ges, 0)
            reader.parse(input)
        except UnicodeError:
            print 'Error - bad Unicode in file', \
                  filePath.encode(globalref.localTextEncoding)
            f.close()
            raise ReadFileError(_('Problem with Unicode characters in file'))
        except xml.sax.SAXException:
            f.close()
            raise ReadFileError(_('Could not open as XBEL file'))
        f.close()
        if not handler.rootItem:
            raise ReadFileError(_('Could not open as XBEL file'))
        self.root = handler.rootItem
        if not self.root.data.get(TreeFormats.fieldDefault, ''):
            self.root.data[TreeFormats.fieldDefault] = \
                      TreeDoc.bookmarkRootTitle
        self.fileName = filePath
        self.treeFormats = formats

    def readMozilla(self, fileRef, errors='strict'):
        """Read Mozilla HTML format bookmarks"""
        formats = self.createBookmarkFormat()
        try:
            f = self.getEncodedFileObj(fileRef, 'utf-8', errors)
            filePath = unicode(f.name, sys.getfilesystemencoding())
            fullText = f.read()
        except UnicodeError:
            print 'Warning - bad unicode characters were replaced'
            if errors == 'strict':
                self.readMozilla(fileRef, 'replace')
            else:
                f.close()
            return
        try:
            handler = treexmlparse.\
                      HtmlBookmarkHandler(formats[TreeDoc.folderName],
                                          formats[TreeDoc.bookmarkName],
                                          formats[TreeDoc.separatorName])
            handler.feed(fullText)
            handler.close()
        except treexmlparse.HtmlParseError:
            raise ReadFileError(_('Could not open as HTML bookmark file'))
        if not handler.rootItem:
            raise ReadFileError(_('Could not open as HTML bookmark file'))
        self.root = handler.rootItem
        if not self.root.data.get(TreeFormats.fieldDefault, ''):
            self.root.data[TreeFormats.fieldDefault] = \
                      TreeDoc.bookmarkRootTitle
        self.fileName = filePath
        self.treeFormats = formats

    def readXml(self, fileRef):
        """Read a generic (non-TreeLine) XML file"""
        try:
            f = self.getReadFileObj(fileRef)
            filePath = unicode(f.name, sys.getfilesystemencoding())
            handler = treexmlparse.GenericXmlHandler()
            input = xml.sax.InputSource()
            input.setByteStream(f)
            input.setEncoding('utf-8')
            reader = xml.sax.make_parser()
            reader.setContentHandler(handler)
            reader.setFeature(xml.sax.handler.feature_external_ges, 0)
            reader.parse(input)
        except UnicodeError:
            print 'Error - bad Unicode in file', \
                  filePath.encode(globalref.localTextEncoding)
            f.close()
            raise ReadFileError(_('Problem with Unicode characters in file'))
        except xml.sax.SAXException:
            f.close()
            raise ReadFileError(_('Could not open XML file'))
        f.close()
        if not handler.rootItem:
            raise ReadFileError(_('Could not open XML file'))
        self.root = handler.rootItem
        self.fileName = filePath
        self.treeFormats = TreeFormats(handler.formats)
        for format in self.treeFormats.values():
            format.fixImportedFormat(treexmlparse.GenericXmlHandler.
                                                  textFieldName)

    def readOdf(self, fileRef):
        """Read an Open Document Format (ODF) file"""
        self.treeFormats = TreeFormats(None, True)
        rootItem = TreeItem(None, TreeFormats.rootFormatDefault,
                            TreeDoc.rootTitleDefault)
        defaultFormat = self.treeFormats[TreeFormats.formatDefault]
        defaultFormat.addNewField(TreeFormats.textFieldName,
                                  {u'html': 'n', u'lines': '6'})
        defaultFormat.changeOutputLines([u'<b>{*%s*}</b>' %
                                         TreeFormats.fieldDefault,
                                         u'{*%s*}' %
                                         TreeFormats.textFieldName])
        try:
            f = self.getReadFileObj(fileRef)
            filePath = unicode(f.name, sys.getfilesystemencoding())
            zip = zipfile.ZipFile(f, 'r')
            text = zip.read('content.xml')
            handler = treexmlparse.OdfSaxHandler(rootItem, defaultFormat)
            xml.sax.parseString(text, handler)
        except (zipfile.BadZipfile, KeyError):
            f.close()
            raise ReadFileError(_('Could not unzip ODF file'))
        except UnicodeError:
            f.close()
            raise ReadFileError(_('Problem with Unicode characters in file'))
        except xml.sax.SAXException:
            f.close()
            raise ReadFileError(_('Could not open corrupt ODF file'))
        f.close()
        self.root = rootItem
        self.fileName = filePath

    def readXmlString(self, string):
        """Read xml string and return top item or None"""
        try:
            handler = treexmlparse.TreeSaxHandler(self)
            xml.sax.parseString(string.encode('utf-8'), handler)
        except xml.sax.SAXException:
            return None
        return handler.rootItem

    def readXmlStringAndFormat(self, string):
        """Read xml string and return tuple of top item and new formats"""
        try:
            handler = treexmlparse.TreeSaxHandler(self)
            xml.sax.parseString(string.encode('utf-8'), handler)
        except xml.sax.SAXException:
            return (None, [])
        formats = [format for format in handler.formats.values()
                   if format.name not in self.treeFormats]
        try:
            formats.remove(TreeDoc.copyFormat)
        except ValueError:
            pass
        formatNames = [format.name for format in formats] + \
                       self.treeFormats.keys()
        for format in formats:
            if format.genericType not in formatNames:
                format.genericType = ''
        return (handler.rootItem, formats)

    def writeFile(self, fileRef, updateInfo=True):
        """Write file - raises IOError on failure"""
        lines = [u'<?xml version="1.0" encoding="utf-8" ?>']
        if self.xlstLink:
            lines.append(u'<?%s?>' % self.xlstLink)
        lines.extend(self.root.branchXml([], True))
        text = '\n'.join(lines).encode('utf-8')
        try:
            f = self.getWriteFileObj(fileRef, self.compressFile)
        except IOError:
            print 'Error - could not write file'
            raise
        filePath = unicode(f.name, sys.getfilesystemencoding())
        if self.encryptFile:
            key = filePath.encode(sys.getfilesystemencoding())
            password = TreeDoc.passwordDict.get(key, '')
            if not password:
                if key.endswith('~'):   # for auto-save filename
                    password = TreeDoc.passwordDict.get(key[:-1], '')
                if not password:
                    raise PasswordError, 'Missing password'
            text = encryptPrefix + p3.p3_encrypt(text, password)
        try:
            f.write(text)
        except IOError:
            print 'Error - could not write file', \
                  filePath.encode(globalref.localTextEncoding)
            raise
        f.close()
        if filePath.endswith('.gz'):
            self.compressFile = True
        if updateInfo:
            self.modified = False
            self.tlVersion = __version__
            self.fileName = filePath
            self.fileInfoFormat.updateFileInfo()

    def exportHtml(self, fileRef, item, includeRoot, openOnly=False,
                   indent=20, addHeader=False):
        """Save branch as html to file w/o columns"""
        outGroup = item.outputItemList(includeRoot, openOnly, True)
        self.exportHtmlColumns(fileRef, outGroup, 1, indent, addHeader)

    def exportHtmlColumns(self, fileRef, outGroup, numCol=1, indent=20,
                          addHeader=False):
        """Save contents of outGroup as html to file in columns"""
        try:
            f = self.getWriteFileObj(fileRef, False)
        except IOError:
            print 'Error - could not write file'
            raise
        filePath = unicode(f.name, sys.getfilesystemencoding())
        if self.lineBreaks:
            outGroup.addBreaks()
        outGroups = outGroup.splitColumns(numCol)
        for group in outGroups:
            group.addPrefix()
            group.addIndents()
        htmlTitle = os.path.splitext(os.path.basename(filePath))[0]
        lines = [u'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 '\
                 'Transitional//EN">', u'<html>', u'<head>',
                 u'<meta http-equiv="Content-Type" content="text/html; '\
                 'charset=utf-8">', u'<title>%s</title>' % htmlTitle,
                 u'<style type="text/css"><!--', u'div {margin-left: %dpx}'\
                 % indent, u'td {padding: 10px}',
                 u'tr {vertical-align: top}', u'--></style>',
                 u'</head>', u'<body>']
        if addHeader:
            header = self.fileInfoFormat.getHeaderFooter(True)
            if header:
                lines.append(header)
        lines.extend([u'<table>', u'<tr><td>'])
        for item in outGroups[0]:
            lines.extend(item.textLines)
        for group in outGroups[1:]:
            lines.append(u'</td><td>')
            for item in group:
                lines.extend(item.textLines)
        lines.extend([u'</td></tr>', u'</table>'])
        if addHeader:
            footer = self.fileInfoFormat.getHeaderFooter(False)
            if footer:
                lines.append(footer)
        lines.extend([u'</body>', u'</html>'])
        try:
            f.writelines([(line + '\n').encode('utf-8') for line in lines])
        except IOError:
            print 'Error - could not write file', \
                  filePath.encode(globalref.localTextEncoding)
            raise
        f.close()

    def exportDirTable(self, dirName, nodeList, addHeader=False):
        """Write tree to nested directory struct with html tables"""
        oldDir = os.getcwd()
        os.chdir(dirName.encode(sys.getfilesystemencoding()))
        if addHeader:
            header = self.fileInfoFormat.getHeaderFooter(True)
            footer = self.fileInfoFormat.getHeaderFooter(False)
        else:
            header = footer = ''
        if len(nodeList) > 1:
            self.treeFormats.addIfMissing(TreeDoc.copyFormat)
            item = TreeItem(None, TreeDoc.copyFormat.name)
            item.data[TreeFormats.fieldDefault] = TreeDoc.rootTitleDefault
            for child in nodeList:
                item.childList.append(child)
                child.parent = item
        else:
            item = nodeList[0]
        linkDict = {}
        item.createDirTableLinkDict(linkDict, os.getcwd())
        item.exportDirTable(linkDict, None, header, footer)
        self.treeFormats.removeQuiet(TreeDoc.copyFormat)
        os.chdir(oldDir)

    def exportDirPage(self, dirName, nodeList):
        """Write tree to nested direct struct with html page for each node"""
        oldDir = os.getcwd()
        os.chdir(dirName.encode(sys.getfilesystemencoding()))
        cssLines = ['#sidebar {', 'width: 16em;', 'float: left;',
                    'clear: left;', 'border-right: 1px solid black;',
                    'margin-right: 1em;', '}']
        try:
            f = codecs.open('default.css', 'w', 'utf-8')
            f.writelines([(line + '\n').encode('utf-8') for line in cssLines])
        except (IOError, UnicodeError):
            print 'Error - could not write file to default.css'
            raise IOError(_('Error - cannot write file to %s') % 'default.css')
        f.close()
        if len(nodeList) > 1:
            self.treeFormats.addIfMissing(TreeDoc.copyFormat)
            item = TreeItem(None, TreeDoc.copyFormat.name)
            item.data[TreeFormats.fieldDefault] = TreeDoc.rootTitleDefault
            for child in nodeList:
                item.childList.append(child)
                child.parent = item
        else:
            item = nodeList[0]
        linkDict = {}
        item.createDirPageLinkDict(linkDict, os.getcwd())
        item.exportDirPage(linkDict)
        self.treeFormats.removeQuiet(TreeDoc.copyFormat)
        os.chdir(oldDir)

    def exportXslt(self, fileRef, includeRoot, indent=20):
        """Write XSLT file and add link in treeline file"""
        try:
            f = self.getWriteFileObj(fileRef, False)
        except IOError:
            print 'Error - could not write file'
            raise
        filePath = unicode(f.name, sys.getfilesystemencoding())
        title = os.path.splitext(os.path.basename(filePath))[0]
        lines = [u'<xsl:stylesheet version="1.0" '\
                 u'xmlns:xsl="http://www.w3.org/1999/XSL/Transform">',
                 u"<xsl:output method='html'/>", u'<xsl:template match="/">',
                 u'<html>', u'<head>']
        if self.xslCssLink:
            lines.append('<link rel="stylesheet" href="%s" type="text/css"/>'
                         % self.xslCssLink)
        lines.extend([u'<title>%s</title>' % title, u'</head>', u'<body>',
                     u'<xsl:apply-templates/>', u'</body>', u'</html>',
                     u'</xsl:template>'])
        if not includeRoot:
            lines.extend([u'', u'<xsl:template match="/%s">'
                          % self.root.formatName,
                          u'<xsl:apply-templates/>', u'</xsl:template>'])
        for formatName in self.treeFormats:
            lines.extend(self.treeFormats[formatName].
                         xsltTemplate(indent, True))
        lines.extend([u'', u'<xsl:template match="*" />', u'',
                      u'</xsl:stylesheet>'])
        try:
            f.writelines([(line + '\n').encode('utf-8') for line in lines])
        except IOError:
            print 'Error - could not write file', \
                  filePath.encode(globalref.localTextEncoding)
            raise
        f.close()
        # find relative link path
        trlPath = os.path.abspath(self.fileName).split(os.sep)
        xslPath = os.path.abspath(filePath).split(os.sep)
        while trlPath[0] == xslPath[0]:
            del trlPath[0]
            del xslPath[0]
        xslPath = '/'.join(['..'] * (len(trlPath) - len(xslPath)) + xslPath)
        link = u'xml-stylesheet type="text/xsl" href="%s"' % xslPath
        if self.xlstLink != link:
            self.xlstLink = link
            self.modified = True

    def exportTrlSubtree(self, fileRef, nodeList, addBranches=True):
        """Write subtree TRL file starting form item"""
        lines = [u'<?xml version="1.0" encoding="utf-8" ?>']
        if self.xlstLink:
            lines.append(u'<?%s?>' % self.xlstLink)
        if not addBranches:
            newList = []
            for item in nodeList:  # replace items with childless items
                newItem = TreeItem(item.parent, item.formatName)
                newItem.data = item.data
                newList.append(newItem)
            nodeList = newList
        if len(nodeList) > 1:
            format = nodeformat.NodeFormat(TreeFormats.rootFormatDefault, {},
                                           TreeFormats.fieldDefault)
            self.treeFormats.addIfMissing(format)
            item = TreeItem(None, format.name)
            item.data[TreeFormats.fieldDefault] = TreeDoc.rootTitleDefault
            for child in nodeList:
                item.childList.append(child)
                child.parent = item
        else:
            item = nodeList[0]
        lines.extend(item.branchXml([], True))
        try:
            f = self.getWriteFileObj(fileRef, self.compressFile)
            f.writelines([(line + '\n').encode('utf-8') for line in lines])
        except IOError:
            print 'Error - could not write file'
            self.treeFormats.removeQuiet(TreeDoc.copyFormat)
            raise
        f.close()
        self.treeFormats.removeQuiet(TreeDoc.copyFormat)

    def exportTable(self, fileRef, nodeList, addBranches=True):
        """Write data to table for nodes or children of nodes"""
        if addBranches:
            newList = []
            for item in nodeList:
                newList.extend(item.childList)
            nodeList = newList
        typeList = []
        headings = []
        tableList = []
        for item in nodeList:
            itemFormat = item.nodeFormat()
            if itemFormat not in typeList:
                for field in itemFormat.fieldNames():
                    if field not in headings:
                        headings.append(field)
                typeList.append(itemFormat)
            tableList.append(u'\t'.join([item.data.get(head, '') for
                                        head in headings]))
        tableList.insert(0, u'\t'.join([head for head in headings]))
        try:
            text = os.linesep.join(tableList).\
                      encode(globalref.localTextEncoding, 'strict')
        except (ValueError, UnicodeError):
            print 'Warning - bad unicode characters were replaced'
            text = os.linesep.join(tableList).\
                      encode(globalref.localTextEncoding, 'replace')
        try:
            f = self.getWriteFileObj(fileRef, False)
            f.write(text)
        except IOError:
            print 'Error - could not write file'
            raise
        f.close()

    def exportTabbedTitles(self, fileRef, nodeList, addBranches=True,
                           includeRoot=True, openOnly=False):
        """Write tabbed titles for descendants of item"""
        if addBranches:
            initLevel = not includeRoot and -1 or 0
            titleList = []
            for item in nodeList:
                itemList = item.exportToText(initLevel, openOnly)
                if not includeRoot:
                    del itemList[0]
                titleList.extend(itemList)
        else:
            titleList = [item.title() for item in nodeList]
        try:
            text = os.linesep.join(titleList).\
                      encode(globalref.localTextEncoding, 'strict')
        except (ValueError, UnicodeError):
            print 'Warning - bad unicode characters were replaced'
            text = os.linesep.join(titleList).\
                      encode(globalref.localTextEncoding, 'replace')
        try:
            f = self.getWriteFileObj(fileRef, False)
            f.write(text)
        except IOError:
            print 'Error - could not write file'
            raise
        f.close()

    def exportXbel(self, fileRef, nodeList, addBranches=True):
        """Export XBEL bookmarks"""
        if len(nodeList) > 1 or not addBranches:
            title = TreeDoc.bookmarkRootTitle
            level = 1
        else:
            title = xml.sax.saxutils.escape(nodeList[0].title(), escDict)
            level = 0
        lines = [u'<!DOCTYPE xbel>', u'<xbel>', u'<title>%s</title>' % title]
        for item in nodeList:
            lines.extend(item.exportXbelBookmarks(level, addBranches))
        lines.append(u'</xbel>')
        try:
            f = self.getWriteFileObj(fileRef, False)
            f.writelines([(line + '\n').encode('utf-8') for line in lines])
        except IOError:
            print 'Error - could not write file'
            raise
        f.close()

    def exportHtmlBookmarks(self, fileRef, nodeList, addBranches=True):
        """Export HTML bookmarks"""
        if len(nodeList) > 1 or not addBranches:
            title = TreeDoc.bookmarkRootTitle
            level = 1
        else:
            title = xml.sax.saxutils.escape(nodeList[0].title())
            level = 0
        lines = [u'<!DOCTYPE NETSCAPE-Bookmark-file-1>',
                 u'<META HTTP-EQUIV="Content-Type" CONTENT="text/html; '\
                  'charset=UTF-8">', u'<TITLE>%s</TITLE>' % title,
                 u'<H1>%s</H1>' % title, '']
        for item in nodeList:
            lines.extend(item.exportHtmlBookmarks(level, addBranches))
        try:
            f = self.getWriteFileObj(fileRef, False)
            f.writelines([(line + '\n').encode('utf-8') for line in lines])
        except IOError:
            print 'Error - could not write file'
            raise
        f.close()

    def exportGenericXml(self, fileRef, nodeList, addBranches=True):
        """Export generic XML"""
        lines = [u'<?xml version="1.0" encoding="utf-8" ?>']
        level = 0
        if len(nodeList) > 1:
            lines.append(u'<%s>' % TreeFormats.rootFormatDefault)
            level = 1
        for item in nodeList:
            lines.extend(item.exportGenericXml(treexmlparse.GenericXmlHandler.
                                               textFieldName, level))
        if len(nodeList) > 1:
            lines.append(u'</%s>' % TreeFormats.rootFormatDefault)
        try:
            f = self.getWriteFileObj(fileRef, False)
            f.writelines([(line + '\n').encode('utf-8') for line in lines])
        except IOError:
            print 'Error - could not write file'
            raise
        f.close()

    def exportOdf(self, fileRef, nodeList, fontName, fontSize, fontFixed=False,
                  addBranches=True, includeRoot=True, openOnly=False):
        """Export an ODF format text file"""
        TreeItem.maxLevel = 0
        commonHeader = u'<?xml version="1.0" encoding="utf-8" ?>'
        commonAttr = u' office:version="1.0" '\
                      'xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:'\
                      'xsl-fo-compatible:1.0" '\
                      'xmlns:office="urn:oasis:names:tc:opendocument:'\
                      'xmlns:office:1.0" '\
                      'xmlns:style="urn:oasis:names:tc:opendocument:xmlns:'\
                      'style:1.0" '\
                      'xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:'\
                      'svg-compatible:1.0" '\
                      'xmlns:text="urn:oasis:names:tc:opendocument:'\
                      'xmlns:text:1.0">'
        pitch = fontFixed and 'fixed' or 'variable'
        sizeDelta = 2
        fontDecl = [u'<office:font-face-decls>',
                    u'<style:font-face style:font-pitch="%s" style:name="%s" '\
                     'svg:font-family="%s"/>' % (pitch, fontName, fontName),
                    u'</office:font-face-decls>']
        lines = [commonHeader, u'<office:document-content' + commonAttr]
        lines.extend(fontDecl)
        lines.extend([u'<office:body>', u'<office:text>'])
        for item in nodeList:
            lines.extend(item.exportOdf(1, addBranches, includeRoot, openOnly))
        lines.extend([u'</office:text>', u'</office:body>',
                      u'</office:document-content>'])
        manifest = [commonHeader,
                    u'<manifest:manifest xmlns:manifest="urn:oasis:names:tc:'\
                     'opendocument:xmlns:manifest:1.0">',
                    u'<manifest:file-entry manifest:media-type="application/'\
                     'vnd.oasis.opendocument.text" manifest:full-path="/"/>',
                    u'<manifest:file-entry manifest:media-type="text/xml" '\
                     'manifest:full-path="content.xml"/>',
                    u'<manifest:file-entry manifest:media-type="text/xml" '\
                     'manifest:full-path="styles.xml"/>',
                    u'</manifest:manifest>']
        styles = [commonHeader, u'<office:document-styles' + commonAttr]
        styles.extend(fontDecl)
        styles.extend([u'<office:styles>',
                       u'<style:default-style style:family="paragraph">',
                       u'<style:paragraph-properties '\
                        'style:writing-mode="page"/>',
                       u'<style:text-properties fo:font-size="%dpt" '\
                        'fo:hyphenate="false" style:font-name="%s"/>' %
                        (fontSize, fontName),
                       u'</style:default-style>',
                       u'<style:style style:name="Standard" '\
                        'style:class="text" style:family="paragraph"/>',
                       u'<style:style style:name="Text_20_body" '\
                        'style:display-name="Text body" style:class="text" '\
                        'style:family="paragraph" '\
                        'style:parent-style-name="Standard">',
                       u'<style:paragraph-properties '\
                        'fo:margin-bottom="6.0pt"/>',
                       u'</style:style>',
                       u'<style:style style:name="Heading" '\
                        'style:class="text" style:family="paragraph" '\
                        'style:next-style-name="Text_20_body" '\
                        'style:parent-style-name="Standard">',
                       u'<style:paragraph-properties '\
                        'fo:keep-with-next="always" fo:margin-bottom="6.0pt" '\
                        'fo:margin-top="12.0pt"/>',
                       u'<style:text-properties fo:font-size="%dpt" '\
                        'style:font-name="%s"/>' % (fontSize + sizeDelta,
                                                    fontName),
                       u'</style:style>'])
        outline = [u'<text:outline-style>']
        for level in range(1, TreeItem.maxLevel + 1):
            size = fontSize
            if level <= 2:
                size += 2 * sizeDelta
            elif level <=4:
                size += sizeDelta
            italic = ' '
            if level % 2 == 0:
                italic = 'fo:font-style="italic" '
            styles.extend([u'<style:style style:name="Heading_20_%d" '\
                            'style:display-name="Heading %d" '\
                            'style:class="text" style:family="paragraph" '\
                            'style:parent-style-name="Heading" '\
                            'style:default-outline-level="%d">' % \
                            (level, level, level),
                           u'<style:text-properties fo:font-size="%dpt" '\
                            '%s fo:font-weight="bold"/>' % \
                            (size, italic),
                           u'</style:style>'])
            outline.append(u'<text:outline-level-style text:level="%d" '\
                            'style:num-format=""/>' % level)
        styles.extend(outline)
        styles.extend([u'</text:outline-style>', u'</office:styles>',
                       u'<office:automatic-styles>',
                       u'<style:page-layout style:name="pm1">',
                       u'<style:page-layout-properties '\
                        'fo:margin-bottom="0.75in" fo:margin-left="0.75in" '\
                        'fo:margin-right="0.75in" fo:margin-top="0.75in" '\
                        'fo:page-height="11in" fo:page-width="8.5in" '\
                        'style:print-orientation="portrait"/>',
                       u'</style:page-layout>',
                       u'</office:automatic-styles>',
                       u'<office:master-styles>',
                       u'<style:master-page style:name="Standard" '\
                        'style:page-layout-name="pm1"/>',
                       u'</office:master-styles>',
                       u'</office:document-styles>'])
        try:
            f = zipfile.ZipFile(fileRef, 'w', zipfile.ZIP_DEFLATED)
            f.writestr('content.xml', u'\n'.join(lines).encode('utf-8') + '\n')
            f.writestr('META-INF/manifest.xml', u'\n'.join(manifest) + '\n')
            f.writestr('styles.xml', u'\n'.join(styles) + '\n')
        except IOError:
            print 'Error - could not write file'
            raise
        f.close()


class ReadFileError(Exception):
    """Exception class for errors on reading file content"""
    pass


class PasswordError(Exception):
    """Exception class for missing or invalid encryption passwords"""
    pass


def testXmlParser():
    """Return True if parser works correctly"""
    try:
        handler = xml.sax.ContentHandler()
        xml.sax.parseString('<XML>test</XML>', handler)
    except xml.sax.SAXException:
        return False
    return True

def splitPath(path):
    """Return a list of elements of path, ignores drive spec"""
    result = []
    path = os.path.splitdrive(path)[1]
    while True:
        path, tail = os.path.split(path)
        result.insert(0, tail)
        if path[-1:] in ('', '/', '\\'):
            return result

def relativePath(base, destination):
    """Return a path to destination relative to base,
       assumes paths are absolute"""
    if os.path.splitdrive(base)[0] != os.path.splitdrive(destination)[0]:
        return destination
    base = splitPath(base)
    destination = splitPath(destination)
    while base and destination and base[0] == destination[0]:
        base = base[1:]
        destination = destination[1:]
    prefix = '..%s' % os.sep * len(base)
    if prefix:
        destination.insert(0, prefix)
    if not destination:
        return ''
    return os.path.join(*destination)


if __name__ == '__main__':
    doc = TreeDoc()
    if len(sys.argv) > 1:
        doc.readFile(sys.argv[1])
    print '\n'.join(doc.root.exportToText())
    print
    print '\n'.join(doc.root.childList[0].formatChildText())
