#!/usr/bin/env python

#****************************************************************************
# treeformats.py, provides non-GUI base classes for storing node format info
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#****************************************************************************

import sys
import nodeformat
import treedoc
import globalref

class TreeFormats(dict):
    """A dict to store node formats by name in the doc"""
    rootFormatDefault = _('ROOT', 'root format default name')
    formatDefault = _('DEFAULT', 'default format name')
    fieldDefault = _('Name', 'default field name')
    textFieldName = _('Text', 'text field name')
    linkFieldName = _('Link', 'link field name')
    def __init__(self, initDict=None, setDefaults=False):
        if not initDict:
            initDict = {}
        dict.__init__(self, initDict)
        self.derivedDict = {}
        self.hasConditionals = False
        if setDefaults:
            self[TreeFormats.rootFormatDefault] = \
                    nodeformat.NodeFormat(TreeFormats.rootFormatDefault,
                                          {}, TreeFormats.fieldDefault)
            self[TreeFormats.formatDefault] = \
                    nodeformat.NodeFormat(TreeFormats.formatDefault,
                                          {}, TreeFormats.fieldDefault)
            self[TreeFormats.rootFormatDefault].childType = \
                    TreeFormats.formatDefault

    def nameList(self, excludeFileInfo=False):
        """Return sorted list of names of format items"""
        names = self.keys()
        if excludeFileInfo and nodeformat.FileInfoFormat.name in self:
            names.remove(nodeformat.FileInfoFormat.name)
        names.sort()
        return names

    def addIfMissing(self, format):
        """Add format to list if not a duplicate"""
        self.setdefault(format.name, format)

    def removeQuiet(self, format):
        """Remove from list if there"""
        try:
            del self[format.name]
        except KeyError:
            pass

    def renameFields(self, nameDict):
        """Rename data fields for all items, doesn't change node format"""
        for format in self.values():
            if format.genericType in nameDict:
                nameDict[format.name] = nameDict[format.genericType]
        for item in globalref.docRef.root.descendantGen():
            for oldName, newName in nameDict.get(item.formatName, []):
                if oldName in item.data:
                    item.data[newName] = item.data[oldName]
                    del item.data[oldName]

    def renameFormats(self, nameDict):
        """Rename format types referenced by nodes"""
        for item in globalref.docRef.root.descendantGen():
            item.formatName = nameDict.get(item.formatName, item.formatName)

    def updateAllLineFields(self):
        """Re-find fields to update format lines for any changes
           in the fieldLists"""
        for format in self.values():
            format.updateLineFields()
        globalref.docRef.fileInfoFormat.updateLineFields()

    def updateAutoChoices(self):
        """Update auto menu choices for all AutoChoice fields"""
        autoFields = {}
        for format in self.values():
            fields = format.findAutoChoiceFields()
            if fields:
                autoFields[format.name] = fields
        if autoFields:
            for item in globalref.docRef.root.descendantGen():
                for field in autoFields.get(item.formatName, []):
                    field.addChoice(item.data.get(field.name, ''))
            for fieldList in autoFields.values():
                for field in fieldList:
                    field.sortChoices()

    def updateUniqueID(self, updateAll=False):
        """Adds UniqueID fields to list to be updated,
           if updateAll, fills in any blank UniqueID fields"""
        fieldsFound = False
        for format in self.values():
            if format.findUniqueIDFields():
                fieldsFound = True
        if updateAll and fieldsFound:
            globalref.docRef.root.setDescendantUniqueID()

    def updateDerivedTypes(self):
        """Update fields for all derived types,
           update the dict containing lists of type families and
           update fields used in conditionals"""
        self.hasConditionals = False
        self.derivedDict = {}
        for format in self.values():
            if format.genericType:
                format.updateFromGeneric()
                generic = self[format.genericType]
                if format.genericType in self.derivedDict:
                    self.derivedDict[format.genericType].append(format)
                else:
                    self.derivedDict[format.genericType] = [generic, format]
            if format.conditional:
                self.hasConditionals = True
                format.conditional.setupFields(format)

    def configCopy(self, fileRef, password=''):
        """Copy the configuration from another TreeLine file"""
        if hasattr(fileRef, 'read'):
            fileName = unicode(fileRef.name, sys.getfilesystemencoding())
        else:
            fileName = fileRef
        origDocRef = globalref.docRef
        refDoc = treedoc.TreeDoc()
        if password:
            refDoc.setPassword(fileName, password)
        try:
            refDoc.readFile(fileRef)
        except:
            globalref.docRef = origDocRef
            raise
        globalref.docRef = origDocRef
        origDocRef.undoStore.addFormatUndo(self, origDocRef.fileInfoFormat,
                                           {}, {})
        for newFormat in refDoc.treeFormats.values():
            format = self.get(newFormat.name, None)
            if format:
                format.duplicateSettings(newFormat)
            else:
                self[newFormat.name] = newFormat
        self.updateAutoChoices()
        self.updateUniqueID()
        self.updateDerivedTypes()
        globalref.docRef.modified = True
        globalref.updateViewAll()

    def commonFields(self, itemList):
        """Return names of fields that are common to all nodes in list"""
        if not itemList:
            return []
        typeList = []
        for item in itemList:
            if item.formatName not in typeList:
                typeList.append(item.formatName)
        fieldNames = self[typeList.pop(0)].fieldNames()
        for type in typeList:
            typeFields = self[type].fieldNames()
            for field in fieldNames[:]:
                if field not in typeFields:
                    fieldNames.remove(field)
        return fieldNames
