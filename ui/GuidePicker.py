# Guide Picker

'''
A pop-up window to show which guide components to pick
'''

import maya.cmds as mc
if mc.about(v=True) < '2025':
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
else:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
import sys, re
from functools import partial
from bear.system import Settings
from bear.system import MessageHandling
from bear.utilities import Nodes
from bear.utilities import AddNode

guidePickerName = 'bearGuidePicker'
guidePickerRenameDialogName = 'bearGuidePickerRenameDialog'

def showPicker(collections, guideGroups, guideRefPrefix, guideFile):

    if mc.window(guidePickerName, exists=True):
        mc.deleteUI(guidePickerName, window=True)
    mainUI(guidePickerName, collections, guideGroups, guideRefPrefix, guideFile)

def mayaMainWindow():
    
    app = QApplication
    if not app:
        app = QApplication(sys.argv)
    return next(w for w in app.topLevelWidgets() if w.objectName() == 'MayaWindow')
    
def duplicateGuide(pickedGuide, guideRefPrefix):

    pickedGuide = mc.duplicate(guideRefPrefix+':'+pickedGuide, fullPath=True, rr=True, un=True)[0]
    
    return pickedGuide
    
class RenameDialog(QDialog):

    def __init__(self, 
                pickedGuide,
                guideRefPrefix,
                parent=mayaMainWindow()):

        super(RenameDialog, self).__init__(parent)
        
        self.screenWidth, self.screenHeight = Settings.getScreenResolution()
        
        self.name = guidePickerRenameDialogName
        self.component = Nodes.getComponent(pickedGuide)
        self.side = Nodes.getSide(pickedGuide)
        self.pickedGuide = pickedGuide
        self.guideRefPrefix = guideRefPrefix

        self.skipped = False
        self.skippedAll = False
        self.renamed = False

        verticalLayout = QVBoxLayout()

        self.nameField = QLineEdit()
        self.nameField.setText(self.component)

        buttonLayout = QHBoxLayout()
        skipAllButton = QPushButton('Skip All')
        skipButton = QPushButton('Skip')
        renameButton = QPushButton('Rename')
        skipAllButton.setFixedSize(self.screenWidth/35, self.screenWidth/80)
        skipButton.setFixedSize(self.screenWidth/35, self.screenWidth/80)
        renameButton.setFixedSize(self.screenWidth/35, self.screenWidth/80)

        verticalLayout.addWidget(self.nameField)
        verticalLayout.addLayout(buttonLayout)
        buttonLayout.addWidget(skipAllButton, alignment=Qt.AlignCenter)
        buttonLayout.addWidget(skipButton, alignment=Qt.AlignLeft)
        buttonLayout.addWidget(renameButton, alignment=Qt.AlignRight)

        renameButton.clicked.connect(self.confirm)
        skipAllButton.clicked.connect(partial(self.reject, True))
        skipButton.clicked.connect(self.reject)

        self.setLayout(verticalLayout)

        self.setMinimumWidth(self.screenWidth/9)
        self.setMinimumHeight(self.screenHeight/20)

        self.setWindowTitle('Rename incoming guide...')
        self.setObjectName(self.name)

    def open(self):
        
        while True:
            result = self.exec_()
            if result == QDialog.Accepted:
                if self.isUniqueName() and self.isValidName():
                    return self.nameField.text()
            elif result == QDialog.Rejected and self.skippedAll:
                return False
            else:
                return None
            
    def reject(self, all=False):
        
        if all:
            self.skippedAll = True
            self.done(False)
        else:
            super().reject()

    def confirm(self):

        if self.isValidName():
            self.accept()
        else:
            MessageHandling.invalidCharacter()

        if self.isUniqueName():
            self.accept()
        else:
            MessageHandling.guideAlreadyExists()

    def isValidName(self):

        if not re.match("^[a-zA-Z0-9]*$", self.nameField.text()):
            return False
        return True
    
    def isUniqueName(self):

        newGuide = Nodes.createName(self.nameField.text(), self.side, Settings.guideGroup)[0]
        if mc.objExists(newGuide):
            return False
        return True
    
class mainUI(QMainWindow):
    
    def __init__(self, name, collections=[], guideGroups=[[]], guideRefPrefix=None, guideFile=None, parent=mayaMainWindow()):
        super(mainUI, self).__init__(parent)
        
        print('\n\nImporting BEAR guides')
        
        self.screenWidth, self.screenHeight = Settings.getScreenResolution()

        self.name = name
        self.selectedGuideNodes = list()
        self.guideRefPrefix = guideRefPrefix
        self.guideFile = guideFile
        
        self.setWindowTitle('Guide Picker')
        self.setObjectName(self.name)

        verticalLayout = QVBoxLayout()
        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabel('External Guides')
        centerWidget = QWidget()
        self.setCentralWidget(centerWidget)

        self.createTree(self.treeWidget, collections, guideGroups)
        verticalLayout.addWidget(self.treeWidget)

        # Add Replace by Token checkbox and fields
        self.replaceByTokenCheckbox = QCheckBox("Replace by Token")
        self.replaceByTokenCheckbox.toggled.connect(self.toggleTokenFields)
        verticalLayout.addWidget(self.replaceByTokenCheckbox)

        self.currentTokenField = QLineEdit()
        self.currentTokenField.setPlaceholderText("Current token")
        self.newTokenField = QLineEdit()
        self.newTokenField.setPlaceholderText("New token")
        self.currentTokenField.setEnabled(False)
        self.newTokenField.setEnabled(False)
        verticalLayout.addWidget(self.currentTokenField)
        verticalLayout.addWidget(self.newTokenField)

        self.replaceAttrsCheckbox = QCheckBox("Replace attribute values")
        verticalLayout.addWidget(self.replaceAttrsCheckbox)
        self.replaceAttrsCheckbox.setEnabled(False)

        buttonLayout = QHBoxLayout()
        self.pickButton = QPushButton('Pick')
        self.cancelButton = QPushButton('Done')
        self.pickButton.setFixedSize(self.screenWidth/30, self.screenWidth/65)
        self.cancelButton.setFixedSize(self.screenWidth/30, self.screenWidth/65)
        self.pickButton.clicked.connect(self.pick)
        self.cancelButton.clicked.connect(self.cancel)
        buttonLayout.addWidget(self.cancelButton, alignment=Qt.AlignLeft)
        buttonLayout.addWidget(self.pickButton, alignment=Qt.AlignRight)

        verticalLayout.addLayout(buttonLayout)

        self.setMinimumWidth(self.screenWidth/8)
        self.setMinimumHeight(self.screenHeight/3)

        centerWidget.setLayout(verticalLayout)

        if not guideGroups:
            if mc.window(self.name, exists=True):
                mc.deleteUI(self.name, window=True)
            return

        self.show()

    def createTree(self, treeParent, collections, guideGroups):
        treeParent.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for c, guideList in enumerate(guideGroups):
            if collections[c]:
                collectionName = collections[c].split(':')[-1]
                treeWidget = QTreeWidgetItem(collectionName)
                treeWidget.setText(0, collectionName)
                treeParent.addTopLevelItem(treeWidget)
                for guideGroup in guideList:
                    guideName = guideGroup.split(':')[-1]
                    subWidget = QTreeWidgetItem(guideName)
                    subWidget.setText(0, guideName)
                    treeWidget.addChild(subWidget)
            else:
                guideName = guideList[0].split(':')[-1]
                treeWidget = QTreeWidgetItem(guideName)
                treeWidget.setText(0, guideName)
                treeParent.addTopLevelItem(treeWidget)

    def toggleTokenFields(self):
        """Enable or disable the token fields based on the checkbox state."""
        if self.replaceByTokenCheckbox.isChecked():
            self.currentTokenField.setEnabled(True)
            self.newTokenField.setEnabled(True)
            self.replaceAttrsCheckbox.setEnabled(True)
        else:
            self.currentTokenField.setEnabled(False)
            self.newTokenField.setEnabled(False)
            self.replaceAttrsCheckbox.setEnabled(False)

    def parentGuide(self, selectedItem, pickedGuide):

        selectedItemParent = selectedItem.parent()
        guideParent = selectedItemParent.text(0) if selectedItemParent else None
        if Nodes.exists(guideParent):
            parentedGuide = Nodes.setParent(pickedGuide, guideParent)
        else:
            parentedGuide = Nodes.setParent(pickedGuide, Settings.guideRoot)

        return parentedGuide
    
    def rename(self, pickedGuide, newName=None, currentToken=None, newToken=None):
        
        name = Nodes.getComponent(pickedGuide)
        pickedGuide = mc.ls(duplicateGuide(pickedGuide, self.guideRefPrefix))[0]

        if currentToken and newToken:
            if currentToken in name:
                newName = name.replace(currentToken, newToken)
            else:
                newName = name
                
        newPickedGuide = mc.rename(pickedGuide, Nodes.replaceToken(pickedGuide, newName, 'component'))
        if mc.objExists('%s.name'%newPickedGuide):
            mc.setAttr('%s.name'%newPickedGuide, newName, type='string')
        
        Nodes.renameHierarchy(newPickedGuide, name, newName, includeRoot=False)

        if currentToken and newToken:
            for childNode in Nodes.getAllChildren(newPickedGuide):
                for attrName in mc.listAttr(childNode, userDefined=True):
                    attr = f'{childNode}.{attrName}'
                    if mc.getAttr(attr, lock=True):
                        continue
                    if mc.getAttr(attr, type=True) == 'string':
                        attrVal = mc.getAttr(attr)
                        if currentToken in attrVal:
                            newAttrVal = attrVal.replace(currentToken, newToken)
                            mc.setAttr(attr, newAttrVal, type='string')
        
        return newPickedGuide

    def pick(self):
        AddNode.compNode(root=Settings.guideRoot, createRootOnly=True)
        
        selectedItems = self.treeWidget.selectedItems()

        pickedGuides = list()

        # Get token replacement values
        currentToken = self.currentTokenField.text()
        newToken = self.newTokenField.text()

        for selectedItem in selectedItems:
            
            if selectedItem.parent():
                if selectedItem.parent().text(0) in [x.text(0) for x in selectedItems]:
                    continue

            pickedItem = selectedItem.text(0)
            self.component = Nodes.getComponent(pickedItem)
            childGuides = list()
            parentGuide = None
            pickedGuide = None

            if Nodes.getComponentType(pickedItem) == 'Collection':
                childGuides = [selectedItem.child(x).text(0) for x in range(selectedItem.childCount())]
                parentGuide = pickedItem

            if Nodes.exists(pickedItem) and not childGuides:
                if self.replaceByTokenCheckbox.isChecked():
                    # If Replace by Token is checked, replace the token in the picked guide's name
                    pickedGuide = self.rename(pickedItem, currentToken=currentToken, newToken=newToken)
                else:
                    newName = RenameDialog(pickedItem, self.guideRefPrefix).open()
                    if newName == False:
                        return
                    if newName:
                        pickedGuide = self.rename(pickedItem, newName)
                pickedGuide = self.parentGuide(selectedItem, pickedGuide)

            if not Nodes.exists(pickedItem) and childGuides:
                pickedGuide = duplicateGuide(pickedItem, self.guideRefPrefix)
                mc.delete(Nodes.getChildren(pickedGuide, longName=True))
                pickedGuide = self.parentGuide(selectedItem, pickedGuide)

            if not Nodes.exists(pickedItem) and not childGuides:
                pickedGuide = duplicateGuide(pickedItem, self.guideRefPrefix)
                pickedGuide = self.parentGuide(selectedItem, pickedGuide)
            
            for childGuide in childGuides:
                pickedChildGuide = None
                if Nodes.exists(childGuide):
                    if self.replaceByTokenCheckbox.isChecked():
                        pickedChildGuide = self.replaceByToken(childGuide, currentToken, newToken)
                    else:
                        newName = RenameDialog(childGuide, self.guideRefPrefix).open()
                        if newName == False:
                            return
                        if newName:
                            pickedChildGuide = self.rename(childGuide, newName)
                    pickedChildGuide = Nodes.setParent(pickedChildGuide, parentGuide)
                else:
                    pickedChildGuide = duplicateGuide(childGuide, self.guideRefPrefix)
                    pickedChildGuide = Nodes.setParent(pickedChildGuide, parentGuide)
                if pickedChildGuide:
                    pickedGuides.append(pickedChildGuide)

            self.parentGuide(selectedItem, pickedGuide)

            if pickedGuide:
                pickedGuides.append(pickedGuide)

        if not any(pickedGuides) == None:
            mc.select(pickedGuides)

        print('\n\nBEAR guides import completed')

    def cancel(self):
        if self.guideFile:
            mc.file(self.guideFile, removeReference=True)
        if mc.window(self.name, exists=True):
            mc.deleteUI(self.name, window=True)
