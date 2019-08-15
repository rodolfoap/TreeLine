#!/usr/bin/env python

#****************************************************************************
# plugininterface.py, provides an interface class for plugin extension modules
#
# TreeLine, an information storage program
# Copyright (C) 2006, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#*****************************************************************************


"""Plugin Interface Rules

   Plugins are python files located in the plugins directory
   (<prefix>/lib/treeline/plugins/ on Linux or
   TreeLine\lib\plugins\ on Windows).

   Plugins must define a function named "main" that takes an instance of the
   PluginInterface class as its only argument.  The function should initialize
   the plugin.  It is called after the TreeLine GUI is initialized (with a new
   file) but before any other files are opened.  The return value of the
   function is stored by TreeLine to avoid garbage collection of the
   reference (although this shouldn't be necessary for non-trivial plugins).

   There should be a module doc string defined by the plugin.  The first line
   is used as the plugin listing in Help->About Plugins.  It should contain the
   plugin name and a very brief description.

   To avoid problems with plugins breaking when TreeLine is revised, the plugin
   API is restricted to the methods of the PluginInterface class.  References
   from within the method code and elsewhere in TreeLine code should not be
   used.  Exceptions to this rule include certain data members of node objects
   (childList, parent and data) and the interface's mainWin data member (to be
   used only as a parent for new Qt objects).  Of course, if a method returns
   a Qt object, the normal Qt API is available.

   There are methods that setup callback functions for various TreeLine
   operations.  Probably the most useful is the view update callback, which is
   called any time something changes in TreeLine requiring view or control
   availability updates.

   Plugins used with windows binary installations are limited to the Python
   modules that are used somewhere in TreeLine itself.  No other modules are
   available, with the exception of urllib2, which is specifically included in
   the binary for plugin use.
"""

import sys
import os.path
import tempfile
from PyQt4 import QtCore, QtGui
import treedoc
import nodeformat
import optiondefaults
import globalref


class PluginInterface(object):
    """Defines the available interface for the plugins"""
    def __init__(self, mainWin):
        self.mainWin = mainWin   # may be used in plugin as widget parent only
        self.viewUpdateCallbacks = []  # internal use only
        self.dataChangeCallbacks = []  # internal use only
        self.fileNewCallbacks = []     # internal use only
        self.fileOpenCallbacks = []    # internal use only
        self.fileSaveCallbacks = []    # internal use only

    def pluginPath(self):
        """Return path of this plugin's directory"""
        try:
            frame = sys._getframe(1)
            fileName = frame.f_code.co_filename
        finally:
            del frame
        return os.path.dirname(fileName)

    def getLanguage(self):
        """Return language code used by TreeLine for translations"""
        return globalref.lang

    #*************************************************************************
    #  Node Interfaces:
    #*************************************************************************

    def getCurrentNode(self):
        """Return a reference to the currently active node"""
        return globalref.docRef.selection.currentItem

    def getSelectedNodes(self):
        """Return a list of currently selected nodes"""
        return list(globalref.docRef.selection)

    def changeSelection(self, newSelectList):
        """Change tree selections, last item in newSelectList becomes the
           current item, views are updated"""
        globalref.docRef.selection.change(newSelectList)

    def getRootNode(self):
        """Return a reference to the root node"""
        return globalref.docRef.root

    def getNodeChildList(self, node):
        """Return a list of node's child nodes,
           this method provided for completeness - 
           node.childList may be used directly"""
        return node.childList

    def getNodeParent(self, node):
        """Return node's parent node or None if node is root,
           this method provided for completeness -
           node.parent may be used directly"""
        return node.parent

    def getNodeDescendantList(self, node):
        """Return a list containing the current node and all of its
           descendant nodes"""
        return node.descendantList(True)

    def addChildNode(self, parent, text=u'New', pos=-1):
        """Add new child before position, -1 is at end - return new item"""
        return parent.addChild(text, pos)

    def insertSibling(self, siblingNode, text=u'New', inAfter=False):
        """Add new sibling before or after sibling - return new item"""
        return siblingNode.insertSibling(text, inAfter)

    def setNodeOpenClosed(self, node, setOpen=True):
        """Open children in tree if open is True,
           close children if False"""
        node.open = setOpen

    def getNodeDataDict(self, node):
        """Return a dictionary containing the node's raw field data
           field names are the dictionary keys, the data is unicode text,
           this method provided for completeness -
           node.data may be used directly"""
        return node.data

    def getNodeTitle(self, node):
        """Return the formatted unicode text for the node's title
           as shown in the tree"""
        return node.title()

    def setNodeTitle(self, node, titleText):
        """Set the node's title to titleText by modifying the field data used
           in the title format,
           returns True if successful, False otherwise"""
        return node.setTitle(titleText)

    def getNodeOutput(self, node, lineSep='<br />\n'):
        """Return the formatted unicode text for the node's output,
           separate lines using lineSep"""
        return lineSep.join(node.formatText())

    def getChildNodeOutput(self, node, lineSep='<br />\n'):
        """Return the formatted unicode text for the node children's output,
           separate lines using lineSep"""
        return lineSep.join(node.formatChildText())

    def getFieldOutput(self, node, fieldName):
        """Return formatted text for the given fieldName data"""
        field = node.nodeFormat().findField(fieldName)
        if field:
            return node.nodeFormat().fieldText(field, node)
        return ''

    def getNodeFormatName(self, node):
        """Return the format type name for the given node"""
        return node.formatName

    def setNodeFormat(self, node, formatName):
        """Set the given node to the given node format type"""
        if formatName in globalref.docRef.treeFormats:
            node.formatName = formatName

    def setDataChangeCallback(self, callbackFunc):
        """Set callback function to be called every time a node's dictionary
           data is changed.  The callbackFunc must take two arguments:
           the node being changed and a list of changed fields"""
        self.dataChangeCallbacks.append(callbackFunc)

    #*************************************************************************
    #  Format Interfaces:
    #*************************************************************************

    def getNodeFormatNames(self):
        """Return text list of available node format names"""
        return globalref.docRef.treeFormats.nameList(True)

    def newNodeFormat(self, formatName, defaultFieldName='Name'):
        """Create a new node format, names must only contain characters
           [a-zA-Z0-9_.-].  If defaultFieldName, a text field is created
           and added to the title line and the first output line"""
        format = nodeformat.NodeFormat(formatName, {}, defaultFieldName)
        globalref.docRef.treeFormats[formatName] = format

    def copyFileFormat(self, fileRef, password=''):
        """Copy the configuration from another TreeLine file,
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined),
           passord is optional - used to open an encrypted TreeLine file,
           returns True/False on success/failure"""
        try:
            globalref.docRef.treeFormats.configCopy(fileRef, password)
            return True
        except (treedoc.PasswordError, IOError, UnicodeError,
                treedoc.ReadFileError):
            return False

    def getFormatIconName(self, formatName):
        """Return the node format's currently set icon name,
           a default setting will return an empty string,
           blank will return 'NoIcon'"""
        try:
            return globalref.docRef.treeFormats[formatName].iconName
        except KeyError:
            return ''

    def setFormatIconName(self, formatName, iconName):
        """Set the node format's icon to iconName,
           an empty string or unknown icon name will get the default icon,
           use 'NoIcon' to get a blank"""
        try:
            globalref.docRef.treeFormats[formatName].iconName = iconName
        except KeyError:
            pass

    def addTreeIcon(self, name, image):
        """Add an icon to those available for use in the tree,
           icon data can be in any image format supported by Qt,
           if name matches one already loaded, the earlier one is replaced"""
        icon = QtGui.QIcon()
        pixmap = QtGui.QPixmap(image)
        if not pixmap.isNull():
            icon.addPixmap(pixmap)
            globalref.treeIcons[name] = icon

    def getTitleLineFormat(self, formatName):
        """Return the node format's title formatting line"""
        try:
            return globalref.docRef.treeFormats[formatName].getLines()[0]
        except KeyError:
            return ''

    def setTitleLineFormat(self, formatName, newLine):
        """Set the node format's title formatting line to newLine"""
        try:
            globalref.docRef.treeFormats[formatName].insertLine(newLine, 0)
        except KeyError:
            pass

    def getOutputFormatLines(self, formatName):
        """Return a list of the node format's output formatting lines"""
        try:
            return globalref.docRef.treeFormats[formatName].getLines()[1:]
        except KeyError:
            return []

    def setOutputFormatLines(self, formatName, lineList):
        """Set the node format's output formatting lines to lineList"""
        try:
            format = globalref.docRef.treeFormats[formatName]
        except KeyError:
            return
        format.lineList = format.lineList[:1]
        for line in lineList:
            format.addLine(line)

    def getFormatFieldNames(self, formatName):
        """Return a list of the node format's field names"""
        try:
            return globalref.docRef.treeFormats[formatName].fieldNames()
        except KeyError:
            return []

    def addNewFormatField(self, formatName, fieldName, fieldType='Text'):
        """Add a new field to the node format, type should be one of:
           Text, Number, Choice, Combination, AutoChoice, Date, Time, 
           Boolean, URL, Path, Email, InternalLink, ExecuteLink, Picture"""
        try:
            globalref.docRef.treeFormats[formatName].\
                             addNewField(fieldName, {'type': fieldType})
        except KeyError:
            pass

    def getFormatFieldType(self, formatName, fieldName):
        """Return the type of the given field in the given format"""
        try:
            field = globalref.docRef.treeFormats[formatName].\
                                     findField(fieldName)
        except KeyError:
            return ''
        if field:
            return field.typeName
        return ''

    def changeFormatFieldType(self, formatName, fieldName, newFieldType):
        """Change the type of the given field in the given format,
           type should be one of:  Text, Number, Choice,
           Combination, AutoChoice, Date, Time, Boolean, URL, Path, Email,
           InternalLink, ExecuteLink, Picture"""
        try:
            field = globalref.docRef.treeFormats[formatName].\
                                     findField(fieldName)
        except KeyError:
            return
        if field:
            field.changeType(newFieldType)

    def getFormatFieldFormat(self, formatName, fieldName):
        """Return the format code string of the given field"""
        try:
            field = globalref.docRef.treeFormats[formatName].\
                                     findField(fieldName)
        except KeyError:
            return ''
        if field:
            return field.format
        return ''

    def setFormatFieldFormat(self, formatName, fieldName, newFieldFormat):
        """Change the format code string of the given field"""
        try:
            field = globalref.docRef.treeFormats[formatName].\
                                     findField(fieldName)
        except KeyError:
            return
        if field:
            field.format = newFieldFormat
            field.initFormat()

    def getFormatFieldExtraText(self, formatName, fieldName):
        """Return a tuple of the prefix and suffix text of the given field"""
        try:
            field = globalref.docRef.treeFormats[formatName].\
                                     findField(fieldName)
        except KeyError:
            return ('', '')
        if field:
            return (field.prefix, field.suffix)
        return ('', '')

    def setFormatFieldExtraText(self, formatName, fieldName, newPrefix='',
                                newSuffix=''):
        """Set the format prefix and suffix text of the given field"""
        try:
            field = globalref.docRef.treeFormats[formatName].\
                                     findField(fieldName)
        except KeyError:
            return
        if field:
            field.prefix = newPrefix
            field.suffix = newSuffix

    def getFormatFieldHtmlProp(self, formatName, fieldName):
        """Return True if the given field is set to use HTML,
           False for plain text"""
        try:
            field = globalref.docRef.treeFormats[formatName].\
                                     findField(fieldName)
        except KeyError:
            return False
        if field:
            return field.html
        return False

    def setFormatFieldHtmlProp(self, formatName, fieldName, htmlProp=True):
        """Change the HTML handling of the given field"""
        try:
            field = globalref.docRef.treeFormats[formatName].\
                                     findField(fieldName)
        except KeyError:
            return
        if field:
            field.html = htmlProp

    def getFormatFieldNumLines(self, formatName, fieldName):
        """Return the number of lines set for the given field"""
        try:
            field = globalref.docRef.treeFormats[formatName].\
                                     findField(fieldName)
        except KeyError:
            return 0
        if field:
            return field.numLines
        return 0

    def setFormatFieldNumLines(self, formatName, fieldName, numLines):
        """Set the number of lines set for the given field"""
        try:
            field = globalref.docRef.treeFormats[formatName].\
                                     findField(fieldName)
        except KeyError:
            return
        if field:
            field.numLines = numLines

    #*************************************************************************
    #  View Interfaces:
    #*************************************************************************

    def updateViews(self):
        """Refresh the tree view and the current right-side views to reflect
           current data"""
        globalref.updateViewAll()

    def setViewUpdateCallback(self, callbackFunc):
        """Set callback function to be called after every TreeLine 
           view update and control availability change (it is called often
           but is a good way to check for specific changes)"""
        self.viewUpdateCallbacks.append(callbackFunc)

    def getActiveEditView(self):
        """Return the currently active text editor in the Data Editor
           right-hand view.  This does not include the combo boxes used for
           some fields.  Returns None if something else has the focus."""
        return self.mainWin.focusWidgetWithAttr('addHtmlTag')

    def insertEditViewText(self, text):
        """Inserts the given text into the currently active text editor
           in the Data Editor right-hand view
           (if one of the editors has the focus"""
        editor = self.getActiveEditView()
        if editor:
            editor.insertPlainText(text)

    #*************************************************************************
    #  File Interfaces:
    #*************************************************************************

    def openFile(self, fileRef, importOnFail=True, addToRecent=True,
                 newWinOk=True):
        """Open file given by fileRef interactively (QMessageBox on failure),
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined),
           if importOnFail and not a TreeLine file, will prompt for import type,
           if addToRecent, will add filename to recently used file list,
           if newWinOk will allow to create new window based on user setting"""
        if hasattr(fileRef, 'read'):
            fd, fileName = tempfile.mkstemp()
            os.write(fd, fileRef.read())
            os.close(fd)
            fileRef.close()
        else:
            fileName = fileRef
        globalref.treeControl.openFile(fileName, newWinOk, importOnFail,
                                       addToRecent)
        if hasattr(fileRef, 'read'):
            os.remove(fileName)

    def newFile(self):
        """Start a new file"""
        self.mainWin.fileNew()

    def readFile(self, fileRef, password=''):
        """Open TreeLine file given by fileRef non-interactively,
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined),
           returns True/False on success/failure"""
        if password:
            if hasattr(fileRef, 'read'):
                fileName = unicode(fileRef.name, sys.getfilesystemencoding())
            else:
                fileName = fileRef
            globalref.docRef.setPassword(fileName, password)
        try:
            globalref.docRef.readFile(fileRef)
            return True
        except (treedoc.PasswordError, IOError, UnicodeError):
            return False

    def saveFile(self, fileRef):
        """Save TreeLine file to fileRef interactively
           (QMessageBox on failure)"""
        globalref.treeControl.saveFile(fileRef)

    def writeFile(self, fileRef, password=''):
        """Save TreeLine file to fileRef non-interactively,
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined),
           returns True/False on success/failure"""
        if password:
            if hasattr(fileRef, 'read'):
                fileName = unicode(fileRef.name, sys.getfilesystemencoding())
            else:
                fileName = fileRef
            globalref.docRef.setPassword(fileName, password)
        try:
            globalref.docRef.writeFile(fileRef)
            return True
        except IOError:
            return False

    def getFileName(self, caption, defaultExt='', filterList=None,
                    currentFilter='', saveMode=True):
        """Return user specified file name for open, save as & export,
           starts from directory of current or recently used file,
           caption is the dialog title,
           defaultExt is added to base file name in saveMode,
           filterList is a list of filters with extensions (defaults to *.trl),
           currentFilter is the active filter in saveMode,
           saveMode is True for save and export, False for file open"""
        if not filterList:
            filterList = [self.mainWin.tlGenFileFilter]
        if saveMode:
            return self.mainWin.getSaveFileName(caption, defaultExt,
                                                filterList, currentFilter)
        else:
            return self.mainWin.getOpenFileName(caption, filterList)

    def getCurrentFileName(self):
        """Return the currently open filename"""
        return globalref.docRef.fileName

    def getDocModified(self):
        """Return True if the current document is marked as modified,
           False otherwise"""
        return globalref.docRef.modified

    def setDocModified(self, value):
        """A value of True sets the document status to modified,
           a value of False is unmodified"""
        globalref.docRef.modified = value
        globalref.updateViewMenuStat()

    def setFileNewCallback(self, callbackFunc):
        """Set callback function to be called after a new file is started"""
        self.fileNewCallbacks.append(callbackFunc)

    def setFileOpenCallback(self, callbackFunc):
        """Set callback function to be called after opening a file"""
        self.fileOpenCallbacks.append(callbackFunc)

    def setFileSaveCallback(self, callbackFunc):
        """Set callback function to be called after a file is saved"""
        self.fileSaveCallbacks.append(callbackFunc)

    def fileExport(self):
        """Export data to html,xml, etc. via dialog and return the fileName"""
        return self.mainWin.fileExport()

    def exportHtml(self, fileRef, includeRoot=True, openOnly=False, indent=20,
                   addHeader=False):
        """Export current branch to single-column HTML,
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined),
           remaining parameters are options,
           returns True on success, False on failure"""
        try:
            globalref.docRef.exportHtml(fileRef, self.getCurrentNode(),
                                        includeRoot, openOnly, indent, 
                                        addHeader)
            return True
        except IOError:
            return False

    def exportDirTable(self, dirName, nodeList, addHeader=False):
        """Export tree to nested directory struct with html tables,
           dirName is initial export directory,
           nodeList is list of nodes to export (defaults to selection)"""
        if not nodeList:
            nodeList = self.getSelectedNodes()
        try:
            globalref.docRef.exportDirTable(dirName, nodeList, addHeader)
            return True
        except IOError:
            return False

    def exportDirPage(self, dirName, nodeList):
        """Export tree to nested directory struct with html page for each node,
           dirName is initial export directory,
           nodeList is list of nodes to export (defaults to selection)"""
        if not nodeList:
            nodeList = self.getSelectedNodes()
        try:
            globalref.docRef.exportDirPage(dirName, nodeList)
            return True
        except IOError:
            return False

    def exportXslt(self, fileRef, includeRoot=True, indent=20):
        """Export XSLT file for the current formatting,
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined),
           returns True on success, False on failure"""
        try:
            globalref.docRef.exportXslt(fileRef, includeRoot, indent)
            self.updateViews()
            return True
        except IOError:
            return False

    def exportTrlSubtree(self, fileRef, nodeList, addBranches=True):
        """Export current branch as a TreeLine subtree,
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined),
           nodeList is list of nodes to export (defaults to selection),
           returns True on success, False on failure"""
        if not nodeList:
            nodeList = self.getSelectedNodes()
        try:
            globalref.docRef.exportTrlSubtree(fileRef, nodeList, addBranches)
            return True
        except IOError:
            return False

    def exportTable(self, fileRef, nodeList, addBranches=True):
        """Export current item's children as a table of data,
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined)
           nodeList is list of nodes to export (defaults to selection),
           returns True on success, False on failure"""
        if not nodeList:
            nodeList = self.getSelectedNodes()
        try:
            globalref.docRef.exportTable(fileRef, nodeList, addBranches)
            return True
        except IOError:
            return False

    def exportTabbedTitles(self, fileRef, nodeList, addBranches=True,
                           includeRoot=True, openOnly=False):
        """Export current branch to tabbed text titles,
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined)
           nodeList is list of nodes to export (defaults to selection),
           returns True on success, False on failure"""
        if not nodeList:
            nodeList = self.getSelectedNodes()
        try:
            globalref.docRef.exportTabbedTitles(fileRef, nodeList, addBranches,
                                                includeRoot, openOnly)
            return True
        except IOError:
            return False

    def exportXbelBookmarks(self, fileRef, nodeList, addBranches=True):
        """Export current branch to XBEL format bookmarks,
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined)
           nodeList is list of nodes to export (defaults to selection),
           returns True on success, False on failure"""
        if not nodeList:
            nodeList = self.getSelectedNodes()
        try:
            globalref.docRef.exportXbel(fileRef, nodeList, addBranches)
            return True
        except IOError:
            return False

    def exportHtmlBookmarks(self, fileRef, nodeList, addBranches=True):
        """Export current branch to HTML format bookmarks,
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined)
           nodeList is list of nodes to export (defaults to selection),
           returns True on success, False on failure"""
        if not nodeList:
            nodeList = self.getSelectedNodes()
        try:
            globalref.docRef.exportHtmlBookmarks(fileRef, nodeList,
                                                 addBranches)
            return True
        except IOError:
            return False

    def exportGenericXml(self, fileRef, nodeList, addBranches=True):
        """Export current branch to generic XML (non-TreeLine) file,
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined)
           nodeList is list of nodes to export (defaults to selection),
           returns True on success, False on failure"""
        if not nodeList:
            nodeList = self.getSelectedNodes()
        try:
            globalref.docRef.exportGenericXml(fileRef, nodeList, addBranches)
            return True
        except IOError:
            return False

    def exportOdf(self, fileRef, nodeList, addBranches=True,
                  includeRoot=True, openOnly=False):
        """Export an ODF format text file,
           fileRef is either a file path string or a file-like object
           (if it is a file-like object, fileRef.name must be defined)
           nodeList is list of nodes to export (defaults to selection),
           returns True on success, False on failure"""
        if not nodeList:
            nodeList = self.getSelectedNodes()
        fontInfo = QtGui.QFontInfo(self.mainWin.dataOutSplit.widget(0).font())
        try:
            globalref.docRef.exportOdf(fileRef, nodeList, fontInfo.family(),
                                       fontInfo.pointSize(),
                                       fontInfo.fixedPitch(), addBranches,
                                       includeRoot, openOnly)
            return True
        except IOError:
            return False

    #*************************************************************************
    #  Menu Interfaces:
    #*************************************************************************

    def getMenuBar(self):
        """Return the main window's top menu bar (QMenuBar)"""
        return self.mainWin.menuBar()

    def getPulldownMenu(self, index):
        """Return top pulldown menu at position index (QMenu),
           return None if index is not valid"""
        try:
            return self.mainWin.pulldownMenuList[index]
        except IndexError:
            return None

    def addMenuAction(self, name, action, initKey=''):
        """Adds a QAction to the shortcut key editor (menu section) and to
           the toolbar editor (if it has an icon).  This does not add it to a
           menu (use menu.insertAction(...) on a menu from functions above).
           Give a name without punctuation or spaces (spaces are added in the
           editor based on CamelCase splits); initKey is optional control
           key string"""
        optiondefaults.menuKeyBindList.append((name, initKey))
        optiondefaults.cmdTranslationDict[name] = name
        globalref.options.addDefaultKey(name, initKey)
        self.mainWin.actions[name] = action
        icon = action.icon()
        if icon and not icon.isNull():
            self.mainWin.toolIcons[name.lower()] = icon
        self.mainWin.setupShortcuts()
        self.mainWin.setupToolbars()

    def addShortcutKey(self, name, function, initKey=''):
        """Adds a non-menu keyboard shortcut that the user can set in the
           Shortcut Editor.  Give a name without punctuation or spaces (spaces
           are added in the editor based on CamelCase splits), function is
           any Python function, initKey is optional control key string"""
        optiondefaults.otherKeyBindList.append((name, initKey))
        optiondefaults.cmdTranslationDict[name] = name
        globalref.options.addDefaultKey(name, initKey)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(), self.mainWin,
                                   function)
        self.mainWin.shortcuts[name] = shortcut
        self.mainWin.setupShortcuts()

    #*************************************************************************
    #  Internal methods (not for plugin use):
    #*************************************************************************

    def execCallback(self, funcList, *args):
        """Call functions in funcList with given args if any"""
        for func in funcList:
            func(*args)
