# Settings

import json, os, sys, shutil
import maya.cmds as mc
import maya.mel as mel

def getRootPath():

    rootPath = os.path.dirname(__file__)
    for _ in range(1):
        rootPath = os.path.dirname(rootPath)

    return rootPath

def getPath(folders=[]):

    path = os.path.join(getRootPath(), *folders)
    
    return path

def getUserFile(returnInstance=False):
    
    mayaUserFolder = mc.internalVar(userAppDir=True)
    mayaVersion = mc.about(version=True)
    processId = os.getpid()
    userDataFolder = os.path.join(mayaUserFolder, mayaVersion, 'prefs', 'bear')
    if not os.path.exists(userDataFolder):
        os.makedirs(userDataFolder)
    userDataFolderInstance = os.path.join(userDataFolder, str(processId))
    if not os.path.exists(userDataFolderInstance):
        os.makedirs(userDataFolderInstance)

    userFile = os.path.join(userDataFolder, 'bear_user_settings.json')
    
    userFileInstance = os.path.join(userDataFolderInstance, 'bear_user_settings.json')
    if returnInstance:
        return userFile, userFileInstance, userDataFolderInstance
    
    defaultUserFile = getDefaultSettings('bear_user_settings.json')
    if not os.path.isfile(userFile):
        shutil.copy(defaultUserFile, userFile)

    if os.path.isfile(userFileInstance):
        return userFileInstance
    else:
        shutil.copy(userFile, userFileInstance)

    return userFile

def getDefaultSettings(settingsFileName='bear_builder_settings.json'):

    rootFolder = getRootPath()
    defaultFile = rootFolder+'/ui/'+settingsFileName
    
    return defaultFile

def getScreenResolution():
    
    if sys.platform.startswith('darwin'):
        from AppKit import NSScreen
        width = int(NSScreen.mainScreen().frame().size.width)
        height = int(NSScreen.mainScreen().frame().size.height)
    elif sys.platform.startswith('win'):
        import ctypes
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
    elif sys.platform.startswith('linux'):
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
    else:
        width = 0
        height = 0
        
    return width, height

def loadSettings(settingsFilePath=None):

    userFile = getUserFile()
    userAttrs = json.load(open(userFile))

    projectFolder = userAttrs['projectFolder']
    assetFolder = userAttrs['assetFolder']

    defaultLoadedSettings = json.load(open(getDefaultSettings()))

    if not settingsFilePath:
        settingsFilePath = projectFolder+'/bear_builder_settings.json'
    
    if os.path.isfile(settingsFilePath):
        projectLoadedSettings = json.load(open(settingsFilePath))
    else:
        projectLoadedSettings = {}
    
    for key in defaultLoadedSettings.keys():
        if key in projectLoadedSettings.keys():
            userAttrs[key] = projectLoadedSettings[key]
        else:
            userAttrs[key] = defaultLoadedSettings[key]

    return userAttrs, assetFolder

def getMayaUserFolder():
    # Get the Maya version (e.g., '2023')
    maya_version = mc.about(version=True)

    if mc.about(os=True) == "mac":
        maya_user_folder = os.path.expanduser(f'~/Library/Preferences/Autodesk/maya/{maya_version}')
    elif mc.about(os=True) == "win64":
        maya_user_folder = os.path.join(os.getenv('APPDATA').replace("\\", "/"), f'Autodesk/maya/{maya_version}')
    else:  # Assuming it's Linux
        maya_user_folder = os.path.expanduser(f'~/.maya/{maya_version}')

    return maya_user_folder
    
loadedSettings = loadSettings()[0]

guideRoot = loadedSettings['guideRoot']
rigRoot = loadedSettings['rigRoot']
deformConstraintsGroup = 'deformConstraints'
spaceAttrName = 'space'
spaceNodeSuffix = 'spc'
spaceLocSuffix = 'slc'
reverseSpaceNodeSuffix = 'revSpc'
drivenNodeSuffix = 'drv'
skinJointSuffix = loadedSettings['skinJointToken']
setupSkinJointSuffix = 'setupSkinJoint'
setupJointSuffix = 'jnt'
skinMeshSuffix = 'skinMesh'
skinMeshTransferSuffix = 'skinMeshTransfer'
simMeshSuffix = 'simulationMesh'
simCurveSuffix = 'simulationCurve'
simulatedGeoSuffix = 'simulatedGeo'
skinnedGeoSuffix = 'skinnedGeo'
collisionMeshSuffix = 'collisionMesh'
expressionSuffix = 'xpr'
controlSuffix = loadedSettings['controlToken']
offNodeSuffix = loadedSettings['spaceToken']
cntNodeSuffix = 'cnt'
deformNodeSuffix = 'deform'
inverseNodeSuffix = 'inverse'
bshGeoNodeSuffix = 'bsh'
geoBshSuffix = 'geoBsh'
bshSrcGeoNodeSuffix = 'bshSrc'
collisionGeoNodeSuffix = 'collision'
geoNodeSuffix = loadedSettings['geometryToken']
layoutGeoNodeSuffix = 'layoutGeo'
layoutSuffix = 'layout'
locNodeSuffix = 'loc'
guidePivotSuffix = loadedSettings['guidePivotToken']
guideShapeSuffix = loadedSettings['guideShapeToken']
guideCurveSuffix = 'gdeCrv'
guideSurfaceSuffix = 'gdeSrf'
guideOffSuffix = 'gdcOff'
guidePoseSuffix = 'guidePose'
pathNodeSuffix = 'pth'
motionPathSuffix = 'motionPath'
motionPathGuideSuffix = 'motionPathGde'
motionPathNodeSuffix = 'mpt'
dynMotionPathSuffix = 'dynMotionPath'
transferSuffix = 'trf'
pivotSuffix = 'pvt'
templateSuffix = 'tmp'
templateNode = 'template'
pivotOffsetSuffix = 'pivotOffset'
pivotCompensateSuffix = 'pivotCompensate'
clusterHandleSuffix = 'clsHandle'
clusterSuffix = 'clsHandleCluster'
guideClusterHandleSuffix = 'gdeClsHandle'
guideClusterSuffix = 'gdeClsHandleCluster'
proximityPinSuffix = 'prxPin'
proximityLocSuffix = 'prxLoc'
proximityWrapSuffix = 'prxWrap'
dupNodeSuffix = 'dup'
curveDupNodeSuffix = 'dupCrv'
folNodeSuffix = 'fol'
attachNodeSuffix = 'att'
curveSuffix = 'crv'
dynamicsCurveSuffix = 'dynCrv'
surfaceSuffix = 'srf'
baseNodeSuffix = 'base'
layoutSuffix = 'layout'
parentSuffix = 'pnt'
parentGuideSuffix = 'pntGde'
matrixSuffix = 'mtx'
ikHandleSuffix = 'ikHandle'
orientConstraintSuffix = 'orientConstraint'
pointConstraintSuffix = 'pointConstraint'
parentConstraintSuffix = 'parentConstraint'
poleVectorConstraintSuffix = 'poleVectorConstraint'
aimConstraintSuffix = 'aimConstraint'
decomposeMatrixSuffix = 'decompMtx'
originOffNodeSuffix = 'ognOff'
originNodeSuffix = 'ogn'
mulNodeSuffix = 'mul'
addNodeSuffix = 'add'
divNodeSuffix = 'div'
plusNodeSuffix = 'plus'
clampNodeSuffix = 'clamp'
conditionNodeSuffix = 'condition'
curveInfoSuffix = 'curveInfo'
curveInfoGuideSuffix = 'curveInfoGde'
keepOutSuffix = 'keepOut'
keepOutDrivenSuffix = 'keepOutDriven'
muscleObjectSuffix = 'muscleObject'
collisionShapeSuffix = 'collisionShape'
postDeformAlignmentNode = 'pra'
squashStretchMeshSuffix = 'squashStretch'
latticeNodeSuffix = 'lattice'
mirrorScaleSuffix = 'mirScl'
scaleCompensateNode = 'sclCmp'
distanceSuffix = 'dst'
distanceGuideSuffix = 'dstGde'
distanceLocSuffix = 'dstLoc'
distanceLocGuideSuffix = 'dstLocGde'
tempConnectionNode = 'tmpCon'
connectionNode = 'con'
scriptNode = 'script'
refSuffix = 'ref'
dummySuffix = 'dummy'
setSuffix='set'
controlSetSuffix='controlSet'
jointSetSuffix='jointSet'
leftSide = loadedSettings['leftSideToken']
rightSide = loadedSettings['rightSideToken']

namingOrder = loadedSettings['namingConvention'].split('_')

modelSubFolder = '/model'
guideSubFolder = '/guide'
setupSubFolder = ''
rigSettingsSubFolder = '/rigSettings'
controlTransformsSubFolder = '/controlTransforms'
deformSubFolder = '/deform'
blendshapesSubFolder = '/blendshapes'
deliverySubFolder = '/delivery'

modelFileIndicator = 'model'
guideFileIndicator = 'guide'
setupFileIndicator = 'setup'
rigSettingsFileIndicator = 'rigSettings'
controlTransformsFileIndicator = 'controlTransforms'
inputOrderFileIndicator = 'inputOrder'
deformFileIndicator = 'deform'
blendshapesFileIndicator = 'blendshapes'
deliveryFileIndicator = 'delivery'

poseCorrectionsGroup = 'poseCorrections'
faceBshGroup = 'blendshapes_face'
correctiveBshGroup = 'blendshapes_face_corrective'
basePoseBind = 'basePose_bind'
basePoseDefault = 'basePose_default'
geometryGroup = loadedSettings['geometryGroup']
guidelinesGroup = 'guidelines'
templateGroup = 'template'
guideGroup = 'guide'
rigGroup = 'rig'
skinMeshesGroup = 'skinMeshes'
skinTemplateGroup = 'skinTemplate'
placeHolderGroup = 'placeHolderNodes'

licenseVersion = 'full'
try:
    from bear.utilities import PoseInterpolator
except:
    licenseVersion = 'free'

createControllerTag = loadedSettings['createControllerTags']

shapes = ['Circle', 
            '3D Circle',
            'Sphere', 
            'Rectangle', 
            'Rounded Rectangle',
            'Triangle',
            'Pyramid',
            'Cube', 
            'Octagon',
            'Cross', 
            'Arrow', 
            'Double Arrow', 
            'Quad Arrow', 
            'Marker',
            'Needle', 
            'Double Needle', 
            'Square Needle', 
            'Sphere Needle', 
            'Pyramid Needle', 
            'Placement', 
            'Biped Leg IK', 
            'Quadruped Leg IK']
            
colors = ['Red', 
            'Orange', 
            'Yellow', 
            'Green', 
            'Blue', 
            'Purple', 
            'Bright Red', 
            'Bright Orange', 
            'Bright Yellow', 
            'Bright Green', 
            'Bright Blue', 
            'Bright Purple', 
            'Dark Red', 
            'Dark Orange', 
            'Dark Yellow', 
            'Dark Green', 
            'Dark Blue', 
            'Dark Purple',
            'White',
            'Grey',
            'Black']

colorsHSV = [(0, 1, 1), #red
                (0.08, 1, 1), #orange
                (0.2, 0.7, 1), #yellow
                (0.32, 1, 1), #green
                (0.665, 1, 1), #blue
                (0.8, 1, 1), #purple
                (0, 0.5, 1), #brightred
                (0.08, 0.7, 1), #brightorange
                (0.2, 0.4, 1), #brightyellow
                (0.32, 0.7, 1), #brightgreen
                (0.56, 1, 1), #brightblue
                (0.8, 0.7, 1), #brightpurple
                (0, 1, 0.4), #darkred
                (0.12, 1, 0.4), #darkorange
                (0.2, 0.7, 0.65), #darkyellow
                (0.42, 1, 0.28), #darkgreen
                (0.665, 1, 0.1), #darkblue
                (0.8, 1, 0.1), #darkpurple
                (0, 0, 1), #white
                (0, 0, 0.3), #grey
                (0, 0, 0)] #black

colorsRGB = [mel.eval('hsv_to_rgb <<%s, %s, %s>>'%(colorsHSV[x][0], colorsHSV[x][1], colorsHSV[x][2])) for x in range (len(colorsHSV))]