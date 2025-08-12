# DataStructure

import maya.cmds as mc
import inspect, imp, os, json

from bear.system import Settings
from bear.system import Files
from bear.system import MessageHandling
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.utilities import Tools
from bear.utilities import Weights
from bear.components.various import DeformTweak
from bear.ui import GuidePicker
    
def getSignature(module, asList=False):

    buildAttrs = list() if asList else dict()

    signature = None
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            if obj.__name__ == 'Build':
                try:
                    signature = inspect.getargspec(module.Build().__init__)
                except:
                    signature = inspect.getfullargspec(module.Build().__init__)
    
    if signature == None:
        return buildAttrs
    
    for s, sig in enumerate(signature[0][1:]):
        if asList:
            buildAttrs.append([sig, list(signature[3])[s]])
        else:
            buildAttrs[sig] = list(signature[3])[s]
    
    return buildAttrs

def getModuleByName(moduleName, moduleFolder, modulesRootFolder):

    modulePath = modulesRootFolder+'/components'+moduleFolder+'/'+moduleName+'.py'
    if os.path.isfile(modulePath):
        module = imp.load_source(moduleName, modulePath)
    else:
        modulePath = modulesRootFolder+'/components'+moduleFolder+'/'+moduleName+'.pyc'
        module = imp.load_compiled(moduleName, modulePath)

    return module

class Asset(object):
    
    def __init__(self,
                    versionName=None,
                    assetFolder=None,
                    customFile=None,
                    guideRefPrefix='guideRef',
                    rigSettingsRefPrefix='rigSettingsRef',
                    skinRefPrefix='skinRef',
                    skinGeoName='skin',
                    hasLayoutGeometry=False,
                    loadFromFile=None,
                    *args, **kwargs):

        self.rootFolder = Settings.getPath()
        projectFile = Settings.getUserFile()
        self.projectFolder = json.load(open(projectFile))['projectFolder']

        if assetFolder:
            self.assetFolder = assetFolder
        else:
            self.assetFolder = json.load(open(projectFile))['assetFolder']

        self.loadedSettings = Settings.loadSettings()[0]
            
        if not os.path.isdir(self.projectFolder):
            self.projectFolder = None

        self.modelSubFolder = Settings.modelSubFolder
        self.guideSubFolder = Settings.guideSubFolder
        self.setupSubFolder = Settings.setupSubFolder
        self.rigSettingsSubFolder = Settings.rigSettingsSubFolder
        self.deformSubFolder = Settings.deformSubFolder
        self.blendshapesSubFolder = Settings.blendshapesSubFolder
        self.deliverySubFolder = Settings.deliverySubFolder

        self.modelFileIndicator = Settings.modelFileIndicator
        self.guideFileIndicator = Settings.guideFileIndicator
        self.setupFileIndicator = Settings.setupFileIndicator
        self.rigSettingsFileIndicator = Settings.rigSettingsFileIndicator
        self.controlTransformsFileIndicator = Settings.controlTransformsFileIndicator
        self.inputOrderFileIndicator = Settings.inputOrderFileIndicator
        self.deformFileIndicator = Settings.deformFileIndicator
        self.blendshapesFileIndicator = Settings.blendshapesFileIndicator
        self.deliveryFileIndicator = Settings.deliveryFileIndicator

        self.versionName = versionName
        self.versionNaming = self.loadedSettings['versionNaming']
        self.versionFolder = None
        
        self.assetNode = Nodes.getAssetNode()[0]
        self.templateRoot = Settings.templateGroup
        self.skinTemplateRoot = Settings.skinTemplateGroup
        self.skinMeshRoot = Settings.skinMeshesGroup
        self.poseCorrectionsRoot = Settings.poseCorrectionsGroup
        self.faceBlendshapesRoot = Settings.faceBshGroup
        self.correctiveBlendshapes = Settings.correctiveBshGroup
        self.rigRoot = Settings.rigRoot
        self.guideRoot = Settings.guideRoot
        self.geometryRoot = Settings.geometryGroup.replace(' ', '').split(',')
        self.skinGeoName = skinGeoName
        self.hasLayoutGeometry = hasLayoutGeometry

        self.mayaFileType = self.loadedSettings['mayaFileType']

        self.loadFromFile = loadFromFile
        self.useFileLocation = False

        self.modelFile = None
        self.guideFile = None
        self.setupFile = None
        self.rigSettingsFile = None
        self.skinFile = None
        self.blendshapesFile = None
        self.deliveryFile = None

        if not self.versionName:
            self.versionName = Files.Config(self.projectFolder,
                                            self.assetFolder).getVersion()
        if self.versionName:
            self.guideRefPrefix = guideRefPrefix+'_'+self.versionName
            self.rigSettingsRefPrefix = rigSettingsRefPrefix+'_'+self.versionName
            self.skinRefPrefix = skinRefPrefix+'_'+self.versionName
        else:
            self.guideRefPrefix = guideRefPrefix
            self.rigSettingsRefPrefix = None
            self.skinRefPrefix = None

        if customFile:
            self.modelFile = customFile
        else:
            self.modelFile = Files.Config(self.projectFolder,
                                          self.assetFolder,
                                          fileType=self.modelFileIndicator,
                                          version=self.versionName).assembleFilePath()
        self.guideFile = Files.Config(self.projectFolder,
                                          self.assetFolder,
                                          fileType=self.guideFileIndicator,
                                          version=self.versionName).assembleFilePath()
        self.setupFile = Files.Config(self.projectFolder,
                                          self.assetFolder,
                                          fileType=self.setupFileIndicator,
                                          version=self.versionName).assembleFilePath()
        self.rigSettingsFolder = Files.Config(self.projectFolder,
                                          self.assetFolder,
                                          fileType=self.rigSettingsFileIndicator,
                                          version=self.versionName).assembleFolderPath()
        self.controlTransformsFolder = Files.Config(self.projectFolder,
                                          self.assetFolder,
                                          fileType=self.controlTransformsFileIndicator,
                                          version=self.versionName).assembleFolderPath()
        self.inputOrderFolder = Files.Config(self.projectFolder,
                                          self.assetFolder,
                                          fileType=self.inputOrderFileIndicator,
                                          version=self.versionName).assembleFolderPath()
        self.skinFile = Files.Config(self.projectFolder,
                                          self.assetFolder,
                                          fileType=self.deformFileIndicator,
                                          version=self.versionName).assembleFilePath()
        self.blendshapesFile = Files.Config(self.projectFolder,
                                          self.assetFolder,
                                          fileType=self.blendshapesFileIndicator,
                                          version=self.versionName).assembleFilePath()
        self.deliveryFile = Files.Config(self.projectFolder,
                                          self.assetFolder,
                                          fileType=self.deliveryFileIndicator,
                                          version=self.versionName).assembleFilePath()

    def model(self):
        
        if self.modelFile == None:
            return
        
        if not mc.file(self.modelFile, q=True, exists=True):
            mc.error(f"Model file does not exist: {self.modelFile}")

        if mc.file(location=True, q=True) != self.modelFile:
            if self.modelFile.endswith('.usd'):
                mc.file(self.modelFile, o=True, typ="USD Import", ignoreVersion=True)
            else:
                mc.file(self.modelFile, i=True, ignoreVersion=True)
        else:
            return
    
    def guideSettings(self, 
                        guideGroup=None,
                        nodeList=[],
                        alignGuideGroupSettings=True,
                        alignPivotPosition=True, 
                        alignPivotRotation=True,
                        alignShapeSettings=True,
                        alignShapeTransforms=True,
                        copyGuide=False,
                        fromAsset=False,
                        getFromSide=False,
                        oldName=None,
                        newName=None,
                        newCollectionName=None):
        
        if self.loadFromFile != None:
            self.guideFile = self.loadFromFile        
        elif self.guideFile == None:
            MessageHandling.noGuide()
            return None, None
        
        if not mc.file(self.guideFile, q=True, exists=True):
            mc.error(f"Guide file does not exist: {self.guideFile}")
        if not self.guideFile in mc.file(reference=True, q=True):
            try:
                mc.file(self.guideFile, r=True, namespace=self.guideRefPrefix, ignoreVersion=True)
            except:
                pass
        
        for topNode in mc.ls(assemblies=True):
            if self.guideRefPrefix+':' in topNode:
                mc.hide(topNode)

        # copyGuide makes definition only
        if copyGuide and not fromAsset:
            
            refIncomingGuide = [x for x in mc.ls(assemblies=True) if mc.objExists('%s.globalNamingConvention'%x) and mc.referenceQuery(x, isNodeReferenced=True)]
            if refIncomingGuide == []:
                MessageHandling.noGuide()
                return None, None
            else:
                refIncomingGuide = refIncomingGuide[0]
            incomingGuide = mc.duplicate(refIncomingGuide, name=self.guideRoot+'_'+'incoming')[0]

            for guideChild in Nodes.getAllChildren(incomingGuide):
                try:
                    if not mc.objExists(guideChild+'.componentType') and not mc.referenceQuery(guideChild, isNodeReferenced=True):
                        mc.delete(guideChild)
                except:
                    pass

            guideCollections = list()
            for guideCollection in mc.listRelatives(incomingGuide, children=True, fullPath=True):
                guideChildren = mc.listRelatives(guideCollection, children=True, fullPath=True)
                if guideChildren != None:
                    for guideChild in guideChildren:
                        guideName = guideChild.split('|')[-1]
                        if len(mc.ls(guideName)) > 1:
                            if mc.objExists('guide1'):
                                mc.delete('guide1')
                            if mc.objExists(incomingGuide):
                                mc.delete(incomingGuide)
                            if self.guideFile:
                                mc.file(self.guideFile, removeReference=True)
                            MessageHandling.uniqueCollection() #TODO implement picker window to pick desired guide groups
                            return None, None
                guideName = guideCollection.split('|')[-1]
                if newCollectionName != None:
                    if mc.getAttr(guideCollection+'.componentType') == 'Collection':
                        newCollection = mc.rename(guideCollection, '_'.join([newCollectionName]+guideName.split('_')[1:]))
                        mc.setAttr('%s.name'%newCollection,  newCollectionName, type='string')
                        guideCollections.append(newCollection)

            guideRoot = incomingGuide if not mc.objExists(self.guideRoot) else self.guideRoot
            incomingGuideGroups = list()
            if mc.objExists(guideRoot):
                for x in mc.listRelatives(incomingGuide, children=True):
                    Nodes.setParent(x, guideRoot)
                    incomingGuideGroups.append(x.split('|')[-1])

            Nodes.setParent(guideRoot, 'world' if self.assetNode == None else self.assetNode)
            Nodes.applyGlobalScale(guideRoot, [guideRoot], lock=True)
            mc.showHidden(guideRoot)
            
            if mc.objExists(self.guideRoot):
                mc.delete(incomingGuide)
            else:
                mc.rename(incomingGuide, '_'.join(incomingGuide.split('_')[:-1]))

            if mc.objExists('guide1'):
                mc.delete('guide1')
            if mc.objExists(incomingGuide):
                mc.delete(incomingGuide)

            return self.guideFile, incomingGuideGroups
        
        # import guide from asset
        if copyGuide and fromAsset:

            refIncomingGuide = [x for x in mc.ls(assemblies=True) if mc.objExists('%s.globalNamingConvention'%x) and mc.referenceQuery(x, isNodeReferenced=True)]
            if refIncomingGuide == []:
                MessageHandling.noGuide()
                return None, None
            else:
                refIncomingGuide = refIncomingGuide[0]
                
            guideCollections = list()
            guideGroups = list()
            for guideParent in mc.listRelatives(refIncomingGuide, children=True, fullPath=True):
                guideGroups.append([])
                if Nodes.getComponentType(guideParent) == 'Collection':
                    guideCollections.append(guideParent)
                    guideChildren = mc.listRelatives(guideParent, children=True, fullPath=True)
                    if guideChildren != None:
                        for guideChild in guideChildren:
                            guideGroups[-1].append(guideChild)
                else:
                    guideCollections.append(None)
                    guideGroups[-1].append(guideParent)

            GuidePicker.showPicker(guideCollections, guideGroups, self.guideRefPrefix, self.guideFile)
            
            if Nodes.exists(Settings.guideRoot):
                Nodes.setParent(Settings.guideRoot, 'world' if self.assetNode == None else self.assetNode)
                Nodes.applyGlobalScale(Settings.guideRoot, [Settings.guideRoot], lock=True)
                mc.showHidden(Settings.guideRoot)
            
            return None, None

        trgGuideRoot= Tools.getNodeByName(guideGroup, getRef=False)
        
        def getSourceSideNode(node, originalNode):

            if getFromSide == False:
                srcNode = node
            else:
                if getFromSide == None:
                    srcNode = node
                else:
                    srcNode = Nodes.replaceSide(originalNode, getFromSide).replace(newName, oldName)
            return srcNode

        trgGuideRoot = Tools.getNodeByName(guideGroup, getRef=False)
        
        if nodeList == [] and trgGuideRoot:
            trgNodeList = Nodes.getAllChildren(trgGuideRoot, includeRoot=True)
        else:
            trgNodeList = nodeList

        for trgNode in trgNodeList+[Settings.guideRoot]:
            
            if oldName and newName:
                replacedTrgNode = trgNode.replace(newName, oldName)
            else:
                replacedTrgNode = trgNode
            
            srcNode = Tools.getNodeByName(self.guideRefPrefix+':'+getSourceSideNode(replacedTrgNode, trgNode))

            if srcNode and Nodes.getNodeType(srcNode) != Settings.guideOffSuffix:
                
                # retrieving global scale
                globalScaleValue = 1
                isScaled = False
                parentIsScaled = False
                for parentNode in Nodes.getAllParents(srcNode):
                    globalScaleAttr = parentNode+'.globalScale'
                    if mc.objExists(globalScaleAttr):
                        globalScaleValue *= mc.getAttr(globalScaleAttr)
                        if mc.getAttr(globalScaleAttr) != 1:
                            parentIsScaled = True
                globalScaleAttr = srcNode+'.globalScale'
                if mc.objExists(globalScaleAttr):
                    if mc.getAttr(globalScaleAttr) != 1:
                        isScaled = True

                objType = Nodes.getShapeType(trgNode)
                
                trgType = None
                if Nodes.getNodeType(trgNode) == Settings.guideCurveSuffix:
                    trgType = 'guideCurve'
                    continue
                if Nodes.getNodeType(trgNode) == Settings.guideOffSuffix:
                    trgType = 'guideOff'
                    continue
                if Nodes.getNodeType(trgNode) == Settings.guideGroup:
                    trgType = 'guide'
                if Nodes.getNodeType(trgNode) == Settings.guidePivotSuffix:
                    trgType = 'guidePivot'
                if Nodes.getNodeType(trgNode) == Settings.guideShapeSuffix:
                    trgType = 'guideShape'
                if Nodes.getNodeType(trgNode) == Settings.guideSurfaceSuffix:
                    trgType = 'guideSurface'
                
                guideType = 'locator'
                if objType in ['nurbsCurve', 'bezierCurve'] and trgType == 'guidePivot':
                    guideType = 'pivotShape'
                if objType == 'lattice':
                    guideType = 'lattice'
                if objType == 'nurbsSurface':
                    guideType = 'nurbsSurface'
                
                trsList = list()
                if trgType == 'guide' or trgType == 'guidePivot':
                    trsList.append('s')
                    if alignPivotRotation:
                        trsList.append('r')
                    if alignPivotPosition:
                        trsList.append('t')
                if (trgType == 'guideShape' or trgType == 'guideSurface') and alignShapeTransforms:
                    trsList.append('s')
                    trsList.append('r')
                    trsList.append('t')

                if mc.objExists(srcNode):
                    for trs in trsList:
                        for axis in 'xyz':
                            attrName = '%s.%s%s' % (srcNode, trs, axis)
                            sourceValue = mc.getAttr(attrName)
                            # global scale applied to translate and control scale
                            if trs == 't':
                                if parentIsScaled and not isScaled:
                                    sourceValue = sourceValue*globalScaleValue
                            if trs == 's' and trgType == 'guideShape':
                                sourceValue = sourceValue*globalScaleValue
                            #
                            trgAttr = '%s.%s%s' % (trgNode, trs, axis)
                            try:
                                mc.setAttr(trgAttr, sourceValue)
                            except:
                                pass
                            if mc.objectType(srcNode) == 'joint' and mc.objectType(trgNode) == 'joint' and alignPivotRotation:
                                sourceJointOrient = mc.getAttr('%s.jointOrient%s' % (srcNode, axis.capitalize()))
                                mc.setAttr('%s.jointOrient%s' % (trgNode, axis.capitalize()), sourceJointOrient)
                else:
                    MessageHandling.warning('Object %s not found in guide' % srcNode)

                    # curve joint guiding
                    if trs == 't' and 'joint' in trgNode:
                        srcMotionPath = Nodes.replaceNodeType(srcNode, Settings.motionPathGuideSuffix)
                        trgMotionPath = Nodes.replaceNodeType(trgNode, Settings.motionPathGuideSuffix)
                        if mc.objExists(srcMotionPath) and mc.objExists(trgMotionPath):
                            fractionModeVal = mc.getAttr('%s.fractionMode'%srcMotionPath)
                            srcUVal = mc.getAttr('%s.uValue'%srcMotionPath)
                            mc.setAttr('%s.fractionMode'%trgMotionPath, fractionModeVal)
                            mc.setAttr('%s.curvePosition'%trgNode, srcUVal)

                attrList = None
                if (alignGuideGroupSettings and trgType == 'guide') or (alignShapeSettings and trgType != 'guide'):
                    attrList = mc.listAttr(trgNode, userDefined=True)
                if attrList != None:
                    for attr in attrList:
                        sourceAttr = '%s.%s' % (srcNode, attr)
                        if mc.objExists(sourceAttr):
                            targetAttr = '%s.%s' % (trgNode, attr)
                            if not mc.getAttr(sourceAttr, lock=True) and not mc.getAttr(targetAttr, lock=True):
                                attrType = mc.getAttr('%s.%s' % (srcNode, attr), type=True)
                                sourceValue = mc.getAttr('%s.%s' % (srcNode, attr))
                                if attrType == 'string':
                                    if sourceValue != None:
                                        if mc.listConnections(targetAttr, source=True, destination=False, plugs=True) == None:
                                            currentSide = Nodes.getSide(guideGroup)
                                            if Settings.leftSide in sourceValue.split('_') or Settings.rightSide in sourceValue.split('_'):
                                                # this is where we make the guide attr value mirroring
                                                sourceValue = Nodes.replaceSide(sourceValue, currentSide, byString=True)
                                            mc.setAttr(targetAttr, sourceValue, type='string')
                                elif attrType == 'enum':
                                    srcEnumList = mc.attributeQuery(attr, n=srcNode, listEnum=True)[0].split(':')
                                    trgEnumList = mc.attributeQuery(attr, n=trgNode, listEnum=True)[0].split(':')
                                    enumName = srcEnumList[sourceValue]
                                    targetValue = None
                                    for enumIndex in range(len(srcEnumList)):
                                        if enumIndex < len(trgEnumList)-1:
                                            if trgEnumList[enumIndex] == enumName:
                                                targetValue = enumIndex
                                    if targetValue != None:
                                        mc.setAttr(targetAttr, targetValue)
                                else:
                                    if not Nodes.isConnected(trgNode, customAttrName=attr):
                                        mc.setAttr(targetAttr, sourceValue)
                    
                if alignShapeSettings:
                    if guideType == 'pivotShape' and alignPivotPosition:
                        try:
                            srcCVs = srcNode.getCVs()
                            for c, cv in enumerate(srcCVs):
                                try:
                                    trgNode.setCV(index=c, pt=cv)
                                except:
                                    MessageHandling.warning('Guide CV not found: %s, %s'%(trgNode, cv))
                            mc.move(1, 0, 0, '%s.cv[*]' % trgNode, r=True, ws=True) # this is to refresh curve state
                            mc.move(-1, 0, 0, '%s.cv[*]' % trgNode, r=True, ws=True) # this is to refresh curve state
                        except:
                            pass
                            
                    if guideType == 'lattice':
                        divisions = srcNode.getDivisions()
                        for s in range(divisions[0]):
                            for t in range(divisions[1]):
                                for u in range(divisions[2]):
                                    srcPt = srcNode.point(s, t, u)
                                    for a, axis in enumerate('xyz'):
                                        mc.setAttr('%s.pt[%s][%s][%s].%sValue' % (trgNode, s, t, u, axis), srcPt[a])
                    
                    if guideType == 'nurbsSurface' and 'surfaceNode' in trgNode:
                        spans = mc.getAttr('%s.spansUV'%srcNode)[0]
                        for u in range(spans[0]+3):
                            for v in range(spans[1]+3):
                                srcPt = mc.getAttr('%s.cv[%s][%s]'%(srcNode, u, v))
                                try:
                                    mc.setAttr('%s.cv[%s][%s].xValue'%(trgNode, u, v), srcPt[0][0])
                                    mc.setAttr('%s.cv[%s][%s].yValue'%(trgNode, u, v), srcPt[0][1])
                                    mc.setAttr('%s.cv[%s][%s].zValue'%(trgNode, u, v), srcPt[0][2])
                                except:
                                    pass
                        # surface cvs for non-control guided, hard coded on 'surfaceNode', global scale
                        mc.scale(globalScaleValue, globalScaleValue, globalScaleValue, '%s.cv[0:*][0:*]'%trgNode)
                
                # shape appearance global scale and pivot shape match
                if Nodes.getShapeType(srcNode) == 'joint' and Nodes.getShapeType(trgNode) == 'joint':
                    mc.setAttr('%s.radius'%trgNode, mc.getAttr('%s.radius'%srcNode)*globalScaleValue)
                if Nodes.getShapeType(srcNode) == 'locator' and Nodes.getShapeType(trgNode) == 'locator':
                    for axis in 'XYZ':
                        mc.setAttr('%s.localScale%s'%(trgNode, axis), mc.getAttr('%s.localScale%s'%(srcNode, axis))*globalScaleValue)
                if guideType == 'pivotShape' and Nodes.getNodeType(trgNode) == Settings.guidePivotSuffix:
                    pivotInitialShapeSize = mc.getAttr('%s.pivotInitialShapeSize'%trgNode) if mc.objExists('%s.pivotInitialShapeSize'%trgNode) else 1
                    srcSize = mc.getAttr('%s.pivotShapeSize'%srcNode) if mc.objExists('%s.pivotShapeSize'%srcNode) else 1
                    convertedSize = (srcSize/pivotInitialShapeSize)*globalScaleValue
                    for shapeNode in mc.listRelatives(trgNode, shapes=True):
                        mc.scale(convertedSize, convertedSize, convertedSize, '%s.cv[*]'%shapeNode, os=True, r=True)
                    if mc.objExists('%s.pivotShapeSize'%trgNode):
                        mc.setAttr('%s.pivotShapeSize'%trgNode, srcSize*globalScaleValue)
        
        # reseting global scale
        for childNode in Nodes.getAllChildren(trgGuideRoot, includeRoot=True):
            if Nodes.getNodeType(childNode) == 'guide':
                globalScaleAttr = childNode+'.globalScale'
                if mc.objExists(globalScaleAttr):
                    if not mc.getAttr(globalScaleAttr, lock=True):
                        mc.setAttr(globalScaleAttr, 1)
            # hard fix for transform nodes auto-generated on joints
            if 'transform' in childNode:
                for axis in 'xyz':
                    mc.setAttr('%s.s%s'%(childNode, axis), 1)
                trsChildNodes = mc.listRelatives(childNode, children=True)
                if trsChildNodes:
                    for trsChild in trsChildNodes:
                        Nodes.setParent(trsChild, Nodes.getParent(childNode))
                mc.delete(childNode)
                
        return self.guideFile

    def rigSettings(self, selection=None):
        
        Files.Config(self.projectFolder,
                    self.assetFolder,
                    fileType=Settings.rigSettingsFileIndicator,
                    version=self.versionName,
                    selection=selection).loadRigSettings(self.rigSettingsFolder)
        
    def skin(self, 
                nodeList=[], 
                applyJoints=True, 
                byVertexPosition=False, 
                byUVs=False, 
                byVertexID=True,
                loadSkin=True,
                loadLattice=True,
                loadSmooth=True,
                loadProxWrap=True, 
                loadGeometryConstraints=True,
                loadInputOrder=True,
                excludeNodes=[]):

        if self.skinFile == None:
            return

        # we store the current pose values
        #vals = Tools.setPose()

        # we reset all parent matrices
        #for controlNode in [x for x in mc.ls(type='transform') if Nodes.getNodeType(x) == Settings.controlSuffix]:
            #Nodes.setOffsetParentMatrix(controlNode)
        
        if any([loadSkin, loadLattice, loadSmooth, loadProxWrap, loadGeometryConstraints]):
            if not mc.file(self.skinFile, q=True, exists=True):
                mc.error(f"Deform file does not exist: {self.skinFile}")
            if not self.skinFile in mc.file(reference=True, q=True):
                mc.file(self.skinFile, r=True, namespace=self.skinRefPrefix, ignoreVersion=True)

        for topNode in mc.ls(assemblies=True):
            if self.skinRefPrefix+':' in topNode:
                mc.hide(topNode)
        
        # nodes collection
        if nodeList == []:
            if self.geometryRoot:
                for geometryRoot in self.geometryRoot:
                    if mc.objExists(geometryRoot):
                        nodeList.extend(Nodes.getAllChildren(geometryRoot, includeRoot=True, fullPath=True))
            if self.rigRoot:
                nodeList.extend([x for x in Nodes.getAllChildren(self.rigRoot, fullPath=True) if x.endswith(Settings.templateSuffix) \
                                                                                            or x.endswith(Settings.templateNode) \
                                                                                            or x.endswith(Settings.latticeNodeSuffix) \
                                                                                            or x.endswith(Settings.skinnedGeoSuffix) \
                                                                                            or x.endswith(Settings.skinMeshSuffix) \
                                                                                            or x.endswith(Settings.deformNodeSuffix) \
                                                                                            or x.endswith(Settings.skinMeshTransferSuffix) \
                                                                                            or x.endswith(Settings.deformNodeSuffix) \
                                                                                            or x.endswith(Settings.inverseNodeSuffix) \
                                                                                            or x.endswith(Settings.squashStretchMeshSuffix)])
            
            # skin meshes

            skmSrcList = mc.ls(self.skinRefPrefix+':*_'+Settings.skinMeshSuffix, type='transform')+mc.ls(self.skinRefPrefix+':*_'+Settings.skinMeshTransferSuffix, type='transform')
            if skmSrcList:
                if not Nodes.exists(Settings.skinMeshesGroup):
                    mc.group(name=Settings.skinMeshesGroup, empty=True)
                    Nodes.setParent(Settings.skinMeshesGroup, Settings.rigRoot)
            for skmSrc in skmSrcList:
                skmSrcParent = mc.pickWalk(skmSrc, d='up')[0]
                skmTrgParent = skmSrcParent.split(self.skinRefPrefix+':')[1]
                if not mc.objExists(skmTrgParent):
                    skmTrgParent = mc.group(name=skmTrgParent, empty=True)
                    Nodes.setParent(skmTrgParent, self.assetNode)
                if not mc.objExists(skmSrc.split(self.skinRefPrefix+':')[1]):
                    srcSkinCluster = Nodes.getSkinCluster(skmSrc)[0]
                    if srcSkinCluster:
                        mc.setAttr(srcSkinCluster+'.envelope', 0)
                    skmTrg = mc.duplicate(skmSrc)[0]
                    shapeList = mc.listRelatives(skmTrg, shapes=True)
                    if shapeList:
                        for shapeNode in shapeList:
                            mc.select(shapeNode)
                            mc.hyperShade(a='lambert1')
                    Nodes.setParent(skmTrg, skmTrgParent)
                    nodeList.append(skmTrg)
            Nodes.hide(Settings.skinMeshesGroup)
        
        # load skinning
        for node in nodeList:
            nodeSplit = node.split('|')
            if '' in nodeSplit:
                nodeSplit.remove('')
            if '|' in node:
                refPrefixNode = '|'.join([self.skinRefPrefix+':'+x for x in nodeSplit])
                if not mc.objExists(refPrefixNode):
                    refPrefixNode = self.skinRefPrefix+':'+nodeSplit[-1]
            else:
                refPrefixNode = self.skinRefPrefix+':'+node
            refNodeList = mc.ls(refPrefixNode)
            trgNodeList = mc.ls(node)
            if trgNodeList == []:
                MessageHandling.warning('target node not found, skipped: %s' % node)
                
            if refNodeList != [] and trgNodeList != []:

                refNode = refNodeList[0]
                trgNode = trgNodeList[0]

                refUVSet = 'map1'
                trgUVSet = 'map1'

                # we are reseting offset parent matrix for any post deform values applied
                Nodes.setOffsetParentMatrix(trgNode)
                
                if not trgNode in excludeNodes:
                    
                    # uv set transfer
                    if mc.objectType(node) == 'mesh':
                        refUVSets = mc.polyUVSet(refNode, allUVSets=True, q=True)
                        trgUVSets = mc.polyUVSet(trgNode, allUVSets=True, q=True)
                        refUVSet = refUVSets[0]
                        trgUVSet = trgUVSets[0]

                    # input order
                    refInputNodes = list()
                    refHistory = mc.listHistory(refNode, gl=True, pdo=True)
                    if refHistory:
                        for inputNode in refHistory:
                            if mc.objectType(inputNode) == 'tweak':
                                break
                            refInputNodes.append(inputNode)

                    for refInputNode in refInputNodes:
                        
                        trgInputNode = refInputNode.replace(self.skinRefPrefix+':', '')
                        
                        if mc.objectType(refInputNode) == 'skinCluster' and loadSkin and Nodes.getObjectType(trgNode) == 'mesh':
                            
                            refSkinClusterNode = refInputNode

                            skinMethod = mc.getAttr('%s.skinningMethod' % refInputNode)
                            
                            trgSkinClusterNode = Nodes.getSkinCluster(trgNode)[0]

                            deformTweakSkinCluster = False
                            deformTweakAttrVals = None
                            if refSkinClusterNode != None:
                                if 'deformTweak' in refSkinClusterNode:
                                    deformTweakSkinCluster = True
                                    deformTweakAttrVals = DeformTweak.getCompAttrs(trgNode)
                                if trgSkinClusterNode != None:
                                    mc.delete(trgSkinClusterNode)
                                trgSkinClusterNode = None
                                    
                            if refSkinClusterNode != None:
                                normalizeWeights = mc.getAttr('%s.normalizeWeights' % refSkinClusterNode)
                                mc.setAttr(refSkinClusterNode+'.envelope', 0)

                            if applyJoints and refSkinClusterNode != None and trgSkinClusterNode == None:
                                
                                refSkinJointList = mc.skinCluster(refSkinClusterNode, inf=True, q=True)
                                skinJointList = [x[len(self.skinRefPrefix)+1:] for x in refSkinJointList]
                                
                                if len(refSkinJointList) != len(skinJointList):
                                    MessageHandling.warning("Joint count doesn't match the reference, skin transfer might not succeed as expected: %s" % trgNode)

                                trgSkinJointList = []
                                jointIA = 'label'
                                for skinJoint in skinJointList:
                                    trgSkinJoint = Tools.getNodeByName(skinJoint, getRef=False)
                                    if trgSkinJoint != None:
                                        trgSkinJointList.append(trgSkinJoint)
                                        jointType = mc.getAttr('%s.type'%trgSkinJoint)
                                        if jointType == 0:
                                            jointIA = 'closestJoint'
                                            MessageHandling.warning('joint has no label: %s' % skinJoint)
                                    else:
                                        MessageHandling.warning('target skin joint node not found, skipped: %s' % skinJoint)
                                
                                if trgSkinJointList != []:
                                    trgSkinClusterNode = mc.skinCluster(trgSkinJointList, trgNode, name=trgInputNode, toSelectedBones=True)[0]
                                    if deformTweakSkinCluster:
                                        DeformTweak.connectBindPreMatrix(trgSkinJointList, trgSkinClusterNode, 0)
                                        if deformTweakAttrVals:
                                            DeformTweak.createBlendshape(*[trgNode]+deformTweakAttrVals)
                                        DeformTweak.addCompAttrs(*[trgNode]+deformTweakAttrVals)
                                else:
                                    trgSkinClusterNode = None
                            
                            if trgSkinClusterNode != None and refSkinClusterNode != None and not 'lattice' in trgNode:

                                mc.setAttr('%s.normalizeWeights' % trgSkinClusterNode, normalizeWeights)                        
                                mc.select([refNode, trgNode])
                                refVertexCount = mc.polyEvaluate(refNode, v=True)
                                trgVertexCount = mc.polyEvaluate(trgNode, v=True)
                                
                                if byUVs:

                                    mc.copySkinWeights(ia=jointIA, uv=(refUVSet, trgUVSet), sa='closestPoint', sm=True, nm=True)

                                if byVertexID:

                                    if refVertexCount != trgVertexCount:
                                        MessageHandling.warning("Vertex count doesn't match the reference, using vertex position transfer method: %s" % trgNode)
                                        byVertexPosition = True
                                    else:
                                        Weights.SkinTransfer(refNode, trgNode).transferWeights()

                                if byVertexPosition:
                                    
                                    mc.select([refNode, trgNode])
                                    mc.copySkinWeights(ia=jointIA, sa='closestPoint', sm=True, nm=True)
            
                                mc.setAttr('%s.skinningMethod' % trgSkinClusterNode, skinMethod)

                        if mc.objectType(refInputNode) == 'ffd' and loadLattice:

                            trgFfdNode = refInputNode.split(self.skinRefPrefix+':')[-1]
                            if not mc.objExists(trgFfdNode):
                                MessageHandling.warning('Target lattice node does not exist, weight transfer skipped: %s, %s' % (trgNode, trgFfdNode))
                            else:
                                Weights.DeformerTransfer(sourceDeformerNode=refInputNode,
                                                            targetDeformerNode=trgFfdNode,
                                                            targetGeo=trgNode,
                                                            deformerType='ffd').transferWeights()
                        
                        if mc.objectType(refInputNode) == 'deltaMush' and loadSmooth:
                            refMushAttrVals = list()
                            for attr in mc.listAttr(refInputNode, cb=True):
                                if 'componentTagExpression' in attr: # this needs to be skipped or error occurs
                                    continue
                                refMushAttrVals.append(mc.getAttr('%s.%s'%(refInputNode, attr)))
                            Nodes.delete(trgInputNode)
                            trgMushNode = mc.deltaMush(trgNode, name=trgInputNode)[0]
                            for x, attr in enumerate([n for n in mc.listAttr(refInputNode, cb=True) if not 'componentTagExpression' in n]):
                                mc.setAttr('%s.%s'%(trgMushNode, attr), refMushAttrVals[x])

                            Weights.DeformerTransfer(sourceDeformerNode=refInputNode,
                                                        targetDeformerNode=trgMushNode,
                                                        targetGeo=trgNode,
                                                        deformerType='deltaMush').transferWeights()
                        
                        if mc.objectType(refInputNode) == 'tension' and loadSmooth:
                            refTensionAttrVals = list()
                            for attr in mc.listAttr(refInputNode, cb=True):
                                if 'componentTagExpression' in attr: # this needs to be skipped or error occurs
                                    continue
                                refTensionAttrVals.append(mc.getAttr('%s.%s'%(refInputNode, attr)))
                            Nodes.delete(trgInputNode)
                            trgMushNode = mc.tension(trgNode, name=trgInputNode)[0]
                            for x, attr in enumerate([n for n in mc.listAttr(refInputNode, cb=True) if not 'componentTagExpression' in n]):
                                mc.setAttr('%s.%s'%(trgMushNode, attr), refTensionAttrVals[x])

                            Weights.DeformerTransfer(sourceDeformerNode=refInputNode,
                                                        targetDeformerNode=trgMushNode,
                                                        targetGeo=trgNode,
                                                        deformerType='tension').transferWeights()
                    
                        if mc.objectType(refInputNode) == 'proximityWrap' and loadProxWrap:
                            refWrapShape = mc.listConnections(refInputNode, shapes=True)[-1]
                            refWrapGeoNode = Nodes.getTransformNode(refWrapShape)
                            if refWrapGeoNode:
                                trgWrapGeoNode = refWrapGeoNode[len(self.skinRefPrefix+':'):]
                                plugs = mc.listConnections('%s.originalGeometry'%refInputNode, plugs=True)
                                if plugs:
                                    trgDrivenGeoNodes = list()
                                    for plug in plugs:
                                        refDrivenOrigShape = plug.split('.')[0]
                                        refDrivenGeoNode = Nodes.getTransformNode(refDrivenOrigShape)
                                        trgDrivenGeoNode = refDrivenGeoNode[len(self.skinRefPrefix+':'):]
                                        trgDrivenGeoNodes.append(trgDrivenGeoNode)
                                # we check if deformer has already been applied to avoid duplicate deformers
                                pxwDeformer = trgWrapGeoNode + '_' + Settings.proximityWrapSuffix
                                Nodes.delete(pxwDeformer)
                                if mc.objExists(trgWrapGeoNode) and any([mc.objExists(x) for x in trgDrivenGeoNodes]):
                                    Nodes.proximityWrap(trgWrapGeoNode, trgDrivenGeoNodes)

                        if mc.objectType(refInputNode) == 'wrap' and loadProxWrap:

                            refWrapGeoNode = mc.listConnections(refInputNode, type='transform')[0]
                            refExclBindVal = mc.getAttr('%s.exclusiveBind'%refInputNode)
                            trgWrapGeoNode = refWrapGeoNode[len(self.skinRefPrefix+':'):]
                            if mc.objExists(trgWrapGeoNode):
                                mc.select(trgNode, trgWrapGeoNode)
                                trgWrapNode = Nodes.getInputNodes(trgNode, inputType='wrap')[0][0]
                                Nodes.delete(trgWrapNode)
                                mc.CreateWrap()
                                trgParent = Nodes.getParent(trgNode)
                                baseGeos = mc.ls(trgWrapGeoNode+'Base*', type='transform')
                                for baseGeo in baseGeos:
                                    Nodes.setParent(baseGeo, trgParent)
                                trgWrapNode = Nodes.getInputNodes(trgNode, inputType='wrap')[0][0]
                                mc.setAttr('%s.exclusiveBind'%trgWrapNode, refExclBindVal)
                        
                    # input order
                    for r, refInputNode in enumerate(refInputNodes[:-1]):
                        trgInputNodes = list()
                        inputNodes = mc.listHistory(trgNode, gl=True, pdo=True)
                        if not inputNodes:
                            continue
                        for inputNode in inputNodes:
                            if mc.objectType(inputNode) == 'tweak':
                                break
                            trgInputNodes.append(inputNode)
                        trgInputNode = refInputNode.replace(self.skinRefPrefix+':', '')
                        nextRefInput = refInputNodes[r+1]
                        nextTrgInput = nextRefInput.replace(self.skinRefPrefix+':', '')
                        if mc.objExists(trgInputNode) and mc.objExists(nextTrgInput):
                            #nextIndex = trgInputNodes.index(nextTrgInput)
                            #if len(trgInputNodes)-1 > nextIndex:
                                #if nextTrgInput != trgInputNodes[nextIndex]:
                            # NOTE need to sort this out to avoid redundant script messages
                            try:
                                mc.scriptEditorInfo(suppressWarnings=True)
                                mc.reorderDeformers(trgInputNode, nextTrgInput, trgNode)
                                mc.scriptEditorInfo(suppressWarnings=False)
                            except:
                                pass
                    
                    # parent scale constraint
                    if loadGeometryConstraints:
                        pntCnt = None
                        trgParentNode = None
                        conNodes = mc.listConnections(refNode)
                        if not conNodes:
                            continue
                        for conNode in conNodes:
                            if mc.objectType(conNode) == 'parentConstraint':
                                pntCnt = conNode
                                break
                        if pntCnt:
                            refParentNode = mc.parentConstraint(pntCnt, targetList=True, q=True)[0]
                            trgParentNode = refParentNode[len(self.skinRefPrefix)+1:]
                        conNodes = mc.listConnections(trgNode)
                        if conNodes:
                            for conNode in conNodes:
                                if not mc.objExists(conNode):
                                    continue
                                if mc.objectType(conNode) == 'parentConstraint' or mc.objectType(conNode) == 'scaleConstraint':
                                    Nodes.delete(conNode)
                        if trgParentNode:
                            if mc.objExists(trgParentNode) and mc.objExists(trgNode) and trgParentNode != trgNode:
                                constraintOutput = Tools.parentScaleConstraint(trgParentNode, trgNode, useMatrix=False)
                                if constraintOutput:
                                    if not mc.objExists(Settings.deformConstraintsGroup):
                                        AddNode.emptyNode(nodeType=Settings.deformConstraintsGroup, parentNode=self.rigRoot)
                                        mc.hide(Settings.deformConstraintsGroup)
                                    for cntNode in constraintOutput:
                                        Nodes.setParent(cntNode, Settings.deformConstraintsGroup)

        if loadInputOrder:
            self.inputOrder()

        # recover pose
        #Tools.setPose(vals)

        return self.skinFile

    def inputOrder(self):
        
        Files.Config(self.projectFolder,
                    self.assetFolder,
                    fileType=Settings.inputOrderFileIndicator,
                    version=self.versionName).loadInputOrder(self.inputOrderFolder)
        
    def postDeform(self):
        
        Files.Config(self.projectFolder,
                    self.assetFolder,
                    fileType=Settings.controlTransformsFileIndicator,
                    version=self.versionName).loadControlTransforms(self.controlTransformsFolder)

    def blendshapes(self):

        if self.blendshapesFile == None:
            return
        if mc.objExists(self.poseCorrectionsRoot):
            Nodes.setParent(self.faceBlendshapesRoot, 'world')
            mc.delete(self.poseCorrectionsRoot)

        mc.file(self.blendshapesFile, r=True, mergeNamespacesOnClash=True, namespace=':', ignoreVersion=True)
        mc.file(self.blendshapesFile, importReference=True, ignoreVersion=True)

        Nodes.setParent(self.faceBlendshapesRoot, self.poseCorrectionsRoot)
        Nodes.setParent(self.poseCorrectionsRoot, self.assetNode)
        if mc.objExists(self.poseCorrectionsRoot):
            mc.hide(self.poseCorrectionsRoot)