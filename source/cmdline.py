#!/usr/bin/env python

#****************************************************************************
# cmdline.py, provides a class to read and execute command line arguments
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import sys
import os.path
from PyQt4 import QtGui
import treedoc
import globalref

usage = [_('Usage:'),
         '',
         '   treeline [%s] [%s]' % (_('qt-options'), _('infile')),
         '',
         _('-or- (non-interactive):'),
         '',
         '   treeline [%s] [%s] [%s] %s [%s ...]' %
            (_('import-option'), _('export-option'), _('misc-options'),
             _('infile'), _('infile2')),
         '',
         _('Qt-options:'),
         '',
         '   %s' % _('see Qt documentation for valid Qt options'),
         '',
         _('Import-options:'),
         '',
         '   --import-tabbed     %s' %
            _('import a tab indented text file'),
         '   --import-table      %s' %
            _('import a tab-delimitted text table, one node per line'),
         '   --import-lines      %s' %
            _('import plain text, one node per line'),
         '   --import-para       %s' %
            _('import plain text, one node per paragraph'),
         '   --import-treepad    %s' %
            _('import a Treepad text-node file'),
         '   --import-xbel       %s' %
            _('import an XML bookmark file in XBEL format'),
         '   --import-mozilla    %s' %
            _('import an html bookmark file in Mozilla format'),
         '   --import-xml        %s' %
            _('import a generic XML file (non-TreeLine format)'),
         '   --import-odf        %s' %
            _('import an ODF text document'),
         '',
         _('Export-options:'),
         '',
         '   --export-html       %s' %
            _('export a single HTML file'),
         '   --export-dir        %s' %
            _('export HTML in directories'),
         '   --export-xslt       %s' %
            _('export an XSLT file'),
         '   --export-tabbed     %s' %
            _('export a tab indented text file'),
         '   --export-table      %s' %
            _('export a text table of the first children only'),
         '   --export-xbel       %s' %
            _('export an XML bookmark file in XBEL format'),
         '   --export-mozilla    %s' %
            _('export an html bookmark file in Mozilla format'),
         '   --export-xml        %s' %
            _('export a generic XML file (non-TreeLine format)'),
         '   --export-odf        %s' %
            _('export an ODF text document'),
         '',
         _('Misc-options:'),
         '',
         '   -o, --outfile=%-5s %s' %
            (_('FILE'),
             _('the output filename, not used with multiple infiles')),
         '   -n, --no-root       %s' %
            _('exclude the root node form the output if applicable'),
         '   --add-header        %s' %
            _('add a header and footer to HTML exports'),
         '   --indent=%-10s %s' %
            (_('NUM'),
             _('change the indent amount for HTML exports (default = 20)')),
         '   -q, --quiet         %s' %
            _('supress normal status information, only give errors'),
         '   -h, --help          %s' %
            _('display this information and exit'),
         '',
         _("No more than one import-option and one export-option may be\n"\
           "specified.  If either are not present, the native TreeLine\n"\
           "file format is assumed."),
         '',
         _("The output filename option can only be specified if there is\n"\
           "only one input file.  If it is not specified, the input's base\n"\
           "file name is used with the appropriate output file extension.\n"\
           "If the extensions are the same, an underscore is added before\n"\
           "the extension.  Note that this avoids overwriting the input\n"\
           "file, but other files may be overwritten without notification\n"\
           "if they share the output file's name.")]

class CmdLine(object):
    """Parses and executes command line arguments for file translations"""
    options = 'o:nqh'
    longOptions = ['import-tabbed', 'import-table', 'import-lines',
                   'import-para', 'import-treepad', 'import-xbel',
                   'import-mozilla', 'import-xml', 'import-odf',
                   'export-html', 'export-dir', 'export-xslt',
                   'export-tabbed', 'export-table', 'export-xbel',
                   'export-mozilla', 'export-xml', 'export-odf',
                   'outfile=', 'no-root', 'indent=', 'quiet', 'help']
    def __init__(self, opts, args):
        self.doc = None
        self.outfile = ''
        self.includeRoot = True
        self.addHeader = False
        self.indent = 20
        self.quiet = False
        importType = ''
        exportType = ''
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                printUsage()
                return
            elif opt.startswith('--import-'):
                if importType:
                    printUsage()
                    sys.exit(2)
                importType = opt[9:]
            elif opt.startswith('--export-'):
                if exportType:
                    printUsage()
                    sys.exit(2)
                exportType = opt[9:]
            elif opt in ('-o', '--outfile'):
                self.outfile = arg
                if len(args) > 1:
                    printUsage()
                    sys.exit(2)
            elif opt in ('-n', '--no-root'):
                self.includeRoot = False
            elif opt == '--add-header':
                self.addHeader = True
            elif opt == '--indent':
                try:
                    self.indent = int(arg)
                except ValueError:
                    printUsage()
                    sys.exit(2)
            elif opt in ('-q', '--quiet'):
                self.quiet = True
        if not args:
            printUsage()
            sys.exit(2)
        if not importType:
            importType = 'trl'
        if not exportType:
            exportType = 'trl'
        errorFlag = False
        pathEncoding = globalref.localTextEncoding
        for fileName in args:
            self.doc = treedoc.TreeDoc()
            try:
                self.importFile(fileName, importType)
            except (IOError, UnicodeError):
                print _('Error - could not read file %s', '%s is filename') % \
                      fileName.encode(pathEncoding)
                errorFlag = True
                continue
            except treedoc.ReadFileError, e:
                print _('Error in %(filename)s - %(details)s') % \
                      {'filename': fileName.encode(pathEncoding),
                       'details': e}
                errorFlag = True
                continue
            try:
                newFileName = self.exportFile(fileName, exportType)
                if not self.quiet:
                    print _('File "%(infile)s" (%(intype)s type) was exported'\
                            ' to "%(outfile)s" (%(outtype)s type)') \
                       % {'infile': fileName.encode(pathEncoding),
                          'intype': importType,
                          'outfile': newFileName.encode(pathEncoding),
                          'outtype': exportType}
            except IOError:
                errorFlag = True
        if errorFlag:
            sys.exit(1)

    def importFile(self, fileName, importType):
        """Import file using importType"""
        if importType == 'trl':
            importType = 'File'
        getattr(self.doc, 'read%s' % importType.title())(fileName)

    def exportFile(self, oldFileName, exportType):
        """Export file using exportType, return new filename on success"""
        if exportType == 'trl':
            fileName = self.newFileName(oldFileName, '.trl')
            self.doc.writeFile(fileName)
        elif exportType == 'html':
            fileName = self.newFileName(oldFileName, '.html')
            self.doc.exportHtml(fileName, self.doc.root, self.includeRoot,
                                False, self.indent, self.addHeader)
        elif exportType == 'dir':
            dirName = os.path.split(oldFileName)[0]
            if not dirName:
                dirName = '.'
            fileName = dirName
            self.doc.exportDir(dirName, [self.doc.root], self.addHeader)
        elif exportType == 'xslt':
            fileName = self.newFileName(oldFileName, '.xsl')
            self.doc.exportXslt(fileName, self.includeRoot, self.indent)
        elif exportType == 'tabbed':
            fileName = self.newFileName(oldFileName, '.txt')
            self.doc.exportTabbedTitles(fileName, [self.doc.root], True,
                                        self.includeRoot)
        elif exportType == 'table':
            fileName = self.newFileName(oldFileName, '.tbl')
            self.doc.exportTable(fileName, [self.doc.root])
        elif exportType == 'xbel':
            fileName = self.newFileName(oldFileName, '.xml')
            self.doc.exportXbel(fileName, [self.doc.root])
        elif exportType == 'mozilla':
            fileName = self.newFileName(oldFileName, '.html')
            self.doc.exportHtmlBookmarks(fileName, [self.doc.root])
        elif exportType == 'xml':
            fileName = self.newFileName(oldFileName, '.xml')
            self.doc.exportGenericXml(fileName, [self.doc.root])
        elif exportType == 'odf':
            fileName = self.newFileName(oldFileName, '.odt')
            fontInfo = QtGui.QFontInfo(QtGui.QApplication.font())
            self.doc.exportOdf(fileName, [self.doc.root], fontInfo.family(),
                               fontInfo.pointSize(), fontInfo.fixedPitch(), 
                               True, self.includeRoot)
        return fileName

    def newFileName(self, oldFileName, newExt):
        """Return a new filename with a new extension, add an underscore to
           base name if the names are the same"""
        if self.outfile:
            return self.outfile
        baseName, oldExt = os.path.splitext(oldFileName)
        if oldExt == newExt:
            baseName += '_'
        return baseName + newExt


def printUsage():
    """Print usage text"""
    print u'\n'.join(usage).encode(globalref.localTextEncoding)
