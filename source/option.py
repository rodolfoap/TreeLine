#!/usr/bin/env python

#****************************************************************************
# option.py, provides classes to read and set user preferences
#
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import sys
import os.path
import codecs
import globalref

class Option(object):
    """Stores and retrieves string options"""
    def __init__(self, dirName, keySpaces=20):
        self.path = ''
        self.pluginPath = ''
        self.iconPath = ''
        self.templatePath = ''
        if dirName:
            fileName = dirName.split('-')[0]
            if sys.platform.startswith('win'):
                self.path = unicode(os.environ.get('APPDATA', ''),
                                    sys.getfilesystemencoding())
                altPath = os.path.join(globalref.modPath, u'%s.ini' % fileName)
                if self.path and os.path.exists(self.path):
                    self.path = os.path.join(self.path, u'bellz', dirName)
                    if (os.path.exists(self.path) or
                           not os.path.exists(altPath)) and self.createDirs():
                        self.path = os.path.join(self.path,
                                                 u'%s.ini' % fileName)
                    else:
                        self.path = altPath
                else:
                    self.path = altPath
            else:
                self.path = unicode(os.environ.get('HOME', ''),
                                    sys.getfilesystemencoding())
                if self.path and os.path.exists(self.path):
                    self.path = os.path.join(self.path, u'.%s' % dirName)
                    if self.createDirs():
                        self.path = os.path.join(self.path, u'%src' % fileName)
                else:
                    self.path = ''
        self.keySpaces = keySpaces
        self.dfltDict = {}
        self.userDict = {}
        self.dictList = (self.userDict, self.dfltDict)
        self.chgList = []

    def createDirs(self):
        """Create option, plugin, icon & template directories if necessary
           and save path locations.  Return True on success."""
        try:
            if not os.path.isdir(self.path):
                if os.path.isfile(self.path):
                    os.remove(self.path)
                os.makedirs(self.path)
            self.pluginPath = os.path.join(self.path, u'plugins')
            if not os.path.isdir(self.pluginPath):
                os.makedirs(self.pluginPath)
            self.iconPath = os.path.join(self.path, u'icons')
            if not os.path.isdir(self.iconPath):
                os.makedirs(self.iconPath)
            self.templatePath = os.path.join(self.path, u'templates')
            if not os.path.isdir(self.templatePath):
                os.makedirs(self.templatePath)
        except OSError:
            self.path = ''
            self.pluginPath = ''
            self.iconPath = ''
            self.templatePath = ''
            return False
        return True

    def loadAll(self, defaultList):
        """Reads defaultList & file, writes file if required
           return true if file read"""
        self.loadSet(defaultList, self.dfltDict)
        if self.path:
            try:
                f = codecs.open(self.path, 'r', 'utf-8')
            except IOError:
                try:
                    f = codecs.open(self.path, 'w', 'utf-8')
                except IOError:
                    print 'Error - could not write to config file', \
                          self.path.encode(globalref.localTextEncoding)
                    self.path = ''
                else:
                    f.writelines([line + '\n' for line in defaultList])
                    f.close()
            else:
                self.loadSet(f.readlines(), self.userDict)
                f.close()
                return True
        return False

    def loadSet(self, list, data):
        """Reads settings from list into dict"""
        for line in list:
            line = line.split('#', 1)[0].strip()
            if line:
                item = line.split(None, 1) + ['']   # add value if blank
                data[item[0]] = item[1].strip()

    def addData(self, key, strData, storeChange=0):
        """Add new entry, add to write list if storeChange"""
        self.userDict[key] = strData
        if storeChange:
            self.chgList.append(key)

    def boolData(self, key, defaultOnly=False):
        """Returns true or false from yes or no in option data"""
        dictList = defaultOnly and (self.dfltDict,) or self.dictList
        for data in dictList:
            val = data.get(key)
            if val and val[0] in ('y', 'Y'):
                return True
            if val and val[0] in ('n', 'N'):
                return False
        print 'Option error - bool key', key, 'is not valid'
        return False

    def numData(self, key, min=None, max=None, defaultOnly=False):
        """Return float from option data"""
        dictList = defaultOnly and (self.dfltDict,) or self.dictList
        for data in dictList:
            val = data.get(key)
            if val:
                try:
                    num = float(val)
                    if (min == None or num >= min) and \
                       (max == None or num <= max):
                        return num
                except ValueError:
                    pass
        print 'Option error - float key', key, 'is not valid'
        return False

    def intData(self, key, min=None, max=None, defaultOnly=False):
        """Return int from option data"""
        dictList = defaultOnly and (self.dfltDict,) or self.dictList
        for data in dictList:
            val = data.get(key)
            if val:
                try:
                    num = int(val)
                    if (min == None or num >= min) and \
                       (max == None or num <= max):
                        return num
                except ValueError:
                    pass
        print 'Option error - int key', key, 'is not valid'
        return False

    def strData(self, key, emptyOk=0, defaultOnly=False):
        """Return string from option data"""
        dictList = defaultOnly and (self.dfltDict,) or self.dictList
        for data in dictList:
            val = data.get(key)
            if val != None:
                if val or emptyOk:
                    return val
        print 'Option error - string key', key, 'is not valid'
        return ''

    def changeData(self, key, strData, storeChange):
        """Change entry, add to write list if storeChange
           Return true if changed"""
        for data in self.dictList:
            val = data.get(key)
            if val != None:
                if strData == val:  # no change reqd
                    return False
                self.userDict[key] = strData
                if storeChange:
                    self.chgList.append(key)
                return True
        print 'Option error - key', key, 'is not valid'
        return False

    def addDefaultKey(self, key, initValue=' '):
        """Add a new value to the default dict if it isn't there,
           set the init value (set to space by default so it always
           gets overwritten wit changeData"""
        for data in self.dictList:
            if data.has_key(key):
                return
        self.dfltDict[key] = initValue

    def writeChanges(self):
        """Write any stored changes to the option file - rtn true on success"""
        if self.path and self.chgList:
            try:
                f = codecs.open(self.path, 'r', 'utf-8')
                fileList = f.readlines()
                f.close()
                for key in self.chgList[:]:
                    hitList = [line for line in fileList if
                               line.strip().split(None, 1)[:1] == [key]]
                    if not hitList:
                        hitList = [line for line in fileList if
                                   line.replace('#', ' ', 1).strip().
                                   split(None, 1)[:1] == [key]]
                    if hitList:
                        fileList[fileList.index(hitList[-1])] = '%s%s\n' % \
                                (key.ljust(self.keySpaces), self.userDict[key])
                        self.chgList.remove(key)
                for key in self.chgList:
                    fileList.append('%s%s\n' % (key.ljust(self.keySpaces),
                                                self.userDict[key]))
                f = codecs.open(self.path, 'w', 'utf-8')
                f.writelines([line for line in fileList])
                f.close()
                return True
            except IOError:
                print 'Error - could not write to config file', \
                      self.path.encode(globalref.localTextEncoding)
        return False
