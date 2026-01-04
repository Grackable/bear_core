# Message Handling

import maya.cmds as mc
if mc.about(v=True) < '2025':
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
else:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
import sys, os
from functools import partial
import configparser, datetime
try: # catching here for install process
    from bear.system import Settings
except:
    pass

def mayaMainWindow():
    
    app = QApplication
    if not app:
        app = QApplication(sys.argv)
    return next(w for w in app.topLevelWidgets() if w.objectName() == 'MayaWindow')

def warning(text):
    
    mc.scriptEditorInfo(suppressInfo=False, suppressWarnings=False, suppressResults=False, suppressErrors=False)
    mc.warning(text)

class InfoPopUp(QDialog):

    def __init__(self, messageText, hyperlink=None, parent=mayaMainWindow()):
        super(InfoPopUp, self).__init__(parent)

        self.setWindowTitle('BEAR Trial')
        self.resize(300, 150)

        main_layout = QVBoxLayout(self)

        text_label = QLabel(messageText)
        text_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(text_label)

        if hyperlink:
            hyperlink_label = QLabel()
            hyperlink_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            hyperlink_label.setOpenExternalLinks(True)
            hyperlink_label.setText(hyperlink)
            hyperlink_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(hyperlink_label)

        button_layout = QHBoxLayout()

        ok_button = QPushButton('OK')
        ok_button.setMaximumSize(70, 30)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        main_layout.addLayout(button_layout)

    def open(self):
        """Return True if OK pressed, False if rejected."""
        result = self.exec()  # Qt6-safe
        return result == QDialog.Accepted
    
class PopUpMessage(QMessageBox):

    def __init__(
        self,
        messageText,
        query=False,
        versionCheck=False,
        okAbort=False,
        yesNo=False,
        parent=mayaMainWindow()
    ):
        super().__init__(parent)

        self.setText(messageText)
        self.setWindowTitle('BEAR Builder')

        self._buttons = {}

        if query:
            self.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            self.setDefaultButton(QMessageBox.Yes)

        elif versionCheck:
            self._buttons['new'] = self.addButton(
                'Save New Version', QMessageBox.ActionRole
            )
            self._buttons['overwrite'] = self.addButton(
                'Overwrite', QMessageBox.ActionRole
            )
            self._buttons['cancel'] = self.addButton(
                'Cancel', QMessageBox.RejectRole
            )

        elif okAbort:
            self._buttons['ok'] = self.addButton(
                'OK', QMessageBox.AcceptRole
            )
            self._buttons['cancel'] = self.addButton(
                'Cancel', QMessageBox.RejectRole
            )

        elif yesNo:
            self._buttons['yes'] = self.addButton(
                'Yes', QMessageBox.AcceptRole
            )
            self._buttons['no'] = self.addButton(
                'No', QMessageBox.RejectRole
            )

        else:
            self.setStandardButtons(QMessageBox.Ok)

    def open(self):
        result = self.exec()

        # Standard buttons path
        if not self._buttons:
            return result

        # Custom buttons path
        clicked = self.clickedButton()
        for key, btn in self._buttons.items():
            if btn is clicked:
                return key

        return None
        
def noNodeDefined(componentName, tag='geo'):

    messageText = '%s: No %s defined, building aborted. A %s input is required.' % (componentName, tag, tag)
    PopUpMessage(messageText).open()

def noTypeFound(fileType):

    messageText = 'No %s found in the current scene.'%fileType
    PopUpMessage(messageText).open()

def noGuide():

    messageText = 'No guide found. Please check if your specified folder is correct and the asset exists.'
    PopUpMessage(messageText).open()

def noJointGuides():

    messageText = 'No joing guides found. Make sure to check the joint guides option in the component guide settings and rebuild the guide.'
    PopUpMessage(messageText).open()

def missingGuideControls():

    messageText = 'Missing guide controls. Make sure to rebuild the guide before rig build when you make guide definition changes.\n\n' + \
                    'See the script editor for details.'
    PopUpMessage(messageText).open()

def noControls():

    messageText = 'No controls found.'
    PopUpMessage(messageText).open()

def noBlendshapes():

    messageText = 'No blendshapes in scene, saving blendshapes skipped.'
    PopUpMessage(messageText).open()

def noBlendshapesComponent():

    messageText = 'No blendshapes component found. Please create a BlendshapesConfig component and try again.'
    PopUpMessage(messageText).open()

def onlySameComponentType():

    messageText = 'You can only edit multiple guide components of the same type.'
    PopUpMessage(messageText).open()

def hierarchyScaling():

    messageText = 'Global Scale adjustments on multiple levels in the hierarchy is not supported.\n' + \
                'You can scale multiple components or collection on the same hierarchy level only. Building aborted.'
    PopUpMessage(messageText).open()

def noAsset():
    messageText = "No asset group found. Would you like to continue saving the file as is?"
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def emptyGuide(guideGroup):

    messageText = 'Component is not ready for rig build: %s\n\n' % guideGroup \
                + 'Build the guide first and try again.'
    PopUpMessage(messageText).open()

def hasGuide(guideNode, name=None):

    if not mc.objExists(guideNode):
        if name == None:
            messageText = 'No guide found.'
        else:
            messageText = "No guide with the name '%s' found." % name
        PopUpMessage(messageText).open()
        return False
    else:
        return True

def hasNodesToSave(nodes, keyword):
    
    messageText = 'No {0} found, {0} saving aborted.'.format(keyword)
    if nodes == [] or nodes == None:
        PopUpMessage(messageText).open()
        return False
    else:
        return True

def unableToSaveFile(reason):

    if reason == 'unknown':
        messageText = "Saving aborted. Save your scene first in any folder or according to the conventions in Settings."
    if reason == 'invalidPath':
        messageText = "Invalid path, saving aborted. Please check your folder conventions in Settings."
    if reason == 'notLatestRigFile':
        messageText = "Current rig file is not the latest, saving aborted. You can only save from the latest rig file."
    if reason == 'setupNotOpened':
        messageText = "Setup can only be saved from the setup file."
    if reason == 'modelNotOpened':
        messageText = "Model can only be saved from the model file."
    if reason == 'guide':
        messageText = "Guide can only be saved from the guide or setup file."
    if reason == 'deform':
        messageText = "Deform can only be saved from the deform or setup file."
    if reason == 'rigSettings':
        messageText = "Rig Settings can only be saved from the rig settings or setup file."
    if reason == 'blendshapes':
        messageText = "Blendshapes can only be saved from the blendshapes or setup file."
    if reason == 'delivery':
        messageText = "Delivery can only be saved from the delivery or setup file."
    if reason == 'noGuideFound':
        messageText = "No guide found, saving aborted."
    if reason == 'noRigSettingsFound':
        messageText = "No rig found, saving aborted."
    if reason == 'noSkinFound':
        messageText = "No skin found, saving aborted."
    if reason == 'noBlendshapesFound':
        messageText = "No blendshapes found, saving aborted."
    if reason == 'noAnimRigFound':
        messageText = "No rig found, saving aborted."
        
    PopUpMessage(messageText).open()

def outdatedVersion():

    messageText = "Current file is not the latest or you are on a different asset. Continue?"
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def confirmFileType(curFileType, fileType):
    if fileType == 'delivery':
        messageText = (
            'Delivery save will remove the guide and clean up the scene.\n\n'
            'This action cannot be undone. Would you like to proceed?'
        )
    else:
        messageText = f"You are about to save {fileType} from the {curFileType} file. Would you like to proceed?"

    # Ask the user
    output = PopUpMessage(messageText, yesNo=True).open()

    # Return True if user clicked Yes, False otherwise
    return output == "yes"
    
def queryNewAsset(folderType, currentAssetFolder, newAssetFolder):

    if currentAssetFolder:
        messageText = 'You are about to save a different %s than the current. Would you like to proceed?\n\n'%folderType \
                    + 'Current %s folder: %s\n'%(folderType.capitalize(), currentAssetFolder) \
                    + 'New %s folder:      %s'%(folderType.capitalize(), newAssetFolder)
    else:
        messageText = 'You are about to save to the following asset folder. Would you like to proceed?\n\n' \
                    + '%s folder: %s'%(folderType.capitalize(), newAssetFolder)
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def queryNewSetupFile(filePath):
    messageText = f"The following setup file will be created:\n\n{filePath}"
    output = PopUpMessage(messageText, okAbort=True).open()
    return output == "ok"

def queryNewVersionOverwrite(filePath, assetName, versionName, keyword, saveAll):

    if not os.path.isfile(filePath):
        return True

    if saveAll:
        messageText = (
            f"{assetName} {versionName} already exists.\n"
            "How would you like to proceed?"
        )
    else:
        messageText = (
            f"{assetName} {keyword} file {versionName} already exists.\n"
            "How would you like to proceed?"
        )

    result = PopUpMessage(messageText, versionCheck=True).open()

    if result in ('new', 'overwrite'):
        return result

    return False

def queryFolderCreation(filePath, name):
    
    messageText = "The specified %s folder does not exist. It will be created if you proceed.\n\n%s" % (name, filePath)
    output = PopUpMessage(messageText, okAbort=True).open()
    return output == "ok"

def folderCreationFailed(folderPath):

    messageText = 'Folder creation failed. Please check if your drive exists:\n\n%s'%folderPath
    PopUpMessage(messageText).open()

def alignToGeoFromAsset():

    messageText = "Align to Geometry requires an external asset which has a geometry and guide in place. Please enable From Asset."
    PopUpMessage(messageText).open()

def alignToGeoExternalAsset():

    messageText = "Align to Geometry requires an external asset. Please specify a different asset than the current."
    PopUpMessage(messageText).open()

def alignToGeoNoInputs():

    messageText = "Align to Geometry is enabled.\n\n" \
                + "With Selected Components chosen, Align to Geometry requires a selection of guide groups or guide pivots as well as the geometry at the end of the selection.\n\n" \
                + "With All Components chosen, select the geometry only."
    PopUpMessage(messageText).open()

def noComponent():

    messageText = 'No component found.'
    PopUpMessage(messageText).open()

def nothingSelected():

    messageText = 'Nothing selected.'
    PopUpMessage(messageText).open()

def noComponentGroupSelected():

    messageText = 'No component group selected.'
    PopUpMessage(messageText).open()

def noSelectedNode():

    messageText = 'Nothing selected, aborted.'
    PopUpMessage(messageText).open()

def noComponentSelected():

    messageText = 'Selected node is not a component or no components in scene.'
    PopUpMessage(messageText).open()

def noSelectedComponent(node):

    messageText = 'Selected node is not a component or guide is missing, aborted: %s' % node
    PopUpMessage(messageText).open()

def insufficientGuideInputs():

    messageText = 'Insufficient guide inputs. Please check your guide settings. Building aborted.'
    PopUpMessage(messageText).open()

def multipleNodes(count, nameTag='components', taskTag='built'):
    if count > 1:
        messageText = f"{count} {nameTag} will be {taskTag}. Continue?"
        output = PopUpMessage(messageText, query=True).open()
        return output == "yes"
    else:
        return True

def noCompGroup(compGroup):

    messageText = 'Component group not found: %s.\nData may not have loaded correctly.'%compGroup
    PopUpMessage(messageText).open()

def querySkeletonRemoval():
    messageText = (
        "There is an existing Skeleton rig component. "
        "Rebuilding a rig component will delete this Skeleton rig component. "
        "Be aware that skin data might get lost. Would you like to proceed?"
    )
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def noPoseMirrorFound():

    messageText = 'No pose mirror found on selected set.'
    PopUpMessage(messageText).open()

def folderExists(folderPath):

    if os.path.isdir(folderPath) or folderPath == '':
        return True
    else:
        messageText = 'Folder does not exist:\n\n%s' % folderPath
        PopUpMessage(messageText).open()
        return False

def fileExists(filePath, fileType='this'):

    if os.path.isfile(filePath):
        return True
    else:
        messageText = '%s file does not exist:\n\n%s' % (fileType.capitalize(), filePath)
        PopUpMessage(messageText).open()
        return False

def foreignProjectFolder():

    messageText = 'The asset you picked belongs to a different project. Please change the project in the settings UI first and try again.'
    PopUpMessage(messageText).open()

def loadDefaultSettingsQuery(folderPath):

    if os.path.isdir(folderPath):
        return True
    if folderPath == '':
        folderText = 'No project folder defined. Please go to Settings and set a project folder.'
    else:
        folderText = 'Project folder does not exist. Please go to Settings and define a project folder.'
    messageText = '%s Do you wish to load the default settings?'%folderText
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def saveDefaultSettingsQuery(folderPath):

    if os.path.isdir(folderPath):
        return True
    if folderPath == '':
        folderText = 'No project folder defined. Please go to Settings and set a project folder.'
    else:
        folderText = 'Project folder does not exist. Please go to Settings and define a project folder.'
    messageText = '%s Do you wish to overwrite the default settings?'%folderText
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def assetFolderQuery(assetFolderPath):

    messageText = 'Asset folder does not exist. Do you wish to create it?\n\n' \
                + assetFolderPath
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def promptCustomSave(hasAssetName=True):

    messageText = ''
    if not hasAssetName:
        messageText += 'There is no asset name defined. ' \
                        'It is recommended to define an asset name in the Asset Folder tab in Settings.\n\n'
    messageText += 'Do you wish to be prompted with a custom save dialog?'
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def settingsLoaded(filePath):

    if os.path.isfile(filePath):
        messageText = 'Settings successfully loaded.'
        PopUpMessage(messageText).open()
        return True
    else:
        messageText = 'Project folder has no settings file: %s' % filePath
        PopUpMessage(messageText).open()
        return False

def noSettingsFile():

    messageText = 'Project folder has no settings file, loading default.'
    PopUpMessage(messageText).open()

def folderAlreadyExists(folderPath):

    if os.path.isdir(folderPath):
        messageText = 'New version folder already exists, saving aborted: %s' % folderPath
        PopUpMessage(messageText).open()
        return True
    else:
        return False

def fileNotFound():

    messageText = 'File not found. Please check if asset exists.'
    PopUpMessage(messageText).open()

def versionExists(filePath, versionName, fileType=None):
    
    if filePath == None:
        messageText = '%s version not found.' % fileType.capitalize()
        PopUpMessage(messageText).open()
        return False
    if os.path.isfile(filePath) and versionName in filePath:
        return True
    else:
        messageText = '%s version not found.' % fileType.capitalize()
        PopUpMessage(messageText).open()
        return False

def downloadFailed():
    
    messageText = "Licenses could not be retrieved. Please make sure you are connected to the internet."
    PopUpMessage(messageText).open()

def noProjectFolderFound():
    
    messageText = "Project folder does not exist. You can set the project folder under File -> Settings."
    PopUpMessage(messageText).open()

def versionFolderFound():

    messageText = "Your asset has a version folder, but it's not enabled in Settings. Please adjust your Settings or remove the version folder. Saving aborted."
    PopUpMessage(messageText).open()

def noVersionFolderFound():

    messageText = "Your asset has no version folder, but it's enabled in Settings. Please adjust your Settings or create a version folder. Saving aborted."
    PopUpMessage(messageText).open()

def noVersionFound():

    messageText = 'No version found. Check your folder conventions in Settings. You may check if you are using version folders.'
    PopUpMessage(messageText).open()

def alreadyExists(node, queryReplace=False):

    if queryReplace:
        if mc.objExists(node):
            messageText = '%s already exists, replace?' % node
            output = PopUpMessage(messageText, query=True).open()
            if output == "yes":
                mc.delete(node)
                return True
            else:
                return False
        else:
            return True
    else:
        messageText = '%s already exists, aborted.'
        PopUpMessage(messageText).open()
        return False
    
def confirmAssetSwitch(currentName, newName, name):

    messageText = 'You have opened a new %s. Would you like to switch %s in BEAR?\n\n'%(name, name) \
                + 'Current Asset:    %s\n'%currentName \
                + 'New Asset:         %s'%newName
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def moreThanOneNode():

    messageText = 'There are more than 1 nodes with this name. Please use long name as input.'
    PopUpMessage(messageText).open()
    return False

def guideAlreadyExists():

    messageText = 'This guide already exists in the scene. Choose a new name or skip.'
    PopUpMessage(messageText).open()
    return False

def placeholderCreated(node):
    
    messageText = 'A placeholder node was created for:\n\n%s\n\n' % node \
                    + "Please check the component build order."
    PopUpMessage(messageText).open()

def objectExists(node):
    
    if not mc.objExists(node):
        messageText = 'Object %s does not exist, aborted.' % node
        PopUpMessage(messageText).open()
        return False
    else:
        return True

def validType(node, shapeType='ffd'):
    
    if not mc.objExists(node):
        return False
    
    if mc.objectType(node) != shapeType:
        messageText = '%s is no valid shape type: %s' % (node, shapeType)
        PopUpMessage(messageText).open()
        return False
     
    return True

def geometryGroupExists(geometryGroupName):
    
    if not mc.objExists(geometryGroupName):
        messageText = "The specified geometry group '%s' does not exist. Saving aborted.\n" % geometryGroupName \
                    + "Please check your settings and make sure all skin geometry is parented under the geometry group."
        PopUpMessage(messageText).open()
        return False
    else:
        return True

def skinMeshSetExists(nodes):
    
    for node in nodes:
        if not mc.objExists(node):
            messageText = 'SkinMesh Set does not exist, aborted.\n\n'
            messageText += '\n'.join(nodes)
            PopUpMessage(messageText).open()
            return False
    return True

def skinJointsRemoved(removedSkinJoints):
    
    messageText = 'Following joints have been removed from the Skin Cluster:\n\n'
    for removedSet in removedSkinJoints:
        messageText += (removedSet[0]+':\n\n' + \
                        '\n'.join(removedSet[1])+'\n\n')
    PopUpMessage(messageText).open()

def usingFileFolderAsAssetName(assetName):

    messageText = 'Using File Folder as Asset Name: %s' % assetName
    PopUpMessage(messageText).open()

def saveFileRequired():

    messageText = 'Please save your file first.'
    PopUpMessage(messageText).open()

def invalidCharacter():

    messageText = 'The name has invalid characters. Only standard alphabetic characters and numbers are allowed. No underscores or spaces are allowed.'
    PopUpMessage(messageText).open()

def invalidFolder():
    
    messageText = 'Invalid asset or sub folder names.'
    PopUpMessage(messageText).open()

def foldersCreated():
    
    messageText = 'Asset folders have been created.'
    PopUpMessage(messageText).open()

def querySideBuilding():
    
    messageText = "You have selected a side to build under Guide in the Builder UI. " \
                + "Building sides is only possible on selected components. Side building is ignored on collections."
    PopUpMessage(messageText).open()

def uniqueName(node, item, type='component'):

    if mc.objExists(node):
        messageText = '%s name already exists. A unique %s name is required:\n\n%s' % (type.capitalize(), type, item)
        PopUpMessage(messageText).open()
        return False
    else:
        return True

def uniqueCollection():

    messageText = "A component of the collection already exists in the scene. A new collection must have unique component names.\n\n" + \
                    "You can create the collection in a new scene, rename non-unique component names and save a new collection under Edit -> Save Collection."
    PopUpMessage(messageText).open()

def noMeshType():

    messageText = 'Selected node is not of type mesh, aborted.' % ' or '.join()
    PopUpMessage(messageText).open()

def selectionOrder(order):

    messageText = 'Aborted. You need to select the following order:\n\n%s' % ', '.join(order)
    PopUpMessage(messageText).open()

def invalidLoop():

    messageText = 'The selected loops are touching a pole. Please make sure no poles are inside or at the end of the loops.'
    PopUpMessage(messageText).open()
    return

def nodesProcessed(nodes):

    if nodes == []:
        messageText = 'No open/closed guide nodes found, aborted.'
    else:
        messageText = 'The following open/closed guide nodes have been matched:\n\n%s' % ', '.join(nodes)
    PopUpMessage(messageText).open()

def rebuildRequired(buildType='guide'):

    messageText = 'An error has occured. Rebuild the guide and try again.'
    PopUpMessage(messageText).open()

def noDeliveryScriptFound():

    messageText = "No delivery script found. Please use a Script component with 'delivery' as Run After Build Step."
    PopUpMessage(messageText).open()

def deliveryError():

    messageText = "An error has occured in the delivery script file. Make sure you are saving from the setup file."
    PopUpMessage(messageText).open()

def symmetryOutput(leftVCount, rightVCount, midVCount, unmatchedVCount, popIfGood=True, query=False):
    messageText = (
        f'Detected symmetrical vertices:\n\n'
        f'Symmetrical: {leftVCount}\n'
        f'Middle: {midVCount}\n'
        f'Unmatched: {unmatchedVCount}\n\n'
    )

    if unmatchedVCount == 0 and leftVCount == rightVCount:
        summary = 'Object symmetry looks good'
        messageText += summary
        if popIfGood:
            PopUpMessage(messageText).open()
        return True
    else:
        summary = (
            'Object is not fully symmetrical. Unmatched vertices will be ignored.\n'
            'You can go ahead and perform the mirror, however it is recommended '
            'to fix the geometry or increase the tolerance.'
        )
        if query:
            messageText += summary + ' Continue?'
            output = PopUpMessage(messageText, query=True).open()
            return output == "yes"
        else:
            messageText += summary
            PopUpMessage(messageText).open()
        return True
        
def setMirror():
    
    messageText = 'Please set a mirror source first.'
    PopUpMessage(messageText).open()

def collectionSelected():
    
    messageText = 'Please select a collection group. You can only save one collection at a time.'
    PopUpMessage(messageText).open()

def collectionOverwriteExisting():
    
    messageText = 'A coilection with that name already exists. Overwrite?'
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def collectionFolderMissing():
    
    messageText = 'Collection folder does not exist. Do you wish to create the folder?'
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def selectionCount(count, exactCount=False):

    if exactCount:
        messageText = 'Aborted. Please select exactly %s vertex marking the end of the loop.'%count
    else:
        messageText = 'Aborted. Please select at least %s object%s.' % (count, '' if count == 1 else 's')
    PopUpMessage(messageText).open()

def selectionType(type='edge'):

    messageText = 'Aborted. Selection needs to be of type '+type+'.'
    PopUpMessage(messageText).open()

def noNameTag(nameTag, node=None):

    messageText = 'Please select a %s node.' % nameTag
    if node != None:
        if not nameTag in node:
            PopUpMessage(messageText).open()
            return False
        else:
            return True
    PopUpMessage(messageText).open()

def noObjectFound(nameTag):
    
    messageText = 'No %s found.' % nameTag
    PopUpMessage(messageText).open()

def selectSourceTarget():

    messageText = 'Aborted. You need to select the source and the target geometry.'
    PopUpMessage(messageText).open()

def noTemplateModule():

    messageText = 'No template module defined.'
    PopUpMessage(messageText).open()
    return

def vertexCount(node, count):
    
    if mc.polyEvaluate(node, v=True) != count:
        messageText = 'Aborted. Selected geometries must have the vertex count as defined in the template file.'
        PopUpMessage(messageText).open()
        return False
    else:
        return True

def noInputNode(inputTag):

    messageText = 'Source object has no %s, aborted.' % inputTag
    PopUpMessage(messageText).open()

def noSourceObject():
    
    messageText = 'No source object defined, aborted.'
    PopUpMessage(messageText).open()

def missingInput(inputTag):

    messageText = 'No %s defined, aborted.' % inputTag 
    PopUpMessage(messageText).open()

def quadrupedNeckBuild():

    messageText = "The quadruped neck already builds with FK controls. There is no neck needed for the head component.\n\n" \
                + "The 'Has Neck' attribute on the head component has been set to False."
    PopUpMessage(messageText).open()

def incorrectNamingConvention():

    messageText = "The naming convention is incorrect.\n" \
                + "Make sure to use the following\n" \
                + "tokens in your desired order:\n\n" \
                + "component\n" \
                + "side\n" \
                + "element\n" \
                + "indices\n" \
                + "specific\n" \
                + "nodeType\n"
    PopUpMessage(messageText).open()

def queryNamingConvention():

    messageText = "This will apply the token order to all objects and close BEAR. Continue?"
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def namingConventionApplied():

    messageText = "Naming convention applied. Please restart BEAR."
    PopUpMessage(messageText).open()

def usingExistingGuideRoot():

    messageText = "Using existing guide root."
    PopUpMessage(messageText).open()

def noObjectsToRename():

    messageText = "No objects to rename."
    PopUpMessage(messageText).open()

def queryRenameTokens():

    messageText = "This will rename the objects in the scene. Continue?"
    output = PopUpMessage(messageText, query=True).open()
    return output == "yes"

def tokensRenamed():

    messageText = "Objects renamed."
    PopUpMessage(messageText).open()

def convertToGuidePlacer():
    
    messageText = 'Limb guides will now be updated with guide placer nodes. This might take a few seconds.'
    PopUpMessage(messageText).open()

def convertToGuidePlacerComplete():
    
    messageText = 'Limb guides have been updated. The new guide placer nodes allow more convenient guide placing and guide to geometry matching.'
    PopUpMessage(messageText).open()

def noIndicesInFront():

    messageText = "You can't have indices in the front."
    PopUpMessage(messageText).open()

def noIndices(objType):

    messageText = "The %s you have chose have no indices in their name."%(objType)
    PopUpMessage(messageText).open()

def noCorrespondingObjectsFound(names, objType):

    messageText = "No corresponding %s found: %s"%(names, objType)
    PopUpMessage(messageText).open()

def unableToMatchIkFk():

    messageText = "Can't match inbetween state. Matching aborted."
    PopUpMessage(messageText).open()

def printRigHierarchy(compName, rig, side, compType, printDetails=False, printBuildTime=False):
    
    print('\nBuilding %s component: %s %s'%(compType, compName, side if side else ''))

    if printDetails:
        for key, value in rig.items():
            if type(value) != dict:
                print(key+': '+str(value))
            else:
                for key, value in value.items():
                    if type(value) != dict:
                        print('   '+key+': '+str(value))
                    else:
                        for key, value in value.items():
                            if type(value) != dict:
                                print('      '+key+': '+str(value))
                            else:
                                for key, value in value.items():
                                    if type(value) != dict:
                                        print('            '+key+': '+str(value))
                                    else:
                                        for key, value in value.items():
                                            if type(value) != dict:
                                                print('               '+key+': '+str(value))

    print('%s component build completed'%compType + (' (build time: %s sec.)'%(mc.timer(endTimer=True)) if printBuildTime else ''))