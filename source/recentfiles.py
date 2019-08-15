#!/usr/bin/env python

#****************************************************************************
# recentfiles.py, classes to handle recent file lists and states
#
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import os.path
import sys
import time
from PyQt4 import QtCore, QtGui
import globalref


class RecentFileList(list):
    """A list of RecentFile objects"""
    def __init__(self):
        list.__init__(self)
        self.numEntries = globalref.options.intData('RecentFiles', 0, 99)
        self.loadList()

    def loadList(self):
        """Load recent files from options"""
        self[:] = []
        for num in range(self.numEntries):
            entry = RecentFile()
            entry.loadPath(num)
            if entry.pathIsValid():
                self.append(entry)

    def writeList(self):
        """Write list of paths to options"""
        for num in range(self.numEntries):
            try:
                entry = self[num]
            except IndexError:
                entry = RecentFile()
            entry.writePath(num)
        globalref.options.writeChanges()

    def addEntry(self, path):
        """If path is in list, move to start;
           otherwise create a new entry at the start"""
        try:
            entry = self.pop(self.index(RecentFile(path)))
        except ValueError:
            entry = RecentFile(path)
        self.insert(0, entry)
        self.updateMenu()

    def removeEntry(self, path):
        """Remove the given pathname if found"""
        try:
            self.remove(RecentFile(path))
        except ValueError:
            pass
        self.updateMenu()

    def firstPath(self):
        """Return the first valid path"""
        for entry in self:
            path = os.path.dirname(entry.path)
            if os.path.exists(path):
                return path
        return ''

    def changeNumEntries(self, numEntries):
        """Modify number of available entries"""
        for i in range(numEntries, self.numEntries):
            globalref.options.changeData(RecentFile().optionTitle(i), '', True)
            TreeState().writeState(i)
        for i in range(self.numEntries, numEntries):
            globalref.options.addDefaultKey(RecentFile().optionTitle(i))
            globalref.options.addDefaultKey(TreeState().optionTitle(i))
        self.numEntries = numEntries
        self.updateMenu()

    def updateMenu(self):
        """Refresh menu items"""
        menu = globalref.mainWin.recentFileSep.parentWidget()
        actionList = globalref.mainWin.recentFileActions
        menuLength = min(self.numEntries, len(self))
        while len(actionList) < menuLength:
            actionList.append(RecentAction(globalref.mainWin))
            menu.insertAction(globalref.mainWin.recentFileSep,
                              actionList[-1])
        while len(actionList) > menuLength:
            menu.removeAction(actionList[-1])
            del actionList[-1]
        for action, entry, num in zip(actionList, self,
                                      range(menuLength)):
            action.setPath(entry, num)

    def saveTreeState(self, treeView):
        """Set the tree state from the current file"""
        try:
            entry = self[self.index(RecentFile(globalref.docRef.fileName))]
        except ValueError:
            return
        entry.treeState.saveState(treeView)

    def restoreTreeState(self, treeView):
        """Restore the state in the current file, return True if changed"""
        try:
            entry = self[self.index(RecentFile(globalref.docRef.fileName))]
        except ValueError:
            return False
        return entry.treeState.restoreState(treeView)

    def clearTreeStates(self):
        """Remove all saved tree state data"""
        for entry in self:
            entry.treeState = TreeState()


class RecentFile(object):
    """Contains path info and creates menu actions"""
    maxEntryLength = 30
    def __init__(self, path=''):
        self.path = path
        if self.path:
            self.path = os.path.abspath(self.path)
        self.treeState = TreeState()

    def loadPath(self, num):
        """Load path from option position num"""
        self.path = globalref.options.strData(self.optionTitle(num), True)
        if self.path:
            self.path = os.path.abspath(self.path)
            self.treeState.loadState(num)

    def pathIsValid(self):
        """Return True if has a valid path"""
        return os.access(self.path.encode(sys.getfilesystemencoding()),
                         os.R_OK)

    def writePath(self, num):
        """Save path to option at position num"""
        globalref.options.changeData(self.optionTitle(num), self.path, True)
        self.treeState.writeState(num)

    def abbrevPath(self):
        """Return shortened version of path"""
        abbrevPath = self.path
        if len(self.path) > RecentFile.maxEntryLength:
            truncLength = RecentFile.maxEntryLength - 3
            pos = self.path.find(os.sep, len(self.path) - truncLength)
            if pos < 0:
                pos = len(self.path) - truncLength
            abbrevPath = '...' + self.path[pos:]
        return abbrevPath

    def optionTitle(self, num):
        """Return option key"""
        return 'RecentFile%d' % (num + 1)

    def __cmp__(self, other):
        """Compare paths"""
        return cmp(os.path.normcase(self.path), os.path.normcase(other.path))


class RecentAction(QtGui.QAction):
    """Menu item for a recent file entry"""
    def __init__(self, parent):
        QtGui.QAction.__init__(self, parent)
        self.connect(self, QtCore.SIGNAL('triggered()'), self.openItem)

    def setPath(self, recentFile, num):
        """Set menu title to abbreviated path name and add number"""
        self.setText('&%d %s' % (num + 1, recentFile.abbrevPath()))
        self.setStatusTip(recentFile.path)

    def openItem(self):
        """Execute function to open this file"""
        globalref.treeControl.recentOpen(unicode(self.statusTip()))


class TreeState(object):
    """Loads and saves the tree states of recent files"""
    def __init__(self):
        self.timeStamp = 0
        self.topNode = 0
        self.selectNodes = [0]
        self.openNodes = [0]

    def loadState(self, num):
        """Load state from option position num"""
        stateStr = globalref.options.strData(self.optionTitle(num), True)
        states = stateStr.split(':')
        try:
            self.timeStamp = int(states[0])
            self.topNode = int(states[1])
            self.selectNodes = [int(s) for s in states[2].split(',')]
            self.openNodes = [int(s) for s in states[3].split(',')]
        except (ValueError, IndexError):
            pass

    def writeState(self, num):
        """Save state to option at position num"""
        stateStr = '%d:%d:%s:%s' % (self.timeStamp, self.topNode,
                                    ','.join([str(n) for n in
                                              self.selectNodes]),
                                    ','.join([str(n) for n in self.openNodes]))
        globalref.options.changeData(self.optionTitle(num), stateStr, True)

    def saveState(self, treeView):
        """Set the state from the current file"""
        self.timeStamp = int(time.time())
        allNodes = globalref.docRef.root.descendantList(True)
        self.topNode = allNodes.index(treeView.itemAt(0, 0).docItemRef)
        self.selectNodes = [allNodes.index(item) for item in
                            globalref.docRef.selection]
        if not self.selectNodes:
            self.selectNodes = [0]
        if not allNodes[0].open:    # root closed, return default
            self.openNodes = [0]
        else:
            self.openNodes = []
            for i, node in enumerate(allNodes):
                if node.open and \
                        not [child for child in node.childList if child.open] \
                        and node.allAncestorsOpen():
                    self.openNodes.append(i)

    def restoreState(self, treeView):
        """Restore this state in the current file, return True if changed"""
        fileTimeStamp = os.stat(globalref.docRef.fileName).st_mtime
        if fileTimeStamp > self.timeStamp:  # file modified externally
            return False
        allNodes = globalref.docRef.root.descendantList(True)
        try:
            selectedNodes = [allNodes[i] for i in self.selectNodes]
        except IndexError:
            selectedNodes = [allNodes[0]]
        globalref.docRef.selection.replace(selectedNodes)
        globalref.docRef.selection.prevSelects = []
        for i in self.openNodes:
            try:
                node = allNodes[i]
                while not node.open and node != allNodes[0]:
                    node.open = True
                    node = node.parent
            except IndexError:
                pass
        globalref.updateViewAll()
        try:
            topNode = allNodes[self.topNode].viewData
            treeView.scrollToItem(topNode,
                                  QtGui.QAbstractItemView.PositionAtTop)
        except IndexError:
            pass
        return True

    def optionTitle(self, num):
        """Return option key"""
        return 'TreeState%d' % (num + 1)
