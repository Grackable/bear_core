# -*- coding: utf-8 -*-

# Builder

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import sys, os, shutil, re, importlib, json, datetime, subprocess
from functools import partial
import maya.cmds as mc
import maya.OpenMaya as om
import maya.utils as utils

from bear.ui import UndoDec
from bear.ui import GuideProperties
from bear.ui import Elements
from bear.system import Files
from bear.system import Settings
from bear.system import Component
from bear.system import Collection # we need this import for createByCompGroup in Component, so the module is found
from bear.system import MessageHandling
from bear.system import DataStructure
from bear.system import Assembly
if Settings.licenseVersion == 'full':
    from bear.utilities import AlignGuide
from bear.utilities import Tools
from bear.utilities import Nodes
from bear.utilities import UnloadModules

def getLogo(tile=20):
    
    logoSize = max([x for x in [70, 90, 110, 130, 150, 180, 220, 260, 320, 380] if x <= (Settings.getScreenResolution()[0]/tile)])
    logoMap = QPixmap(Settings.getPath(['ui', 'icons', 'logo_%sp.png'%str(logoSize)]))

    return logoMap

def mayaMainWindow():
    
    app = QApplication
    if not app:
        app = QApplication(sys.argv)
    return next(w for w in app.topLevelWidgets() if w.objectName() == 'MayaWindow')
        
def addTooltipButton():

    size = Settings.getScreenResolution()[0]/150.0
    button = QPushButton()
    button.setIcon(QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation))
    button.setMinimumSize(size, size)
    button.setMaximumSize(size, size)

    return button
    
def addSplitter(layout):     

    splitter = QSplitter()
    splitter.setFixedHeight(1)
    splitter.setFrameShape(QFrame.HLine)
    layout.addWidget(splitter)

class tooltipUI(QMainWindow):

    def __init__(self, tag, tagNiceName=None, heightMultiplier=1.0, parent=mayaMainWindow()):

        super(tooltipUI, self).__init__(parent)

        tagName = tagNiceName if tagNiceName else ' '.join(re.findall('[A-Z][a-z]*', tag[0].upper()+tag[1:]+'Tooltip'))

        self.tooltipWindowName = tagName

        if mc.window(self.tooltipWindowName, exists=True):
            mc.deleteUI(self.tooltipWindowName, window=True)

        self.screenWidth, self.screenHeight = Settings.getScreenResolution()
        
        tooltipFile = open(Settings.getPath(['ui', 'tooltips', 'tooltip_'+tag+'.html']))
        
        textDoc = QTextDocument()
        textDoc.setHtml(tooltipFile.read())

        textWidget = QTextEdit()
        textWidget.setDocument(textDoc)

        palette = QPalette()
        textWidget.setPalette(palette)
        textFont = QFont()
        textFont.setPointSize(12)

        textWidget.setFont(textFont)
        textWidget.setReadOnly(True)
        textWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
   
        self.setCentralWidget(textWidget)

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.Popup)
        self.setStyleSheet("background-color:rgb(55,90,130);border:0px;")
        self.setWindowTitle(tagName)
        mousePos = QCursor().pos()
        
        self.setGeometry(0, 0, textWidget.document().size().width()*0.55, textWidget.document().size().height()*1.7*heightMultiplier)
        self.move(mousePos.x()+5, mousePos.y()+5)

        self.show()

class mainUI(QMainWindow):

    def __init__(self, parent=mayaMainWindow()):

        super(mainUI, self).__init__(parent)

        self.rootFolder = Settings.getRootPath()

        self.userFile = Settings.getUserFile()
        self.projectFolder = json.load(open(self.userFile))['projectFolder']
        self.assetFolder = json.load(open(self.userFile))['assetFolder']

        if not os.path.isdir(self.projectFolder):
            self.projectFolder = None
        
        self.bearBuilderName = 'bearBuilder'
        self.guidePropertiesName = 'bearGuideProperties'
        self.outputPropertiesName = 'bearOutputProperties'
        self.guidePickerName = 'bearGuidePicker'
        self.guidePickerRenameDialogName = 'bearGuidePickerRenameDialog'

        if mc.window(self.bearBuilderName, exists=True):
            mc.deleteUI(self.bearBuilderName, window=True)

        self.screenWidth, self.screenHeight = Settings.getScreenResolution()
        
        self.loadSettings(promptNoFile=True)

        self.guideRoot = DataStructure.Asset().guideRoot
        self.rigRoot = DataStructure.Asset().rigRoot
        self.skinMeshRoot = DataStructure.Asset().skinMeshRoot
        self.poseCorrectionsRoot = DataStructure.Asset().poseCorrectionsRoot

        self.projectFolderEdit = None

        if self.loadedSettings['autoShowGuideProperties']:
            self.addCallback()
        self.closeEvent = self.closeEventCatcher
        
        self.setObjectName(self.bearBuilderName)

        self.menuBar()

        self.createWidget = QWidget()
        self.buildWidget = QWidget()
        self.assembleWidget = QWidget()
        
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.createWidget, 'Definition')
        self.tabWidget.addTab(self.buildWidget, 'Build')
        self.tabWidget.addTab(self.assembleWidget, 'Deform')

        self.globalWidgets()
        
        self.setCentralWidget(self.tabWidget)

        self.definitionTab()
        self.buildTab()
        self.deformTab()

        self.tooltips()

        self.setGeometry(self.screenWidth/4.25, self.screenHeight/5.6, self.screenWidth/30, self.screenHeight/20)
        self.setWindowTitle('BEAR Builder')

        utils.executeDeferred(om.MSceneMessage.addCallback, om.MSceneMessage.kMayaExiting, self.closeEventCatcher)
        Elements.loadScreenPosition(self, 'mainUI')
        self.show()

    def guideSelection(self, *args, **kwargs):
        
        self.loadSettings()
        if self.loadedSettings['autoShowGuideProperties']:
            GuideProperties.showGuides()
        else:
            self.removeCallback()
            GuideProperties.showGuides()

    def guideSelectPivot(self, *args, **kwargs):

        Tools.selectNode(Settings.guidePivotSuffix)

    def guideSelectShape(self, *args, **kwargs):

        Tools.selectNode(Settings.guideShapeSuffix)

    def addCallback(self, *args, **kwargs):
        
        self.removeCallback()
        self.guideSelectionCallback = om.MEventMessage.addEventCallback('SelectionChanged', self.guideSelection)

    def removeCallback(self, *args, **kwargs):

        try:
            om.MMessage.removeCallback(self.guideSelectionCallback)
        except:
            pass

    def copyInstanceToUserFile(self, removeInstanceFile=False):
        
        userFile, userFileInstance, userDataFolderInstance = Settings.getUserFile(returnInstance=True)
        if os.path.isfile(userFileInstance):
            shutil.copy(userFileInstance, userFile)
        if removeInstanceFile:
            if os.path.isfile(userFileInstance):
                os.remove(userFileInstance)
            if os.path.isdir(userDataFolderInstance):
                os.rmdir(userDataFolderInstance)

    def closeEventCatcher(self, event):

        Elements.saveScreenPosition(self, 'mainUI')
        self.removeCallback()
        
        if mc.window(self.guidePropertiesName, exists=True):
            mc.deleteUI(self.guidePropertiesName, window=True)
        if mc.window(self.outputPropertiesName, exists=True):
            mc.deleteUI(self.outputPropertiesName, window=True)
        if mc.window(self.guidePickerName, exists=True):
            mc.deleteUI(self.guidePickerName, window=True)
        if mc.window(self.guidePickerRenameDialogName, exists=True):
            mc.deleteUI(self.guidePickerRenameDialogName, window=True)

        self.copyInstanceToUserFile(removeInstanceFile=True)

        event.accept()

    def globalWidgets(self):
        
        #create
        self.compName = QLineEdit()
        self.collectionTree = QTreeWidget()
        self.collectionTree.setHeaderLabel('Collections')
        self.componentTree = QTreeWidget()
        self.componentTree.setHeaderLabel('Components')

        #build
        self.buildSideNone = QRadioButton('Inactive')
        self.buildSideLeft = QRadioButton('Left')
        self.buildSideRight = QRadioButton('Right')
        self.buildAssetFolder = QLineEdit(self.assetFolder)
        self.modelCheckBox = QCheckBox('Model')
        self.guideCheckBox = QCheckBox('Guide')
        self.showGuidePropertiesButton = QPushButton('Settings')
        self.showGuidePropertiesButton.setFixedSize(self.screenWidth/40, self.screenWidth/80)
        self.showGuidePropertiesButton.clicked.connect(partial(self.guideSelection))
        self.selectComponentButton = QPushButton('Select Component')
        self.selectComponentButton.clicked.connect(partial(self.componentSelect))
        self.guideSelectPivotButton = QPushButton('Select Pivot')
        self.guideSelectPivotButton.clicked.connect(partial(self.guideSelectPivot))
        self.guideSelectShapeButton = QPushButton('Select Shape')
        self.guideSelectShapeButton.clicked.connect(partial(self.guideSelectShape))
        self.guideDefinitionCheckBox = QCheckBox('Definition')
        self.guidePositionCheckBox = QCheckBox('Pivot Positions')
        self.guideOrientationCheckBox = QCheckBox('Pivot Orientations')
        self.guideShapeSettingsCheckBox = QCheckBox('Shape Settings')
        self.guideShapeTransformsCheckBox = QCheckBox('Shape Transforms')
        self.guideSettingsCheckBox = QCheckBox('Guide Settings')
        self.rigCheckBox = QCheckBox('Rig')
        self.rigSettingsCheckBox = QCheckBox('Rig Settings')
        self.buildSelectSelected = QRadioButton('Selected Components')
        self.buildSelectAll = QRadioButton('All Components')

        #assemble
        self.assembleAssetFolder = QLineEdit(self.assetFolder)
        self.deformerCheckBox = QCheckBox('Deformer')
        self.skinCheckBox = QCheckBox('Skin')
        self.latticeCheckBox = QCheckBox('Lattice')
        self.smoothCheckBox = QCheckBox('Smooth')
        self.proximityWrapCheckBox = QCheckBox('Wrap')
        self.geometryConstraintsCheckBox = QCheckBox('Parent Constraints')
        self.inputOrderCheckBox = QCheckBox('Input Order')
        self.vertexID = QRadioButton('By Vertex ID')
        self.vertexPosition = QRadioButton('By Vertex Position')
        self.uvs = QRadioButton('By UVs')
        self.postDeformCheckBox = QCheckBox('Post Deform')
        self.faceCorrectionsCheckBox = QCheckBox('Face Corrections')
        self.poseCorrectionsCheckBox = QCheckBox('Pose Corrections')
        if Settings.licenseVersion != 'free':
            self.faceCorrectionsCheckBox.setVisible(False)
            self.poseCorrectionsCheckBox.setVisible(False)
        self.assembleSelectSelected = QRadioButton('Selected Geometries')
        self.assembleSelectAll = QRadioButton('All Geometries')

        #execute
        self.createButton = QPushButton('Create')
        self.buildButton = QPushButton('Build')
        self.assembleButton = QPushButton('Build')
        self.createButton.setFixedSize(self.screenWidth/30, self.screenWidth/65)
        self.buildButton.setFixedSize(self.screenWidth/30, self.screenWidth/65)
        self.assembleButton.setFixedSize(self.screenWidth/30, self.screenWidth/65)

        #tooltips
        self.collectionsTooltip = addTooltipButton()
        self.componentsTooltip = addTooltipButton()
        self.nameTooltip = addTooltipButton()

        self.guideToolsTooltip = addTooltipButton()
        self.modelTooltip = addTooltipButton()
        self.guideTooltip = addTooltipButton()
        self.guideSettingsTooltip = addTooltipButton()
        self.rigTooltip = addTooltipButton()
        self.rigSettingsTooltip = addTooltipButton()
        self.buildFromAssetTooltip = addTooltipButton()

        self.deformerTooltip = addTooltipButton()
        self.postDeformTooltip = addTooltipButton()
        if Settings.licenseVersion != 'free':
            self.faceCorrectionsTooltip = addTooltipButton()
            self.poseCorrectionsTooltip = addTooltipButton()
        self.deformFromAssetTooltip = addTooltipButton()
        
        self.collectionsTooltip.clicked.connect(partial(tooltipUI, 'collections'))
        self.componentsTooltip.clicked.connect(partial(tooltipUI, 'components'))
        self.nameTooltip.clicked.connect(partial(tooltipUI, 'name'))

        self.guideToolsTooltip.clicked.connect(partial(tooltipUI, 'guideTools', heightMultiplier=0.88))
        self.modelTooltip.clicked.connect(partial(tooltipUI, 'model'))
        self.guideTooltip.clicked.connect(partial(tooltipUI, 'guide', heightMultiplier=0.95))
        self.guideSettingsTooltip.clicked.connect(partial(tooltipUI, 'guideSettings', heightMultiplier=0.88))
        self.rigTooltip.clicked.connect(partial(tooltipUI, 'rig'))
        self.rigSettingsTooltip.clicked.connect(partial(tooltipUI, 'rigSettings'))
        self.buildFromAssetTooltip.clicked.connect(partial(tooltipUI, 'fromAsset'))

        self.deformerTooltip.clicked.connect(partial(tooltipUI, 'deformer', heightMultiplier=0.92))
        self.postDeformTooltip.clicked.connect(partial(tooltipUI, 'postDeform'))
        if Settings.licenseVersion != 'free':
            self.faceCorrectionsTooltip.clicked.connect(partial(tooltipUI, 'faceCorrections'))
            self.poseCorrectionsTooltip.clicked.connect(partial(tooltipUI, 'poseCorrections'))

        self.deformFromAssetTooltip.clicked.connect(partial(tooltipUI, 'fromAsset'))

    def menuBar(self):

        menuBar = QMenuBar()

        # file menu
        fileItem = menuBar.addMenu('File')
        load = fileItem.addAction('Open')
        fileItem.addSeparator()
        saveSetup = fileItem.addAction('Save Setup')
        saveGuide = fileItem.addAction('Save Guide')
        saveSetupSettings = fileItem.addAction('Save Rig Settings')
        saveTransformsSettings = fileItem.addAction('Save Control Transforms')
        saveSkin = fileItem.addAction('Save Deform')
        saveInputOrder = fileItem.addAction('Save Input Order')
        if Settings.licenseVersion != 'free':
            saveBlendshapes = fileItem.addAction('Save Blendshapes')
        saveAll = fileItem.addAction('Save All')
        fileItem.addSeparator()
        saveModel = fileItem.addAction('Save Model')
        fileItem.addSeparator()
        saveDelivery = fileItem.addAction('Save Delivery')
        fileItem.addSeparator()
        openAssetFolder = fileItem.addAction('Open Asset Folder')
        fileItem.addSeparator()
        settings = fileItem.addAction('Settings')
        fileItem.addSeparator()
        fileItem.addSeparator()
        about = fileItem.addAction('About')
        load.triggered.connect(partial(self.openFile))
        saveSetup.triggered.connect(partial(self.saveFile, Settings.setupFileIndicator))
        saveModel.triggered.connect(partial(self.saveFile, Settings.modelFileIndicator))
        saveGuide.triggered.connect(partial(self.saveFile, Settings.guideFileIndicator))
        saveSetupSettings.triggered.connect(partial(self.saveFile, Settings.rigSettingsFileIndicator))
        saveInputOrder.triggered.connect(partial(self.saveFile, Settings.inputOrderFileIndicator))
        saveTransformsSettings.triggered.connect(partial(self.saveFile, Settings.controlTransformsFileIndicator))
        saveSkin.triggered.connect(partial(self.saveFile, Settings.deformFileIndicator))
        if Settings.licenseVersion != 'free':
            saveBlendshapes.triggered.connect(partial(self.saveFile, Settings.blendshapesFileIndicator))
        saveDelivery.triggered.connect(partial(self.saveFile, Settings.deliveryFileIndicator))
        openAssetFolder.triggered.connect(partial(self.openAssetFolder))
        saveAll.triggered.connect(self.saveAll)
        settings.triggered.connect(self.settingsUI)
        about.triggered.connect(self.aboutUI)

        # edit menu
        editItem = menuBar.addMenu('Edit')
        deleteComp = editItem.addAction('Delete Component')
        executeScript = editItem.addAction('Execute Script for enabled build steps')
        saveCollection = editItem.addAction('Save Collection')
        deleteComp.triggered.connect(partial(self.deleteComponent))
        executeScript.triggered.connect(partial(self.executeScriptManually))
        saveCollection.triggered.connect(partial(self.saveCollectionPreset))

        self.setMenuBar(menuBar)

    def componentSelect(self):

        selection = mc.ls(sl=True)
        guideComps = list()
        for sel in selection:
            guideComp = Nodes.getComponentGroupByType(sel)
            if guideComp:
                guideComps.append(guideComp)
        mc.select(guideComps)

    @UndoDec.undo
    def deleteComponent(self):
        
        selection = mc.ls(sl=True)
        if Settings.guideGroup in selection:
            selection = Nodes.getChildren(Settings.guideGroup)
        if Settings.rigGroup in selection:
            selection = Nodes.getChildren(Settings.rigGroup)
        for sel in selection:
            if Nodes.getComponentType(sel):
                Tools.deleteComponent(sel)
            else:
                MessageHandling.noComponentGroupSelected()
                return
        if not Nodes.getChildren(Settings.guideGroup):
            Nodes.delete(Settings.guideGroup)
        if not Nodes.getChildren(Settings.rigGroup):
            Nodes.delete(Settings.rigGroup)

    def executeScriptManually(self):
        
        if self.modelCheckBox.isChecked():
            Component.customScript('model', 
                                   forceRun=True, 
                                   modelEnabled=self.modelCheckBox.isChecked())
        if self.guideCheckBox.isChecked():
            Component.customScript('guide', 
                                   forceRun=True,
                                   guideEnabled=self.guideCheckBox.isChecked())
        if self.rigCheckBox.isChecked():
            Component.customScript('rig', 
                                   forceRun=True,
                                   rigEnabled=self.rigCheckBox.isChecked())
        if self.postDeformCheckBox.isChecked():
            Component.customScript('postDeform', 
                                   forceRun=True,
                                   postDeformEnabled=self.postDeformCheckBox.isChecked())

    def saveCollectionPreset(self):

        selection = mc.ls(sl=True)
        if not selection:
            MessageHandling.collectionSelected()
            return
        if len(selection) > 1:
            MessageHandling.collectionSelected()
            return
        collectionGroup = selection[0]
        if not Nodes.getComponentType(collectionGroup) == 'Collection':
            MessageHandling.collectionSelected()
            return

        Files.SaveCollectionDialog(collectionGroup).open()

    def openAssetFolder(self):
        
        folderPath = self.projectFolder+'/'+self.assetFolder
        if not os.path.exists(folderPath):
            raise FileNotFoundError(f"The folder {folderPath} does not exist.")
        if sys.platform.startswith('darwin'):
            subprocess.run(['open', folderPath])
        elif sys.platform.startswith('win'):
            os.startfile(folderPath)
        elif sys.platform.startswith('linux'):
            subprocess.run(['xdg-open', folderPath])
        else:
            raise NotImplementedError(f"Platform {sys.platform} is not supported.")

    def createFolderButton(self, folder, isSubFolder, isAssetFolder=False, isProjectFolder=False, isCustomFolder=False, customFile=False, versionPicker=None):

        folderButton = QPushButton()
        folderButton.setIcon(QApplication.style().standardIcon(QStyle.SP_DirIcon))
        folderButton.setMaximumSize(18, 18)
        if customFile:
            folderButton.clicked.connect(partial(self.filePicker, folder))
        else:
            folderButton.clicked.connect(partial(self.folderPicker, folder, isSubFolder, isAssetFolder, isProjectFolder, isCustomFolder, versionPicker))
        return folderButton
    
    def getVersions(self, versionPicker, folderPath):
        
        if not os.path.isdir(folderPath):
            return
        versions = os.listdir(folderPath)[::-1]
        if versionPicker:
            versionPicker.clear()
            versionPicker.addItems(versions)

    def versionStateChange(self, checkbox1, checkbox2, *args):
        
        if not checkbox1.isChecked():
            checkbox2.setChecked(True)
        if not checkbox2.isChecked():
            checkbox1.setChecked(True)

    def filePicker(self, folder):
        
        pickedDir = QFileDialog.getOpenFileName(self, 'Pick File')[0]
        folder.setText(pickedDir)

    def folderPicker(self, folder, isSubFolder, isAssetFolder=False, isProjectFolder=False, isCustomFolder=False, versionPicker=None):
        
        pickedDir = QFileDialog.getExistingDirectory(self, 'Pick Folder')

        projectFolder = json.load(open(Settings.getUserFile()))['projectFolder']
        
        if isAssetFolder:
            self.projectFolder = self.projectFolderEdit.text() if self.projectFolderEdit else projectFolder
        
        if isCustomFolder:
            folder.setText(pickedDir)
            return
        
        if pickedDir != '':
            if self.projectFolder:
                subDir = pickedDir.replace(self.projectFolder, '')
            else:
                subDir = pickedDir
            if not self.projectFolder:
                self.projectFolder = pickedDir
            if not self.projectFolder in pickedDir and not isProjectFolder:
                MessageHandling.foreignProjectFolder()
                return
            if isSubFolder and self.projectFolder and self.assetFolder and not isAssetFolder:
                subDir = pickedDir.replace(self.projectFolder, '').replace(self.assetFolder, '')
            dirName = subDir if isSubFolder or isAssetFolder else pickedDir
            folder.setText(dirName)
            self.getVersions(versionPicker, pickedDir)

    def versionPicker(self, folder):

        fileDialog = QFileDialog()
        fileDialog.setDirectory(self.projectFolder+'/*')
        pickedFolder = fileDialog.getExistingDirectory(self, 'Pick Folder')
        if pickedFolder != '':
            versionName = pickedFolder.split('/')[-1]
            if versionName:
                folder.setText(versionName)

    def openFile(self):

        self.loadSettings()
        
        output = Files.Config(
            self.projectFolder,
            self.assetFolder,
            ).open()
        if output:
            self.settingsUI(setAssetFolder=output[1], setProjectFolder=output[0])
            self.saveSettings(assetFolder=output[1], projectFolder=output[0])
            self.getVersions(self.buildVersion, self.projectFolder+'/'+self.assetFolder)
            self.getVersions(self.assembleVersion, self.projectFolder+'/'+self.assetFolder)

    def saveAll(self):

        keywords = [
            Settings.setupFileIndicator, 
            Settings.guideFileIndicator, 
            Settings.rigSettingsFileIndicator, 
            Settings.controlTransformsFileIndicator, 
            Settings.inputOrderFileIndicator, 
            Settings.deformFileIndicator,
            ]
        if Settings.licenseVersion != 'free' and Nodes.exists(Settings.poseCorrectionsGroup):
            keywords.append(Settings.blendshapesFileIndicator)
        setupSave = self.saveFile(keywords[0], saveAll=True)
        if not setupSave:
            return
        for keyword in keywords[1:]:
            self.saveFile(keyword, querySave=False)

    def saveFile(self, keyword, querySave=True, saveAll=False):

        self.loadSettings()
        
        output = Files.Config(
            self.projectFolder,
            self.assetFolder,
            fileType=keyword, 
            querySave=querySave, 
            saveAll=saveAll, 
            ).save()
        
        if output:
            self.getVersions(self.buildVersion, self.projectFolder+'/'+self.assetFolder)
            self.getVersions(self.assembleVersion, self.projectFolder+'/'+self.assetFolder)
        
        return output
    
    def setAlignGeoText(self):
        
        currentSelection = mc.ls(sl=True)
        if currentSelection:
            alignGeo = currentSelection[-1]
            if Nodes.getShapeType(alignGeo) == 'mesh':
                self.alignToGeoText.setText(alignGeo)
        else:
            self.alignToGeoText.setText('')

    def applyNamingConvention(self, namingConvention):

        rigNodeFound = False
        for rigNode in [Settings.guideRoot, Settings.rigRoot]:
            if mc.objExists(rigNode+'.namingConvention'):
                rigNodeFound=True
        if not rigNodeFound:
            MessageHandling.noObjectsToRename()
            return

        if not MessageHandling.queryNamingConvention():
            return

        # testing if naming convention in the dialog is correct
        namingOrder = namingConvention.text().split('_')
        namingOrderTest = namingOrder[::]

        if namingOrderTest[0] == 'indices':
            MessageHandling.noIndicesInFront()
            return

        for tokenType in ['component',
                            'side',
                            'nodeType',
                            'element',
                            'indices',
                            'specific']:
            if not tokenType in namingOrderTest:
                MessageHandling.incorrectNamingConvention()
                return
            namingOrderTest.remove(tokenType)
        if len(namingOrderTest) != 0:
            MessageHandling.incorrectNamingConvention()
            return

        # applying naming convention
        Nodes.renameToNamingConvention(namingOrder)

        self.saveSettings(False)

        self.close()
        self.settingsWindow.close()
        if mc.about(v=True) >= '2022':
            importlib.reload(UnloadModules)
        else:
            reload(UnloadModules)
        UnloadModules.execute()

        MessageHandling.namingConventionApplied()

    def renameTokens(self, 
                        guideRoot,
                        rigRoot,
                        geometryGroup,
                        guidePivotSuffix,
                        guideShapeSuffix,
                        spaceSuffix,
                        controlSuffix,
                        skinJointSuffix,
                        leftSideToken,
                        rightSideToken,
                        query=True,
                        renameOnCreation=False):
        
        rigNodeFound = False
        for rigNode in [Settings.guideRoot, Settings.rigRoot]:
            if mc.objExists(rigNode):
                if not mc.objExists(rigNode+'.namingConvention'):
                    Nodes.addNamingAttr(rigNode, ['nodeType'])
                    MessageHandling.usingExistingGuideRoot()
                rigNodeFound=True
                current_guideRoot = mc.getAttr('%s.guideRoot'%rigNode) if mc.objExists('%s.guideRoot'%rigNode) else 'guide'
                current_rigRoot = mc.getAttr('%s.rigRoot'%rigNode) if mc.objExists('%s.rigRoot'%rigNode) else 'rig'
                current_geometryGroup = mc.getAttr('%s.geometryGroup'%rigNode)
                current_guidePivotSuffix = mc.getAttr('%s.guidePivotToken'%rigNode)
                current_guideShapeSuffix = mc.getAttr('%s.guideShapeToken'%rigNode)
                current_spaceSuffix = mc.getAttr('%s.spaceToken'%rigNode)
                current_controlSuffix = mc.getAttr('%s.controlToken'%rigNode)
                current_skinJointSuffix = mc.getAttr('%s.skinJointToken'%rigNode)
                current_leftSide = mc.getAttr('%s.leftSideToken'%rigNode)
                current_rightSide = mc.getAttr('%s.rightSideToken'%rigNode)
            if renameOnCreation: # this is basically for collection creation only
                current_guideRoot = 'guide'
                current_guidePivotSuffix = 'guidePivot'
                current_guideShapeSuffix = 'guideShape'
                current_leftSide = 'L'
                current_rightSide = 'R'
            break
        if not rigNodeFound:
            MessageHandling.noObjectsToRename()
            return

        if query:
            if not MessageHandling.queryRenameTokens():
                return
                
        if type(guideRoot) == str: # if one input is a str, all the others are expected to be str too
            new_guideRoot = guideRoot
            new_rigRoot = rigRoot
            new_geometryGroup = geometryGroup
            new_guidePivotSuffix = guidePivotSuffix
            new_guideShapeSuffix = guideShapeSuffix
            new_spaceSuffix = spaceSuffix
            new_controlSuffix = controlSuffix
            new_skinJointSuffix = skinJointSuffix
            new_leftSideToken = leftSideToken
            new_rightSideToken = rightSideToken
        else:
            new_guideRoot = guideRoot.text()
            new_rigRoot = rigRoot.text()
            new_geometryGroup = geometryGroup.text()
            new_guidePivotSuffix = guidePivotSuffix.text()
            new_guideShapeSuffix = guideShapeSuffix.text()
            new_spaceSuffix = spaceSuffix.text()
            new_controlSuffix = controlSuffix.text()
            new_skinJointSuffix = skinJointSuffix.text()
            new_leftSideToken = leftSideToken.text()
            new_rightSideToken = rightSideToken.text()

        for node in [x for x in mc.ls() if mc.objExists('%s.namingConvention'%x)][::-1]:
            namingConvention = mc.getAttr('%s.namingConvention'%node)
            if len(node.split('_')) != len(namingConvention.split(',')):
                continue
            if Nodes.getToken(node, 'nodeType')[0] == Settings.guideGroup:
                sideAttr = '%s.side'%node
                if mc.objExists(sideAttr):
                    mc.setAttr(sideAttr, lock=False)
                    if mc.getAttr(sideAttr) == current_leftSide:
                        mc.setAttr(sideAttr, new_leftSideToken, type='string')
                    if mc.getAttr(sideAttr) == current_rightSide:
                        mc.setAttr(sideAttr, new_rightSideToken, type='string')
                    mc.setAttr(sideAttr, lock=True)
            if Nodes.getToken(node, 'nodeType')[0] == current_guidePivotSuffix:
                node = mc.rename(node, Nodes.replaceNodeType(node, new_guidePivotSuffix))
            if Nodes.getToken(node, 'nodeType')[0] == current_guideShapeSuffix:
                node = mc.rename(node, Nodes.replaceNodeType(node, new_guideShapeSuffix))
            if Nodes.getToken(node, 'nodeType')[0] == current_spaceSuffix:
                node = mc.rename(node, Nodes.replaceNodeType(node, new_spaceSuffix))
            if Nodes.getToken(node, 'nodeType')[0] == current_controlSuffix:
                node = mc.rename(node, Nodes.replaceNodeType(node, new_controlSuffix))
            if Nodes.getToken(node, 'nodeType')[0] == current_skinJointSuffix:
                node = mc.rename(node, Nodes.replaceNodeType(node, new_skinJointSuffix))
            if Nodes.getToken(node, 'side')[0] == current_leftSide:
                node = mc.rename(node, Nodes.replaceSide(node, new_leftSideToken))
            if Nodes.getToken(node, 'side')[0] == current_rightSide:
                node = mc.rename(node, Nodes.replaceSide(node, new_rightSideToken))

        for node in mc.ls(type='transform'):
            if mc.referenceQuery(node, isNodeReferenced=True):
                continue
            if node == current_guideRoot:
                node = mc.rename(node, new_guideRoot)
            if node == current_rigRoot:
                node = mc.rename(node, new_rigRoot)
            if node == current_geometryGroup:
                node = mc.rename(node, new_geometryGroup)

        if not renameOnCreation:
            self.saveSettings(close=False)

        for rigNode in [Settings.guideRoot, Settings.rigRoot]:
            if mc.objExists(rigNode):
                Nodes.addNamingToRigNode(rigNode)

        if query:
            MessageHandling.tokensRenamed()

    def cancelSettings(self):
        
        self.tooltips()
        self.settingsWindow.close()

    def saveSettings(self, close=True, assetFolder=None, projectFolder=None):

        self.projectFolder = self.settings['projectFolder'].text()
        self.assetFolder = self.settings['assetFolder'].text()

        if assetFolder:
            self.assetFolder = assetFolder
        if projectFolder:
            self.projectFolder = projectFolder

        if self.projectFolder == '':
            if MessageHandling.saveDefaultSettingsQuery(self.projectFolder):
                self.projectFolder = self.rootFolder+'/ui'
            else:
                return
        if not os.path.isdir(self.projectFolder+self.assetFolder):
            if MessageHandling.queryFolderCreation(self.projectFolder+self.assetFolder, 'asset'):
                try:
                    os.makedirs(self.projectFolder+self.assetFolder)
                except:
                    MessageHandling.folderCreationFailed(self.projectFolder+self.assetFolder)
            else:
                return
            
        settingsFileObj = open(self.projectFolder+'/bear_builder_settings.json', 'w+')
        userFileObj = open(Settings.getUserFile(), 'w+')

        userFileAttrs = json.load(open(Settings.getDefaultSettings('bear_user_settings.json')))
        builderFileAttrs = json.load(open(Settings.getDefaultSettings('bear_builder_settings.json')))

        for fileObj in [settingsFileObj, userFileObj]:
            fileAttrs = userFileAttrs if fileObj == userFileObj else builderFileAttrs
            settings = dict()
            for settingLabel, qItem in self.settings.items():
                if not settingLabel in fileAttrs.keys():
                    continue
                if settingLabel == 'projectFolder':
                    settings[settingLabel] = self.projectFolder
                elif settingLabel == 'assetFolder':
                    settings[settingLabel] = self.assetFolder
                else:
                    if type(qItem) == QLineEdit:
                        val = str(qItem.text())
                    if type(qItem) == QCheckBox:
                        val = qItem.isChecked()
                    if type(qItem) == QComboBox:
                        val = str(qItem.currentText())
                    if type(qItem) == QSpinBox:
                        val = qItem.value()
                    settings[settingLabel] = val

                if settingLabel == 'autoShowGuideProperties':
                    if val:
                        self.addCallback()
                        #self.showGuidePropertiesButton.setVisible(False)
                    else:
                        self.removeCallback()
                        #self.showGuidePropertiesButton.setVisible(True)
            fileObj.write(json.dumps(settings, indent=4))
            fileObj.close()

        #self.tooltips()
        if close:
            self.settingsWindow.close()

        self.buildAssetFolder.setText(self.assetFolder)
        self.assembleAssetFolder.setText(self.assetFolder)
        self.getVersions(self.buildVersion, self.projectFolder+'/'+self.assetFolder)
        self.getVersions(self.assembleVersion, self.projectFolder+'/'+self.assetFolder)

        self.copyInstanceToUserFile()

        if mc.about(v=True) >= '2022':
            importlib.reload(Settings)
        else:
            reload(Settings)

    def loadSettings(self, 
                    projectFolderEdit=None, 
                    applyToUI=False, 
                    fileCheck=False, 
                    projectFolder=None, 
                    promptNoFile=False, 
                    queryDefaultLoad=False):
        
        if not projectFolder:
            if projectFolderEdit:
                projectFolder = projectFolderEdit.text()
            else:
                projectFolder = self.projectFolder
            
        if projectFolder == '' and queryDefaultLoad:
            if MessageHandling.loadDefaultSettingsQuery(projectFolder):
                settingsFilePath = self.rootFolder+'/ui/bear_builder_settings.json'
            else:
                return
        
        if not projectFolder:
            settingsFilePath = self.rootFolder+'/ui/bear_builder_settings.json'
            self.loadedSettings, self.assetFolder = Settings.loadSettings(settingsFilePath)
            return

        if os.path.isdir(projectFolder):
            settingsFilePath = projectFolder+'/bear_builder_settings.json'
            if fileCheck:
                if not MessageHandling.settingsLoaded(settingsFilePath):
                    return
            else:
                if not os.path.isfile(settingsFilePath):
                    if promptNoFile:
                        MessageHandling.noSettingsFile()
                    if queryDefaultLoad:
                        if MessageHandling.loadDefaultSettingsQuery(settingsFilePath):
                            settingsFilePath = self.rootFolder+'/ui/bear_builder_settings.json'
                        else:
                            return
                    settingsFilePath = self.rootFolder+'/ui/bear_builder_settings.json'
            self.projectFolder = projectFolder
            self.loadedSettings, self.assetFolder = Settings.loadSettings(settingsFilePath)
        else:
            if MessageHandling.loadDefaultSettingsQuery(projectFolder):
                self.projectFolder = None
                self.loadedSettings, self.assetFolder = Settings.loadSettings(self.rootFolder+'/ui/bear_builder_settings.json')

        if applyToUI:
            for settingLabel, qItem in self.settings.items():
                if settingLabel == 'projectFolder':
                    qItem.setText(projectFolder)
                    continue
                if settingLabel == 'assetFolder':
                    qItem.setText(self.assetFolder)
                    continue
                if type(qItem) == QLineEdit:
                    qItem.setText(self.loadedSettings[settingLabel])
                if type(qItem) == QCheckBox:
                    qItem.setChecked(self.loadedSettings[settingLabel])
                if type(qItem) == QComboBox:
                    qItem.setCurrentText(self.loadedSettings[settingLabel])

    def settingsUI(self, setAssetFolder=None, setProjectFolder=None):

        self.loadSettings()
        if setAssetFolder:
            self.assetFolder = setAssetFolder
        else:
            self.assetFolder = json.load(open(Settings.getUserFile()))['assetFolder']
        if setProjectFolder:
            self.projectFolder = setProjectFolder
        else:
            self.projectFolder = json.load(open(Settings.getUserFile()))['projectFolder']

        self.settingsName = 'settings'

        if mc.window(self.settingsName, exists=True):
            mc.deleteUI(self.settingsName, window=True)
        
        self.settingsWindow = QMainWindow(self)
        self.settingsWindow.setObjectName(self.settingsName)

        self.centralWidget = QWidget()
        self.settingsWindow.setCentralWidget(self.centralWidget)

        self.projectAndAssetFolderWidget = QWidget()
        self.namingConventionWidget = QWidget()
        self.globalScriptsWidget = QWidget()
        self.settingsWidget = QWidget()
        
        self.tabWidget = QToolBox()
        self.tabWidget.addItem(self.projectAndAssetFolderWidget, 'Project && Asset Folder')
        self.tabWidget.addItem(self.namingConventionWidget, 'Naming Convention')
        self.tabWidget.addItem(self.globalScriptsWidget, 'Global Scripts')
        self.tabWidget.addItem(self.settingsWidget, 'General Settings')
        
        backgroundColor = self.tabWidget.palette().window().color()
        self.buttonColor = self.tabWidget.palette().button().color()
        palette = self.tabWidget.palette()
        palette.setColor(self.tabWidget.backgroundRole(), backgroundColor)
        self.tabWidget.setPalette(palette)

        self.centralWidget.setMinimumSize(self.screenWidth/10, self.screenHeight/10)

        # project folder
        boxLayout = QVBoxLayout()
        projectAndAssetFolderTooltip = addTooltipButton()
        projectAndAssetFolderTooltip.clicked.connect(partial(tooltipUI, 'projectAndAssetFolder'))
        self.tooltips(settingsTooltip=projectAndAssetFolderTooltip)
        boxLayout.addWidget(projectAndAssetFolderTooltip, alignment=Qt.AlignRight)

        formLayout = QFormLayout()
        self.projectFolderEdit = QLineEdit(self.projectFolder)
        formLayout.addRow('Project Folder:', self.lineEditWithPicker(self.projectFolderEdit, isSubFolder=False, isProjectFolder=True)[0])
        loadSettingsButton = QPushButton('Load Settings From Project')
        formLayout.addWidget(loadSettingsButton)
        loadSettingsButton.clicked.connect(partial(self.loadSettings, self.projectFolderEdit, applyToUI=True, fileCheck=True, queryDefaultLoad=True))

        # asset folder

        assetFolder = QLineEdit(self.assetFolder)

        formLayout.addRow('Asset Folder:', self.lineEditWithPicker(assetFolder, isSubFolder=True, isAssetFolder=True)[0])

        self.projectAndAssetFolderWidget.setLayout(boxLayout)

        boxLayout.addLayout(formLayout)

        # names & tokens
        boxLayout = QVBoxLayout()
        namesTooltip = addTooltipButton()
        namesTooltip.clicked.connect(partial(tooltipUI, 'namingConvention', tagNiceName='Naming Convention'))
        self.tooltips(settingsTooltip=namesTooltip)
        boxLayout.addWidget(namesTooltip, alignment=Qt.AlignRight)

        formLayout = QFormLayout()

        guideRoot = QLineEdit(self.loadedSettings['guideRoot'])
        rigRoot = QLineEdit(self.loadedSettings['rigRoot'])
        geometryGroup = QLineEdit(self.loadedSettings['geometryGroup'])
        geometrySuffix = QLineEdit(self.loadedSettings['geometryToken'])
        guidePivotSuffix = QLineEdit(self.loadedSettings['guidePivotToken'])
        guideShapeSuffix = QLineEdit(self.loadedSettings['guideShapeToken'])
        spaceSuffix = QLineEdit(self.loadedSettings['spaceToken'])
        controlSuffix = QLineEdit(self.loadedSettings['controlToken'])
        skinJointSuffix = QLineEdit(self.loadedSettings['skinJointToken'])
        leftSideToken = QLineEdit(self.loadedSettings['leftSideToken'])
        rightSideToken = QLineEdit(self.loadedSettings['rightSideToken'])
        renameTokensButton = QPushButton('Rename Objects')
        namingConvention = QLineEdit(self.loadedSettings['namingConvention'])
        namingConventionButton = QPushButton('Apply Token Order')

        formLayout.addRow('Token Order:', namingConvention)
        formLayout.addWidget(namingConventionButton)
        formLayout.addRow('Guide Root:', guideRoot)
        formLayout.addRow('Rig Root:', rigRoot)
        formLayout.addRow('Geometry Group:', geometryGroup)
        formLayout.addRow('Guide Pivot Token:', guidePivotSuffix)
        formLayout.addRow('Guide Shape Token:', guideShapeSuffix)
        formLayout.addRow('Offset Token:', spaceSuffix)
        formLayout.addRow('Control Token:', controlSuffix)
        formLayout.addRow('Skin Joint Token:', skinJointSuffix)
        formLayout.addRow('Left Side Token:', leftSideToken)
        formLayout.addRow('Right Side Token:', rightSideToken)
        formLayout.addWidget(renameTokensButton)
        boxLayout.addLayout(formLayout)

        self.namingConventionWidget.setLayout(boxLayout)

        # global scripts
        
        boxLayout = QVBoxLayout()
        globalScriptsTooltip = addTooltipButton()
        globalScriptsTooltip.clicked.connect(partial(tooltipUI, 'globalScripts', tagNiceName='Global Scripts'))
        self.tooltips(settingsTooltip=globalScriptsTooltip)
        boxLayout.addWidget(globalScriptsTooltip, alignment=Qt.AlignRight)

        formLayout = QFormLayout()

        scriptsFolder = QLineEdit(self.loadedSettings['globalScriptsFolder'])
        modelScript = QLineEdit(self.loadedSettings['modelScript'])
        guideScript = QLineEdit(self.loadedSettings['guideScript'])
        rigScript = QLineEdit(self.loadedSettings['rigScript'])
        postScript = QLineEdit(self.loadedSettings['postDeformScript'])
        deliveryScript = QLineEdit(self.loadedSettings['deliveryScript'])

        formLayout.addRow('Global Scripts Folder:', self.lineEditWithPicker(scriptsFolder, isCustomFolder=True)[0])
        addSplitter(formLayout)
        formLayout.addRow('Model Script:', modelScript)
        formLayout.addRow('Guide Script:', guideScript)
        formLayout.addRow('Rig Script:', rigScript)
        formLayout.addRow('Post Deform Script:', postScript)
        formLayout.addRow('Delivery Script:', deliveryScript)
        enableCheckbox = QCheckBox('Enable Script Execution on Build')
        enableCheckbox.setChecked(self.loadedSettings['enableScriptExecution'])
        formLayout.addWidget(enableCheckbox)
        boxLayout.addLayout(formLayout)

        self.globalScriptsWidget.setLayout(boxLayout)

        # settings
        boxLayout = QVBoxLayout()
        settingsTooltip = addTooltipButton()
        settingsTooltip.clicked.connect(partial(tooltipUI, 'generalSettings'))
        self.tooltips(settingsTooltip=settingsTooltip)
        boxLayout.addWidget(settingsTooltip, alignment=Qt.AlignRight)

        formLayout = QFormLayout()

        removeReferenceCheckBox = QCheckBox()
        removeReferenceCheckBox.setChecked(self.loadedSettings['removeReference'])

        showTooltipsCheckBox = QCheckBox()
        showTooltipsCheckBox.setChecked(self.loadedSettings['showTooltips'])
        showTooltipsCheckBox.clicked.connect(partial(self.tooltips, showTooltipsCheckBox, projectAndAssetFolderTooltip))
        showTooltipsCheckBox.clicked.connect(partial(self.tooltips, showTooltipsCheckBox, namesTooltip))
        showTooltipsCheckBox.clicked.connect(partial(self.tooltips, showTooltipsCheckBox, globalScriptsTooltip))
        showTooltipsCheckBox.clicked.connect(partial(self.tooltips, showTooltipsCheckBox, settingsTooltip))

        autoShowGuidePropertiesCheckBox = QCheckBox()
        autoShowGuidePropertiesCheckBox.setChecked(self.loadedSettings['autoShowGuideProperties'])

        hideGuideAfterRigBuildCheckBox = QCheckBox()
        hideGuideAfterRigBuildCheckBox.setChecked(self.loadedSettings['hideGuideAfterRigBuild'])
        hideRigAfterGuideBuildCheckBox = QCheckBox()
        hideRigAfterGuideBuildCheckBox.setChecked(self.loadedSettings['hideRigAfterGuideBuild'])
        showGuideAfterGuideBuildCheckBox = QCheckBox()
        showGuideAfterGuideBuildCheckBox.setChecked(self.loadedSettings['showGuideAfterGuideBuild'])
        showRigAfterRigBuildCheckBox = QCheckBox()
        showRigAfterRigBuildCheckBox.setChecked(self.loadedSettings['showRigAfterRigBuild'])
        useCustomDeliverySavingCheckBox = QCheckBox()
        useCustomDeliverySavingCheckBox.setChecked(self.loadedSettings['useCustomDeliverySaving'])
        controllerTagsCheckbox = QCheckBox()
        controllerTagsCheckbox.setChecked(self.loadedSettings['createControllerTags'])
        numParentFolders = QSpinBox()
        numParentFolders.setMaximum(100)
        numParentFolders.setValue(self.loadedSettings['numParentFolders'])

        formLayout.addRow('Show Tooltips:', showTooltipsCheckBox)
        formLayout.addRow('Hide Guide after Rig Build:', hideGuideAfterRigBuildCheckBox)
        formLayout.addRow('Hide Rig after Guide Build:', hideRigAfterGuideBuildCheckBox)
        formLayout.addRow('Show Guide after Guide Build:', showGuideAfterGuideBuildCheckBox)
        formLayout.addRow('Show Rig after Rig Build:', showRigAfterRigBuildCheckBox)
        formLayout.addRow('Pop-Up Guide Settings:', autoShowGuidePropertiesCheckBox)
        formLayout.addRow('Remove Reference after Build:', removeReferenceCheckBox)
        formLayout.addRow('Use Custom Delivery Saving:', useCustomDeliverySavingCheckBox)
        formLayout.addRow('Create Controller Tags:', controllerTagsCheckbox)
        formLayout.addRow('Parent folders used as Asset Name tokens:', numParentFolders)

        # versions

        versionNaming = QLineEdit(self.loadedSettings['versionNaming'])
        formLayout.addRow('Version Naming:', versionNaming)

        # files

        mayaFileType = QComboBox()
        mayaFileType.addItem('mayaBinary')
        mayaFileType.addItem('mayaAscii')
        mayaFileType.setCurrentText(self.loadedSettings['mayaFileType'])
        formLayout.addRow('Maya File Type:', mayaFileType)

        boxLayout.addLayout(formLayout)

        self.settingsWidget.setLayout(boxLayout)
        
        # set settings
        self.settings = dict()
        self.settings['projectFolder'] = self.projectFolderEdit

        self.settings['assetFolder'] = assetFolder
        self.settings['modelSubFolder'] = Settings.modelSubFolder
        self.settings['guideSubFolder'] = Settings.guideSubFolder
        self.settings['setupSubFolder'] = Settings.setupSubFolder
        self.settings['rigSettingsSubFolder'] = Settings.rigSettingsSubFolder
        self.settings['deformSubFolder'] = Settings.deformSubFolder
        self.settings['blendshapesSubFolder'] = Settings.blendshapesSubFolder
        self.settings['deliverySubFolder'] = Settings.deliverySubFolder

        self.settings['modelFileIndicator'] = Settings.modelFileIndicator
        self.settings['guideFileIndicator'] = Settings.guideFileIndicator
        self.settings['setupFileIndicator'] = Settings.setupFileIndicator
        self.settings['rigSettingsFileIndicator'] = Settings.rigSettingsFileIndicator
        self.settings['deformFileIndicator'] = Settings.deformFileIndicator
        self.settings['blendshapesFileIndicator'] = Settings.blendshapesFileIndicator
        self.settings['deliveryFileIndicator'] = Settings.deliveryFileIndicator

        self.settings['versionNaming'] = versionNaming
        self.settings['mayaFileType'] = mayaFileType
        
        self.settings['guideRoot'] = guideRoot
        self.settings['rigRoot'] = rigRoot
        self.settings['geometryGroup'] = geometryGroup
        self.settings['geometryToken'] = geometrySuffix
        self.settings['guidePivotToken'] = guidePivotSuffix
        self.settings['guideShapeToken'] = guideShapeSuffix
        self.settings['spaceToken'] = spaceSuffix
        self.settings['controlToken'] = controlSuffix
        self.settings['skinJointToken'] = skinJointSuffix
        self.settings['leftSideToken'] = leftSideToken
        self.settings['rightSideToken'] = rightSideToken
        self.settings['namingConvention'] = namingConvention

        self.settings['removeReference'] = removeReferenceCheckBox

        self.settings['showTooltips'] = showTooltipsCheckBox

        self.settings['autoShowGuideProperties'] = autoShowGuidePropertiesCheckBox

        self.settings['hideGuideAfterRigBuild'] = hideGuideAfterRigBuildCheckBox
        self.settings['hideRigAfterGuideBuild'] = hideRigAfterGuideBuildCheckBox
        self.settings['showGuideAfterGuideBuild'] = showGuideAfterGuideBuildCheckBox
        self.settings['showRigAfterRigBuild'] = showRigAfterRigBuildCheckBox
        self.settings['useCustomDeliverySaving'] = useCustomDeliverySavingCheckBox
        self.settings['createControllerTags'] = controllerTagsCheckbox
        self.settings['numParentFolders'] = numParentFolders

        self.settings['globalScriptsFolder'] = scriptsFolder
        self.settings['modelScript'] = modelScript
        self.settings['guideScript'] = guideScript
        self.settings['rigScript'] = rigScript
        self.settings['postDeformScript'] = postScript
        self.settings['deliveryScript'] = deliveryScript
        self.settings['enableScriptExecution'] = enableCheckbox

        if setAssetFolder:
            self.saveSettings(assetFolder=setAssetFolder)
            return

        self.loadSettings(projectFolder=json.load(open(Settings.getUserFile()))['projectFolder'], applyToUI=True)

        saveLayout = QHBoxLayout()
        saveLayout.addStretch()
        cancelButton = QPushButton('Cancel')
        cancelButton.setMinimumSize(50, 20)
        saveButton = QPushButton('Save')
        saveButton.setMinimumSize(50, 20)
        saveLayout.addWidget(saveButton)
        saveLayout.addWidget(cancelButton)
        namingConventionButton.clicked.connect(partial(self.applyNamingConvention, 
                                                            namingConvention))
        renameTokensButton.clicked.connect(partial(self.renameTokens, 
                                                            guideRoot,
                                                            rigRoot,
                                                            geometryGroup,
                                                            guidePivotSuffix,
                                                            guideShapeSuffix,
                                                            spaceSuffix,
                                                            controlSuffix,
                                                            skinJointSuffix,
                                                            leftSideToken,
                                                            rightSideToken))
        cancelButton.clicked.connect(self.cancelSettings)
        saveButton.clicked.connect(partial(self.saveSettings, close=True))

        globalLayout = QVBoxLayout()
        globalLayout.addWidget(self.tabWidget)
        globalLayout.addLayout(saveLayout)

        self.centralWidget.setLayout(globalLayout)

        self.settingsWindow.setWindowTitle('BEAR Builder Settings')
        self.settingsWindow.setGeometry(self.screenWidth/2.5, self.screenHeight/5, self.screenWidth/4.5, self.screenHeight/2.8)
        mousePos = QCursor().pos()
        self.settingsWindow.move(mousePos.x()+60, mousePos.y()-self.screenHeight/8)
        self.settingsWindow.show()

    def aboutUI(self):

        self.aboutName = 'about'

        if mc.window(self.aboutName, exists=True):
            mc.deleteUI(self.aboutName, window=True)
        
        self.aboutWindow = QMainWindow(self)
        self.aboutWindow.setObjectName(self.aboutName)

        self.centralWidget = QWidget()
        self.aboutWindow.setCentralWidget(self.centralWidget)

        boxLayout = QVBoxLayout(self.centralWidget)

        bearVersionFile = open(self.rootFolder+'/system/version.txt')
        bearVersion = bearVersionFile.read()

        label1 = QLabel()
        labelLicense = QLabel()
        label2 = QLabel()
        label3 = QLabel()
        label4 = QLabel()
        text1 = u'BEAR - BE-A-Rigger'
        textLicense = u'License: Free'
        text2 = u'Version: Core %s'%bearVersion
        text3 = u'''<a href='http://www.bearigger.com'>www.bearigger.com</a>'''
        text4 = u'© Gregor Weiss'
        label1.setText(text1)
        labelLicense.setText(textLicense)
        label2.setText(text2)
        label3.setText(text3)
        label4.setText(text4)

        label3.setTextFormat(Qt.RichText)
        label3.setTextInteractionFlags(Qt.TextBrowserInteraction)
        label3.setOpenExternalLinks(True)
        
        logoLabel = QLabel(self)
        logoLabel.setPixmap(getLogo(tile=10))

        boxLayout.addWidget(label1, alignment=Qt.AlignCenter)
        boxLayout.addWidget(labelLicense, alignment=Qt.AlignCenter)
        boxLayout.addWidget(label2, alignment=Qt.AlignCenter)
        boxLayout.addWidget(label3, alignment=Qt.AlignCenter)
        boxLayout.addWidget(logoLabel, alignment=Qt.AlignCenter)
        boxLayout.addWidget(label4, alignment=Qt.AlignCenter)

        self.aboutWindow.setWindowTitle('BEAR About')
        aboutCenter = self.aboutWindow.frameGeometry().center()
        center = QPoint(aboutCenter.x()*2, aboutCenter.y()*2)
        self.aboutWindow.move(QDesktopWidget().availableGeometry().center() - center)
        mousePos = QCursor().pos()
        self.aboutWindow.move(mousePos.x()+100, mousePos.y()-self.screenHeight/12)
        self.aboutWindow.show()

    def getModules(self, moduleFolder):
        
        moduleNames = list()
        path = self.rootFolder+'/components'+moduleFolder
        if os.path.isdir(path):
            for fileName in os.listdir(path):
                if (fileName.endswith('.py') or fileName.endswith('.pyc')) and not '__init__.py' in fileName and not fileName == '__pycache__':
                    moduleName = fileName.split('.')[0]
                    module = DataStructure.getModuleByName(moduleName, moduleFolder, self.rootFolder)
                    buildAttrs = DataStructure.getSignature(module)
                    if 'notInUse' in buildAttrs.keys():
                        continue
                    if buildAttrs != {} and not moduleName in ['Curve']:
                        if not moduleName in moduleNames:
                            moduleNames.append(moduleName)

        return moduleNames

    def getCollections(self, collectionFolder):
        
        collectionNames = list()
        path = self.rootFolder+'/collections'+collectionFolder
        if os.path.isdir(path):
            for fileName in os.listdir(path):
                if fileName[-3:] == '.ma' or fileName == '.mb':
                    collectionName = fileName[:-3]
                    collectionNames.append(collectionName)

        return collectionNames

    def getFolders(self, parentFolder):
        
        folders = ['/'+x for x in os.listdir(self.rootFolder+parentFolder) if not '__init__'in x and not 'Empty' in x and not x == '__pycache__']

        return folders

    def lineEditWithPicker(self, 
                        lineEdit, 
                        isSubFolder=True, 
                        isAssetFolder=False, 
                        isProjectFolder=False, 
                        isCustomFolder=False, 
                        customFile=False,
                        versionPicker=None):

        layout = QHBoxLayout()
        layout.addWidget(lineEdit)
        folderButton = self.createFolderButton(lineEdit, isSubFolder, isAssetFolder, isProjectFolder, isCustomFolder, customFile, versionPicker)
        layout.addWidget(folderButton)

        return layout, folderButton

    def tooltips(self, checkBox=None, settingsTooltip=None):
        
        self.loadSettings()
        if checkBox == None:
            checkState = self.loadedSettings['showTooltips']
        else:
            checkState = checkBox.isChecked()
        if settingsTooltip:
            settingsTooltip.setVisible(checkState)
        self.collectionsTooltip.setVisible(checkState)
        self.componentsTooltip.setVisible(checkState)
        self.nameTooltip.setVisible(checkState)
        self.guideToolsTooltip.setVisible(checkState)
        self.modelTooltip.setVisible(checkState)
        self.guideTooltip.setVisible(checkState)
        self.guideSettingsTooltip.setVisible(checkState)
        self.rigTooltip.setVisible(checkState)
        self.rigSettingsTooltip.setVisible(checkState)
        self.buildFromAssetTooltip.setVisible(checkState)
        self.deformerTooltip.setVisible(checkState)
        self.postDeformTooltip.setVisible(checkState)
        if Settings.licenseVersion != 'free':
            self.faceCorrectionsTooltip.setVisible(checkState)
            self.poseCorrectionsTooltip.setVisible(checkState)
        self.deformFromAssetTooltip.setVisible(checkState)

    def setComponentName(self, treeParent, *args, **kwargs):
        
        if len(self.collectionTreeParent.selectedItems()) > 0 and len(self.componentTreeParent.selectedItems()) > 0:
            if treeParent == self.collectionTreeParent:
                for selectedItem in self.componentTreeParent.selectedItems():
                    self.componentTreeParent.setItemSelected(selectedItem, False)
            if treeParent == self.componentTreeParent:
                for selectedItem in self.collectionTreeParent.selectedItems():
                    self.collectionTreeParent.setItemSelected(selectedItem, False)
        if len(self.collectionTreeParent.selectedItems()) > 0 and len(self.componentTreeParent.selectedItems()) > 0:
            if self.collectionTreeParent.currentItem().parent() is not None and self.componentTreeParent.currentItem().parent() is not None:
                self.compName.setText('multiple selected')
                self.compName.setEnabled(False)
                return

        selectedItems = self.collectionTreeParent.selectedItems()+self.componentTreeParent.selectedItems()
        for selectedItem in selectedItems:
            if selectedItem.parent() is None and len(selectedItems) > 1 and selectedItem.text(0) != 'Empty':
                treeParent.setItemSelected(selectedItem, False)
        selectedItems = self.collectionTreeParent.selectedItems()+self.componentTreeParent.selectedItems()

        if len(selectedItems) == 0:
            self.compName.setText('')
            self.compName.setEnabled(True)
        elif len(selectedItems) == 1:
            selectedItem = selectedItems[0]
            if selectedItem.parent() is not None:
                if selectedItem.treeWidget() == self.componentTreeParent:
                    if selectedItem.parent() is not None:
                        moduleFolder = '/'+selectedItem.parent().text(0)
                        moduleName = selectedItem.text(0)
                        module = DataStructure.getModuleByName(moduleName, moduleFolder, self.rootFolder)
                        buildAttrs = DataStructure.getSignature(module)
                        if buildAttrs != {}:
                            for buildAttr, value in buildAttrs.items():
                                if buildAttr == 'name':
                                    compName = value
                else:
                    compName = selectedItem.text(0)[0].lower()+selectedItem.text(0)[1:]
            elif selectedItem.text(0) == 'Empty':
                compName = 'collection'
            else:
                compName = ''
            self.compName.setText(compName)
            self.compName.setEnabled(True)
        else:
            self.compName.setText('multiple selected')
            self.compName.setEnabled(False)

    def createTree(self, treeParent, treeParentName):

        treeParent.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for folder in self.getFolders('/'+treeParentName):
            treeWidget = QTreeWidgetItem(folder)
            treeWidget.setText(0, folder[1:])
            treeParent.addTopLevelItem(treeWidget)
            if treeParentName == 'collections':
                subItems = self.getCollections(folder)
            else:
                subItems = self.getModules(folder)
            for subItem in subItems:
                subWidget = QTreeWidgetItem(subItem)
                subWidget.setText(0, subItem)
                treeWidget.addChild(subWidget)
        if treeParentName == 'collections':
            newWidget = QTreeWidgetItem('Empty')
            newWidget.setText(0, 'Empty')
            treeParent.addTopLevelItem(newWidget)

        return treeParent

    def definitionTab(self):
        
        boxLayout = QVBoxLayout(self.createWidget)
        
        nameLayout = QHBoxLayout()
        nameLayout.addWidget(self.compName)
        nameLayout.addWidget(self.nameTooltip)
        formLayout = QFormLayout()
        formLayout.addRow('Name:', nameLayout)

        collectionLayout = QHBoxLayout()
        componentLayout = QHBoxLayout()
        
        self.collectionTreeParent = self.createTree(self.collectionTree, 'collections')
        self.componentTreeParent = self.createTree(self.componentTree, 'components')

        self.collectionTreeParent.currentItemChanged.connect(partial(self.setComponentName, self.collectionTreeParent))
        self.collectionTreeParent.itemClicked.connect(partial(self.setComponentName, self.collectionTreeParent))
        self.componentTreeParent.currentItemChanged.connect(partial(self.setComponentName, self.componentTreeParent))
        self.componentTreeParent.itemClicked.connect(partial(self.setComponentName, self.componentTreeParent))

        collectionLayout.addWidget(self.collectionTree)
        collectionLayout.addWidget(self.collectionsTooltip)
        componentLayout.addWidget(self.componentTree)
        componentLayout.addWidget(self.componentsTooltip)

        componentTreeLayout = QVBoxLayout()
        componentTreeLayout.addLayout(collectionLayout)
        componentTreeLayout.addLayout(componentLayout)

        addSplitter(boxLayout)

        self.createButton.clicked.connect(self.create)

        createLayout = QHBoxLayout()
        logoLabel = QLabel(self)
        logoLabel.setPixmap(getLogo(tile=20))
        createLayout.addWidget(logoLabel, alignment=Qt.AlignLeft)
        createLayout.addWidget(self.createButton, alignment=Qt.AlignRight)

        boxLayout.addLayout(createLayout)

        boxLayout.insertLayout(0, componentTreeLayout)
        boxLayout.insertLayout(1, formLayout)

    def updateEnabled(self, input1, input2, target, *args):

        if input1.isChecked() and input2.isChecked():
            target.setEnabled(True)
        else:
            target.setEnabled(False)

    def updateEnabledSide(self, input1, input2, target, *args):

        if input1.isChecked() and not input2.isChecked():
            target.setEnabled(True)
        else:
            target.setEnabled(False)

    def updateSetChecked(self, input1, target, *args):

        if input1.isChecked():
            target.setChecked(True)

    def buildTab(self):

        boxLayout = QVBoxLayout(self.buildWidget)

        formLayout = QFormLayout()

        # align to geo
        alignToGeoLayout = QHBoxLayout()
        self.alignToGeoCheckbox = QCheckBox('Align to Geometry:')
        self.alignToGeoText = QLineEdit()
        button = QPushButton()
        button.setIcon(QApplication.style().standardIcon(QStyle.SP_ArrowBack))
        button.setFixedSize(18, 18)
        button.clicked.connect(self.setAlignGeoText)
        self.alignToGeoCheckbox.setChecked(False)
        self.alignToGeoCheckbox.setEnabled(False)
        self.alignToGeoCheckbox.setVisible(Settings.licenseVersion == 'full')
        self.alignToGeoText.setEnabled(False)
        self.alignToGeoText.setVisible(Settings.licenseVersion == 'full')
        button.setEnabled(False)
        button.setVisible(Settings.licenseVersion == 'full')
        self.guideCheckBox.stateChanged.connect(self.alignToGeoCheckbox.setEnabled)
        self.guideCheckBox.stateChanged.connect(partial(self.updateEnabled, self.guideCheckBox, self.alignToGeoCheckbox, self.alignToGeoText))
        self.guideCheckBox.stateChanged.connect(partial(self.updateEnabled, self.guideCheckBox, self.alignToGeoCheckbox, button))
        self.alignToGeoCheckbox.stateChanged.connect(partial(self.updateEnabled, self.guideCheckBox, self.alignToGeoCheckbox, self.alignToGeoText))
        self.alignToGeoCheckbox.stateChanged.connect(partial(self.updateEnabled, self.guideCheckBox, self.alignToGeoCheckbox, button))
        alignToGeoLayout.addWidget(self.alignToGeoCheckbox)
        alignToGeoLayout.addWidget(self.alignToGeoText)
        alignToGeoLayout.addWidget(button)

        #side
        sideGroup = QButtonGroup(self.buildWidget)
        sideLayout = QHBoxLayout()
        sideLabel = QLabel('Side:')
        sideLabel.setEnabled(False)
        sideLayout.addWidget(sideLabel)
        sideLayout.addWidget(self.buildSideNone)
        self.buildSideNone.setChecked(True)
        self.buildSideNone.setEnabled(False)
        self.buildSideLeft.setEnabled(False)
        self.buildSideRight.setEnabled(False)
        sideLayout.addWidget(self.buildSideLeft)
        sideLayout.addWidget(self.buildSideRight)
        sideGroup.addButton(self.buildSideNone)
        sideGroup.addButton(self.buildSideLeft)
        sideGroup.addButton(self.buildSideRight)
        sideGroup.setId(self.buildSideNone, 1)
        sideGroup.setId(self.buildSideLeft, 1)
        sideGroup.setId(self.buildSideRight, 1)
        self.guideCheckBox.stateChanged.connect(partial(self.updateEnabledSide, self.guideCheckBox, self.alignToGeoCheckbox, sideLabel))
        self.guideCheckBox.stateChanged.connect(partial(self.updateEnabledSide, self.guideCheckBox, self.alignToGeoCheckbox, self.buildSideNone))
        self.guideCheckBox.stateChanged.connect(partial(self.updateEnabledSide, self.guideCheckBox, self.alignToGeoCheckbox, self.buildSideLeft))
        self.guideCheckBox.stateChanged.connect(partial(self.updateEnabledSide, self.guideCheckBox, self.alignToGeoCheckbox, self.buildSideRight))
        self.alignToGeoCheckbox.stateChanged.connect(partial(self.updateEnabledSide, self.guideCheckBox, self.alignToGeoCheckbox, sideLabel))
        self.alignToGeoCheckbox.stateChanged.connect(partial(self.updateEnabledSide, self.guideCheckBox, self.alignToGeoCheckbox, self.buildSideNone))
        self.alignToGeoCheckbox.stateChanged.connect(partial(self.updateEnabledSide, self.guideCheckBox, self.alignToGeoCheckbox, self.buildSideLeft))
        self.alignToGeoCheckbox.stateChanged.connect(partial(self.updateEnabledSide, self.guideCheckBox, self.alignToGeoCheckbox, self.buildSideRight))

        #from asset
        fromAssetLayout = QHBoxLayout(self.buildWidget)
        self.buildVersion = QComboBox()
        self.buildAssetFolder.setEnabled(False)
        assetLayout, buildAssetFolderPicker = self.lineEditWithPicker(self.buildAssetFolder, isSubFolder=True, isAssetFolder=True, versionPicker=self.buildVersion)
        buildAssetFolderPicker.setEnabled(False)
        assetLayout.setEnabled(False)
        self.buildFromAssetCheckBox = QCheckBox()
        self.buildFromAssetCheckBox.toggled.connect(self.buildAssetFolder.setEnabled)
        self.buildFromAssetCheckBox.toggled.connect(buildAssetFolderPicker.setEnabled)
        self.alignToGeoCheckbox.stateChanged.connect(partial(self.updateSetChecked, self.alignToGeoCheckbox, self.buildFromAssetCheckBox))
        fromAssetLayout.addWidget(self.buildFromAssetCheckBox, alignment=Qt.AlignTop)
        fromAssetLayout.addLayout(formLayout)
        formLayout.addRow('From Asset:', assetLayout)
        fromAssetLayout.addWidget(self.buildFromAssetTooltip)

        #version
        versionLayout = QHBoxLayout()
        versionLayout.addWidget(self.buildVersion, alignment=Qt.AlignLeft)
        self.buildVersion.setEnabled(False)
        self.buildFromAssetCheckBox.toggled.connect(self.buildVersion.setEnabled)
        if self.projectFolder and self.assetFolder:
            self.getVersions(self.buildVersion, self.projectFolder+'/'+self.assetFolder)
        formLayout.addRow(QLabel('From Version:'), versionLayout)

        stepsLayout = QVBoxLayout()

        boxLayout.addWidget(QLabel('Guide Tools:'))
        guideToolsLayout = QHBoxLayout()
        guideToolsLayout.addWidget(self.selectComponentButton, alignment=Qt.AlignRight)
        guideToolsLayout.addWidget(self.guideSelectPivotButton, alignment=Qt.AlignRight)
        guideToolsLayout.addWidget(self.guideSelectShapeButton, alignment=Qt.AlignRight)
        guideToolsLayout.addWidget(self.showGuidePropertiesButton, alignment=Qt.AlignRight)
        guideToolsLayout.addWidget(self.guideToolsTooltip, alignment=Qt.AlignRight)
        boxLayout.addLayout(guideToolsLayout)
        addSplitter(boxLayout)

        stepsLayout.addWidget(QLabel('Build Steps:'))

        #model
        modelLayout = QHBoxLayout()
        modelLayout.addWidget(self.modelCheckBox)
        modelLayout.addWidget(self.modelTooltip, alignment=Qt.AlignRight)
        stepsLayout.addLayout(modelLayout)
        subModelLayout = QHBoxLayout()
        modelCheckBoxAssetNameLayout = QHBoxLayout()
        subModelLayout.addSpacing(20)
        subModelItemsLayout = QVBoxLayout()
        subModelItemsLayout.addLayout(modelCheckBoxAssetNameLayout)
        stepsLayout.addLayout(subModelLayout)
        subModelLayout.addLayout(subModelItemsLayout)

        #guide
        guideLayout = QHBoxLayout()
        guideLayout.addWidget(self.guideCheckBox)
        guideLayout.addWidget(self.guideTooltip, alignment=Qt.AlignRight)
        stepsLayout.addLayout(guideLayout)
        subGuideLayout = QHBoxLayout()
        subGuideLayout.addSpacing(20)
        subGuideItemsLayout = QVBoxLayout()
        subGuideItemsLayout.addLayout(alignToGeoLayout)
        subGuideItemsLayout.addLayout(sideLayout)
        stepsLayout.addLayout(subGuideLayout)
        subGuideLayout.addLayout(subGuideItemsLayout)
        
        #guide settings
        guideSettingsLayout = QHBoxLayout()
        guideSettingsLayout.addWidget(self.guideSettingsCheckBox)
        guideSettingsLayout.addWidget(self.guideSettingsTooltip, alignment=Qt.AlignRight)
        stepsLayout.addLayout(guideSettingsLayout)
        subGuideSettingsLayout = QHBoxLayout()
        subGuideSettingsLayout.addSpacing(20)
        subGuideSettingsItemsLayout = QVBoxLayout()
        self.guideDefinitionCheckBox.setEnabled(False)
        self.guidePositionCheckBox.setEnabled(False)
        self.guideOrientationCheckBox.setEnabled(False)
        self.guideShapeSettingsCheckBox.setEnabled(False)
        self.guideShapeTransformsCheckBox.setEnabled(False)
        self.guideDefinitionCheckBox.setChecked(True)
        self.guidePositionCheckBox.setChecked(True)
        self.guideOrientationCheckBox.setChecked(True)
        self.guideShapeSettingsCheckBox.setChecked(True)
        self.guideShapeTransformsCheckBox.setChecked(True)
        self.guideSettingsCheckBox.stateChanged.connect(self.guideDefinitionCheckBox.setEnabled)
        self.guideSettingsCheckBox.stateChanged.connect(self.guidePositionCheckBox.setEnabled)
        self.guideSettingsCheckBox.stateChanged.connect(self.guideOrientationCheckBox.setEnabled)
        self.guideSettingsCheckBox.stateChanged.connect(self.guideShapeSettingsCheckBox.setEnabled)
        self.guideSettingsCheckBox.stateChanged.connect(self.guideShapeTransformsCheckBox.setEnabled)
        subGuideSettingsItemsLayout.addWidget(self.guideDefinitionCheckBox)
        subGuideSettingsItemsLayout.addWidget(self.guidePositionCheckBox)
        subGuideSettingsItemsLayout.addWidget(self.guideOrientationCheckBox)
        subGuideSettingsItemsLayout.addWidget(self.guideShapeSettingsCheckBox)
        subGuideSettingsItemsLayout.addWidget(self.guideShapeTransformsCheckBox)
        stepsLayout.addLayout(subGuideSettingsLayout)
        subGuideSettingsLayout.addLayout(subGuideSettingsItemsLayout)

        # rig and rig settings
        rigLayout = QHBoxLayout()
        rigLayout.addWidget(self.rigCheckBox)
        rigLayout.addWidget(self.rigTooltip, alignment=Qt.AlignRight)
        stepsLayout.addLayout(rigLayout)
        rigSettingsLayout = QHBoxLayout()
        rigSettingsLayout.addWidget(self.rigSettingsCheckBox)
        rigSettingsLayout.addWidget(self.rigSettingsTooltip, alignment=Qt.AlignRight)
        stepsLayout.addLayout(rigSettingsLayout)

        selectLayout = QHBoxLayout()
        self.buildSelectAll.setChecked(True)
        selectLayout.addWidget(self.buildSelectAll, alignment=Qt.AlignRight)
        selectLayout.addWidget(self.buildSelectSelected, alignment=Qt.AlignRight)
        
        executeLayout = QHBoxLayout()
        executeLayout.insertLayout(0, selectLayout)
        self.buildButton.clicked.connect(self.build)
        executeLayout.addWidget(self.buildButton, alignment=Qt.AlignRight)

        boxLayout.addLayout(stepsLayout)

        addSplitter(boxLayout)
        boxLayout.addLayout(fromAssetLayout)
        addSplitter(boxLayout)
        boxLayout.addLayout(executeLayout)

    def deformTab(self):

        boxLayout = QVBoxLayout(self.assembleWidget)

        formLayout = QFormLayout()
        
        #from asset
        fromAssetLayout = QHBoxLayout(self.assembleWidget)
        self.assembleVersion = QComboBox()
        self.assembleAssetFolder.setEnabled(False)
        versionAssetLayout, assembleAssetFolderPicker = self.lineEditWithPicker(self.assembleAssetFolder, isSubFolder=True, isAssetFolder=True, versionPicker=self.assembleVersion)
        assembleAssetFolderPicker.setEnabled(False)
        versionAssetLayout.setEnabled(False)
        self.assembleFromAssetCheckBox = QCheckBox()
        self.assembleFromAssetCheckBox.toggled.connect(self.assembleAssetFolder.setEnabled)
        self.assembleFromAssetCheckBox.toggled.connect(assembleAssetFolderPicker.setEnabled)
        fromAssetLayout.addWidget(self.assembleFromAssetCheckBox, alignment=Qt.AlignTop)
        fromAssetLayout.addLayout(formLayout)
        formLayout.addRow('From Asset:', versionAssetLayout)
        fromAssetLayout.addWidget(self.deformFromAssetTooltip)

        #version
        versionLayout = QHBoxLayout()
        versionLayout.addWidget(self.assembleVersion, alignment=Qt.AlignLeft)
        self.assembleVersion.setEnabled(False)
        self.assembleFromAssetCheckBox.toggled.connect(self.assembleVersion.setEnabled)
        if self.projectFolder and self.assetFolder:
            self.getVersions(self.assembleVersion, self.projectFolder+'/'+self.assetFolder)
        formLayout.addRow(QLabel('From Version:'), versionLayout)

        #pre skin
        stepsLayout = QVBoxLayout()
        
        #deform
        stepsLayout.addWidget(QLabel('Deform Steps:'))
        skinGroup = QButtonGroup(self.assembleWidget)
        selectGroup = QButtonGroup(self.assembleWidget)
        self.vertexID.setEnabled(False)
        self.vertexID.setChecked(True)
        self.vertexPosition.setEnabled(False)
        self.uvs.setEnabled(False)
        skinGroup.addButton(self.vertexID)
        skinGroup.addButton(self.vertexPosition)
        skinGroup.addButton(self.uvs)
        skinGroup.setId(self.vertexID, 3)
        skinGroup.setId(self.vertexPosition, 3)
        skinGroup.setId(self.uvs, 3)
        selectGroup.addButton(self.assembleSelectAll)
        selectGroup.addButton(self.assembleSelectSelected)
        selectGroup.setId(self.assembleSelectAll, 4)
        selectGroup.setId(self.assembleSelectSelected, 4)
        self.assembleSelectAll.setChecked(True)
        self.assembleSelectAll.setEnabled(False)
        self.assembleSelectSelected.setEnabled(False)
        
        # deformer
        deformerLayout = QHBoxLayout()
        deformerLayout.addWidget(self.deformerCheckBox)
        deformerLayout.addWidget(self.deformerTooltip, alignment=Qt.AlignRight)
        stepsLayout.addLayout(deformerLayout)
        subDeformerLayout = QHBoxLayout()
        subDeformerLayout.addSpacing(20)
        subDeformerItemsLayout = QVBoxLayout()

        #skin
        skinLayout = QHBoxLayout()
        skinLayout.addWidget(self.skinCheckBox)
        subDeformerItemsLayout.addLayout(skinLayout)

        subSkinLayout = QHBoxLayout()
        subSkinLayout.addSpacing(5)
        subDeformerItemsLayout.addLayout(subSkinLayout)

        subSkinOptionsLayout = QHBoxLayout()
        subSkinOptionsLayout.addSpacing(20)
        subSkinItemsLayout = QVBoxLayout()
        itemHBoxLayout = QHBoxLayout()
        selectHBoxLayout = QHBoxLayout()
        subSkinItemsLayout.addLayout(itemHBoxLayout)
        subSkinOptionsLayout.addLayout(subSkinItemsLayout)
        subSkinLayout.addLayout(subSkinOptionsLayout)

        itemHBoxLayout.addWidget(self.vertexID)
        itemHBoxLayout.addWidget(self.vertexPosition)
        itemHBoxLayout.addWidget(self.uvs)
        selectHBoxLayout.addWidget(self.assembleSelectAll)
        selectHBoxLayout.addWidget(self.assembleSelectSelected)
        selectGroup = QButtonGroup(self.assembleWidget)
        
        self.skinCheckBox.setChecked(True)
        self.latticeCheckBox.setChecked(True)
        self.smoothCheckBox.setChecked(True)
        self.proximityWrapCheckBox.setChecked(True)
        self.geometryConstraintsCheckBox.setChecked(True)
        self.inputOrderCheckBox.setChecked(True)
        
        self.skinCheckBox.stateChanged.connect(partial(self.updateEnabled, self.deformerCheckBox, self.skinCheckBox, self.vertexID))
        self.skinCheckBox.stateChanged.connect(partial(self.updateEnabled, self.deformerCheckBox, self.skinCheckBox, self.vertexPosition))
        self.skinCheckBox.stateChanged.connect(partial(self.updateEnabled, self.deformerCheckBox, self.skinCheckBox, self.uvs))
        
        self.deformerCheckBox.stateChanged.connect(partial(self.updateEnabled, self.deformerCheckBox, self.skinCheckBox, self.vertexID))
        self.deformerCheckBox.stateChanged.connect(partial(self.updateEnabled, self.deformerCheckBox, self.skinCheckBox, self.vertexPosition))
        self.deformerCheckBox.stateChanged.connect(partial(self.updateEnabled, self.deformerCheckBox, self.skinCheckBox, self.uvs))
        self.deformerCheckBox.stateChanged.connect(self.assembleSelectAll.setEnabled)
        self.deformerCheckBox.stateChanged.connect(self.assembleSelectSelected.setEnabled)

        #
        self.skinCheckBox.setEnabled(False)
        self.latticeCheckBox.setEnabled(False)
        self.smoothCheckBox.setEnabled(False)
        self.proximityWrapCheckBox.setEnabled(False)
        self.geometryConstraintsCheckBox.setEnabled(False)
        self.inputOrderCheckBox.setEnabled(False)
        self.deformerCheckBox.stateChanged.connect(self.skinCheckBox.setEnabled)
        self.deformerCheckBox.stateChanged.connect(self.latticeCheckBox.setEnabled)
        self.deformerCheckBox.stateChanged.connect(self.smoothCheckBox.setEnabled)
        self.deformerCheckBox.stateChanged.connect(self.proximityWrapCheckBox.setEnabled)
        self.deformerCheckBox.stateChanged.connect(self.geometryConstraintsCheckBox.setEnabled)
        self.deformerCheckBox.stateChanged.connect(self.inputOrderCheckBox.setEnabled)
        subDeformerItemsLayout.addWidget(self.latticeCheckBox)
        subDeformerItemsLayout.addWidget(self.smoothCheckBox)
        subDeformerItemsLayout.addWidget(self.proximityWrapCheckBox)
        subDeformerItemsLayout.addWidget(self.geometryConstraintsCheckBox)
        subDeformerItemsLayout.addWidget(self.inputOrderCheckBox)
        subDeformerItemsLayout.addSpacing(10)
        subDeformerItemsLayout.addLayout(selectHBoxLayout)
        stepsLayout.addLayout(subDeformerLayout)
        subDeformerLayout.addLayout(subDeformerItemsLayout)

        deformLayout = QHBoxLayout()
        deformLayout.addWidget(self.deformerCheckBox)
        deformLayout.addWidget(self.deformerTooltip, alignment=Qt.AlignRight)
        deformLayout.addLayout(deformerLayout)
        stepsLayout.addLayout(deformLayout)

        #post skin, blendshapes
        if Settings.licenseVersion != 'free':
            
            faceCorrectionsLayout = QHBoxLayout()
            faceCorrectionsLayout.addWidget(self.faceCorrectionsCheckBox)
            faceCorrectionsLayout.addWidget(self.faceCorrectionsTooltip, alignment=Qt.AlignRight)
            stepsLayout.addLayout(faceCorrectionsLayout)
            
            poseCorrectionsLayout = QHBoxLayout()
            poseCorrectionsLayout.addWidget(self.poseCorrectionsCheckBox)
            poseCorrectionsLayout.addWidget(self.poseCorrectionsTooltip, alignment=Qt.AlignRight)
            stepsLayout.addLayout(poseCorrectionsLayout)
        
        postDeformLayout = QHBoxLayout()
        postDeformLayout.addWidget(self.postDeformCheckBox)
        postDeformLayout.addWidget(self.postDeformTooltip, alignment=Qt.AlignRight)
        stepsLayout.addLayout(postDeformLayout)

        addSplitter(boxLayout)

        boxLayout.insertLayout(0, stepsLayout)
        boxLayout.insertLayout(2, fromAssetLayout)
        
        addSplitter(boxLayout)

        self.assembleButton.clicked.connect(self.assemble)
        boxLayout.addWidget(self.assembleButton, alignment=Qt.AlignRight)

    @UndoDec.undo
    def create(self):

        currentSelection = mc.ls(sl=True)
        
        # check name string
        if not re.match("^[a-zA-Z0-9]*$", self.compName.text()) and self.compName.text() != 'multiple selected':
            MessageHandling.invalidCharacter()
            return

        # collections

        selectedCollections = list()
        for selectedItem in [x for x in self.collectionTreeParent.selectedItems() if x.parent() is not None or x.text(0) == 'Empty']:
            if not MessageHandling.uniqueName(self.compName.text()+'_'+self.guideRoot, item=selectedItem.text(0), type='collection'):
                continue
            itemName = selectedItem.text(0)[0].lower()+selectedItem.text(0)[1:]
            if mc.objExists(itemName+'_'+self.guideRoot) and self.compName.text() == 'multiple selected':
                if not MessageHandling.uniqueName(itemName+'_'+self.guideRoot, item=selectedItem.text(0), type='collection'):
                    continue
            if selectedItem.text(0) == 'Empty' and (self.compName.text() == 'collection' or self.compName.text() == 'multiple selected'):
                if not MessageHandling.uniqueName('collection'+'_'+self.guideRoot, item=selectedItem.text(0), type='collection'):
                    continue
            selectedCollections.append(selectedItem)
        
        for selectedCollection in selectedCollections:
            collectionFolder = '' if selectedCollection.parent() is None else '/'+selectedCollection.parent().text(0)
            filePath = self.rootFolder+'/collections'+collectionFolder+'/'+selectedCollection.text(0)+'.ma'
            name = self.compName.text() if self.compName.text() != 'multiple selected' else None
            guideFile = DataStructure.Asset(loadFromFile=filePath).guideSettings(copyGuide=True,
                                                                                    newCollectionName=name)[0]
            if guideFile:
                mc.file(guideFile, removeReference=True)
            Nodes.renameToNamingConvention(Settings.namingOrder)
            self.renameTokens(Settings.guideRoot,
                                Settings.rigRoot,
                                Settings.geometryGroup,
                                Settings.guidePivotSuffix,
                                Settings.guideShapeSuffix,
                                Settings.offNodeSuffix,
                                Settings.controlSuffix,
                                Settings.skinJointSuffix,
                                Settings.leftSide,
                                Settings.rightSide,
                                query=False,
                                renameOnCreation=True)

        # components
        selectedModules = list()
        for selectedItem in [x for x in self.componentTreeParent.selectedItems() if x.parent() is not None]:
            moduleFolder = '' if selectedItem.parent() is None else '/'+selectedItem.parent().text(0)
            module = DataStructure.getModuleByName(selectedItem.text(0), moduleFolder, self.rootFolder)
            selectedModules.append(module)

        guideGroups = list()
        for selectedModule in selectedModules:
            name = self.compName.text() if len(selectedModules) == 1 and len(self.collectionTreeParent.selectedItems()) == 0 else None
            guideGroup = Component.Build(module=selectedModule, 
                                            name=name, 
                                            buildStep='definition').create()
            guideGroups.append(guideGroup)
            if len(currentSelection) == 1:
                if mc.objExists('%s.componentType'%currentSelection[0]):
                    if mc.getAttr('%s.componentType'%currentSelection[0]) == 'Collection':
                        selGuideGroup = Nodes.replaceNodeType(currentSelection[0], Settings.guideGroup)
                        mc.parent(guideGroup, selGuideGroup)
                    else:
                        parentSelection = Nodes.getParent(currentSelection[0])
                        if parentSelection:
                            if mc.objExists('%s.componentType'%parentSelection):
                                if mc.getAttr('%s.componentType'%parentSelection) == 'Collection':
                                    selGuideGroup = Nodes.replaceNodeType(parentSelection, Settings.guideGroup)
                                    mc.parent(guideGroup, selGuideGroup)

        if not None in guideGroups:
            mc.select(guideGroups)

    @UndoDec.undo
    def build(self):
            
        mc.scriptEditorInfo(suppressInfo=False, suppressWarnings=True, suppressResults=False, suppressErrors=False)

        self.removeCallback()
        
        self.loadSettings()
        
        # removing guideAlign reference if any
        if not self.guideCheckBox.isChecked() or not self.alignToGeoCheckbox.isChecked():
            refNodes = mc.ls(type='reference')
            for refNode in refNodes:
                if 'guideAlign' in refNode:
                    filePath = mc.referenceQuery(refNode, filename=True)
                    mc.file(filePath, removeReference=True)
        
        # converting old guide to new guide with placer guides
        if self.guideCheckBox.isChecked():
            updateGroups = list()
            guideGroups = [x for x in mc.ls(type='transform') \
                           if (Nodes.getComponentType(x) == 'Leg' or Nodes.getComponentType(x) == 'Arm') \
                            and Nodes.getNodeType(x) == Settings.guideGroup \
                            and not mc.referenceQuery(x, isNodeReferenced=True)]
            for guideGroup in guideGroups[::]:
                if not mc.getAttr(guideGroup+'.readyForRigBuild'):
                    continue
                oldLimbRig = False
                bearVersion = mc.getAttr('%s.bearVersion'%guideGroup).split('.')
                if int(bearVersion[0]) == 0:
                    oldLimbRig = True
                else:
                    oldLimbRig = int(bearVersion[1]) < 2
                if oldLimbRig:
                    updateGroups.append(guideGroup)
            if updateGroups:
                MessageHandling.convertToGuidePlacer()
                for guideGroup in updateGroups:
                    for n in range(2):
                        output = Component.Build(buildStep='guide', 
                                                side=Nodes.getSide(guideGroup),
                                                assetFolder=self.assetFolder).createByCompGroup(guideGroup)
                MessageHandling.convertToGuidePlacerComplete()

        # folder and file checks

        self.assetFolder = self.buildAssetFolder.text() if self.buildFromAssetCheckBox.isChecked() else self.loadedSettings['assetFolder']

        if self.buildFromAssetCheckBox.isChecked():
            versionName = self.buildVersion.currentText()
        else:
            versionName = Files.Config(self.projectFolder,
                                            self.assetFolder).getVersion()

        # If the From Asset Checkbox is checked, the current guide will be ignored and only the external guide will be built
        createFromBuildAsset = self.buildFromAssetCheckBox.isChecked()

        if self.modelCheckBox.isChecked() and self.assetFolder:
            if not MessageHandling.fileExists(Files.Config(self.projectFolder,
                                                             self.assetFolder,
                                                             version=versionName,
                                                             fileType=Settings.modelFileIndicator).assembleFilePath(),
                                                Settings.modelFileIndicator):
                return

        if self.guideSettingsCheckBox.isChecked() and self.assetFolder:
            if not MessageHandling.fileExists(Files.Config(self.projectFolder,
                                                             self.assetFolder,
                                                             version=versionName,
                                                             fileType=Settings.guideFileIndicator).assembleFilePath(),
                                                Settings.guideFileIndicator):
                return
            
        if self.rigSettingsCheckBox.isChecked() and self.assetFolder:
            if not MessageHandling.folderExists(Files.Config(self.projectFolder,
                                                             self.assetFolder,
                                                             version=versionName,
                                                             fileType=Settings.rigSettingsFileIndicator).assembleFolderPath()):
                return
                
        # building
        
        if self.modelCheckBox.isChecked():
            assetNode = None
            if assetNode == None or MessageHandling.alreadyExists(assetNode, queryReplace=True):
                if self.assetFolder == '':
                    DataStructure.Asset().model()
                else:
                    mc.file(f=True, new=True)
                    Component.Build(buildStep='model').create()
        
        buildSteps = list()
        if self.modelCheckBox.isChecked():
            buildSteps.append('model')
        if self.guideCheckBox.isChecked():
            buildSteps.append('guide')
        if self.guideSettingsCheckBox.isChecked():
            buildSteps.append('guideSettings')
        if self.rigCheckBox.isChecked():
            buildSteps.append('rig')
        if self.rigSettingsCheckBox.isChecked():
            buildSteps.append('rigSettings')
        
        currentSelection = mc.ls(sl=True, type='transform')
        guideGroups = list()
        rigGroups = list()
        allGuideGroups = list()
        rootSelected = False
        for selectedNode in currentSelection:
            if selectedNode == Settings.guideRoot or selectedNode == Settings.rigRoot:
                rootSelected = True
        if self.buildSelectAll.isChecked() or rootSelected:
            if mc.objExists(Settings.guideRoot):
                guideChildren = mc.listRelatives(Settings.guideRoot, children=True, type='transform')
                if guideChildren == None:
                    guideChildren = []
                if not guideChildren and not self.buildFromAssetCheckBox.isChecked():
                    MessageHandling.noGuide()
                    return
                else:
                    guideChildren = [x for x in guideChildren if Nodes.getNodeType(x) == 'guide']
                    guideGroups.extend(guideChildren)
            if mc.objExists('rig'):
                rigChildren = mc.listRelatives('rig', children=True, type='transform')
                if rigChildren != None:
                    rigGroups.extend([x for x in rigChildren if Nodes.getNodeType(x) == 'rig'])
            if (self.guideCheckBox.isChecked() or self.rigCheckBox.isChecked()) and Nodes.exists(Settings.guideRoot):
                for x in Nodes.getAllChildren(Settings.guideRoot):
                    if mc.objExists(x+'.componentType'):
                        if not mc.getAttr(x+'.componentType') == 'Collection':
                            allGuideGroups.append(x)
        else:
            for selectedNode in mc.ls(sl=True, type='transform'):
                # if a node inside the module is selected, we search for the upper stream compGroup
                compGroup = None
                if self.guideCheckBox.isChecked() and self.alignToGeoCheckbox.isChecked():
                    if mc.objExists('%s.componentType'%selectedNode):
                        compGroup = selectedNode
                else:
                    for parentNode in [selectedNode]+Nodes.getAllParents(selectedNode)[::-1]:
                        if mc.objExists('%s.componentType'%parentNode):
                            compGroup = parentNode
                            break
                if compGroup:
                    guideGroup = Nodes.replaceNodeType(compGroup, 'guide')
                    if not guideGroup in guideGroups:
                        guideGroups.append(guideGroup)
                        # only if we want to get a query pop-up on selected
                        #if Nodes.getComponentType(guideGroup) != 'Collection':
                            #allGuideGroups.append(guideGroup)
                    if Nodes.getComponentType(guideGroup) == 'Collection':
                        for x in Nodes.getAllChildren(guideGroup):
                            if mc.objExists(x+'.componentType'):
                                if not mc.getAttr(x+'.componentType') == 'Collection':
                                    allGuideGroups.append(x)
            if guideGroups == [] and (self.guideCheckBox.isChecked() or self.rigCheckBox.isChecked()) and not self.buildFromAssetCheckBox.isChecked():
                MessageHandling.noComponentGroupSelected()
                return
            if self.rigSettingsCheckBox.isChecked() and len(mc.ls(sl=True, type='transform')) == 0:
                MessageHandling.nothingSelected()
                return
        
        # filtering out rig groups, replacing with guide groups
        for compGroup in guideGroups+rigGroups:
            guideGroup = Nodes.replaceNodeType(compGroup, 'guide')
            if not mc.objExists(guideGroup):
                continue
            userAttrs = mc.listAttr(guideGroup, userDefined=True)
            if userAttrs != None:
                if not 'componentType' in userAttrs:
                    guideGroups.remove(guideGroup)
            # TODO query side building on collections
            if self.guideCheckBox.isChecked() and not self.alignToGeoCheckbox.isChecked():
                if Nodes.getComponentType(guideGroup) == 'Collection' and not self.buildSideNone.isChecked():
                    MessageHandling.querySideBuilding()

        # checking if global scale adjustment is not on collection and components at the same time
        if self.guideCheckBox.isChecked():
            subScaling = False
            for guideGroup in guideGroups:
                if Nodes.getComponentType(guideGroup) == 'Collection':
                    subGroups = mc.listRelatives(guideGroup, children=True, type='transform')
                    if not subGroups:
                        continue
                    for subGroup in subGroups:
                        for node in Nodes.getAllParents(subGroup):
                            if mc.objExists('%s.globalScale'%subGroup) and mc.objExists('%s.globalScale'%node):
                                if mc.getAttr('%s.globalScale'%subGroup) != 1 and mc.getAttr('%s.globalScale'%node) != 1 and node != subGroup:
                                    subScaling = True
                                    break
                if mc.objExists('%s.globalScale'%guideGroup) and mc.objExists('%s.globalScale'%Settings.guideRoot):
                    if mc.getAttr('%s.globalScale'%guideGroup) != 1 and mc.getAttr('%s.globalScale'%Settings.guideRoot) != 1:
                        subScaling = True
            if subScaling:
                MessageHandling.hierarchyScaling()
                return

        # continuing build
        buildVersionName = self.buildVersion.currentText() if self.buildFromAssetCheckBox.isChecked() else None

        # align guide to geometry
        if self.guideCheckBox.isChecked() and self.alignToGeoCheckbox.isChecked():
            if not self.buildFromAssetCheckBox.isChecked():
                MessageHandling.alignToGeoFromAsset()
                return
            if self.buildAssetFolder.text() == self.loadedSettings['assetFolder']:
                MessageHandling.alignToGeoExternalAsset()
                return
            setupFilePath = Files.Config(self.projectFolder,
                                        self.assetFolder,
                                        version=versionName).assembleSetupFilePath()
            if not setupFilePath:
                MessageHandling.fileNotFound()
                return
            guidePivots = [x for x in currentSelection if Nodes.getNodeType(x) == Settings.guidePivotSuffix]
            alignGuides = guideGroups+guidePivots
            alignGeo = self.alignToGeoText.text()
            if not Nodes.exists(alignGeo):
                alignGeo = None
            if not alignGeo:
                if currentSelection:
                    alignGeo = currentSelection[-1]
                    if Nodes.getShapeType(alignGeo) != 'mesh':
                        alignGeo = None
                else:
                    alignGeo = None
            if not alignGuides or not alignGeo:
                MessageHandling.alignToGeoNoInputs()
                return
            # we create the reference here in order to support undo properly
            if os.path.isfile(setupFilePath) and not setupFilePath in mc.file(reference=True, q=True):
                try:
                    mc.file(setupFilePath, r=True, mergeNamespacesOnClash=True, namespace='guideAlign', gl=True, options='v=0;')
                except:
                    pass
            [mc.hide(x) for x in mc.ls(assemblies=True) if mc.referenceQuery(x, isNodeReferenced=True) and 'guideAlign' in x]
            AlignGuide.alignGuideToGeo(alignGuides, alignGeo)
            return

        # continuing build
        if not createFromBuildAsset:
            if not MessageHandling.multipleNodes(len(allGuideGroups)):
                return

        if self.buildSideNone.isChecked():
            buildSide = None
        if self.buildSideLeft.isChecked():
            buildSide = Settings.leftSide
        if self.buildSideRight.isChecked():
            buildSide = Settings.rightSide
            
        if (not mc.objExists('%s.namingConvention'%Settings.guideRoot) or createFromBuildAsset) and self.guideCheckBox.isChecked():
            # if no guide is in scene, we are looking for a gde file in the asset
            guideFile, incomingGuideGroups = DataStructure.Asset(assetFolder=self.assetFolder, 
                                                            versionName=buildVersionName).guideSettings(copyGuide=True, fromAsset=self.buildFromAssetCheckBox.isChecked())
            if guideFile in mc.file(reference=True, q=True):
                if self.loadedSettings['removeReference']:
                    mc.file(guideFile, removeReference=True)
            if mc.objExists(Settings.guideRoot):
                if createFromBuildAsset:
                    guideGroups = incomingGuideGroups
                else:
                    guideGroups.extend(mc.listRelatives(Settings.guideRoot, children=True, type='transform'))
        
        if guideGroups == []:
            if self.guideSettingsCheckBox.isChecked():
                # per guide control loading
                nodes = [x for x in mc.ls(sl=True) if Nodes.getNodeType(x) == Settings.guidePivotSuffix or Nodes.getNodeType(x) == Settings.guideShapeSuffix]
                guideFile = DataStructure.Asset(assetFolder=self.assetFolder,
                                                versionName=buildVersionName).guideSettings(guideGroup=None,
                                                                                            nodeList=nodes,
                                                                                            alignGuideGroupSettings=self.guideDefinitionCheckBox.isChecked(),
                                                                                            alignPivotPosition=self.guidePositionCheckBox.isChecked(),
                                                                                            alignPivotRotation=self.guideOrientationCheckBox.isChecked(),
                                                                                            alignShapeSettings=self.guideShapeSettingsCheckBox.isChecked(),
                                                                                            alignShapeTransforms=self.guideShapeTransformsCheckBox.isChecked())
                if guideFile in mc.file(reference=True, q=True):
                    if self.loadedSettings['removeReference']:
                        mc.file(guideFile, removeReference=True)
                mc.select(nodes)
        
        if not self.buildFromAssetCheckBox.isChecked():
            print('\n\nStarting BEAR Build')

        for buildStep in buildSteps:
            if buildStep == 'guide':
                mc.scriptEditorInfo(suppressInfo=True)
            if buildStep == 'rig':
                for rigGroup in Nodes.getAllChildren(Settings.rigRoot, nodeType=Settings.rigGroup):
                    if mc.objExists('%s.componentType'%rigGroup):
                        if mc.getAttr('%s.componentType'%rigGroup) == 'Skeleton' and Nodes.replaceNodeType(rigGroup, 'guide') in guideGroups:
                            if MessageHandling.querySkeletonRemoval():
                                mc.delete(rigGroup)
                            else:
                                return
            compGroups = list()
            output = None
            if guideGroups == None:
                guideGroups = []
            
            for guideGroup in guideGroups:
                if not mc.objExists(guideGroup+'.readyForRigBuild'):
                    continue
                side = buildSide if not self.buildSideNone.isChecked() \
                                    and self.guideCheckBox.isChecked() \
                                    and 'side' in mc.listAttr(guideGroup, userDefined=True) \
                                        else Nodes.getSide(guideGroup)
                if buildStep == 'rig':
                    if not mc.getAttr(guideGroup+'.readyForRigBuild'):
                        MessageHandling.emptyGuide(guideGroup)
                        continue
                    if Nodes.getComponentType(guideGroup) == 'Collection':
                        for subGroup in mc.listRelatives(guideGroup, children=True):
                            if not mc.getAttr(subGroup+'.readyForRigBuild'):
                                MessageHandling.emptyGuide(subGroup)
                                break
                    # special check for quadruped neck and hasNeck enabled at the same time
                    if 'neck' in mc.listAttr(guideGroup, userDefined=True):
                        if mc.getAttr('%s.neck'%guideGroup) == 'True' and Nodes.getComponentType(guideGroup) == 'Quadruped':
                            for subGroup in mc.listRelatives(guideGroup, children=True):
                                if 'hasNeck' in mc.listAttr(subGroup, userDefined=True):
                                    if mc.getAttr('%s.hasNeck'%subGroup) == 'True':
                                        mc.setAttr('%s.hasNeck'%subGroup, 'False', type='string')
                                        MessageHandling.quadrupedNeckBuild()

                output = Component.Build(side=side,
                                            buildStep=buildStep, 
                                            versionName=buildVersionName,
                                            assetFolder=self.assetFolder,
                                            alignGuideGroupSettings=self.guideDefinitionCheckBox.isChecked(),
                                            alignGuidePositions=self.guidePositionCheckBox.isChecked(),
                                            alignGuideOrientations=self.guideOrientationCheckBox.isChecked(),
                                            alignGuideShapeSettings=self.guideShapeSettingsCheckBox.isChecked(),
                                            alignGuideShapeTransforms=self.guideShapeTransformsCheckBox.isChecked(),
                                            removeRef=self.loadedSettings['removeReference']).createByCompGroup(guideGroup)
                
                if output != None:
                    if buildStep == 'guide':
                        compGroups.append(output)
                        if self.loadedSettings['hideRigAfterGuideBuild']:
                            if mc.objExists(Settings.rigRoot):
                                mc.hide(Settings.rigRoot)
                        if self.loadedSettings['showGuideAfterGuideBuild']:
                            mc.showHidden(Settings.guideRoot)
                    if buildStep == 'rig':
                        compGroups.append(output['rigGroup'])
                        for controlNode in mc.ls('*_'+Settings.controlSuffix, type='transform'):
                            if mc.objExists('%s.missingGuideControl'%controlNode):
                                MessageHandling.missingGuideControls()
                                break
                        if self.loadedSettings['hideGuideAfterRigBuild']:
                            if mc.objExists(Settings.guideRoot):
                                mc.hide(Settings.guideRoot)
                        if self.loadedSettings['showRigAfterRigBuild']:
                            mc.showHidden(Settings.rigRoot)

            # reseting guide root global scale
            if buildStep == 'guide':
                if mc.objExists(Settings.guideRoot):
                    mc.setAttr('%s.globalScale'%Settings.guideRoot, lock=False)
                    mc.setAttr('%s.globalScale'%Settings.guideRoot, 1)

            if buildStep == 'guideSettings':                                                                                                     
                if self.loadedSettings['removeReference'] and output:
                    mc.file(output, removeReference=True)

            if compGroups != []:
                mc.select(compGroups)

            Component.customScript(buildStep, 
                                   modelEnabled=self.modelCheckBox.isChecked(),
                                   guideEnabled=self.guideCheckBox.isChecked(),
                                   rigEnabled=self.rigCheckBox.isChecked())
            

            if buildStep == 'rigSettings':                                                                                                     
                nodes = [x for x in mc.ls(sl=True) if Nodes.getNodeType(x) == Settings.controlSuffix]
                DataStructure.Asset(assetFolder=self.assetFolder,
                                    versionName=buildVersionName).rigSettings(selection=nodes if self.buildSelectSelected.isChecked() else None)

        if self.loadedSettings['autoShowGuideProperties']:
            self.guideSelection()

        if not self.buildFromAssetCheckBox.isChecked():
            print('\nBEAR Build completed\n')

    @UndoDec.undo
    def assemble(self):
        
        self.loadSettings()

        # folder and file checks

        self.assetFolder = self.assembleAssetFolder.text() if self.assembleFromAssetCheckBox.isChecked() else self.loadedSettings['assetFolder']

        if self.assembleFromAssetCheckBox.isChecked():
            versionName = self.assembleVersion.currentText()
        else:
            versionName = Files.Config(self.projectFolder,
                                            self.assetFolder).getVersion()
        
        if self.deformerCheckBox.isChecked() and self.assetFolder and not self.inputOrderCheckBox.isChecked():
            if not MessageHandling.fileExists(Files.Config(self.projectFolder,
                                                             self.assetFolder,
                                                             version=versionName,
                                                             fileType=Settings.deformFileIndicator).assembleFilePath(),
                                                Settings.deformFileIndicator):
                return
        
        # assembling

        buildSteps = list()
        if self.deformerCheckBox.isChecked():
            buildSteps.append('deform')
        if Settings.licenseVersion != 'free':
            if self.faceCorrectionsCheckBox.isChecked():
                buildSteps.append('faceCorrections')
            if self.poseCorrectionsCheckBox.isChecked():
                buildSteps.append('poseCorrections')
        if self.postDeformCheckBox.isChecked():
            buildSteps.append('postDeform')
            
        assembleVersionName = self.assembleVersion.currentText() if self.assembleFromAssetCheckBox.isChecked() else None

        print('\n\nStarting BEAR Deform\n')

        for buildStep in buildSteps:
            Assembly.Build(buildStep=buildStep, 
                            projectFolder=self.projectFolder,
                            assetFolder=self.assetFolder,
                            versionName=assembleVersionName,
                            skinNodes=mc.ls(sl=True) if self.assembleSelectSelected.isChecked() else [],
                            byUVs=self.uvs.isChecked(),
                            byVertexID=self.vertexID.isChecked(),
                            loadSkin=self.skinCheckBox.isChecked(),
                            loadLattice=self.latticeCheckBox.isChecked(),
                            loadSmooth=self.smoothCheckBox.isChecked(),
                            loadProxWrap=self.proximityWrapCheckBox.isChecked(),
                            loadGeometryConstraints=self.geometryConstraintsCheckBox.isChecked(),
                            loadInputOrder=self.inputOrderCheckBox.isChecked(),
                            removeRef=self.loadedSettings['removeReference']).skinning()

            Component.customScript(buildStep,
                                   postDeformEnabled=self.postDeformCheckBox.isChecked())

        print('\nBEAR Deform completed\n')