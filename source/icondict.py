#!/usr/bin/env python

#****************************************************************************
# icondict.py, provides a class to load and store tree icons
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************

import os.path
from PyQt4 import QtGui
import globalref

class IconDict(dict):
    """Loads and stores icons by name"""
    iconExt = ['.png', '.bmp', '.ico', 'gif']
    defaultName = 'default'
    noneName = 'NoIcon'
    def __init__(self):
        dict.__init__(self, {})
        self.pathList = []
        self.subPaths = ['']
        self.allLoaded = False
        self[IconDict.noneName] = None

    def addIconPath(self, potentialPaths, subPaths=None):
        """Add first good path from potentialPaths,
           set subPaths from a list if given"""
        if subPaths:
            self.subPaths = subPaths
        for path in potentialPaths:
            for subPath in self.subPaths:
                try:
                    for name in os.listdir(os.path.join(path, subPath)):
                        pixmap = QtGui.QPixmap(os.path.join(path, subPath,
                                                            name))
                        if not pixmap.isNull():
                            self.pathList.append(path)
                            return
                except OSError:
                    pass

    def getIcon(self, name, substitute=False):
        """Return an icon matching name or the default icon"""
        try:
            return self[name]
        except KeyError:
            icon = self.loadIcon(name)
            if not icon and substitute and name != IconDict.defaultName:
                icon = self.getIcon(IconDict.defaultName)
            return icon

    def loadAllIcons(self):
        """Load all icons available in self.pathList"""
        self.clear()
        self[IconDict.noneName] = None
        for path in self.pathList:
            for subPath in self.subPaths:
                try:
                    for name in os.listdir(os.path.join(path, subPath)):
                        pixmap = QtGui.QPixmap(os.path.join(path, subPath,
                                                            name))
                        if not pixmap.isNull():
                            name = os.path.splitext(name)[0]
                            try:
                                icon = self[name]
                            except KeyError:
                                icon = QtGui.QIcon()
                                self[name] = icon
                            icon.addPixmap(pixmap)
                except OSError:
                    pass
        self.allLoaded = True

    def loadIcons(self, iconList):
        """Load icons from name list"""
        for iconName in iconList:
            self.loadIcon(iconName)

    def loadIcon(self, iconName):
        """Load icon from iconPath, add to dictionary and return the icon"""
        icon = QtGui.QIcon()
        for path in self.pathList:
            for ext in IconDict.iconExt:
                fileName = iconName + ext
                for subPath in self.subPaths:
                    pixmap = QtGui.QPixmap(os.path.join(path, subPath,
                                                        fileName))
                    if not pixmap.isNull():
                        icon.addPixmap(pixmap)
                if not icon.isNull():
                    self[iconName] = icon
                    return icon
        return None
