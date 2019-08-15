#!/usr/bin/env python

#****************************************************************************
# treeselection.py, stores and controls node selections for TreeLine
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#****************************************************************************

import globalref

class TreeSelection(list):
    """A list for tree node selections"""
    maxHistoryLength = 100
    def __init__(self, initList=[]):
        list.__init__(self, initList)
        self.currentItem = None  # set by GUI when changed
        if self:
            self.currentItem = self[-1]
        self.searchOpenList = []
        self.prevSelects = []
        self.nextSelects = []

    def __getslice__(self, i, j):
        """Modified to copy object with slice"""
        result = TreeSelection(list.__getslice__(self, i, j))
        result.currentItem = self.currentItem
        result.searchOpenList = self.searchOpenList[:]
        result.prevSelects = self.prevSelects[:]
        result.nextSelects = self.nextSelects[:]
        return result

    def change(self, selectList):
        """Replace selection with items in list and update view"""
        self.addToHistory()
        self[:] = selectList
        globalref.updateViewSelection()

    def replace(self, selectList):
        """Replace selection with items in list"""
        self.addToHistory()
        self[:] = selectList

    def selectEmptyCurrent(self):
        """Add currentItem to an empty selection list"""
        if not self:
            self.append(self.currentItem)

    def addOrRemove(self, item, select=True):
        """Add or remove item from selection list"""
        self.addToHistory()
        if select:
            self.append(item)
        else:
            try:
                self.remove(item)
            except ValueError:
                pass

    def openSelection(self):
        """Open ancestors of all selected items"""
        for item in self:
            ancestor = item.parent
            while ancestor:
                ancestor.open = True
                ancestor = ancestor.parent

    def changeSearchOpen(self, selectList):
        """Replace selection with items in list,
           if open search enabled, close previously selected search items,
           open new selected search items"""
        if self == selectList:
            return
        openSearch = globalref.options.boolData('OpenSearchNodes')
        if openSearch:
            for item in self.searchOpenList:
                item.open = False
                globalref.updateViewItem(item)
        self.searchOpenList = []
        for item in selectList:
            parents = item.openParents(openSearch)
            parents.reverse()  # must start with a visible (loaded) node
            self.searchOpenList.extend(parents)
        for item in self.searchOpenList:
            globalref.updateViewItem(item)
        self.addToHistory()
        self[:] = selectList
        globalref.updateViewSelection()

    def addToHistory(self):
        """Add selection list to previous selection list"""
        if self:
            self.prevSelects.append(list(self))
            if len(self.prevSelects) > TreeSelection.maxHistoryLength:
                del self.prevSelects[:5]
            self.nextSelects = []

    def restorePrevSelect(self):
        """Go back to the most recent saved selection"""
        self.validateHistory()
        if self.prevSelects:
            for item in self.prevSelects[-1]:
                item.openParents(False)
                globalref.updateViewItem(item)
            self.nextSelects.append(list(self))
            self[:] = self.prevSelects.pop(-1)
            globalref.updateViewSelection()
        else:
            globalref.updateViewMenuStat()

    def restoreNextSelect(self):
        """Go forward to the most recent saved selection"""
        self.validateHistory()
        if self.nextSelects:
            for item in self.nextSelects[-1]:
                item.openParents(False)
                globalref.updateViewItem(item)
            self.prevSelects.append(list(self))
            self[:] = self.nextSelects.pop(-1)
            globalref.updateViewSelection()
        else:
            globalref.updateViewMenuStat()

    def validateHistory(self):
        """Clear previous and next lists if no longer valid"""
        if self.prevSelects:
            for item in self.prevSelects[-1]:
                if not item.isValid():
                    self.prevSelects = []
                    break
        if self.nextSelects:
            for item in self.nextSelects[-1]:
                if not item.isValid():
                    self.nextSelects = []
                    break

    def formatNames(self):
        """Return a list of format type names used in the selection"""
        currentTypes = []
        for item in self:
            if item.formatName not in currentTypes:
                currentTypes.append(item.formatName)
        return currentTypes

    def uniqueBranches(self):
        """Return a list of unique branch top items"""
        result = []
        for item in self:
            parent = item.parent
            while parent and parent not in self:
                parent = parent.parent
            if not parent:
                result.append(item)
        return result

    def treeSelectPrev(self):
        """Select previous item"""
        item = self.currentItem.prevItem()
        if item:
            self.change([item])

    def treeSelectNext(self):
        """Select next item"""
        item = self.currentItem.nextItem()
        if item:
            self.change([item])

    def treeOpenItem(self):
        """Set selection to open"""
        if not self:
            self.change([self.currentItem])
        for item in self:
            item.open = True
            globalref.updateViewItem(item)

    def treeCloseItem(self):
        """Set selection to closed"""
        if not self:
            self.replace([self.currentItem])
        newSelects = []
        for item in self:
            if item.open and item.childList:
                if item not in newSelects:
                    newSelects.append(item)
            elif item.parent and item.parent not in newSelects:
                newSelects.append(item.parent)
        for item in newSelects:
            item.open = False
            globalref.updateViewItem(item)
        self.change([item for item in newSelects if item.allAncestorsOpen()])

    def treePrevSibling(self):
        """Select previous sibling item"""
        item = self.currentItem.prevSibling()
        if item:
            self.changeSearchOpen([item])

    def treeNextSibling(self):
        """Select next sibling item"""
        item = self.currentItem.nextSibling()
        if item:
            self.changeSearchOpen([item])

    def treeSelectParent(self):
        """Select parent item"""
        item = self.currentItem.parent
        if item:
            self.changeSearchOpen([item])

    def treeTop(self):
        """Select root item"""
        item = globalref.docRef.root
        self.change([item])

    def treeBottom(self):
        """Select last open item in tree"""
        item = globalref.docRef.root.lastDescendant(False)
        self.change([item])

    def findText(self, wordList, forward=True):
        """Select item containing words in searchStr in any field,
           starts with currentItem, return item if found"""
        fullList = globalref.docRef.root.descendantList(True)
        currentPos = fullList.index(self.currentItem)
        fullList = fullList[currentPos+1:] + fullList[:currentPos]
        if not forward:
            fullList.reverse()
        for item in fullList:
            if item.matchWords(wordList):
                self.changeSearchOpen([item])
                return item
        return None

    def findTitleText(self, searchStr):
        """Select item containing searchStr in the title,
           starts with currentItem (included in search),
           return True if found"""
        searchStr = searchStr.lower()
        next = self.currentItem
        while True:
            if next.title().lower().find(searchStr) >= 0:
                self.changeSearchOpen([next])
                return True
            next = next.nextItem(True)
            if not next:
                next = globalref.docRef.root
            if next is self.currentItem:
                return False

    def findNextTitle(self, searchStr, forward=True):
        """Select item containing searchStr in the title,
           starts with currentItem (_not_ included in search),
           return True if found"""
        searchStr = searchStr.lower()
        next = self.currentItem
        while True:
            if forward:
                next = next.nextItem(True)
                if not next:
                    next = globalref.docRef.root
            else:
                next = next.prevItem(True)
                if not next:
                    next = globalref.docRef.root.lastDescendant(True)
            if next is self.currentItem:
                return False
            if next.title().lower().find(searchStr) >= 0:
                self.changeSearchOpen([next])
                return True

    def findRefField(self, searchStr):
        """Select item containing searchStr in a line of the refField,
           starts with currentItem, return True if found"""
        next = self.currentItem
        while True:
            next = next.nextItem(True)
            if not next:
                next = globalref.docRef.root
            if next is self.currentItem:
                return False
            if next.matchRefText(searchStr):
                self.changeSearchOpen([next])
                return True

    def letterSearch(self, char, forward=True):
        """Move to the next or previous visible item starting with letter"""
        fullList = globalref.docRef.root.descendantList(False)
        currentPos = fullList.index(self.currentItem)
        fullList = fullList[currentPos+1:] + fullList[:currentPos]
        matches = [item for item in fullList
                   if item.title()[0].upper() == char]
        if matches:
            if forward:
                self.changeSearchOpen([matches[0]])
            else:
                self.changeSearchOpen([matches[-1]])
