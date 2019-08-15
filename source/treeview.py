#!/usr/bin/env python

#****************************************************************************
# treeview.py, provides classes for the main tree view
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import copy
import string
from PyQt4 import QtCore, QtGui
import treedoc
import treeitem
import treemainwin
import optiondefaults
import globalref


class TreeViewItem(QtGui.QTreeWidgetItem):
    """Qt tree item, contains ref to treecore TreeItem"""
    def __init__(self, parent, docItemRef):
        QtGui.QTreeWidgetItem.__init__(self, parent)
        self.docItemRef = docItemRef
        docItemRef.viewData = self
        self.tempSortKey = None
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        self.setText(0, docItemRef.title())
        self.childrenLoaded = False
        if self.docItemRef.open:
            self.treeWidget().expandItem(self)
        elif self.docItemRef.childList:
            dummyItem = QtGui.QTreeWidgetItem(self)
        self.setTreeIcon()

    def setTreeIcon(self):
        """Set tree node icon"""
        if globalref.options.boolData('ShowTreeIcons'):
            icon = globalref.treeIcons.getIcon(self.docItemRef.
                                               nodeFormat().iconName, True)
            if icon:
                self.setIcon(0, icon)

    def loadChildren(self):
        """Load child items if this item is open and not yet loaded"""
        if not self.childrenLoaded and self.docItemRef.open:
            self.takeChild(0)    # remove dummy child
            for child in self.docItemRef.childList:
                TreeViewItem(self, child)
            self.childrenLoaded = True

    def loadTempSortKey(self):
        """Calculate a list of ancestor's view indexes for sort keys"""
        indexList = []
        index = self.treeWidget().indexFromItem(self)
        while index.isValid():
            indexList.insert(0, index)
            index = index.parent()
        self.tempSortKey = [index.row() for index in indexList]


class TreeView(QtGui.QTreeWidget):
    """Left pane view of tree structure"""
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setColumnCount(1)
        self.header().hide()
        self.setRootIsDecorated(True)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        self.updateGenOptions()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.dragStartPos = None
        self.incremSearchMode = False
        self.incremSearchStr = ''
        self.blockColumnResize = False
        self.editedItem = None
        self.noSelectClickCallback = None
        self.connect(self, QtCore.SIGNAL('itemExpanded(QTreeWidgetItem*)'),
                     self.loadItemChildren)
        self.connect(self, QtCore.SIGNAL('itemCollapsed(QTreeWidgetItem*)'),
                     self.setCollapsed)
        self.connect(self, QtCore.SIGNAL('itemSelectionChanged()'),
                     self.changeSelected)
        self.connect(self,
                     QtCore.SIGNAL('currentItemChanged(QTreeWidgetItem*, '\
                                   'QTreeWidgetItem*)'),
                     self.changeCurrent)

    def updateTree(self):
        """Replace contents of TreeView from the doc"""
        if globalref.docRef.treeFormats.hasConditionals:
            globalref.docRef.root.setDescendantCondTypes()
        origX = self.horizontalScrollBar().value()
        origMaxX = self.horizontalScrollBar().maximum()
        origY = self.verticalScrollBar().value()
        self.blockSignals(True)
        self.blockColumnResize = True
        self.clear()
        self.blockSignals(False)
        item = TreeViewItem(self, globalref.docRef.root)
        if origY <= self.verticalScrollBar().maximum():
            self.verticalScrollBar().setValue(origY)
        self.blockSignals(True)
        if globalref.docRef.selection:
            try:
                self.setCurrentItem(globalref.docRef.selection[-1].viewData)
                globalref.docRef.selection.currentItem = \
                                 globalref.docRef.selection[-1]
                self.scrollToItem(globalref.docRef.selection[-1].viewData)
                for node in globalref.docRef.selection:
                    self.setItemSelected(node.viewData, True)
            except RuntimeError:
                pass  # skip if node doesn't exist anymore
        self.resizeColumnToContents(0)
        self.blockColumnResize = False
        self.blockSignals(False)
        self.horizontalScrollBar().setMaximum(origMaxX)
        self.horizontalScrollBar().setValue(origX)

    def updateSelect(self):
        """Update view selection"""
        origX = self.horizontalScrollBar().value()
        self.blockSignals(True)
        self.clearSelection()
        self.setCurrentItem(globalref.docRef.selection[-1].viewData)
        globalref.docRef.selection.currentItem = globalref.docRef.selection[-1]
        self.scrollToItem(globalref.docRef.selection[-1].viewData)
        for node in globalref.docRef.selection:
            self.setItemSelected(node.viewData, True)
        self.blockSignals(False)
        self.horizontalScrollBar().setValue(origX)

    def updateTreeItem(self, item):
        """Update the title and open status of item"""
        if item.viewData and hasattr(item.viewData, 'treeWidget'):
            try:
                if globalref.docRef.treeFormats.hasConditionals:
                    item.setConditionalType()
                    item.viewData.setTreeIcon()
                item.viewData.setText(0, item.title())
                if item.open != self.isItemExpanded(item.viewData):
                    self.setItemExpanded(item.viewData, item.open)
                self.resizeColumnToContents(0)
            except RuntimeError:
                pass   # skip if doesn't exist anymore due to closed parent

    def loadItemChildren(self, treeViewItem):
        """Ensure children are loaded in response to parent expanding"""
        treeViewItem.docItemRef.open = True
        treeViewItem.loadChildren()
        if not self.blockColumnResize:
            self.resizeColumnToContents(0)

    def updateGenOptions(self):
        """Update tree option settings"""
        self.setIndentation(globalref.options.intData('IndentOffset', 0,
                            optiondefaults.maxIndentOffset))
        if globalref.options.boolData('ClickRename'):
            self.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        else:
            self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

    def setCollapsed(self, treeViewItem):
        """Set collapsing item to closed"""
        treeViewItem.docItemRef.open = False

    def changeCurrent(self, currentItem, prevItem):
        """Set current item in selection, called from tree signal"""
        if currentItem:
            globalref.docRef.selection.currentItem = currentItem.docItemRef

    def changeSelected(self):
        """Set selection based on signal"""
        selections = self.selectedItems()[:]
        if len(selections) > 1 and \
                 (globalref.options.strData('SelectOrder') == 'tree' or
                  len(selections) > len(globalref.docRef.selection) + 1):
                 # sort if tree order or always for shift-select
            for item in selections:
                item.loadTempSortKey()
            selections.sort(lambda x,y: cmp(x.tempSortKey, y.tempSortKey))
        globalref.docRef.selection.replace([item.docItemRef for item in
                                            selections])
        globalref.updateRightView()

    def edit(self, index, trigger, event):
        """Override to block editing with multiple selection,
           also saves ref to edited item to avoid
           commiting change to wrong item due to next commands"""
        if len(globalref.docRef.selection) == 1:
            result = QtGui.QTreeWidget.edit(self, index, trigger, event)
            if result:
                self.editedItem = globalref.docRef.selection[0]
            return result
        else:
            return False

    def commitData(self, editor):
        """Change tree based on results of edit operation"""
        text = unicode(editor.text())
        item = self.editedItem
        if text and text != item.title() and item.setTitle(text, True):
            QtGui.QTreeWidget.commitData(self, editor)
            self.resizeColumnToContents(0)
            globalref.updateRightView()
        self.editedItem = None

    def findText(self, wordList, forward=True):
        """Select item containing words in searchStr in any field,
           starts with currentItem, return True if found"""
        return globalref.docRef.selection.findText(wordList, forward)

    def treeIncremSearch(self):
        """Begin iterative search"""
        self.incremSearchMode = True
        self.incremSearchStr = ''
        globalref.setStatusBar(_('Search for:'), 0, True)

    def doIncremSearch(self):
        """Search for searchStr in all titles"""
        globalref.setStatusBar(_('Search for: %s') % self.incremSearchStr,
                               0, True)
        if globalref.docRef.selection.findTitleText(self.incremSearchStr):
            globalref.setStatusBar(_('Search for: %s') % self.incremSearchStr,
                                   0, True)
        else:
            globalref.setStatusBar(_('Search for: %s  (not found)') %
                                   self.incremSearchStr, 0, True)

    def treeIncremNext(self):
        """Search for next occurance of increm string"""
        if self.incremSearchStr:
            if globalref.docRef.selection.findNextTitle(self.incremSearchStr,
                                                        True):
                globalref.setStatusBar(_('Next:  %s') % self.incremSearchStr,
                                       0, True)
            else:
                globalref.setStatusBar(_('Next:  %s  (not found)') %
                                       self.incremSearchStr, 0, True)

    def treeIncremPrev(self):
        """Search for previous occurance of increm string"""
        if self.incremSearchStr:
            if globalref.docRef.selection.findNextTitle(self.incremSearchStr,
                                                        False):
                globalref.setStatusBar(_('Previous:  %s') %
                                       self.incremSearchStr, 0, True)
            else:
                globalref.setStatusBar(_('Previous:  %s  (not found)') %
                                       self.incremSearchStr, 0, True)

    def showTypeMenu(self):
        """Show popup menu for changing the item type"""
        self.scrollToItem(self.currentItem())
        rect = self.visualItemRect(self.currentItem())
        pt = self.mapToGlobal(QtCore.QPoint(rect.center().x(), rect.bottom()))
        globalref.mainWin.typeSubMenu.popup(pt)

    def mimeTypes(self):
        """Return list of supported mime types"""
        return ['text/xml']

    def mimeData(self):
        """Return mime data for give TreeWidgetItems"""
        copyFormat = treedoc.TreeDoc.copyFormat
        if len(globalref.docRef.selection) > 1:
            globalref.docRef.treeFormats.addIfMissing(copyFormat)
            root = treeitem.TreeItem(None, copyFormat.name)
            for item in globalref.docRef.selection:
                root.childList.append(copy.copy(item))
                root.childList[-1].parent = root
        else:
            root = globalref.docRef.selection[0]
        text = u'\n'.join(root.branchXml([copyFormat]))
        globalref.docRef.treeFormats.removeQuiet(copyFormat)
        mime = QtCore.QMimeData()
        mime.setData('text/xml', text.encode('utf-8'))
        # mime.setText(text)
        return mime

    def dropMimeData(self, parent, mimeData, isCopy=False):
        """Decode dropped data"""
        mainWin = self.parent().parent().parent().parent()
        oldMainWin = globalref.mainWin
        if globalref.treeControl.duplicateWindows():
            oldMainWin.saveMultiWinTree()
        globalref.updateRefs(mainWin)
        text = unicode(mimeData.data('text/xml'), 'utf-8')
        root, newFormats = globalref.docRef.readXmlStringAndFormat(text)
        if not root:
            globalref.updateRefs(oldMainWin)
            return False
        if root.formatName == treedoc.TreeDoc.copyFormat.name:
            itemList = root.childList
        else:
            itemList = [root]
        undoParents = [parent] + filter(None, [item.parent for item in
                                               globalref.docRef.selection])
        if newFormats:
            globalref.docRef.undoStore.addBranchUndo(undoParents)
            for format in newFormats:
                globalref.docRef.treeFormats.addIfMissing(format)
            globalref.docRef.treeFormats.updateDerivedTypes()
            globalref.docRef.treeFormats.updateUniqueID()
            if treemainwin.TreeMainWin.configDlg:
                treemainwin.TreeMainWin.configDlg.resetParam()
        else:
            globalref.docRef.undoStore.addChildListUndo(undoParents)
        for node in itemList:
            parent.addTree(node)
            if isCopy:
                node.setDescendantUniqueID(True)
        parent.open = True
        globalref.docRef.selection.replace(itemList)
        if newFormats:
            globalref.docRef.treeFormats.updateAutoChoices()
        globalref.updateViewAll()
        globalref.updateRefs(oldMainWin)
        if globalref.treeControl.duplicateWindows():
            oldMainWin.updateMultiWinTree()
        return True

    def mousePressEvent(self, event):
        """Mouse press down event stores position to check for dragging
           and selects item on right-click for popup menu"""
        if self.incremSearchMode:
            self.incremSearchMode = False
            globalref.setStatusBar('')
        clickedItem = self.itemAt(event.pos())
        if not clickedItem:  # skip unselecting click on blank space
            self.dragStartPos = None
            return
        if self.noSelectClickCallback:
            self.noSelectClickCallback(clickedItem.docItemRef)
            self.noSelectClickCallback = None
            return
        if event.button() == QtCore.Qt.LeftButton:
            self.dragStartPos = QtCore.QPoint(event.pos())
        elif event.button() == QtCore.Qt.RightButton:
            return           # stop rename when context menu is used
        origX = self.horizontalScrollBar().value()
        QtGui.QTreeWidget.mousePressEvent(self, event)
        # work around Qt bug - can't set to old value directly?
        self.horizontalScrollBar().setValue(origX + 1)
        self.horizontalScrollBar().setValue(origX)

    def mouseReleaseEvent(self, event):
        """Mouse release event for popup menus"""
        self.dragStartPos = None
        clickedItem = self.itemAt(event.pos())
        if not clickedItem:  # skip unselecting click on blank space
            return
        QtGui.QTreeWidget.mouseReleaseEvent(self, event)

    def contextMenuEvent(self, event):
        """Show popup menu"""
        if event.reason() == QtGui.QContextMenuEvent.Mouse:
            clickedItem = self.itemAt(event.pos())
            if not clickedItem:
                event.ignore()
                return
            if not self.isItemSelected(clickedItem):
                self.blockSignals(True)
                self.clearSelection()
                self.blockSignals(False)
                self.setItemSelected(clickedItem, True)
            pos = event.globalPos()
        else:       # shown for menu key or other reason
            if not globalref.docRef.selection:
                event.ignore()
                return
            selectList = globalref.docRef.selection[:]
            if globalref.docRef.selection.currentItem in selectList:
                selectList.insert(0, globalref.docRef.selection.currentItem)
            posList = [self.visualItemRect(item.viewData).bottomLeft() for
                       item in selectList]
            posList = [pos for pos in posList if self.rect().contains(pos)]
            if not posList:
                posList = [QtCore.QPoint(0, 0)]
            pos = self.mapToGlobal(posList[0])
        parentList = [item for item in globalref.docRef.selection if
                      item.childList]
        if parentList:
            menu = globalref.mainWin.parentPopup
        else:
            menu = globalref.mainWin.childPopup
        menu.popup(pos)
        event.accept()

    def mouseMoveEvent(self, event):
        """Mouse move event to start drag & drop"""
        if event.buttons() == QtCore.Qt.LeftButton and self.dragStartPos and \
                globalref.docRef.selection and \
                (event.pos() - self.dragStartPos).manhattanLength() > \
                QtGui.QApplication.startDragDistance() and \
                globalref.options.boolData('DragTree'):
            oldSelect = globalref.docRef.selection[:]
            drag = QtGui.QDrag(self)
            drag.setMimeData(self.mimeData())
            dropAction = drag.start(QtCore.Qt.MoveAction |
                                    QtCore.Qt.CopyAction)
            if dropAction == QtCore.Qt.MoveAction:
                if drag.target() == None:  # move to different session
                    if globalref.docRef.root in oldSelect:
                        return   # can't delete root
                    undoParents = filter(None, [item.parent for item in
                                                globalref.docRef.selection])
                    globalref.docRef.undoStore.addChildListUndo(undoParents)
                    globalref.docRef.selection.replace([undoParents[0]])
                elif filter(None, [node.hasDescendant(globalref.docRef.
                                                      selection[0])
                                   for node in oldSelect]):
                    return  # don't delete if drag to descendant
                for item in oldSelect:
                    item.delete()
                globalref.updateViewAll()

    def dragMoveEvent(self, event):
        """Drag move event to set proper (+) or (-) for drag & drop"""
        event.setDropAction(self.dropActionFromEvent(event))
        event.accept()

    def dropEvent(self, event):
        """Drop event for drag & drop"""
        parentItem = self.itemAt(event.pos())
        if parentItem and (not self.isItemSelected(parentItem) or
                           not event.source()):
            event.setDropAction(self.dropActionFromEvent(event))
            if self.dropMimeData(parentItem.docItemRef, event.mimeData(),
                                 event.dropAction() == QtCore.Qt.CopyAction):
                event.accept()
                return
        event.ignore()

    def dropActionFromEvent(self, event):
        """Return appropriate action based on modifier keys and drag source"""
        if event.keyboardModifiers() == QtCore.Qt.ControlModifier:
            action = QtCore.Qt.CopyAction
        elif event.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            action = QtCore.Qt.MoveAction
        elif event.source() == self:
            action = QtCore.Qt.MoveAction
        else:
            action = QtCore.Qt.CopyAction
        return action

    def focusOutEvent(self, event):
        """Stop incremental search on focus loss"""
        if self.incremSearchMode:
            self.incremSearchMode = False
            globalref.setStatusBar('')
        QtGui.QTreeWidget.focusOutEvent(self, event)

    def keyPressEvent(self, event):
        """Bind keys to functions"""
        keyText = unicode(event.text())
        if self.incremSearchMode:
            if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter,
                               QtCore.Qt.Key_Escape):
                self.incremSearchMode = False
                globalref.setStatusBar('')
            elif event.key() == QtCore.Qt.Key_Backspace and \
                                self.incremSearchStr:
                self.incremSearchStr = self.incremSearchStr[:-1]
                self.doIncremSearch()
            elif keyText and keyText in string.printable:
                self.incremSearchStr += keyText
                self.doIncremSearch()
            event.accept()
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter) and \
                event.modifiers() == QtCore.Qt.NoModifier and \
                globalref.options.boolData('InsertOnEnter') and \
                self.state() != QtGui.QAbstractItemView.EditingState:
            if len(globalref.docRef.selection) == 1 and \
                       not globalref.docRef.selection[0].parent:
                globalref.mainWin.editAddChild()  # only root selected
            else:
                globalref.mainWin.editInAfter()
            event.accept()
        else:
            origX = self.horizontalScrollBar().value()
            QtGui.QTreeWidget.keyPressEvent(self, event)
            self.horizontalScrollBar().setValue(origX)
