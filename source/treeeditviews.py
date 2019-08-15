#!/usr/bin/env python

#****************************************************************************
# treeeditviews.py, provides classes for the data edit views
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
import tempfile
from PyQt4 import QtCore, QtGui
import configdialog
import treemainwin
import optiondefaults
import globalref


class DataEditLine(QtGui.QTextEdit):
    """Line editor within data edit view"""
    fileBrowsePath = ''
    def __init__(self, field, item, labelRef, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.field = field
        self.item = item
        self.labelRef = labelRef
        self.sizeCache = None
        self.setAcceptRichText(False)
        self.setTabChangesFocus(True)
        self.setWordWrapMode(QtGui.QTextOption.WordWrap)
        self.labelFont = QtGui.QFont(labelRef.font())
        self.labelBoldFont = QtGui.QFont(self.labelFont)
        self.labelBoldFont.setBold(True)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        editText, ok = self.field.editText(item)
        if not ok:
            self.labelRef.setFont(self.labelBoldFont)
        self.setPlainText(editText)
        try:
            self.document().adjustSize()  # fix scroll bar overlapping
        except AttributeError:
            pass   # not in Qt < 4.2
        self.connect(self, QtCore.SIGNAL('textChanged()'), self.readChange)

    def readChange(self):
        """Update variable from edit contents"""
        text = unicode(self.toPlainText()).strip()
        editText, ok = self.field.editText(self.item)
        if text != editText:
            globalref.docRef.undoStore.addDataUndo(self.item, True)
            newText, ok = self.field.storedText(text)
            self.item.data[self.field.name] = newText
            self.labelRef.setFont(ok and self.labelFont or self.labelBoldFont)
            globalref.docRef.modified = True
            self.sizeCache = None
            self.emit(QtCore.SIGNAL('entryChanged'))
            if globalref.pluginInterface:
                globalref.pluginInterface.execCallback(globalref.
                                                       pluginInterface.
                                                       dataChangeCallbacks,
                                                       self.item, [self.field])

    def fileBrowse(self):
        """Open file browser to set contents"""
        dfltPath = unicode(self.toPlainText()).strip()
        if not dfltPath or not os.path.exists(dfltPath):
            dfltPath = DataEditLine.fileBrowsePath
            if not dfltPath or not os.path.exists(dfltPath):
                dfltPath = os.path.dirname(globalref.docRef.fileName)
        fileName = unicode(QtGui.QFileDialog.getOpenFileName(self,
                                                    _('Browse for file name'),
                                                    dfltPath,
                                                    '%s (*)' % _('All Files')))
        if fileName:
            DataEditLine.fileBrowsePath = os.path.dirname(fileName)
            if ' ' in fileName and self.field.typeName == u'ExecuteLink':
                fileName = "'%s'" % fileName
            self.setPlainText(fileName)

    def showExtEditor(self):
        """Start external editor for the text in this edit box"""
        tmpPathName = self.writeTmpFile()
        if tmpPathName and self.findExtEditor(tmpPathName):
            try:
                f = file(tmpPathName, 'r')
                self.setPlainText(f.read().strip().decode('utf-8'))
                f.close()
            except IOError:
                pass
        try:
            os.remove(tmpPathName)
        except OSError:
            print 'Could not remove tmp file %s' % tmpPathName.\
                    encode(globalref.localTextEncoding)

    def writeTmpFile(self):
        """Write tmp file with editor contents, return successful path"""
        fd, fullPath = tempfile.mkstemp(prefix='tl_', text=True)
        try:
            f = os.fdopen(fd, 'w')
            f.write(unicode(self.toPlainText()).strip().encode('utf-8'))
            f.close()
        except IOError:
            return ''
        return fullPath

    def findExtEditor(self, argument):
        """Find and launch external editor, look in option text,
           then EDITOR variable, then prompt for new option text,
           return True on success"""
        paths = [globalref.options.strData('ExtEditorPath', True),
                 os.environ.get('EDITOR', '')]
        for path in paths:
            if path and not sys.platform.startswith('win'):
                if os.system("%s '%s'" % (path, argument)) == 0:
                    return True
            elif path:
                try:  # spawnl for Win - os.system return value not relaible 
                    if os.spawnl(os.P_WAIT, path, os.path.basename(path),
                                 argument) <= 0:
                        return True
                except OSError:
                    pass
        ans = QtGui.QMessageBox.warning(self, _('External Editor'),
                                        _('Could not find an external '\
                                          'editor.\nManually locate?\n'\
                                          '(or set EDITOR env variable)'),
                                        _('&Browse'), _('&Cancel'), '', 0, 1)
        if ans == 0:
            filter = sys.platform.startswith('win') and \
                                  '%s (*.exe)' % _('Programs') \
                                  or '%s (*)' % _('All Files')
            path = unicode(QtGui.QFileDialog.getOpenFileName(self,
                                                             _('Locate extern'\
                                                               'al editor'),
                                                             '', filter))
            if path:
                globalref.options.changeData('ExtEditorPath', path, True)
                globalref.options.writeChanges()
                return self.findExtEditor(argument)
        return False

    def copyAvail(self):
        """Return True if there is selected text"""
        return self.textCursor().hasSelection()

    def insertFromMimeData(self, mimeData):
        """Override to paste properly from copied node"""
        try:
            text = unicode(mimeData.text())
        except UnicodeError:
            return
        item = globalref.docRef.readXmlString(text)
        if item:
            text = item.title()
        self.insertPlainText(text)

    def addHtmlTag(self, openTag, closeTag):
        """Add HTML tag based on popup menu"""
        cursor = self.textCursor()
        text = unicode(cursor.selectedText())
        selectStart = cursor.selectionStart() + len(openTag)
        selectEnd = cursor.selectionEnd() + len(openTag)
        cursor.insertText(u'%s%s%s' % (openTag, text, closeTag))
        cursor.setPosition(selectStart)
        cursor.setPosition(selectEnd, QtGui.QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

    def addHtmlLinkTag(self, ref, text):
        """Add HTML inline internal link with given text"""
        self.insertPlainText('<a href="#%s">%s</a>' % (ref, text))

    def contextMenuEvent(self, event):
        """Override popup menu to add tag submenu, ext editor and config
           modification menu items"""
        menu = self.createStandardContextMenu()
        firstAction = menu.actions()[0]
        extEditAct = QtGui.QAction(_('&External Editor...'), self)
        menu.insertAction(firstAction, extEditAct)
        self.connect(extEditAct, QtCore.SIGNAL('triggered()'),
                     self.showExtEditor)
        menu.insertMenu(firstAction, globalref.mainWin.tagSubMenu)
        addLinkAct = QtGui.QAction(_('&Add Internal Link...'), self)
        menu.insertAction(firstAction, addLinkAct)
        self.connect(addLinkAct, QtCore.SIGNAL('triggered()'),
                     globalref.mainWin.inlineLinkTagPrompt)
        menu.insertSeparator(firstAction)
        typeConfigAct = QtGui.QAction(_('&Modify Type Config...'), self)
        menu.insertAction(firstAction, typeConfigAct)
        self.connect(typeConfigAct, QtCore.SIGNAL('triggered()'),
                     self.parent().modifyTypeConfig)
        fieldConfigAct = QtGui.QAction(_('Modify &Field Config...'), self)
        menu.insertAction(firstAction, fieldConfigAct)
        self.connect(fieldConfigAct, QtCore.SIGNAL('triggered()'),
                     self.parent().modifyFieldConfig)
        menu.insertSeparator(firstAction)
        menu.exec_(event.globalPos())

    def sizeHint(self):
        """Return preferred size"""
        width = self.parent().newEditLineWidth()
        if self.field.hasFileBrowse:
            width -= DataEditGroup.browseButtonWidth + \
                     self.parent().layout().spacing()
        if self.sizeCache and self.sizeCache.width() == width:
            return self.sizeCache
        fontMetrics = QtGui.QFontMetrics(self.font())
        lineHeight = fontMetrics.lineSpacing()
        if self.field.numLines > 1:
            height = self.field.numLines * lineHeight + \
                     DataEditGroup.vertMargins
        else:
            maxNumLines = globalref.options.intData('MaxEditLines', 1,
                                                    optiondefaults.maxNumLines)
            textRect = fontMetrics.boundingRect(0, 0, width - \
                                                DataEditGroup.horizMargins,
                                                100000, QtCore.Qt.TextWordWrap,
                                                self.toPlainText())
            height = min(textRect.height(), maxNumLines * lineHeight) \
                     + DataEditGroup.vertMargins
        self.sizeCache = QtCore.QSize(width, height)
        return self.sizeCache

    def minimumSizeHint(self):
        return QtCore.QSize(0, 0)

    def focusInEvent(self, event):
        """Signal focus to update html tag command availability"""
        self.emit(QtCore.SIGNAL('focusChange'))
        QtGui.QTextEdit.focusInEvent(self, event)

    def focusOutEvent(self, event):
        """Signal focus to update html tag command availability"""
        self.emit(QtCore.SIGNAL('focusChange'))
        QtGui.QTextEdit.focusOutEvent(self, event)


class DataEditCombo(QtGui.QComboBox):
    """Combo box for fields with choices, 
       fills with options when about to sow list"""
    def __init__(self, field, item, labelRef, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        self.field = field
        self.item = item
        self.labelRef = labelRef
        self.listLoaded = False
        self.setEditable(True)
        self.setInsertPolicy(QtGui.QComboBox.NoInsert)
        self.setAutoCompletion(True)

        self.listView = QtGui.QTreeWidget()
        self.listView.setColumnCount(2)
        self.listView.header().hide()
        self.listView.setRootIsDecorated(False)
        self.listView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setModel(self.listView.model())
        self.setView(self.listView)
        self.setModelColumn(0)

        self.labelFont = QtGui.QFont(labelRef.font())
        self.labelBoldFont = QtGui.QFont(self.labelFont)
        self.labelBoldFont.setBold(True)
        editText, ok = self.field.editText(item)
        if not ok:
            self.labelRef.setFont(self.labelBoldFont)
        self.setEditText(editText)
        self.connect(self, QtCore.SIGNAL('editTextChanged(const QString&)'),
                     self.readChange)

    def readChange(self, text):
        """Update variable from edit contents"""
        # text = unicode(text).strip()   # bad results with autocomplete
        text = unicode(self.lineEdit().text())
        editText, ok = self.field.editText(self.item)
        if text != editText:
            globalref.docRef.undoStore.addDataUndo(self.item, True)
            newText, ok = self.field.storedText(text)
            self.item.data[self.field.name] = newText
            self.labelRef.setFont(ok and self.labelFont or self.labelBoldFont)
            globalref.docRef.modified = True
            self.emit(QtCore.SIGNAL('entryChanged'))
            if globalref.pluginInterface:
                globalref.pluginInterface.execCallback(globalref.
                                                       pluginInterface.
                                                       dataChangeCallbacks,
                                                       self.item, [self.field])

    def loadListBox(self):
        """Populate list box for combo"""
        text = unicode(self.lineEdit().text())
        self.blockSignals(True)
        self.listView.clear()
        if self.field.autoAddChoices:
            self.field.addChoice(text, True)
        strList = self.field.getEditChoices(text)
        item = None
        for choice, annot in strList:
            if choice == None:   # separator
                pass  # separator not implemented
            else:
                QtGui.QTreeWidgetItem(self.listView, [choice, annot])
        try:
            choices = [choice for (choice, annot) in strList]
            i = choices.index(text)
            self.setCurrentIndex(i)
        except ValueError:
            editText, ok = self.field.storedText(text)
            if ok and editText:
                # add missing item if valid
                item = QtGui.QTreeWidgetItem(None, [text, '(current)'])
                self.listView.insertTopLevelItem(0, item)
                self.setCurrentIndex(0)
            else:
                self.setEditText(text)
        self.listView.resizeColumnToContents(0)
        self.blockSignals(False)
        self.listLoaded = True

    def showPopup(self):
        """Load combo box before showing it"""
        self.loadListBox()
        QtGui.QComboBox.showPopup(self)

    def copyAvail(self):
        """Return True if there is selected text"""
        return self.lineEdit().hasSelectedText()

    def cut(self):
        """Pass cut command to lineEdit"""
        self.lineEdit().cut()

    def copy(self):
        """Pass copy command to lineEdit"""
        self.lineEdit().copy()

    def paste(self):
        """Paste text from clipboard"""
        try:
            text = unicode(QtGui.QApplication.clipboard().text())
        except UnicodeError:
            return
        item = globalref.docRef.readXmlString(text)
        if item:
            text = item.title()
        self.lineEdit().insert(text)

    def contextMenuEvent(self, event):
        """Override popup menu to add config modification menu items"""
        menu = self.lineEdit().createStandardContextMenu()
        firstAction = menu.actions()[0]
        typeConfigAct = QtGui.QAction(_('&Modify Type Config...'), self)
        menu.insertAction(firstAction, typeConfigAct)
        self.connect(typeConfigAct, QtCore.SIGNAL('triggered()'),
                     self.parent().modifyTypeConfig)
        fieldConfigAct = QtGui.QAction(_('Modify &Field Config...'), self)
        menu.insertAction(firstAction, fieldConfigAct)
        self.connect(fieldConfigAct, QtCore.SIGNAL('triggered()'),
                     self.parent().modifyFieldConfig)
        menu.insertSeparator(firstAction)
        menu.exec_(event.globalPos())

    def sizeHint(self):
        """Return preferred size"""
        return QtCore.QSize(self.parent().newEditLineWidth(),
                            QtGui.QFontMetrics(self.font()).lineSpacing() +
                            DataEditGroup.vertMargins)

    def focusInEvent(self, event):
        """Update list box to get autocomplete to work"""
        if not self.listLoaded:
            self.loadListBox()
        QtGui.QComboBox.focusInEvent(self, event)

    def focusOutEvent(self, event):
        """Update auto choices on leaving the widget"""
        if self.field.autoAddChoices:
            self.field.addChoice(unicode(self.lineEdit().text()), True)
        QtGui.QComboBox.focusOutEvent(self, event)


class DataEditGroup(QtGui.QGroupBox):
    """Collection of editors for one item"""
    browseButtonWidth = 40
    horizMargins = 20
    vertMargins = 14
    def __init__(self, item, viewRef, parent=None):
        QtGui.QGroupBox.__init__(self, item.formatName, parent)
        self.item = item
        self.viewRef = viewRef
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        layout = QtGui.QGridLayout(self)
        layout.setColumnStretch(1, 1)
        self.titleLabel = QtGui.QLabel(self.item.title())
        self.titleLabel.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.titleLabel.setTextFormat(QtCore.Qt.PlainText)
        layout.addWidget(self.titleLabel, 0, 0, 1, 3)
        fieldList = [field for field in item.nodeFormat().fieldList if
                     not field.hidden]
        self.maxLabelWidth = 0
        fontMetrics = QtGui.QFontMetrics(self.titleLabel.font())
        labels = []
        for row, field in enumerate(fieldList):
            labels.append(QtGui.QLabel(field.labelName()))
            layout.addWidget(labels[-1], row + 2, 0)
            self.maxLabelWidth = max(self.maxLabelWidth,
                                     fontMetrics.width(labels[-1].text()))
        for row, field in enumerate(fieldList):
            if field.hasEditChoices:
                line = DataEditCombo(field, item, labels[row], self)
                layout.addWidget(line, row + 2, 1, 1, 2)
            elif field.hasFileBrowse:
                line = DataEditLine(field, item, labels[row], self)
                layout.addWidget(line, row + 2, 1)
                browseButton = QtGui.QPushButton('...', self)
                browseButton.setFixedWidth(40)
                self.connect(browseButton, QtCore.SIGNAL('clicked()'),
                             line.fileBrowse)
                layout.addWidget(browseButton, row + 2, 2)
            else:
                line = DataEditLine(field, item, labels[row], self)
                layout.addWidget(line, row + 2, 1, 1, 2)
                self.connect(line, QtCore.SIGNAL('focusChange'),
                             globalref.mainWin.updateAddTagAvail)
            self.connect(line, QtCore.SIGNAL('entryChanged'),
                         self.checkTitleChange)

    def checkTitleChange(self):
        """Update item title based on signal"""
        globalref.updateViewItem(self.item)
        self.setTitle(self.item.formatName)
        self.titleLabel.setText(self.item.title())
        globalref.updateViewMenuStat()

    def newEditLineWidth(self):
        """Return width remaining for edit widgets"""
        return max(self.viewRef.width() - self.maxLabelWidth - 80, 100)

    def modifyTypeConfig(self):
        """Bring up type config dialog with this data type"""
        globalref.mainWin.dataConfig(True)
        configdialog.ConfigDialog.currentType = self.item.formatName
        configdialog.ConfigDialog.currentField = globalref.docRef.\
                                       treeFormats[self.item.formatName].\
                                       fieldList[0].name
        treemainwin.TreeMainWin.configDlg.tabs.setCurrentIndex(1)
        treemainwin.TreeMainWin.configDlg.updatePage()

    def modifyFieldConfig(self):
        """Bring up type config dialog with the caller's field"""
        field = self.sender().parent().field.name
        globalref.mainWin.dataConfig(True)
        configdialog.ConfigDialog.currentType = self.item.formatName
        configdialog.ConfigDialog.currentField = field
        treemainwin.TreeMainWin.configDlg.tabs.setCurrentIndex(3)
        treemainwin.TreeMainWin.configDlg.updatePage()

class DataEditScrollView(QtGui.QScrollArea):
    """Right pane view to edit database info"""
    def __init__(self, parent=None):
        QtGui.QScrollArea.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.fullView = QtGui.QWidget()
        self.fullLayout = QtGui.QVBoxLayout(self.fullView)
        self.setWidget(self.fullView)
        self.dataGroups = []

    def replaceGroups(self, items, heightLimit=0, resetScroll=True):
        """Replace contents with selected item data list,
           stop adding when heightLimit is reached,
           return number of items added"""
        if resetScroll:
            self.horizontalScrollBar().setValue(0)
            self.verticalScrollBar().setValue(0)
        for group in self.dataGroups:
            group.close()
        self.dataGroups = []
        return self.addItems(items, heightLimit)

    def addItems(self, items, heightLimit=0):
        """Adds given items to the view,
           stop adding when heightLimit is reached,
           return number of items added"""
        viewHeightUsed = 0
        numItemsCreated = 0
        for item in items:
            group = DataEditGroup(item, self)
            viewHeightUsed += group.sizeHint().height() + \
                              self.fullLayout.spacing()
            if heightLimit and viewHeightUsed > heightLimit:
                if numItemsCreated == 0:
                    self.dataGroups.append(group)
                    self.fullLayout.addWidget(group)
                    numItemsCreated += 1
                break
            self.dataGroups.append(group)
            self.fullLayout.addWidget(group)
            numItemsCreated += 1
        self.fullView.adjustSize()
        return numItemsCreated

    def invalidateLayouts(self):
        """Invalidate layouts for resize"""
        for group in self.dataGroups:
            group.layout().invalidate()
        self.fullLayout.invalidate()


class DataEditView(QtGui.QWidget):
    """Right pane parent view to edit database info"""
    def __init__(self, showChildren=True, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.showChildren = showChildren
        self.oldViewHeight = 0
        self.allItems = []
        self.shownRanges = []
        topLayout = QtGui.QVBoxLayout(self)
        topLayout.setSpacing(0)
        topLayout.setMargin(0)
        self.controller = QtGui.QWidget()
        topLayout.addWidget(self.controller)
        controlLayout = QtGui.QHBoxLayout(self.controller)
        controlLayout.setMargin(0)
        self.controlLabel = QtGui.QLabel()
        controlLayout.addWidget(self.controlLabel)
        self.backButton = QtGui.QPushButton('<<')
        controlLayout.addWidget(self.backButton)
        buttonSize = self.backButton.fontMetrics().\
                     size(QtCore.Qt.TextShowMnemonic, _('All')) + \
                     QtCore.QSize(16, 4)
        self.backButton.setMaximumSize(buttonSize)
        self.backButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.connect(self.backButton, QtCore.SIGNAL('clicked()'),
                     self.viewBack)
        self.forwardButton = QtGui.QPushButton('>>')
        controlLayout.addWidget(self.forwardButton)
        self.forwardButton.setMaximumSize(buttonSize)
        self.forwardButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.connect(self.forwardButton, QtCore.SIGNAL('clicked()'),
                     self.viewForward)
        allButton = QtGui.QPushButton(_('All'))
        controlLayout.addWidget(allButton)
        allButton.setMaximumSize(buttonSize)
        allButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.connect(allButton, QtCore.SIGNAL('clicked()'), self.viewAll)
        self.scrollView = DataEditScrollView()
        topLayout.addWidget(self.scrollView)

    def updateView(self):
        """Replace contents with selected item data list"""
        origFirstItem = self.allItems[:1]
        self.allItems = []
        if self.showChildren and len(globalref.docRef.selection) == 1:
            self.allItems = globalref.docRef.selection[0].childList
        elif not self.showChildren:
            self.allItems = globalref.docRef.selection
        self.hide()
        resetScroll = self.allItems[:1] != origFirstItem
        numGroups = self.scrollView.replaceGroups(self.allItems,
                                                  self.availableHeight(),
                                                  resetScroll)
        self.shownRanges = [(0, numGroups)]
        self.updateControl()
        self.show()

    def updateControl(self):
        """Udate control visibility, label and button availability"""
        start, end = self.shownRanges[-1]
        if start == 0 and end == len(self.allItems):
            self.controller.hide()
            return
        if end == start + 1:
            text = _('Node %(node_num)d of %(total_num)d') % \
                   {'node_num': end, 'total_num': len(self.allItems)}
        else:
            text = _('Nodes %(start_node)d-%(end_node)d of %(total_num)d') \
                    % {'start_node': start + 1, 'end_node': end,
                       'total_num': len(self.allItems)}
        self.controlLabel.setText(text)
        self.backButton.setEnabled(len(self.shownRanges) > 1)
        self.forwardButton.setEnabled(end < len(self.allItems))
        self.controller.show()

    def viewBack(self):
        """View previous set of groups"""
        self.shownRanges = self.shownRanges[:-1]
        start, end = self.shownRanges[-1]
        self.hide()
        self.scrollView.replaceGroups(self.allItems[start:end])
        self.updateControl()
        self.show()
        self.scrollView.dataGroups[0].setFocus(QtCore.Qt.TabFocusReason)

    def viewForward(self):
        """View next set of groups"""
        start = self.shownRanges[-1][1]
        self.hide()
        numGroups = self.scrollView.replaceGroups(self.allItems[start:],
                                                  self.availableHeight())
        self.shownRanges.append((start, start + numGroups))
        self.updateControl()
        self.show()
        self.scrollView.dataGroups[0].setFocus(QtCore.Qt.TabFocusReason)

    def viewAll(self):
        """View all groups"""
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.hide()
        if len(self.shownRanges) == 1:
            start = self.shownRanges[-1][1]
            self.scrollView.addItems(self.allItems[start:])
        else:
            self.scrollView.replaceGroups(self.allItems)
        self.shownRanges = [(0, len(self.allItems))]
        self.updateControl()
        self.show()
        globalref.focusTree()
        QtGui.QApplication.restoreOverrideCursor()

    def availableHeight(self):
        """Return screen height times number of pages"""
        numPages = globalref.options.intData('EditorPages', 0, 999)
        return (self.height() - self.controller.sizeHint().height()) * \
               numPages

    def copyAvail(self):
        """Return 1 if there is selected text"""
        if hasattr(self.focusWidget(), 'copyAvail'):
            return self.focusWidget().copyAvail()
        return 0

    def copy(self):
        """Copy selections to clipboard"""
        if hasattr(self.focusWidget(), 'copy'):
            self.focusWidget().copy()

    def cut(self):
        """Cut selections to clipboard"""
        if hasattr(self.focusWidget(), 'cut'):
            self.focusWidget().cut()

    def paste(self):
        """Paste text given in param"""
        if hasattr(self.focusWidget(), 'paste'):
            self.focusWidget().paste()

    def scrollPage(self, numPages=1):
        """Scrolls down by numPages (negative for up)
           leaving a one-line overlap"""
        delta = self.scrollView.maximumViewportSize().height()
        if delta == 0:
            return
        fontSize = self.fontMetrics().height()
        if delta > fontSize:
            delta -= fontSize
        scrollBar = self.scrollView.verticalScrollBar()
        if (numPages > 0 and scrollBar.value() < scrollBar.maximum()) or \
                (numPages < 0 and scrollBar.value() > scrollBar.minimum()):
            scrollBar.setValue(scrollBar.value() + numPages * delta)
        elif numPages < 0:
            self.viewBack()
        else:
            self.viewForward()

    def resizeEvent(self, event):
        """Change the minimum viewport size if view size changes"""
        if (event.oldSize().height() == 0 and event.size().height()) or \
           (event.oldSize().width() == 0 and event.size().width()):
            self.setEnabled(True)
            self.updateView()
        else:
            self.scrollView.invalidateLayouts()
        QtGui.QWidget.resizeEvent(self, event)
        self.scrollView.fullView.adjustSize()
