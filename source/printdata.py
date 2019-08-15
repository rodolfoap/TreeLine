#!/usr/bin/env python

#****************************************************************************
# printdata.py, provides a class for printing
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

from PyQt4 import QtCore, QtGui
import nodeformat
import globalref
import optiondefaults
import output
import printdialogs


class PrintData(object):
    """Stores print data and main printing fuctions"""
    def __init__(self):
        # self.printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        self.printer = QtGui.QPrinter()
        try:
            pageSize = getattr(QtGui.QPrinter,
                               globalref.options.strData('PrintPageSize',
                                                         False))
        except AttributeError:
            pageSize = QtGui.QPrinter.Letter
        self.printer.setPageSize(pageSize)
        if globalref.options.boolData('PrintLandscape'):
            self.printer.setOrientation(QtGui.QPrinter.Landscape)
        else:
            self.printer.setOrientation(QtGui.QPrinter.Portrait)
        self.printer.setFullPage(True)
        self.printFont = None   # set by setPrintContent
        self.printList = []
        self.pageActiveLevels = []

    def getOutputFont(self):
        """Return the output view font,
           ignores use output font option"""
        return globalref.mainWin.dataOutSplit.widget(0).font()

    def getOptionPrintFont(self):
        """Return font set in option storage or None,
           ignores use output font option"""
        return globalref.mainWin.getFontFromOptions('Print')

    def setOptionPrintFont(self, font):
        """Set the print font in option storage"""
        globalref.mainWin.saveFontToOptions(font, 'Print')

    def filePrintOpt(self):
        """Set margins, page size and other options for printing"""
        dlg = printdialogs.PrintOptionsDialog(self, True, globalref.mainWin)
        if dlg.exec_() != QtGui.QDialog.Accepted:
            return

    def pageSizes(self):
        """Return a tuple of dpi, pageRect (page without margins) and
           availRect (page without margins and header/footer)"""
        dpi = min(self.printer.logicalDpiX(), self.printer.logicalDpiY())
        minXMargin = (self.printer.paperRect().width() -
                      self.printer.pageRect().width()) // 2
        minYMargin = (self.printer.paperRect().height() -
                      self.printer.pageRect().height()) // 2
        xMargin = int(globalref.options.numData('HorizMargin',
                                                optiondefaults.minPrintMargin,
                                                optiondefaults.maxPrintMargin)
                      * dpi)
        yMargin = int(globalref.options.numData('VertMargin',
                                                optiondefaults.minPrintMargin,
                                                optiondefaults.maxPrintMargin)
                      * dpi)
        xMargin = max(xMargin, minXMargin)
        yMargin = max(yMargin, minYMargin)
        pageRect = QtCore.QRect(xMargin, yMargin,
                                self.printer.width() - 2 * xMargin,
                                self.printer.height() - 2 * yMargin)
        numCols = globalref.options.intData('PrintNumCols', 1,
                                            optiondefaults.maxNumCol)
        colSpacing = globalref.options.numData('PrintColSpace', 0.0,
                                               optiondefaults.maxPrintMargin)
        colSpacing = int(dpi * colSpacing)
        colWidth = (pageRect.width() - colSpacing * (numCols - 1)) // numCols
        lineHeight = QtGui.QFontMetrics(self.printFont, self.printer).\
                     lineSpacing()
        headerHt = globalref.docRef.fileInfoFormat.getHeaderFooter(True) and \
                   2 * lineHeight or 0
        footerHt = globalref.docRef.fileInfoFormat.getHeaderFooter(False) and \
                   2 * lineHeight or 0
        availRects = []
        for colNum in range(numCols):
            colStart = xMargin + colNum * (colSpacing + colWidth)
            rect = QtCore.QRect(colStart, yMargin + headerHt, colWidth,
                                pageRect.height() - headerHt - footerHt)
            availRects.append(rect)
        return (dpi, pageRect, availRects)

    def textHeight(self, text, width):
        """Returns height of rich text in printer setup"""
        # subtract one pixel for roundoff error
        doc = self.document(text, width - 1)
        layout = doc.documentLayout()
        layout.setPaintDevice(self.printer)
        return layout.documentSize().height()

    def document(self, text, width):
        """Return a QTextDocument for height calculation & painting"""
        doc = QtGui.QTextDocument()
        doc.setHtml(text)
        doc.setDefaultFont(self.printFont)
        frameFormat = doc.rootFrame().frameFormat()
        frameFormat.setBorder(0)
        frameFormat.setMargin(0)
        frameFormat.setPadding(0)
        doc.rootFrame().setFrameFormat(frameFormat)
        # TODO change to width setting only after Qt 4.2
        doc.setPageSize(QtCore.QSizeF(width, width * 10000))
        return doc

    def setPrintContent(self):
        """Add tree content to self.printList"""
        self.printFont = self.getOptionPrintFont()
        if not self.printFont or \
                    globalref.options.boolData('PrintUseOutputFont'):
            self.printFont = self.getOutputFont()
        dpi, pageRect, availRects = self.pageSizes()
        addBranches = True
        mode = globalref.options.strData('PrintWhat')
        if mode == 'tree':
            nodeList = [globalref.docRef.root]
        elif mode == 'node':
            nodeList = globalref.docRef.selection
            addBranches = False
        else:        # branches
            nodeList = globalref.docRef.selection.uniqueBranches()
        includeRoot = globalref.options.boolData('PrintRoot')
        openOnly = globalref.options.boolData('PrintOpenOnly')
        indent = globalref.options.numData('PrintIndentOffset', 0.0,
                                           optiondefaults.maxPrintIndent)
        indent = int(dpi * indent)
        outGroup = output.OutputGroup()
        if addBranches:
            for node in nodeList:
                branch = node.outputItemList(includeRoot, openOnly)
                outGroup.extend(branch)
        else:
            outGroup.extend([node.outputItem() for node in nodeList])
        outGroup.setHeights(self.textHeight, availRects[0].width(), indent)
        if globalref.options.boolData('PrintLines'):
            self.pageActiveLevels = []
        else:
            self.pageActiveLevels = None
        firstChildAdjust = globalref.options.boolData('PrintKeepFirstChild') \
                           and 0.2 or 0.0
        self.printList = outGroup.splitPages(availRects[0].height(),
                                             self.pageActiveLevels,
                                             firstChildAdjust)
        for group in self.printList:
            group.joinPrefixItems()
            group.addPrefix()
            if globalref.docRef.lineBreaks:
                group.addBreaks()
        numCols = len(availRects)
        maxPage = len(self.printList) // numCols
        if len(self.printList) % numCols:
            maxPage += 1
        globalref.docRef.fileInfoItem.data[nodeformat.FileInfoFormat.
                                           numPagesFieldName] = repr(maxPage)

    def filePrintPreview(self):
        """Show a preview of the printing results"""
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.setPrintContent()
        numPages = int(globalref.docRef.fileInfoItem.data[nodeformat.
                                                          FileInfoFormat.
                                                          numPagesFieldName])
        dlg = printdialogs.PrintPrevDlg(self, numPages,
                                        self.printer.paperRect(),
                                        self.printPage, globalref.mainWin)
        dlg.resize(globalref.options.intData('PrintPrevXSize', 10, 10000),
                   globalref.options.intData('PrintPrevYSize', 10, 10000))
        if globalref.options.boolData('SaveWindowGeom'):
            dlg.move(globalref.options.intData('PrintPrevXPos', 0, 10000),
                     globalref.options.intData('PrintPrevYPos', 0, 10000))
        QtGui.QApplication.restoreOverrideCursor()
        result = dlg.exec_()
        if globalref.options.boolData('SaveWindowGeom'):
            globalref.options.changeData('PrintPrevXSize', dlg.width(), True)
            globalref.options.changeData('PrintPrevYSize', dlg.height(), True)
            globalref.options.changeData('PrintPrevXPos', dlg.x(), True)
            globalref.options.changeData('PrintPrevYPos', dlg.y(), True)
            globalref.options.writeChanges()
        if result == QtGui.QDialog.Accepted:
            self.filePrint()

    def printPage(self, pageNum, painter):
        """Send pageNum to painter"""
        dpi, pageRect, availRects = self.pageSizes()
        numCols = len(availRects)
        painter.setFont(self.printFont)
        globalref.docRef.fileInfoItem.data[nodeformat.FileInfoFormat.
                                           pageNumFieldName] = repr(pageNum)
        addLines = globalref.options.boolData('PrintLines')
        indent = globalref.options.numData('PrintIndentOffset', 0.0,
                                           optiondefaults.maxPrintIndent)
        indent = int(dpi * indent)
        xLineDelta = indent // 2
        yLineDelta = 0
        if globalref.docRef.spaceBetween:
            yLineDelta = QtGui.QFontMetrics(self.printFont).ascent()
        linePos = QtGui.QFontMetrics(self.printFont).ascent() // 2 + 1
        header = globalref.docRef.fileInfoFormat.getHeaderFooter(True)
        if header:
            doc = self.document(header, pageRect.width())
            layout = doc.documentLayout()
            painter.save()
            painter.translate(pageRect.left(), pageRect.top())
            layout.draw(painter,
                        QtGui.QAbstractTextDocumentLayout.PaintContext())
            painter.restore()
        for colNum, colRect in enumerate(availRects):
            listIndex = (pageNum - 1) * numCols + colNum
            if listIndex >= len(self.printList) or \
                      not self.printList[listIndex]:
                break
            yPos = colRect.top()
            lineStarts = [yPos] * (self.printList[listIndex][0].level + 1)
            for item in self.printList[listIndex]:
                xPos = colRect.left() + indent * item.level
                doc = self.document(''.join(item.textLines),
                                    colRect.right() - xPos)
                layout = doc.documentLayout()
                painter.save()
                painter.translate(xPos, yPos)
                layout.draw(painter,
                            QtGui.QAbstractTextDocumentLayout.PaintContext())
                painter.restore()
                if addLines:
                    if item.level:
                        painter.drawLine(xPos - xLineDelta, yPos + linePos,
                                         xPos - 2, yPos + linePos)
                        if len(lineStarts) > item.level:
                            yPrev = lineStarts[item.level]
                            lineStarts = lineStarts[:item.level]
                        else:
                            yPrev = yPos - yLineDelta
                        painter.drawLine(xPos - xLineDelta, yPrev,
                                         xPos - xLineDelta, yPos + linePos)
                        lineStarts.append(yPos + linePos)
                    else:
                        lineStarts = [0]
                yPos += item.height
            if addLines and listIndex < len(self.pageActiveLevels):
                for level in self.pageActiveLevels[listIndex]:
                    xPos = colRect.left() + indent * level - xLineDelta
                    if len(lineStarts) > level:
                        yStart = lineStarts[level]
                    else:
                        yStart = colRect.top()
                    painter.drawLine(xPos, yStart, xPos, colRect.bottom())
        footer = globalref.docRef.fileInfoFormat.getHeaderFooter(False)
        if footer:
            doc = self.document(footer, pageRect.width())
            layout = doc.documentLayout()
            painter.save()
            lineHeight = QtGui.QFontMetrics(self.printFont, self.printer).\
                         lineSpacing()
            painter.translate(pageRect.left(), pageRect.bottom() - lineHeight)
            layout.draw(painter,
                        QtGui.QAbstractTextDocumentLayout.PaintContext())
            painter.restore()

    def filePrint(self):
        """Print file starting from selected item"""
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.setPrintContent()
        QtGui.QApplication.restoreOverrideCursor()
        printDlg = QtGui.QPrintDialog(self.printer, globalref.mainWin)
        maxPage = int(globalref.docRef.fileInfoItem.data[nodeformat.
                                                         FileInfoFormat.
                                                         numPagesFieldName])
        printDlg.setMinMax(1, maxPage)
        if printDlg.exec_() != QtGui.QDialog.Accepted:
            return
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.setPrintContent()
        minPage = max(self.printer.fromPage(), 1)
        maxPage = int(globalref.docRef.fileInfoItem.data[nodeformat.
                                                         FileInfoFormat.
                                                         numPagesFieldName])
        if 1 <= self.printer.toPage() < maxPage:
            maxPage = self.printer.toPage()
        if self.printer.pageOrder() == QtGui.QPrinter.FirstPageFirst:
            seq = range(minPage, maxPage + 1)
        else:
            seq = range(maxPage, minPage - 1, -1)
        painter = QtGui.QPainter()
        if not painter.begin(self.printer):
            QtGui.QApplication.restoreOverrideCursor()
            QtGui.QMessageBox.warning(globalref.mainWin, 'TreeLine',
                                      _('Error initializing printer'))
            return
        self.printPage(seq.pop(0), painter)
        for num in seq:
            self.printer.newPage()
            self.printPage(num, painter)
        painter.end()
        QtGui.QApplication.restoreOverrideCursor()
