#!/usr/bin/env python

#****************************************************************************
# configdialog.py, provides classes for the config dialogs
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
import copy
from PyQt4 import QtCore, QtGui
import treeformats
import nodeformat
import conditional
import globalref
import optiondefaults

stdWinFlags = QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | \
              QtCore.Qt.WindowSystemMenuHint


class ConfigDialog(QtGui.QDialog):
    """Base dialog for tree configuration changes"""
    treeFormats = None
    fileInfoFormat = None
    currentType = ''
    currentField = ''
    typeRenameDict = {}
    fieldRenameDict = {}
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle(_('Configure Data Types'))

        self.formatModified = False
        self.prevPage = None

        topLayout = QtGui.QVBoxLayout(self)
        self.setLayout(topLayout)

        self.tabs = QtGui.QTabWidget()
        topLayout.addWidget(self.tabs)
        typeListPage = TypeListPage(self.setModified)
        self.tabs.addTab(typeListPage, _('T&ype List'))
        typeConfigPage = TypeConfigPage(self.setModified)
        self.tabs.addTab(typeConfigPage, _('&Type Config'))
        fieldListPage = FieldListPage(self.setModified)
        self.tabs.addTab(fieldListPage, _('Field &List'))
        fieldConfigPage = FieldConfigPage(self.setModified)
        self.tabs.addTab(fieldConfigPage, _('&Field Config'))
        outputPage = OutputPage(self.setModified)
        self.tabs.addTab(outputPage, _('&Output'))
        self.connect(self.tabs, QtCore.SIGNAL('currentChanged(int)'),
                     self.updatePage)

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        self.advancedButton = QtGui.QPushButton(_('&Show Advanced'))
        ctrlLayout.addWidget(self.advancedButton)
        self.advancedButton.setCheckable(True)
        self.connect(self.advancedButton, QtCore.SIGNAL('clicked(bool)'),
                     self.toggleAdvanced)
        ctrlLayout.addStretch(0)
        okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(okButton)
        self.connect(okButton, QtCore.SIGNAL('clicked()'), self.applyAndClose)
        self.applyButton = QtGui.QPushButton(_('&Apply'))
        ctrlLayout.addWidget(self.applyButton)
        self.connect(self.applyButton, QtCore.SIGNAL('clicked()'),
                     self.applyChanges)
        self.resetButton = QtGui.QPushButton(_('&Reset'))
        ctrlLayout.addWidget(self.resetButton)
        self.connect(self.resetButton, QtCore.SIGNAL('clicked()'),
                     self.resetParam)
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'),
                     self.resetAndClose)
        self.resetParam(True)

    def resetParam(self, changeCurrent=False):
        """Reset type formats and update page,
           called initially, by the reset button, and after a file change"""
        self.prevPage = None
        ConfigDialog.treeFormats = copy.deepcopy(globalref.docRef.treeFormats)
        ConfigDialog.fileInfoFormat = copy.deepcopy(globalref.docRef.
                                                    fileInfoFormat)
        ConfigDialog.treeFormats.updateDerivedTypes()
        if changeCurrent or \
                ConfigDialog.currentType not in ConfigDialog.treeFormats:
            ConfigDialog.currentType = globalref.docRef.selection.\
                                                 currentItem.formatName
        if changeCurrent or ConfigDialog.currentField not in \
               ConfigDialog.treeFormats[ConfigDialog.currentType].fieldNames():
            ConfigDialog.currentField = globalref.docRef.\
                                        treeFormats[ConfigDialog.currentType].\
                                        fieldList[0].name
        ConfigDialog.typeRenameDict = {}
        ConfigDialog.fieldRenameDict = {}
        self.updatePage()
        self.formatModified = False
        self.setControlAvailability()

    def resetCurrent(self):
        """Reset current type and field based on tree selection"""
        ConfigDialog.currentType = globalref.docRef.selection.\
                                   currentItem.formatName
        ConfigDialog.currentField = globalref.docRef.\
                                    treeFormats[ConfigDialog.currentType].\
                                    fieldList[0].name
        page = self.tabs.currentWidget()
        page.updateContent()

    def updatePage(self):
        """Update new page and advanced button state when changing tabs"""
        if self.prevPage:
            self.prevPage.readChanges()
        page = self.tabs.currentWidget()
        self.advancedButton.setEnabled(len(page.advancedWidgets))
        page.toggleAdvanced(self.advancedButton.isChecked())
        page.updateContent()
        self.prevPage = page

    def toggleAdvanced(self, show):
        """Toggle state of advanced widgets in sub-dialogs"""
        if show:
            self.advancedButton.setText(_('Hide Advanced'))
        else:
            self.advancedButton.setText(_('Show Advanced'))
        page = self.tabs.currentWidget()
        page.toggleAdvanced(show)

    def setControlAvailability(self):
        """Set buttons to enabled or disabled based on modified status"""
        self.applyButton.setEnabled(self.formatModified)
        self.resetButton.setEnabled(self.formatModified)

    def setModified(self):
        """Change availability of controls for a modified format"""
        self.formatModified = True
        self.setControlAvailability()

    def applyChanges(self):
        """Apply copied format changes to main doc format"""
        self.tabs.currentWidget().readChanges()
        globalref.docRef.undoStore.addFormatUndo(globalref.docRef.treeFormats,
                                               globalref.docRef.fileInfoFormat,
                                               ConfigDialog.fieldRenameDict,
                                               ConfigDialog.typeRenameDict)
        globalref.docRef.treeFormats = ConfigDialog.treeFormats
        if ConfigDialog.typeRenameDict:
            globalref.docRef.treeFormats.\
                      renameFormats(ConfigDialog.typeRenameDict)
        if ConfigDialog.fieldRenameDict:
            globalref.docRef.treeFormats.\
                      renameFields(ConfigDialog.fieldRenameDict)
        if ConfigDialog.fileInfoFormat.name in ConfigDialog.treeFormats:
            globalref.docRef.fileInfoFormat = ConfigDialog.fileInfoFormat
        globalref.docRef.treeFormats.updateAllLineFields()
        globalref.docRef.treeFormats.updateAutoChoices()
        globalref.docRef.treeFormats.updateUniqueID(True)
        globalref.docRef.treeFormats.updateDerivedTypes()
        ConfigDialog.treeFormats = copy.deepcopy(globalref.docRef.treeFormats)
        ConfigDialog.fileInfoFormat = copy.deepcopy(globalref.docRef.
                                                    fileInfoFormat)
        ConfigDialog.treeFormats.updateDerivedTypes()
        ConfigDialog.typeRenameDict = {}
        ConfigDialog.fieldRenameDict = {}
        globalref.docRef.modified = True
        globalref.updateViewAll()
        self.formatModified = False
        self.setControlAvailability()

    def applyAndClose(self):
        """Apply copied format changes to main doc format & close the dialog"""
        if self.formatModified:
            self.applyChanges()
        self.close()

    def resetAndClose(self):
        """Reset type formats and update page and close"""
        self.resetParam()
        self.close()

    def closeEvent(self, event):
        """Signal dialog closing"""
        if self.formatModified:
            event.ignore()
        else:
            self.hide()
            self.emit(QtCore.SIGNAL('dialogClosed'), False)
            event.accept()


class ConfigPage(QtGui.QWidget):
    """Abstract base class for config dialog tabbed pages"""
    def __init__(self, setModifiedFunction, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setModifiedFunction = setModifiedFunction
        self.advancedWidgets = []

    def toggleAdvanced(self, show=True):
        """Toggle state of advanced widgets"""
        for widget in self.advancedWidgets:
            widget.setVisible(show)

    def readChanges(self):
        """Make changes to the format for each widget"""
        pass

    def changeCurrentType(self, index):
        """Change the current format type based on a signal"""
        self.readChanges()
        ConfigDialog.currentType = ConfigDialog.treeFormats.\
                                                nameList(True)[index]
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        ConfigDialog.currentField = currentFormat.fieldNames()[0]
        self.updateContent()

    def changeCurrentField(self, index):
        """Change the current format field based on a signal"""
        self.readChanges()
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        ConfigDialog.currentField = currentFormat.fieldNames()[index]
        self.updateContent()

    def changeField(self, currentItem, prevItem):
        """Change the current format field based on a tree widget signal"""
        self.changeCurrentField(self.fieldListBox.
                                     indexOfTopLevelItem(currentItem))


class TypeListPage(ConfigPage):
    """Config page for a list of node types"""
    def __init__(self, setModifiedFunction, parent=None):
        ConfigPage.__init__(self, setModifiedFunction, parent)
        topLayout = QtGui.QVBoxLayout(self)
        box = QtGui.QGroupBox(_('Add or Remove Data Types'))
        topLayout.addWidget(box)
        horizLayout = QtGui.QHBoxLayout(box)
        self.listBox = QtGui.QListWidget()
        horizLayout.addWidget(self.listBox)
        self.connect(self.listBox, QtCore.SIGNAL('currentRowChanged(int)'),
                     self.changeCurrentType)

        buttonLayout = QtGui.QVBoxLayout()
        horizLayout.addLayout(buttonLayout)
        newButton = QtGui.QPushButton(_('&New Type...'))
        buttonLayout.addWidget(newButton)
        self.connect(newButton, QtCore.SIGNAL('clicked()'), self.newType)
        copyButton = QtGui.QPushButton(_('Co&py Type...'))
        buttonLayout.addWidget(copyButton)
        self.connect(copyButton, QtCore.SIGNAL('clicked()'), self.copyType)
        renameButton = QtGui.QPushButton(_('R&ename Type...'))
        buttonLayout.addWidget(renameButton)
        self.connect(renameButton, QtCore.SIGNAL('clicked()'), self.renameType)
        deleteButton = QtGui.QPushButton(_('&Delete Type'))
        buttonLayout.addWidget(deleteButton)
        self.connect(deleteButton, QtCore.SIGNAL('clicked()'), self.deleteType)

    def updateContent(self):
        """Update page contents from current format settings"""
        names = ConfigDialog.treeFormats.nameList(True)
        self.listBox.blockSignals(True)
        self.listBox.clear()
        self.listBox.addItems(names)
        selectNum = names.index(ConfigDialog.currentType)
        self.listBox.setCurrentRow(selectNum)
        self.listBox.blockSignals(False)

    def newType(self):
        """Create a new type based on button signal"""
        dlg = FieldEntry(_('Add Type'), _('Enter new type name:'), '',
                         ConfigDialog.treeFormats.nameList(True), self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            newFormat = nodeformat.NodeFormat(dlg.text, {},
                                              treeformats.TreeFormats.
                                              fieldDefault)
            ConfigDialog.treeFormats[dlg.text] = newFormat
            ConfigDialog.currentType = dlg.text
            ConfigDialog.currentField = treeformats.TreeFormats.fieldDefault
            self.updateContent()
            self.setModifiedFunction()

    def copyType(self):
        """Copy selected type based on button signal"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        allowDerive = not currentFormat.genericType
        dlg = FieldCopyEntry(ConfigDialog.currentType,
                             ConfigDialog.treeFormats.nameList(True),
                             allowDerive, self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            newFormat = copy.deepcopy(currentFormat)
            newFormat.name = dlg.text
            ConfigDialog.treeFormats[dlg.text] = newFormat
            if dlg.derived:
                newFormat.genericType = ConfigDialog.currentType
                ConfigDialog.treeFormats.updateDerivedTypes()
            ConfigDialog.currentType = dlg.text
            self.updateContent()
            self.setModifiedFunction()

    def renameType(self):
        """Rename the selected type based on button signal"""
        oldName = ConfigDialog.currentType
        currentFormat = ConfigDialog.treeFormats[oldName]
        dlg = FieldEntry(_('Rename Type'), _('Rename from "%s" to:') % oldName,
                         oldName, ConfigDialog.treeFormats.nameList(True),
                         self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            currentFormat.name = dlg.text
            del ConfigDialog.treeFormats[oldName]
            ConfigDialog.treeFormats[dlg.text] = currentFormat
            reverseDict = {}
            for old, new in ConfigDialog.typeRenameDict.items():
                reverseDict[new] = old
            origName = reverseDict.get(oldName, oldName)
            ConfigDialog.typeRenameDict[origName] = dlg.text
            ConfigDialog.currentType = dlg.text
            for format in ConfigDialog.treeFormats.values():
                if format.genericType == oldName:
                    format.genericType = dlg.text
            self.updateContent()
            self.setModifiedFunction()

    def deleteType(self):
        """Delete the selected type based on button signal"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        if globalref.docRef.root.usesType(ConfigDialog.currentType):
            QtGui.QMessageBox.warning(self, 'TreeLine',
                              _('Cannot delete data type being used by nodes'))
            return
        del ConfigDialog.treeFormats[ConfigDialog.currentType]
        ConfigDialog.currentType = ConfigDialog.treeFormats.nameList(True)[0]
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        ConfigDialog.currentField = currentFormat.fieldList[0].name
        self.updateContent()
        self.setModifiedFunction()


class TypeConfigPage(ConfigPage):
    """Config page for a node type"""
    noChildTypeName = _('[None]', 'no default child type')
    def __init__(self, setModifiedFunction, parent=None):
        ConfigPage.__init__(self, setModifiedFunction, parent)
        topLayout = QtGui.QGridLayout(self)
        typeBox = QtGui.QGroupBox(_('&Data Type'))
        topLayout.addWidget(typeBox, 0, 0)
        typeLayout = QtGui.QVBoxLayout(typeBox)
        self.typeCombo = QtGui.QComboBox()
        typeLayout.addWidget(self.typeCombo)
        self.connect(self.typeCombo, QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.changeCurrentType)

        iconBox = QtGui.QGroupBox(_('Icon'))
        topLayout.addWidget(iconBox, 0, 1)
        iconLayout = QtGui.QHBoxLayout(iconBox)
        self.iconLabel = QtGui.QLabel()
        iconLayout.addWidget(self.iconLabel)
        self.iconLabel.setAlignment(QtCore.Qt.AlignCenter)
        iconButton = QtGui.QPushButton(_('Change &Icon'))
        iconLayout.addWidget(iconButton)
        self.connect(iconButton, QtCore.SIGNAL('clicked()'), self.changeIcon)

        childBox = QtGui.QGroupBox(_('Default C&hild Type'))
        topLayout.addWidget(childBox, 1, 0)
        childLayout = QtGui.QVBoxLayout(childBox)
        self.childCombo = QtGui.QComboBox()
        childLayout.addWidget(self.childCombo)
        self.connect(self.childCombo,
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     setModifiedFunction)

        # Advanced
        refFieldBox = QtGui.QGroupBox(_('Link R&eference Field'))
        topLayout.addWidget(refFieldBox, 1, 1)
        self.advancedWidgets.append(refFieldBox)
        refFieldLayout = QtGui.QVBoxLayout(refFieldBox)
        self.refFieldCombo = QtGui.QComboBox()
        refFieldLayout.addWidget(self.refFieldCombo)
        self.connect(self.refFieldCombo,
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     setModifiedFunction)

        siblingBox = QtGui.QGroupBox(_('Sibling Text'))
        topLayout.addWidget(siblingBox, 2, 0, 2, 1)
        self.advancedWidgets.append(siblingBox)
        siblingLayout = QtGui.QVBoxLayout(siblingBox)
        siblingLayout.setSpacing(0)
        prefixLabel = QtGui.QLabel(_('&Prefix Tags'))
        siblingLayout.addWidget(prefixLabel)
        self.prefixEdit = QtGui.QLineEdit()
        siblingLayout.addWidget(self.prefixEdit)
        self.connect(self.prefixEdit,
                     QtCore.SIGNAL('textEdited(const QString &)'),
                     setModifiedFunction)
        prefixLabel.setBuddy(self.prefixEdit)
        siblingLayout.addSpacing(8)
        suffixLabel = QtGui.QLabel(_('Suffi&x Tags'))
        siblingLayout.addWidget(suffixLabel)
        self.suffixEdit = QtGui.QLineEdit()
        siblingLayout.addWidget(self.suffixEdit)
        self.connect(self.suffixEdit,
                     QtCore.SIGNAL('textEdited(const QString &)'),
                     setModifiedFunction)
        suffixLabel.setBuddy(self.suffixEdit)

        self.genericBox = QtGui.QGroupBox(_('Derived from &Generic Type'))
        topLayout.addWidget(self.genericBox, 2, 1)
        self.advancedWidgets.append(self.genericBox)
        genericLayout = QtGui.QVBoxLayout(self.genericBox)
        self.genericCombo = QtGui.QComboBox()
        genericLayout.addWidget(self.genericCombo)
        self.connect(self.genericCombo,
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     setModifiedFunction)
        self.connect(self.genericCombo,
                     QtCore.SIGNAL('currentIndexChanged(const QString &)'),
                     self.readGenericChange)

        self.conditionBox = QtGui.QGroupBox(_('Automatic Types'))
        topLayout.addWidget(self.conditionBox, 3, 1)
        self.advancedWidgets.append(self.conditionBox)
        conditionLayout = QtGui.QVBoxLayout(self.conditionBox)
        self.conditionButton = QtGui.QPushButton()
        conditionLayout.addWidget(self.conditionButton)
        self.conditionButton.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                                      QtGui.QSizePolicy.Fixed)
        self.connect(self.conditionButton, QtCore.SIGNAL('clicked()'),
                     self.createCondition)

        topLayout.setRowStretch(4, 1)

    def updateContent(self):
        """Update page contents from current format settings"""
        typeNames = ConfigDialog.treeFormats.nameList(True)
        self.typeCombo.blockSignals(True)
        self.typeCombo.clear()
        self.typeCombo.addItems(typeNames)
        selectNum = typeNames.index(ConfigDialog.currentType)
        self.typeCombo.setCurrentIndex(selectNum)
        self.typeCombo.blockSignals(False)

        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        icon = globalref.treeIcons.getIcon(currentFormat.iconName, True)
        if icon:
            self.iconLabel.setPixmap(icon.pixmap(16, 16))
        else:
            self.iconLabel.setText(_('None', 'no icon set'))

        self.childCombo.blockSignals(True)
        self.childCombo.clear()
        self.childCombo.addItem(TypeConfigPage.noChildTypeName)
        self.childCombo.addItems(typeNames)
        try:
            childItem = typeNames.index(currentFormat.childType) + 1
        except ValueError:
            childItem = 0
        self.childCombo.setCurrentIndex(childItem)
        self.childCombo.blockSignals(False)

        self.refFieldCombo.blockSignals(True)
        self.refFieldCombo.clear()
        fieldNames = currentFormat.fieldNames()
        self.refFieldCombo.addItems(fieldNames)
        self.refFieldCombo.setCurrentIndex(fieldNames.
                                           index(currentFormat.refField.name))
        self.refFieldCombo.blockSignals(False)

        self.prefixEdit.setText(currentFormat.sibPrefix)
        self.suffixEdit.setText(currentFormat.sibSuffix)

        typeNames.remove(ConfigDialog.currentType)
        availGenerics = [name for name in typeNames if not
                         ConfigDialog.treeFormats[name].genericType]
        self.genericCombo.blockSignals(True)
        self.genericCombo.clear()
        self.genericCombo.addItem(TypeConfigPage.noChildTypeName)
        self.genericCombo.addItems(availGenerics)
        if currentFormat.genericType:
            genericNum = availGenerics.index(currentFormat.genericType) + 1
        else:
            genericNum = 0
        self.genericCombo.setCurrentIndex(genericNum)
        self.genericCombo.blockSignals(False)
        self.genericBox.setEnabled(ConfigDialog.currentType not in
                                   ConfigDialog.treeFormats.derivedDict)
        self.setConditionAvail()

    def changeIcon(self):
        """Change the icon setting based on button signal"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        dlg = IconSelectDlg(currentFormat, self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            currentFormat.iconName = dlg.currentName
            self.setModifiedFunction()
            self.updateContent()

    def setConditionAvail(self):
        """Set conditional type available if geenric or derived type"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        if self.genericCombo.currentIndex() > 0 or \
                 ConfigDialog.currentType in \
                 ConfigDialog.treeFormats.derivedDict:
            self.conditionBox.setEnabled(True)
            if currentFormat.conditional:
                self.conditionButton.setText(_('Modify Co&nditional Types'))
                return
        else:
            self.conditionBox.setEnabled(False)
        self.conditionButton.setText(_('Create Co&nditional Types'))

    def createCondition(self):
        """Create or modify a conditional type based on a button signal"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        dlg = ConditionDlg(_('Set Types Conditionally'), currentFormat, self)
        dlg.setConditions(currentFormat.conditional)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            currentFormat.conditional = dlg.conditional()
            ConfigDialog.treeFormats.updateDerivedTypes()
            self.setConditionAvail()
            self.setModifiedFunction()

    def readChanges(self):
        """Make changes to the format for each widget"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        currentFormat.childType = unicode(self.childCombo.currentText())
        if currentFormat.childType == TypeConfigPage.noChildTypeName:
            currentFormat.childType = ''

        currentFormat.refField = currentFormat.fieldList[self.refFieldCombo.
                                                         currentIndex()]
        currentFormat.sibPrefix = unicode(self.prefixEdit.text())
        currentFormat.sibSuffix = unicode(self.suffixEdit.text())

    def readGenericChange(self, genericName):
        """MAke changes based on signal from generic type setting,
           allows field names and conditionals to update immediately"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        previousGeneric = currentFormat.genericType
        generic = unicode(genericName)
        if generic == TypeConfigPage.noChildTypeName:
            currentFormat.genericType = ''
        else:
            currentFormat.genericType = generic
        if previousGeneric != currentFormat.genericType:
            self.readChanges()
            ConfigDialog.treeFormats.updateDerivedTypes()
            if ConfigDialog.currentField not in currentFormat.fieldNames():
                ConfigDialog.currentField = currentFormat.fieldList[0].name
            self.updateContent()


class FieldListPage(ConfigPage):
    """Config page for a list of fields"""
    def __init__(self, setModifiedFunction, parent=None):
        ConfigPage.__init__(self, setModifiedFunction, parent)
        topLayout = QtGui.QVBoxLayout(self)
        typeBox = QtGui.QGroupBox(_('&Data Type'))
        topLayout.addWidget(typeBox)
        typeLayout = QtGui.QVBoxLayout(typeBox)
        self.typeCombo = QtGui.QComboBox()
        typeLayout.addWidget(self.typeCombo)
        self.connect(self.typeCombo, QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.changeCurrentType)

        fieldBox = QtGui.QGroupBox(_('Modify Field List'))
        topLayout.addWidget(fieldBox)
        horizLayout = QtGui.QHBoxLayout(fieldBox)
        self.fieldListBox = QtGui.QTreeWidget()
        horizLayout.addWidget(self.fieldListBox)
        self.fieldListBox.setRootIsDecorated(False)
        self.fieldListBox.setColumnCount(2)
        self.fieldListBox.setHeaderLabels([_('Name'), _('Type')])
        self.connect(self.fieldListBox,
                     QtCore.SIGNAL('currentItemChanged(QTreeWidgetItem*, '\
                                   'QTreeWidgetItem*)'),
                     self.changeField)

        buttonLayout = QtGui.QVBoxLayout()
        horizLayout.addLayout(buttonLayout)
        self.upButton = QtGui.QPushButton(_('Move &Up'))
        buttonLayout.addWidget(self.upButton)
        self.connect(self.upButton, QtCore.SIGNAL('clicked()'), self.moveUp)
        self.downButton = QtGui.QPushButton(_('Move Do&wn'))
        buttonLayout.addWidget(self.downButton)
        self.connect(self.downButton, QtCore.SIGNAL('clicked()'), self.moveDown)
        self.newButton = QtGui.QPushButton(_('&New Field...'))
        buttonLayout.addWidget(self.newButton)
        self.connect(self.newButton, QtCore.SIGNAL('clicked()'), self.newField)
        self.renameButton = QtGui.QPushButton(_('R&ename Field...'))
        buttonLayout.addWidget(self.renameButton)
        self.connect(self.renameButton, QtCore.SIGNAL('clicked()'),
                     self.renameField)
        self.deleteButton = QtGui.QPushButton(_('Delete F&ield'))
        buttonLayout.addWidget(self.deleteButton)
        self.connect(self.deleteButton, QtCore.SIGNAL('clicked()'),
                     self.deleteField)

    def updateContent(self):
        """Update page contents from current format settings"""
        typeNames = ConfigDialog.treeFormats.nameList(True)
        self.typeCombo.blockSignals(True)
        self.typeCombo.clear()
        self.typeCombo.addItems(typeNames)
        selectNum = typeNames.index(ConfigDialog.currentType)
        self.typeCombo.setCurrentIndex(selectNum)
        self.typeCombo.blockSignals(False)

        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        self.fieldListBox.blockSignals(True)
        self.fieldListBox.clear()
        for field in currentFormat.fieldList:
            QtGui.QTreeWidgetItem(self.fieldListBox,
                                  [field.name, _(field.typeName)])
        selectNum = currentFormat.fieldNames().index(ConfigDialog.currentField)
        selectItem = self.fieldListBox.topLevelItem(selectNum)
        self.fieldListBox.setCurrentItem(selectItem)
        self.fieldListBox.setItemSelected(selectItem, True)
        self.fieldListBox.blockSignals(False)
        self.setButtonsAvail()

    def setButtonsAvail(self):
        """Update button availability"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        num = currentFormat.fieldNames().index(ConfigDialog.currentField)
        notDerived = not currentFormat.genericType
        self.upButton.setEnabled(num > 0 and notDerived)
        self.downButton.setEnabled(num < len(currentFormat.fieldList) - 1 and
                                   notDerived)
        self.newButton.setEnabled(notDerived)
        self.renameButton.setEnabled(notDerived)
        self.deleteButton.setEnabled(len(currentFormat.fieldList) > 1 and
                                     notDerived)

    def moveUp(self):
        """Move field up based on button signal"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        fieldList = currentFormat.fieldList
        num = currentFormat.fieldNames().index(ConfigDialog.currentField)
        if num > 0:
            fieldList[num-1], fieldList[num] = fieldList[num], fieldList[num-1]
            if ConfigDialog.currentType in \
                    ConfigDialog.treeFormats.derivedDict:
                ConfigDialog.treeFormats.updateDerivedTypes()
            self.updateContent()
            self.setModifiedFunction()

    def moveDown(self):
        """Move field down based on button signal"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        fieldList = currentFormat.fieldList
        num = currentFormat.fieldNames().index(ConfigDialog.currentField)
        if num < len(fieldList) - 1:
            fieldList[num], fieldList[num+1] = fieldList[num+1], fieldList[num]
            if ConfigDialog.currentType in \
                    ConfigDialog.treeFormats.derivedDict:
                ConfigDialog.treeFormats.updateDerivedTypes()
            self.updateContent()
            self.setModifiedFunction()

    def newField(self):
        """Create new field based on button signal"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        dlg = FieldEntry(_('Add Field'), _('Enter new field name:'), '',
                         currentFormat.fieldNames(), self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            htmlAttrs = globalref.options.boolData('HtmlNewFields') and \
                        {'html': 'y'} or {}
            currentFormat.addNewField(dlg.text, htmlAttrs)
            ConfigDialog.currentField = dlg.text
            if ConfigDialog.currentType in \
                    ConfigDialog.treeFormats.derivedDict:
                ConfigDialog.treeFormats.updateDerivedTypes()
            self.updateContent()
            self.setModifiedFunction()

    def renameField(self):
        """Rename field down based on button signal"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        currentField = currentFormat.findField(ConfigDialog.currentField)
        dlg = FieldEntry(_('Rename Field'),
                         _('Rename from "%s" to:') % currentField.name,
                         currentField.name, currentFormat.fieldNames(), self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            currentField.name = dlg.text
            derivedTypes = ConfigDialog.treeFormats.derivedDict.\
                           get(ConfigDialog.currentType, [])
            for format in derivedTypes:
                field = format.findField(ConfigDialog.currentField)
                if field:
                    field.name = dlg.text
            ConfigDialog.fieldRenameDict[ConfigDialog.currentType] = \
                    ConfigDialog.fieldRenameDict.\
                    get(ConfigDialog.currentType, []) + \
                    [(ConfigDialog.currentField, dlg.text)]
            ConfigDialog.currentField = dlg.text
            self.updateContent()
            self.setModifiedFunction()

    def deleteField(self):
        """Delete field down based on button signal"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        currentField = currentFormat.findField(ConfigDialog.currentField)
        num = currentFormat.fieldNames().index(ConfigDialog.currentField)
        currentFormat.removeField(currentField)
        derivedTypes = ConfigDialog.treeFormats.derivedDict.\
                       get(ConfigDialog.currentType, [])
        for format in derivedTypes:
            field = format.findField(ConfigDialog.currentField)
            if field:
                format.removeField(field)
        currentFormat.fieldList.remove(currentField)
        if currentFormat.refField == currentField:
            currentFormat.refField = currentFormat.fieldList[0]
        if num:
            num -= 1
        ConfigDialog.currentField = currentFormat.fieldList[num].name
        self.updateContent()
        self.setModifiedFunction()


class FieldConfigPage(ConfigPage):
    """Config page for a field"""
    types = [N_('Text', 'field type'), N_('Number', 'field type'),
             N_('Choice', 'field type'), N_('Combination', 'field type'),
             N_('AutoChoice', 'field type'), N_('Date', 'field type'),
             N_('Time', 'field type'), N_('Boolean', 'field type'),
             N_('URL', 'field type'), N_('Path', 'field type'),
             N_('InternalLink', 'field type'), N_('ExecuteLink', 'field type'),
             N_('UniqueID', 'field type'), N_('Email', 'field type'),
             N_('Picture', 'field type')]
    typeTransDict = dict([(_(name), name) for name in types])
    noAltLinkText = _('No Alternate', 'no alt link field text')
    def __init__(self, setModifiedFunction, parent=None):
        ConfigPage.__init__(self, setModifiedFunction, parent)
        self.currentFileInfoField = ''
        self.fileInfoFieldModified = False

        topLayout = QtGui.QGridLayout(self)
        typeBox = QtGui.QGroupBox(_('&Data Type'))
        topLayout.addWidget(typeBox, 0, 0)
        typeLayout = QtGui.QVBoxLayout(typeBox)
        self.typeCombo = QtGui.QComboBox()
        typeLayout.addWidget(self.typeCombo)
        self.connect(self.typeCombo, QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.changeCurrentType)

        fieldBox = QtGui.QGroupBox(_('F&ield'))
        topLayout.addWidget(fieldBox, 0, 1)
        fieldLayout = QtGui.QVBoxLayout(fieldBox)
        self.fieldCombo = QtGui.QComboBox()
        fieldLayout.addWidget(self.fieldCombo)
        self.connect(self.fieldCombo,
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.changeCurrentField)

        self.fieldTypeBox = QtGui.QGroupBox(_('Fi&eld Type'))
        topLayout.addWidget(self.fieldTypeBox, 1, 0)
        fieldTypeLayout = QtGui.QVBoxLayout(self.fieldTypeBox)
        self.fieldTypeCombo = QtGui.QComboBox()
        fieldTypeLayout.addWidget(self.fieldTypeCombo)
        self.fieldTypeCombo.addItems([_(name) for name in
                                      FieldConfigPage.types])
        self.connect(self.fieldTypeCombo,
                     QtCore.SIGNAL('currentIndexChanged(const QString &)'),
                     self.changeType)

        self.formatBox = QtGui.QGroupBox(_('O&utput Format'))
        topLayout.addWidget(self.formatBox, 1, 1)
        formatLayout = QtGui.QHBoxLayout(self.formatBox)
        self.formatEdit = QtGui.QLineEdit()
        formatLayout.addWidget(self.formatEdit)
        self.connect(self.formatEdit,
                     QtCore.SIGNAL('textEdited(const QString &)'),
                     setModifiedFunction)
        self.connect(self.formatEdit,
                     QtCore.SIGNAL('textEdited(const QString &)'),
                     self.checkFileInfoMod)
        self.helpButton = QtGui.QPushButton(_('Format &Help'))
        formatLayout.addWidget(self.helpButton)
        self.connect(self.helpButton, QtCore.SIGNAL('clicked()'),
                     self.formatHelp)

        extraBox = QtGui.QGroupBox(_('Extra Text'))
        topLayout.addWidget(extraBox, 2, 0)
        extraLayout = QtGui.QVBoxLayout(extraBox)
        extraLayout.setSpacing(0)
        prefixLabel = QtGui.QLabel(_('&Prefix'))
        extraLayout.addWidget(prefixLabel)
        self.prefixEdit = QtGui.QLineEdit()
        extraLayout.addWidget(self.prefixEdit)
        self.connect(self.prefixEdit,
                     QtCore.SIGNAL('textEdited(const QString &)'),
                     setModifiedFunction)
        self.connect(self.prefixEdit,
                     QtCore.SIGNAL('textEdited(const QString &)'),
                     self.checkFileInfoMod)
        prefixLabel.setBuddy(self.prefixEdit)
        extraLayout.addSpacing(8)
        suffixLabel = QtGui.QLabel(_('Suffi&x'))
        extraLayout.addWidget(suffixLabel)
        self.suffixEdit = QtGui.QLineEdit()
        extraLayout.addWidget(self.suffixEdit)
        self.connect(self.suffixEdit,
                     QtCore.SIGNAL('textEdited(const QString &)'),
                     setModifiedFunction)
        self.connect(self.suffixEdit,
                     QtCore.SIGNAL('textEdited(const QString &)'),
                     self.checkFileInfoMod)
        suffixLabel.setBuddy(self.suffixEdit)

        self.handleBox = QtGui.QGroupBox(_('Content Text Handling'))
        topLayout.addWidget(self.handleBox, 2, 1)
        handleLayout = QtGui.QVBoxLayout(self.handleBox)
        self.htmlButton = QtGui.QRadioButton(_('Allow HT&ML rich text'))
        handleLayout.addWidget(self.htmlButton)
        self.connect(self.htmlButton, QtCore.SIGNAL('toggled(bool)'),
                     setModifiedFunction)
        self.connect(self.htmlButton, QtCore.SIGNAL('toggled(bool)'),
                     self.checkFileInfoMod)
        self.plainButton = QtGui.QRadioButton(_('Plai&n text with '\
                                                'line breaks'))
        handleLayout.addWidget(self.plainButton)

        self.defaultBox = QtGui.QGroupBox(_('Default V&alue for New Nodes'))
        topLayout.addWidget(self.defaultBox, 3, 0)
        defaultLayout = QtGui.QVBoxLayout(self.defaultBox)
        self.defaultCombo = QtGui.QComboBox()
        defaultLayout.addWidget(self.defaultCombo)
        self.defaultCombo.setEditable(True)
        self.connect(self.defaultCombo,
                     QtCore.SIGNAL('editTextChanged(const QString &)'),
                     setModifiedFunction)

        self.heightBox = QtGui.QGroupBox(_('Editor Height'))
        topLayout.addWidget(self.heightBox, 3, 1)
        heightLayout = QtGui.QHBoxLayout(self.heightBox)
        heightLabel = QtGui.QLabel(_('Num&ber of text lines'))
        heightLayout.addWidget(heightLabel)
        self.heightCtrl = QtGui.QSpinBox()
        heightLayout.addWidget(self.heightCtrl)
        self.heightCtrl.setMinimum(1)
        self.heightCtrl.setMaximum(optiondefaults.maxNumLines)
        self.connect(self.heightCtrl, QtCore.SIGNAL('valueChanged(int)'),
                     setModifiedFunction)
        heightLabel.setBuddy(self.heightCtrl)

        # Advanced
        self.linkBox = QtGui.QGroupBox(_('Field &with alternate '\
                                         'text for links'))
        topLayout.addWidget(self.linkBox, 4, 0)
        self.advancedWidgets.append(self.linkBox)
        linkLayout = QtGui.QVBoxLayout(self.linkBox)
        self.linkCombo = QtGui.QComboBox()
        linkLayout.addWidget(self.linkCombo)
        self.connect(self.linkCombo, QtCore.SIGNAL('currentIndexChanged(int)'),
                     setModifiedFunction)

        self.paramBox = QtGui.QGroupBox(_('Optional Parameters'))
        topLayout.addWidget(self.paramBox, 4, 1)
        self.advancedWidgets.append(self.paramBox)
        paramLayout = QtGui.QVBoxLayout(self.paramBox)
        self.reqdButton = QtGui.QCheckBox(_('Re&quired to be filled'))
        paramLayout.addWidget(self.reqdButton)
        self.connect(self.reqdButton, QtCore.SIGNAL('toggled(bool)'),
                     setModifiedFunction)
        self.hiddenButton = QtGui.QCheckBox(_('Hidden on editor &view'))
        paramLayout.addWidget(self.hiddenButton)
        self.connect(self.hiddenButton, QtCore.SIGNAL('toggled(bool)'),
                     setModifiedFunction)

        topLayout.setRowStretch(5, 1)

    def updateContent(self):
        """Update page contents from current format settings"""
        typeNames = ConfigDialog.treeFormats.nameList(True)
        typeNames.append(_('File Info Reference'))
        self.typeCombo.blockSignals(True)
        self.typeCombo.clear()
        self.typeCombo.addItems(typeNames)
        if self.currentFileInfoField:
            selectNum = len(typeNames) - 1
        else:
            selectNum = typeNames.index(ConfigDialog.currentType)
        self.typeCombo.setCurrentIndex(selectNum)
        self.typeCombo.blockSignals(False)

        currentFormat, currentField = self.currentFormatField()
        self.fieldCombo.blockSignals(True)
        self.fieldCombo.clear()
        self.fieldCombo.addItems(currentFormat.fieldNames())
        selectNum = currentFormat.fieldNames().index(currentField.name)
        self.fieldCombo.setCurrentIndex(selectNum)
        self.fieldCombo.blockSignals(False)

        self.fieldTypeCombo.blockSignals(True)
        selectNum = FieldConfigPage.types.index(currentField.typeName)
        self.fieldTypeCombo.setCurrentIndex(selectNum)
        self.fieldTypeCombo.blockSignals(False)

        self.formatEdit.setText(currentField.format)

        self.prefixEdit.setText(currentField.prefix)
        self.suffixEdit.setText(currentField.suffix)

        self.htmlButton.setChecked(currentField.html)
        self.plainButton.setChecked(not currentField.html)

        self.defaultCombo.blockSignals(True)
        self.defaultCombo.clear()
        self.defaultCombo.addItem(currentField.getEditInitDefault())
        self.defaultCombo.addItems(currentField.initDefaultChoices())
        self.defaultCombo.setCurrentIndex(0)
        self.defaultCombo.blockSignals(False)

        self.heightCtrl.blockSignals(True)
        self.heightCtrl.setValue(currentField.numLines)
        self.heightCtrl.blockSignals(False)

        self.linkCombo.blockSignals(True)
        self.linkCombo.clear()
        self.linkCombo.addItem(FieldConfigPage.noAltLinkText)
        if currentField.allowAltLinkText:
            linkFields = [name for name in currentFormat.fieldNames() if
                          name != currentField.name]
            self.linkCombo.addItems(linkFields)
            if currentField.linkAltField:
                self.linkCombo.setCurrentIndex(linkFields.index(currentField.\
                                                                linkAltField))
        self.linkCombo.blockSignals(False)

        self.reqdButton.blockSignals(True)
        self.reqdButton.setChecked(currentField.isRequired)
        self.reqdButton.blockSignals(False)
        self.hiddenButton.blockSignals(True)
        self.hiddenButton.setChecked(currentField.hidden)
        self.hiddenButton.blockSignals(False)

        self.fileInfoFieldModified = False
        self.setControlAvailability()

    def currentFormatField(self):
        """Return a tuple of the current format & field"""
        if self.currentFileInfoField:
            currentFormat = ConfigDialog.fileInfoFormat
            currentField = currentFormat.findField(self.currentFileInfoField)
        else:
            currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
            currentField = currentFormat.findField(ConfigDialog.currentField)
        return (currentFormat, currentField)

    def changeCurrentType(self, index):
        """Change the current format type based on a signal"""
        if index == len(ConfigDialog.treeFormats.nameList(True)):
            self.readChanges()
            self.currentFileInfoField = ConfigDialog.fileInfoFormat.\
                                        fieldList[0].name
            self.updateContent()
        else:
            self.currentFileInfoField = ''
            ConfigPage.changeCurrentType(self, index)

    def changeCurrentField(self, index):
        """Change the current format field based on a signal"""
        if self.currentFileInfoField:
            self.readChanges()
            self.currentFileInfoField = ConfigDialog.fileInfoFormat.\
                                        fieldNames()[index]
            self.updateContent()
        else:
            ConfigPage.changeCurrentField(self, index)

    def setControlAvailability(self):
        """Set controls available based on field type"""
        currentFormat, currentField = self.currentFormatField()
        self.fieldTypeBox.setEnabled(not self.currentFileInfoField and
                                     not currentFormat.genericType)
        self.formatBox.setEnabled(currentField.defaultFormat != '')
        self.handleBox.setEnabled(currentField.htmlOption)
        self.defaultBox.setEnabled(not self.currentFileInfoField)
        self.heightBox.setEnabled(not currentField.hasEditChoices and
                                  not self.currentFileInfoField)
        self.linkBox.setEnabled(currentField.allowAltLinkText and
                                not self.currentFileInfoField)
        self.paramBox.setEnabled(not self.currentFileInfoField)

    def checkFileInfoMod(self):
        """Check for modified file info field"""
        if self.currentFileInfoField:
            self.fileInfoFieldModified = True

    def changeType(self, text):
        """Change field type based on combo box signal"""
        self.readChanges()  # preserve previous changes
        currentFormat, currentField = self.currentFormatField()
        currentField.changeType(FieldConfigPage.typeTransDict[unicode(text)])
        if ConfigDialog.currentType in ConfigDialog.treeFormats.derivedDict:
            ConfigDialog.treeFormats.updateDerivedTypes()
        self.updateContent()
        self.setModifiedFunction()

    def formatHelp(self):
        """Provide format help menu based on button signal"""
        currentFormat, currentField = self.currentFormatField()
        menu = QtGui.QMenu(self)
        self.formatDict = {}
        for item in currentField.formatMenuList:
            if item:
                descr, key = item
                self.formatDict[descr] = key
                menu.addAction(descr)
            else:
                menu.addSeparator()
        menu.popup(self.helpButton.\
                   mapToGlobal(QtCore.QPoint(0, self.helpButton.height())))
        self.connect(menu, QtCore.SIGNAL('triggered(QAction*)'),
                     self.insertFormat)

    def insertFormat(self, action):
        """Insert format text from id into edit box"""
        self.formatEdit.insert(self.formatDict[unicode(action.text())])

    def readChanges(self):
        """Make changes to the format for each widget"""
        currentFormat, currentField = self.currentFormatField()
        currentField.format = unicode(self.formatEdit.text())
        currentField.prefix = unicode(self.prefixEdit.text())
        currentField.suffix = unicode(self.suffixEdit.text())
        if currentField.htmlOption:
            currentField.html = self.htmlButton.isChecked()
        currentField.setInitDefault(unicode(self.defaultCombo.currentText()))
        if not currentField.hasEditChoices:
            currentField.numLines = self.heightCtrl.value()

        if currentField.allowAltLinkText:
            text = unicode(self.linkCombo.currentText())
            if text == FieldConfigPage.noAltLinkText:
                text = ''
            currentField.linkAltField = text
        currentField.isRequired = self.reqdButton.isChecked()
        currentField.hidden = self.hiddenButton.isChecked()
        currentField.initFormat()
        if self.currentFileInfoField and self.fileInfoFieldModified:
            ConfigDialog.treeFormats[currentFormat.name] = currentFormat
            self.fileInfoFieldModified = False


class OutputPage(ConfigPage):
    """Config page for type output"""
    refLevelList = [_('No Other Reference'), _('File Info Reference'),
                    _('Any Ancestor Reference'), _('Parent Reference'),
                    _('Grandparent Reference'),
                    _('Great Grandparent Reference'), _('Child Reference'),
                    _('Child Count')]
    # refLevelFlags correspond to refLevelList
    refLevelFlags = ['', '!', '?', '*', '**', '***', '&', '#']
    fieldPattern = re.compile('{\*.*?\*}')
    def __init__(self, setModifiedFunction, parent=None):
        ConfigPage.__init__(self, setModifiedFunction, parent)
        self.refLevelFlag = ''
        self.refLevelType = ''

        topLayout = QtGui.QGridLayout(self)
        typeBox = QtGui.QGroupBox(_('&Data Type'))
        topLayout.addWidget(typeBox, 0, 0)
        typeLayout = QtGui.QVBoxLayout(typeBox)
        self.typeCombo = QtGui.QComboBox()
        typeLayout.addWidget(self.typeCombo)
        self.connect(self.typeCombo, QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.changeCurrentType)

        fieldBox = QtGui.QGroupBox(_('F&ield List'))
        topLayout.addWidget(fieldBox, 1, 0, 2, 1)
        horizLayout = QtGui.QVBoxLayout(fieldBox)
        self.fieldListBox = QtGui.QTreeWidget()
        horizLayout.addWidget(self.fieldListBox)
        self.fieldListBox.setRootIsDecorated(False)
        self.fieldListBox.setColumnCount(2)
        self.fieldListBox.setHeaderLabels([_('Name'), _('Type')])
        self.connect(self.fieldListBox,
                     QtCore.SIGNAL('currentItemChanged(QTreeWidgetItem*, '\
                                   'QTreeWidgetItem*)'),
                     self.changeVirtualField)

        titleButtonLayout = QtGui.QVBoxLayout()
        topLayout.addLayout(titleButtonLayout, 1, 1)
        self.toTitleButton = QtGui.QPushButton('>>')
        titleButtonLayout.addWidget(self.toTitleButton)
        self.toTitleButton.setMaximumWidth(self.toTitleButton.
                                           sizeHint().height())
        self.connect(self.toTitleButton, QtCore.SIGNAL('clicked()'),
                     self.fieldToTitle)
        self.delTitleButton = QtGui.QPushButton('<<')
        titleButtonLayout.addWidget(self.delTitleButton)
        self.delTitleButton.setMaximumWidth(self.delTitleButton.
                                            sizeHint().height())
        self.connect(self.delTitleButton, QtCore.SIGNAL('clicked()'),
                     self.delTitleField)

        titleBox = QtGui.QGroupBox(_('Titl&e Format'))
        topLayout.addWidget(titleBox, 1, 2)
        titleLayout = QtGui.QVBoxLayout(titleBox)
        self.titleEdit = TitleEdit()
        titleLayout.addWidget(self.titleEdit)
        self.connect(self.titleEdit,
                     QtCore.SIGNAL('cursorPositionChanged(int, int)'),
                     self.setControlAvailability)
        self.connect(self.titleEdit,
                     QtCore.SIGNAL('textEdited(const QString &)'),
                     setModifiedFunction)

        outputButtonLayout = QtGui.QVBoxLayout()
        topLayout.addLayout(outputButtonLayout, 2, 1)
        self.toOutputButton = QtGui.QPushButton('>>')
        outputButtonLayout.addWidget(self.toOutputButton)
        self.toOutputButton.setMaximumWidth(self.toOutputButton.
                                            sizeHint().height())
        self.connect(self.toOutputButton, QtCore.SIGNAL('clicked()'),
                     self.fieldToOutput)
        self.delOutputButton = QtGui.QPushButton('<<')
        outputButtonLayout.addWidget(self.delOutputButton)
        self.delOutputButton.setMaximumWidth(self.delOutputButton.\
                                             sizeHint().height())
        self.connect(self.delOutputButton, QtCore.SIGNAL('clicked()'),
                     self.delOutputField)

        outputBox = QtGui.QGroupBox(_('O&utput Format'))
        topLayout.addWidget(outputBox, 2, 2)
        outputLayout = QtGui.QVBoxLayout(outputBox)
        self.outputEdit = QtGui.QTextEdit()
        self.outputEdit.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        outputLayout.addWidget(self.outputEdit)
        self.outputEdit.setTabChangesFocus(True)
        self.connect(self.outputEdit, QtCore.SIGNAL('cursorPositionChanged()'),
                     self.setControlAvailability)
        self.connect(self.outputEdit, QtCore.SIGNAL('textChanged()'),
                     setModifiedFunction)

        topLayout.setRowStretch(1, 1)
        topLayout.setRowStretch(2, 1)

        # Advanced
        advancedStack = QtGui.QStackedWidget()
        topLayout.addWidget(advancedStack, 0, 2)
        otherBox = QtGui.QGroupBox(_('Other Field References'))
        spaceWidget = QtGui.QWidget()
        advancedStack.addWidget(spaceWidget)
        advancedStack.addWidget(otherBox)
        self.advancedWidgets.append(advancedStack)
        otherLayout = QtGui.QHBoxLayout(otherBox)
        levelLayout =  QtGui.QVBoxLayout()
        otherLayout.addLayout(levelLayout)
        levelLayout.setSpacing(0)
        levelLabel = QtGui.QLabel(_('Re&ference Level'))
        levelLayout.addWidget(levelLabel)
        levelCombo = QtGui.QComboBox()
        levelLayout.addWidget(levelCombo)
        levelLabel.setBuddy(levelCombo)
        levelCombo.addItems(OutputPage.refLevelList)
        self.connect(levelCombo, QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.changeRefLevel)
        refTypeLayout = QtGui.QVBoxLayout()
        otherLayout.addLayout(refTypeLayout)
        refTypeLayout.setSpacing(0)
        refTypeLabel = QtGui.QLabel(_('Reference Ty&pe'))
        refTypeLayout.addWidget(refTypeLabel)
        self.refTypeCombo = QtGui.QComboBox()
        refTypeLayout.addWidget(self.refTypeCombo)
        refTypeLabel.setBuddy(self.refTypeCombo)
        self.connect(self.refTypeCombo,
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.changeRefType)

    def toggleAdvanced(self, show=True):
        """Toggle state of advanced widgets,
           done with a stack to preserve spacing"""
        self.advancedWidgets[0].setCurrentIndex(show)

    def updateContent(self):
        """Update page contents from current format settings"""
        typeNames = ConfigDialog.treeFormats.nameList(True)
        self.typeCombo.blockSignals(True)
        self.typeCombo.clear()
        self.typeCombo.addItems(typeNames)
        selectNum = typeNames.index(ConfigDialog.currentType)
        self.typeCombo.setCurrentIndex(selectNum)
        self.typeCombo.blockSignals(False)

        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        if not self.refLevelFlag:
            format = currentFormat
        elif self.refLevelFlag == '!':
            format = ConfigDialog.fileInfoFormat
        elif self.refLevelFlag == '#':
            format = nodeformat.ChildCountFormat()
        else:
            format = ConfigDialog.treeFormats[self.refLevelType]
        self.fieldListBox.blockSignals(True)
        self.fieldListBox.clear()
        for field in format.fieldList:
            if field.showInDialog:
                QtGui.QTreeWidgetItem(self.fieldListBox,
                                      [field.name, _(field.typeName)])
        try:
            selectNum = format.fieldNames().index(ConfigDialog.currentField)
        except ValueError:
            selectNum = 0
        selectItem = self.fieldListBox.topLevelItem(selectNum)
        self.fieldListBox.setCurrentItem(selectItem)
        self.fieldListBox.setItemSelected(selectItem, True)
        self.fieldListBox.blockSignals(False)

        lines = currentFormat.getLines()
        self.titleEdit.blockSignals(True)
        self.titleEdit.setText(lines[0])
        self.titleEdit.end(False)
        self.titleEdit.blockSignals(False)
        self.outputEdit.blockSignals(True)
        self.outputEdit.setPlainText(u'\n'.join(lines[1:]))
        cursor = self.outputEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.outputEdit.setTextCursor(cursor)
        self.outputEdit.blockSignals(False)

        self.refTypeCombo.blockSignals(True)
        self.refTypeCombo.clear()
        self.refTypeCombo.addItems(typeNames)
        try:
            self.refTypeCombo.setCurrentIndex(typeNames.
                                              index(self.refLevelType))
        except ValueError:     # type no longer exists
            self.refLevelType = unicode(self.refTypeCombo.currentText())
        self.refTypeCombo.blockSignals(False)
        self.refTypeCombo.setEnabled(self.refLevelFlag not in ['', '!', '#'])

        self.setControlAvailability()

    def changeVirtualField(self, currentItem, prevItem):
        """Change the current format field based on a tree widget signal,
           update global if not set to alternate ref level"""
        if not currentItem:
            currentItem = self.fieldListBox.\
                        topLevelItem(self.fieldListBox.topLevelItemCount() - 1)
            self.fieldListBox.setCurrentItem(currentItem)
            self.fieldListBox.setItemSelected(currentItem, True)
        if not self.refLevelFlag:
            ConfigDialog.currentField = unicode(currentItem.text(0))

    def changeRefLevel(self, num):
        """Change the reference level based on a widget signal"""
        self.refLevelFlag = OutputPage.refLevelFlags[num]
        if self.refLevelFlag not in ['', '!', '#'] and not self.refLevelType:
            self.refLevelType = ConfigDialog.treeFormats.nameList(True)[0]
        self.updateContent()

    def changeRefType(self, num):
        """Change the reference level type based on a widget signal"""
        self.refLevelType = ConfigDialog.treeFormats.nameList(True)[num]
        self.updateContent()

    def setControlAvailability(self):
        """Set controls available based on text cursor movements"""
        titleCursorField = self.titleFieldPos()
        self.toTitleButton.setEnabled(titleCursorField == ())
        self.delTitleButton.setEnabled(len(titleCursorField) > 1)
        outputCursorField = self.outputFieldPos()
        self.toOutputButton.setEnabled(outputCursorField == ())
        self.delOutputButton.setEnabled(len(outputCursorField) > 1)

    def currentFieldSepName(self):
        """Return current field name with proper separators"""
        return u'{*%s%s*}' % (self.refLevelFlag,
                              unicode(self.fieldListBox.currentItem().text(0)))

    def fieldToTitle(self):
        """Add selected field to cursor pos in editor"""
        self.titleEdit.insert(self.currentFieldSepName())
        self.titleEdit.setFocus()

    def delTitleField(self):
        """Remove field from cursor pos in editor"""
        start, end = self.titleFieldPos()
        self.titleEdit.setSelection(start, end - start)
        self.titleEdit.insert('')

    def fieldToOutput(self):
        """Add selected field to cursor pos in editor"""
        self.outputEdit.insertPlainText(self.currentFieldSepName())
        self.outputEdit.setFocus()

    def delOutputField(self):
        """Remove field from cursor pos in editor"""
        start, end = self.outputFieldPos()
        outputCursor = self.outputEdit.textCursor()
        outputCursor.setPosition(start)
        outputCursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
        self.outputEdit.setTextCursor(outputCursor)
        self.outputEdit.insertPlainText('')

    def titleFieldPos(self):
        """Return tuple of start, end for field pattern at title cursor,
           or (None,) if selection overlaps a field end,
           or empty tuple if not found"""
        position = self.titleEdit.cursorPosition()
        start = self.titleEdit.selectionStart()
        if start < 0:
            start = position
        elif start == position:   # backward selection
            position += len(unicode(self.titleEdit.selectedText()))
        return self.fieldPosAtCursor(start, position,
                                     unicode(self.titleEdit.text()))

    def outputFieldPos(self):
        """Return tuple of start, end for field pattern at output cursor
           or (None,) if selection overlaps a field end,
           or empty tuple if not found"""
        outputCursor = self.outputEdit.textCursor()
        anchor = outputCursor.anchor()
        position = outputCursor.position()
        block = outputCursor.block()
        blockStart = block.position()
        if anchor < blockStart or anchor > blockStart + block.length():
            return (None,)      # multi-line selection
        result = self.fieldPosAtCursor(anchor - blockStart,
                                       position - blockStart,
                                       unicode(block.text()))
        if len(result) > 1:
            return (result[0] + blockStart, result[1] + blockStart)
        return result

    def fieldPosAtCursor(self, anchorPos, cursorPos, textLine):
        """Find field pattern enclosing the cursor or selection,
           return tuple of start, end if found,
           return (None,) if selection overlaps a field end,
           return empty tuple if not found"""
        for match in OutputPage.fieldPattern.finditer(textLine):
            cursorIn = match.start() < cursorPos < match.end()
            anchorIn = match.start() < anchorPos < match.end()
            if cursorIn and anchorIn:
                return (match.start(), match.end())
            if cursorIn or anchorIn:
                return (None,)
        return ()

    def readChanges(self):
        """Make changes to the format for each widget"""
        currentFormat = ConfigDialog.treeFormats[ConfigDialog.currentType]
        currentFormat.changeTitleLine(unicode(self.titleEdit.text()))
        currentFormat.changeOutputLines(unicode(self.outputEdit.
                                                toPlainText()).split('\n'))


class TitleEdit(QtGui.QLineEdit):
    """LineEdit that avoids changing the selection on focus changes"""
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)

    def focusInEvent(self, event):
        """Override to keep selection & cursor position"""
        cursorPos = self.cursorPosition()
        selectStart = self.selectionStart()
        if selectStart == cursorPos:
            selectStart = cursorPos + len(unicode(self.selectedText()))
        QtGui.QLineEdit.focusInEvent(self, event)
        self.setCursorPosition(cursorPos)
        if selectStart >= 0:
            self.setSelection(selectStart, cursorPos - selectStart)
        self.emit(QtCore.SIGNAL('focusIn'), self)

    def focusOutEvent(self, event):
        """Override to keep selection & cursor position"""
        cursorPos = self.cursorPosition()
        selectStart = self.selectionStart()
        if selectStart == cursorPos:
            selectStart = cursorPos + len(unicode(self.selectedText()))
        QtGui.QLineEdit.focusOutEvent(self, event)
        self.setCursorPosition(cursorPos)
        if selectStart >= 0:
            self.setSelection(selectStart, cursorPos - selectStart)


class FieldEntry(QtGui.QDialog):
    """Dialog for alpha-numeric and underscore text entry"""
    illegalRe = re.compile(r'[^\w_\-.]', re.U)
    def __init__(self, caption, labelText, dfltText='', badStr=[],
                 parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.text = ''
        self.badStr = badStr
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(caption)

        self.topLayout = QtGui.QVBoxLayout(self)
        label = QtGui.QLabel(labelText)
        self.topLayout.addWidget(label)
        self.entry = QtGui.QLineEdit(dfltText)
        self.topLayout.addWidget(self.entry)
        self.entry.setFocus()
        self.connect(self.entry, QtCore.SIGNAL('returnPressed()'),
                     self, QtCore.SLOT('accept()'))
        ctrlLayout = QtGui.QHBoxLayout()
        self.topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(okButton)
        self.connect(okButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))

    def accept(self):
        """Check for acceptable string before closing"""
        self.text = unicode(self.entry.text()).strip()
        error = ''
        if not self.text:
            error = _('Empty name is not acceptable')
        elif not self.text[0].isalpha():
            error = _('Name must start with a letter')
        elif self.text[:3].lower() == 'xml':
            error = _('Name cannot start with "xml"')
        elif FieldEntry.illegalRe.search(self.text):
            badChars = set(FieldEntry.illegalRe.findall(self.text))
            error = '%s: "%s"' % \
                    (_('The following characters are not allowed'),
                     unicode(''.join(badChars)))
        elif self.text in self.badStr:
            error = _('Entered name was already used')
        if error:
            QtGui.QMessageBox.warning(self, 'TreeLine', error)
            return
        return QtGui.QDialog.accept(self)


class FieldCopyEntry(FieldEntry):
    """Dialog for alpha-numeric and underscore text entry with derive option"""
    def __init__(self, dfltText='', badStr=[], allowDerive=True, parent=None):
        FieldEntry.__init__(self, _('Copy Type'), _('Enter new type name:'),
                            dfltText, badStr, parent)
        self.derived = False
        self.deriveCheck = QtGui.QCheckBox(_('Derive from original'))
        self.topLayout.insertWidget(2, self.deriveCheck)
        self.deriveCheck.setEnabled(allowDerive)

    def accept(self):
        """Check for derived and acceptable string before closing"""
        self.derived = self.deriveCheck.isChecked()
        return FieldEntry.accept(self)


class ConditionDlg(QtGui.QDialog):
    """Dialog for selecting conditional filter rules"""
    boolOp = [N_('and', 'filter bool'), N_('or', 'filter bool')]
    boolOpTransDict = dict([(_(name), name) for name in boolOp])
    def __init__(self, caption, nodeFormat, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.nodeFormat = nodeFormat
        self.fieldList = nodeFormat.fieldNames()
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(caption)
        self.topLayout = QtGui.QVBoxLayout(self)
        self.setLayout(self.topLayout)
        
        self.ruleList = [ConditionRule(1, self.fieldList)]
        self.topLayout.addWidget(self.ruleList[-1])
        self.boolList = []

        ctrlLayout = QtGui.QHBoxLayout()
        self.topLayout.addLayout(ctrlLayout)
        ctrlLayout.insertStretch(0)
        addButton = QtGui.QPushButton(_('&Add New Rule'))
        ctrlLayout.addWidget(addButton)
        self.connect(addButton, QtCore.SIGNAL('clicked()'), self.addRule)
        self.remButton = QtGui.QPushButton(_('&Remove Rule'))
        ctrlLayout.addWidget(self.remButton)
        self.connect(self.remButton, QtCore.SIGNAL('clicked()'),
                     self.removeRule)
        self.okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(self.okButton)
        self.connect(self.okButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('reject()'))
        if len(self.ruleList) < 1:
            self.remButton.setEnabled(False)

    def addRule(self):
        """Add new rule to dialog"""
        if self.ruleList:
            boolBox = QtGui.QComboBox()
            boolBox.setEditable(False)
            self.boolList.append(boolBox)
            boolBox.addItems([_(op) for op in ConditionDlg.boolOp])
            self.topLayout.insertWidget(len(self.ruleList) * 2 - 1,
                                        boolBox, 0, QtCore.Qt.AlignHCenter)
        rule = ConditionRule(len(self.ruleList) + 1, self.fieldList)
        self.ruleList.append(rule)
        self.topLayout.insertWidget(len(self.ruleList) * 2 - 2, rule)
        self.remButton.setEnabled(True)

    def removeRule(self):
        """Remove the last rule"""
        if len(self.ruleList) > 0:
            if self.boolList:
                self.boolList[-1].hide()
                del self.boolList[-1]
            self.ruleList[-1].hide()
            del self.ruleList[-1]
            self.topLayout.invalidate()
            if len(self.ruleList) < 1:
                self.remButton.setEnabled(False)

    def setConditions(self, condition):
        """Set dialog to match Condition instance"""
        while len(self.ruleList) > 1:
            self.removeRule()
        if condition:
            self.ruleList[0].setCondition(condition.conditionList[0],
                                          self.nodeFormat, self.fieldList)
        for condLine in condition.conditionList[1:]:
            self.addRule()
            self.boolList[-1].setCurrentIndex(ConditionDlg.boolOp.
                                              index(condLine.boolOper))
            self.ruleList[-1].setCondition(condLine, self.nodeFormat,
                                           self.fieldList)

    def conditional(self):
        """Return a Conditional instance for this rule set"""
        return conditional.Conditional(self.ruleText())

    def ruleText(self):
        """Return full text of this rule set"""
        textList = [rule.ruleText(self.nodeFormat) for rule in self.ruleList]
        boolList = [ConditionDlg.boolOpTransDict[unicode(box.currentText())]
                    for box in self.boolList]
        result = ''
        if textList:
            result = textList.pop(0)
        for text in textList:
            result = ' '.join((result, boolList.pop(0), text))
        return result


class ConditionRule(QtGui.QGroupBox):
    """Saves rules for filtering items"""
    oper = ['==', '<', '<=', '>', '>=', '!=',
            N_('starts with', 'filter rule'), N_('ends with', 'filter rule'),
            N_('contains', 'filter rule'), N_('True', 'filter rule'),
            N_('False', 'filter rule')]
    operTransDict = dict([(_(name), name) for name in oper])
    def __init__(self, num, fieldList, parent=None):
        QtGui.QGroupBox.__init__(self, parent)
        self.setTitle(_('Rule %d') % num)
        layout = QtGui.QHBoxLayout(self)
        self.fieldBox = QtGui.QComboBox()
        self.fieldBox.setEditable(False)
        self.fieldBox.addItems(fieldList)
        layout.addWidget(self.fieldBox)

        self.opBox = QtGui.QComboBox()
        self.opBox.setEditable(False)
        self.opBox.addItems([_(op) for op in ConditionRule.oper])
        layout.addWidget(self.opBox)
        self.connect(self.opBox, QtCore.SIGNAL('activated(const QString &)'),
                     self.changeOp)

        self.edit = QtGui.QLineEdit()
        self.edit.setMinimumWidth(80)
        layout.addWidget(self.edit)
        self.fieldBox.setFocus()

    def changeOp(self, newOp):
        """Update the dialog based on type selection change"""
        newOp = ConditionRule.operTransDict[unicode(newOp)]
        hasFields = newOp not in ('True', 'False')
        self.fieldBox.setEnabled(hasFields)
        self.edit.setEnabled(hasFields)

    def setCondition(self, condLine, nodeFormat, fieldList):
        """Set values to match ConditionLine instance"""
        try:
            fieldNum = fieldList.index(condLine.field.name)
        except ValueError:
            fieldNum = 0
        self.fieldBox.setCurrentIndex(fieldNum)
        self.opBox.setCurrentIndex(ConditionRule.oper.index(condLine.oper))
        value = condLine.field.formatEditText(condLine.value)[0]
        self.edit.setText(value)

    def ruleText(self, nodeFormat):
        """Return full text of this rule"""
        op = ConditionRule.operTransDict[unicode(self.opBox.currentText())]
        field = unicode(self.fieldBox.currentText())
        value = unicode(self.edit.text())
        value = nodeFormat.findField(field).storedText(value)[0]
        value = value.replace('\\', '\\\\').replace('"', '\\"')
        return '%s %s "%s"' % (field, op, value)


class IconSelectDlg(QtGui.QDialog):
    """Dialog for selecting icons for a format type"""
    iconList = [N_('default', 'icon name'), N_('treeline', 'icon name'),
                N_('anchor', 'icon name'), N_('arrow_1', 'icon name'),
                N_('arrow_2', 'icon name'), N_('arrow_3', 'icon name'),
                N_('arrow_4', 'icon name'), N_('arrow_5', 'icon name'),
                N_('bell', 'icon name'), N_('book_1', 'icon name'),
                N_('book_2', 'icon name'), N_('book_3', 'icon name'),
                N_('bookmark', 'icon name'), N_('bulb', 'icon name'),
                N_('bullet_1', 'icon name'), N_('bullet_2', 'icon name'),
                N_('bullet_3', 'icon name'), N_('check_1', 'icon name'),
                N_('check_2', 'icon name'), N_('check_3', 'icon name'),
                N_('clock', 'icon name'), N_('colors', 'icon name'),
                N_('date_1', 'icon name'), N_('date_2', 'icon name'),
                N_('disk', 'icon name'), N_('doc', 'icon name'),
                N_('euro', 'icon name'), N_('folder_1', 'icon name'),
                N_('folder_2', 'icon name'), N_('folder_3', 'icon name'),
                N_('gear', 'icon name'), N_('gnu', 'icon name'),
                N_('hand', 'icon name'), N_('heart', 'icon name'),
                N_('home', 'icon name'), N_('lock_1', 'icon name'),
                N_('lock_2', 'icon name'), N_('mag', 'icon name'),
                N_('mail', 'icon name'), N_('minus', 'icon name'),
                N_('misc', 'icon name'), N_('move', 'icon name'),
                N_('music', 'icon name'), N_('note', 'icon name'),
                N_('pencil', 'icon name'), N_('person', 'icon name'),
                N_('plus', 'icon name'), N_('printer', 'icon name'),
                N_('question', 'icon name'), N_('rocket', 'icon name'),
                N_('round_minus', 'icon name'), N_('round_plus', 'icon name'),
                N_('smiley_1', 'icon name'), N_('smiley_2', 'icon name'),
                N_('smiley_3', 'icon name'), N_('smiley_4', 'icon name'),
                N_('smiley_5', 'icon name'), N_('sphere', 'icon name'),
                N_('star', 'icon name'), N_('sum', 'icon name'),
                N_('table', 'icon name'), N_('task_1', 'icon name'),
                N_('task_2', 'icon name'), N_('term', 'icon name'),
                N_('text', 'icon name'), N_('trash', 'icon name'),
                N_('tux_1', 'icon name'), N_('tux_2', 'icon name'),
                N_('warning', 'icon name'), N_('wrench', 'icon name'),
                N_('write', 'icon name'), N_('x_1', 'icon name'),
                N_('x_2', 'icon name'), N_('x_3', 'icon name')]
    iconTransDict = dict([(_(name), name) for name in iconList])
    dialogSize = ()
    dialogPos = ()

    def __init__(self, nodeFormat, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.currentName = nodeFormat.iconName
        if not self.currentName or \
               self.currentName not in globalref.treeIcons.keys():
            self.currentName = globalref.treeIcons.defaultName
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('Set Data Type Icon'))
        topLayout = QtGui.QVBoxLayout(self)
        self.iconView = QtGui.QListWidget()
        self.iconView.setViewMode(QtGui.QListView.ListMode)
        self.iconView.setMovement(QtGui.QListView.Static)
        self.iconView.setResizeMode(QtGui.QListView.Adjust)
        self.iconView.setWrapping(True)
        self.iconView.setGridSize(QtCore.QSize(112, 32))
        topLayout.addWidget(self.iconView)

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        clearButton = QtGui.QPushButton(_('Clear &Select'))
        ctrlLayout.addWidget(clearButton)
        self.connect(clearButton, QtCore.SIGNAL('clicked()'),
                     self.iconView.clearSelection)
        okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(okButton)
        self.connect(okButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        self.connect(self.iconView,
                     QtCore.SIGNAL('itemDoubleClicked(QListWidgetItem*)'),
                     QtCore.SLOT('accept()'))
        if IconSelectDlg.dialogSize:
            self.resize(IconSelectDlg.dialogSize[0],
                        IconSelectDlg.dialogSize[1])
            self.move(IconSelectDlg.dialogPos[0], IconSelectDlg.dialogPos[1])
        self.loadIcons()

    def loadIcons(self):
        """Load icons from the icon source"""
        if not globalref.treeIcons.allLoaded:
            globalref.treeIcons.loadAllIcons()
        for name, icon in globalref.treeIcons.items():
            if icon:
                try:
                    transName = _(name.encode())
                except UnicodeError:
                    transName = name
                item = QtGui.QListWidgetItem(icon, transName, self.iconView)
                if name == self.currentName:
                    self.iconView.setCurrentItem(item)
        self.iconView.sortItems()
        self.show()  # req'd to make scroll to item work
        selectedItem = self.iconView.currentItem()
        if selectedItem:
            self.iconView.scrollToItem(selectedItem,
                                      QtGui.QAbstractItemView.PositionAtCenter)

    def saveSize(self):
        """Record dialog size at close"""
        IconSelectDlg.dialogSize = (self.width(), self.height())
        IconSelectDlg.dialogPos = (self.x(), self.y())

    def accept(self):
        """Save changes before closing"""
        selectedItems = self.iconView.selectedItems()
        if selectedItems:
            name = unicode(selectedItems[0].text())
            self.currentName = IconSelectDlg.iconTransDict.get(name, name)
            if self.currentName == globalref.treeIcons.defaultName:
                self.currentName = ''
        else:
            self.currentName = globalref.treeIcons.noneName
        QtGui.QDialog.accept(self)
        self.saveSize()

    def reject(self):
        """Save size before closing"""
        QtGui.QDialog.reject(self)
        self.saveSize()
