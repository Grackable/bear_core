# Files

'''
All methods for saving/loading files
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
from functools import partial
import sys, re, os, json, shutil
from bear.system import Settings
from bear.system import MessageHandling
from bear.system import Component
from bear.utilities import Nodes
from bear.utilities import Tools

saveCollectionDialogName = 'saveCollectionDialog'

def mayaMainWindow():
    
    app = QApplication
    if not app:
        app = QApplication(sys.argv)
    return next(w for w in app.topLevelWidgets() if w.objectName() == 'MayaWindow')
    
def getCollectionFolder():

    collectionFolder = Settings.getPath(['collections'])
    
    return collectionFolder

class SaveCollectionDialog(QDialog):

    def __init__(self, 
                 collectionGroup,
                parent=mayaMainWindow()):

        super(SaveCollectionDialog, self).__init__(parent)
        
        self.screenWidth, self.screenHeight = Settings.getScreenResolution()
        
        self.collectionGroup = collectionGroup
        self.component = Nodes.getComponent(collectionGroup)
        
        self.name = saveCollectionDialogName

        verticalLayout = QVBoxLayout()

        formLayout = QFormLayout()
        
        self.folderField = QLineEdit('/')
        self.fileNameField = QLineEdit(self.component[0].upper()+self.component[1:])

        formLayout.addRow('Folder:', self.folderField)
        formLayout.addRow('Name:', self.fileNameField)

        buttonLayout = QHBoxLayout()
        saveButton = QPushButton('Save')
        cancelButton = QPushButton('Cancel')
        saveButton.setFixedSize(self.screenWidth/35, self.screenWidth/80)
        cancelButton.setFixedSize(self.screenWidth/35, self.screenWidth/80)

        verticalLayout.addLayout(formLayout)
        verticalLayout.addLayout(buttonLayout)
        buttonLayout.addWidget(saveButton, alignment=Qt.AlignLeft)
        buttonLayout.addWidget(cancelButton, alignment=Qt.AlignRight)

        saveButton.clicked.connect(partial(self.confirm, self.folderField, self.fileNameField))
        cancelButton.clicked.connect(self.close)

        self.setLayout(verticalLayout)

        self.setMinimumWidth(self.screenWidth/15)
        self.setMinimumHeight(self.screenHeight/20)

        self.setWindowTitle('Save Collection...')
        self.setObjectName(self.name)

    def open(self):
        
        self.exec_()

    def confirm(self, folderField, fileNameField):

        if not self.isValidName(folderField.text().replace('/', '')) or not self.isValidName(fileNameField.text()):
            MessageHandling.invalidCharacter()
            return

        self.mayaFileType = '.ma'
        collectionFileName = fileNameField.text()+self.mayaFileType
        collectionFolder = getCollectionFolder()+folderField.text()
        if not os.path.isdir(collectionFolder):
            if MessageHandling.collectionFolderMissing():
                os.makedirs(collectionFolder)
        existingCollections = os.listdir(collectionFolder)
        if collectionFileName in existingCollections:
            if not MessageHandling.collectionOverwriteExisting():
                return
        self.save(self.collectionGroup, collectionFolder, collectionFileName)
        self.close()

    def save(self, collectionGroup, collectionFolder, collectionFileName):

        guideGroups = Nodes.getChildren(collectionGroup)

        mc.undoInfo(openChunk=True)

        for guideGroup in guideGroups:
            Nodes.delete(Nodes.getRelatedNodes(guideGroup))
            Nodes.delete(Nodes.getChildren(guideGroup))

        mc.file(collectionFolder+'/'+collectionFileName, 
                type='mayaBinary' if self.mayaFileType == '.mb' else 'mayaAscii', 
                exportSelected=True, 
                prompt=False, 
                force=True,
                shader=True,
                channels=False,
                constraints=False,
                ch=False,
                expressions=False)
        
        mc.undoInfo(closeChunk=True)
        mc.undo()

    def isValidName(self, name):

        if not re.match("^[a-zA-Z0-9]*$", name):
            return False
        return True
    
    def close(self):
        
        if mc.window(self.name, exists=True):
            mc.deleteUI(self.name, window=True)

def createVersionName(versionNaming, number):
        
    v = versionNaming.replace('*', '')
    indexCount = len([i for i, k in enumerate(versionNaming) if k == '*'])
    num_str = "{:0{}d}".format(number, indexCount)
    return v+num_str
    
def getNextVersion(versionNaming, version):

    number = ''
    versionList = [x for x in version if x.isdigit()]
    for i in range(len(versionList)):
        number += versionList[i]
    nextVersion = createVersionName(versionNaming, int(number)+1)
    
    return nextVersion
    
class Config(object):
    def __init__(self,
                 projectFolder,
                 assetFolder,
                 fileType=None, 
                 version=None,
                 querySave=True, 
                 saveAll=False,
                 selection=None):

        self.projectFolder = projectFolder
        self.assetFolder = assetFolder
        self.loadedSettings = Settings.loadSettings()[0]
        numAssetNameTokens = self.loadedSettings['numParentFolders']
        parentFolders = self.assetFolder[1:].split('/')[:-1]
        numParentFolders = len(parentFolders)
        if numAssetNameTokens > numParentFolders:
            numAssetNameTokens = numParentFolders
        self.assetName = '_'.join(self.assetFolder[1:].split('/')[numParentFolders-numAssetNameTokens:])
        self.fileType = fileType
        self.version = version
        self.querySave = querySave
        self.saveAll = saveAll
        self.selection = selection
        if fileType:
            self.typeFolder = '' if fileType == 'delivery' else '/'+fileType
        self.mayaFileType = self.loadedSettings['mayaFileType']
        self.versionNaming = self.loadedSettings['versionNaming']
        self.fileSuffix = '.mb' if self.mayaFileType == 'mayaBinary' else '.ma'
        if fileType == Settings.rigSettingsFileIndicator or fileType == Settings.controlTransformsFileIndicator:
            self.fileSuffix = '.json'
        userSettings = json.load(open(Settings.getUserFile()))
        if not assetFolder:
            self.assetFolder = userSettings['assetFolder']
        if not projectFolder:
            self.projectFolder = userSettings['projectFolder']
        
    def assembleVersionPath(self):
        if not self.version:
            return
        assembledPath = self.projectFolder+\
            self.assetFolder+\
                '/'+self.version
        return assembledPath
        
    def assembleFilePath(self):
        if not self.version:
            return
        assembledPath = self.projectFolder+\
            self.assetFolder+\
                '/'+self.version+\
                    self.typeFolder+\
                        '/'+self.assetName+'_'+self.fileType+self.fileSuffix
        return assembledPath
        
    def assembleSetupFilePath(self):
        if not self.version:
            return
        assembledPath = self.projectFolder+\
            self.assetFolder+\
                '/'+self.version+\
                    '/'+self.assetName+'_'+Settings.setupFileIndicator+self.fileSuffix
        return assembledPath
        
    def assembleFolderPath(self):
        if not self.version:
            self.version = createVersionName(self.versionNaming, 1)
        assembledPath = self.projectFolder+\
            self.assetFolder+\
                '/'+self.version+\
                    self.typeFolder
        return assembledPath
        
    def assembleAssetFolderPath(self):
        assembledPath = self.projectFolder+self.assetFolder
        return assembledPath
    
    def versionUp(self, folderPath):
        newFolderPath = self.assembleFolderPath()
        shutil.copytree(folderPath, newFolderPath)

    def getVersion(self):
        assetFolder = self.assembleAssetFolderPath()
        if assetFolder == self.projectFolder:
            return
        if not os.path.isdir(assetFolder):
            return
        if os.listdir(assetFolder) == []:
            return
        versionFolder = max(os.listdir(assetFolder))
        if not versionFolder:
            versionFolder = createVersionName(self.versionNaming, 1)
        return versionFolder

    def getTokens(self, filePath=None):
        if filePath:
            curFilePath = filePath
        else:
            curFilePath = mc.file(location=True, q=True)
        if curFilePath == 'unknown':
            if self.fileType:
                curFileName = self.assetFolder+'_'+self.fileType+self.fileSuffix
            else:
                curFileName = None
            curAssetFolder = self.assetFolder
            curFileType = self.fileType
            curVersion = createVersionName(self.versionNaming, 1)
        else:
            curFolders = curFilePath.split('/')
            curFileName = curFolders[-1]
            if curFileName.split('_')[-1].split('.')[0] == Settings.setupFileIndicator:
                curIsSetupFile = True
                i = 0
            else:
                curIsSetupFile = False
                i = -1
            projectTokens = len(self.projectFolder.split('/'))
            curAssetFolder = '/'+'/'.join(curFolders[projectTokens:-2+i])
            curVersion = curFolders[-2+i]
            curFileType = Settings.setupFileIndicator if curIsSetupFile else curFolders[-1+i]
        if self.fileType == Settings.setupFileIndicator or not self.fileType:
            self.typeFolder = Settings.setupSubFolder
        else:
            self.typeFolder = '' if self.fileType == 'delivery' else '/'+self.fileType
        self.version = curVersion

        return {
            'projectFolder': self.projectFolder,
            'assetFolder': curAssetFolder,
            'fileName': curFileName,
            'fileType': curFileType,
            'version': curVersion,
            'filePath': curFilePath,
            }
    
    def saveControlTransforms(self, targetFolderPath, bySelection=False):
            
        if not os.path.isdir(targetFolderPath):
            os.mkdir(targetFolderPath)

        if not mc.objExists(Settings.rigGroup):
            return
        
        if bySelection:
            controlNodes = [
                x for x in mc.ls(sl=True) \
                if Nodes.getNodeType(x) in [Settings.controlSuffix]
                ]
        else:
            controlNodes = [
                x for x in Nodes.getAllChildren(Settings.rigGroup) \
                if Nodes.getNodeType(x) in [Settings.controlSuffix]
                and not mc.referenceQuery(x, isNodeReferenced=True)
                ]
        
        for controlNode in controlNodes:
            if not Nodes.getAttr('%s.postDeformAlignment'%controlNode):
                continue
            trsVal = Nodes.getTransformValues(controlNode, includeOffsetParentMatrix=True)
            if not trsVal:
                continue

            controlTransformsFilePath = targetFolderPath+'/'+controlNode+'.json'
            fileObj = open(controlTransformsFilePath, 'w')
            json.dump(trsVal, fileObj, indent=4)
            fileObj.close()

        return True

    def loadControlTransforms(self, sourceFolderPath, bySelection=False):

        if not os.path.isdir(sourceFolderPath):
            return
        
        if bySelection:
            controlNodes = [
                x for x in mc.ls(sl=True) \
                if Nodes.getNodeType(x) in [Settings.controlSuffix]
                ]
            
        settingsFiles = [x for x in os.listdir(sourceFolderPath) if x.endswith('.json')]
        
        for settingsFile in settingsFiles:
            controlNode = settingsFile.split('.')[0]
            controlSettingsFilePath = sourceFolderPath+'/'+settingsFile
            fileObj = open(controlSettingsFilePath, 'r')
            trsVal = json.load(fileObj)
            fileObj.close()

            if not Nodes.exists(controlNode):
                continue
            
            Nodes.setOffsetParentMatrix(controlNode)
            Nodes.setTrs(controlNode, trsVal=trsVal)
            Nodes.setOffsetParentMatrix(controlNode, matrix=Nodes.getMatrix(controlNode, includeOffsetParentMatrix=True))
            Nodes.setTrs(controlNode)

    def saveRigSettings(self, targetFolderPath):

        if not mc.objExists(Settings.rigRoot):
            return

        if not os.path.isdir(targetFolderPath):
            os.mkdir(targetFolderPath)

        for controlNode in Nodes.getAllChildren(Settings.rigRoot, nodeType=Settings.controlSuffix):
            settings = dict()
            attrNames = mc.listAttr(controlNode, userDefined=True)
            if attrNames:
                for attrName in attrNames:
                    if attrName == 'namingConvention' or attrName == 'postDeformAlignment':
                        continue
                    attr = '%s.%s'%(controlNode, attrName)
                    if mc.getAttr(attr, lock=True):
                        continue
                    attrVal = mc.getAttr(attr)
                    if type(attrVal) == bool:
                        attrVal = int(attrVal)
                    settings[attr] = attrVal
            if not settings:
                continue
            targetFilePath = targetFolderPath+'/'+controlNode+'.json'
            fileObj = open(targetFilePath, 'w')
            json.dump(settings, fileObj, indent=4)
            fileObj.close()

        print('Rig settings saved.')

    def loadRigSettings(self, sourceFolderPath):
        
        if not os.path.isdir(sourceFolderPath):
            return
            
        settingsFiles = [x for x in os.listdir(sourceFolderPath) if x.endswith('.json')]
        
        for settingsFile in settingsFiles:

            fileObj = open(sourceFolderPath+'/'+settingsFile, 'r')
            settings = json.load(fileObj)
            fileObj.close()

            for attr in settings:
                attrVal = settings[attr]
                attrNode, attrName = attr.split('.')
                if self.selection != None:
                    if not attrNode in self.selection:
                        continue
                Nodes.setAttr(f'{attrNode}.{attrName}', attrVal)

        if settingsFiles:
            print('Rig settings loaded.')

    def saveInputOrder(self, targetFolderPath):

        if not os.path.isdir(targetFolderPath):
            os.mkdir(targetFolderPath)

        nodes = [x for x in mc.ls(type='transform') if Nodes.getShapeType(x) == 'mesh' and not ":" in x]
            
        inputsSaved = list()
        for node in nodes:
            inputNodes = list()
            inputs = mc.listHistory(node, gl=True, pdo=True)
            if not inputs:
                continue
            for inputNode in inputs:
                if mc.objectType(inputNode) == 'tweak':
                    break
                inputNodes.append(inputNode)

            inputNodes = inputNodes[::-1]
            if len(inputNodes) < 2:
                continue
            inputsSaved.append(node)

            inputOrderFilePath = f"{targetFolderPath}/{node}_inputOrder.json"
            fileObj = open(inputOrderFilePath, 'w')
            json.dump(inputNodes, fileObj)
            fileObj.close()

        print('Input order saved.')
    
    def loadInputOrder(self, sourceFolderPath):

        if not os.path.isdir(sourceFolderPath):
            return
        
        inputOrderFiles = [x for x in os.listdir(sourceFolderPath) if x.endswith('.json')]

        for inputOrderFile in inputOrderFiles:

            fileObj = open(sourceFolderPath+'/'+inputOrderFile, 'r')
            inputNodes = json.load(fileObj)
            fileObj.close()

            node = inputOrderFile.replace('_inputOrder.json', '')

            if not Nodes.exists(node):
                continue
            existingInputs = mc.listHistory(node, gl=True, pdo=True)
            if not existingInputs:
                continue
            if len(existingInputs) == 1:
                continue
            existingInputs = existingInputs[::-1]
            for i, inputNode in enumerate(inputNodes):
                if i > len(inputNodes)-2:
                    continue
                if not inputNodes[i+1] in existingInputs:
                    continue
                if not inputNode in existingInputs:
                    continue
                if existingInputs.index(inputNode) == i:
                    continue
                try:
                    mc.reorderDeformers(inputNodes[i+1], inputNode, node)
                except:
                    pass

        if inputOrderFiles:
            print('Input order loaded.')

    def save(self):
        # file token assembly
        tokens = self.getTokens()
        curFileType = tokens['fileType']
        curProjectFolder = tokens['projectFolder']
        curAssetFolder = tokens['assetFolder']
        curVersion = tokens['version']
        curFilePath = tokens['filePath']
        
        # data assembly
        curSelection = mc.ls(sl=True)
        nodes = []
        parents = []
        ignoreNodes = []
        ignoreParents = []
        saveDependencies = True
        directSave = False
        
        self.version = self.getVersion()
        assembledFilePath = self.assembleFilePath()
        
        if self.projectFolder in mc.file(location=True, q=True):
            foreignFile = False
        else:
            curAssetFolder = None
            foreignFile = True
            
        # file checks
        if self.querySave:
            doConfirm = False
            if curFileType == Settings.setupFileIndicator:
                if self.fileType == Settings.modelFileIndicator:
                    doConfirm = True
            else:
                if (self.fileType == Settings.modelFileIndicator and curFileType != Settings.modelFileIndicator) or \
                    (self.fileType == Settings.guideFileIndicator and curFileType != Settings.guideFileIndicator) or \
                    (self.fileType == Settings.deformFileIndicator and curFileType != Settings.deformFileIndicator) or \
                    (self.fileType == Settings.blendshapesFileIndicator and curFileType != Settings.blendshapesFileIndicator) or \
                    (self.fileType == Settings.deliveryFileIndicator and curFileType != Settings.deliveryFileIndicator):
                    doConfirm = True

            if doConfirm and not foreignFile:
                if not MessageHandling.confirmFileType(curFileType, self.fileType):
                    return

            if curProjectFolder != self.projectFolder and not foreignFile:
                if not MessageHandling.queryNewAsset('project', curProjectFolder, self.projectFolder):
                    return
                
            if curProjectFolder == self.projectFolder and curAssetFolder != self.assetFolder:
                if not MessageHandling.queryNewAsset('asset', curAssetFolder, self.assetFolder):
                    return
            
            if assembledFilePath:
                if not os.path.isfile(assembledFilePath) and self.fileType == Settings.setupFileIndicator:
                    if not MessageHandling.queryNewSetupFile(assembledFilePath):
                        return
                # overwrite
                instruction = MessageHandling.queryNewVersionOverwrite(assembledFilePath, self.assetFolder, self.version, self.fileType, self.saveAll)
            else:
                instruction = True
        else:
            instruction = True
        if instruction == 'newVersion':
            curFolderPath = self.assembleFolderPath()
            latestVersion = self.getVersion()
            self.version = getNextVersion(self.versionNaming, latestVersion)
            self.versionUp(curFolderPath)
            newFolderPath = self.assembleFolderPath()
            mc.file(curFilePath, rename=self.assembleSetupFilePath())
            # update reference pathes
            for refFile in mc.file(reference=True, q=True):
                if curFolderPath in mc.referenceQuery(refFile, filename=True):
                    refNode = mc.referenceQuery(refFile, referenceNode=True)
                    newRefFile = refFile.replace(curFolderPath, newFolderPath)
                    mc.file(newRefFile, loadReference=refNode, type=self.mayaFileType, options="v=0;")
        elif instruction != False:
            pass
        else:
            return
        
        # create version folder
        folderPath = self.assembleFolderPath()
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)
        
        # save instructions
        selectedSave = True
        if self.fileType == Settings.setupFileIndicator:
            targetFilePath = self.assembleSetupFilePath()
            selectedSave = False
            directSave = True
        else:
            targetFilePath = self.assembleFilePath()
        if self.fileType == Settings.modelFileIndicator:
            selectedSave = False
            directSave = True
        if self.fileType == Settings.guideFileIndicator:
            nodes = mc.ls(Settings.guideRoot)
            parents = [Nodes.getParent(x) for x in nodes]
            [Nodes.setParent(x, 'world') for x in nodes]
        if self.fileType == Settings.rigSettingsFileIndicator:
            self.fileSuffix = '.json'
            targetFolderPath = self.assembleFolderPath()
            self.saveRigSettings(targetFolderPath)
            return
        if self.fileType == Settings.inputOrderFileIndicator:
            self.fileSuffix = '.json'
            targetFolderPath = self.assembleFolderPath()
            self.saveInputOrder(targetFolderPath)
            return
        if self.fileType == Settings.controlTransformsFileIndicator:
            self.fileSuffix = '.json'
            targetFolderPath = self.assembleFolderPath()
            self.saveControlTransforms(targetFolderPath)
            return
        if self.fileType == Settings.deformFileIndicator:
            nodes = mc.ls(Settings.rigRoot, Settings.geometryGroup)
            parents = [Nodes.getParent(x) for x in nodes]
            [Nodes.setParent(x, 'world') for x in nodes]
            ignoreNodes = mc.ls(Settings.guideRoot)
            ignoreParents = [Nodes.getParent(x) for x in ignoreNodes]
            [Nodes.setParent(x, 'world') for x in ignoreNodes]
        if self.fileType == Settings.blendshapesFileIndicator:
            nodes = mc.ls(Settings.poseCorrectionsGroup)
        if self.fileType == Settings.deliveryFileIndicator:
            selectedSave = False
            directSave = True
            Tools.deleteComponents()
            Nodes.delete([Settings.templateGroup, Settings.skinMeshesGroup, Settings.poseCorrectionsGroup])
            Component.customScript(buildStep='delivery', forceRun=True)
        
        # perform saving
        folderPath = self.assembleFolderPath()
        if not os.path.isdir(folderPath):
            os.mkdir(folderPath)

        if selectedSave and not nodes:
            MessageHandling.noTypeFound(self.fileType)
            return True
        
        if nodes:
            mc.select(nodes)
        if directSave:
            if targetFilePath:
                mc.file(rename=targetFilePath)
            mc.file(force=True, save=True, options="v=0;")
        else:
            mc.file(targetFilePath, 
                    type=self.mayaFileType, 
                    exportSelected=True, 
                    prompt=False, 
                    force=True,
                    shader=True,
                    channels=saveDependencies,
                    constraints=saveDependencies,
                    ch=saveDependencies,
                    expressions=saveDependencies)

        # remove reference to make sure reference will not be outdated
        if targetFilePath in mc.file(reference=True, q=True):
            mc.file(targetFilePath, removeReference=True)
            
        [Nodes.setParent(x, parent) for x, parent in zip(nodes, parents)]
        [Nodes.setParent(x, parent) for x, parent in zip(ignoreNodes, ignoreParents)]
        mc.select(curSelection)

        return True

    def open(self):

        if not self.projectFolder:
            MessageHandling.noProjectFolderFound()
            return
        self.getTokens()
        self.version = self.getVersion()
        if self.version:
            folderPath = self.assembleVersionPath()
        else:
            folderPath = self.assembleAssetFolderPath()
        targetFilePath = mc.fileDialog2(
                        fileMode=1, 
                        caption='Open File', 
                        dialogStyle=1, 
                        startingDirectory=folderPath)
        
        if targetFilePath:
            try:
                mc.file(targetFilePath, o=True, f=True, ignoreVersion=True, options="v=0;p=17;f=0")
            except:
                pass
            tokens = self.getTokens(targetFilePath[0])
            newAssetFolder = tokens['assetFolder']
            newProjectFolder = tokens['projectFolder']
            if self.assetFolder != newAssetFolder:
                if MessageHandling.confirmAssetSwitch(self.assetFolder, newAssetFolder, 'asset'):
                    return newProjectFolder, newAssetFolder