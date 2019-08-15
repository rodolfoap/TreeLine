#!/usr/bin/env python

#****************************************************************************
# treerightviews.py, provides classes for the title edit & data output views
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
import webbrowser
import xml.sax.saxutils
from PyQt4 import QtCore, QtGui
import treedoc
import optiondefaults
import globalref


class DataOutView(QtGui.QTextBrowser):
    """Right pane view of database info, read-only"""
    def __init__(self, showChildren=True, parent=None):
        QtGui.QTextBrowser.__init__(self, parent)
        self.showChildren = showChildren
        self.showDescendants = False
        self.oldViewHeight = 0
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.connect(self, QtCore.SIGNAL('highlighted(const QString&)'),
                     self.showLink)

    def updateView(self):
        """Replace contents with selected item data list"""
        path = os.path.dirname(globalref.docRef.fileName)
        self.setSearchPaths([path])
        sep = globalref.docRef.lineBreaks and u'<br />\n' or u'\n'
        if self.showChildren and len(globalref.docRef.selection) == 1:
            if self.showDescendants:
                indent = globalref.options.intData('IndentOffset', 0,
                                                optiondefaults.maxIndentOffset)
                outGroup = globalref.docRef.selection[0].outputItemList(False)
                if globalref.docRef.lineBreaks:
                    outGroup.addInnerBreaks()
                outGroup.joinPrefixItems()
                outGroup.addPrefix()
                for item in outGroup:
                    item.addAbsoluteIndents(indent)
                lines = []
                for item in outGroup:
                    lines.extend(item.textLines)
                self.setHtml(u'\n'.join(lines))
            else:
                self.setHtml(sep.join(globalref.docRef.selection[0].
                             formatChildText(True, True)))
        elif not self.showChildren and globalref.docRef.selection:
            self.setHtml(sep.join(globalref.docRef.selection[0].
                         formatTextItems(globalref.docRef.selection,
                                         True, True)))
        else:
            self.setHtml('')

    def setSource(self, url):
        """Called when user clicks on a URL, opens an internal link or
           an external browser"""
        name = xml.sax.saxutils.unescape(unicode(url.toString()),
                                         treedoc.unEscDict)
        if name.startswith(u'#'):
            globalref.docRef.selection.findRefField(name[1:])
        elif name.startswith(u'exec:'):
            if not globalref.options.boolData('EnableExecLinks'):
                QtGui.QMessageBox.warning(self, 'TreeLine',
                                         _('Executable links are not enabled'))
            elif sys.platform.startswith('win'):
                name = name.replace("'", '"')
                # windows interprets first quoted text as a title!
                os.system(u'start "tl exec" %s' % name[5:])
            else:
                os.system(u'%s &' % name[5:])
        else:
            name = name.replace(' ', '%20')
            try:
                webbrowser.open(name, True)
            except:
                pass

    def showLink(self, text):
        """Send link text to the statusbar"""
        text = xml.sax.saxutils.unescape(unicode(text), treedoc.unEscDict)
        globalref.setStatusBar(text)

    def copyAvail(self):
        """Return True if there is selected text"""
        return self.textCursor().hasSelection()

    def cut(self):
        """Substitute copy for cut command"""
        self.copy()

    def highlightWords(self, wordList):
        """Highlight given search terms in thsi view"""
        if not hasattr(QtGui.QTextEdit, 'ExtraSelection'):
            return    # requires Qt 4.2 or greater
        # backColor = self.palette().highlight()
        backColor = self.palette().brush(QtGui.QPalette.Active,
                                         QtGui.QPalette.Highlight)
        foreColor = self.palette().brush(QtGui.QPalette.Active,
                                         QtGui.QPalette.HighlightedText)
        selections = []
        for word in wordList:
            while self.find(word):
                extraSel = QtGui.QTextEdit.ExtraSelection()
                extraSel.cursor = self.textCursor()
                extraSel.format.setBackground(backColor)
                extraSel.format.setForeground(foreColor)
                selections.append(extraSel)
            cursor = QtGui.QTextCursor(self.document())
            self.setTextCursor(cursor)  # reset main cursor/selection
        self.setExtraSelections(selections)

    def scrollPage(self, numPages=1):
        """Scrolls down by numPages (negative for up)
           leaving a one-line overlap"""
        delta = self.height() - 2 * self.frameWidth() - \
                self.fontMetrics().height()
        if delta > 0:
            scrollBar = self.verticalScrollBar()
            scrollBar.setValue(scrollBar.value() + numPages * delta)

    def resizeEvent(self, event):
        """Update view if was collaped by splitter"""
        if (event.oldSize().height() == 0 and event.size().height()) or \
           (event.oldSize().width() == 0 and event.size().width()):
            self.setEnabled(True)
            self.updateView()
        return QtGui.QTextBrowser.resizeEvent(self, event)


class TitleListView(QtGui.QTextEdit):
    """Right pane list edit view, titles of current selection or its children"""
    def __init__(self, showChildren=True, parent=None):
        QtGui.QTextEdit.__init__(self, parent)
        self.showChildren = showChildren
        self.oldViewHeight = 0
        self.setAcceptRichText(False)
        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.setTabChangesFocus(True)
        self.connect(self, QtCore.SIGNAL('textChanged()'), self.readChange)

    def updateView(self):
        """Replace contents with selected item child list"""
        items = []
        if self.showChildren and len(globalref.docRef.selection) == 1:
            items = globalref.docRef.selection[0].childList
        elif not self.showChildren and globalref.docRef.selection:
            items = globalref.docRef.selection
        self.blockSignals(True)
        if items:
            self.setPlainText(u'\n'.join([item.title() for item in items]))
        else:
            self.clear()
        self.blockSignals(False)

    def readChange(self):
        """Update doc from edit view contents"""
        textList = filter(None, [u' '.join(text.split()) for text in
                                 unicode(self.toPlainText()).split('\n')])
        if self.showChildren and len(globalref.docRef.selection) == 1:
            globalref.docRef.selection[0].editChildList(textList)
            globalref.docRef.selection.validateHistory()
        elif not self.showChildren and \
                 len(globalref.docRef.selection) == len(textList):
            for item, text in zip(globalref.docRef.selection, textList):
                if item.title() != text and item.setTitle(text, True):
                    globalref.updateViewItem(item)
        else:
            self.updateView()  # remove illegal changes
        globalref.updateViewMenuStat()

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

    def scrollPage(self, numPages=1):
        """Scrolls down by numPages (negative for up)
           leaving a one-line overlap"""
        delta = self.height() - 2 * self.frameWidth() - \
                self.fontMetrics().height()
        if delta > 0:
            scrollBar = self.verticalScrollBar()
            scrollBar.setValue(scrollBar.value() + numPages * delta)

    def keyPressEvent(self, event):
        """Bind keys to functions"""
        if not self.showChildren and event.key() in \
                (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            pass
        else:
            QtGui.QTextEdit.keyPressEvent(self, event)

    def resizeEvent(self, event):
        """Update view if was collaped by splitter"""
        if (event.oldSize().height() == 0 and event.size().height()) or \
           (event.oldSize().width() == 0 and event.size().width()):
            self.setEnabled(True)
            self.updateView()
        return QtGui.QTextEdit.resizeEvent(self, event)
