#!/usr/bin/env python

#****************************************************************************
# treeflatview.py, provides classes for a flattened "tree" view
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import string
from PyQt4 import QtCore, QtGui
import globalref


class FlatViewItem(QtGui.QListWidgetItem):
    """Qt flat tree item, contains ref to treecore TreeItem"""
    def __init__(self, parent, docItemRef):
        QtGui.QListWidgetItem.__init__(self, parent)
        self.docItemRef = docItemRef
        docItemRef.viewData = self
        self.tempSortKey = None
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
        self.setText(docItemRef.title())
        self.setTreeIcon()

    def setTreeIcon(self):
        """Set tree node icon"""
        if globalref.options.boolData('ShowTreeIcons'):
            icon = globalref.treeIcons.getIcon(self.docItemRef.
                                               nodeFormat().iconName, True)
            if icon:
                self.setIcon(icon)

    def loadTempSortKey(self):
        """Calculate a view index for sort key"""
        self.tempSortKey = self.listWidget().indexFromItem(self).row()


class FlatView(QtGui.QListWidget):
    """Left pane view of flat node structure"""
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        self.updateGenOptions()
        self.rootItems = []
        self.incremSearchMode = False
        self.incremSearchStr = ''
        self.editedItem = None
        self.noSelectClickCallback = None
        self.connect(self, QtCore.SIGNAL('itemSelectionChanged()'),
                     self.changeSelected)
        self.connect(self,
                     QtCore.SIGNAL('currentItemChanged(QListWidgetItem*, '\
                                   'QListWidgetItem*)'),
                     self.changeCurrent)

    def updateTree(self, viewSwitched=False):
        """Replace contents of FlatView from the doc"""
        if viewSwitched:
            self.rootItems = globalref.docRef.selection.uniqueBranches()
        if globalref.docRef.treeFormats.hasConditionals:
            for root in self.rootItems:
                root.setDescendantCondTypes()
        origX, origY = (self.horizontalOffset(), self.verticalOffset())
        self.blockSignals(True)
        self.clear()
        self.blockSignals(False)
        for root in self.rootItems:
            for node in root.descendantGen():
                if (not globalref.mainWin.condFilter or
                        globalref.mainWin.condFilter.evaluateType(node)) and \
                        (not globalref.mainWin.textFilter or
                         node.matchWords(globalref.mainWin.textFilter)):
                    FlatViewItem(self, node)
        self.blockSignals(True)
        self.scrollContentsBy(origX, origY)
        self.updateSelect()
        self.blockSignals(False)

    def updateSelect(self):
        """Update view selection"""
        self.blockSignals(True)
        self.clearSelection()
        selectList = []
        for item in globalref.docRef.selection:
            if hasattr(item.viewData, 'listWidget'):
                try:
                    item.viewData.text()
                    selectList.append(item)
                except RuntimeError:
                    pass
        if len(selectList) < len(globalref.docRef.selection):
            if not selectList and self.item(0):
                selectList = [self.item(0).docItemRef]
            globalref.docRef.selection.replace(selectList)
            globalref.updateRightView()
        if selectList:
            self.setCurrentItem(selectList[-1].viewData)
            globalref.docRef.selection.currentItem = selectList[-1]
            self.scrollToItem(selectList[-1].viewData)
            for node in selectList:
                self.setItemSelected(node.viewData, True)
        self.blockSignals(False)

    def updateTreeItem(self, item):
        """Update the title and open status of item"""
        if hasattr(item.viewData, 'listWidget'):
            try:
                item.viewData.text()
            except RuntimeError:
                return
            if globalref.docRef.treeFormats.hasConditionals:
                item.setConditionalType()
                item.viewData.setTreeIcon()
            item.viewData.setText(item.title())

    def updateGenOptions(self):
        """Update flat tree option settings"""
        if globalref.options.boolData('ClickRename'):
            self.setEditTriggers(QtGui.QAbstractItemView.SelectedClicked)
        else:
            self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

    def changeCurrent(self, currentItem, prevItem):
        """Set current item in selection, called from tree signal"""
        if currentItem:
            globalref.docRef.selection.currentItem = currentItem.docItemRef

    def changeSelected(self):
        """Set selection based on signal"""
        selections = self.selectedItems()[:]
        if len(selections) > 1 and \
                globalref.options.strData('SelectOrder') == 'tree':
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
            result = QtGui.QListWidget.edit(self, index, trigger, event)
            if result:
                self.editedItem = globalref.docRef.selection[0]
            return result
        else:
            return False

    def commitData(self, editor):
        """Change tree based on results of edit operation"""
        text = unicode(editor.text())
        item = globalref.docRef.selection[0]
        if text and text != item.title() and item == self.editedItem and \
                    item.setTitle(text, True):
            QtGui.QListWidget.commitData(self, editor)
            globalref.updateRightView()
        self.editedItem = None

    def treeIncremSearch(self):
        """Begin iterative search"""
        self.incremSearchMode = True
        self.incremSearchStr = ''
        globalref.setStatusBar(_('Search for:'), 0, True)

    def doIncremSearch(self):
        """Search for searchStr in all titles"""
        globalref.setStatusBar(_('Search for: %s') % self.incremSearchStr,
                               0, True)
        if self.findTitleText(self.incremSearchStr):
            globalref.setStatusBar(_('Search for: %s') % self.incremSearchStr,
                                   0, True)
        else:
            globalref.setStatusBar(_('Search for: %s  (not found)') %
                                             self.incremSearchStr, 0, True)

    def findText(self, wordList, forward=True):
        """Select item containing words in searchStr in any field,
           starts with currentItem, return item if found"""
        fullList = [self.item(i).docItemRef for i in range(self.count())]
        currentPos = fullList.index(self.currentItem().docItemRef)
        fullList = fullList[currentPos+1:] + fullList[:currentPos]
        if not forward:
            fullList.reverse()
        for item in fullList:
            if item.matchWords(wordList):
                self.clearSelection()
                self.setCurrentItem(item.viewData)
                self.scrollToItem(item.viewData)
                self.setItemSelected(item.viewData, True)
                return item
        return None

    def findTitleText(self, searchStr, forward=True, includeCurrent=True):
        """Select item containing search string"""
        searchStr = searchStr.lower()
        itemList = [self.item(i) for i in range(self.count())]
        start = self.currentRow()
        if forward:
            if not includeCurrent:
                start += 1
            seqences = [itemList[start:], itemList[:self.currentRow()]]
        else:
            if not includeCurrent:
                start -= 1
            seqences = [itemList[start::-1], itemList[-1:self.currentRow():-1]]
        for partialList in seqences:
            for item in partialList:
                if unicode(item.text()).lower().find(searchStr) >= 0:
                    self.clearSelection()
                    self.setCurrentItem(item)
                    self.scrollToItem(item)
                    self.setItemSelected(item, True)
                    return True
        return False

    def treeIncremNext(self):
        """Search for next occurance of increm string"""
        if self.incremSearchStr:
            if self.findTitleText(self.incremSearchStr, True, False):
                globalref.setStatusBar(_('Next:  %s') % self.incremSearchStr,
                                       0, True)
            else:
                globalref.setStatusBar(_('Next:  %s  (not found)') %
                                       self.incremSearchStr, 0, True)

    def treeIncremPrev(self):
        """Search for previous occurance of increm string"""
        if self.incremSearchStr:
            if self.findTitleText(self.incremSearchStr, False, False):
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

    def mousePressEvent(self, event):
        """Mouse press down event saves selected item for rename"""
        if self.incremSearchMode:
            self.incremSearchMode = False
            globalref.setStatusBar('')
        clickedItem = self.itemAt(event.pos())
        if not clickedItem:  # skip unselecting click on blank space
            return
        if self.noSelectClickCallback:
            self.noSelectClickCallback(clickedItem.docItemRef)
            self.noSelectClickCallback = None
            return
        if event.button() == QtCore.Qt.RightButton:
            return           # stop rename when context menu is used
        QtGui.QListWidget.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """Mouse release event for popup menus"""
        clickedItem = self.itemAt(event.pos())
        if not clickedItem:  # skip unselecting click on blank space
            return
        # if event.button() == QtCore.Qt.LeftButton and self.editTrigger:
            # self.editItem(clickedItem) # Qt's edit triggers hit too often
        QtGui.QListWidget.mouseReleaseEvent(self, event)

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

    def focusOutEvent(self, event):
        """Stop incremental search on focus loss"""
        if self.incremSearchMode:
            self.incremSearchMode = False
            globalref.setStatusBar('')
        QtGui.QListWidget.focusOutEvent(self, event)

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
        else:
            QtGui.QListWidget.keyPressEvent(self, event)
