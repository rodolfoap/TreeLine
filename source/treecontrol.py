#!/usr/bin/env python

#****************************************************************************
# treecontrol.py, provides a class for control of the main windows
#
# TreeLine, an information storage program
# Copyright (C) 2009, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#****************************************************************************

import sys
import os.path
from PyQt4 import QtCore, QtGui, QtNetwork
try:
    from __main__ import __version__, iconPath
except ImportError:
    __version__ = '??'
    iconPath = None
import globalref
import treedoc
import treemainwin
import treedialogs
import option
import optiondefaults
import icondict
import recentfiles


class TreeControl(object):
    """Program and main window control"""
    def __init__(self, userStyle):
        self.windowList = []
        globalref.treeControl = self
        self.serverSocket = None
        mainVersion = '.'.join(__version__.split('.')[:2])
        globalref.options = option.Option(u'treeline-%s' % mainVersion, 21)
        globalref.options.loadAll(optiondefaults.defaultOutput())
        iconPathList = [iconPath, os.path.join(globalref.modPath, u'icons/'),
                        os.path.join(globalref.modPath, u'../icons/')]
        if not iconPath:
            del iconPathList[0]
        globalref.treeIcons = icondict.IconDict()
        globalref.treeIcons.addIconPath([os.path.join(path, u'tree') for path
                                         in iconPathList])
        globalref.treeIcons.addIconPath([globalref.options.iconPath])
        treemainwin.TreeMainWin.toolIcons = icondict.IconDict()
        treemainwin.TreeMainWin.toolIcons.\
                    addIconPath([os.path.join(path, u'toolbar')
                                 for path in iconPathList],
                                [u'', u'32x32', u'16x16'])
        treemainwin.TreeMainWin.toolIcons.loadAllIcons()
        windowIcon = globalref.treeIcons.getIcon(u'treeline')
        if windowIcon:
            QtGui.QApplication.setWindowIcon(windowIcon)
        if not userStyle:
            if sys.platform.startswith('dar'):
                QtGui.QApplication.setStyle('macintosh')
            elif not sys.platform.startswith('win'):
                QtGui.QApplication.setStyle('plastique')
        self.recentFiles = recentfiles.RecentFileList()
        qApp = QtGui.QApplication.instance()
        qApp.connect(qApp, QtCore.SIGNAL('focusChanged(QWidget*, QWidget*)'),
                     self.updateFocus)

    def getSocket(self):
        """Open a socket from another TreeLine process, focus or open the
           applicable file"""
        socket = self.serverSocket.nextPendingConnection()
        if socket and socket.waitForReadyRead(1000):
            data = unicode(socket.readAll(), globalref.localTextEncoding)
            if data.startswith('[') and data.endswith(']'):
                fileNames = eval(data)
                if fileNames:
                    self.openMultipleFiles(fileNames)
                else:
                    globalref.mainWin.activateWindow()
                    globalref.mainWin.raise_()

    def firstWindow(self, fileNames):
        """Open first main window"""
        try:
            # check for existing TreeLine session
            socket = QtNetwork.QLocalSocket()
            socket.connectToServer('treeline-session',
                                   QtCore.QIODevice.WriteOnly)
            # if found, send files to open and exit TreeLine
            if socket.waitForConnected(1000):
                socket.write(repr(fileNames))
                if socket.waitForBytesWritten(1000):
                    socket.close()
                    sys.exit(0)
            qApp = QtGui.QApplication.instance()
            # start local server to listen for attempt to start new session
            self.serverSocket = QtNetwork.QLocalServer()
            self.serverSocket.listen('treeline-session')
            qApp.connect(self.serverSocket, QtCore.SIGNAL('newConnection()'),
                         self.getSocket)
        except AttributeError:
            print 'Warning:  Could not create local socket'
        if fileNames:
            fileNames = [unicode(fileName, globalref.localTextEncoding) for
                         fileName in fileNames]
            self.openMultipleFiles(fileNames)
        else:
            win = treemainwin.TreeMainWin()
            self.windowList.append(win)
            self.updateWinMenu()
            self.autoOpen()
            win.show()
        globalref.setStatusBar(_('Ready'), 2000)

    def openMultipleFiles(self, fileNames):
        """Open files in multiple windows if unique"""
        for fileName in fileNames:
            fileName = os.path.abspath(fileName)
            if self.matchingWindows(fileName):
                win = self.matchingWindows(fileName)[0]
                win.activateWindow()
                win.raise_()
            else:
                win = treemainwin.TreeMainWin()
                self.windowList.append(win)
                self.openFile(fileName, False)
                win.show()
            QtGui.QApplication.alert(win)

    def autoOpen(self):
        """Open last used file"""
        if globalref.options.boolData('AutoFileOpen') and \
                 self.recentFiles:
            path = self.recentFiles[0].path
            if path and not self.openFile(path, False, False):
                self.recentFiles.removeEntry(path)
        elif not self.recentFiles and \
                globalref.options.intData('RecentFiles', 0, 99):
            globalref.mainWin.show()
            # prompt for template if no recent files
            globalref.mainWin.fileNew(False)

    def recentOpen(self, filePath):
        """Open from recentFiles call"""
        if filePath and self.savePrompt():
            if not self.openFile(filePath):
                self.recentFiles.removeEntry(filePath)

    def openFile(self, filePath, newWinOk=True, importOnFail=True,
                 addToRecent=True):
        """Open given file, fail quietly if not importOnFail,
           return True on success or user cancel,
           return False on failure (to remove from recent files)"""
        if self.matchingWindows(filePath):
            win = self.matchingWindows(filePath)[0]
            win.activateWindow()
            win.raise_()
            return True
        oldWin = globalref.mainWin
        if newWinOk and globalref.options.boolData('OpenNewWindow') and \
                (globalref.docRef.fileName or globalref.docRef.modified):
            win = treemainwin.TreeMainWin()
        else:
            win = globalref.mainWin
        if not self.checkAutoSave(filePath):
            return True
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            win.doc = treedoc.TreeDoc(filePath)
            win.fileImported = False
        except treedoc.PasswordError:
            QtGui.QApplication.restoreOverrideCursor()
            dlg = treedialogs.PasswordEntry(False, win)
            if dlg.exec_() != QtGui.QDialog.Accepted:
                globalref.updateRefs(oldWin)
                return True
            win.doc.setPassword(filePath, dlg.password)
            result = self.openFile(filePath, False, importOnFail)
            if not dlg.saveIt:
                win.doc.clearPassword(filePath)
            return result
        except (IOError, UnicodeError):
            QtGui.QApplication.restoreOverrideCursor()
            QtGui.QMessageBox.warning(win, 'TreeLine',
                              _('Error - could not read file "%s"') % filePath)
            globalref.updateRefs(oldWin)
            return False
        except treedoc.ReadFileError, e:
            QtGui.QApplication.restoreOverrideCursor()
            if not importOnFail:
                globalref.updateRefs(oldWin)
                return True
            # assume file is not a TreeLine file
            importType = self.chooseImportType()
            if not importType:
                globalref.updateRefs(oldWin)
                return True
            try:
                QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                win.doc = treedoc.TreeDoc(filePath, False, importType)
            except treedoc.ReadFileError, e:
                QtGui.QApplication.restoreOverrideCursor()
                QtGui.QMessageBox.warning(win, 'TreeLine', _('Error - %s') % e)
                globalref.updateRefs(oldWin)
                return False
            win.fileImported = True
        win.doc.root.open = True
        QtGui.QApplication.restoreOverrideCursor()
        if win not in self.windowList:
            self.windowList.append(win)
        win.updateForFileChange(addToRecent)
        if win.pluginInterface:
            win.pluginInterface.execCallback(win.pluginInterface.
                                             fileOpenCallbacks)
        win.show()
        return True

    def chooseImportType(self):
        """Show dialog for selecting file import type"""
        choices = [(_('Tab &indented text, one node per line'),
                    treedoc.tabbedImport),
                    (_('Text &table with header row, one node per line'),
                     treedoc.tableImport),
                    (_('Plain text, one &node per line (CR delimitted)'),
                     treedoc.textLineImport),
                    (_('Plain text &paragraphs (blank line delimitted)'),
                     treedoc.textParaImport),
                    (_('Treepad &file (text nodes only)'),
                     treedoc.treepadImport),
                    (_('&XML bookmarks (XBEL format)'), treedoc.xbelImport),
                    (_('&HTML bookmarks (Mozilla format)'),
                     treedoc.mozillaImport),
                    (_('&Generic XML (Non-TreeLine file)'),
                     treedoc.xmlImport),
                    (_('Open Document (ODF) text'), treedoc.odfImport)]
        dlg = treedialogs.RadioChoiceDlg(_('Import Text'),
                                         _('Choose Text Import Method'),
                                         choices, globalref.mainWin)
        if dlg.exec_() != QtGui.QDialog.Accepted:
            return None
        return dlg.getResult()

    def newFile(self, templatePath='', newWinOk=True):
        """Open a new file"""
        if newWinOk and globalref.options.boolData('OpenNewWindow') and \
                (globalref.docRef.fileName or globalref.docRef.modified):
            win = treemainwin.TreeMainWin()
            self.windowList.append(win)
        else:
            win = globalref.mainWin
        if templatePath:
            try:
                win.doc = treedoc.TreeDoc(templatePath)
                win.doc.root.open = True
                win.doc.fileName = ''
                win.doc.fileInfoFormat.updateFileInfo()
            except (treedoc.PasswordError, IOError, UnicodeError,
                    treedoc.ReadFileError):
                QtGui.QMessageBox.warning(win, 'TreeLine',
                            _('Error - could not read template file "%s"') \
                            % templatePath)
                win.doc = treedoc.TreeDoc()
        else:
            win.doc = treedoc.TreeDoc()
        win.updateForFileChange(False)
        if win.pluginInterface:
            win.pluginInterface.execCallback(win.pluginInterface.
                                             fileNewCallbacks)
        win.show()

    def saveFile(self, fileName):
        """Save file to fileName, return True on success"""
        win = globalref.mainWin
        unsetPassword = False
        if win.doc.encryptFile and not win.doc.hasPassword(fileName):
            dlg = treedialogs.PasswordEntry(True, win)
            if dlg.exec_() != QtGui.QDialog.Accepted:
                return False
            win.doc.setPassword(fileName, dlg.password)
            unsetPassword = not dlg.saveIt
        try:
            win.doc.writeFile(fileName)
        except IOError:
            QtGui.QMessageBox.warning(win, 'TreeLine',
                                _('Error - Could not write to %s') % fileName)
            return False
        if unsetPassword:
            win.doc.clearPassword(fileName)
        win.updateCmdAvail()
        self.delAutoSaveFile()
        self.resetAutoSave()
        if win.pluginInterface:
            win.pluginInterface.execCallback(win.pluginInterface.
                                             fileSaveCallbacks)
        return True

    def resetAutoSave(self):
        """Restart auto save timer if the option is enabled"""
        globalref.mainWin.autoSaveTimer.stop()
        minutes = globalref.options.intData('AutoSaveMinutes', 0, 999)
        if minutes:
            globalref.mainWin.autoSaveTimer.start(60000 * minutes)

    def autoSave(self):
        """Perform auto save if the option is enabled (called from timer)"""
        win = globalref.mainWin
        if win.doc.modified and win.doc.fileName and not win.fileImported:
            unsetPassword = False
            if win.doc.encryptFile and \
                        not win.doc.hasPassword(win.doc.fileName):
                dlg = PasswordEntry(True, win)
                if dlg.exec_() != QtGui.QDialog.Accepted:
                    return
                win.doc.setPassword(win.doc.fileName, dlg.password)
                unsetPassword = not dlg.saveIt
            try:
                win.doc.writeFile(win.doc.fileName + '~', False)
            except IOError:
                pass
            if unsetPassword:
                win.doc.clearPassword(win.doc.fileName)

    def checkAutoSave(self, filePath):
        """Check for presence of auto save file & prompt user,
           return True if OK to continue"""
        if not globalref.options.intData('AutoSaveMinutes', 0, 999):
            return True
        autoSaveFile = self.autoSaveFilePath(filePath)
        if not  autoSaveFile:
            return True
        ans = QtGui.QMessageBox.information(self, 'TreeLine',
                                            _('Backup file "%s" exists.\n'\
                                              'A previous session may '\
                                              'have crashed.') % autoSaveFile,
                                            _('&Restore Backup'),
                                            _('&Delete Backup'),
                                            _('&Cancel File Open'), 0, 2)
        if ans == 0:
            if not self.restoreAutoSaveFile(filePath):
                QtGui.QMessageBox.warning(self, 'TreeLine',
                                          _('Error - could not restore '\
                                            'backup'))
            return False
        elif ans == 1:
            self.delAutoSaveFile(filePath)
            return True
        else:
            return False

    def autoSaveFilePath(self, baseName=''):
        """Return the path to a backup file if it exists"""
        filePath = baseName and baseName or globalref.docRef.fileName
        filePath = filePath + '~'
        if len(filePath) > 1 and \
                 os.access(filePath.encode(sys.getfilesystemencoding()),
                           os.R_OK):
            return filePath
        return ''

    def delAutoSaveFile(self, baseName=''):
        """Remove the backup auto save file if it exists"""
        filePath = self.autoSaveFilePath(baseName)
        if filePath:
            try:
                os.remove(filePath)
            except OSError:
                print 'Could not remove backup file %s' % \
                      filePath.encode(globalref.localTextEncoding)

    def restoreAutoSaveFile(self, baseName):
        """Open backup file, then move baseName~ to baseName by overwriting,
           return True on success"""
        fileName = baseName + '~'
        self.openFile(fileName, False, False, False)
        if globalref.docRef.fileName != fileName:
            return False
        try:
            os.remove(baseName)
        except OSError:
            print 'Could not remove file %s' % \
                  baseName.encode(globalref.localTextEncoding)
            return False
        try:
            os.rename(fileName, baseName)
        except OSError:
            print 'Could not rename file %s' % \
                  fileName.encode(globalref.localTextEncoding)
            return False
        globalref.docRef.fileName = baseName
        globalref.mainWin.setMainCaption()
        return True

    def savePrompt(self, closing=False):
        """Ask for save if doc modified, return false on cancel"""
        win = globalref.mainWin
        if not self.duplicateWindows():
            if win.doc.modified and (closing or not globalref.options.
                                     boolData('OpenNewWindow')):
                text = win.fileImported and _('Save changes?') or \
                       _('Save changes to "%s"?') % win.doc.fileName
                ans = QtGui.QMessageBox.information(win, 'TreeLine', text,
                                                    _('&Yes'), _('&No'),
                                                    _('&Cancel'), 0, 2)
                if ans == 0:
                    win.fileSave()
                elif ans == 1:
                    self.delAutoSaveFile()
                    return True
                else:
                    return False
            if globalref.options.boolData('PersistTreeState'):
                self.recentFiles.saveTreeState(win.treeView)
        return True

    def newWindow(self):
        """Create a new window viewing the current file"""
        globalref.mainWin.saveMultiWinTree()
        doc = globalref.mainWin.doc
        win = treemainwin.TreeMainWin()
        self.windowList.append(win)
        win.doc = doc
        win.updateForFileChange(False)
        win.show()

    def closeWindow(self):
        """Close the current window without exiting"""
        if self.windowCount() > 1:
            globalref.mainWin.close()
        elif self.savePrompt():
            self.newFile('', False)

    def duplicateWindows(self):
        """Return list of windows with the same file as the active window"""
        return [win for win in self.windowList if win != globalref.mainWin and
                win.doc.fileName == globalref.mainWin.doc.fileName]

    def matchingWindows(self, fileName):
        """Return list of windows with the given file name"""
        return [win for win in self.windowList if win.doc.fileName == fileName]

    def removeWin(self, win):
        """Remove given windoww from the window list"""
        self.windowList.remove(win)

    def windowCount(self):
        """Return the current number of windows"""
        return len(self.windowList)

    def updateWinMenu(self):
        """Update the window list menu in the active main window"""
        mainWin = globalref.mainWin
        for action in mainWin.winMenu.actions():
            if hasattr(action, 'refWin'):
                mainWin.winMenu.removeAction(action)
        num = 1
        for win in self.windowList:
            action = WindowAction(mainWin, win, num)
            mainWin.winMenu.addAction(action)
            if win is mainWin:
                action.setChecked(True)
            num += 1

    def updateDialogs(self):
        """Update non-modal dialogs in response to their close signal"""
        globalref.mainWin.updateNonModalDialogs()

    def updateFocus(self):
        """Check for focus change to a different main window"""
        win = QtGui.QApplication.activeWindow()
        while win and win.parent():
            win = win.parent()
        if win and win != globalref.mainWin and win in self.windowList:
            oldWin = globalref.mainWin
            if self.duplicateWindows():
                oldWin.saveMultiWinTree()
            globalref.updateRefs(win)
            self.recentFiles.updateMenu()
            self.updateWinMenu()
            if self.duplicateWindows():
                win.updateMultiWinTree()
            win.updateNonModalDialogs()

    def forceUpdateWindow(self):
        """Update an alternate window that shows the same file"""
        oldWin = globalref.mainWin
        oldWin.saveMultiWinTree()
        for win in self.duplicateWindows():
            globalref.updateRefs(win)
            win.updateMultiWinTree()
        globalref.updateRefs(oldWin)
        oldWin.updateMultiWinTree()


class WindowAction(QtGui.QAction):
    """Menu item for a window entry"""
    maxLength = 30
    def __init__(self, parent, refWin, num):
        QtGui.QAction.__init__(self, parent)
        self.refWin = refWin
        self.setText('&%d %s' % (num, self.abbrevPath()))
        self.setStatusTip(refWin.doc.fileName)
        self.setCheckable(True)
        self.connect(self, QtCore.SIGNAL('triggered()'), self.raiseWin)

    def abbrevPath(self):
        """Return shortened version of path"""
        abbrevPath = self.refWin.doc.fileName
        if len(abbrevPath) > WindowAction.maxLength:
            truncLength = WindowAction.maxLength - 3
            pos = abbrevPath.find(os.sep, len(abbrevPath) - truncLength)
            if pos < 0:
                pos = len(abbrevPath) - truncLength
            abbrevPath = '...' + abbrevPath[pos:]
        return abbrevPath

    def raiseWin(self):
        """Raise referenced window"""
        self.refWin.activateWindow()
        self.refWin.raise_()
