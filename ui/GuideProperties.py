# Guide Properties

'''
A pop-up window to show all guide properties when a guide component or guide shape node is selected
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
from bear.system import Settings, Guiding, MessageHandling
from bear.utilities import Nodes
if Settings.licenseVersion == 'full':
    from bear.utilities import DeformGuide
import maya.OpenMaya as om
import maya.utils as utils

guideName = 'bearGuideProperties'

def showGuides():
    
    if mc.window(guideName, exists=True):
        mc.deleteUI(guideName, window=True)
    mainUI(guideName)

def mayaMainWindow():
    
    app = QApplication
    if not app:
        app = QApplication(sys.argv)
    return next(w for w in app.topLevelWidgets() if w.objectName() == 'MayaWindow')

class SpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()

class DoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()

class ClickOutsideDeselectListWidget(QListWidget):
    def __init__(self, spaceEditField, parent=None):
        super().__init__(parent)
        self.spaceEditField = spaceEditField

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            self.setCurrentItem(None)
            if self.spaceEditField is not None:
                self.spaceEditField.clear()

        super().mousePressEvent(event)

class mainUI(QMainWindow):

    def __init__(self, name, currentGuideNode=None, parent=mayaMainWindow()):
        
        super(mainUI, self).__init__(parent)
        
        self.screenWidth, self.screenHeight = Settings.getScreenResolution()

        self.name = name
        self.selectedGuideNodes = list()

        self.closeEvent = self.closeEventCatcher
        
        if self.name == guideName:
            for node in mc.ls(sl=True, type='transform'):
                if Nodes.getNodeType(node) == Settings.guidePivotSuffix:
                    guideShapeNode = Nodes.replaceNodeType(node, Settings.guideShapeSuffix)
                    if Nodes.exists(guideShapeNode):
                        self.selectedGuideNodes.append(guideShapeNode)
                    else:
                        self.selectedGuideNodes.append(node)
                if Nodes.getNodeType(node) == Settings.guideGroup \
                    or Nodes.getNodeType(node) == Settings.guideShapeSuffix \
                    or Nodes.getNodeType(node) == Settings.rigGroup \
                    or Nodes.getNodeType(node) == Settings.controlSuffix \
                        and node != Settings.guideGroup:
                    # add support for rig group or control selected
                    if Nodes.getNodeType(node) == Settings.rigGroup:
                        node = Nodes.replaceNodeType(node, Settings.guideGroup)
                    if Nodes.getNodeType(node) == Settings.controlSuffix:
                        node = Nodes.replaceNodeType(node, Settings.guideShapeSuffix)
                    self.selectedGuideNodes.append(node)
        else:
            self.selectedGuideNodes.append(currentGuideNode)
        
        if len(self.selectedGuideNodes) > 1:
            self.setWindowTitle('...multiple guides selected')
        
        self.setObjectName(self.name)

        centerWidget = QWidget()
        self.setCentralWidget(centerWidget)

        verticalLayout = QVBoxLayout(centerWidget)

        # --- Scroll area ---
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scrollContent = QWidget()
        self.formLayout = QFormLayout(scrollContent)
        scrollContent.setLayout(self.formLayout)

        scrollArea.setWidget(scrollContent)
        verticalLayout.addWidget(scrollArea)

        self.setMinimumWidth(self.screenWidth/6)

        centerWidget.setLayout(verticalLayout)
            
        self.itemCount = 0
        self.allGuideAttrs = list()
        self.assembleAttrs()

        self.applyDynamicMinimumSize()

        if not self.allGuideAttrs or self.allGuideAttrs == []:
            if mc.window(self.name, exists=True):
                mc.deleteUI(self.name, window=True)
            return

        self.show()
        QApplication.processEvents()
        self.moveNearCursor()

        utils.executeDeferred(om.MSceneMessage.addCallback, om.MSceneMessage.kMayaExiting, self.closeEventCatcher)

    def moveNearCursor(self, margin=20):
        cursor = QCursor.pos()

        screen = QApplication.screenAt(cursor)
        if not screen:
            return

        sg = screen.availableGeometry()

        win_w = self.width()
        win_h = self.height()

        # --- Horizontal ---
        x = cursor.x() + margin  # default: open to the right
        if x + win_w > sg.right():
            x = cursor.x() - win_w - margin  # flip to left

        # --- Vertical ---
        y = cursor.y() + margin  # default: open downward
        if y + win_h > sg.bottom():
            y = cursor.y() - win_h - margin  # flip upward

        # Clamp (safety net)
        x = max(sg.left(), min(x, sg.right() - win_w))
        y = max(sg.top(), min(y, sg.bottom() - win_h))

        self.move(x, y)

    def applyDynamicMinimumSize(self):
        """
        Sets a minimum window height based on item count,
        clamped so scrolling activates for large forms.
        """

        # Estimated row height (Qt form rows are very consistent)
        ROW_HEIGHT = 25
        VERTICAL_PADDING = 100

        min_height = (5 * ROW_HEIGHT) + VERTICAL_PADDING
        height = (self.itemCount * ROW_HEIGHT * 0.8) + VERTICAL_PADDING

        # Clamp to screen
        screen_h = self.screenHeight
        MAX_HEIGHT_RATIO = 0.7  # never exceed 80% of screen

        if height > screen_h * MAX_HEIGHT_RATIO:
            height = screen_h * MAX_HEIGHT_RATIO

        min_height = min(min_height, int(screen_h * MAX_HEIGHT_RATIO))
        min_height = max(min_height, 200)  # sane minimum
        
        self.setMinimumHeight(min_height)
        self.adjustSize()
        current_width = self.size().width()
        self.resize(current_width, height)

    def closeEventCatcher(self, event):
        
        event.accept()

    def assembleAttrs(self):

        for s, selectedGuideNode in enumerate(self.selectedGuideNodes):
            if s > 0 and Nodes.getNodeType(selectedGuideNode) == Settings.guideShapeSuffix:
                return
            guideAttrs = self.getAttrs(selectedGuideNode)
            if guideAttrs:
                self.allGuideAttrs.extend(guideAttrs)

    def selectNode(self, lineEdit):
        
        node = lineEdit.text()
        if not node:
            return
        selection = node.split(',')
        if Nodes.listExists(selection):
            mc.select(selection)
    
    def setLineEditText(self, guideAttr, lineEdit):
        
        if 'Loop' in guideAttr:
            self.setLoopText(lineEdit)
            return
        
        currentSelection = mc.ls(sl=True)
        if currentSelection:
            sel = currentSelection[-1]
            lineEdit.setText(sel)
        else:
            lineEdit.setText('')

    def setLoopText(self, lineEdit):

        selection = mc.ls(sl=True, fl=True)
        selType = None
        for sel in selection:
            if '.e' in sel:
                selType = 'Edge' if len(selection) == 1 else 'Edges'
            if '.vtx' in sel:
                if len(selection) > 1:
                    MessageHandling.selectionCount(1, exactCount=True)
                    return
                selType = 'Vertex'
        if selType == None:
            MessageHandling.selectionType('edge')
            return
        ordered = DeformGuide.getOrderedLoopVertices(selection)
        text = ','.join(ordered)
        lineEdit.setText(text)
        
    def updateJointCount(self, lineEdit, spinBox, *args):

        # depending on edge loop inputs, we update joint count attribute value

        text = lineEdit.text()
        if not text:
            return

        # supports comma-separated entries
        count = len(text.split(","))

        spinBox.setValue(count)

    def getAttrs(self, guideNode):
        
        if not mc.objExists(guideNode):
            return
        
        userAttrs = mc.listAttr(guideNode, userDefined=True)
        if not userAttrs:
            return
        
        guideAttrs = list()
        for userAttr in userAttrs:
            if userAttr == 'shape':
                if mc.getAttr('%s.shape'%guideNode, lock=True):
                    continue
            if not userAttr in self.allGuideAttrs+['global', 
                                                'globalScale', 
                                                'readyForRigBuild', 
                                                'guide', 
                                                'namingConvention', 
                                                'element', 
                                                'parentType',
                                                'bearVersion',
                                                'curvePosition',
                                                'blendShape',
                                                'pivotInitialShapeSize',
                                                'oldLimbRig']:
                if not 'visBuffer' in userAttr:
                    guideAttrs.append(userAttr)

        # setting how some items are sorted in the ui
        if 'color' in guideAttrs:
            guideAttrs.remove('color')
            guideAttrs.insert(0, 'color')
        if 'toggleColorDisplay' in guideAttrs:
            guideAttrs.remove('toggleColorDisplay')
            guideAttrs.insert(1, 'toggleColorDisplay')
        if 'shape' in guideAttrs:
            guideAttrs.remove('shape')
            guideAttrs.insert(0, 'shape')
        if 'parentNode' in guideAttrs:
            guideAttrs.remove('parentNode')
            guideAttrs.insert(len(guideAttrs), 'parentNode')
        if 'parentOrientNode' in guideAttrs:
            guideAttrs.remove('parentOrientNode')
            guideAttrs.insert(len(guideAttrs), 'parentOrientNode')
        if 'orientNode' in guideAttrs:
            guideAttrs.remove('orientNode')
            guideAttrs.insert(len(guideAttrs), 'orientNode')
        if 'spaceNodes' in guideAttrs:
            guideAttrs.remove('spaceNodes')
            guideAttrs.insert(len(guideAttrs), 'spaceNodes')
        if 'spaceNames' in guideAttrs:
            guideAttrs.remove('spaceNames')
            guideAttrs.insert(len(guideAttrs), 'spaceNames')
        if 'displaySwitch' in guideAttrs:
            guideAttrs.remove('displaySwitch')
            guideAttrs.insert(len(guideAttrs), 'displaySwitch')
        if 'side' in guideAttrs:
            guideAttrs.remove('side')
            guideAttrs.insert(0,  'side')
        if 'name' in guideAttrs:
            guideAttrs.remove('name')
            guideAttrs.insert(0, 'name')
        if 'componentType' in guideAttrs:
            guideAttrs.remove('componentType')
            guideAttrs.insert(0, 'componentType')

        if guideAttrs == []:
            return
        
        if not guideAttrs or guideAttrs == []:
            return None, None
        if self.name == 'bearGuideProperties':
            guideAttrs = [x for x in guideAttrs if x.split('_')[0] != 'output']
        else:
            guideAttrs = [x for x in guideAttrs if x.split('_')[0] == 'output']

        if Nodes.getNodeType(guideNode) != Settings.guideGroup:
            if not 'pivotShapeSize' in guideAttrs:
                guideAttrs.append('pivotShapeSize')

        self.itemCount = 0

        upperLoopField = None
        upperJointSpin = None
        lowerLoopField = None
        lowerJointSpin = None

        for guideAttr in guideAttrs:

            self.itemCount += 1
            
            attrVal = Guiding.getBuildAttrs(guideNode, guideAttr)
            if attrVal == None and not guideAttr == 'side':
                attrVal = ''
                
            if attrVal == 'unsupported':
                if Settings.licenseVersion == 'free':
                    continue
                else:
                    attrVal = True
            
            spaceEditField = None
            inputField = None
            
            if guideAttr == 'name':
                inputField = QLineEdit()
                inputField.setText(attrVal)
                inputField.textChanged.connect(partial(self.setPropertyValue, guideAttr, inputField))
            if guideAttr == 'side' or guideAttr == 'componentType':
                inputField = QLabel()
                if guideAttr == 'componentType':
                    inputText = attrVal
                if attrVal == None:
                    inputText = 'None'
                if attrVal == Settings.leftSide:
                    inputText = 'Left'
                if attrVal == Settings.rightSide:
                    inputText = 'Right'
                inputField.setText(inputText)
            if type(attrVal) == bool:
                inputField = QCheckBox()
                inputField.setChecked(attrVal)
                inputField.stateChanged.connect(partial(self.setPropertyValue, guideAttr, inputField))
            if mc.about(v=True) >= '2022':
                strCheck = type(attrVal) == str
            else:
                strCheck = (type(attrVal) == str or type(attrVal) == unicode) # unicode seems to happen in maya 2020
            if type(attrVal) == list:
                if type(attrVal[0]) == str:
                    if 'vtx' in attrVal[0]:
                        attrVal = ','.join(attrVal)
                        strCheck = True
            if strCheck and not guideAttr == 'side' and not guideAttr == 'componentType':
                if attrVal.upper() in ['X', 'Y', 'Z', '-X', '-Y', '-Z'] and attrVal != '':
                    inputField = QComboBox()
                    inputField.addItems(['X', 'Y', 'Z', '-X', '-Y', '-Z'])
                    inputField.setCurrentText(attrVal.upper())
                    inputField.currentIndexChanged.connect(partial(self.setPropertyValue, guideAttr, inputField))
                elif 'Node' in guideAttr or 'Geo' in guideAttr or 'Loop' in guideAttr or 'Vertex' in guideAttr:
                    inputField = QHBoxLayout()
                    inputFieldText = QLineEdit()
                    inputFieldText.setText(attrVal)
                    inputFieldButton = QPushButton()
                    inputFieldButton.setToolTip("Plug selection")
                    inputFieldButton.setIcon(QApplication.style().standardIcon(QStyle.SP_ArrowBack))
                    inputFieldButton.setFixedSize(self.screenWidth/100, self.screenWidth/100)
                    inputFieldButton.clicked.connect(partial(self.setLineEditText, guideAttr, inputFieldText))
                    inputFieldText.textChanged.connect(partial(self.setPropertyValue, guideAttr, inputFieldText))
                    selectButton = QPushButton()
                    selectButton.setToolTip("Select object(s)")
                    selectButton.setIcon(QApplication.style().standardIcon(QStyle.SP_ArrowForward))
                    selectButton.setFixedSize(self.screenWidth/100, self.screenWidth/100)
                    selectButton.clicked.connect(partial(self.selectNode, inputFieldText))
                    inputField.addWidget(inputFieldText)
                    inputField.addWidget(inputFieldButton)
                    inputField.addWidget(selectButton)
                    if guideAttr == 'upperLidBorderEdgeLoop':
                        upperLoopField = inputFieldText
                    if guideAttr == 'lowerLidBorderEdgeLoop':
                        lowerLoopField = inputFieldText
                    if guideAttr == 'upperLipBorderEdgeLoop':
                        upperLoopField = inputFieldText
                    if guideAttr == 'lowerLipBorderEdgeLoop':
                        lowerLoopField = inputFieldText
                else:
                    inputField = QLineEdit()
                    inputField.setText(attrVal)
                    inputField.textChanged.connect(partial(self.setPropertyValue, guideAttr, inputField))
            if type(attrVal) == int:
                if mc.attributeQuery(guideAttr, node=guideNode, at=True) == 'enum':
                    inputField = QComboBox()
                    enumVals = mc.attributeQuery(guideAttr, node=guideNode, listEnum=True)[0].split(':')
                    inputField.addItems(enumVals)
                    inputField.setCurrentIndex(attrVal)
                    inputField.currentIndexChanged.connect(partial(self.setPropertyValue, guideAttr, inputField))
                else:
                    inputField = SpinBox()
                    inputField.setMaximum(1000000)
                    inputField.setValue(attrVal)
                    inputField.valueChanged.connect(partial(self.setPropertyValue, guideAttr, inputField))
                    if guideAttr == 'upperLidJointCount':
                        upperJointSpin = inputField
                    if guideAttr == 'lowerLidJointCount':
                        lowerJointSpin = inputField
                    if guideAttr == 'upperLipJointCount':
                        upperJointSpin = inputField
                    if guideAttr == 'lowerLipJointCount':
                        lowerJointSpin = inputField
            if type(attrVal) == float:
                inputField = DoubleSpinBox()
                inputField.setDecimals(3)
                inputField.setSingleStep(1)
                inputField.setMaximum(100000)
                inputField.setMinimum(-100000)
                inputField.setValue(attrVal)
                inputField.valueChanged.connect(partial(self.setPropertyValue, guideAttr, inputField))
            if type(attrVal) == list and not 'Loop' in guideAttr:
                if type(attrVal[0]) == int or type(attrVal[0]) == bool:
                    inputField = QLineEdit()
                    inputField.setText(', '.join([str(x) for x in attrVal]))
                    inputField.textChanged.connect(partial(self.setPropertyValue, guideAttr, inputField))
                else:
                    def setSpaceField(inputField, spaceEditField, *args, **kwargs):
                        if inputField.currentItem():
                            spaceEditField.setText(inputField.currentItem().text())
                    def moveItemUp(inputField):
                        current_row = inputField.currentRow()
                        if current_row > 0:
                            item = inputField.takeItem(current_row)
                            inputField.insertItem(current_row - 1, item)
                            inputField.setCurrentRow(current_row - 1)
                    def moveItemDown(inputField):
                        current_row = inputField.currentRow()
                        if current_row < inputField.count() - 1:
                            item = inputField.takeItem(current_row)
                            inputField.insertItem(current_row + 1, item)
                            inputField.setCurrentRow(current_row + 1)
                    def addNewSpace(inputField, spaceEditField, *args, **kwargs):
                        newSpaces = [spaceEditField.text()]
                        if newSpaces[0] == '':
                            newSpaces = mc.ls(sl=True)
                        for newSpace in newSpaces:
                            for i in range(inputField.count()):
                                item = inputField.item(i)
                                if item.text() == newSpace:
                                    return
                            if newSpace == '':
                                return
                            currentIndex = inputField.currentRow()
                            newItem = QListWidgetItem()
                            newItem.setText(newSpace)
                            if currentIndex == -1:
                                inputField.addItem(newItem)
                            else:
                                inputField.insertItem(currentIndex+1, newItem)
                            inputField.setCurrentItem(newItem)
                    def removeSpace(inputField, spaceEditField, *args, **kwargs):
                        spaceName = spaceEditField.text()
                        for i in range(inputField.count()):
                            item = inputField.item(i)
                            if item.text() == spaceName:
                                inputField.takeItem(i)
                                inputField.setCurrentItem(item)
                                spaceEditField.setText('')
                                inputField.setCurrentItem(inputField.item(inputField.count()-1))
                                return
                    def updateList(inputField, spaceEditField, *args, **kwargs):
                        if inputField.currentItem():
                            inputField.currentItem().setText(spaceEditField.text())
                    spaceEditField = QLineEdit()
                    inputField = ClickOutsideDeselectListWidget(spaceEditField)
                    inputField.setMaximumHeight(Settings.getScreenResolution()[1]*0.1)
                    inputField.setMaximumWidth(Settings.getScreenResolution()[0]*0.2)
                    for subVal in attrVal:
                        if str(subVal) == '':
                            continue
                        self.itemCount += 1
                        label = QListWidgetItem()
                        label.setText(str(subVal))
                        inputField.addItem(label)
                    hLayout = QHBoxLayout()
                    moveUpButton = QPushButton()
                    moveUpButton.setText('▲')
                    moveDownButton = QPushButton()
                    moveDownButton.setText('▼')
                    addNewButton = QPushButton()
                    addNewButton.setText('Add')
                    removeButton = QPushButton()
                    removeButton.setText('Remove')
                    spaceEditField.textEdited.connect(partial(updateList, inputField, spaceEditField))
                    hLayout.addWidget(spaceEditField)
                    hLayout.addWidget(moveUpButton)
                    hLayout.addWidget(moveDownButton)
                    hLayout.addWidget(addNewButton)
                    hLayout.addWidget(removeButton)
                    inputField.currentItemChanged.connect(partial(setSpaceField, inputField, spaceEditField))
                    inputField.itemClicked.connect(partial(setSpaceField, inputField, spaceEditField))
                    moveUpButton.clicked.connect(partial(moveItemUp, inputField))
                    moveDownButton.clicked.connect(partial(moveItemDown, inputField))
                    addNewButton.clicked.connect(partial(addNewSpace, inputField, spaceEditField))
                    removeButton.clicked.connect(partial(removeSpace, inputField, spaceEditField))
                    inputField.currentTextChanged.connect(partial(self.setPropertyValue, guideAttr, inputField))

            guideAttrNiceName = ' '+' '.join(re.findall('[A-Z][^A-Z]*', guideAttr[0].upper()+guideAttr[1:]))

            self.formLayout.addRow(guideAttrNiceName+':', inputField)
            if spaceEditField:
                self.formLayout.addRow('', hLayout)
                spaceEditField = None

        if upperLoopField and upperJointSpin:
            upperLoopField.textChanged.connect(
                partial(self.updateJointCount, upperLoopField, upperJointSpin)
            )

        if lowerLoopField and lowerJointSpin:
            lowerLoopField.textChanged.connect(
                partial(self.updateJointCount, lowerLoopField, lowerJointSpin)
            )

        return guideAttrs
            
    def setPropertyValue(self, guideAttr, inputField, *args):

        for selectedGuideNode in self.selectedGuideNodes:
            
            if not mc.objExists(selectedGuideNode):
                continue

            guideNodeAttr = selectedGuideNode+'.'+guideAttr
            if not mc.objExists(guideNodeAttr):
                selectedGuideNode = Nodes.replaceNodeType(selectedGuideNode, Settings.guidePivotSuffix)
                guideNodeAttr = selectedGuideNode+'.'+guideAttr
            if not mc.objExists(guideNodeAttr):
                continue

            attrType = mc.attributeQuery(guideAttr, node=selectedGuideNode, at=True)

            if type(inputField) in [QSpinBox, QDoubleSpinBox]:
                if attrType == 'typed':
                    Nodes.setAttr(guideNodeAttr, str(inputField.value()), type='string')
                else:
                    if mc.objectType(selectedGuideNode) == 'joint' and guideAttr == 'pivotShapeSize':
                        guideNodeAttr = selectedGuideNode+'.radius'
                    Nodes.setAttr(guideNodeAttr, inputField.value())

            if type(inputField) == QCheckBox:
                if attrType == 'typed':
                    Nodes.setAttr(guideNodeAttr, str(inputField.isChecked()), type='string')
                else:
                    Nodes.setAttr(guideNodeAttr, inputField.isChecked())

            if type(inputField) == QLineEdit:
                value = inputField.text()

                Nodes.setAttr(guideNodeAttr, value, type='string')

            if type(inputField) == QComboBox:
                if attrType == str:
                    Nodes.setAttr(guideNodeAttr, inputField.currentText(), type='string')
                else:
                    if inputField.currentText() in 'XYZ':
                        Nodes.setAttr(guideNodeAttr, inputField.currentText(), type='string')
                    else:
                        Nodes.setAttr(guideNodeAttr, inputField.currentIndex())

            if type(inputField) == ClickOutsideDeselectListWidget:
                val = ', '.join([inputField.item(i).text() for i in range(inputField.count())])
                if val == '':
                    val = ','
                Nodes.setAttr(guideNodeAttr, val, type='string')