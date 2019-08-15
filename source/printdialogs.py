#!/usr/bin/env python

#****************************************************************************
# printdialogs.py, provides a print preview and print settings dialogs
#
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
import configdialog
import nodeformat
import optiondefaults
import globalref

stdWinFlags = QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint | \
              QtCore.Qt.WindowSystemMenuHint


class PrintPrevDlg(QtGui.QDialog):
    """Provides a generic print preview with page controls"""
    def __init__(self, printData, numPages, paperRect, pageCmd, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('Print Preview'))

        self.printData = printData
        self.curPage = 1
        self.minPage = 1
        self.maxPage = numPages
        topLayout = QtGui.QVBoxLayout(self)
        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)

        self.prevButton  = QtGui.QPushButton(_('P&rev. Page'))
        ctrlLayout.addWidget(self.prevButton)
        self.connect(self.prevButton, QtCore.SIGNAL('clicked()'),
                     self.prevPage)

        self.nextButton  = QtGui.QPushButton(_('&Next Page'))
        ctrlLayout.addWidget(self.nextButton)
        self.connect(self.nextButton, QtCore.SIGNAL('clicked()'),
                     self.nextPage)

        self.statusLabel = QtGui.QLabel('')
        ctrlLayout.addWidget(self.statusLabel, 1)
        self.statusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.statusLabel.setFrameStyle(QtGui.QFrame.Panel |
                                       QtGui.QFrame.Sunken)
        self.statusLabel.setMargin(2)

        previewButton = QtGui.QPushButton(_('Print Option&s...'))
        ctrlLayout.addWidget(previewButton)
        self.connect(previewButton, QtCore.SIGNAL('clicked()'),
                     self.showOptions)

        printButton  = QtGui.QPushButton(_('&Print...'))
        ctrlLayout.addWidget(printButton)
        self.connect(printButton, QtCore.SIGNAL('clicked()'), self.accept)

        cancelButton  = QtGui.QPushButton(_('&Close'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self.reject)

        self.preview = PrintPrev(paperRect, pageCmd)
        topLayout.addWidget(self.preview, 1)

        self.updatePageNum()

    def updatePageNum(self):
        """Enable/disable prev & next buttons, update status label 
           and preview"""
        self.prevButton.setEnabled(self.curPage > self.minPage)
        self.nextButton.setEnabled(self.curPage < self.maxPage)
        self.statusLabel.setText(_('Page %(current)i of %(max)i') %
                                 {'current':self.curPage, 'max':self.maxPage})
        self.preview.setPageNum(self.curPage)

    def prevPage(self):
        """Go to previous page"""
        if self.curPage > self.minPage:
            self.curPage -= 1
            self.updatePageNum()

    def nextPage(self):
        """Go to next page"""
        if self.curPage < self.maxPage:
            self.curPage += 1
            self.updatePageNum()

    def showOptions(self):
        """Show a modal options dialog"""
        dlg = PrintOptionsDialog(self.printData, False, self)
        self.setUpdatesEnabled(False)  # halt repaint until settings consistent
        if dlg.exec_() == QtGui.QDialog.Accepted:
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.printData.setPrintContent()
            self.maxPage = int(globalref.docRef.fileInfoItem.data[nodeformat.
                                                            FileInfoFormat.
                                                            numPagesFieldName])
            if self.curPage > self.maxPage:
                self.curPage = self.maxPage
            self.preview.paperRect = self.printData.printer.paperRect()
            self.updatePageNum()
            QtGui.QApplication.restoreOverrideCursor()
        self.setUpdatesEnabled(True)


class PrintPrev(QtGui.QWidget):
    """Provides a widget for the paper"""
    def __init__(self, paperRect, pageCmd, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

        self.paperRect = paperRect
        self.pageCmd = pageCmd
        self.pageNum = 0

    def sizeHint(self):
        """Return preferred size"""
        return QtCore.QSize(250, 450)

    def setPageNum(self, pageNum):
        """Set new page number and update"""
        self.pageNum = pageNum
        self.update()

    def paintEvent(self, event):
        """Paint the current page"""
        paint = QtGui.QPainter(self)
        viewRect = paint.viewport()
        paperViewSize = self.paperRect.size()  # used for aspect ratio only
        paperViewSize.scale(viewRect.size(), QtCore.Qt.KeepAspectRatio)
        leftMargin = (viewRect.width() - paperViewSize.width()) // 2
        topMargin = (viewRect.height() - paperViewSize.height()) // 2
        paperViewRect = QtCore.QRect(leftMargin, topMargin,
                                     paperViewSize.width(),
                                     paperViewSize.height())
        paint.setWindow(self.paperRect)
        paint.setViewport(paperViewRect)
        paint.fillRect(self.paperRect, QtGui.QBrush(QtCore.Qt.white))
        self.pageCmd(self.pageNum, paint)


class PrintOptionsDialog(QtGui.QDialog):
    """Base dialog for print configuration"""
    def __init__(self, printData, showExtraButtons=True, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('Print Options'))
        self.printData = printData

        topLayout = QtGui.QVBoxLayout(self)
        self.setLayout(topLayout)

        tabs = QtGui.QTabWidget()
        topLayout.addWidget(tabs)
        generalPage = GeneralPage()
        tabs.addTab(generalPage, _('&General Options'))
        pageSetupPage = PageSetupPage(self.printData.printer)
        tabs.addTab(pageSetupPage, _('&Page Setup'))
        fontPage = FontPage(self.printData)
        tabs.addTab(fontPage, _('&Font Selection'))
        headerPage = HeaderPage()
        tabs.addTab(headerPage, _('&Header/Footer'))
        self.tabPages = [generalPage, pageSetupPage, fontPage, headerPage]

        ctrlLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(ctrlLayout)
        ctrlLayout.addStretch(0)
        if showExtraButtons:
            previewButton =  QtGui.QPushButton(_('Print Pre&view...'))
            ctrlLayout.addWidget(previewButton)
            self.connect(previewButton, QtCore.SIGNAL('clicked()'),
                         self.preview)
            printButton = QtGui.QPushButton(_('P&rint...'))
            ctrlLayout.addWidget(printButton)
            self.connect(printButton, QtCore.SIGNAL('clicked()'),
                         self.quickPrint)
        okButton = QtGui.QPushButton(_('&OK'))
        ctrlLayout.addWidget(okButton)
        self.connect(okButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('accept()'))
        cancelButton = QtGui.QPushButton(_('&Cancel'))
        ctrlLayout.addWidget(cancelButton)
        self.connect(cancelButton, QtCore.SIGNAL('clicked()'), self,
                     QtCore.SLOT('reject()'))

    def quickPrint(self):
        """Accept this dialog and go to print dialog"""
        self.accept()
        self.printData.filePrint()

    def preview(self):
        """Accept this dialog and go to print preview dialog"""
        self.accept()
        self.printData.filePrintPreview()

    def accept(self):
        """Store results before closing dialog"""
        for page in self.tabPages:
            page.saveChanges()
        globalref.options.writeChanges()
        QtGui.QDialog.accept(self)

class GeneralPage(QtGui.QWidget):
    """Misc print option dialog page"""
    printWhat = ['tree', 'branch', 'node']
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        topLayout = QtGui.QGridLayout(self)
        self.setLayout(topLayout)

        whatGroupBox = QtGui.QGroupBox(_('What to print'))
        topLayout.addWidget(whatGroupBox, 0, 0)
        whatLayout = QtGui.QVBoxLayout(whatGroupBox)
        self.whatButtons = QtGui.QButtonGroup(self)
        treeButton = QtGui.QRadioButton(_('&Entire tree'))
        self.whatButtons.addButton(treeButton,
                                   GeneralPage.printWhat.index('tree'))
        whatLayout.addWidget(treeButton)
        branchButton = QtGui.QRadioButton(_('Selected &branches'))
        self.whatButtons.addButton(branchButton,
                                   GeneralPage.printWhat.index('branch'))
        whatLayout.addWidget(branchButton)
        nodeButton = QtGui.QRadioButton(_('Selected &nodes'))
        self.whatButtons.addButton(nodeButton,
                                   GeneralPage.printWhat.index('node'))
        whatLayout.addWidget(nodeButton)
        setting = globalref.options.strData('PrintWhat')
        try:
            self.whatButtons.button(GeneralPage.printWhat.
                                    index(setting)).setChecked(True)
        except ValueError:
            self.whatButtons.button(0).setChecked(True)
        self.connect(self.whatButtons, QtCore.SIGNAL('buttonClicked(int)'),
                     self.updateCmdAvail)

        optionBox = QtGui.QGroupBox(_('Features'))
        topLayout.addWidget(optionBox, 0, 1)
        optionLayout = QtGui.QVBoxLayout(optionBox)
        self.linesButton = QtGui.QCheckBox(_('Draw &lines to children'))
        optionLayout.addWidget(self.linesButton)
        self.linesButton.setChecked(globalref.options.boolData('PrintLines'))
        self.rootButton = QtGui.QCheckBox(_('&Include root node'))
        optionLayout.addWidget(self.rootButton)
        self.rootButton.setChecked(globalref.options.boolData('PrintRoot'))
        self.openOnlyButton = QtGui.QCheckBox(_('Only open no&de children'))
        optionLayout.addWidget(self.openOnlyButton)
        self.openOnlyButton.setChecked(globalref.options.
                                       boolData('PrintOpenOnly'))
        self.widowButton = QtGui.QCheckBox(_('&Keep first child with parent'))
        optionLayout.addWidget(self.widowButton)
        self.widowButton.setChecked(globalref.options.
                                    boolData('PrintKeepFirstChild'))
        topLayout.setRowStretch(1, 1)

    def updateCmdAvail(self):
        """Update options available"""
        if GeneralPage.printWhat[self.whatButtons.checkedId()] == 'node':
            self.rootButton.setChecked(False)
            self.rootButton.setEnabled(False)
            self.openOnlyButton.setChecked(False)
            self.openOnlyButton.setEnabled(False)
        else:
            self.rootButton.setEnabled(True)
            self.openOnlyButton.setEnabled(True)

    def saveChanges(self):
        """Update option data with current dialog settings"""
        globalref.options.changeData('PrintWhat',
                                     GeneralPage.printWhat[self.whatButtons.
                                                           checkedId()], True)
        globalref.options.changeData('PrintLines',
                                     self.linesButton.isChecked() and
                                     'yes' or 'no', True)
        globalref.options.changeData('PrintRoot',
                                     self.rootButton.isChecked() and
                                     'yes' or 'no', True)
        globalref.options.changeData('PrintOpenOnly',
                                     self.openOnlyButton.isChecked() and
                                     'yes' or 'no', True)
        globalref.options.changeData('PrintKeepFirstChild',
                                    self.widowButton.isChecked() and
                                    'yes' or 'no', True)


class PageSetupPage(QtGui.QWidget):
    """Page setup print option dialog page"""
    pageSizes = [u'Letter', u'Legal', u'Tabloid', u'A3', u'A4', u'A5',
                 u'Comm10E', u'C5E', u'DLE']
    pageSizeDescr = [_('Letter (8.5 x 11 in.)'), _('Legal (8.5 x 14 in.)'),
                     _('Tabloid (11 x 17 in.)'), _('A3 (279 x 420 mm)'),
                     _('A4 (210 x 297 mm)'), _('A5 (148 x 210 mm)'),
                     _('#10 Envelope (4.125 x 9.5 in.)'),
                     _('C5 Envelope (163 x 229 mm)'),
                     _('DL Envelope (110 x 22 mm)')]
    units = [u'inch', u'centimeter', u'millimeter']
    unitNames = [_('inches'), _('centimeters'), _('millimeters')]
    unitValues = {'inch': 1.0, 'centimeter': 2.54, 'millimeter': 25.4}
    def __init__(self, printer, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.printer = printer
        topLayout = QtGui.QVBoxLayout(self)
        self.setLayout(topLayout)
        horizLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(horizLayout)

        leftLayout = QtGui.QVBoxLayout()
        horizLayout.addLayout(leftLayout)

        paperGroup = QtGui.QGroupBox(_('Paper &Size'))
        leftLayout.addWidget(paperGroup)
        paperLayout = QtGui.QVBoxLayout(paperGroup)
        self.paperBox = QtGui.QComboBox()
        paperLayout.addWidget(self.paperBox)
        self.paperBox.addItems(PageSetupPage.pageSizeDescr)
        sizeList = [getattr(QtGui.QPrinter, name) for name in
                    PageSetupPage.pageSizes]
        try:
            sizeNum = sizeList.index(self.printer.pageSize())
        except ValueError:
            sizeNum = 0
        self.paperBox.setCurrentIndex(sizeNum)

        orientGroup = QtGui.QGroupBox(_('Orientation'))
        leftLayout.addWidget(orientGroup)
        orientLayout = QtGui.QVBoxLayout(orientGroup)
        self.portraitButton = QtGui.QRadioButton(_('&Portrait'))
        orientLayout.addWidget(self.portraitButton)
        self.landscapeButton = QtGui.QRadioButton(_('&Landscape'))
        orientLayout.addWidget(self.landscapeButton)
        if self.printer.orientation() == QtGui.QPrinter.Landscape:
            self.landscapeButton.setChecked(True)
        else:
            self.portraitButton.setChecked(True)

        unitsGroup = QtGui.QGroupBox(_('&Units'))
        leftLayout.addWidget(unitsGroup)
        unitsLayout = QtGui.QVBoxLayout(unitsGroup)
        self.unitsBox = QtGui.QComboBox()
        unitsLayout.addWidget(self.unitsBox)
        self.unitsBox.addItems(PageSetupPage.unitNames)
        self.currentUnit = globalref.options.strData('PrintUnits', False)
        try:
            unitNum = PageSetupPage.units.index(self.currentUnit)
        except ValueError:
            self.currentUnit = u'inch'
            unitNum = 0
        self.unitsBox.setCurrentIndex(unitNum)
        self.connect(self.unitsBox, QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.changeUnits)

        rightLayout = QtGui.QVBoxLayout()
        horizLayout.addLayout(rightLayout)

        columnGroup = QtGui.QGroupBox(_('Columns'))
        rightLayout.addWidget(columnGroup)
        columnLayout = QtGui.QGridLayout(columnGroup)
        numLabel = QtGui.QLabel(_('&Number of columns'))
        columnLayout.addWidget(numLabel, 0, 0)
        self.columnSpin = QtGui.QSpinBox()
        columnLayout.addWidget(self.columnSpin, 0, 1)
        numLabel.setBuddy(self.columnSpin)
        self.columnSpin.setMinimum(1)
        self.columnSpin.setMaximum(optiondefaults.maxNumCol)
        self.columnSpin.setValue(globalref.options.intData('PrintNumCols', 1,
                                 optiondefaults.maxNumCol))

        self.spaceLabel = QtGui.QLabel()
        columnLayout.addWidget(self.spaceLabel, 1, 0)
        self.columnSpaceSpin = QtGui.QDoubleSpinBox()
        columnLayout.addWidget(self.columnSpaceSpin, 1, 1)
        self.spaceLabel.setBuddy(self.columnSpaceSpin)
        self.columnSpaceSpin.setMinimum(0.0)
        self.columnSpace = globalref.options.numData('PrintColSpace', 0.0,
                                                     optiondefaults.
                                                     maxPrintMargin)

        offsetGroup = QtGui.QGroupBox(_('Offsets'))
        rightLayout.addWidget(offsetGroup)
        offsetLayout = QtGui.QGridLayout(offsetGroup)
        self.indentLabel = QtGui.QLabel()
        offsetLayout.addWidget(self.indentLabel, 0, 0)
        self.indentSpin = QtGui.QDoubleSpinBox()
        offsetLayout.addWidget(self.indentSpin, 0, 1)
        self.indentLabel.setBuddy(self.indentSpin)
        self.indentSpin.setMinimum(0.0)
        self.indent = globalref.options.numData('PrintIndentOffset', 0.0,
                                                optiondefaults.maxPrintIndent)

        self.horizLabel = QtGui.QLabel()
        offsetLayout.addWidget(self.horizLabel, 1, 0)
        self.horizMarginSpin = QtGui.QDoubleSpinBox()
        offsetLayout.addWidget(self.horizMarginSpin, 1, 1)
        self.horizLabel.setBuddy(self.horizMarginSpin)
        self.horizMargin = globalref.options.numData('HorizMargin',
                                                 optiondefaults.minPrintMargin,
                                                 optiondefaults.maxPrintMargin)

        self.vertLabel = QtGui.QLabel()
        offsetLayout.addWidget(self.vertLabel, 2, 0)
        self.vertMarginSpin = QtGui.QDoubleSpinBox()
        offsetLayout.addWidget(self.vertMarginSpin, 2, 1)
        self.vertLabel.setBuddy(self.vertMarginSpin)
        self.vertMargin = globalref.options.numData('VertMargin',
                                                optiondefaults.minPrintMargin,
                                                optiondefaults.maxPrintMargin)
        self.writeFloatValues()
        topLayout.addStretch()

    def saveChanges(self):
        """Update option data with current dialog settings"""
        pageSizeName = PageSetupPage.pageSizes[self.paperBox.currentIndex()]
        pageSize = getattr(QtGui.QPrinter, pageSizeName)
        self.printer.setPageSize(pageSize)
        globalref.options.changeData('PrintPageSize', pageSizeName, True)

        if self.portraitButton.isChecked():
            self.printer.setOrientation(QtGui.QPrinter.Portrait)
            globalref.options.changeData('PrintLandscape', 'no', True)
        else:
            self.printer.setOrientation(QtGui.QPrinter.Landscape)
            globalref.options.changeData('PrintLandscape', 'yes', True)

        globalref.options.changeData('PrintUnits', self.currentUnit, True)
        globalref.options.changeData('PrintNumCols',
                                     repr(self.columnSpin.value()), True)
        self.readFloatValues()
        globalref.options.changeData('PrintColSpace', repr(self.columnSpace),
                                     True)
        globalref.options.changeData('PrintIndentOffset', repr(self.indent),
                                     True)
        globalref.options.changeData('HorizMargin', repr(self.horizMargin),
                                     True)
        globalref.options.changeData('VertMargin', repr(self.vertMargin), True)

    def writeFloatValues(self):
        """Convert and write float values to the spin boxes"""
        factor = PageSetupPage.unitValues[self.currentUnit]
        stepSize = int(factor * 2) / 10.0
        decimals = 2
        if self.currentUnit == 'millimeter':
            decimals = 1
        unitText = PageSetupPage.unitNames[PageSetupPage.units.
                                           index(self.currentUnit)]

        self.columnSpaceSpin.setMaximum(optiondefaults.maxPrintMargin * factor)
        self.columnSpaceSpin.setSingleStep(stepSize)
        self.columnSpaceSpin.setDecimals(decimals)
        self.columnSpaceSpin.setValue(self.columnSpace * factor)
        self.spaceLabel.setText(_('Space &between columns (%s)') % unitText)

        self.indentSpin.setMaximum(optiondefaults.maxPrintIndent * factor)
        self.indentSpin.setSingleStep(stepSize)
        self.indentSpin.setDecimals(decimals)
        self.indentSpin.setValue(self.indent * factor)
        self.indentLabel.setText(_('Child &indent offset (%s)') % unitText)

        self.horizMarginSpin.setMinimum(optiondefaults.minPrintMargin * factor)
        self.horizMarginSpin.setMaximum(optiondefaults.maxPrintMargin * factor)
        self.horizMarginSpin.setSingleStep(stepSize)
        self.horizMarginSpin.setDecimals(decimals)
        self.horizMarginSpin.setValue(self.horizMargin * factor)
        self.horizLabel.setText(_('Horizontal page &margins (%s)') % unitText)

        self.vertMarginSpin.setMinimum(optiondefaults.minPrintMargin * factor)
        self.vertMarginSpin.setMaximum(optiondefaults.maxPrintMargin * factor)
        self.vertMarginSpin.setSingleStep(stepSize)
        self.vertMarginSpin.setDecimals(decimals)
        self.vertMarginSpin.setValue(self.vertMargin * factor)
        self.vertLabel.setText(_('Vertical page m&argins (%s)') % unitText)

    def readFloatValues(self):
        """Read and convert float values from the spin boxes"""
        factor = PageSetupPage.unitValues[self.currentUnit]
        self.columnSpace = self.columnSpaceSpin.value() / factor
        self.indent = self.indentSpin.value() / factor
        self.horizMargin = self.horizMarginSpin.value() / factor
        self.vertMargin = self.vertMarginSpin.value() / factor

    def changeUnits(self, unitNum):
        """Change the current unit based on a signal"""
        self.readFloatValues()
        self.currentUnit = PageSetupPage.units[unitNum]
        self.writeFloatValues()


class SmallListWidget(QtGui.QListWidget):
    """ListWidget with a smaller size hint"""
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self, parent)

    def sizeHint(self):
        """Return smaller width"""
        return QtCore.QSize(100, 80)


class FontPage(QtGui.QWidget):
    """Font selection print option dialog page"""
    def __init__(self, printData, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.printData = printData
        self.outputFont = self.printData.getOutputFont()
        self.currentFont = self.printData.getOptionPrintFont()
        if not self.currentFont:
            self.currentFont = self.outputFont

        topLayout = QtGui.QVBoxLayout(self)
        self.setLayout(topLayout)
        defaultBox = QtGui.QGroupBox(_('Default Font'))
        topLayout.addWidget(defaultBox)
        defaultLayout = QtGui.QVBoxLayout(defaultBox)
        self.outputCheck = QtGui.QCheckBox(_('Use &Data Output font'))
        defaultLayout.addWidget(self.outputCheck)
        self.outputCheck.setChecked(globalref.options.
                                    boolData('PrintUseOutputFont'))
        self.connect(self.outputCheck, QtCore.SIGNAL('clicked(bool)'),
                     self.setFontSelectAvail)

        self.fontBox = QtGui.QGroupBox(_('Select Font'))
        topLayout.addWidget(self.fontBox)
        fontLayout = QtGui.QGridLayout(self.fontBox)
        spacing = fontLayout.spacing()
        fontLayout.setSpacing(0)

        label = QtGui.QLabel(_('&Font'))
        fontLayout.addWidget(label, 0, 0)
        label.setIndent(2)
        self.familyEdit = QtGui.QLineEdit()
        fontLayout.addWidget(self.familyEdit, 1, 0)
        self.familyEdit.setReadOnly(True)
        self.familyList = SmallListWidget()
        fontLayout.addWidget(self.familyList, 2, 0)
        label.setBuddy(self.familyList)
        self.familyEdit.setFocusProxy(self.familyList)
        fontLayout.setColumnMinimumWidth(1, spacing)
        families = [unicode(fam) for fam in QtGui.QFontDatabase().families()]
        families.sort(lambda x,y: cmp(x.lower(), y.lower()))
        self.familyList.addItems(families)
        self.connect(self.familyList,
                     QtCore.SIGNAL('currentItemChanged(QListWidgetItem*, '\
                                   'QListWidgetItem*)'), self.updateFamily)

        label = QtGui.QLabel(_('Font st&yle'))
        fontLayout.addWidget(label, 0, 2)
        label.setIndent(2)
        self.styleEdit = QtGui.QLineEdit()
        fontLayout.addWidget(self.styleEdit, 1, 2)
        self.styleEdit.setReadOnly(True)
        self.styleList = SmallListWidget()
        fontLayout.addWidget(self.styleList, 2, 2)
        label.setBuddy(self.styleList)
        self.styleEdit.setFocusProxy(self.styleList)
        fontLayout.setColumnMinimumWidth(3, spacing)
        self.connect(self.styleList,
                     QtCore.SIGNAL('currentItemChanged(QListWidgetItem*, '\
                                   'QListWidgetItem*)'), self.updateStyle)

        label = QtGui.QLabel(_('&Size'))
        fontLayout.addWidget(label, 0, 4)
        label.setIndent(2)
        self.sizeEdit = QtGui.QLineEdit()
        fontLayout.addWidget(self.sizeEdit, 1, 4)
        self.sizeEdit.setFocusPolicy(QtCore.Qt.ClickFocus)
        validator = QtGui.QIntValidator(1, 512, self)
        self.sizeEdit.setValidator(validator)
        self.sizeList = SmallListWidget()
        fontLayout.addWidget(self.sizeList, 2, 4)
        label.setBuddy(self.sizeList)
        self.connect(self.sizeList,
                     QtCore.SIGNAL('currentItemChanged(QListWidgetItem*, '\
                                   'QListWidgetItem*)'), self.updateSize)

        fontLayout.setColumnStretch(0, 38)
        fontLayout.setColumnStretch(2, 24)
        fontLayout.setColumnStretch(4, 10)

        sampleBox = QtGui.QGroupBox(_('Sample'))
        topLayout.addWidget(sampleBox)
        sampleLayout = QtGui.QVBoxLayout(sampleBox)
        self.sampleEdit = QtGui.QLineEdit()
        sampleLayout.addWidget(self.sampleEdit)
        self.sampleEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.sampleEdit.setText('AaBbCcDdEeFfGg...TtUuVvWvXxYyZz')
        self.sampleEdit.setFixedHeight(self.sampleEdit.sizeHint().height() * 2)

        self.setFontSelectAvail()

    def setFontSelectAvail(self):
        """Disable font selection if default is checked"""
        if self.outputCheck.isChecked():
            font = self.readFont()
            if font:
                self.currentFont = font
            self.setFont(self.outputFont)
            self.fontBox.setEnabled(False)
        else:
            self.setFont(self.currentFont)
            self.fontBox.setEnabled(True)

    def setFont(self, font):
        """Set the font selector to the given font"""
        fontInfo = QtGui.QFontInfo(font)
        family = fontInfo.family()
        matches = self.familyList.findItems(family, QtCore.Qt.MatchExactly)
        if matches:
            self.familyList.setCurrentItem(matches[0])
            self.familyList.scrollToItem(matches[0],
                                         QtGui.QAbstractItemView.PositionAtTop)
        style = QtGui.QFontDatabase().styleString(fontInfo)
        matches = self.styleList.findItems(style, QtCore.Qt.MatchExactly)
        if matches:
            self.styleList.setCurrentItem(matches[0])
            self.styleList.scrollToItem(matches[0])
        size = repr(fontInfo.pointSize())
        matches = self.sizeList.findItems(size, QtCore.Qt.MatchExactly)
        if matches:
            self.sizeList.setCurrentItem(matches[0])
            self.sizeList.scrollToItem(matches[0])

    def updateFamily(self, currentItem, previousItem):
        """Update the family edit box and adjust the style and size options"""
        family = unicode(currentItem.text())
        self.familyEdit.setText(family)
        if self.familyEdit.hasFocus():
            self.familyEdit.selectAll()
        prevStyle = unicode(self.styleEdit.text())
        prevSize = unicode(self.sizeEdit.text())
        fontDb = QtGui.QFontDatabase()
        styles = [unicode(style) for style in fontDb.styles(family)]
        self.styleList.clear()
        self.styleList.addItems(styles)
        if prevStyle:
            try:
                num = styles.index(prevStyle)
            except ValueError:
                num = 0
            self.styleList.setCurrentRow(num)
            self.styleList.scrollToItem(self.styleList.currentItem())
        sizes = [repr(size) for size in fontDb.pointSizes(family)]
        self.sizeList.clear()
        self.sizeList.addItems(sizes)
        if prevSize:
            try:
                num = sizes.index(prevSize)
            except ValueError:
                num = 0
            self.sizeList.setCurrentRow(num)
            self.sizeList.scrollToItem(self.sizeList.currentItem())
            self.updateSample()

    def updateStyle(self, currentItem, previousItem):
        """Update the style edit box"""
        if currentItem:
            style = unicode(currentItem.text())
            self.styleEdit.setText(style)
            if self.styleEdit.hasFocus():
                self.styleEdit.selectAll()
            self.updateSample()

    def updateSize(self, currentItem, previousItem):
        """Update the size edit box"""
        if currentItem:
            size = unicode(currentItem.text())
            self.sizeEdit.setText(size)
            if self.sizeEdit.hasFocus():
                self.sizeEdit.selectAll()
            self.updateSample()

    def updateSample(self):
        """Update the font sample edit font"""
        font = self.readFont()
        if font:
            self.sampleEdit.setFont(font)

    def readFont(self):
        """Return the selected font or None"""
        family = unicode(self.familyEdit.text())
        style = unicode(self.styleEdit.text())
        size = unicode(self.sizeEdit.text())
        if family and style and size:
            return QtGui.QFontDatabase().font(family, style, int(size))
        return None

    def saveChanges(self):
        """Update option data with current dialog settings"""
        if self.outputCheck.isChecked():
            globalref.options.changeData('PrintUseOutputFont', 'yes', True)
            self.printData.printFont = self.outputFont
        else:
            globalref.options.changeData('PrintUseOutputFont', 'no', True)
            font = self.readFont()
            if font:
                self.currentFont = font
            self.printData.setOptionPrintFont(self.currentFont)
            self.printData.printFont = self.currentFont


class FieldListWidget(QtGui.QTreeWidget):
    """TreeWidget with a smaller size hint"""
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.setRootIsDecorated(False)
        self.setColumnCount(2)
        self.setHeaderLabels([_('Name'), _('Type')])

    def sizeHint(self):
        """Return smaller width"""
        return QtCore.QSize(150, 60)


class HeaderPage(QtGui.QWidget):
    """Header/footer print option dialog page"""
    names = [_('&Header Left'), _('Header C&enter'), _('He&ader Right'),
             _('Footer &Left'), _('Footer Ce&nter'), _('Footer R&ight')]
    fieldPattern = re.compile('{\*.*?\*}')
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.fileInfoFormat = copy.deepcopy(globalref.docRef.fileInfoFormat)
        self.fileInfoFormatModified = False

        topLayout = QtGui.QGridLayout(self)
        self.setLayout(topLayout)
        fieldBox = QtGui.QGroupBox(_('Fiel&ds'))
        topLayout.addWidget(fieldBox, 0, 0, 3, 1)
        fieldLayout = QtGui.QVBoxLayout(fieldBox)
        self.fieldListWidget = FieldListWidget()
        fieldLayout.addWidget(self.fieldListWidget)
        fieldFormatButton = QtGui.QPushButton(_('Field Forma&t'))
        fieldLayout.addWidget(fieldFormatButton)
        self.connect(fieldFormatButton, QtCore.SIGNAL('clicked()'),
                     self.fieldFormat)

        self.addFieldButton = QtGui.QPushButton('>>')
        topLayout.addWidget(self.addFieldButton, 0, 1)
        self.addFieldButton.setMaximumWidth(self.addFieldButton.sizeHint().
                                            height())
        self.connect(self.addFieldButton, QtCore.SIGNAL('clicked()'),
                     self.addField)
        self.delFieldButton = QtGui.QPushButton('<<')
        topLayout.addWidget(self.delFieldButton, 1, 1)
        self.delFieldButton.setMaximumWidth(self.delFieldButton.sizeHint().
                                            height())
        self.connect(self.delFieldButton, QtCore.SIGNAL('clicked()'),
                     self.delField)

        headerFooterBox = QtGui.QGroupBox(_('Header and Footer'))
        topLayout.addWidget(headerFooterBox, 0, 2, 2, 1)
        headerFooterLayout = QtGui.QGridLayout(headerFooterBox)
        spacing = headerFooterLayout.spacing()
        headerFooterLayout.setSpacing(0)
        self.textEdits = []
        for num, name in enumerate(HeaderPage.names):
            if num < 3:
                row = 1
                col = num * 2
            else:
                row = 4
                col = (num - 3) * 2
            label = QtGui.QLabel(name)
            headerFooterLayout.addWidget(label, row - 1, col)
            label.setIndent(2)
            lineEdit = configdialog.TitleEdit()
            headerFooterLayout.addWidget(lineEdit, row, col)
            label.setBuddy(lineEdit)
            self.textEdits.append(lineEdit)
            self.connect(lineEdit,
                         QtCore.SIGNAL('cursorPositionChanged(int, int)'),
                         self.setButtonAvail)
            self.connect(lineEdit, QtCore.SIGNAL('focusIn'),
                         self.setCurrentEditor)
        headerFooterLayout.setColumnMinimumWidth(1, spacing)
        headerFooterLayout.setColumnMinimumWidth(3, spacing)
        headerFooterLayout.setRowMinimumHeight(2, spacing)
        self.loadFields()
        self.loadText()
        self.focusedEditor = self.textEdits[0]
        self.setButtonAvail()

    def setButtonAvail(self):
        """Update button availability"""
        currentFieldPos = self.currentFieldPos()
        self.addFieldButton.setEnabled(currentFieldPos == ())
        self.delFieldButton.setEnabled(len(currentFieldPos) > 1)

    def setCurrentEditor(self, sender):
        """Set focusedEditor based on editor focus change signal"""
        self.focusedEditor = sender
        self.setButtonAvail()

    def loadFields(self, selNum=0):
        """Load list with field names"""
        self.fieldListWidget.clear()
        for field in self.fileInfoFormat.fieldList:
            QtGui.QTreeWidgetItem(self.fieldListWidget,
                                  [field.name, _(field.typeName)])
        self.fieldListWidget.setItemSelected(self.fieldListWidget.
                                             topLevelItem(selNum), True)

    def loadText(self):
        """Load text into editors"""
        lines = self.fileInfoFormat.getLines()
        lines.extend([''] * (6 - len(lines)))
        for editor, line in zip(self.textEdits, lines):
            editor.blockSignals(True)
            editor.setText(line)
            editor.blockSignals(False)

    def addField(self):
        """Add selected field to active header"""
        fieldName = unicode(self.fieldListWidget.selectedItems()[0].text(0))
        text = u'{*!%s*}' % fieldName
        editor = self.focusedEditor
        editor.insert(text)
        editor.setFocus()

    def delField(self):
        """Remove field at cursor from active header"""
        start, end = self.currentFieldPos()
        editor = self.focusedEditor
        editor.setSelection(start, end - start)
        editor.insert('')
        editor.setFocus()

    def currentFieldPos(self):
        """Return tuple of start, end for field at cursorPos in focusedEditor
           or (None,) if selection overlaps a field end,
           or empty tuple if not found"""
        textLine = unicode(self.focusedEditor.text())
        cursorPos = self.focusedEditor.cursorPosition()
        anchorPos = self.focusedEditor.selectionStart()
        if anchorPos < 0:
            anchorPos = cursorPos
        elif anchorPos == cursorPos:  # backward selection
            cursorPos += len(unicode(self.focusedEditor.selectedText()))
        for match in HeaderPage.fieldPattern.finditer(textLine):
            cursorIn = match.start() < cursorPos < match.end()
            anchorIn = match.start() < anchorPos < match.end()
            if cursorIn and anchorIn:
                return (match.start(), match.end())
            if cursorIn or anchorIn:
                return (None,)
        return ()

    def fieldFormat(self):
        """Show the dialog to change field formats"""
        fieldName = unicode(self.fieldListWidget.selectedItems()[0].text(0))
        dlg = HeaderFieldFormatDialog(fieldName, self.fileInfoFormat, self)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            if dlg.modified:
                self.fileInfoFormatModified = True

    def saveChanges(self):
        """Update option data with current dialog settings"""
        newLines = [unicode(editor.text()) for editor in self.textEdits]
        prevLines = self.fileInfoFormat.getLines()
        prevLines.extend([''] * (6 - len(prevLines)))
        self.fileInfoFormat.lineList = []
        for num, (newLine, prevLine) in enumerate(zip(newLines, prevLines)):
            if newLine:
                self.fileInfoFormat.insertLine(newLine, num)
            if newLine != prevLine:
                self.fileInfoFormatModified = True
        if self.fileInfoFormatModified:
            globalref.docRef.undoStore.addFormatUndo(globalref.docRef.
                                                     treeFormats,
                                                     globalref.docRef.
                                                     fileInfoFormat,
                                                     {}, {})
            globalref.docRef.treeFormats[self.fileInfoFormat.name] = \
                             self.fileInfoFormat
            globalref.docRef.fileInfoFormat = self.fileInfoFormat
            globalref.docRef.treeFormats.updateAllLineFields()
            globalref.docRef.modified = True
            globalref.updateViewMenuStat()
            self.fileInfoFormatModified = False


class HeaderFieldFormatDialog(QtGui.QDialog):
    """Dialog to modify file info field formats used in headers and footers"""
    def __init__(self, fieldName, fileInfoFormat, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.field = fileInfoFormat.findField(fieldName)
        self.fileInfoFormat = fileInfoFormat
        self.modified = False

        self.setWindowFlags(stdWinFlags)
        self.setWindowTitle(_('Field Format for "%s"') % fieldName)
        topLayout = QtGui.QVBoxLayout(self)
        self.setLayout(topLayout)
        horizLayout = QtGui.QHBoxLayout()
        topLayout.addLayout(horizLayout)

        extraBox = QtGui.QGroupBox(_('Extra Text'))
        horizLayout.addWidget(extraBox)
        extraLayout = QtGui.QVBoxLayout(extraBox)
        spacing = extraLayout.spacing()
        extraLayout.setSpacing(0)
        prefixLabel = QtGui.QLabel(_('&Prefix'))
        extraLayout.addWidget(prefixLabel)
        self.prefixEdit = QtGui.QLineEdit()
        extraLayout.addWidget(self.prefixEdit)
        prefixLabel.setBuddy(self.prefixEdit)
        extraLayout.addSpacing(spacing)
        extraLayout.addStretch(1)
        suffixLabel = QtGui.QLabel(_('Suffi&x'))
        extraLayout.addWidget(suffixLabel)
        self.suffixEdit = QtGui.QLineEdit()
        extraLayout.addWidget(self.suffixEdit)
        suffixLabel.setBuddy(self.suffixEdit)

        rightLayout = QtGui.QVBoxLayout()
        horizLayout.addLayout(rightLayout)
        self.formatBox = QtGui.QGroupBox(_('O&utput Format'))
        rightLayout.addWidget(self.formatBox)
        formatLayout = QtGui.QHBoxLayout(self.formatBox)
        self.formatEdit = QtGui.QLineEdit()
        formatLayout.addWidget(self.formatEdit)
        self.helpButton = QtGui.QPushButton(_('Format &Help'))
        formatLayout.addWidget(self.helpButton)
        self.connect(self.helpButton, QtCore.SIGNAL('clicked()'),
                     self.formatHelp)

        self.handleBox = QtGui.QGroupBox(_('Content Text Handling'))
        rightLayout.addWidget(self.handleBox)
        handleLayout = QtGui.QVBoxLayout(self.handleBox)
        self.htmlButton = QtGui.QRadioButton(_('Allow HT&ML rich text'))
        handleLayout.addWidget(self.htmlButton)
        self.plainButton = QtGui.QRadioButton(_('Plai&n text with '\
                                                'line breaks'))
        handleLayout.addWidget(self.plainButton)

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

        self.prefixEdit.setText(self.field.prefix)
        self.suffixEdit.setText(self.field.suffix)
        self.formatEdit.setText(self.field.format)
        self.htmlButton.setChecked(self.field.html)
        self.plainButton.setChecked(not self.field.html)

        self.formatBox.setEnabled(self.field.defaultFormat != '')
        self.handleBox.setEnabled(self.field.htmlOption)

    def formatHelp(self):
        """Provide format help menu based on button signal"""
        menu = QtGui.QMenu(self)
        self.formatDict = {}
        for item in self.field.formatMenuList:
            if item:
                descr, key = item
                self.formatDict[descr] = key
                menu.addAction(descr)
            else:
                menu.addSeparator()
        menu.popup(self.helpButton.
                   mapToGlobal(QtCore.QPoint(0, self.helpButton.height())))
        self.connect(menu, QtCore.SIGNAL('triggered(QAction*)'),
                     self.insertFormat)

    def insertFormat(self, action):
        """Insert format text from id into edit box"""
        self.formatEdit.insert(self.formatDict[unicode(action.text())])

    def accept(self):
        """Set changes after OK is hit"""
        prefix = unicode(self.prefixEdit.text())
        if self.field.prefix != prefix:
            self.field.prefix = prefix
            self.modified = True
        suffix = unicode(self.suffixEdit.text())
        if self.field.suffix != suffix:
            self.field.suffix = suffix
            self.modified = True
        format = unicode(self.formatEdit.text())
        if self.field.format != format:
            self.field.format = format
            self.modified = True
        if self.field.htmlOption:
            html = self.htmlButton.isChecked()
            if self.field.html != html:
                self.field.html = html
                self.modified = True
        QtGui.QDialog.accept(self)
