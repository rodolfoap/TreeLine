#!/usr/bin/env python

"""
****************************************************************************
 treeline.py, the main program file

 TreeLine, an information storage program
 Copyright (C) 2011, Douglas W. Bell

 This is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License, either Version 2 or any later
 version.  This program is distributed in the hope that it will be useful,
 but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
*****************************************************************************
"""

__progname__ = 'TreeLine'
__version__ = '1.4.1'
__author__ = 'Doug Bell'

helpFilePath = None    # modified by install script if required
iconPath = None        # modified by install script if required
templatePath = None    # modified by install script if required
translationPath = 'translations'


import sys
import signal
import getopt
import os.path
import locale
import __builtin__
from PyQt4 import QtCore, QtGui
import globalref


def setModulePath():
    """Set module path in globalref"""
    globalref.modPath = unicode(os.path.abspath(sys.path[0]),
                                sys.getfilesystemencoding())
    if globalref.modPath.endswith('.zip'):  # for py2exe
        globalref.modPath = os.path.dirname(globalref.modPath)

def loadTranslator(fileName, app):
    """Load and install qt translator, return True if sucessful"""
    translator = QtCore.QTranslator(app)
    path = os.path.join(globalref.modPath, translationPath)
    result = translator.load(fileName, path)
    if not result:
        path = os.path.join(globalref.modPath, '..', translationPath)
        result = translator.load(fileName, path)
    if not result:
        path = os.path.join(globalref.modPath, '..', 'i18n', translationPath)
        result = translator.load(fileName, path)
    if result:
        QtCore.QCoreApplication.installTranslator(translator)
        return True
    else:
        print 'Warning: translation file "%s" could not be loaded' % fileName
        return False

def setupTranslator(app):
    """Set language, load translators and setup translator function"""
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        pass
    globalref.lang = os.environ.get('LC_MESSAGES', '')
    if not globalref.lang:
        globalref.lang = os.environ.get('LANG', '')
        if not globalref.lang:
            try:
                globalref.lang = locale.getdefaultlocale()[0]
            except ValueError:
                pass
            if not globalref.lang:
                globalref.lang = ''
    numTranslators = 0
    if globalref.lang and globalref.lang[:2] not in ['C', 'en']:
        numTranslators += loadTranslator('qt_%s' % globalref.lang, app)
        numTranslators += loadTranslator('treeline_%s' % globalref.lang, app)

    def translate(text, comment=''):
        """Translation function that sets context to calling module's
           filename"""
        try:
            frame = sys._getframe(1)
            fileName = frame.f_code.co_filename
        finally:
            del frame
        context = os.path.basename(os.path.splitext(fileName)[0])
        return unicode(QtCore.QCoreApplication.translate(context, text,
                                                         comment))

    def markNoTranslate(text, comment=''):
        return text

    if numTranslators:
        __builtin__._ = translate
    else:
        __builtin__._ = markNoTranslate
    __builtin__.N_ = markNoTranslate

def setLocalEncoding():
    """Store locale's default text encoding in globalref.localTextEncoding"""
    try:
        # not reliable?
        globalref.localTextEncoding = locale.getpreferredencoding()
        'test'.encode(globalref.localTextEncoding)
    except (AttributeError, LookupError, TypeError, locale.Error):
        try:
            # not available on windows
            globalref.localTextEncoding = locale.nl_langinfo(locale.CODESET)
            'test'.encode(globalref.localTextEncoding)
        except (AttributeError, LookupError, TypeError, locale.Error):
            try:
                globalref.localTextEncoding = locale.getdefaultlocale()[1]
                'test'.encode(globalref.localTextEncoding)
            except (AttributeError, LookupError, TypeError, locale.Error):
                globalref.localTextEncoding = 'utf-8'


def main():
    userStyle = '-style' in ' '.join(sys.argv)
    app = QtGui.QApplication(sys.argv)
    setModulePath()
    setupTranslator(app)  # must be before importing any treeline modules
    setLocalEncoding()

    import treedoc
    from cmdline import CmdLine
    import treecontrol
    import treemainwin

    if not treedoc.testXmlParser():
        QtGui.QMessageBox.critical(None, _('Error'),
                                   _('Error loading XML Parser\n'\
                                     'See TreeLine ReadMe file'), 1, 0)
        sys.exit(3)
    try:
        opts, args = getopt.gnu_getopt(sys.argv, CmdLine.options,
                                       CmdLine.longOptions)
    except getopt.GetoptError:
        import cmdline
        cmdline.printUsage()
        sys.exit(2)
    args = args[1:]

    treeControl = treecontrol.TreeControl(userStyle)

    if opts:
        CmdLine(opts, args)
    else:
        treeControl.firstWindow(args)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        app.exec_()


if __name__ == '__main__':
    main()
