#!/usr/bin/env python

#****************************************************************************
# treemainwin.py, provides a class for the main window
#
# TreeLine, an information storage program
# Copyright (C) 2009, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import sys
import os.path
import base64
from PyQt4 import QtCore, QtGui
try:
    from __main__ import __version__, __author__, helpFilePath
except ImportError:
    __version__ = __author__ = '??'
    helpFilePath = None
import treedoc
import treeview
import treeflatview
import treerightviews
import treeeditviews
import configdialog
import treedialogs
import printdata
import globalref
import optiondefaults
import optiondlg
import output
import helpview
import spellcheck
import plugininterface


class TreeMainWin(QtGui.QMainWindow):
    """Main window, menus, toolbar, and status"""
    toolIcons = None
    configDlg = None
    setTypeDlg = None
    sortDlg = None
    findDlg = None
    helpView = None
    tlPlainFileFilter = u'%s (*.trl *.xml)' % _('TreeLine Files - Plain')
    tlCompFileFilter = u'%s (*.trl *.trl.gz)' % \
                       _('TreeLine Files - Compressed')
    tlEncryptFileFilter = u'%s (*.trl)' % _('TreeLine Files - Encrypted')
    tlGenFileFilter = u'%s (*.trl *.xml *.trl.gz)' % _('TreeLine Files')
    allFileFilter = u'%s (*)' % _('All Files')
    textFileFilter = u'%s (*.txt)' % _('Text Files')
    treepadFileFilter = u'%s (*.hjt)' % _('Treepad Files')
    xbelFileFilter = u'%s (*.xml)' % _('XBEL Bookmarks')
    mozFileFilter = u'%s (*.html *.htm)' % _('Mozilla Bookmarks')
    htmlFileFilter = u'%s (*.html *.htm)' % _('Html Files')
    xsltFileFilter = u'%s (*.xsl *.xslt)' % _('XSLT Files')
    tableFileFilter = u'%s (*.tbl *.txt)' % _('Table Files')
    xmlFileFilter = u'%s (*.xml)' % _('XML Files')
    odfFileFilter = u'%s (*.odt)' % _('ODF Text Files')
    tagMenuEntries = [('TextAddBoldTag', _('&Bold'), ('<b>', '</b>')),
                      ('TextAddItalicsTag', _('&Italics'), ('<i>', '</i>')),
                      ('TextAddUnderlineTag', _('&Underline'),
                       ('<u>', '</u>')),
                      ('TextAddSizeTag', _('&Size...'),
                       ('<font size="%s">', '</font>')),
                      ('TextAddColorTag', _('&Color...'),
                       ('<font color="%s">', '</font>'))]
    tagDict = dict([(text, tag) for name, text, tag in tagMenuEntries])
    defaultWinSize = (640, 500)
    winCascade = 24

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setStatusBar(QtGui.QStatusBar())
        self.showStatusBar = globalref.options.boolData('ShowStatusBar')
        self.viewStatusBar(self.showStatusBar)
        globalref.mainWin = self
        if globalref.options.boolData('SaveWindowGeom'):
            if globalref.treeControl.windowCount():
                rect = globalref.treeControl.windowList[-1].geometry()
                rect.adjust(TreeMainWin.winCascade, TreeMainWin.winCascade,
                            TreeMainWin.winCascade, TreeMainWin.winCascade)
            else:
                rect = QtCore.QRect(globalref.options.intData('WindowXPos',
                                                              -1000, 10000),
                                    globalref.options.intData('WindowYPos',
                                                              -1000, 10000),
                                    globalref.options.intData('WindowXSize',
                                                              10, 10000),
                                    globalref.options.intData('WindowYSize',
                                                              10, 10000))
            if rect.x() != -1000 or rect.y() != -1000:
                desktop = QtGui.QApplication.desktop()
                if desktop.isVirtualDesktop():
                    availRect = desktop.screen().rect()
                else:
                    availRect = desktop.availableGeometry(desktop.
                                                          primaryScreen())
                winRect = rect.intersected(availRect)
                self.setGeometry(winRect)
            else:
                self.resize(rect.size())
        else:
            self.resize(*TreeMainWin.defaultWinSize)
        self.origPalette = QtGui.QApplication.palette()
        self.updateColors()
        self.autoSaveTimer = QtCore.QTimer(self)
        self.connect(self.autoSaveTimer, QtCore.SIGNAL('timeout()'),
                     globalref.treeControl.autoSave)

        split = QtGui.QSplitter()
        self.setCentralWidget(split)
        self.leftTabs = QtGui.QTabWidget()
        self.leftTabs.tabBar().setFocusPolicy(QtCore.Qt.NoFocus)
        split.addWidget(self.leftTabs)
        self.leftTabs.setTabPosition(QtGui.QTabWidget.South)

        self.treeView = treeview.TreeView()
        self.leftTabs.addTab(self.treeView, _('Tree View'))
        self.flatView = treeflatview.FlatView()
        self.leftTabs.addTab(self.flatView, _('Flat View'))

        self.rightTabs = QtGui.QTabWidget()
        self.rightTabs.tabBar().setFocusPolicy(QtCore.Qt.NoFocus)
        split.addWidget(self.rightTabs)
        self.rightTabs.setTabPosition(QtGui.QTabWidget.South)

        self.dataOutSplit = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.rightTabs.addTab(self.dataOutSplit, _('Data Output'))
        parentOutView = treerightviews.DataOutView(False)
        self.dataOutSplit.addWidget(parentOutView)
        childOutView = treerightviews.DataOutView(True)
        self.dataOutSplit.addWidget(childOutView)

        self.dataEditSplit = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.rightTabs.addTab(self.dataEditSplit, _('Data Editor'))
        parentEditView = treeeditviews.DataEditView(False)
        self.dataEditSplit.addWidget(parentEditView)
        childEditView = treeeditviews.DataEditView(True)
        self.dataEditSplit.addWidget(childEditView)

        self.titleListSplit = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.rightTabs.addTab(self.titleListSplit, _('Title List'))
        parentTitleView = treerightviews.TitleListView(False)
        self.titleListSplit.addWidget(parentTitleView)
        childTitleView = treerightviews.TitleListView(True)
        self.titleListSplit.addWidget(childTitleView)

        self.showItemChildren = globalref.options.boolData('StartShowChildren')
        childOutView.showDescendants = globalref.options.\
                                       boolData('StartShowDescend')

        treeFont = self.getFontFromOptions('Tree')
        if treeFont:
            self.treeView.setFont(treeFont)
            self.flatView.setFont(treeFont)
        outFont = self.getFontFromOptions('Output')
        if outFont:
            parentOutView.setFont(outFont)
            childOutView.setFont(outFont)
        editFont = self.getFontFromOptions('Editor')
        if editFont:
            parentEditView.setFont(editFont)
            childEditView.setFont(editFont)
            parentTitleView.setFont(editFont)
            childTitleView.setFont(editFont)

        if globalref.options.boolData('SaveWindowGeom'):
            mainSplitPercent = globalref.options.intData('TreeSplitPercent', 0,
                                                         100)
            treeWidth = int(split.width() / 100.0 * mainSplitPercent)
            split.setSizes([treeWidth, split.width() - treeWidth])
            outSplitPercent = globalref.options.intData('OutputSplitPercent',
                                                        0, 100)
            outHeight = int(self.dataOutSplit.height() / 100.0 *
                            outSplitPercent)
            self.dataOutSplit.setSizes([outHeight,
                                        self.dataOutSplit.height() -
                                        outHeight])
            editSplitPercent = globalref.options.intData('EditorSplitPercent',
                                                         0, 100)
            editHeight = int(self.dataEditSplit.height() / 100.0 *
                             editSplitPercent)
            self.dataEditSplit.setSizes([editHeight,
                                         self.dataEditSplit.height() -
                                         editHeight])
            titleSplitPercent = globalref.options.intData('TitleSplitPercent',
                                                          0, 100)
            titleHeight = int(self.titleListSplit.height() / 100.0 *
                              titleSplitPercent)
            self.titleListSplit.setSizes([titleHeight,
                                          self.titleListSplit.height() -
                                          titleHeight])
        else:
            childTitleView.oldViewHeight = 80

        self.doc = None
        self.pluginInterface = None
        self.condFilter = None
        self.textFilter = []
        self.fileImported = False
        self.duplicateSelect = None
        self.storedOpenNodes = []
        self.linkTagEditor = None
        self.printData = printdata.PrintData()

        self.actions = {}
        self.shortcuts = {}
        self.toolbars = []
        self.recentFileSep = None
        self.winMenu = None
        self.setupMenus()
        self.recentFileActions = []
        globalref.treeControl.recentFiles.updateMenu()
        self.setupShortcuts()
        self.addActionIcons()
        self.setupToolbars()
        self.restoreToolbarPos()
        self.filterStatus = QtGui.QLabel()
        self.doc = treedoc.TreeDoc()
        self.show()  # show window outline early and fix data edit view resizing
        self.updateForFileChange(False)

        self.connect(self.leftTabs, QtCore.SIGNAL('currentChanged(int)'),
                     self.updateLeftView)
        self.connect(self.rightTabs, QtCore.SIGNAL('currentChanged(int)'),
                     self.updateRightView)
        self.connect(QtGui.QApplication.clipboard(),
                     QtCore.SIGNAL('dataChanged()'), self.setPasteAvail)
        self.setPasteAvail()
        if globalref.options.boolData('SaveWindowGeom'):
            viewNum = globalref.options.intData('ActiveRightView', 0, 2)
            self.rightTabs.setCurrentIndex(viewNum)
        self.setupPlugins()
        self.updateAddTagAvail()

    def getFontFromOptions(self, optionPrefix):
        """Return font if set in options or None"""
        fontName = globalref.options.strData('%sFont' % optionPrefix, True)
        if fontName:
            try:
                fontSize = int(globalref.options.strData('%sFontSize' %
                                                         optionPrefix, True))
            except ValueError:
                fontSize = 10
            font = QtGui.QFont(fontName, fontSize)
            font.setBold(globalref.options.boolData('%sFontBold' %
                                                    optionPrefix))
            font.setItalic(globalref.options.boolData('%sFontItalic' %
                                                      optionPrefix))
            font.setUnderline(globalref.options.boolData('%sFontUnderline' %
                                                         optionPrefix))
            font.setStrikeOut(globalref.options.boolData('%sFontStrikeOut' %
                                                         optionPrefix))
            return font
        return None

    def saveFontToOptions(self, font, optionPrefix):
        """Store font in option settings"""
        globalref.options.changeData('%sFont' % optionPrefix,
                                     unicode(font.family()), True)
        globalref.options.changeData('%sFontSize' % optionPrefix,
                                     unicode(font.pointSize()), True)
        globalref.options.changeData('%sFontBold' % optionPrefix,
                                     font.bold() and 'yes' or 'no', True)
        globalref.options.changeData('%sFontItalic' % optionPrefix,
                                     font.italic() and 'yes' or 'no', True)
        globalref.options.changeData('%sFontUnderline' % optionPrefix,
                                     font.underline() and 'yes' or 'no', True)
        globalref.options.changeData('%sFontStrikeOut' % optionPrefix,
                                     font.strikeOut() and 'yes' or 'no', True)
        globalref.options.writeChanges()

    def updateViews(self):
        """Update left and right views"""
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.updateLeftView()
        QtGui.QApplication.restoreOverrideCursor()
        self.updateRightView()

    def updateLeftView(self, switchFlat=False):
        """Update the active left view, switchFlat is true if switching
           to the flat view"""
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        current = self.leftTabs.currentWidget()
        filters = []
        if current == self.treeView:
            self.doc.selection.openSelection()
            self.actions['ViewTree'].setChecked(True)
            self.treeView.updateTree()
        else:
            self.actions['ViewFlat'].setChecked(True)
            self.flatView.updateTree(switchFlat)
            if self.condFilter:
                filters.append(_('Conditional Filter'))
            if self.textFilter:
                filters.append(_('Text Filter'))
        if filters:
            self.filterStatus.setText((u' %s ' % _('and')).join(filters))
            self.statusBar().addWidget(self.filterStatus)
            self.filterStatus.show()
            self.statusBar().show()
        elif self.filterStatus.isVisible():
            self.statusBar().removeWidget(self.filterStatus)
            if not self.showStatusBar:
                self.statusBar().hide()
        QtGui.QApplication.restoreOverrideCursor()

    def updateViewSelection(self):
        """Change the selection in the active left view"""
        self.leftTabs.currentWidget().updateSelect()
        self.updateRightView()

    def updateViewItem(self, item):
        """Update item display in the active left view"""
        self.leftTabs.currentWidget().updateTreeItem(item)

    def updateRightView(self):
        """Update given right-hand view or the active one"""
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        splitter = self.rightTabs.currentWidget()
        if splitter == self.dataOutSplit:
            self.actions['ViewDataOutput'].setChecked(True)
        elif splitter == self.dataEditSplit:
            self.actions['ViewDataEdit'].setChecked(True)
        else:
            self.actions['ViewTitleList'].setChecked(True)
        if splitter.width():   # not collapsed
            childView = splitter.widget(1)
            topView = splitter.widget(0)
            if len(self.doc.selection) != 1 or not self.showItemChildren or \
                    (not self.doc.selection[0].childList and
                     childView.__class__ != treerightviews.TitleListView):
                if childView.height():
                    childView.oldViewHeight = int(childView.height() * 100.0 /
                                                  (topView.height() +
                                                   childView.height()))
                    splitter.setSizes([100, 0])
            elif childView.oldViewHeight:
                childHeight = int(splitter.height() / 100.0 *
                                  childView.oldViewHeight)
                splitter.setSizes([splitter.height() - childHeight,
                                   childHeight])
                childView.oldViewHeight = 0
            for index in range(2):
                if splitter.widget(index).height():    # not collapsed
                    splitter.widget(index).setEnabled(True)
                    splitter.widget(index).updateView()
                else:
                    splitter.widget(index).setEnabled(False)
        if TreeMainWin.setTypeDlg and TreeMainWin.setTypeDlg.isVisible():
            # could be updateDlg(), except needed after ConfigDialog apply
            TreeMainWin.setTypeDlg.loadList()
        self.updateCmdAvail()
        if TreeMainWin.sortDlg and TreeMainWin.sortDlg.isVisible():
            TreeMainWin.sortDlg.updateDialog()
        QtGui.QApplication.restoreOverrideCursor()

    def saveMultiWinTree(self):
        """Save tree select and open nodes when multiple windows show
           the same file"""
        self.duplicateSelect = self.doc.selection[:]
        self.storedOpenNodes = [node for node in self.doc.root.descendantList()
                                if node.open]

    def updateMultiWinTree(self):
        """Update the tree and restore tree select and open nodes when
           multiple windows show the same file"""
        if self.duplicateSelect:
            self.doc.selection = self.duplicateSelect
        for node in self.doc.root.descendantGen():
            node.open = False
        for node in self.storedOpenNodes:
            node.open = True
        self.updateViews()

    def updateCmdAvail(self):
        """Update the enabled status of menus"""
        notRoot = len(self.doc.selection) and \
                  self.doc.root not in self.doc.selection
        hasPrevSib = len(self.doc.selection) and None not in \
                     [node.prevSibling() for node in self.doc.selection]
        hasNextSib = len(self.doc.selection) and None not in \
                     [node.nextSibling() for node in self.doc.selection]
        selectParents = [node.parent for node in self.doc.selection]
        numChildren = [len(node.childList) for node in self.doc.selection]

        self.selectReqdActGrp.setEnabled(len(self.doc.selection))
        self.notRootActGrp.setEnabled(notRoot)
        self.selParentsActGrp.setEnabled(len(filter(None, numChildren)))

        self.actions['FileSave'].setEnabled(self.doc.modified)
        self.actions['EditUndo'].setEnabled(len(self.doc.undoStore.undoList))
        self.actions['EditRedo'].setEnabled(len(self.doc.redoStore.undoList))
        self.actions['EditRename'].setEnabled(len(self.doc.selection) == 1)
        self.actions['EditIndent'].setEnabled(hasPrevSib)
        self.actions['EditUnindent'].setEnabled(notRoot and
                                                self.doc.root not in
                                                selectParents)
        self.actions['EditMoveUp'].setEnabled(hasPrevSib)
        self.actions['EditMoveDown'].setEnabled(hasNextSib)
        self.actions['EditMoveFirst'].setEnabled(hasPrevSib)
        self.actions['EditMoveLast'].setEnabled(hasNextSib)
        self.actions['ViewPreviousSelect'].setEnabled(len(self.doc.selection.
                                                          prevSelects))
        self.actions['ViewNextSelect'].setEnabled(len(self.doc.selection.
                                                      nextSelects))
        self.actions['DataFilterClear'].setEnabled(self.condFilter != None or
                                                   len(self.textFilter))
        self.actions['ToolsRemXLST'].setEnabled(len(self.doc.xlstLink))
        self.actions['WinUpdateWindow'].setEnabled(len(globalref.treeControl.
                                                       duplicateWindows()))
        self.statusBar().clearMessage()
        if self.pluginInterface:
            self.pluginInterface.execCallback(self.pluginInterface.
                                                   viewUpdateCallbacks)

    def updateForFileChange(self, addToRecent=True):
        """Update GUI after file new or open"""
        globalref.updateRefs(self)
        self.setMainCaption()
        if self.leftTabs.currentWidget() == self.flatView:
            self.leftTabs.setCurrentWidget(self.treeView)
        if addToRecent:
            globalref.treeControl.recentFiles.addEntry(self.doc.fileName)
        if addToRecent and globalref.options.boolData('PersistTreeState'):
            if not globalref.treeControl.recentFiles.\
                    restoreTreeState(self.treeView):
                self.updateViews()
        else:
            self.updateViews()
        self.updateNonModalDialogs()
        globalref.treeControl.updateWinMenu()
        self.updateCmdAvail()
        globalref.treeControl.resetAutoSave()

    def updateNonModalDialogs(self):
        """Update any open non-modal dialogs and their toggle actions"""
        if TreeMainWin.configDlg and TreeMainWin.configDlg.isVisible():
            TreeMainWin.configDlg.resetParam(True)
            self.actions['DataConfigType'].setChecked(True)
        else:
            TreeMainWin.configDlg = None
            self.actions['DataConfigType'].setChecked(False)
        if TreeMainWin.setTypeDlg and TreeMainWin.setTypeDlg.isVisible():
            TreeMainWin.setTypeDlg.loadList()
            self.actions['DataSetDescendType'].setChecked(True)
        else:
            TreeMainWin.setTypeDlg = None
            self.actions['DataSetDescendType'].setChecked(False)
        if TreeMainWin.sortDlg and TreeMainWin.sortDlg.isVisible():
            TreeMainWin.sortDlg.updateDialog()
            self.actions['DataSort'].setChecked(True)
        else:
            TreeMainWin.sortDlg = None
            self.actions['DataSort'].setChecked(False)
        self.actions['ToolsFind'].setChecked(bool(TreeMainWin.findDlg and \
                                             TreeMainWin.findDlg.isVisible()))

    def updateAddTagAvail(self):
        """Update enabled status of editor tag entry commands"""
        self.addTagGroup.setEnabled(self.focusWidgetWithAttr('addHtmlTag') !=
                                    None)

    def setPasteAvail(self):
        """Check to see if text is available to paste"""
        text = self.clipText()
        self.actions['EditPaste'].setEnabled(len(text))
        self.actions['EditPasteText'].setEnabled(len(text))

    def clipText(self):
        """Return text from the clipboard"""
        try:
            # QString argument is work-around for bug in PyQt 4.6
            text = unicode(QtGui.QApplication.clipboard().\
                    text(QtCore.QString('xml')))
            if not text:
                text = unicode(QtGui.QApplication.clipboard().text())
        except UnicodeError:
            text = ''
        return text

    def updateColors(self):
        """Adjust the colors to the current option settings"""
        if globalref.options.boolData('UseDefaultColors'):
            pal = self.origPalette
        else:
            pal = QtGui.QPalette()
            pal.setColor(QtGui.QPalette.Base,
                         self.getOptionColor('Background'))
            pal.setColor(QtGui.QPalette.Text,
                         self.getOptionColor('Foreground'))
        QtGui.QApplication.setPalette(pal)

    def getOptionColor(self, name):
        """Return a color from option storage"""
        return QtGui.QColor(globalref.options.intData('%sR' % name, 0, 255),
                            globalref.options.intData('%sG' % name, 0, 255),
                            globalref.options.intData('%sB' % name, 0, 255))

    def setOptionColor(self, name, color):
        """Store given color in options"""
        globalref.options.changeData('%sR' % name, str(color.red()), True)
        globalref.options.changeData('%sG' % name, str(color.green()), True)
        globalref.options.changeData('%sB' % name, str(color.blue()), True)

    def focusWidgetWithAttr(self, attr):
        """Return the focused widget or it's ancestor
           that has the given attr or None"""
        widget = QtGui.QApplication.focusWidget()
        while widget and not hasattr(widget, attr):
            widget = widget.parent()
        return widget

    def setupPlugins(self):
        """Load plugin modules"""
        self.pluginInterface = plugininterface.PluginInterface(self)
        pluginPaths = [os.path.join(globalref.modPath, 'plugins')]
        userPluginPath = globalref.options.pluginPath
        if userPluginPath:
            pluginPaths.append(userPluginPath)
        pluginList = []
        for pluginPath in pluginPaths:
            if os.access(pluginPath, os.R_OK):
                sys.path.insert(1, pluginPath)
                pluginList.extend([name[:-3] for name in
                                        os.listdir(pluginPath) if
                                        name.endswith('.py')])
        self.pluginInstances = []  # saves returned ref - avoid garbage collect
        self.pluginDescript = []
        errorList = []
        for name in pluginList:
            try:
                module = __import__(name)
                if not hasattr(module, 'main'):
                    raise ImportError
                self.pluginInstances.append(module.main(self.pluginInterface))
                descript = module.__doc__
                if descript:
                    descript = [line for line in descript.split('\n')
                                if line.strip()][0].strip()
                if not descript:
                    descript = name
                self.pluginDescript.append(descript)
            except ImportError:
                errorList.append(name)
        if errorList:
            QtGui.QMessageBox.warning(self, 'TreeLine',
                                _('Could not load plugin module %s') %
                                ', '.join(errorList))

    def setStatusMsg(self, text, timeout=0, forceShow=False):
        """Set the status bar message with optional timeout.
           Force a hidden bar to show if forceShow is true"""
        self.statusBar().showMessage(text, timeout)
        if text and forceShow:
            self.statusBar().show()
        if not text and not self.showStatusBar:
            self.statusBar().hide()

    def setMainCaption(self):
        """Set main window caption using doc filename path"""
        caption = ''
        if self.doc.fileName:
            caption = u'%s [%s] ' % (os.path.basename(self.doc.fileName),
                                     os.path.dirname(self.doc.fileName))
        caption += u'- TreeLine'
        self.setWindowTitle(caption)

    def getSaveFileName(self, caption, defaultExt, filterList,
                        currentFilter=''):
        """Return user specified file name for save as & export"""
        dir, name = os.path.split(self.doc.fileName)
        if not dir:
            dir = globalref.treeControl.recentFiles.firstPath()
        if not dir:
            dir = unicode(os.environ.get('HOME', ''),
                          sys.getfilesystemencoding())
        if name:
            dir = os.path.join(dir, os.path.splitext(name)[0] + defaultExt)
        currentFilter = QtCore.QString(currentFilter)
        fileName = QtGui.QFileDialog.getSaveFileName(self, caption, dir,
                                                     ';;'.join(filterList),
                                                     currentFilter)
        fileName = unicode(fileName)
        if fileName:
            selectedFilter = unicode(currentFilter)
            fileName = fileName.split(';*')[0]  # fix windows all filter bug
            if '.' not in fileName and \
                          selectedFilter != TreeMainWin.allFileFilter:
                fileName += defaultExt
            if selectedFilter == TreeMainWin.tlPlainFileFilter:
                self.doc.compressFile = False
                self.doc.encryptFile = False
            elif selectedFilter == TreeMainWin.tlCompFileFilter:
                self.doc.compressFile = True
                self.doc.encryptFile = False
            elif selectedFilter == TreeMainWin.tlEncryptFileFilter:
                self.doc.encryptFile = True
            return fileName
        return ''

    def getOpenFileName(self, caption, filterList):
        """Return user specified file name for file open"""
        dfltPath = os.path.dirname(self.doc.fileName)
        if not dfltPath:
            dfltPath = globalref.treeControl.recentFiles.firstPath()
        if not dfltPath:
            dfltPath = unicode(os.environ.get('HOME', ''),
                               sys.getfilesystemencoding())
        if not dfltPath:
            dfltPath = '..'
        fileName = QtGui.QFileDialog.getOpenFileName(self, caption, dfltPath,
                                                     ';;'.join(filterList))
        return unicode(fileName)

    def fileNew(self, newWinOk=True):
        """New file command"""
        if globalref.treeControl.savePrompt():
            dlg = treedialogs.TemplateDialog(self)
            if dlg.exec_() != QtGui.QDialog.Accepted:
                return
            globalref.treeControl.newFile(dlg.selectedPath(), newWinOk)

    def fileOpen(self):
        """Open a file"""
        if globalref.treeControl.savePrompt():
            filters = [TreeMainWin.tlGenFileFilter, TreeMainWin.textFileFilter,
                       TreeMainWin.treepadFileFilter,
                       TreeMainWin.xbelFileFilter, TreeMainWin.mozFileFilter,
                       TreeMainWin.odfFileFilter, TreeMainWin.allFileFilter]
            fileName = self.getOpenFileName('', filters)
            if fileName:
                globalref.treeControl.openFile(fileName)

    def fileOpenSample(self):
        """Open a sample template file"""
        if globalref.treeControl.savePrompt():
            path = self.findHelpPath()
            if not path:
                QtGui.QMessageBox.warning(self, 'TreeLine',
                                          _('Sample directory not found'))
                return
            fileName = unicode(QtGui.QFileDialog.getOpenFileName(self,
                                            _('Open Sample Template File'),
                                            os.path.dirname(path),
                                            TreeMainWin.tlGenFileFilter))
            if fileName:
                globalref.treeControl.openFile(fileName)

    def fileSave(self):
        """Save current file"""
        if self.doc.fileName and not self.fileImported:
            globalref.treeControl.saveFile(self.doc.fileName)
        else:
            self.fileSaveAs()

    def fileSaveAs(self):
        """Save file with a new name"""
        oldFileName = self.doc.fileName
        filterList = [TreeMainWin.tlPlainFileFilter,
                      TreeMainWin.tlCompFileFilter,
                      TreeMainWin.tlEncryptFileFilter,
                      TreeMainWin.allFileFilter]
        currentFilter = self.doc.encryptFile and 2 or \
                        (self.doc.compressFile and 1 or 0)
        fileName = self.getSaveFileName(_('Save As'), '.trl', filterList,
                                        filterList[currentFilter])
        if fileName and globalref.treeControl.saveFile(fileName):
            self.setMainCaption()
            globalref.treeControl.recentFiles.addEntry(fileName)
            globalref.treeControl.updateWinMenu()
            self.fileImported = False
            globalref.treeControl.delAutoSaveFile(oldFileName)

    def fileExport(self):
        """Export the file as html, a table or text.  Return fileName or ''"""
        ExportDlg = treedialogs.ExportDlg
        dlg = ExportDlg(self)
        if dlg.exec_() != QtGui.QDialog.Accepted:
            return ''
        indent = globalref.options.intData('IndentOffset', 0,
                                           optiondefaults.maxIndentOffset)
        nodeList = self.doc.selection
        addBranches = True
        if ExportDlg.exportWhat == ExportDlg.entireTree:
            nodeList = [self.doc.root]
        elif ExportDlg.exportWhat == ExportDlg.selectNode:
            addBranches = False
        elif ExportDlg.exportType != ExportDlg.tableType:
            nodeList = self.doc.selection.uniqueBranches()
        if not nodeList:
            QtGui.QMessageBox.warning(self, 'TreeLine',
                                      _('Nothing to export'))
            return ''
        fileName = ''
        try:
            if ExportDlg.exportType == ExportDlg.htmlType:
                fileName = self.getSaveFileName(_('Export Html'), '.html',
                                                [TreeMainWin.htmlFileFilter,
                                                 TreeMainWin.allFileFilter])
                if not fileName:
                    return ''
                outGroup = output.OutputGroup()
                if addBranches:
                    for node in nodeList:
                        branch = node.outputItemList(ExportDlg.includeRoot,
                                                     ExportDlg.openOnly, True)
                        outGroup.extend(branch)
                else:
                    outGroup.extend([node.outputItem(True) for node in
                                     nodeList])
                self.doc.exportHtmlColumns(fileName, outGroup,
                                           ExportDlg.numColumns, indent,
                                           ExportDlg.addHeader)
            elif ExportDlg.exportType == ExportDlg.dirTableType:
                defaultDir, fn = os.path.split(self.doc.fileName)
                if not defaultDir:
                    defaultDir = unicode(os.environ.get('HOME', ''),
                                         sys.getfilesystemencoding())
                dirName = QtGui.QFileDialog.getExistingDirectory(self,
                                                     _('Export to Directory'),
                                                     defaultDir)
                dirName = unicode(dirName)
                if dirName:
                    self.doc.exportDirTable(dirName, nodeList,
                                            ExportDlg.addHeader)
                    fileName = dirName
            elif ExportDlg.exportType == ExportDlg.dirPageType:
                defaultDir, fn = os.path.split(self.doc.fileName)
                if not defaultDir:
                    defaultDir = unicode(os.environ.get('HOME', ''),
                                         sys.getfilesystemencoding())
                dirName = QtGui.QFileDialog.getExistingDirectory(self,
                                                     _('Export to Directory'),
                                                     defaultDir)
                dirName = unicode(dirName)
                if dirName:
                    self.doc.exportDirPage(dirName, nodeList)
                    fileName = dirName
            elif ExportDlg.exportType == ExportDlg.xsltType:
                dlgText = _('A link to a stylesheet can be added to the '\
                            'XSL file\nEnter a CSS filename (blank for none)')
                link, ok = QtGui.QInputDialog.getText(self, 'TreeLine',
                                                      dlgText,
                                                      QtGui.QLineEdit.Normal,
                                                      self.doc.xslCssLink)
                if ok:
                    fileName = self.getSaveFileName(_('Export XSLT'), '.xsl',
                                                 [TreeMainWin.xsltFileFilter,
                                                  TreeMainWin.allFileFilter])
                    if fileName:
                        if self.doc.xslCssLink != unicode(link):
                            self.doc.xslCssLink = unicode(link)
                            self.doc.modified = True
                        self.doc.exportXslt(fileName, ExportDlg.includeRoot,
                                            indent)
                        self.actions['FileSave'].setEnabled(self.doc.modified)
            elif ExportDlg.exportType == ExportDlg.trlType:
                filterList = [TreeMainWin.tlPlainFileFilter,
                              TreeMainWin.tlCompFileFilter,
                              TreeMainWin.allFileFilter]
                origCompress = self.doc.compressFile
                fileName = self.getSaveFileName(_('Export Subtree'), '.trl',
                                                filterList,
                                                self.doc.compressFile)
                if fileName:
                    self.doc.exportTrlSubtree(fileName, nodeList, addBranches)
                self.doc.compressFile = origCompress
            elif ExportDlg.exportType == ExportDlg.tableType:
                fileName = self.getSaveFileName(_('Export Table'), '.tbl',
                                                [TreeMainWin.tableFileFilter,
                                                 TreeMainWin.allFileFilter])
                if fileName:
                    self.doc.exportTable(fileName, nodeList, addBranches)
            elif ExportDlg.exportType == ExportDlg.textType:
                fileName = self.getSaveFileName(_('Export Titles'), '.txt',
                                                [TreeMainWin.textFileFilter,
                                                 TreeMainWin.allFileFilter])
                if fileName:
                    self.doc.exportTabbedTitles(fileName, nodeList,
                                                addBranches,
                                                ExportDlg.includeRoot,
                                                ExportDlg.openOnly)
            elif ExportDlg.exportType == ExportDlg.xbelType:
                fileName = self.getSaveFileName(_('Export XBEL Bookmarks'),
                                                '.xml',
                                                [TreeMainWin.xbelFileFilter,
                                                 TreeMainWin.allFileFilter])
                if fileName:
                    self.doc.exportXbel(fileName, nodeList, addBranches)
            elif ExportDlg.exportType == ExportDlg.mozType:
                fileName = self.getSaveFileName(_('Export Html Bookmarks'),
                                                '.html',
                                                [TreeMainWin.mozFileFilter,
                                                 TreeMainWin.allFileFilter])
                if fileName:
                    self.doc.exportHtmlBookmarks(fileName, nodeList,
                                                 addBranches)
            elif ExportDlg.exportType == ExportDlg.xmlType:
                fileName = self.getSaveFileName(_('Export Generic XML'),
                                                '.xml',
                                                [TreeMainWin.xmlFileFilter,
                                                 TreeMainWin.allFileFilter])
                if fileName:
                    self.doc.exportGenericXml(fileName, nodeList, addBranches)
            else:    #  ODF type
                fontInfo = QtGui.QFontInfo(self.dataOutSplit.widget(0).font())
                fileName = self.getSaveFileName(_('Export ODF Text'), '.odt',
                                                [TreeMainWin.odfFileFilter,
                                                 TreeMainWin.allFileFilter])
                if fileName:
                    self.doc.exportOdf(fileName, nodeList, fontInfo.family(),
                                       fontInfo.pointSize(),
                                       fontInfo.fixedPitch(), addBranches,
                                       ExportDlg.includeRoot,
                                       ExportDlg.openOnly)
        except IOError, e:
            if ExportDlg.exportType == ExportDlg.dirTableType:
                QtGui.QMessageBox.warning(self, 'TreeLine', unicode(e))
            else:
                QtGui.QMessageBox.warning(self, 'TreeLine',
                                         _('Error - Could not write to %s') % \
                                          fileName)
            return ''
        return fileName


    def editUndo(self):
        """Undo the previous action"""
        self.doc.undoStore.undo(self.doc.redoStore)
        if TreeMainWin.setTypeDlg and TreeMainWin.setTypeDlg.isVisible():
            TreeMainWin.setTypeDlg.loadList()
        if TreeMainWin.configDlg:
            TreeMainWin.configDlg.resetParam()

    def editRedo(self):
        """Redo the previous undo"""
        self.doc.redoStore.undo(self.doc.undoStore)
        if TreeMainWin.setTypeDlg and TreeMainWin.setTypeDlg.isVisible():
            TreeMainWin.setTypeDlg.loadList()
        if TreeMainWin.configDlg:
            TreeMainWin.configDlg.resetParam()

    def editCut(self):
        """Cut the branch or text to the clipboard"""
        widget = self.focusWidgetWithAttr('copyAvail')
        if (self.treeView.hasFocus() or self.flatView.hasFocus()) or \
                  not widget or not widget.copyAvail():
            self.editCopyTree()
            self.editDelete()
        else:
            widget.cut()

    def editCopyTree(self):
        """Copy the tree branch to the clipboard"""
        if not self.doc.selection:
            return
        clip = QtGui.QApplication.clipboard()
        if clip.supportsSelection():
            textList = []
            if len(self.doc.selection) > 1:
                for node in self.doc.selection:
                    textList.extend(node.exportToText())
            else:
                textList = self.doc.selection[0].exportToText()
            clip.setText(u'\n'.join(textList), QtGui.QClipboard.Selection)
        self.mimeData = self.treeView.mimeData()  # TEMP req'd for PyQt bug
        clip.setMimeData(self.mimeData)

    def editCopy(self):
        """Copy the branch or text to the clipboard"""
        split = self.rightTabs.currentWidget()
        if split == self.dataOutSplit:  # check select in dataOut (no focus)
            views = [view for view in split.children() if \
                     hasattr(view, 'copyAvail') and view.copyAvail()]
            if views:
                views[0].copy()
                return
        widget = self.focusWidgetWithAttr('copyAvail')
        if (self.treeView.hasFocus() or self.flatView.hasFocus()) or \
                  not widget or not widget.copyAvail():
            self.editCopyTree()
        else:
            widget.copy()

    def editCopyText(self):
        """Copy node title text to the clipboard"""
        if not self.doc.selection:
            return
        titles = [item.title() for item in self.doc.selection]
        clip = QtGui.QApplication.clipboard()
        if clip.supportsSelection():
            clip.setText(u'\n'.join(titles), QtGui.QClipboard.Selection)
        clip.setText(u'\n'.join(titles))

    def editPaste(self):
        """Paste items or text from the clipboard"""
        text = self.clipText()
        if not text:
            return
        leftFocus = self.treeView.hasFocus() or self.flatView.hasFocus()
        if leftFocus:
            item, newFormats = self.doc.readXmlStringAndFormat(text)
            if item:
                if not self.doc.selection:
                    return
                if item.formatName == treedoc.TreeDoc.copyFormat.name:
                    itemList = item.childList
                else:            # copyFormat is dummy root of multi-select
                    itemList = [item]
                if newFormats:
                    self.doc.undoStore.addBranchUndo(self.doc.selection)
                    for format in newFormats:
                        self.doc.treeFormats.addIfMissing(format)
                    self.doc.treeFormats.updateDerivedTypes()
                    self.doc.treeFormats.updateUniqueID()
                    if TreeMainWin.configDlg:
                        TreeMainWin.configDlg.resetParam()
                else:
                    self.doc.undoStore.addChildListUndo(self.doc.selection)
                selectList = []
                for parent in self.doc.selection:
                    for node in itemList:
                        newNode = node.duplicateNode()
                        parent.addTree(newNode)
                        selectList.append(newNode)
                    parent.open = True
                self.doc.selection.replace(selectList)
                if newFormats:
                    self.doc.treeFormats.updateAutoChoices()
                self.updateViews()
            else:
                print 'Error reading XML string'
        else:
            item = self.doc.readXmlString(text)
            if item:
                text = item.title()
            widget = self.focusWidgetWithAttr('paste')
            if widget:
                widget.paste()

    def editPasteText(self):
        """Paste text from the clipboard"""
        text = self.clipText()
        if not text:
            return
        item = self.doc.readXmlString(text)
        if item and item.data:
            text = item.title()
        elif item and item.childList:
            text = item.childList[0].title()
        else:
            text = text.split(u'\n', 1)[0].strip()
        if self.treeView.hasFocus() or self.flatView.hasFocus():
            for item in self.doc.selection:
                item.setTitle(text, True)
                self.updateViewItem(item)
            self.updateCmdAvail()
        else:
            widget = self.focusWidgetWithAttr('pasteText')
            if widget:
                widget.paste()

    def editRename(self):
        """Start rename editor in selected tree node"""
        view = self.leftTabs.currentWidget()
        view.editItem(self.doc.selection[0].viewData)

    def editInBefore(self):
        """Insert new sibling before selection"""
        newList = []
        self.doc.undoStore.addParentListUndo(self.doc.selection)
        for sibling in self.doc.selection:
            newList.append(sibling.insertSibling())
        if globalref.options.boolData('RenameNewNodes'):
            self.doc.selection.replace(newList)
            if len(newList) == 1:
                self.updateViews()
                view = self.leftTabs.currentWidget()
                view.editItem(newList[0].viewData)
                return
        self.updateViews()

    def editInAfter(self):
        """Insert new sibling after selection"""
        newList = []
        self.doc.undoStore.addParentListUndo(self.doc.selection)
        for sibling in self.doc.selection:
            newList.append(sibling.insertSibling(inAfter=True))
        if globalref.options.boolData('RenameNewNodes'):
            self.doc.selection.replace(newList)
            if len(newList) == 1:
                self.updateViews()
                view = self.leftTabs.currentWidget()
                view.editItem(newList[0].viewData)
                return
        self.updateViews()

    def editAddChild(self):
        """Add a new child to the selected parent"""
        newList = []
        self.doc.undoStore.addChildListUndo(self.doc.selection)
        for parent in self.doc.selection:
            newList.append(parent.addChild())
            parent.open = True
        if globalref.options.boolData('RenameNewNodes'):
            self.doc.selection.replace(newList)
            if len(newList) == 1:
                self.updateViews()
                view = self.leftTabs.currentWidget()
                view.editItem(newList[0].viewData)
                return
        self.updateViews()

    def editDelete(self):
        """Delete the selected items"""
        if not self.doc.selection or self.doc.root in self.doc.selection:
            return
        nextSel = filter(None, [item.parent for item in self.doc.selection])
        nextSel.extend(filter(None, [item.prevSibling() for item in
                                     self.doc.selection]))
        nextSel.extend(filter(None, [item.nextSibling() for item in
                                     self.doc.selection]))
        self.doc.undoStore.addParentListUndo(self.doc.selection)
        for item in self.doc.selection:
            item.delete()
            try:
                self.flatView.rootItems.remove(item)
            except ValueError:
                pass
        while nextSel[-1] in self.doc.selection:
            del nextSel[-1]
        self.doc.selection.replace([nextSel[-1]])
        self.doc.selection.currentItem = nextSel[-1]  # Reqd if only root left
        self.doc.selection.validateHistory()
        self.updateViews()

    def sortedSelection(self):
        """Return a sorted selection list for indent & move commands"""
        sortedList = self.doc.selection[:]
        for item in sortedList:
            item.viewData.loadTempSortKey()
        sortedList.sort(lambda x,y: cmp(x.viewData.tempSortKey,
                        y.viewData.tempSortKey))
        return sortedList

    def editIndent(self):
        """Indent the selected items"""
        sortlist = self.sortedSelection()
        parentList = [item.parent for item in sortlist]
        siblingList = [item.prevSibling() for item in sortlist]
        self.doc.undoStore.addChildListUndo(parentList + siblingList)
        for item in sortlist:
            if item.indent():
                item.parent.open = True
        self.updateViews()

    def editUnindent(self):
        """Unindent the selected item"""
        sortlist = self.sortedSelection()
        parentList = [item.parent for item in sortlist]
        gpList = [item.parent for item in parentList]
        self.doc.undoStore.addChildListUndo(parentList + gpList)
        sortlist.reverse()
        for item in sortlist:
            item.unindent()
        self.updateViews()

    def editMoveUp(self):
        """Move the selected item up"""
        sortlist = self.sortedSelection()
        self.doc.undoStore.addParentListUndo(sortlist, True)
        for item in sortlist:
            item.move(-1)
        self.updateViews()

    def editMoveDown(self):
        """Move the selected item down"""
        sortlist = self.sortedSelection()
        sortlist.reverse()
        self.doc.undoStore.addParentListUndo(sortlist, True)
        for item in sortlist:
            item.move(1)
        self.updateViews()

    def editMoveFirst(self):
        """Move the selected item to be first child"""
        sortlist = self.sortedSelection()
        sortlist.reverse()
        self.doc.undoStore.addParentListUndo(sortlist, True)
        for item in sortlist:
            item.moveFirst()
        self.updateViews()

    def editMoveLast(self):
        """Move the selected item to be first child"""
        sortlist = self.sortedSelection()
        self.doc.undoStore.addParentListUndo(sortlist, True)
        for item in sortlist:
            item.moveLast()
        self.updateViews()

    def viewPrevSelect(self):
        """View the previous tree selection"""
        self.doc.selection.restorePrevSelect()

    def viewNextSelect(self):
        """View the next tree selection"""
        self.doc.selection.restoreNextSelect()

    def viewLeftSelect(self, action):
        """Show left view given by action"""
        if action == self.actions['ViewTree']:
            self.leftTabs.setCurrentWidget(self.treeView)
        else:
            self.leftTabs.setCurrentWidget(self.flatView)

    def viewRightSelect(self, action):
        """Show right view given by action"""
        if action == self.actions['ViewDataOutput']:
            self.rightTabs.setCurrentWidget(self.dataOutSplit)
        elif action == self.actions['ViewDataEdit']:
            self.rightTabs.setCurrentWidget(self.dataEditSplit)
        else:
            self.rightTabs.setCurrentWidget(self.titleListSplit)

    def viewChildren(self, checked):
        """Set to view item alone, with children or with descendants"""
        self.showItemChildren = checked
        self.updateRightView()

    def viewDescendants(self, checked):
        """Toggle showing descendants in output view"""
        self.dataOutSplit.widget(1).showDescendants = checked
        self.updateRightView()

    def viewStatusBar(self, checked):
        """Toggle the display of the status bar"""
        if checked:
            self.statusBar().show()
        else:
            self.statusBar().hide()
        self.showStatusBar = checked

    def dataTypeChange(self, action):
        """Change type based on submenu selection"""
        if self.doc.selection:
            self.doc.undoStore.addTypeUndo(self.doc.selection)
            for item in self.doc.selection:
                item.changeType(unicode(action.toolTip()))
            self.doc.modified = True
            self.updateViews()

    def dataSet(self, show):
        """Show dialog for setting item data types"""
        if show:
            if not TreeMainWin.setTypeDlg:
                TreeMainWin.setTypeDlg = treedialogs.TypeSetDlg()
                self.connect(TreeMainWin.setTypeDlg,
                             QtCore.SIGNAL('viewClosed'),
                             globalref.treeControl.updateDialogs)
            else:
                TreeMainWin.setTypeDlg.loadList()
            TreeMainWin.setTypeDlg.setCurrentSel()
            TreeMainWin.setTypeDlg.updateDlg()
            TreeMainWin.setTypeDlg.show()
        else:
            TreeMainWin.setTypeDlg.hide()

    def dataConfig(self, show):
        """Show dialog for modifying data types"""
        if show:
            if not TreeMainWin.configDlg:
                TreeMainWin.configDlg = configdialog.ConfigDialog()
                self.connect(TreeMainWin.configDlg,
                             QtCore.SIGNAL('dialogClosed'),
                             globalref.treeControl.updateDialogs)
            elif not TreeMainWin.configDlg.isVisible():
                TreeMainWin.configDlg.resetCurrent()
            TreeMainWin.configDlg.show()
        else:
            TreeMainWin.configDlg.close()

    def dataCopyTypes(self):
        """Copy the configuration from another TreeLine file"""
        dfltDir = os.path.dirname(self.doc.fileName)
        fileName = unicode(QtGui.QFileDialog.getOpenFileName(self,
                           _('Open Configuration File'), dfltDir,
                           TreeMainWin.tlGenFileFilter))
        password = ''
        while fileName:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            try:
                self.doc.treeFormats.configCopy(fileName, password)
                QtGui.QApplication.restoreOverrideCursor()
                if TreeMainWin.configDlg:
                    TreeMainWin.configDlg.resetParam()
                return
            except treedoc.PasswordError:
                QtGui.QApplication.restoreOverrideCursor()
                dlg = treedialogs.PasswordEntry(False, self)
                if dlg.exec_() != QtGui.QDialog.Accepted:
                    return
                password = dlg.password
            except (IOError, UnicodeError, treedoc.ReadFileError):
                QtGui.QApplication.restoreOverrideCursor()
                QtGui.QMessageBox.warning(self, 'TreeLine',
                                          _('Error - could not read file "%s"')
                                          % fileName)
                return

    def dataSort(self, show):
        """Open the dialog for sorting nodes"""
        if show:
            if not TreeMainWin.sortDlg:
                TreeMainWin.sortDlg = treedialogs.SortDlg()
                self.connect(TreeMainWin.sortDlg, QtCore.SIGNAL('viewClosed'),
                             globalref.treeControl.updateDialogs)
            else:
                TreeMainWin.sortDlg.updateDialog()
            TreeMainWin.sortDlg.show()
        else:
            TreeMainWin.sortDlg.hide()

    def dataFilterCond(self):
        """Filter types with conditional rules"""
        if self.condFilter:
            type = self.condFilter.formatName
        else:
            typeList = self.doc.treeFormats.nameList(True)
            defaultTypeNum = 0
            if self.doc.selection:
                defaultTypeNum = typeList.index(self.doc.selection[0].
                                                formatName)
            type, ok = QtGui.QInputDialog.getItem(self, _('Filter Data'),
                                                  _('Select data type'),
                                                  typeList, defaultTypeNum,
                                                  False)
            if not ok:
                return
        format = self.doc.treeFormats[unicode(type)]
        dlg = configdialog.ConditionDlg(_('Filter %s Data Type') % format.name,
                                       format, self)
        if self.condFilter:
            dlg.setConditions(self.condFilter)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            self.condFilter = dlg.conditional()
            self.condFilter.setupFields(format)
            self.condFilter.formatName = format.name
            if self.leftTabs.currentWidget() == self.flatView:
                self.updateLeftView()
            else:
                self.leftTabs.setCurrentWidget(self.flatView)
            self.updateCmdAvail()

    def dataFilterText(self):
        """Filter with a text search string"""
        searchStr, ok = QtGui.QInputDialog.getText(self, _('Filter Data'),
                                                   _('Enter key words'),
                                                   QtGui.QLineEdit.Normal,
                                                   ' '.join(self.textFilter))
        if not ok:
            return
        self.textFilter = [text.lower() for text in
                           unicode(searchStr).strip().split()]
        if self.leftTabs.currentWidget() == self.flatView:
            self.updateLeftView()
        else:
            self.leftTabs.setCurrentWidget(self.flatView)
        self.updateCmdAvail()

    def dataFilterClear(self):
        """Clear current filtering"""
        self.condFilter = None
        self.textFilter = []
        if self.leftTabs.currentWidget() == self.flatView:
            self.updateLeftView()
        self.updateCmdAvail()

    def dataEditField(self):
        """Edit a child field in all selected nodes"""
        if not self.doc.selection:
            return
        fieldList = self.doc.treeFormats.commonFields(self.doc.selection)
        if fieldList:           # has common fields
            dlg = treedialogs.EditFieldsDlg(fieldList, self)
            if dlg.exec_() != QtGui.QDialog.Accepted:
                return
            self.doc.undoStore.addDataUndo(self.doc.selection)
            for item in self.doc.selection:
                item.editFields(dlg.resultDict)
                if self.pluginInterface:
                    fields = [item.nodeFormat().findField(name) for name in
                              dlg.resultDict.keys()]
                    self.pluginInterface.execCallback(globalref.
                                                      pluginInterface.
                                                      dataChangeCallbacks,
                                                      item, fields)
            self.updateViews()
        else:
            QtGui.QMessageBox.warning(self, 'TreeLine',
                                      _('No common fields to set'))

    def dataNumbering(self):
        """Add numbering to a data field"""
        item = self.doc.selection[0]
        NumberingDlg = treedialogs.NumberingDlg
        dlg = NumberingDlg(item.branchFields(), item.maxDescendLevel(), self)
        if dlg.exec_() != QtGui.QDialog.Accepted:
            return
        self.doc.undoStore.addBranchUndo(item)
        if dlg.currentStyle == NumberingDlg.outlineType:
            item.addNumbering(dlg.getField(), dlg.currentFormat,
                              dlg.includeRoot(), False, not dlg.existOnly(),
                              False, dlg.startNumber())
        elif dlg.currentStyle == NumberingDlg.sectionType:
            item.addNumbering(dlg.getField(), dlg.currentFormat,
                              dlg.includeRoot(), True, not dlg.existOnly(),
                              False, dlg.startNumber())
        else:        # singleType
            item.addNumbering(dlg.getField(), dlg.currentFormat,
                              False, False, not dlg.existOnly(), True,
                              dlg.startNumber())
        self.updateViews()
        if TreeMainWin.configDlg:
            TreeMainWin.configDlg.resetParam()

    def dataAddCat(self):
        """Add child's category items as a new child level"""
        selectList = self.doc.selection.uniqueBranches()
        children = []
        for item in selectList:
            children.extend(item.childList)
        fieldList = self.doc.treeFormats.commonFields(children)
        if fieldList:           # has common fields
            dlg = treedialogs.FieldSelectDlg(fieldList, _('Category Fields'),
                                             _('Select fields for new level'),
                                             self)
            if dlg.exec_() != QtGui.QDialog.Accepted:
                return
            self.doc.undoStore.addBranchUndo(selectList)
            for item in selectList:
                item.addChildCat(dlg.getSelList())
            self.updateViews()
            if TreeMainWin.configDlg:
                TreeMainWin.configDlg.resetParam()
        else:
            QtGui.QMessageBox.warning(self, 'TreeLine',
                                      _('Cannot expand without common fields'))

    def dataFlatCat(self):
        """Collapse data by merging fields"""
        selectList = self.doc.selection.uniqueBranches()
        self.doc.undoStore.addBranchUndo(selectList)
        for item in selectList:
            item.flatChildCat()
        self.updateViews()
        if TreeMainWin.configDlg:
            TreeMainWin.configDlg.resetParam()

    def dataArrangeRef(self):
        """Arrange data using parent references"""
        selectList = self.doc.selection.uniqueBranches()
        children = []
        for item in selectList:
            children.extend(item.childList)
        fieldList = self.doc.treeFormats.commonFields(children)
        if not fieldList:
            QtGui.QMessageBox.warning(self, 'TreeLine',
                                      _('No common fields with parent '\
                                        'references'))
            return
        refField, ok = QtGui.QInputDialog.getItem(self, _('Reference Field'),
                                                  _('Select field with parent'\
                                                    ' references'),
                                                  fieldList, 0, False)
        if not ok:
            return
        self.doc.undoStore.addBranchUndo(selectList)
        for item in selectList:
            item.arrangeByRef(unicode(refField))
        self.updateViews()

    def dataFlatRef(self):
        """Collapse data after adding references to parents"""
        selectList = self.doc.selection.uniqueBranches()
        dlg = configdialog.FieldEntry(_('Flatten by Reference'),
                                      _('Enter new field name for parent'\
                                        ' references:'), '',
                                      [], self)
        if dlg.exec_() != QtGui.QDialog.Accepted:
            return
        self.doc.undoStore.addBranchUndo(selectList)
        for item in selectList:
            item.flatByRef(dlg.text)
        self.updateViews()
        if TreeMainWin.configDlg:
            TreeMainWin.configDlg.resetParam()

    def toolsExpand(self):
        """Expand all children of selected item"""
        for item in self.doc.selection:
            item.openBranch(True)
        self.updateViews()

    def toolsCollapse(self):
        """Collapse all children of selected item"""
        for item in self.doc.selection:
            item.openBranch(False)
        self.updateViews()

    def toolsFind(self, show):
        """Find item matching text string"""
        if show:
            if not TreeMainWin.findDlg:
                TreeMainWin.findDlg = treedialogs.FindTextEntry()
                self.connect(TreeMainWin.findDlg, QtCore.SIGNAL('viewClosed'),
                             globalref.treeControl.updateDialogs)
            TreeMainWin.findDlg.entry.selectAll()
            TreeMainWin.findDlg.entry.setFocus()
            TreeMainWin.findDlg.show()
        else:
            TreeMainWin.findDlg.hide()

    def toolsSpellCheck(self):
        """Spell check the tree's text data strting in the selected branch"""
        spellPath = globalref.options.strData('SpellCheckPath', True)
        try:
            spCheck = spellcheck.SpellCheck(spellPath, self.doc.spellChkLang)
        except spellcheck.SpellCheckError:
            if sys.platform.startswith('win'):
                ans = QtGui.QMessageBox.warning(self, _('Spell Check Error'),
                                        _('Could not find either aspell.exe '\
                                          'or ispell.exe\nManually locate?'),
                                        _('&Browse'), _('&Cancel'), '', 0, 1)
                if ans != 0:
                    return
                path = unicode(QtGui.QFileDialog.getOpenFileName(self,
                                         _('Locate aspell.exe or ipsell.exe'),
                                         '', _('Program (*.exe)')))
                if path:
                    path = path[:-4]
                    if ' ' in path:
                        path = '"%s"' % path
                    globalref.options.changeData('SpellCheckPath',
                                      path.encode(sys.getfilesystemencoding()),
                                      True)
                    globalref.options.writeChanges()
                    self.toolsSpellCheck()
                return
            else:
                QtGui.QMessageBox.warning(self, 'TreeLine',
                                  _('TreeLine Spell Check Error\n'\
                                    'Make sure aspell or ispell is installed'))
                return
        if self.leftTabs.currentWidget() == self.flatView:
            self.leftTabs.setCurrentWidget(self.treeView)
        origSelect = self.doc.selection.uniqueBranches()
        dlg = treedialogs.SpellCheckDlg(spCheck, origSelect, self)
        if dlg.startSpellCheck():
            if dlg.exec_() != QtGui.QDialog.Accepted:
                spCheck.close()
                return
        spCheck.close()
        if origSelect[0].parent:
            ans = QtGui.QMessageBox.information(self, _('TreeLine Spell Check'),
                                          _('Finished checking the branch\n'\
                                            'Continue from the root branch?'),
                                          _('&Yes'), _('&No'), '', 0, 1)
            if ans == 0:
                globalref.docRef.selection.changeSearchOpen([self.doc.root])
                self.toolsSpellCheck()
        else:
            QtGui.QMessageBox.information(self, _('TreeLine Spell Check'),
                                          _('Finished checking the branch'))
        globalref.docRef.selection.changeSearchOpen(origSelect)

    def toolsRemXslt(self):
        """Delete reference to XSLT export"""
        if self.doc.xlstLink:
            self.doc.undoStore.addParamUndo([(self.doc, 'xlstLink')])
            self.doc.xlstLink = ''
            self.doc.modified = True
            self.updateCmdAvail()

    def toolsGenOpt(self):
        """Set user preferences for all files"""
        oldAutoSave = globalref.options.intData('AutoSaveMinutes', 0, 999)
        dlg = optiondlg.OptionDlg(globalref.options, self)
        dlg.setWindowTitle(_('General Options'))
        dlg.startGroupBox(_('Startup Condition'))
        optiondlg.OptionDlgBool(dlg, 'AutoFileOpen',
                                _('Automatically open last file used'))
        optiondlg.OptionDlgBool(dlg, 'StartShowChildren',
                                _('Show children in right-hand view'))
        optiondlg.OptionDlgBool(dlg, 'StartShowDescend',
                                _('Show descendants in output view'))
        optiondlg.OptionDlgBool(dlg, 'ShowStatusBar', _('Show status bar'))
        optiondlg.OptionDlgBool(dlg, 'PersistTreeState',
                                     _('Restore view states of recent files'))
        optiondlg.OptionDlgBool(dlg, 'SaveWindowGeom',
                                _('Restore window geometry from last exit'))
        dlg.startGroupBox(_('Features Available'))
        optiondlg.OptionDlgBool(dlg, 'ClickRename', _('Click item to rename'))
        optiondlg.OptionDlgBool(dlg, 'DragTree',
                                _('Tree drag && drop available'))
        optiondlg.OptionDlgBool(dlg, 'InsertOnEnter',
                                _('Insert node with enter'))
        optiondlg.OptionDlgBool(dlg, 'RenameNewNodes',
                                _('Rename new nodes when created'))
        optiondlg.OptionDlgBool(dlg, 'OpenSearchNodes',
                                _('Automatically open search nodes'))
        optiondlg.OptionDlgBool(dlg, 'ShowTreeIcons',
                                _('Show icons in the tree view'))
        optiondlg.OptionDlgBool(dlg, 'EnableExecLinks',
                                _('Enable executable links'))
        optiondlg.OptionDlgBool(dlg, 'OpenNewWindow',
                                _('Open files in new windows'))
        dlg.startNewColumn()
        dlg.startGroupBox(_('New Objects'))
        optiondlg.OptionDlgBool(dlg, 'CompressNewFiles',
                               _('Set new files to compressed by default'))
        optiondlg.OptionDlgBool(dlg, 'EncryptNewFiles',
                               _('Set new files to encrypted by default'))
        optiondlg.OptionDlgBool(dlg, 'HtmlNewFields',
                                _('New fields default to HTML content'))
        dlg.endGroupBox()
        optiondlg.OptionDlgRadio(dlg, 'SelectOrder',
                                 _('Multiple Selection Sequence'),
                                 [('tree', _('Tree order')),
                                  ('select', _('Selection order'))])
        dlg.startGroupBox(_('Data Editor Pages'))
        optiondlg.OptionDlgInt(dlg, 'EditorPages',
                               _('Number of pages shown \n(set to 0 for all)'),
                               0, 999)
        dlg.startGroupBox(_('Undo Memory'))
        optiondlg.OptionDlgInt(dlg, 'UndoLevels',
                               '%s ' % _('Number of undo levels'), 0, 99)
        dlg.startNewColumn()
        dlg.startGroupBox(_('Auto Save'))
        optiondlg.OptionDlgInt(dlg, 'AutoSaveMinutes',
                               _('Minutes between saves \n'
                                 '(set to 0 to disable)'), 0, 999)
        dlg.startGroupBox(_('Recent Files'))
        optiondlg.OptionDlgInt(dlg, 'RecentFiles',
                               _('Number of recent files \nin the File menu'),
                               0, 99)
        dlg.startGroupBox(_('Data Editor Formats'))
        optiondlg.OptionDlgStr(dlg, 'EditDateFormat', _('Dates'))
        optiondlg.OptionDlgStr(dlg, 'EditTimeFormat', _('Times'))
        dlg.startGroupBox(_('Appearance'))
        optiondlg.OptionDlgInt(dlg, 'IndentOffset',
                               _('Child indent offset (points)'),
                               0, optiondefaults.maxIndentOffset)
        optiondlg.OptionDlgInt(dlg, 'MaxEditLines',
                               _('Default max data editor lines'),
                               1, optiondefaults.maxNumLines)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            if not globalref.options.boolData('PersistTreeState'):
                globalref.treeControl.recentFiles.clearTreeStates()
            globalref.options.writeChanges()
            if oldAutoSave != globalref.options.intData('AutoSaveMinutes',
                                                        0, 999):
                globalref.treeControl.resetAutoSave()
            self.doc.undoStore.levels = globalref.options.\
                                                  intData('UndoLevels', 0, 99)
            self.doc.redoStore.levels = globalref.options.\
                                                  intData('UndoLevels', 0, 99)
            globalref.treeControl.recentFiles.\
                      changeNumEntries(globalref.options.
                                       intData('RecentFiles', 0, 99))
            self.treeView.updateGenOptions()
            self.flatView.updateGenOptions()
            self.updateViews()

    def toolsTreeFont(self):
        """Show dialog for setting custom tree font"""
        oldTreeFont = self.treeView.font()
        treeFont, ok = QtGui.QFontDialog.getFont(oldTreeFont, self)
        if ok and treeFont != oldTreeFont:
            self.treeView.setFont(treeFont)
            self.flatView.setFont(treeFont)
            self.saveFontToOptions(treeFont, 'Tree')
            self.updateViews()

    def toolsOutputFont(self):
        """Show dialog for setting custom output font"""
        oldOutputFont = self.dataOutSplit.widget(0).font()
        outputFont, ok = QtGui.QFontDialog.getFont(oldOutputFont, self)
        if ok and outputFont != oldOutputFont:
            self.dataOutSplit.widget(0).setFont(outputFont)
            self.dataOutSplit.widget(1).setFont(outputFont)
            self.saveFontToOptions(outputFont, 'Output')
            self.updateViews()

    def toolsEditFont(self):
        """Show dialog for setting custom editor font"""
        oldEditFont = self.dataEditSplit.widget(0).font()
        editFont, ok = QtGui.QFontDialog.getFont(oldEditFont, self)
        if ok and editFont != oldEditFont:
            for i in range(2):
                self.dataEditSplit.widget(i).setFont(editFont)
                self.titleListSplit.widget(i).setFont(editFont)
            self.saveFontToOptions(editFont, 'Editor')
            self.updateViews()

    def toolsFileOpt(self):
        """Set file preferences"""
        globalref.options.addData('SpaceBetween',
                                  self.doc.spaceBetween and 'yes' or 'no',
                                  False)
        globalref.options.addData('LineBreaks',
                                  self.doc.lineBreaks and 'yes' or 'no', False)
        globalref.options.addData('FormHtml',
                                  self.doc.formHtml and 'yes' or 'no', False)
        globalref.options.addData('CompressFile',
                                  self.doc.compressFile and 'yes' or 'no',
                                  False)
        globalref.options.addData('EncryptFile',
                                  self.doc.encryptFile and 'yes' or 'no',
                                  False)
        globalref.options.addData('ChildFieldSep', self.doc.childFieldSep,
                                  False)
        globalref.options.addData('SpellChkLang', self.doc.spellChkLang, False)
        dlg = optiondlg.OptionDlg(globalref.options, self)
        dlg.setWindowTitle(_('File Options'))
        dlg.startGroupBox(_('Output Formating'))
        optiondlg.OptionDlgBool(dlg, 'SpaceBetween',
                                _('Add blank lines between nodes'), False)
        optiondlg.OptionDlgBool(dlg, 'LineBreaks',
                                _('Add line breaks after each line'), False)
        optiondlg.OptionDlgBool(dlg, 'FormHtml',
                                _('Allow HTML rich text in formats'), False)
        dlg.startGroupBox(_('File Storage'))
        optiondlg.OptionDlgBool(dlg, 'CompressFile',
                                _('Use file compression'), False)
        optiondlg.OptionDlgBool(dlg, 'EncryptFile',
                                _('Use file encryption'), False)
        dlg.startGroupBox(_('Embedded Child Fields'))
        optiondlg.OptionDlgStr(dlg, 'ChildFieldSep',
                               _('Separator String'), False)
        dlg.startGroupBox(_('Spell Check Language'))
        optiondlg.OptionDlgStr(dlg, 'SpellChkLang',
                               '%s\n%s' % (_('2-letter code (blank'),
                                           _('for system default)')),
                               False)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            space = globalref.options.boolData('SpaceBetween')
            breaks = globalref.options.boolData('LineBreaks')
            html = globalref.options.boolData('FormHtml')
            compress = globalref.options.boolData('CompressFile')
            encrypt = globalref.options.boolData('EncryptFile')
            childFieldSep = globalref.options.strData('ChildFieldSep', True)
            spellChkLang = globalref.options.strData('SpellChkLang', True)
            if space != self.doc.spaceBetween or \
                      breaks != self.doc.lineBreaks or \
                      html != self.doc.formHtml or \
                      compress != self.doc.compressFile or \
                      encrypt != self.doc.encryptFile or \
                      childFieldSep != self.doc.childFieldSep or \
                      spellChkLang != self.doc.spellChkLang:
                self.doc.undoStore.addParamUndo([(self.doc, 'spaceBetween'),
                                                 (self.doc, 'lineBreaks'),
                                                 (self.doc, 'formHtml'),
                                                 (self.doc, 'compressFile'),
                                                 (self.doc, 'encryptFile'),
                                                 (self.doc, 'childFieldSep')])
                self.doc.spaceBetween = space
                self.doc.lineBreaks = breaks
                self.doc.formHtml = html
                self.doc.compressFile = compress
                self.doc.encryptFile = encrypt
                self.doc.childFieldSep = childFieldSep
                self.doc.spellChkLang = spellChkLang
                self.doc.modified = True
                self.updateViews()
                self.updateCmdAvail()

    def toolsShortcuts(self):
        """Start dialog to customize keyboard shorcuts"""
        dlg = treedialogs.ShortcutDlg(self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            self.setupShortcuts()

    def toolsCustomToolbar(self):
        """Start dialog to customize toolbar buttons"""
        dlg = treedialogs.ToolbarDlg(self.setupToolbars,
                                     TreeMainWin.toolIcons, self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            pass

    def toolsDefaultColor(self, checked):
        """Toggle default color setting"""
        setting = checked and 'yes' or 'no'
        globalref.options.changeData('UseDefaultColors', setting, True)
        globalref.options.writeChanges()
        self.updateColors()

    def toolsBkColor(self):
        """Set view background color"""
        background = self.getOptionColor('Background')
        newColor = QtGui.QColorDialog.getColor(background, self)
        if newColor.isValid() and newColor != background:
            self.setOptionColor('Background', newColor)
            globalref.options.writeChanges()
            self.updateColors()

    def toolsTxtColor(self):
        """Set view text color"""
        foreground = self.getOptionColor('Foreground')
        newColor = QtGui.QColorDialog.getColor(foreground, self)
        if newColor.isValid() and newColor != foreground:
            self.setOptionColor('Foreground', newColor)
            globalref.options.writeChanges()
            self.updateColors()

    def helpContents(self):
        """View the Using section of the ReadMe file"""
        self.helpReadMe()
        if TreeMainWin.helpView:
            TreeMainWin.helpView.textView.scrollToAnchor('using')

    def findHelpPath(self):
        """Return the full path of the help files or ''"""
        pathList = [helpFilePath, os.path.join(globalref.modPath, '../doc/'),
                    globalref.modPath, os.path.join(globalref.modPath, 'doc/')]
        fileList = ['README.html']
        if globalref.lang and globalref.lang != 'C':
            fileList[0:0] = ['README_%s.html' % globalref.lang,
                             'README_%s.html' % globalref.lang[:2]]
        for path in filter(None, pathList):
            for fileName in fileList:
                fullPath = os.path.join(path, fileName)
                if os.access(fullPath, os.R_OK):
                    return fullPath
        return ''

    def helpReadMe(self):
        """View the ReadMe file"""
        if not TreeMainWin.helpView:
            path = self.findHelpPath()
            if path:
                TreeMainWin.toolIcons.loadIcons(['helpback', 'helpforward',
                                                 'helphome', 'helpprevious',
                                                 'helpnext'])
                TreeMainWin.helpView = helpview.HelpView(path,
                                                  _('TreeLine README File'),
                                                  TreeMainWin.toolIcons)
            else:
                QtGui.QMessageBox.warning(self, 'TreeLine',
                                          _('Read Me file not found'))
                return
        TreeMainWin.helpView.show()
        TreeMainWin.helpView.textView.home()

    def helpAbout(self):
        """About this program"""
        QtGui.QMessageBox.about(self, 'TreeLine',
                               _('TreeLine, Version %(ver)s\n by %(author)s') %
                               {'ver':__version__, 'author':__author__})

    def helpPlugin(self):
        """Show loaded plugin modules"""
        dlg = treedialogs.PluginListDlg(self.pluginDescript, self)
        dlg.exec_()

    def addTextTag(self):
        """Add html tag to active data editor"""
        editor = self.focusWidgetWithAttr('addHtmlTag')
        if not editor:
            return
        label = unicode(self.sender().text())
        openTag, closeTag = TreeMainWin.tagDict[label]
        if label == _('&Size...'):
            num, ok = QtGui.QInputDialog.getInteger(self, _('Font Size'),
                                                    _('Enter size factor '\
                                                      '(-6 to +6)'),
                                                    1, -6, 6)
            if not ok or num == 0:
                return
            openTag = openTag % num
        elif label == _('&Color...'):
            color = QtGui.QColorDialog.getColor(QtGui.QColor(), self)
            if not color.isValid():
                return
            openTag = openTag % color.name()
        editor.addHtmlTag(openTag, closeTag)

    def inlineLinkTagPrompt(self):
        """Prompt user to pick node for inline internal link"""
        self.linkTagEditor = self.focusWidgetWithAttr('addHtmlLinkTag')
        if not self.linkTagEditor:
            return
        view = self.leftTabs.currentWidget()
        view.noSelectClickCallback = self.addInlineLinkTag
        globalref.setStatusBar(_('Click on tree node for link destination'),
                               0, True)
        for action in self.actions.values():
            action.setEnabled(False)

    def addInlineLinkTag(self, item):
        """Add link to item to active data editor"""
        globalref.setStatusBar('')
        self.linkTagEditor.addHtmlLinkTag(item.refFieldText(), item.title())
        self.linkTagEditor = None
        for action in self.actions.values():
            action.setEnabled(True)
        self.updateCmdAvail()

    def focusLeftView(self):
        """Focus active view in the left pane"""
        self.leftTabs.currentWidget().setFocus()

    def treeSelectPrev(self):
        """Select the pevious tree item"""
        self.doc.selection.treeSelectPrev()

    def treeSelectNext(self):
        """Select the next tree item"""
        self.doc.selection.treeSelectNext()

    def treePrevSibling(self):
        """Select the pevious sibling item"""
        self.doc.selection.treePrevSibling()

    def treeNextSibling(self):
        """Select the next sibling item"""
        self.doc.selection.treeNextSibling()

    def treeSelectParent(self):
        """Select the parnt item"""
        self.doc.selection.treeSelectParent()

    def treeOpenItem(self):
        """Set selection to open"""
        self.doc.selection.treeOpenItem()

    def treeCloseItem(self):
        """Set selection to closed"""
        self.doc.selection.treeCloseItem()

    def treePageUp(self):
        """Page up in the left view"""
        view = self.leftTabs.currentWidget()
        view.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                            QtCore.Qt.Key_PageUp,
                                            QtCore.Qt.NoModifier))

    def treePageDown(self):
        """Page down in the left view"""
        view = self.leftTabs.currentWidget()
        view.keyPressEvent(QtGui.QKeyEvent(QtCore.QEvent.KeyPress,
                                            QtCore.Qt.Key_PageDown,
                                            QtCore.Qt.NoModifier))

    def treeIncremSearch(self):
        """Begin an incremental title search"""
        leftView = self.leftTabs.currentWidget()
        leftView.setFocus()
        leftView.treeIncremSearch()

    def treeIncremNext(self):
        """Go to next item in title search (incremental)"""
        self.leftTabs.currentWidget().treeIncremNext()

    def treeIncremPrev(self):
        """Go to previous item in title search (incremental)"""
        self.leftTabs.currentWidget().treeIncremPrev()

    def rightChildPageUp(self):
        """Page up the right-hand child view"""
        self.rightTabs.currentWidget().widget(1).scrollPage(-1)

    def rightChildPageDown(self):
        """Page down the right-hand child view"""
        self.rightTabs.currentWidget().widget(1).scrollPage(1)

    def rightParentPageUp(self):
        """Page up the right-hand parent view"""
        self.rightTabs.currentWidget().widget(0).scrollPage(-1)

    def rightParentPageDown(self):
        """Page down the right-hand parent view"""
        self.rightTabs.currentWidget().widget(0).scrollPage(1)

    def closeEvent(self, event):
        """Ask for save if doc modified"""
        if globalref.treeControl.savePrompt(True):
            globalref.treeControl.recentFiles.writeList()
            toolbarPos = base64.b64encode(self.saveState().data())
            globalref.options.changeData('ToolbarPosition', toolbarPos, True)
            if globalref.options.boolData('SaveWindowGeom'):
                globalref.options.changeData('WindowXSize', self.width(), True)
                globalref.options.changeData('WindowYSize', self.height(),
                                             True)
                globalref.options.changeData('WindowXPos', self.geometry().x(),
                                             True)
                globalref.options.changeData('WindowYPos', self.geometry().y(),
                                             True)
                treeWidth = self.leftTabs.width()
                rightWidth = self.rightTabs.width()
                treePercent = int(treeWidth * 100.0 / (treeWidth + rightWidth))
                globalref.options.changeData('TreeSplitPercent', treePercent,
                                             True)
                mainHeight, childHeight = self.dataOutSplit.sizes()
                outPercent = int(mainHeight * 100.0 /
                                 (mainHeight + childHeight))
                outChildView = self.rightTabs.widget(0).widget(1)
                if outPercent == 100 and outChildView.oldViewHeight:
                    outPercent = 100 - outChildView.oldViewHeight
                globalref.options.changeData('OutputSplitPercent',
                                             outPercent, True)
                mainHeight, childHeight = self.dataEditSplit.sizes()
                editPercent = int(mainHeight * 100.0 /
                                  (mainHeight + childHeight))
                editChildView = self.rightTabs.widget(1).widget(1)
                if editPercent == 100 and editChildView.oldViewHeight:
                    editPercent = 100 - editChildView.oldViewHeight
                globalref.options.changeData('EditorSplitPercent',
                                             editPercent, True)
                mainHeight, childHeight = self.titleListSplit.sizes()
                titlePercent = int(mainHeight * 100.0 /
                                   (mainHeight + childHeight))
                globalref.options.changeData('TitleSplitPercent',
                                             titlePercent, True)
                tabNum = self.rightTabs.currentIndex()
                globalref.options.changeData('ActiveRightView', tabNum, True)
            globalref.options.writeChanges()
            globalref.treeControl.removeWin(self)
            # make clipboard data persistent and fix error message on windows
            if not globalref.treeControl.windowCount():
                clip = QtGui.QApplication.clipboard()
                clipEvent = QtCore.QEvent(QtCore.QEvent.Clipboard)
                QtGui.QApplication.sendEvent(clip, clipEvent)
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, event):
        """Accept drags of files to main window"""
        if event.mimeData().hasUrls():
            event.accept()

    def dropEvent(self, event):
        """Drop a file onto window"""
        fileList = event.mimeData().urls()
        if fileList and globalref.treeControl.savePrompt():
            globalref.treeControl.openFile(unicode(fileList[0].toLocalFile()),
                                           False)

    def loadTypeSubMenu(self):
        """Update type select submenu with type names and check marks"""
        self.typeSubMenu.clear()
        if not self.doc.selection:
            return
        selectionTypes = self.doc.selection.formatNames()
        names = self.doc.treeFormats.nameList(True)
        usedShortcuts = []
        for name in names:
            shortcutPos = 0
            try:
                while name[shortcutPos] in usedShortcuts:
                    shortcutPos += 1
                usedShortcuts.append(name[shortcutPos])
                text = u'%s&%s' % (name[:shortcutPos], name[shortcutPos:])
            except IndexError:
                text = name
            action = self.typeSubMenu.addAction(text)
            action.setCheckable(True)
            if name in selectionTypes:
                action.setChecked(True)

    def setupShortcuts(self):
        """Add shortcuts from options to actions"""
        for name, action in self.actions.iteritems():
            seq = globalref.options.strData(name, True)
            seq = '+'.join(seq.split())  # for legacy config files
            action.setShortcut(QtGui.QKeySequence(seq))
        for name, shortcut in self.shortcuts.iteritems():
            seq = globalref.options.strData(name, True)
            seq = '+'.join(seq.split())  # for legacy config files
            shortcut.setKey(QtGui.QKeySequence(seq))
        # add shortcut to flyout Item Type menu
        setTypeKey = globalref.options.strData('DataSetItemType', True)
        setTypeKey = '+'.join(setTypeKey.split())
        self.typeSubMenu.setTitle('%s  (%s)' % (_('Set &Item Type'),
                                                setTypeKey))

    def addActionIcons(self):
        """Add icons to actions for menus and toolbars"""
        for name, action in self.actions.iteritems():
            icon = TreeMainWin.toolIcons.getIcon(name.lower())
            if icon:
                action.setIcon(icon)

    def setupToolbars(self):
        """Add actions defined in options to toolbars"""
        for toolbar in self.toolbars:
            toolbar.hide()
            self.removeToolBar(toolbar)
        self.toolbars = []
        numToolbars = globalref.options.intData('ToolbarQuantity', 0,
                                                optiondefaults.maxNumToolbars)
        iconSize = globalref.options.intData('ToolbarSize', 1, 128)
        for num in range(numToolbars):
            toolbar = self.addToolBar(_('Toolbar %d' % num))
            toolbar.setObjectName('tb%d' % num)
            toolbar.setIconSize(QtCore.QSize(iconSize, iconSize))
            self.toolbars.append(toolbar)
            commands = globalref.options.strData('Toolbar%d' % num, True)
            commandList = commands.split(',')
            for command in commandList:
                if command:
                    try:
                        toolbar.addAction(self.actions[command])
                    except KeyError:
                        pass
                else:
                    toolbar.addSeparator()

    def restoreToolbarPos(self):
        """Recall the positions of the toolbars"""
        toolbarPos = globalref.options.strData('ToolbarPosition', True)
        if toolbarPos:
            self.restoreState(base64.b64decode(toolbarPos))

    def setupMenus(self):
        """Add menu and toolbar items"""
        fileMenu = self.menuBar().addMenu(_('&File'))
        self.parentPopup = QtGui.QMenu(self)
        self.childPopup = QtGui.QMenu(self)

        self.selectReqdActGrp = QtGui.QActionGroup(self)
        self.notRootActGrp = QtGui.QActionGroup(self)
        self.selParentsActGrp = QtGui.QActionGroup(self)

        fileNewAct = QtGui.QAction(_('&New...'), self)
        fileNewAct.setToolTip(_('New File'))
        fileNewAct.setStatusTip(_('Start a new file'))
        fileMenu.addAction(fileNewAct)
        self.actions['FileNew'] = fileNewAct
        self.connect(fileNewAct, QtCore.SIGNAL('triggered()'), self.fileNew)

        fileOpenAct = QtGui.QAction(_('&Open...'), self)
        fileOpenAct.setToolTip(_('Open File'))
        fileOpenAct.setStatusTip(_('Open a file from disk'))
        fileMenu.addAction(fileOpenAct)
        self.actions['FileOpen'] = fileOpenAct
        self.connect(fileOpenAct, QtCore.SIGNAL('triggered()'), self.fileOpen)

        fileOpenSampleAct =  QtGui.QAction(_('Open Sa&mple...'), self)
        fileOpenSampleAct.setStatusTip(_('Open a sample template file'))
        fileMenu.addAction(fileOpenSampleAct)
        self.actions['FileOpenSample'] = fileOpenSampleAct
        self.connect(fileOpenSampleAct, QtCore.SIGNAL('triggered()'),
                     self.fileOpenSample)

        fileMenu.addSeparator()
        
        fileSaveAct = QtGui.QAction(_('&Save'), self)
        fileSaveAct.setToolTip(_('Save File'))
        fileSaveAct.setStatusTip(_('Save changes to the current file'))
        fileMenu.addAction(fileSaveAct)
        self.actions['FileSave'] = fileSaveAct
        self.connect(fileSaveAct, QtCore.SIGNAL('triggered()'), self.fileSave)

        fileSaveAsAct = QtGui.QAction(_('Save &As...'), self)
        fileSaveAsAct.setStatusTip(_('Save the file with a new name'))
        fileMenu.addAction(fileSaveAsAct)
        self.actions['FileSaveAs'] = fileSaveAsAct
        self.connect(fileSaveAsAct, QtCore.SIGNAL('triggered()'),
                     self.fileSaveAs)

        fileExportAct = QtGui.QAction(_('&Export...'), self)
        fileExportAct.setStatusTip(_('Export the file as html, as a table '\
                                     'or as text'))
        fileMenu.addAction(fileExportAct)
        self.actions['FileExport'] = fileExportAct
        self.connect(fileExportAct, QtCore.SIGNAL('triggered()'),
                     self.fileExport)

        fileMenu.addSeparator()

        filePrintOptAct = QtGui.QAction(_('P&rint Options...'), self)
        filePrintOptAct.setStatusTip(_('Set margins, page size and other '\
                                       'options for printing'))
        fileMenu.addAction(filePrintOptAct)
        self.actions['FilePrintOpt'] = filePrintOptAct
        self.connect(filePrintOptAct, QtCore.SIGNAL('triggered()'),
                     self.printData.filePrintOpt)

        filePrintPreviewAct = QtGui.QAction(_('Print Pre&view...'), self)
        filePrintPreviewAct.setStatusTip(_('Show a preview of printing '\
                                           'results'))
        fileMenu.addAction(filePrintPreviewAct)
        self.actions['FilePrintPreview'] = filePrintPreviewAct
        self.connect(filePrintPreviewAct, QtCore.SIGNAL('triggered()'),
                     self.printData.filePrintPreview)

        filePrintAct = QtGui.QAction(_('&Print...'), self)
        filePrintAct.setStatusTip(_('Print starting at the selected node'))
        fileMenu.addAction(filePrintAct)
        self.actions['FilePrint'] = filePrintAct
        self.connect(filePrintAct, QtCore.SIGNAL('triggered()'),
                     self.printData.filePrint)

        fileMenu.addSeparator()
        self.recentFileSep = fileMenu.addSeparator()

        fileQuitAct = QtGui.QAction(_('&Quit'), self)
        fileQuitAct.setStatusTip(_('Exit the application'))
        fileMenu.addAction(fileQuitAct)
        self.actions['FileQuit'] = fileQuitAct
        self.connect(fileQuitAct, QtCore.SIGNAL('triggered()'), self.close)

        editMenu = self.menuBar().addMenu(_('&Edit'))

        editUndoAct = QtGui.QAction(_('&Undo'), self)
        editUndoAct.setStatusTip(_('Undo the previous action'))
        editMenu.addAction(editUndoAct)
        self.actions['EditUndo'] = editUndoAct
        self.connect(editUndoAct, QtCore.SIGNAL('triggered()'), self.editUndo)

        editRedoAct = QtGui.QAction(_('&Redo'),  self)
        editRedoAct.setStatusTip(_('Redo the previous undo'))
        editMenu.addAction(editRedoAct)
        self.actions['EditRedo'] = editRedoAct
        self.connect(editRedoAct, QtCore.SIGNAL('triggered()'), self.editRedo)

        editMenu.addSeparator()
        editCutAct = QtGui.QAction(_('Cu&t'), self)
        editCutAct.setStatusTip(_('Cut the branch or text to the clipboard'))
        editMenu.addAction(editCutAct)
        self.parentPopup.addAction(editCutAct)
        self.childPopup.addAction(editCutAct)
        self.actions['EditCut'] = editCutAct
        self.connect(editCutAct, QtCore.SIGNAL('triggered()'), self.editCut)

        editCopyAct = QtGui.QAction(_('&Copy'), self)
        editCopyAct.setStatusTip(_('Copy the branch or text to the clipboard'))
        editMenu.addAction(editCopyAct)
        self.parentPopup.addAction(editCopyAct)
        self.childPopup.addAction(editCopyAct)
        self.actions['EditCopy'] = editCopyAct
        self.connect(editCopyAct, QtCore.SIGNAL('triggered()'), self.editCopy)

        editCopyTextAct = QtGui.QAction(_('Cop&y Title Text'), self)
        editCopyTextAct.setStatusTip(_('Copy node title text to the '\
                                       'clipboard'))
        editMenu.addAction(editCopyTextAct)
        self.actions['EditCopyText'] = editCopyTextAct
        self.connect(editCopyTextAct, QtCore.SIGNAL('triggered()'),
                     self.editCopyText)

        editPasteAct = QtGui.QAction(_('&Paste'), self)
        editPasteAct.setStatusTip(_('Paste nodes or text from the clipboard'))
        editMenu.addAction(editPasteAct)
        self.parentPopup.addAction(editPasteAct)
        self.childPopup.addAction(editPasteAct)
        self.actions['EditPaste'] = editPasteAct
        self.connect(editPasteAct, QtCore.SIGNAL('triggered()'),
                     self.editPaste)

        editPasteTextAct = QtGui.QAction(_('Pa&ste Text'), self)
        editPasteTextAct.setStatusTip(_('Paste text from the clipboard'))
        editMenu.addAction(editPasteTextAct)
        self.actions['EditPasteText'] = editPasteTextAct
        self.connect(editPasteTextAct, QtCore.SIGNAL('triggered()'),
                     self.editPasteText)

        editRenameAct = QtGui.QAction(_('Re&name'), self)
        editRenameAct.setStatusTip(_('Rename the current tree entry'))
        editMenu.addAction(editRenameAct)
        self.parentPopup.addAction(editRenameAct)
        self.childPopup.addAction(editRenameAct)
        self.actions['EditRename'] = editRenameAct
        self.connect(editRenameAct, QtCore.SIGNAL('triggered()'),
                     self.editRename)

        editMenu.addSeparator()
        self.parentPopup.addSeparator()
        self.childPopup.addSeparator()

        editInBeforeAct = QtGui.QAction(_('Insert Sibling &Before'),
                                        self.notRootActGrp)
        editInBeforeAct.setStatusTip(_('Insert new sibling before selection'))
        editMenu.addAction(editInBeforeAct)
        self.parentPopup.addAction(editInBeforeAct)
        self.childPopup.addAction(editInBeforeAct)
        self.actions['EditInsertBefore'] = editInBeforeAct
        self.connect(editInBeforeAct, QtCore.SIGNAL('triggered()'),
                     self.editInBefore)

        editInAfterAct = QtGui.QAction(_('Insert Sibling &After'),
                                       self.notRootActGrp)
        editInAfterAct.setStatusTip(_('Insert new sibling after selection'))
        editMenu.addAction(editInAfterAct)
        self.parentPopup.addAction(editInAfterAct)
        self.childPopup.addAction(editInAfterAct)
        self.actions['EditInsertAfter'] = editInAfterAct
        self.connect(editInAfterAct, QtCore.SIGNAL('triggered()'),
                     self.editInAfter)

        editAddChildAct = QtGui.QAction(_('Add C&hild'), self.selectReqdActGrp)
        editAddChildAct.setStatusTip(_('Add a new child to the selected '\
                                       'parent'))
        editMenu.addAction(editAddChildAct)
        self.parentPopup.addAction(editAddChildAct)
        self.childPopup.addAction(editAddChildAct)
        self.actions['EditAddChild'] = editAddChildAct
        self.connect(editAddChildAct, QtCore.SIGNAL('triggered()'),
                     self.editAddChild)

        editMenu.addSeparator()
        self.parentPopup.addSeparator()
        self.childPopup.addSeparator()

        editDeleteAct = QtGui.QAction(_('&Delete Node'), self.notRootActGrp)
        editDeleteAct.setStatusTip(_('Delete the selected nodes'))
        editMenu.addAction(editDeleteAct)
        self.parentPopup.addAction(editDeleteAct)
        self.childPopup.addAction(editDeleteAct)
        self.actions['EditDelete'] = editDeleteAct
        self.connect(editDeleteAct, QtCore.SIGNAL('triggered()'),
                     self.editDelete)

        editIndentAct = QtGui.QAction(_('&Indent Node'), self)
        editIndentAct.setStatusTip(_('Indent the selected nodes'))
        editMenu.addAction(editIndentAct)
        self.parentPopup.addAction(editIndentAct)
        self.childPopup.addAction(editIndentAct)
        self.actions['EditIndent'] = editIndentAct
        self.connect(editIndentAct, QtCore.SIGNAL('triggered()'),
                     self.editIndent)

        editUnindentAct = QtGui.QAction(_('Unind&ent Node'), self)
        editUnindentAct.setStatusTip(_('Unindent the selected nodes'))
        editMenu.addAction(editUnindentAct)
        self.parentPopup.addAction(editUnindentAct)
        self.childPopup.addAction(editUnindentAct)
        self.actions['EditUnindent'] = editUnindentAct
        self.connect(editUnindentAct, QtCore.SIGNAL('triggered()'),
                     self.editUnindent)

        editMenu.addSeparator()
        self.parentPopup.addSeparator()
        self.childPopup.addSeparator()

        editMoveUpAct = QtGui.QAction(_('&Move Up'), self)
        editMoveUpAct.setStatusTip(_('Move the selected nodes up'))
        editMenu.addAction(editMoveUpAct)
        self.parentPopup.addAction(editMoveUpAct)
        self.childPopup.addAction(editMoveUpAct)
        self.actions['EditMoveUp'] = editMoveUpAct
        self.connect(editMoveUpAct, QtCore.SIGNAL('triggered()'),
                     self.editMoveUp)

        editMoveDownAct = QtGui.QAction(_('M&ove Down'), self)
        editMoveDownAct.setStatusTip(_('Move the selected nodes down'))
        editMenu.addAction(editMoveDownAct)
        self.parentPopup.addAction(editMoveDownAct)
        self.childPopup.addAction(editMoveDownAct)
        self.actions['EditMoveDown'] = editMoveDownAct
        self.connect(editMoveDownAct, QtCore.SIGNAL('triggered()'),
                     self.editMoveDown)

        editMoveFirstAct = QtGui.QAction(_('Move &First'), self)
        editMoveFirstAct.setStatusTip(_('Move the selected nodes to be the '\
                                        'first children'))
        editMenu.addAction(editMoveFirstAct)
        self.actions['EditMoveFirst'] = editMoveFirstAct
        self.connect(editMoveFirstAct, QtCore.SIGNAL('triggered()'),
                     self.editMoveFirst)

        editMoveLastAct = QtGui.QAction(_('Move &Last'), self)
        editMoveLastAct.setStatusTip(_('Move the selected nodes to be the '\
                                       'last children'))
        editMenu.addAction(editMoveLastAct)
        self.actions['EditMoveLast'] = editMoveLastAct
        self.connect(editMoveLastAct, QtCore.SIGNAL('triggered()'),
                     self.editMoveLast)

        self.parentPopup.addSeparator()
        self.childPopup.addSeparator()

        viewMenu = self.menuBar().addMenu(_('&View'))

        viewPrevSelAct = QtGui.QAction(_('&Previous Selection'), self)
        viewPrevSelAct.setStatusTip(_('View the previous tree selection'))
        viewMenu.addAction(viewPrevSelAct)
        self.actions['ViewPreviousSelect'] = viewPrevSelAct
        self.connect(viewPrevSelAct, QtCore.SIGNAL('triggered()'),
                     self.viewPrevSelect)

        viewNextSelAct = QtGui.QAction(_('&Next Selection'), self)
        viewNextSelAct.setStatusTip(_('View the next tree selection'))
        viewMenu.addAction(viewNextSelAct)
        self.actions['ViewNextSelect'] = viewNextSelAct
        self.connect(viewNextSelAct, QtCore.SIGNAL('triggered()'),
                     self.viewNextSelect)

        viewMenu.addSeparator()

        viewLeftViewGrp = QtGui.QActionGroup(self)
        viewTreeAct = QtGui.QAction(_('Show &Tree View'), viewLeftViewGrp)
        viewTreeAct.setStatusTip(_('Show the tree in the right view'))
        viewTreeAct.setCheckable(True)
        viewMenu.addAction(viewTreeAct)
        self.actions['ViewTree'] = viewTreeAct

        viewFlatAct = QtGui.QAction(_('Show &Flat View'), viewLeftViewGrp)
        viewFlatAct.setStatusTip(_('Show a flat list in the right view'))
        viewFlatAct.setCheckable(True)
        viewMenu.addAction(viewFlatAct)
        self.actions['ViewFlat'] = viewFlatAct
        self.connect(viewLeftViewGrp, QtCore.SIGNAL('triggered(QAction*)'),
                     self.viewLeftSelect)

        viewMenu.addSeparator()

        viewRightViewGrp = QtGui.QActionGroup(self)
        viewOutAct = QtGui.QAction(_('Show Data &Output'), viewRightViewGrp)
        viewOutAct.setStatusTip(_('Show data output in right view'))
        viewOutAct.setCheckable(True)
        viewMenu.addAction(viewOutAct)
        self.actions['ViewDataOutput'] = viewOutAct

        viewEditAct = QtGui.QAction(_('Show Data &Editor'), viewRightViewGrp)
        viewEditAct.setStatusTip(_('Show data editor in right view'))
        viewEditAct.setCheckable(True)
        viewMenu.addAction(viewEditAct)
        self.actions['ViewDataEdit'] = viewEditAct

        viewTitleAct = QtGui.QAction(_('Show Title &List'), viewRightViewGrp)
        viewTitleAct.setStatusTip(_('Show title list in right view'))
        viewTitleAct.setCheckable(True)
        viewMenu.addAction(viewTitleAct)
        self.actions['ViewTitleList'] = viewTitleAct
        self.connect(viewRightViewGrp, QtCore.SIGNAL('triggered(QAction*)'),
                     self.viewRightSelect)

        viewMenu.addSeparator()

        viewChildAct = QtGui.QAction(_('Show &Child Pane'), self)
        viewChildAct.setStatusTip(_('Toggle splitting right-hand view to '\
                                    'show children'))
        viewChildAct.setCheckable(True)
        viewMenu.addAction(viewChildAct)
        self.actions['ViewShowChild'] = viewChildAct
        viewChildAct.setChecked(self.showItemChildren)
        self.connect(viewChildAct, QtCore.SIGNAL('toggled(bool)'),
                     self.viewChildren)

        viewDescendAct = QtGui.QAction(_('Show Output &Descendants'), self)
        viewDescendAct.setStatusTip(_('Toggle showing descendants in output '\
                                      'view'))
        viewDescendAct.setCheckable(True)
        viewMenu.addAction(viewDescendAct)
        self.actions['ViewShowDescend'] = viewDescendAct
        viewDescendAct.setChecked(self.dataOutSplit.widget(1).showDescendants)
        self.connect(viewDescendAct, QtCore.SIGNAL('toggled(bool)'),
                     self.viewDescendants)

        viewMenu.addSeparator()

        viewStatusAct = QtGui.QAction(_('Show Status Bar'), self)
        viewStatusAct.setStatusTip(_('Toggle the display of the status bar'))
        viewStatusAct.setCheckable(True)
        viewMenu.addAction(viewStatusAct)
        self.actions['ViewStatusBar'] = viewStatusAct
        viewStatusAct.setChecked(self.showStatusBar)
        self.connect(viewStatusAct, QtCore.SIGNAL('toggled(bool)'),
                     self.viewStatusBar)

        dataMenu = self.menuBar().addMenu(_('&Data'))

        self.typeSubMenu = QtGui.QMenu(self)
        dataMenu.addMenu(self.typeSubMenu)
        self.parentPopup.addMenu(self.typeSubMenu)
        self.childPopup.addMenu(self.typeSubMenu)
        self.connect(self.typeSubMenu, QtCore.SIGNAL('triggered(QAction*)'),
                     self.dataTypeChange)
        self.connect(self.typeSubMenu, QtCore.SIGNAL('aboutToShow()'),
                     self.loadTypeSubMenu)

        typeSubMenuShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                              self.treeView.showTypeMenu)
        self.shortcuts['DataSetItemType'] = typeSubMenuShortcut

        dataSetAct = QtGui.QAction(_('&Set Descendant Types...'),
                                   self.selParentsActGrp)
        dataSetAct.setCheckable(True)
        dataSetAct.setStatusTip(_('Set data type of selections and children'))
        dataMenu.addAction(dataSetAct)
        self.actions['DataSetDescendType'] = dataSetAct
        self.connect(dataSetAct, QtCore.SIGNAL('triggered(bool)'),
                     self.dataSet)

        dataConfigAct = QtGui.QAction(_('&Configure Data Types...'), self)
        dataConfigAct.setCheckable(True)
        dataConfigAct.\
                setStatusTip(_('Modify data types, fields & output lines'))
        dataMenu.addAction(dataConfigAct)
        self.actions['DataConfigType'] = dataConfigAct
        self.connect(dataConfigAct, QtCore.SIGNAL('triggered(bool)'),
                     self.dataConfig)

        dataCopyAct = QtGui.QAction(_('C&opy Types from File...'), self)
        dataCopyAct.setStatusTip(_('Copy the configuration from another '\
                                   'TreeLine file'))
        dataMenu.addAction(dataCopyAct)
        self.actions['DataCopyTypes'] = dataCopyAct
        self.connect(dataCopyAct, QtCore.SIGNAL('triggered()'),
                     self.dataCopyTypes)

        dataMenu.addSeparator()
        self.parentPopup.addSeparator()
        self.childPopup.addSeparator()

        dataSortAct = QtGui.QAction(_('Sort &Nodes...'), self)
        dataSortAct.setCheckable(True)
        dataSortAct.setStatusTip(_('Open the dialog for sorting nodes'))
        dataMenu.addAction(dataSortAct)
        self.parentPopup.addAction(dataSortAct)
        self.childPopup.addAction(dataSortAct)
        self.actions['DataSort'] = dataSortAct
        self.connect(dataSortAct, QtCore.SIGNAL('triggered(bool)'),
                     self.dataSort)

        dataEditFieldAct = QtGui.QAction(_('C&hange Selected Data...'),
                                         self.selectReqdActGrp)
        dataEditFieldAct.setStatusTip(_('Edit data values for all selected '\
                                        'nodes'))
        dataMenu.addAction(dataEditFieldAct)
        self.actions['DataChange'] = dataEditFieldAct
        self.connect(dataEditFieldAct, QtCore.SIGNAL('triggered()'),
                     self.dataEditField)

        dataNumberingAct = QtGui.QAction(_('N&umbering...'),
                                         self.selectReqdActGrp)
        dataNumberingAct.setStatusTip(_('Add numbering to a given data field'))
        dataMenu.addAction(dataNumberingAct)
        self.actions['DataNumber'] = dataNumberingAct
        self.connect(dataNumberingAct, QtCore.SIGNAL('triggered()'),
                     self.dataNumbering)

        dataMenu.addSeparator()

        dataFilterCondAct = QtGui.QAction(_('Con&ditional Filter...'), self)
        dataFilterCondAct.setStatusTip(_('Filter types with conditional'\
                                         ' rules'))
        dataMenu.addAction(dataFilterCondAct)
        self.actions['DataFilterCond'] = dataFilterCondAct
        self.connect(dataFilterCondAct, QtCore.SIGNAL('triggered()'),
                     self.dataFilterCond)

        dataFilterTextAct = QtGui.QAction(_('Te&xt Filter...'), self)
        dataFilterTextAct.setStatusTip(_('Filter with a text search string'))
        dataMenu.addAction(dataFilterTextAct)
        self.actions['DataFilterText'] = dataFilterTextAct
        self.connect(dataFilterTextAct, QtCore.SIGNAL('triggered()'),
                     self.dataFilterText)

        dataFilterClearAct = QtGui.QAction(_('Cl&ear Filtering'), self)
        dataFilterClearAct.setStatusTip(_('Clear current filtering'))
        dataMenu.addAction(dataFilterClearAct)
        self.actions['DataFilterClear'] = dataFilterClearAct
        self.connect(dataFilterClearAct, QtCore.SIGNAL('triggered()'),
                     self.dataFilterClear)

        dataMenu.addSeparator()

        dataAddCatAct = QtGui.QAction(_('&Add Category Level...'),
                                      self.selParentsActGrp)
        dataAddCatAct.setStatusTip(_('Insert category nodes above children'))
        dataMenu.addAction(dataAddCatAct)
        self.actions['DataCategoryAdd'] = dataAddCatAct
        self.connect(dataAddCatAct, QtCore.SIGNAL('triggered()'),
                     self.dataAddCat)

        dataFlatCatAct = QtGui.QAction(_('&Flatten by Category'),
                                       self.selParentsActGrp)
        dataFlatCatAct.setStatusTip(_('Collapse data by merging fields'))
        dataMenu.addAction(dataFlatCatAct)
        self.actions['DataCategoryFlat'] = dataFlatCatAct
        self.connect(dataFlatCatAct, QtCore.SIGNAL('triggered()'),
                     self.dataFlatCat)

        dataMenu.addSeparator()

        dataArrangeRefAct = QtGui.QAction(_('Arrange by &Reference...'),
                                          self.selParentsActGrp)
        dataArrangeRefAct.setStatusTip(_('Arrange data using parent '\
                                         'references'))
        dataMenu.addAction(dataArrangeRefAct)
        self.actions['DataRefArrange'] = dataArrangeRefAct
        self.connect(dataArrangeRefAct, QtCore.SIGNAL('triggered()'),
                     self.dataArrangeRef)

        dataFlatRefAct = QtGui.QAction(_('F&latten by Reference...'),
                                       self.selParentsActGrp)
        dataFlatRefAct.setStatusTip(_('Collapse data after adding references'))
        dataMenu.addAction(dataFlatRefAct)
        self.actions['DataRefFlat'] = dataFlatRefAct
        self.connect(dataFlatRefAct, QtCore.SIGNAL('triggered()'),
                     self.dataFlatRef)

        toolsMenu = self.menuBar().addMenu(_('&Tools'))

        toolsExpandAct = QtGui.QAction(_('&Expand Full Branch'),
                                       self.selParentsActGrp)
        toolsExpandAct.setStatusTip(_('Expand all children of selected node'))
        toolsMenu.addAction(toolsExpandAct)
        self.parentPopup.addAction(toolsExpandAct)
        self.actions['ToolsExpand'] = toolsExpandAct
        self.connect(toolsExpandAct, QtCore.SIGNAL('triggered()'),
                     self.toolsExpand)

        toolsCollapseAct = QtGui.QAction(_('&Collapse Full Branch'),
                                         self.selParentsActGrp)
        toolsCollapseAct.setStatusTip(_('Collapse all children of the '\
                                        'selected node'))
        toolsMenu.addAction(toolsCollapseAct)
        self.parentPopup.addAction(toolsCollapseAct)
        self.actions['ToolsCollapse'] = toolsCollapseAct
        self.connect(toolsCollapseAct, QtCore.SIGNAL('triggered()'),
                     self.toolsCollapse)

        toolsMenu.addSeparator()

        toolsFindAct = QtGui.QAction(_('&Find...'), self)
        toolsFindAct.setCheckable(True)
        toolsFindAct.setStatusTip(_('Find node matching text string'))
        toolsMenu.addAction(toolsFindAct)
        self.actions['ToolsFind'] = toolsFindAct
        self.connect(toolsFindAct, QtCore.SIGNAL('triggered(bool)'),
                     self.toolsFind)

        toolsSpellCheckAct = QtGui.QAction(_('&Spell Check'),
                                           self.selectReqdActGrp)
        toolsSpellCheckAct.setStatusTip(_('Spell check the tree\'s text data'))
        toolsMenu.addAction(toolsSpellCheckAct)
        self.actions['ToolsSpellCheck'] = toolsSpellCheckAct
        self.connect(toolsSpellCheckAct, QtCore.SIGNAL('triggered()'),
                     self.toolsSpellCheck)

        toolsRemXsltAct = QtGui.QAction(_('&Remove XSLT Ref'), self)
        toolsRemXsltAct.setStatusTip(_('Delete reference to XSLT export'))
        toolsMenu.addAction(toolsRemXsltAct)
        self.actions['ToolsRemXLST'] = toolsRemXsltAct
        self.connect(toolsRemXsltAct, QtCore.SIGNAL('triggered()'),
                     self.toolsRemXslt)

        toolsMenu.addSeparator()

        toolsGenOptAct = QtGui.QAction(_('&General Options...'), self)
        toolsGenOptAct.setStatusTip(_('Set user preferences for all files'))
        toolsMenu.addAction(toolsGenOptAct)
        self.actions['ToolsGenOptions'] = toolsGenOptAct
        self.connect(toolsGenOptAct, QtCore.SIGNAL('triggered()'),
                     self.toolsGenOpt)

        toolsFileOptAct = QtGui.QAction(_('File &Options...'), self)
        toolsFileOptAct.setStatusTip(_('Set preferences for this file'))
        toolsMenu.addAction(toolsFileOptAct)
        self.actions['ToolsFileOptions'] = toolsFileOptAct
        self.connect(toolsFileOptAct, QtCore.SIGNAL('triggered()'),
                     self.toolsFileOpt)

        fontMenu = toolsMenu.addMenu(_('Set Fo&nts'))

        toolsTreeFontAct = QtGui.QAction(_('&Tree Font...'), self)
        toolsTreeFontAct.setToolTip(_('Set Tree Font'))
        toolsTreeFontAct.setStatusTip(_('Sets font for tree & flat views'))
        fontMenu.addAction(toolsTreeFontAct)
        self.actions['ToolsTreeFont'] = toolsTreeFontAct
        self.connect(toolsTreeFontAct, QtCore.SIGNAL('triggered()'),
                     self.toolsTreeFont)


        toolsOutputFontAct = QtGui.QAction(_('&Data Output Font...'), self)
        toolsOutputFontAct.setToolTip(_('Set Data Output Font'))
        toolsOutputFontAct.setStatusTip(_('Sets font for output views'))
        fontMenu.addAction(toolsOutputFontAct)
        self.actions['ToolsOutputFont'] = toolsOutputFontAct
        self.connect(toolsOutputFontAct, QtCore.SIGNAL('triggered()'),
                     self.toolsOutputFont)

        toolsEditFontAct = QtGui.QAction(_('&Editor Font...'), self)
        toolsEditFontAct.setToolTip(_('Set Editor Font'))
        toolsEditFontAct.setStatusTip(_('Sets font for edit views'))
        fontMenu.addAction(toolsEditFontAct)
        self.actions['ToolsEditFont'] = toolsEditFontAct
        self.connect(toolsEditFontAct, QtCore.SIGNAL('triggered()'),
                     self.toolsEditFont)

        toolsShortcutAct = QtGui.QAction(_('Set &Keyboard Shortcuts...'), self)
        toolsShortcutAct.setStatusTip(_('Customize keyboard commands'))
        toolsMenu.addAction(toolsShortcutAct)
        self.actions['ToolsShortcuts'] = toolsShortcutAct
        self.connect(toolsShortcutAct, QtCore.SIGNAL('triggered()'),
                     self.toolsShortcuts)

        toolsToolbarAct = QtGui.QAction(_('Custo&mize Toolbars...'), self)
        toolsToolbarAct.setStatusTip(_('Customize toolbar buttons'))
        toolsMenu.addAction(toolsToolbarAct)
        self.actions['ToolsCustomToolbar'] = toolsToolbarAct
        self.connect(toolsToolbarAct, QtCore.SIGNAL('triggered()'),
                     self.toolsCustomToolbar)

        toolsMenu.addSeparator()

        toolsDfltColorAct = QtGui.QAction(_('&Use Default System Colors'),
                                          self)
        toolsDfltColorAct.setStatusTip(_('Use system colors, not custom'))
        toolsDfltColorAct.setCheckable(True)
        toolsMenu.addAction(toolsDfltColorAct)
        self.actions['ToolsDefaultColor'] = toolsDfltColorAct
        toolsDfltColorAct.setChecked(globalref.options.
                                     boolData('UseDefaultColors'))
        self.connect(toolsDfltColorAct, QtCore.SIGNAL('toggled(bool)'),
                     self.toolsDefaultColor)

        toolsBkColorAct = QtGui.QAction(_('&Background Color...'), self)
        toolsBkColorAct.setStatusTip(_('Set view background color'))
        toolsMenu.addAction(toolsBkColorAct)
        self.actions['ToolsBackColor'] = toolsBkColorAct
        self.connect(toolsBkColorAct, QtCore.SIGNAL('triggered()'),
                     self.toolsBkColor)

        toolsTxtColorAct = QtGui.QAction(_('&Text Color...'), self)
        toolsTxtColorAct.setStatusTip(_('Set view text color'))
        toolsMenu.addAction(toolsTxtColorAct)
        self.actions['ToolsTextColor'] = toolsTxtColorAct
        self.connect(toolsTxtColorAct, QtCore.SIGNAL('triggered()'),
                     self.toolsTxtColor)

        self.winMenu = self.menuBar().addMenu(_('&Window'))

        winNewAct = QtGui.QAction(_('&New Window'), self)
        winNewAct.setStatusTip(_('Open a new window viewing the same file'))
        self.winMenu.addAction(winNewAct)
        self.actions['WinNewWindow'] = winNewAct
        self.connect(winNewAct, QtCore.SIGNAL('triggered()'),
                     globalref.treeControl.newWindow)

        winCloseAct = QtGui.QAction(_('&Close Window'), self)
        winCloseAct.setStatusTip(_('Close the current window'))
        self.winMenu.addAction(winCloseAct)
        self.actions['WinCloseWindow'] = winCloseAct
        self.connect(winCloseAct, QtCore.SIGNAL('triggered()'),
                     globalref.treeControl.closeWindow)

        winUpdateAct = QtGui.QAction(_('&Update Other Window'), self)
        winUpdateAct.setStatusTip(_('Update the contents of an alternate '
                                    'window'))
        self.winMenu.addAction(winUpdateAct)
        self.actions['WinUpdateWindow'] = winUpdateAct
        self.connect(winUpdateAct, QtCore.SIGNAL('triggered()'),
                     globalref.treeControl.forceUpdateWindow)

        self.winMenu.addSeparator()

        helpMenu = self.menuBar().addMenu(_('&Help'))

        helpContentsAct = QtGui.QAction(_('&Help Contents'), self)
        helpContentsAct.setStatusTip(_('View information about using TreeLine'))
        helpMenu.addAction(helpContentsAct)
        self.actions['HelpContents'] = helpContentsAct
        self.connect(helpContentsAct, QtCore.SIGNAL('triggered()'),
                     self.helpContents)

        helpReadMeAct = QtGui.QAction(_('&View Full ReadMe'), self)
        helpReadMeAct.setStatusTip(_('View the entire ReadMe file'))
        helpMenu.addAction(helpReadMeAct)
        self.actions['HelpFullReadMe'] = helpReadMeAct
        self.connect(helpReadMeAct, QtCore.SIGNAL('triggered()'),
                     self.helpReadMe)

        helpAboutAct = QtGui.QAction(_('&About TreeLine'), self)
        helpAboutAct.setStatusTip(_('About this program'))
        helpMenu.addAction(helpAboutAct)
        self.actions['HelpAbout'] = helpAboutAct
        self.connect(helpAboutAct, QtCore.SIGNAL('triggered()'),
                     self.helpAbout)

        helpPluginAct = QtGui.QAction(_('About &Plugins'), self)
        helpPluginAct.setStatusTip(_('Show loaded plugin modules'))
        helpMenu.addAction(helpPluginAct)
        self.actions['HelpPlugin'] = helpPluginAct
        self.connect(helpPluginAct, QtCore.SIGNAL('triggered()'),
                     self.helpPlugin)

        self.pulldownMenuList = [fileMenu, editMenu, viewMenu, dataMenu,
                                 toolsMenu, helpMenu]

        self.tagSubMenu = QtGui.QMenu(_('&Add Font Tags'), self)
        self.addTagGroup = QtGui.QActionGroup(self)
        for name, text, tags in TreeMainWin.tagMenuEntries:
            action = QtGui.QAction(text, self.addTagGroup)
            self.tagSubMenu.addAction(action)
            self.addAction(action)
            self.actions[name] = action
            self.connect(action, QtCore.SIGNAL('triggered()'),
                         self.addTextTag)

        treeFocusShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                            self.focusLeftView)
        self.shortcuts['TreeFocusView'] = treeFocusShortcut

        treeSelectPrevShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                                 self.treeSelectPrev)
        self.shortcuts['TreeSelectPrev'] = treeSelectPrevShortcut

        treeSelectNextShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                                 self.treeSelectNext)
        self.shortcuts['TreeSelectNext'] = treeSelectNextShortcut

        treePrevSiblingShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                                  self.treePrevSibling)
        self.shortcuts['TreePrevSibling'] = treePrevSiblingShortcut

        treeNextSiblingShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                                  self.treeNextSibling)
        self.shortcuts['TreeNextSibling'] = treeNextSiblingShortcut

        treeSelectParentShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                                   self.treeSelectParent)
        self.shortcuts['TreeSelectParent'] = treeSelectParentShortcut

        treeOpenItemShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                               self.treeOpenItem)
        self.shortcuts['TreeOpenItem'] = treeOpenItemShortcut

        treeCloseItemShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                                self.treeCloseItem)
        self.shortcuts['TreeCloseItem'] = treeCloseItemShortcut

        treePageUpShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                             self.treePageUp)
        self.shortcuts['TreePageUp'] = treePageUpShortcut

        treePageDownShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                               self.treePageDown)
        self.shortcuts['TreePageDown'] = treePageDownShortcut

        treeIncremSearchShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                                   self.treeIncremSearch)
        self.shortcuts['TreeIncremSearch'] = treeIncremSearchShortcut

        treeIncremNextShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                                 self.treeIncremNext)
        self.shortcuts['TreeIncremNext'] = treeIncremNextShortcut

        treeIncremPrevShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                                 self.treeIncremPrev)
        self.shortcuts['TreeIncremPrev'] = treeIncremPrevShortcut

        rightChildUpShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                               self.rightChildPageUp)
        self.shortcuts['RightChildPageUp'] = rightChildUpShortcut

        rightChildDownShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                                 self.rightChildPageDown)
        self.shortcuts['RightChildPageDown'] = rightChildDownShortcut

        rightParentUpShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                                self.rightParentPageUp)
        self.shortcuts['RightParentPageUp'] = rightParentUpShortcut

        rightParentDownShortcut = QtGui.QShortcut(QtGui.QKeySequence(), self,
                                                  self.rightParentPageDown)
        self.shortcuts['RightParentPageDown'] = rightParentDownShortcut
