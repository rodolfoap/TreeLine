#!/usr/bin/env python

#****************************************************************************
# treedialogs.py, provides many dialog interfaces
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import re
import string
import os
import sys
from PyQt4 import QtCore, QtGui
try:
    from __main__ import templatePath
except ImportError:
    templatePath = None
import configdialog
import optiondefaults
import globalref

stdWinFlags = QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | \
              QtCore.Qt.WindowSystemMenuHint


class TypeSetDlg(QtGui.QDialog):
    """Dialog for setting items to a type"""
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(_('Set Data Types'))

        topLayout = QtGui.QVBoxLayout(self)
        self.groupBox = QtGui.QGroupBox()
        topLayout.addWidget(self.groupBox)
        innerLayout = QtGui.QGridLayout(self.groupBox)
        self.listBox = QtGui.QListWidget()
        innerLayout.addWidget(self.listBox, 0, 0, 4, 1)
        self.itemButton = QtGui.QPushButton(_('Set &Selection'))
        innerLayout.addWidget(self.itemButton, 0, 1)
        self.connect(self.itemButton, QtCore.SIGNAL('clicked()'),
                     self.setItem)
        self.childButton = QtGui.QPushButton(_('Set S&election\'s Children'))
        innerLayout.addWidget(self.childButton, 1, 1)
        self.connect(self.childButton, QtCore.SIGNAL('clicked()'),
                     self.setChild)
        self.descendButton = QtGui.QPushButton(_('Set All &Descendants'))
        innerLayout.addWidget(self.descendButton, 2, 1)
        self.connect(self.descendButton, QtCore.SIGNAL('clicked()'),
                     self.setDescend)
        self.conditionButton = QtGui.QPushButton(_('Set Descendants '\
                                                   'C&ondtionally...'))
        innerLayout.addWidget(self.conditionButton, 3, 1)
        self.connect(self.conditionButton, QtCore.SIGNAL('clicked()'),
                     self.setCondition)

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        closeButton = QtGui.QPushButton(_('&Close'))
        ctrlLayout.addWidget(closeButton)
        self.connect(closeButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('close()'))
        self.loadList()
        self.connect(self.listBox, QtCore.SIGNAL('itemSelectionChanged()'),
                     self.updateDlg)
        self.listBox.setFocus()

    def loadList(self):
        """Load types into list box"""
        names = globalref.docRef.treeFormats.nameList(True)
        self.listBox.blockSignals(True)
        self.listBox.clear()
        self.listBox.addItems(names)
        self.listBox.setCurrentItem(self.listBox.item(0))
        self.listBox.blockSignals(False)
        self.updateDlg()

    def updateDlg(self):
        """Update label text & button availability"""
        selTypes = globalref.docRef.selection.formatNames()
        childTypes = []
        descendTypes = []
        for item in globalref.docRef.selection:
            childTypes.extend(item.childTypes())
            descendTypes.extend(item.descendTypes())
        if len(globalref.docRef.selection) == 1:
            self.groupBox.setTitle(_('Selection = "%s"') %
                                   globalref.docRef.selection[0].title())
        elif len(globalref.docRef.selection) > 1:
            self.groupBox.setTitle(_('Multiple Selection'))
        else:
            self.groupBox.setTitle(_('No Selection'))
        currentType = unicode(self.listBox.selectedItems()[0].text())
        self.itemButton.setEnabled(len(selTypes) and
                                   (min(selTypes) != max(selTypes) or
                                   selTypes[0] != currentType))
        self.childButton.setEnabled(len(childTypes) and
                                    (min(childTypes) != max(childTypes) or
                                     childTypes[0] != currentType))
        descendEnable = len(descendTypes) and \
                        (min(descendTypes) != max(descendTypes) or \
                        descendTypes[0] != currentType)
        self.descendButton.setEnabled(descendEnable)
        self.conditionButton.setEnabled(descendEnable)

    def updateViews(self):
        """Update main views due to type setting changes"""
        globalref.docRef.modified = True
        globalref.updateViewAll()

    def setCurrentSel(self):
        """Set type list selection to current item on initial open"""
        selTypes = globalref.docRef.selection.formatNames()
        names = globalref.docRef.treeFormats.nameList(True)
        if len(selTypes) == 1:
            selectNum = names.index(selTypes[0])
            self.listBox.setCurrentItem(self.listBox.item(selectNum))

    def setItem(self):
        """Set types for selected item"""
        newFormat = unicode(self.listBox.selectedItems()[0].text())
        globalref.docRef.undoStore.addTypeUndo(globalref.docRef.selection)
        for item in globalref.docRef.selection:
            item.changeType(newFormat)
        self.updateDlg()
        self.updateViews()

    def setChild(self):
        """Set types for selected item's children"""
        newFormat = unicode(self.listBox.selectedItems()[0].text())
        childList = []
        for parent in globalref.docRef.selection:
            for child in parent.childList:
                childList.append(child)
        globalref.docRef.undoStore.addTypeUndo(childList)
        for item in childList:
            item.changeType(newFormat)
        self.updateDlg()
        self.updateViews()

    def setDescend(self):
        """Set types for selected item's descendants"""
        newFormat = unicode(self.listBox.selectedItems()[0].text())
        itemList = []
        for parent in globalref.docRef.selection:
            for item in parent.descendantGenNoRoot():
                itemList.append(item)
        globalref.docRef.undoStore.addTypeUndo(itemList)
        for item in itemList:
            item.changeType(newFormat)
        self.updateDlg()
        self.updateViews()

    def setCondition(self):
        """Set types for selected item's descendants conditionally"""
        typeList = []
        for item in globalref.docRef.selection:
            for type in item.descendTypes():
                if type not in typeList:
                    typeList.append(type)
        if len(typeList) > 1:
            type, ok = QtGui.QInputDialog.getItem(self, _('Select Type'),
                                                  _('Change from data type'),
                                                  typeList, 0, False)
            if not ok:
                return
            type = unicode(type)
        else:
            type = typeList[0]
        format = globalref.docRef.treeFormats[type]
        dlg = configdialog.ConditionDlg(_('Set Descendants Conditionally'),
                                        format, self)
        if dlg.exec_() != QtGui.QDialog.Accepted:
            return
        cond = dlg.conditional()
        cond.setupFields(format)
        newFormat = unicode(self.listBox.selectedItems()[0].text())
        itemList = []
        for parent in globalref.docRef.selection:
            for item in parent.descendantGenNoRoot():
                if item.formatName == type and cond.evaluate(item.data):
                    itemList.append(item)
        globalref.docRef.undoStore.addTypeUndo(itemList)
        for item in itemList:
            item.changeType(newFormat)
        self.updateDlg()
        self.updateViews()

    def keyPressEvent(self, event):
        """Close on escape key"""
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        else:
            QtGui.QDialog.keyPressEvent(self, event)

    def closeEvent(self, event):
        """Signal that view is closing"""
        self.hide()
        self.emit(QtCore.SIGNAL('viewClosed'), False)
        event.accept()


class FieldSelectList(QtGui.QTreeWidget):
    """List view that shows direction of sort, changes with right-click
       or left/right arrows"""
    directionText = [_('descend', 'sort direction'),
                     _('ascend', 'sort direction')]
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setHeaderLabels(['#', _('Fields'), _('Direction')])
        self.setRootIsDecorated(False)
        self.setSortingEnabled(False)
        self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.resizeColumnToContents(0)
        self.connect(self, QtCore.SIGNAL('itemSelectionChanged()'),
                     self.updateSelection)

    def loadFields(self, fieldList, selectList=None):
        """Load fields into list view, add sequence and direction info
           from selectList if given"""
        self.blockSignals(True)
        self.clear()
        self.blockSignals(False)
        for field in fieldList:
            QtGui.QTreeWidgetItem(self, ['', field])
        self.resizeColumnToContents(1)
        if selectList:
            for field, dir in selectList:
                try:
                    item = self.topLevelItem(fieldList.index(field))
                    self.setItemSelected(item, True)
                    if not dir:
                        self.toggleDirection(item)
                except ValueError:
                    pass

    def selectList(self):
        """Return sort list, a list of tuples (field, direction)"""
        itemList = [self.topLevelItem(i) for i in
                    range(self.topLevelItemCount())]
        fullList = [(unicode(item.text(0)), unicode(item.text(1)),
                     unicode(item.text(2))) for item in itemList]
        selList = [grp for grp in fullList if grp[0]]
        selList.sort()
        return [(grp[1], FieldSelectList.directionText.index(grp[2])) for grp
                in selList]

    def updateSelection(self):
        """Update selected fields based on current selections"""
        selFields = [grp[0] for grp in self.selectList()]
        itemList = [self.topLevelItem(i) for i in
                    range(self.topLevelItemCount())]
        for item in itemList:
            fieldName = unicode(item.text(1))
            if self.isItemSelected(item):
                if fieldName not in selFields:
                    item.setText(2, FieldSelectList.directionText[1])
                    selFields.append(fieldName)
            elif unicode(item.text(1)) in selFields:
                selFields.remove(fieldName)
                item.setText(2, '')
        for item in itemList:
            if self.isItemSelected(item):
                item.setText(0,
                             str(selFields.index(unicode(item.text(1))) + 1))
            else:
                item.setText(0, '')
        self.emit(QtCore.SIGNAL('selectChanged'))

    def toggleDirection(self, item):
        """Toggle sort direction for viewItem"""
        origText = unicode(item.text(2))
        if origText:
            dirNum = FieldSelectList.directionText.index(origText)
            item.setText(2, FieldSelectList.directionText[not dirNum])

    def mousePressEvent(self, event):
        """Signal right-click"""
        if event.button() == QtCore.Qt.RightButton:
            item = self.itemAt(event.pos())
            if item:
                self.toggleDirection(item)
        else:
            QtGui.QTreeWidget.mousePressEvent(self, event)

    def keyPressEvent(self, event):
        """Signal direction change based on arrow click"""
        if event.key() in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Right):
            item = self.currentItem()
            if item:
                self.toggleDirection(item)
        else:
            QtGui.QTreeWidget.keyPressEvent(self, event)


class SortDlg(QtGui.QDialog):
    """Dialog to control sorting options"""
    entireTree, selectBranch, selectChildren, selectSiblings = range(4)
    sortWhat = selectBranch
    allTypes, chooseTypes, titlesAscend, titlesDescend = range(4)
    method = allTypes
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(_('Sorting'))

        topLayout = QtGui.QGridLayout(self)
        whatGroup = QtGui.QGroupBox(_('What to Sort'))
        topLayout.addWidget(whatGroup, 0, 0)
        whatLayout = QtGui.QVBoxLayout(whatGroup)
        self.whatButtons = QtGui.QButtonGroup(self)
        treeButton = QtGui.QRadioButton(_('&Entire tree'))
        self.whatButtons.addButton(treeButton, SortDlg.entireTree)
        whatLayout.addWidget(treeButton)
        branchButton = QtGui.QRadioButton(_('Selected &branches'))
        self.whatButtons.addButton(branchButton, SortDlg.selectBranch)
        whatLayout.addWidget(branchButton)
        childButton = QtGui.QRadioButton(_('Selection\'s childre&n'))
        self.whatButtons.addButton(childButton, SortDlg.selectChildren)
        whatLayout.addWidget(childButton)
        siblingButton = QtGui.QRadioButton(_('Selection\'s &siblings'))
        self.whatButtons.addButton(siblingButton, SortDlg.selectSiblings)
        whatLayout.addWidget(siblingButton)
        self.whatButtons.button(SortDlg.sortWhat).setChecked(True)
        self.connect(self.whatButtons, QtCore.SIGNAL('buttonClicked(int)'),
                     self.updateTypeList)

        methodGroup = QtGui.QGroupBox(_('Sort Method'))
        topLayout.addWidget(methodGroup, 0, 1)
        methodLayout = QtGui.QVBoxLayout(methodGroup)
        self.methodButtons = QtGui.QButtonGroup(self)
        allButton = QtGui.QRadioButton(_('All &types'))
        self.methodButtons.addButton(allButton, SortDlg.allTypes)
        methodLayout.addWidget(allButton)
        chooseButton = QtGui.QRadioButton(_('C&hoose types'))
        self.methodButtons.addButton(chooseButton, SortDlg.chooseTypes)
        methodLayout.addWidget(chooseButton)
        titleAscendButton = QtGui.QRadioButton(_('Titles only, ascendin&g'))
        self.methodButtons.addButton(titleAscendButton, SortDlg.titlesAscend)
        methodLayout.addWidget(titleAscendButton)
        titleDescendButton = QtGui.QRadioButton(_('Titles only, &descending'))
        self.methodButtons.addButton(titleDescendButton, SortDlg.titlesDescend)
        methodLayout.addWidget(titleDescendButton)
        self.methodButtons.button(SortDlg.method).setChecked(True)
        self.connect(self.methodButtons, QtCore.SIGNAL('buttonClicked(int)'),
                     self.updateTypeList)

        self.typeGroup = QtGui.QGroupBox(_('Choose T&ype(s)'))
        topLayout.addWidget(self.typeGroup, 1, 0)
        typeLayout = QtGui.QVBoxLayout(self.typeGroup)
        self.typeListBox = QtGui.QListWidget()
        typeLayout.addWidget(self.typeListBox)
        self.typeListBox.setSelectionMode(QtGui.QAbstractItemView.
                                          ExtendedSelection)
        self.connect(self.typeListBox, QtCore.SIGNAL('itemSelectionChanged()'),
                     self.updateFieldList)

        self.fieldGroup = QtGui.QGroupBox(_('Select &Fields in Order as '\
                                            'Sort Keys'))
        topLayout.addWidget(self.fieldGroup, 1, 1)
        fieldLayout = QtGui.QVBoxLayout(self.fieldGroup)
        self.fieldListBox = FieldSelectList()
        fieldLayout.addWidget(self.fieldListBox)
        self.connect(self.fieldListBox, QtCore.SIGNAL('selectChanged'),
                     self.updateControls)

        self.statusLabel = QtGui.QLabel()
        self.statusLabel.setFrameStyle(QtGui.QFrame.Panel |
                                       QtGui.QFrame.Sunken)
        topLayout.addWidget(self.statusLabel, 2, 0, 1, 2)

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout, 3, 0, 1, 2)
        ctrlLayout.addStretch(0)
        self.okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(self.okButton)
        self.connect(self.okButton, QtCore.SIGNAL('clicked()'),
                     self.sortAndClose)
        self.applyButton = QtGui.QPushButton(_('&Apply'))
        ctrlLayout.addWidget(self.applyButton)
        self.connect(self.applyButton, QtCore.SIGNAL('clicked()'),
                     self.sortNodes)
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('close()'))
        self.updateDialog()

    def updateDialog(self):
        """Update dialog entries based on current node selection"""
        numChildren = sum([len(node.childList) for node in
                           globalref.docRef.selection])
        numSiblings = sum([node.parent and len(node.parent.childList) or 0 for
                           node in globalref.docRef.selection])
        self.whatButtons.button(SortDlg.selectBranch).setEnabled(numChildren)
        self.whatButtons.button(SortDlg.selectChildren).setEnabled(numChildren)
        if numChildren == 0 and self.whatButtons.checkedId() in \
                                (SortDlg.selectBranch, SortDlg.selectChildren):
            self.whatButtons.button(SortDlg.selectSiblings).setChecked(True)
        self.whatButtons.button(SortDlg.selectSiblings).setEnabled(numSiblings)
        if numSiblings == 0 and self.whatButtons.checkedId() == \
                                SortDlg.selectSiblings:
            if numChildren:
                self.whatButtons.button(SortDlg.selectChildren).\
                                 setChecked(True)
            else:
                self.whatButtons.button(SortDlg.entireTree).setChecked(True)
        self.updateTypeList()

    def updateTypeList(self):
        """Update list of available types"""
        SortDlg.sortWhat = self.whatButtons.checkedId()
        SortDlg.method = self.methodButtons.checkedId()
        allTypes = []
        if SortDlg.sortWhat in (SortDlg.entireTree, SortDlg.selectBranch):
            selectList = [globalref.docRef.root]
            if SortDlg.sortWhat == SortDlg.selectBranch:
                selectList = globalref.docRef.selection.uniqueBranches()
            for item in selectList:
                for typeName in item.descendTypes():
                    if typeName not in allTypes:
                        allTypes.append(typeName)
        else:
            selectList = globalref.docRef.selection[:]
            if SortDlg.sortWhat == SortDlg.selectSiblings:
                selectList = [item.parent for item in selectList
                              if item.parent]
            for parent in selectList:
                for child in parent.childList:
                    if child.formatName not in allTypes:
                        allTypes.append(child.formatName)
        allTypes.sort()
        if SortDlg.method == SortDlg.allTypes:
            selectedTypes = allTypes
        elif SortDlg.method == SortDlg.chooseTypes:
            selectedTypes = [unicode(item.text()) for item in
                             self.typeListBox.selectedItems()]
            if not selectedTypes:
                selectedTypes = allTypes[:1]
            selectedTypes = [nodeType for nodeType in selectedTypes
                             if nodeType in allTypes]
        else:
            selectedTypes = []
        self.typeListBox.blockSignals(True)
        self.typeListBox.clear()
        for nodeType in allTypes:
            item = QtGui.QListWidgetItem(nodeType, self.typeListBox)
            if nodeType in selectedTypes:
                self.typeListBox.setCurrentItem(item)
                self.typeListBox.setItemSelected(item, True)
        self.typeListBox.blockSignals(False)
        self.typeGroup.setEnabled(SortDlg.method in (SortDlg.allTypes,
                                                     SortDlg.chooseTypes))
        self.updateFieldList()

    def updateFieldList(self):
        """Update list of available fields"""
        selectedTypes = [unicode(item.text()) for item in
                         self.typeListBox.selectedItems()]
        if SortDlg.method == SortDlg.allTypes and \
                  len(selectedTypes) < self.typeListBox.count():
            SortDlg.method = SortDlg.chooseTypes
            self.methodButtons.button(SortDlg.method).setChecked(True)
        commonFields = []
        if selectedTypes:
            commonFields = globalref.docRef.treeFormats[selectedTypes.pop(0)].\
                           fieldNames()
            for nodeType in selectedTypes:
                typeFields = globalref.docRef.treeFormats[nodeType].\
                                       fieldNames()
                for field in commonFields[:]:
                    if field not in typeFields:
                        commonFields.remove(field)
        oldSelList = self.fieldListBox.selectList()
        self.fieldListBox.loadFields(commonFields, oldSelList)
        self.fieldListBox.setEnabled(SortDlg.method in (SortDlg.allTypes,
                                                        SortDlg.chooseTypes))
        self.updateControls()

    def updateControls(self):
        """Update control availablitiy and status label"""
        selectList = self.fieldListBox.selectList()
        titleMethod = SortDlg.method in (SortDlg.titlesAscend,
                                         SortDlg.titlesDescend)
        if titleMethod:
            self.statusLabel.setText(_('Sorting by titles'))
        elif not self.typeListBox.selectedItems():
            self.statusLabel.setText(_('Select types to sort'))
        elif not self.fieldListBox.topLevelItemCount():
            self.statusLabel.setText(_('No common fields found in selected '\
                                       'types'))
        elif not selectList:
            self.statusLabel.setText(_('Select fields as sort keys'))
        else:
            self.statusLabel.setText(_('To change a field direction, use a'\
                                       ' right mouse click or the '\
                                       'left/right keys'))
        self.okButton.setEnabled(len(selectList) or titleMethod)
        self.applyButton.setEnabled(len(selectList) or titleMethod)

    def sortNodes(self):
        """Sort with the current options"""
        selectedTypes = []
        if SortDlg.method == SortDlg.titlesAscend:
            globalref.docRef.sortFields = [('', True)]
        elif SortDlg.method == SortDlg.titlesDescend:
            globalref.docRef.sortFields = [('', False)]
        else:
            globalref.docRef.sortFields = self.fieldListBox.selectList()
            selectedTypes = [unicode(item.text()) for item in
                             self.typeListBox.selectedItems()]
            if len(selectedTypes) == self.typeListBox.count():
                selectedTypes = []
        selectItems = globalref.docRef.selection
        if SortDlg.sortWhat == SortDlg.entireTree:
            selectItems = [globalref.docRef.root]
        elif SortDlg.sortWhat == SortDlg.selectBranch:
            selectItems = globalref.docRef.selection.uniqueBranches()
        elif SortDlg.sortWhat == SortDlg.selectSiblings:
            selectItems = [item.parent for item in selectItems if item.parent]
        if SortDlg.sortWhat in (SortDlg.entireTree, SortDlg.selectBranch):
            undoList = []
            for item in selectItems:
                undoList.extend([parent for parent in item.descendantGen()
                                 if parent.childList])
                globalref.docRef.undoStore.addChildListUndo(undoList)
            if selectedTypes:
                for item in selectItems:
                    item.sortTypeBranch(selectedTypes)
            else:
                for item in selectItems:
                    item.sortBranch()
        else:
            globalref.docRef.undoStore.addChildListUndo(selectItems)
            if selectedTypes:
                for item in selectItems:
                    item.sortTypeChildren(selectedTypes)
            else:
                for item in selectItems:
                    item.sortChildren()
        globalref.docRef.modified = True
        globalref.updateViewAll()

    def sortAndClose(self):
        """Sort with the current options and close the dialog"""
        self.sortNodes()
        self.close()

    def closeEvent(self, event):
        """Signal that view is closing"""
        self.hide()
        self.emit(QtCore.SIGNAL('viewClosed'), False)
        event.accept()


class FieldSelectDlg(QtGui.QDialog):
    """Dialog for selecting from a field list in order"""
    def __init__(self, fieldList, caption, label, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(caption)
        self.availFields = fieldList[:]
        self.selFields = []

        topLayout = QtGui.QVBoxLayout(self)
        groupBox = QtGui.QGroupBox(label)
        topLayout.addWidget(groupBox)
        boxLayout = QtGui.QVBoxLayout(groupBox)
        self.listView = QtGui.QTreeWidget()
        boxLayout.addWidget(self.listView)
        self.listView.setHeaderLabels(['#', _('Fields')])
        # if directional:
            # label = QtGui.QLabel(_('(Use a right mouse click or the '\
                                   # 'left/right keys\nto change direction)'))
            # boxLayout.addWidget(label)
        self.listView.setRootIsDecorated(False)
        self.listView.setSortingEnabled(False)
        self.listView.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.listView.resizeColumnToContents(0)
        self.listView.setFocus()
        self.connect(self.listView, QtCore.SIGNAL('itemSelectionChanged()'),
                     self.updateSelFields)

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        self.okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(self.okButton)
        self.okButton.setEnabled(False)
        self.connect(self.okButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('reject()'))
        self.loadFields()

    def loadFields(self):
        """Load fields into list view"""
        for field in self.availFields:
            QtGui.QTreeWidgetItem(self.listView, ['', field])
        self.listView.resizeColumnToContents(1)

    def getSelList(self):
        """Return sort list of fields"""
        return self.selFields[:]

    def updateSelFields(self):
        """Update selected fields based on current selections"""
        itemList = [self.listView.topLevelItem(i) for i in
                    range(self.listView.topLevelItemCount())]
        for item in itemList:
            if self.listView.isItemSelected(item):
                if unicode(item.text(1)) not in self.selFields:
                    self.selFields.append(unicode(item.text(1)))
            elif unicode(item.text(1)) in self.selFields:
                self.selFields.remove(unicode(item.text(1)))
        for item in itemList:
            if self.listView.isItemSelected(item):
                item.setText(0, str(self.selFields.index(unicode(item.text(1)))
                                    + 1))
            else:
                item.setText(0, '')
        self.okButton.setEnabled(len(self.selFields))


class EditFieldsDlg(QtGui.QDialog):
    """Dialog for editing all instances of the selected nodes field"""
    def __init__(self, fieldList, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('Change Selection'))
        self.resultDict = {}

        topLayout = QtGui.QVBoxLayout(self)
        groupBox = QtGui.QGroupBox(_('&Field'))
        topLayout.addWidget(groupBox)
        boxLayout = QtGui.QVBoxLayout(groupBox)
        self.fieldBox = QtGui.QComboBox()
        boxLayout.addWidget(self.fieldBox)
        self.fieldBox.addItems(fieldList)
        self.connect(self.fieldBox,
                     QtCore.SIGNAL('currentIndexChanged(const QString &)'),
                     self.changeField)

        groupBox = QtGui.QGroupBox(_('&New Value'))
        topLayout.addWidget(groupBox)
        boxLayout = QtGui.QVBoxLayout(groupBox)
        self.editBox = QtGui.QLineEdit()
        boxLayout.addWidget(self.editBox)
        self.connect(self.editBox,
                     QtCore.SIGNAL('textChanged(const QString &)'),
                     self.updateText)

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        self.okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(self.okButton)
        self.okButton.setEnabled(False)
        self.connect(self.okButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('reject()'))
        self.fieldBox.setFocus()

    def changeField(self, newField):
        """Update the value editor based on new field name"""
        self.editBox.blockSignals(True)
        self.editBox.setText(self.resultDict.get(unicode(newField), ''))
        self.editBox.blockSignals(False)

    def updateText(self, newText):
        """Update the stored values based on editor change"""
        self.resultDict[unicode(self.fieldBox.currentText())] = \
             unicode(newText)
        self.okButton.setEnabled(True)


class TemplateItem(object):
    """Helper class to store template paths and info"""
    nameExp = re.compile(r'(\d+)([a-zA-Z]+?)_(.+)')
    allLanguageName = _('ALL', 'all languages selection for templates')
    def __init__(self, path, fileName):
        self.fullPath = os.path.join(path, fileName)
        self.fileName = fileName
        self.number = sys.maxint
        self.langCode = ''
        noExtName = os.path.splitext(fileName)[0]
        match = TemplateItem.nameExp.match(noExtName)
        if match:
            self.number = int(match.group(1))
            self.langCode = match.group(2)
            self.displayName = match.group(3)
        else:
            self.displayName = noExtName
        self.displayName = self.displayName.replace('_', ' ')

    def __cmp__(self, other):
        """Compare function for sorting"""
        return cmp(self.number, other.number)


class TemplateDialog(QtGui.QDialog):
    """Dialog for selecting template files"""
    pathList = []
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('New File'))

        self.fullTemplateList = []
        self.filterTemplateList = []

        topLayout = QtGui.QVBoxLayout(self)
        groupBox = QtGui.QGroupBox(_('&Select Template'))
        topLayout.addWidget(groupBox)
        boxLayout = QtGui.QGridLayout(groupBox)
        self.listBox = QtGui.QListWidget()
        boxLayout.addWidget(self.listBox, 0, 0, 1, 2)
        self.listBox.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.languageLabel = QtGui.QLabel(_('&Language filter'))
        boxLayout.addWidget(self.languageLabel, 1, 0)
        self.languageLabel.setAlignment(QtCore.Qt.AlignRight)
        self.languageCombo = QtGui.QComboBox()
        boxLayout.addWidget(self.languageCombo, 1, 1)
        self.languageLabel.setBuddy(self.languageCombo)

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(okButton)
        self.connect(okButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('reject()'))

        if not TemplateDialog.pathList:
            self.setPath()
        self.readList()
        self.loadLanguages()
        self.loadListBox()
        self.connect(self.languageCombo,
                     QtCore.SIGNAL('activated(const QString&)'),
                     self.filterLanguages)

    def setPath(self):
        """Find path for templates"""
        TemplateDialog.pathList = []
        if globalref.options.templatePath:
            TemplateDialog.pathList = [globalref.options.templatePath]
        paths = [templatePath,
                 os.path.join(globalref.modPath, u'../templates/'),
                 os.path.join(globalref.modPath, u'templates/')]
        for path in filter(None, paths):
            try:
                for name in os.listdir(path):
                    if name.endswith(u'.trl'):
                        TemplateDialog.pathList.append(path)
                        return
            except OSError:
                pass

    def readList(self):
        """Read template names from directories"""
        for path in TemplateDialog.pathList:
            try:
                for name in os.listdir(path):
                    if name.endswith(u'.trl') and name not in \
                             [item.fileName for item in self.fullTemplateList]:
                        self.fullTemplateList.append(TemplateItem(path, name))
            except OSError:
                print 'Warning - can not read template directory'
        defaultItem = TemplateItem('', '')
        defaultItem.number = -1
        if globalref.lang and globalref.lang != 'C':
            defaultItem.langCode = globalref.lang[:2]
        else:
            defaultItem.langCode = 'en'
        defaultItem.displayName = _('Default - No template - Single line text')
        self.fullTemplateList.append(defaultItem)
        self.fullTemplateList.sort()
        self.filterTemplateList = self.fullTemplateList[:]

    def loadLanguages(self):
        """Populate language combo box"""
        availLanguages = set([item.langCode for item in self.fullTemplateList])
        availLanguages = list(availLanguages)
        availLanguages.sort()
        self.languageCombo.addItems(availLanguages)
        if len(availLanguages) > 1:
            self.languageCombo.insertItem(0, TemplateItem.allLanguageName)
            self.languageCombo.setCurrentIndex(0)
        else:
            self.languageLabel.setEnabled(False)
            self.languageCombo.setEnabled(False)

    def filterLanguages(self, language):
        """Remove templates that don't match language"""
        lang = unicode(language)
        if lang == TemplateItem.allLanguageName:
            self.filterTemplateList = self.fullTemplateList[:]
        else:
            self.filterTemplateList = [item for item in self.fullTemplateList
                                       if item.langCode == lang]
        self.loadListBox()

    def loadListBox(self, language=''):
        """Load template names into list view"""
        self.listBox.clear()
        self.listBox.addItems([item.displayName for item in
                               self.filterTemplateList])
        self.listBox.setCurrentRow(0)

    def selectedPath(self):
        """Return the full path of the currently selected item,
           return '' for the default item"""
        item = self.filterTemplateList[self.listBox.currentRow()]
        if item.number < 0:
            return ''
        return item.fullPath


class ExportDlg(QtGui.QDialog):
    """Dialog for selecting type of file export"""
    htmlType, dirTableType, dirPageType, xsltType, trlType, textType, \
              tableType, xbelType, mozType, xmlType, odfType = range(11)
    exportType = htmlType
    entireTree, selectBranch, selectNode = range(3)
    exportWhat = entireTree
    includeRoot = False
    openOnly = False
    addHeader = False
    numColumns = 1
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('Export File'))
        topLayout = QtGui.QVBoxLayout(self)
        horizLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(horizLayout)

        typeGroupBox = QtGui.QGroupBox(_('Export Type'))
        horizLayout.addWidget(typeGroupBox)
        typeLayout = QtGui.QVBoxLayout(typeGroupBox)
        self.typeButtons = QtGui.QButtonGroup(self)
        htmlButton = QtGui.QRadioButton(_('&HTML single file output'))
        self.typeButtons.addButton(htmlButton, ExportDlg.htmlType)
        typeLayout.addWidget(htmlButton)
        dirButton = QtGui.QRadioButton(_('HTML &directory tables'))
        self.typeButtons.addButton(dirButton, ExportDlg.dirTableType)
        typeLayout.addWidget(dirButton)
        dirPageButton = QtGui.QRadioButton(_('HTML directory &pages'))
        self.typeButtons.addButton(dirPageButton, ExportDlg.dirPageType)
        typeLayout.addWidget(dirPageButton)
        xsltButton = QtGui.QRadioButton(_('&XSLT output'))
        self.typeButtons.addButton(xsltButton, ExportDlg.xsltType)
        typeLayout.addWidget(xsltButton)
        trlButton = QtGui.QRadioButton(_('TreeLine &subtree'))
        self.typeButtons.addButton(trlButton, ExportDlg.trlType)
        typeLayout.addWidget(trlButton)
        textButton = QtGui.QRadioButton(_('&Tabbed title text'))
        self.typeButtons.addButton(textButton, ExportDlg.textType)
        typeLayout.addWidget(textButton)
        tableButton = QtGui.QRadioButton(_('T&able of node or child data'))
        self.typeButtons.addButton(tableButton, ExportDlg.tableType)
        typeLayout.addWidget(tableButton)
        xbelButton = QtGui.QRadioButton(_('XBEL boo&kmarks'))
        self.typeButtons.addButton(xbelButton, ExportDlg.xbelType)
        typeLayout.addWidget(xbelButton)
        mozButton = QtGui.QRadioButton(_('&Mozilla HTML bookmarks'))
        self.typeButtons.addButton(mozButton, ExportDlg.mozType)
        typeLayout.addWidget(mozButton)
        xmlButton = QtGui.QRadioButton(_('&Generic XML'))
        self.typeButtons.addButton(xmlButton, ExportDlg.xmlType)
        typeLayout.addWidget(xmlButton)
        odfButton = QtGui.QRadioButton(_('ODF Text Fo&rmat'))
        self.typeButtons.addButton(odfButton, ExportDlg.odfType)
        typeLayout.addWidget(odfButton)
        self.typeButtons.button(ExportDlg.exportType).setChecked(True)
        self.connect(self.typeButtons, QtCore.SIGNAL('buttonClicked(int)'),
                     self.updateCmdAvail)

        rightLayout = QtGui.QVBoxLayout()
        horizLayout.addLayout(rightLayout)

        whatGroupBox = QtGui.QGroupBox(_('What to Export'))
        rightLayout.addWidget(whatGroupBox)
        whatLayout = QtGui.QVBoxLayout(whatGroupBox)
        self.whatButtons = QtGui.QButtonGroup(self)
        treeButton = QtGui.QRadioButton(_('&Entire tree'))
        self.whatButtons.addButton(treeButton, ExportDlg.entireTree)
        whatLayout.addWidget(treeButton)
        branchButton = QtGui.QRadioButton(_('Selected &branches'))
        self.whatButtons.addButton(branchButton, ExportDlg.selectBranch)
        whatLayout.addWidget(branchButton)
        nodeButton = QtGui.QRadioButton(_('Selected &nodes'))
        self.whatButtons.addButton(nodeButton, ExportDlg.selectNode)
        whatLayout.addWidget(nodeButton)
        self.whatButtons.button(ExportDlg.exportWhat).setChecked(True)
        self.connect(self.whatButtons, QtCore.SIGNAL('buttonClicked(int)'),
                     self.updateCmdAvail)

        optionBox = QtGui.QGroupBox(_('Export Options'))
        rightLayout.addWidget(optionBox)
        optionLayout = QtGui.QVBoxLayout(optionBox)
        self.rootButton = QtGui.QCheckBox(_('&Include root node'))
        optionLayout.addWidget(self.rootButton)
        self.rootButton.setChecked(ExportDlg.includeRoot)
        self.openOnlyButton = QtGui.QCheckBox(_('Only o&pen node children'))
        optionLayout.addWidget(self.openOnlyButton)
        self.openOnlyButton.setChecked(ExportDlg.openOnly)
        self.headerButton = QtGui.QCheckBox(_('Include print header && '\
                                              '&footer'))
        optionLayout.addWidget(self.headerButton)
        self.headerButton.setChecked(ExportDlg.addHeader)
        columnLayout = QtGui.QHBoxLayout()
        optionLayout.addLayout(columnLayout)
        self.numColSpin = QtGui.QSpinBox()
        columnLayout.addWidget(self.numColSpin)
        self.numColSpin.setRange(1, optiondefaults.maxNumCol)
        self.numColSpin.setMaximumWidth(40)
        self.numColSpin.setValue(ExportDlg.numColumns)
        self.colLabel = QtGui.QLabel(_('Co&lumns'))
        columnLayout.addWidget(self.colLabel)
        self.colLabel.setBuddy(self.numColSpin)

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(okButton)
        self.connect(okButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('accept()'))
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('reject()'))
        self.updateCmdAvail()
        typeGroupBox.setFocus()

    def updateCmdAvail(self):
        """Update options available"""
        exportType = self.typeButtons.checkedId()
        exportWhat = self.whatButtons.checkedId()
        if exportType in (ExportDlg.htmlType, ExportDlg.xsltType,
                          ExportDlg.textType, ExportDlg.odfType):
            self.rootButton.setEnabled(True)
        elif exportType == ExportDlg.tableType:
            self.rootButton.setChecked(False)
            self.rootButton.setEnabled(False)
        else:
            self.rootButton.setChecked(True)
            self.rootButton.setEnabled(False)
        if exportType in (ExportDlg.htmlType, ExportDlg.textType,
                          ExportDlg.odfType):
            self.openOnlyButton.setEnabled(True)
        else:
            self.openOnlyButton.setChecked(False)
            self.openOnlyButton.setEnabled(False)
        if exportType in (ExportDlg.htmlType, ExportDlg.dirTableType):
            self.headerButton.setEnabled(True)
        else:
            self.headerButton.setChecked(False)
            self.headerButton.setEnabled(False)
        if exportType == ExportDlg.htmlType:
            self.colLabel.setEnabled(True)
            self.numColSpin.setEnabled(True)
        else:
            self.numColSpin.setValue(1)
            self.numColSpin.setEnabled(False)
            self.colLabel.setEnabled(False)
        if exportType == ExportDlg.tableType:
            self.whatButtons.button(ExportDlg.entireTree).setEnabled(False)
            if self.whatButtons.checkedId() == ExportDlg.entireTree:
                self.whatButtons.button(ExportDlg.selectBranch).\
                                 setChecked(True)
        else:
            self.whatButtons.button(ExportDlg.entireTree).setEnabled(True)
        if exportType == ExportDlg.xsltType:
            self.whatButtons.button(ExportDlg.selectBranch).setEnabled(False)
            self.whatButtons.button(ExportDlg.entireTree).setChecked(True)
        else:
            self.whatButtons.button(ExportDlg.selectBranch).setEnabled(True)
        if exportType in (ExportDlg.dirTableType, ExportDlg.dirPageType,
                          ExportDlg.xsltType):
            self.whatButtons.button(ExportDlg.selectNode).setEnabled(False)
            if self.whatButtons.checkedId() == ExportDlg.selectNode:
                self.whatButtons.button(ExportDlg.selectBranch).\
                                 setChecked(True)
        else:
            self.whatButtons.button(ExportDlg.selectNode).setEnabled(True)
        if exportWhat == ExportDlg.selectNode:
            self.rootButton.setChecked(False)
            self.rootButton.setEnabled(False)
            self.openOnlyButton.setChecked(False)
            self.openOnlyButton.setEnabled(False)

    def accept(self):
        """Store results and store last-used before closing"""
        ExportDlg.exportType = self.typeButtons.checkedId()
        ExportDlg.exportWhat = self.whatButtons.checkedId()
        ExportDlg.includeRoot = self.rootButton.isChecked()
        ExportDlg.openOnly = self.openOnlyButton.isChecked()
        ExportDlg.addHeader = self.headerButton.isChecked()
        ExportDlg.numColumns = self.numColSpin.value()
        QtGui.QDialog.accept(self)


class NumberingDlg(QtGui.QDialog):
    """Dialog for adding numbering to nodes"""
    outlineType, sectionType, singleType = range(3)
    outlineFormat = ['I.', 'A.', '1.', 'a)', '(1)', '(a)', '(i)']
    sectionFormat = ['1', '.1', '.1']
    singleFormat = ['1.']
    def __init__(self, fieldList, maxLevels, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('Data Numbering'))
        self.maxLevels = maxLevels
        self.currentStyle = NumberingDlg.outlineType
        self.currentFormat = []

        topLayout = QtGui.QVBoxLayout(self)
        groupBox = QtGui.QGroupBox(_('&Number Field'))
        topLayout.addWidget(groupBox)
        boxLayout = QtGui.QVBoxLayout(groupBox)
        self.fieldBox = QtGui.QComboBox()
        boxLayout.addWidget(self.fieldBox)
        self.fieldBox.setEditable(True)
        self.fieldBox.addItems(fieldList)
        self.fieldBox.clearEditText()
        self.fieldBox.setFocus()
        self.existOnlyButton = QtGui.QCheckBox(_('Number only where field '\
                                                 'already &exists'))
        boxLayout.addWidget(self.existOnlyButton)
        self.connect(self.fieldBox,
                     QtCore.SIGNAL('editTextChanged(const QString&)'),
                     self.updateField)

        groupBox = QtGui.QGroupBox(_('Root Node'))
        topLayout.addWidget(groupBox)
        boxLayout = QtGui.QVBoxLayout(groupBox)
        self.inclRootButton = QtGui.QCheckBox(_('&Include root node'))
        boxLayout.addWidget(self.inclRootButton)
        self.inclRootButton.setChecked(True)
        self.connect(self.inclRootButton, QtCore.SIGNAL('toggled(bool)'),
                     self.updateRoot)

        groupBox = QtGui.QGroupBox(_('Number Style'))
        topLayout.addWidget(groupBox)
        boxLayout = QtGui.QVBoxLayout(groupBox)
        self.styleGroup = QtGui.QButtonGroup(self)
        button = QtGui.QRadioButton(_('Outline (&discrete numbers)'))
        boxLayout.addWidget(button)
        self.styleGroup.addButton(button, NumberingDlg.outlineType)
        button = QtGui.QRadioButton(_('&Section (append to parent number)'))
        boxLayout.addWidget(button)
        self.styleGroup.addButton(button, NumberingDlg.sectionType)
        button = QtGui.QRadioButton(_('Single &level (children only)'))
        boxLayout.addWidget(button)
        self.styleGroup.addButton(button, NumberingDlg.singleType)
        self.styleGroup.button(self.currentStyle).setChecked(True)
        self.connect(self.styleGroup, QtCore.SIGNAL('buttonClicked(int)'),
                     self.updateStyle)

        groupBox = QtGui.QGroupBox(_('Number &Format'))
        topLayout.addWidget(groupBox)
        boxLayout = QtGui.QHBoxLayout(groupBox)
        self.formatEdit = QtGui.QLineEdit()
        boxLayout.addWidget(self.formatEdit)
        self.connect(self.formatEdit,
                     QtCore.SIGNAL('textChanged(const QString&)'),
                     self.updateFormat)
        boxLayout.addWidget(QtGui.QLabel(_('for Level')))
        self.levelBox = QtGui.QSpinBox()
        boxLayout.addWidget(self.levelBox)
        self.connect(self.levelBox, QtCore.SIGNAL('valueChanged(int)'),
                     self.updateLevel)

        groupBox = QtGui.QGroupBox(_('Initial N&umber'))
        topLayout.addWidget(groupBox)
        boxLayout = QtGui.QHBoxLayout(groupBox)
        boxLayout.addWidget(QtGui.QLabel(_('Start first level at number')))
        self.startBox = QtGui.QSpinBox()
        boxLayout.addWidget(self.startBox)
        self.startBox.setRange(1, 1000000)
        self.loadFormat()

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        self.okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(self.okButton)
        self.okButton.setEnabled(False)
        self.connect(self.okButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('reject()'))

    def updateField(self, text):
        """Update OK button based on combo changes"""
        self.okButton.setEnabled(len(unicode(text).strip()))

    def updateRoot(self, on):
        """Update styles based on include root change"""
        if self.maxLevels <= 1:
            if not on:
                self.currentStyle = NumberingDlg.singleType
                self.styleGroup.button(self.currentStyle).setChecked(True)
                self.styleGroup.button(NumberingDlg.outlineType).\
                                setEnabled(False)
                self.styleGroup.button(NumberingDlg.sectionType).\
                                setEnabled(False)
            else:
                self.styleGroup.button(NumberingDlg.outlineType).\
                                setEnabled(True)
                self.styleGroup.button(NumberingDlg.sectionType).\
                                setEnabled(True)
        if self.currentStyle == NumberingDlg.singleType and on:
            self.currentStyle = NumberingDlg.outlineType
            self.styleGroup.button(NumberingDlg.outlineType).setChecked(True)
        self.loadFormat()

    def updateStyle(self, style):
        """Update dialog based on style selection change"""
        self.currentStyle = style
        if style == NumberingDlg.singleType:
            self.inclRootButton.setChecked(False)
        self.loadFormat()

    def loadFormat(self):
        """Load a default format and level numbers into dialog"""
        numLevels = self.maxLevels
        startLevel = 1
        if self.inclRootButton.isChecked():
            numLevels += 1
            startLevel = 0
        if self.currentStyle == NumberingDlg.singleType:
            self.currentFormat = NumberingDlg.singleFormat[:]
            numLevels = 1
        elif self.currentStyle == NumberingDlg.outlineType:
            self.currentFormat = NumberingDlg.outlineFormat[:]
        else:
            self.currentFormat = NumberingDlg.sectionFormat[:]
        while len(self.currentFormat) < numLevels:
            self.currentFormat.extend(self.currentFormat[-2:])
        self.currentFormat = self.currentFormat[:numLevels]
        self.levelBox.setMinimum(startLevel)
        self.levelBox.setMaximum(startLevel + numLevels - 1)
        self.levelBox.setValue(startLevel)
        self.updateLevel(startLevel)

    def updateLevel(self, levelNum):
        """Update dialog based on a level change"""
        self.formatEdit.blockSignals(True)
        self.formatEdit.setText(self.currentFormat[levelNum -
                                                   self.levelBox.minimum()])
        self.formatEdit.blockSignals(False)

    def updateFormat(self, text):
        """Update dialog based on a format string change"""
        self.currentFormat[self.levelBox.value()
                           - self.levelBox.minimum()] = unicode(text).strip()

    def getField(self):
        """Return adjusted field name"""
        return unicode(self.fieldBox.currentText()).strip()

    def accept(self):
        """Check for acceptable field string before closing"""
        try:
            text = unicode(self.fieldBox.currentText()).strip()
        except UnicodeError:
            text = ''
        if not text.replace('_', '').isalnum():
            QtGui.QMessageBox.warning(self, 'TreeLine',
                                     _('Illegal characters in field (only '\
                                       'alpa-numerics & underscores allowed)'))
            return
        return QtGui.QDialog.accept(self)

    def existOnly(self):
        """Return True if check box for only existing fields is checked"""
        return self.existOnlyButton.isChecked()

    def includeRoot(self):
        """Return True if root include box is checked"""
        return self.inclRootButton.isChecked()

    def startNumber(self):
        """Return value from start number box"""
        return self.startBox.value()


class FindTextEntry(QtGui.QDialog):
    """Dialog for find string text entry"""
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(_('Find'))

        topLayout = QtGui.QVBoxLayout(self)
        label = QtGui.QLabel(_('Enter key words'))
        topLayout.addWidget(label)
        self.entry = QtGui.QLineEdit()
        topLayout.addWidget(self.entry)
        self.entry.setFocus()
        self.statusLabel = QtGui.QLabel()
        topLayout.addWidget(self.statusLabel)
        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        prevButton = QtGui.QPushButton(_('Find &Previous'))
        ctrlLayout.addWidget(prevButton)
        self.connect(prevButton, QtCore.SIGNAL('clicked()'), self.findPrev)
        nextButton = QtGui.QPushButton(_('Find &Next'))
        ctrlLayout.addWidget(nextButton)
        nextButton.setDefault(True)
        self.connect(nextButton, QtCore.SIGNAL('clicked()'), self.findNext)
        closeButton = QtGui.QPushButton(_('&Close'))
        ctrlLayout.addWidget(closeButton)
        self.connect(closeButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('close()'))

    def find(self, forward=True):
        """Find match in direction"""
        searchStr = unicode(self.entry.text()).strip()
        if searchStr:
            wordList = [text.lower() for text in searchStr.split()]
            leftView = globalref.mainWin.leftTabs.currentWidget()
            item = leftView.findText(wordList, forward)
            if item:
                rightSplitter = globalref.mainWin.rightTabs.currentWidget()
                rightView = rightSplitter.widget(0)
                if rightSplitter == globalref.mainWin.dataOutSplit and \
                        rightView.height():
                    rightView.highlightWords(wordList)
                self.statusLabel.setText('')
            else:
                self.statusLabel.setText(_('Text string not found'))

    def findNext(self):
        """Find next match"""
        self.find(True)

    def findPrev(self):
        """Find previous match"""
        self.find(False)
    
    def keyPressEvent(self, event):
        """Close on escape key"""
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        QtGui.QDialog.keyPressEvent(self, event)

    def closeEvent(self, event):
        """Signal that view is closing"""
        self.hide()
        self.emit(QtCore.SIGNAL('viewClosed'), False)
        event.accept()


class SpellCheckDlg(QtGui.QDialog):
    """Dialog for the spell check interface"""
    def __init__(self, spCheck, origSelect, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('Spell Check'))
        self.spCheck = spCheck
        self.origSelect = origSelect
        self.item = None
        self.field = ''
        self.lineNum = 0
        self.textLine = ''
        self.replaceAllDict = {}
        self.tmpIgnoreList = []
        self.word = ''
        self.postion = 0

        topLayout = QtGui.QHBoxLayout(self)
        leftLayout = QtGui.QVBoxLayout()
        topLayout.addLayout(leftLayout)
        wordBox = QtGui.QGroupBox(_('Not in Dictionary'))
        leftLayout.addWidget(wordBox)
        wordLayout = QtGui.QVBoxLayout(wordBox)
        label = QtGui.QLabel(_('Word:'))
        wordLayout.addWidget(label)
        self.wordEdit = QtGui.QLineEdit()
        wordLayout.addWidget(self.wordEdit)
        self.connect(self.wordEdit,
                     QtCore.SIGNAL('textChanged(const QString&)'),
                     self.updateFromWord)
        wordLayout.addSpacing(5)
        label = QtGui.QLabel(_('Context:'))
        wordLayout.addWidget(label)
        self.contextEdit = SpellContextEdit()
        wordLayout.addWidget(self.contextEdit)
        self.connect(self.contextEdit, QtCore.SIGNAL('textChanged()'),
                     self.updateFromContext)

        suggestBox = QtGui.QGroupBox(_('Suggestions'))
        leftLayout.addWidget(suggestBox)
        suggestLayout =  QtGui.QVBoxLayout(suggestBox)
        self.suggestList = QtGui.QListWidget()
        suggestLayout.addWidget(self.suggestList)
        self.connect(self.suggestList,
                     QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem*)'),
                     self.replace)

        rightLayout = QtGui.QVBoxLayout()
        topLayout.addLayout(rightLayout)
        ignoreButton = QtGui.QPushButton(_('Ignor&e'))
        rightLayout.addWidget(ignoreButton)
        self.connect(ignoreButton, QtCore.SIGNAL('clicked()'), self.ignore)
        ignoreAllButton = QtGui.QPushButton(_('&Ignore All'))
        rightLayout.addWidget(ignoreAllButton)
        self.connect(ignoreAllButton, QtCore.SIGNAL('clicked()'),
                     self.ignoreAll)
        rightLayout.addStretch()
        addButton = QtGui.QPushButton(_('&Add'))
        rightLayout.addWidget(addButton)
        self.connect(addButton, QtCore.SIGNAL('clicked()'), self.add)
        addLowerButton = QtGui.QPushButton(_('Add &Lowercase'))
        rightLayout.addWidget(addLowerButton)
        self.connect(addLowerButton, QtCore.SIGNAL('clicked()'), self.addLower)
        rightLayout.addStretch()
        replaceButton = QtGui.QPushButton(_('&Replace'))
        rightLayout.addWidget(replaceButton)
        self.connect(replaceButton, QtCore.SIGNAL('clicked()'), self.replace)
        self.replaceAllButton = QtGui.QPushButton(_('Re&place All'))
        rightLayout.addWidget(self.replaceAllButton)
        self.connect(self.replaceAllButton, QtCore.SIGNAL('clicked()'),
                     self.replaceAll)
        rightLayout.addStretch()
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        rightLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        self.widgetDisableList = [ignoreButton, ignoreAllButton, addButton,
                                  addLowerButton, self.suggestList]
        self.fullDisableList = self.widgetDisableList + \
                               [self.replaceAllButton, self.wordEdit]

    def startSpellCheck(self):
        """Initialize item generator, then check items,
           if results found, set words and return True"""
        self.lineGen = self.lineGenerator()
        try:
            self.lineGen.next()
        except StopIteration:
            return False
        return self.spellCheck()

    def continueSpellCheck(self):
        """Check lines, starting with current line,
           exit dialog if end of branes are reached"""
        if not self.spellCheck():
            self.accept()

    def spellCheck(self):
        """Check lines, starting with current line,
           if results found, set words and return True"""
        while True:
            results = self.spCheck.checkLine(self.textLine, self.tmpIgnoreList)
            if results:
                self.word, self.position, suggestions = results[0]
                newWord = self.replaceAllDict.get(self.word, '')
                if newWord:
                    self.textLine = self.replaceWord(newWord)
                    self.changeItem(self.textLine)
                else:
                    globalref.docRef.selection.changeSearchOpen([self.item])
                    self.setWord(suggestions)
                    return True
            else:
                try:
                    self.lineGen.next()
                except StopIteration:
                    return False

    def lineGenerator(self):
        """Yield next line to be checked, also sets item, field and lineNum"""
        for parent in self.origSelect:
            for self.item in parent.descendantGen():
                for self.field in self.item.nodeFormat().fieldNames():
                    text = self.item.data.get(self.field, '')
                    if text:
                        for self.lineNum, self.textLine in \
                                 enumerate(text.split('\n')):
                            self.tmpIgnoreList = []
                            yield self.textLine

    def setWord(self, suggestions):
        """Set dialog contents from the checked line and the spell check
           results"""
        self.wordEdit.blockSignals(True)
        self.wordEdit.setText(self.word)
        self.wordEdit.blockSignals(False)
        self.contextEdit.blockSignals(True)
        self.contextEdit.setPlainText(self.textLine)
        self.contextEdit.setSelection(self.position,
                                      self.position + len(self.word))
        self.contextEdit.blockSignals(False)
        self.suggestList.clear()
        self.suggestList.addItems(suggestions)
        self.suggestList.setCurrentItem(self.suggestList.item(0))
        for widget in self.fullDisableList:
            widget.setEnabled(True)

    def replaceWord(self, newWord):
        """Return textLine with word replaced to newWord"""
        return self.textLine[:self.position] + newWord + \
                       self.textLine[self.position+len(self.word):]

    def changeItem(self, newLine):
        """Replace current line in the current item"""
        globalref.docRef.undoStore.addDataUndo(self.item, True)
        textLines = self.item.data.get(self.field, '').split('\n')
        textLines[self.lineNum] = newLine
        self.item.data[self.field] = '\n'.join(textLines)
        globalref.docRef.modified = True
        globalref.updateViewAll()

    def ignore(self):
        """Set word to ignored and continue spell check"""
        self.tmpIgnoreList.append(self.word)
        self.continueSpellCheck()

    def ignoreAll(self):
        """Add to dictionary's ignore list and continue spell check"""
        self.spCheck.acceptWord(self.word)
        self.continueSpellCheck()

    def add(self):
        """Add to dictionary and continue spell check"""
        self.spCheck.addToDict(self.word, False)
        self.continueSpellCheck()

    def addLower(self):
        """Add to dictionary as lowercase and continue spell check"""
        self.spCheck.addToDict(self.word, True)
        self.continueSpellCheck()

    def replace(self):
        """Replace with current suggestion or contents from word or context
           edit boxes and continue spell check"""
        if self.widgetDisableList[0].isEnabled():
            newWord = unicode(self.suggestList.currentItem().text())
            self.textLine = self.replaceWord(newWord)
        else:
            self.textLine = unicode(self.contextEdit.toPlainText())
        self.changeItem(self.textLine)
        self.continueSpellCheck()

    def replaceAll(self):
        """Replace with current suggestion (in future too) and
           continue spell check"""
        if self.widgetDisableList[0].isEnabled():
            newWord = unicode(self.suggestList.currentItem().text())
        else:
            newWord = unicode(self.wordEdit.text())
        self.textLine = self.replaceWord(newWord)
        self.replaceAllDict[self.word] = newWord
        self.changeItem(self.textLine)
        self.continueSpellCheck()

    def updateFromWord(self):
        """Update dialog after word editor change"""
        for widget in self.widgetDisableList:
            widget.setEnabled(False)
        newWord = unicode(self.wordEdit.text())
        self.suggestList.clearSelection()
        self.contextEdit.blockSignals(True)
        self.contextEdit.setPlainText(self.replaceWord(newWord))
        self.contextEdit.setSelection(self.position,
                                      self.position + len(newWord))
        self.contextEdit.blockSignals(False)

    def updateFromContext(self):
        """Update dialog after context editor change"""
        for widget in self.fullDisableList:
            widget.setEnabled(False)
        self.suggestList.clearSelection()


class SpellContextEdit(QtGui.QTextEdit):
    """Editor for spell check word context"""
    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.setTabChangesFocus(True)

    def sizeHint(self):
        """Set prefered size"""
        fontHeight = QtGui.QFontMetrics(self.currentFont()).lineSpacing()
        return QtCore.QSize(QtGui.QTextEdit.sizeHint(self).width(),
                            fontHeight * 3)

    def setSelection(self, fromPos, toPos):
        """Select given range in first paragraph"""
        cursor = self.textCursor()
        cursor.setPosition(fromPos)
        cursor.setPosition(toPos, QtGui.QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()


class RadioChoiceDlg(QtGui.QDialog):
    """Dialog for choosing between a list of text items (radio buttons)
       choiceList contains tuples of item text and return values"""
    def __init__(self, caption, heading, choiceList, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(caption)
        topLayout = QtGui.QVBoxLayout(self)
        groupBox = QtGui.QGroupBox(heading)
        topLayout.addWidget(groupBox)
        groupLayout = QtGui.QVBoxLayout(groupBox)
        self.buttonGroup = QtGui.QButtonGroup(self)
        for text, value in choiceList:
            button = QtGui.QRadioButton(text)
            button.returnValue = value
            groupLayout.addWidget(button)
            self.buttonGroup.addButton(button)
        self.buttonGroup.buttons()[0].setChecked(True)

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(okButton)
        self.connect(okButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('accept()'))
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('reject()'))
        groupBox.setFocus()

    def getResult(self):
        """Return value of selected button"""
        return self.buttonGroup.checkedButton().returnValue


class PasswordEntry(QtGui.QDialog):
    """Dialog for password entry and optional verification"""
    def __init__(self, retype=True, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.password = ''
        self.saveIt = True
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('Encrypted File Password'))

        topLayout = QtGui.QVBoxLayout(self)
        label = QtGui.QLabel(_('Type Password:'))
        topLayout.addWidget(label)
        self.editors = [QtGui.QLineEdit()]
        self.editors[0].setEchoMode(QtGui.QLineEdit.Password)
        topLayout.addWidget(self.editors[0])
        if retype:
            label = QtGui.QLabel(_('Re-Type Password:'))
            topLayout.addWidget(label)
            self.editors.append(QtGui.QLineEdit())
            self.editors[1].setEchoMode(QtGui.QLineEdit.Password)
            topLayout.addWidget(self.editors[1])
            self.connect(self.editors[0], QtCore.SIGNAL('returnPressed()'),
                         self.editors[1], QtCore.SLOT('setFocus()'))
        self.editors[0].setFocus()
        self.connect(self.editors[-1], QtCore.SIGNAL('returnPressed()'),
                     self, QtCore.SLOT('accept()'))
        self.saveCheck = QtGui.QCheckBox(_('Remember password '\
                                           'during this session'))
        self.saveCheck.setChecked(True)
        topLayout.addWidget(self.saveCheck)

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        okButton = QtGui.QPushButton(_('&OK'))
        okButton.setAutoDefault(False)
        ctrlLayout.addWidget(okButton)
        self.connect(okButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        cancelButton.setAutoDefault(False)
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))

    def accept(self):
        """Store result and check for matching re-type before closing"""
        self.password = unicode(self.editors[0].text())
        self.saveIt = self.saveCheck.isChecked()
        if not self.password:
            QtGui.QMessageBox.warning(self, 'TreeLine',
                                  _('Zero-length passwords are not permitted'))
            self.editors[0].setFocus()
            return
        if len(self.editors) > 1 and \
               unicode(self.editors[1].text()) != self.password:
            QtGui.QMessageBox.warning(self, 'TreeLine',
                                      _('Re-typed password did not match'))
            self.editors[0].clear()
            self.editors[1].clear()
            self.editors[0].setFocus()
            return
        QtGui.QDialog.accept(self)


class ShortcutDlg(QtGui.QDialog):
    """Dialog for keyboard shortcut editing"""
    capsRe = re.compile('[%s]' % string.uppercase)
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('Keyboard Shortcuts'))

        topLayout = QtGui.QVBoxLayout(self)
        tabs = QtGui.QTabWidget()
        topLayout.addWidget(tabs)

        self.editList = []
        menuScrollArea = self.setupScrollArea(optiondefaults.menuKeyBindList)
        tabs.addTab(menuScrollArea, _('&Menu Items'))

        otherScrollArea = self.setupScrollArea(optiondefaults.otherKeyBindList)
        tabs.addTab(otherScrollArea, _('&Non-menu Items'))

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        defaultButton = QtGui.QPushButton(_('Restore Defaults'))
        ctrlLayout.addWidget(defaultButton)
        self.connect(defaultButton, QtCore.SIGNAL('clicked()'),
                     self.restoreDefaults)
        ctrlLayout.addStretch(0)
        okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(okButton)
        self.connect(okButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))

    def setupScrollArea(self, keyList):
        """Add label and edit widgets to a scrollArea and return it"""
        scrollArea = QtGui.QScrollArea()
        viewport = QtGui.QWidget()
        viewLayout = QtGui.QGridLayout(viewport)
        scrollArea.setWidget(viewport)
        scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scrollArea.setWidgetResizable(True)

        for i, (cmd, default) in enumerate(keyList):
            text = optiondefaults.cmdTranslationDict[cmd]
            text = ShortcutDlg.capsRe.sub(' \g<0>', text).strip()
            label = QtGui.QLabel(text)
            viewLayout.addWidget(label, i, 0)
            edit = KeyLineEdit(cmd, self)
            viewLayout.addWidget(edit, i, 1)
            self.editList.append(edit)

        viewport.adjustSize()
        return scrollArea

    def restoreDefaults(self):
        """Set toolbars back to default settings"""
        for edit in self.editList:
            edit.loadKey(True)

    def accept(self):
        """Save changes to options and update actions before closing"""
        for edit in self.editList:
            edit.saveChange()
        globalref.options.writeChanges()
        QtGui.QDialog.accept(self)


class KeyLineEdit(QtGui.QLineEdit):
    """Line editor for user key sequence entry"""
    blankText = ' ' * 8
    def __init__(self, command, dialogRef, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.command = command
        self.dialogRef = dialogRef
        self.setReadOnly(True)
        self.modified = False
        self.key = None
        self.loadKey()

    def loadKey(self, defaultOnly=False):
        """Load key shortcut"""
        keyName = globalref.options.strData(self.command, True, defaultOnly)
        if keyName:
            keyName = '+'.join(keyName.split())  # for legacy config files
            self.key = QtGui.QKeySequence(keyName)
            self.setText(self.key.toString(QtGui.QKeySequence.NativeText))
        else:
            self.key = None
            self.setText(KeyLineEdit.blankText)
        if defaultOnly:
            self.modified = True

    def clearKey(self):
        """Remove existing key"""
        if self.key:
            self.key = None
            self.modified = True
            self.setText(KeyLineEdit.blankText)
            self.selectAll()

    def saveChange(self):
        """Make changes to the option for this key"""
        if self.modified:
            keyText = ''
            if self.key:
                keyText = unicode(self.key.toString())
            globalref.options.changeData(self.command, keyText, True)

    def keyPressEvent(self, event):
        """Capture keypesses"""
        if event.key() in (QtCore.Qt.Key_Shift, QtCore.Qt.Key_Control,
                           QtCore.Qt.Key_Meta, QtCore.Qt.Key_Alt,
                           QtCore.Qt.Key_AltGr, QtCore.Qt.Key_CapsLock,
                           QtCore.Qt.Key_NumLock, QtCore.Qt.Key_ScrollLock):
            event.ignore()
        elif event.key() in (QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Escape):
            self.clearKey()
            event.accept()
        else:
            modifier = event.modifiers()
            if modifier & QtCore.Qt.KeypadModifier:
                modifier = modifier ^ QtCore.Qt.KeypadModifier
            key = QtGui.QKeySequence(event.key() + int(modifier))
            if key != self.key:
                for editor in self.dialogRef.editList:
                    if editor.key == key:
                        cmd = ShortcutDlg.capsRe.sub(' \g<0>',
                                                     editor.command).strip()
                        text = _('Key %(key)s already used for "%(cmd)s"') % \
                               {'key':
                                key.toString(QtGui.QKeySequence.NativeText),
                                'cmd': cmd}
                        QtGui.QMessageBox.warning(self, 'TreeLine', text)
                        event.accept()
                        return
                self.key = key
                self.setText(key.toString(QtGui.QKeySequence.NativeText))
                self.selectAll()
                self.modified = True
            event.accept()

    def contextMenuEvent(self, event):
        """Change to a context menu with a clear command"""
        menu = QtGui.QMenu(self)
        menu.addAction(_('Clear Key'), self.clearKey)
        menu.exec_(event.globalPos())

    def mousePressEvent(self, event):
        """Capture mouse clicks to avoid selection loss"""
        event.accept()

    def mouseReleaseEvent(self, event):
        """Capture mouse clicks to avoid selection loss"""
        event.accept()

    def mouseMoveEvent(self, event):
        """Capture mouse movement to avoid selection loss"""
        event.accept()

    def focusInEvent(self, event):
        """Select contents when focussed"""
        self.selectAll()
        QtGui.QLineEdit.focusInEvent(self, event)


class ToolbarDlg(QtGui.QDialog):
    """Dialog for editing toolbar contents"""
    separatorString = _('--Separator--')
    def __init__(self, updateFunction, toolIcons, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('Customize Toolbars'))

        self.updateFunction = updateFunction
        self.toolIcons = toolIcons
        self.modified = False
        self.numToolbars = 0
        self.availableCommands = []
        self.toolbarLists = []

        topLayout = QtGui.QVBoxLayout(self)
        gridLayout = QtGui.QGridLayout()
        topLayout.addLayout(gridLayout)

        sizeBox = QtGui.QGroupBox(_('Toolbar &Size'))
        gridLayout.addWidget(sizeBox, 0, 0, 1, 2)
        sizeLayout = QtGui.QVBoxLayout(sizeBox)
        self.sizeCombo = QtGui.QComboBox()
        sizeLayout.addWidget(self.sizeCombo)
        self.sizeCombo.addItems([_('Small Icons'), _('Large Icons')])
        if globalref.options.intData('ToolbarSize', 1, 128) < 24:
            self.sizeCombo.setCurrentIndex(0)
        else:
            self.sizeCombo.setCurrentIndex(1)
        self.connect(self.sizeCombo, QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.setModified)

        numberBox = QtGui.QGroupBox(_('Toolbar Quantity'))
        gridLayout.addWidget(numberBox, 0, 2)
        numberLayout = QtGui.QHBoxLayout(numberBox)
        self.quantitySpin = QtGui.QSpinBox()
        numberLayout.addWidget(self.quantitySpin)
        self.quantitySpin.setRange(0, optiondefaults.maxNumToolbars)
        numberlabel = QtGui.QLabel(_('&Toolbars'))
        numberLayout.addWidget(numberlabel)
        numberlabel.setBuddy(self.quantitySpin)
        self.connect(self.quantitySpin, QtCore.SIGNAL('valueChanged(int)'),
                     self.changeQuantity)

        availableBox = QtGui.QGroupBox(_('A&vailable Commands'))
        gridLayout.addWidget(availableBox, 1, 0)
        availableLayout = QtGui.QVBoxLayout(availableBox)
        menuCombo = QtGui.QComboBox()
        availableLayout.addWidget(menuCombo)
        menuList = [self.translatedCommand(cmd).split()[0] for cmd, dflt in
                    optiondefaults.menuKeyBindList]
        uniqueList = []
        for menu in menuList:
            if menu not in uniqueList:
                uniqueList.append(menu)
        uniqueList = ['%s %s' % (menu, _('Menu')) for menu in uniqueList]
        menuCombo.addItems(uniqueList)
        self.connect(menuCombo,
                     QtCore.SIGNAL('currentIndexChanged(const QString&)'),
                     self.updateAvailableCommands)

        self.availableListWidget = QtGui.QListWidget()
        availableLayout.addWidget(self.availableListWidget)

        buttonLayout = QtGui.QVBoxLayout()
        gridLayout.addLayout(buttonLayout, 1, 1)
        self.addButton = QtGui.QPushButton('>>')
        buttonLayout.addWidget(self.addButton)
        self.addButton.setMaximumWidth(self.addButton.sizeHint().height())
        self.connect(self.addButton, QtCore.SIGNAL('clicked()'), self.addTool)

        self.removeButton = QtGui.QPushButton('<<')
        buttonLayout.addWidget(self.removeButton)
        self.removeButton.setMaximumWidth(self.removeButton.sizeHint().
                                          height())
        self.connect(self.removeButton, QtCore.SIGNAL('clicked()'),
                     self.removeTool)

        toolbarBox = QtGui.QGroupBox(_('Tool&bar Commands'))
        gridLayout.addWidget(toolbarBox, 1, 2)
        toolbarLayout = QtGui.QVBoxLayout(toolbarBox)
        self.toolbarCombo = QtGui.QComboBox()
        toolbarLayout.addWidget(self.toolbarCombo)
        self.connect(self.toolbarCombo,
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.updateToolbarCommands)

        self.toolbarListWidget = QtGui.QListWidget()
        toolbarLayout.addWidget(self.toolbarListWidget)
        self.connect(self.toolbarListWidget,
                     QtCore.SIGNAL('currentRowChanged(int)'),
                     self.setButtonsAvailable)

        moveLayout = QtGui.QHBoxLayout()
        toolbarLayout.addLayout(moveLayout)
        self.moveUpButton = QtGui.QPushButton(_('Move &Up'))
        moveLayout.addWidget(self.moveUpButton)
        self.connect(self.moveUpButton, QtCore.SIGNAL('clicked()'),
                     self.moveUp)
        self.moveDownButton = QtGui.QPushButton(_('Move &Down'))
        moveLayout.addWidget(self.moveDownButton)
        self.connect(self.moveDownButton, QtCore.SIGNAL('clicked()'),
                     self.moveDown)

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        defaultButton = QtGui.QPushButton(_('Restore Defaults'))
        ctrlLayout.addWidget(defaultButton)
        self.connect(defaultButton, QtCore.SIGNAL('clicked()'),
                     self.restoreDefaults)
        ctrlLayout.addStretch(0)
        okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(okButton)
        self.connect(okButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        self.applyButton = QtGui.QPushButton(_('&Apply'))
        ctrlLayout.addWidget(self.applyButton)
        self.connect(self.applyButton, QtCore.SIGNAL('clicked()'),
                     self.applyChanges)
        self.applyButton.setEnabled(False)
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))

        self.loadToolbars()
        self.updateAvailableCommands(menuCombo.currentText())
        self.updateToolbarCombo()
        self.updateToolbarCommands(0)

    def translatedCommand(self, command):
        """Return command translated and with spaces added"""
        text = optiondefaults.cmdTranslationDict[command]
        return ShortcutDlg.capsRe.sub(' \g<0>', text).strip()

    def setModified(self):
        """Set modified flag and make apply available"""
        self.modified = True
        self.applyButton.setEnabled(True)

    def setButtonsAvailable(self):
        """Enable or disable buttons based on toolbar list state"""
        toolNum = 0
        numCmds = 0
        cmdNum = 0
        if self.numToolbars:
            toolNum = self.toolbarCombo.currentIndex()
            numCmds = len(self.toolbarLists[toolNum])
            if self.toolbarLists[toolNum]:
                cmdNum = self.toolbarListWidget.currentRow()
        self.addButton.setEnabled(self.numToolbars > 0)
        self.removeButton.setEnabled(self.numToolbars and numCmds)
        self.moveUpButton.setEnabled(self.numToolbars and numCmds > 1 and
                                     cmdNum > 0)
        self.moveDownButton.setEnabled(self.numToolbars and numCmds > 1 and
                                       cmdNum < numCmds - 1)

    def changeQuantity(self, num):
        """Change the toolbar quantity based on a spin box signal"""
        for i in range(self.numToolbars, num):
            globalref.options.addDefaultKey('Toolbar%d' % i)
        self.numToolbars = num
        while num > len(self.toolbarLists):
            self.toolbarLists.append([])
        self.updateToolbarCombo()
        self.setModified()

    def updateAvailableCommands(self, menuName):
        """Fill in available command list for given menu"""
        menuName = unicode(menuName).split()[0]
        self.availableCommands = []
        self.availableListWidget.clear()
        for command, dflt in optiondefaults.menuKeyBindList:
            translation = self.translatedCommand(command)
            if translation.startswith(menuName):
                icon = self.toolIcons.getIcon(command.lower())
                if icon:
                    self.availableCommands.append(command)
                    QtGui.QListWidgetItem(icon, translation,
                                          self.availableListWidget)
        self.availableCommands.append('')   # separator
        QtGui.QListWidgetItem(ToolbarDlg.separatorString,
                              self.availableListWidget)
        self.availableListWidget.setCurrentRow(0)

    def loadToolbars(self, defaultOnly=False):
        """Load toolbar data from options"""
        self.numToolbars = globalref.options.intData('ToolbarQuantity', 0,
                                                 optiondefaults.maxNumToolbars,
                                                 defaultOnly)
        self.quantitySpin.blockSignals(True)
        self.quantitySpin.setValue(self.numToolbars)
        self.quantitySpin.blockSignals(False)
        self.toolbarLists = [globalref.options.
                             strData('Toolbar%d' % num, True, defaultOnly).
                             split(',')
                             for num in range(self.numToolbars)]

    def updateToolbarCombo(self):
        """Fill in toolbar numbers for current toolbar quantity"""
        self.toolbarCombo.clear()
        if self.numToolbars:
            self.toolbarCombo.addItems(['Toolbar %d' % (num + 1) for num in
                                        range(self.numToolbars)])
        else:
            self.toolbarListWidget.clear()
            self.setButtonsAvailable()

    def updateToolbarCommands(self, num):
        """Fill in toolbar commands for toolbar num"""
        self.toolbarListWidget.clear()
        if self.numToolbars == 0:
            return
        for command in self.toolbarLists[num]:
            if command:
                icon = self.toolIcons.getIcon(command.lower())
                QtGui.QListWidgetItem(icon, self.translatedCommand(command),
                                      self.toolbarListWidget)
            else:   # separator
                QtGui.QListWidgetItem(ToolbarDlg.separatorString,
                                      self.toolbarListWidget)
        if len(self.toolbarLists[num]):
            self.toolbarListWidget.setCurrentRow(0)
        self.setButtonsAvailable()

    def addTool(self):
        """Add selected command to toolbar"""
        toolNum = self.toolbarCombo.currentIndex()
        command = self.availableCommands[self.availableListWidget.currentRow()]
        if command:
            icon = self.toolIcons.getIcon(command.lower())
            item = QtGui.QListWidgetItem(icon, self.translatedCommand(command))
        else:
            item = QtGui.QListWidgetItem(ToolbarDlg.separatorString)
        if self.toolbarLists[toolNum]:
            pos = self.toolbarListWidget.currentRow()
        else:
            pos = -1
        self.toolbarListWidget.insertItem(pos + 1, item)
        self.toolbarListWidget.setCurrentRow(pos + 1)
        self.toolbarListWidget.scrollToItem(item)
        self.toolbarLists[toolNum].insert(pos + 1, command)
        self.setModified()

    def removeTool(self):
        """Remove selected command from toolbar"""
        toolNum = self.toolbarCombo.currentIndex()
        pos = self.toolbarListWidget.currentRow()
        self.toolbarListWidget.takeItem(pos)
        del self.toolbarLists[toolNum][pos]
        if self.toolbarLists[toolNum]:
            if pos == len(self.toolbarLists[toolNum]):
                pos -= 1
            self.toolbarListWidget.setCurrentRow(pos)
        self.setModified()

    def moveUp(self):
        """Raise selected command"""
        toolNum = self.toolbarCombo.currentIndex()
        pos = self.toolbarListWidget.currentRow()
        item = self.toolbarListWidget.takeItem(pos)
        self.toolbarListWidget.insertItem(pos - 1, item)
        self.toolbarListWidget.setCurrentRow(pos - 1)
        self.toolbarListWidget.scrollToItem(item)
        command = self.toolbarLists[toolNum].pop(pos)
        self.toolbarLists[toolNum].insert(pos - 1, command)
        self.setModified()

    def moveDown(self):
        """Lower selected command"""
        toolNum = self.toolbarCombo.currentIndex()
        pos = self.toolbarListWidget.currentRow()
        item = self.toolbarListWidget.takeItem(pos)
        self.toolbarListWidget.insertItem(pos + 1, item)
        self.toolbarListWidget.setCurrentRow(pos + 1)
        self.toolbarListWidget.scrollToItem(item)
        command = self.toolbarLists[toolNum].pop(pos)
        self.toolbarLists[toolNum].insert(pos + 1, command)
        self.setModified()

    def restoreDefaults(self):
        """Set toolbars back to default settings"""
        self.loadToolbars(True)
        self.updateToolbarCombo()
        self.updateToolbarCommands(0)
        self.setModified()

    def applyChanges(self):
        """Apply any changes from the dialog"""
        if self.sizeCombo.currentIndex() == 0:
            globalref.options.changeData('ToolbarSize', '16', True)
        else:
            globalref.options.changeData('ToolbarSize', '32', True)
        globalref.options.changeData('ToolbarQuantity', str(self.numToolbars),
                                     True)
        for num, toolbarList in enumerate(self.toolbarLists):
            globalref.options.changeData('Toolbar%d' % num,
                                         ','.join(toolbarList), True)
        globalref.options.writeChanges()
        self.updateFunction()
        self.modified = False
        self.applyButton.setEnabled(False)

    def accept(self):
        """Apply changes and close the dialog"""
        if self.modified:
            self.applyChanges()
        QtGui.QDialog.accept(self)


class PluginListDlg(QtGui.QDialog):
    """Dialog for listing loaded plugins"""
    def __init__(self, plugins, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('TreeLine Plugins'))

        topLayout = QtGui.QVBoxLayout(self)
        label = QtGui.QLabel(_('Plugin Modules Loaded'))
        topLayout.addWidget(label)
        listBox = QtGui.QListWidget()
        listBox.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        listBox.setMinimumSize(250, 65)
        listBox.addItems(plugins)
        topLayout.addWidget(listBox)

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        okButton = QtGui.QPushButton(_('&OK'))
        okButton.setAutoDefault(False)
        ctrlLayout.addWidget(okButton)
        self.connect(okButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('accept()'))
