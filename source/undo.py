#!/usr/bin/env python

#****************************************************************************
# undo.py, provides a classes to store and execute undo & redo operations
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
from treeitem import TreeItem
import globalref


class UndoRedoStore(object):
    """Stores list of info needed for undo or redo steps"""
    def __init__(self, levels=-1):
        self.levels = levels
        if self.levels < 0:
            self.levels = globalref.options.intData('UndoLevels', 0, 999)
        self.undoList = []
        self.tmpRedoRef = None  # ref for clearing redo list when undos added

    def addUndoObj(self, obj, clearRedo=True):
        """Add undo/redo object to list, truncate if longer than levels"""
        self.undoList.append(obj)
        if self.levels:
            self.undoList = self.undoList[-self.levels:]
        else:
            self.undoList = []
        if self.tmpRedoRef and clearRedo:
            self.tmpRedoRef.undoList = []
            self.tmpRedoRef = None

    def addDataUndo(self, items, skipSame=False, clearRedo=True):
        """Syntactic sugar, adds tree item data changes,
           skips adding item if skipSame is true and a single item matches"""
        if skipSame and self.undoList and \
             isinstance(self.undoList[-1], DataUndo) and \
             len(self.undoList[-1].dataList) == 1 and \
             items == self.undoList[-1].dataList[0][0]:
            return
        self.addUndoObj(DataUndo(items), clearRedo)

    def addChildListUndo(self, items, skipSame=False, clearRedo=True):
        """Syntactic sugar, adds tree item child list changes,
           skips adding item if skipSame is true and a single item matches"""
        if skipSame and self.undoList and \
             isinstance(self.undoList[-1], ChildListUndo) and \
             len(self.undoList[-1].dataList) == 1 and \
             items == self.undoList[-1].dataList[0][0]:
            return
        self.addUndoObj(ChildListUndo(items), clearRedo)

    def addParentListUndo(self, items, skipSame=False, clearRedo=True):
        """Adds child list changes from the parents of items,
           skips adding item if skipSame is true and a single item matches"""
        if isinstance(items, TreeItem):
            items = [items]
        if skipSame and self.undoList and \
             isinstance(self.undoList[-1], ChildListUndo) and \
             len(self.undoList[-1].dataList) == 1 and len(items) == 1 and \
             items[0].parent == self.undoList[-1].dataList[0][0]:
            return
        self.addUndoObj(ChildListUndo([item.parent for item in items]),
                        clearRedo)

    def addTypeUndo(self, items, clearRedo=True):
        """Syntactic sugar, adds tree item type setting changes"""
        self.addUndoObj(TypeUndo(items), clearRedo)

    def addParamUndo(self, varList, clearRedo=True):
        """Syntactic sugar, adds general immutable param changes"""
        self.addUndoObj(ParamUndo(varList), clearRedo)

    def addFormatUndo(self, treeFormats, fileInfoFormat, fieldRenameDict,
                      typeRenameDict, clearRedo=True):
        """Syntactic sugar, adds type formatting changes"""
        self.addUndoObj(FormatUndo(treeFormats, fileInfoFormat,
                                   fieldRenameDict, typeRenameDict), clearRedo)

    def addBranchUndo(self, items, clearRedo=True):
        """Syntactic sugar, adds tree branch changes"""
        self.addUndoObj(BranchUndo(items), clearRedo)

    def undo(self, redoRef=None):
        """Restore saved state for next undo item,
           add undo item to redoRef, update selection and views"""
        if self.undoList:
            self.tmpRedoRef = redoRef
            obj = self.undoList.pop()
            obj.undo(redoRef)
            globalref.docRef.modified = obj.docModified
            globalref.docRef.selection = obj.selection
            globalref.docRef.selection.selectEmptyCurrent()
            globalref.updateViewAll()

    def removeLastUndo(self):
        """Remove most recent undo from list"""
        self.undoList = self.undoList[:-1]


class UndoBase(object):
    """Base class for undo/redo info"""
    def __init__(self):
        self.dataList = []  # list of changes
        self.selection = globalref.docRef.selection[:]  # store selected nodes
        self.docModified = globalref.docRef.modified


class DataUndo(UndoBase):
    """Info for undo/redo of tree item data changes"""
    def __init__(self, items):
        """Pass an item or list of items with data to save"""
        UndoBase.__init__(self)
        if isinstance(items, TreeItem):
            items = [items]
        for item in items:
            self.dataList.append((item, item.data.copy()))

    def undo(self, redoRef=None):
        """Restore saved state"""
        if redoRef:
            redoRef.addDataUndo([tuple[0] for tuple in self.dataList],
                                False, False)
        for item, data in self.dataList:
            item.data = data


class ChildListUndo(UndoBase):
    """Info for undo/redo of tree item child lists"""
    def __init__(self, items):
        """Pass an item or list of items with child lists to save"""
        UndoBase.__init__(self)
        if isinstance(items, TreeItem):
            items = [items]
        for item in items:
            if item:
                self.dataList.append((item, item.childList[:]))

    def undo(self, redoRef=None):
        """Restore saved state"""
        if redoRef:
            redoRef.addChildListUndo([tuple[0] for tuple in self.dataList],
                                     False, False)
        for item, childList in self.dataList:
            item.childList = childList
            for child in childList:
                child.parent = item


class TypeUndo(UndoBase):
    """Info for undo/redo of tree item type settings and data
       (for title change)"""
    def __init__(self, items):
        """Pass an item or list of items with type settings to save"""
        UndoBase.__init__(self)
        if isinstance(items, TreeItem):
            items = [items]
        for item in items:
            self.dataList.append((item, item.formatName, item.data.copy()))

    def undo(self, redoRef=None):
        """Restore saved state"""
        if redoRef:
            redoRef.addTypeUndo([tuple[0] for tuple in self.dataList], False)
        for item, format, data in self.dataList:
            item.formatName = format
            item.data = data


class ParamUndo(UndoBase):
    """Info for undo/redo of general immutable parameters"""
    def __init__(self, varList):
        """Pass a list containing a tuple for each variable,
           each tuple has the variable's owner and name string"""
        UndoBase.__init__(self)
        for varOwner, varName in varList:
            value = varOwner.__dict__[varName]
            self.dataList.append((varOwner, varName, value))

    def undo(self, redoRef=None):
        """Restore saved state"""
        if redoRef:
            redoRef.addParamUndo([tuple[:2] for tuple in self.dataList], False)
        for varOwner, varName, value in self.dataList:
            varOwner.__dict__[varName] = value


class FormatUndo(UndoBase):
    """Info for undo/redo of type formatting changes"""
    def __init__(self, treeFormats, fileInfoformat, fieldRenameDict,
                 typeRenameDict):
        """Pass the full list of type formats to save"""
        UndoBase.__init__(self)
        self.treeFormats = copy.deepcopy(treeFormats)
        self.fileInfoFormat = copy.deepcopy(fileInfoformat)
        self.fieldRenameDict = {}
        for typeName, values in fieldRenameDict.items():  # swap dict around
            self.fieldRenameDict[typeName] = []
            for origField, newField in values:
                self.fieldRenameDict[typeName].append((newField, origField))
        self.typeRenameDict = {}
        for origType, newType in typeRenameDict.items(): #swap type dict around
            self.typeRenameDict[newType] = origType

    def undo(self, redoRef=None):
        """Restore saved state"""
        if redoRef:
            redoRef.addFormatUndo(globalref.docRef.treeFormats,
                                  globalref.docRef.fileInfoFormat,
                                  self.fieldRenameDict, self.typeRenameDict,
                                  False)
        globalref.docRef.treeFormats = self.treeFormats
        globalref.docRef.fileInfoFormat = self.fileInfoFormat
        if self.typeRenameDict:
            globalref.docRef.treeFormats.renameFormats(self.typeRenameDict)
        if self.fieldRenameDict:
            globalref.docRef.treeFormats.renameFields(self.fieldRenameDict)
        globalref.docRef.treeFormats.updateDerivedTypes()
        globalref.docRef.treeFormats.updateAllLineFields()
        globalref.docRef.treeFormats.updateAutoChoices()
        globalref.docRef.treeFormats.updateUniqueID(True)


class BranchUndo(UndoBase):
    """Info for undo/redo of tree branches,
       all data, children, etc., and full format"""
    def __init__(self, items):
        """Pass an item or list of items that are the roots of the branches"""
        UndoBase.__init__(self)
        self.treeFormats = copy.deepcopy(globalref.docRef.treeFormats)
        if isinstance(items, TreeItem):
            items = [items]
        self.origItems = items
        for parent in items:
            for item in parent.descendantGen():
                self.dataList.append((item, item.data.copy(),
                                      item.childList[:]))

    def undo(self, redoRef=None):
        """Restore saved state"""
        if redoRef and len(self.dataList) == 1:
            redoRef.addBranchUndo(self.origItems, False)
        globalref.docRef.treeFormats = self.treeFormats
        globalref.docRef.treeFormats.updateDerivedTypes()
        globalref.docRef.treeFormats.updateAllLineFields()
        for item, data, childList in self.dataList:
            item.data = data
            item.childList = childList
            for child in childList:
                child.parent = item
        globalref.docRef.treeFormats.updateAutoChoices()
        globalref.docRef.treeFormats.updateUniqueID(True)
