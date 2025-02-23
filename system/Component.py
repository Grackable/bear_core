# Component

import maya.cmds as mc
import os, sys, imp

from bear.system import Settings
from bear.system import ConnectionHandling
from bear.system import MessageHandling
from bear.system import DataStructure
from bear.system import Guiding
from bear.utilities import Nodes

class Build(object):
    
    def __init__(self, 
                    module=None, 
                    name=None, 
                    side=None, 
                    buildStep=None, 
                    versionName=None, 
                    assetFolder=None, 
                    customFile=None,
                    removeRef=False,
                    alignGuideGroupSettings=True,
                    alignGuidePositions=True,
                    alignGuideOrientations=True,
                    alignGuideShapeSettings=True,
                    alignGuideShapeTransforms=True,
                    definition=False,
                    *args, **kwargs):

        self.module = module
        self.name = name
        self.side = side
        self.buildStep = buildStep
        self.versionName = versionName
        self.assetFolder = assetFolder
        self.customFile = customFile
        self.removeRef = removeRef
        self.alignGuideGroupSettings = alignGuideGroupSettings
        self.alignGuidePositions = alignGuidePositions
        self.alignGuideOrientations = alignGuideOrientations
        self.alignGuideShapeSettings = alignGuideShapeSettings
        self.alignGuideShapeTransforms = alignGuideShapeTransforms
        self.definition = definition
        
    def createByCompGroup(self, compGroup):
        
        comp = None
        
        if not mc.objExists(compGroup+'.componentType'):
            return None

        if self.buildStep == None:
            self.buildStep = Nodes.getNodeType(compGroup)
        guideGroup = Nodes.replaceNodeType(compGroup, 'guide')
        compAttr = guideGroup+'.componentType'
        if not mc.objExists(compAttr):
            MessageHandling.noSelectedComponent(compGroup)
        else:
            moduleName = mc.getAttr(compAttr)
            modulePath = None
            for m in sys.modules:
                if '.'+moduleName in m or m == moduleName:
                    modulePath = m
                    break
            if modulePath:
                self.module = sys.modules[modulePath]
                self.name = mc.getAttr(guideGroup+'.name')
                comp = self.create(compGroup)
        
        if Nodes.getComponentType(compGroup) == 'Script':
            customScript(self.buildStep, compGroup)

        return comp

    def applyBuildAttrs(self, buildAttrs, guideGroup, rigType):
        
        allAttrs = ConnectionHandling.getAllComponentAttrs(guideGroup, rigType)[0]
        
        for buildAttr in buildAttrs:
            defaultVal = str(buildAttrs[buildAttr]).replace("'", "").replace("[", "").replace("]", "")
            
            if buildAttr == 'name':
                defaultVal = self.name
            elif guideGroup in allAttrs:
                if buildAttr in allAttrs[guideGroup]:
                    defaultVal = allAttrs[guideGroup][buildAttr]
            else:
                defaultVal = str(buildAttrs[buildAttr]).replace("'", "").replace("[", "").replace("]", "")
            if buildAttr == 'side' and self.side != None:
                defaultVal = self.side
            
            buildAttrName = str(buildAttr)

            if buildAttr == 'side':
                Nodes.addAttr(guideGroup+'.'+buildAttrName, at='string')
                mc.setAttr(guideGroup+'.'+buildAttrName, lock=False)
                mc.setAttr(guideGroup+'.'+buildAttrName, defaultVal, type='string')
                mc.setAttr(guideGroup+'.'+buildAttrName, lock=True)
            elif mc.objExists(guideGroup+'.'+buildAttrName):
                mc.setAttr(guideGroup+'.'+buildAttrName, defaultVal)
            else:
                mc.addAttr(guideGroup, dt='string', ln=buildAttrName)
                mc.setAttr(guideGroup+'.'+buildAttrName, defaultVal, type='string')

    def create(self, compGroup=None, attrs=None):

        if self.module != None:

            buildAttrs = DataStructure.getSignature(self.module)
            buildAttrsList = DataStructure.getSignature(self.module, asList=True)

            for buildAttr in buildAttrs:
                if buildAttr == 'name':
                    if self.name == None:
                        self.name = buildAttrs[buildAttr]
                if buildAttr == 'side':
                    buildAttrs[buildAttr] = self.side
                # attrs (dict) allows defining individual default build values, for example for parent nodes for muscles in biped or quadruped
                if attrs != None:
                    if buildAttr in attrs.keys():
                        buildAttrs[buildAttr] = attrs[buildAttr]

            compName = self.name
        else:
            compName = None

        if self.buildStep == 'model':
            
            DataStructure.Asset(assetFolder=self.assetFolder,
                                customFile=self.customFile,
                                versionName=self.versionName).model()

        if self.buildStep == 'definition':

            guideGroup = Nodes.createName(component=compName, side=self.side, nodeType='guide')[0]
            if not MessageHandling.uniqueName(guideGroup, guideGroup):
                return
            
            guide = self.module.Build(name=self.name, side=self.side).createGuide(definition=True)
            guideGroup = None if guide == None else guide['guideGroup']
            
            mc.addAttr(guideGroup, dt='string', ln='componentType')
            mc.setAttr(guideGroup+'.componentType', self.module.__name__.split('.')[-1], type='string', lock=True)
            
            self.applyBuildAttrs(buildAttrs, guideGroup, 'guide')
            
            mc.select(clear=True)

            return guideGroup

        if self.buildStep == 'guide':

            if compName == None:
                return

            # we get the transforms of the guide group in order to support preserving them on rebuild if no guide controls are created
            buildTransforms = Nodes.getTrs(compGroup) if compGroup else None
            
            isCollection = False
            if compGroup != None:
                compAttr = '%s.componentType'%compGroup
                if mc.objExists(compAttr):
                    isCollection = True if mc.getAttr(compAttr) == 'Collection' else False
            
            oldName = Nodes.getComponent(compGroup)
            compSide = Nodes.getSide(compGroup)
            
            allAttrs, tempFile, compParent, orderIndex, subComponents, oldLimbRig = ConnectionHandling.recreateComponent(compName, 
                                                                                                            self.side,
                                                                                                            'guide', 
                                                                                                            compGroup,
                                                                                                            definition=self.definition)
            
            if compSide != self.side and orderIndex != None:
                orderIndex += 1
            
            # if we build a new side from a non-side component, we delete the original component
            if compGroup != None:
                if mc.objExists(compGroup) and compSide == None and self.side != None:
                    mc.delete(compGroup)

            if isCollection:
                guide = self.module.Build(name=self.name, side=self.side).createGuide(definition=True,
                                                                                        subComponents=subComponents, 
                                                                                        allAttrs=allAttrs)
            else:
                guide = self.module.Build(name=self.name, side=self.side).createGuide(definition=True)
            
            guideGroup = None if guide == None else guide['guideGroup']
            Nodes.setParent(guideGroup, compParent)
            Nodes.putInOrder(guideGroup, orderIndex)
            
            if not mc.objExists(guideGroup+'.componentType'):
                mc.addAttr(guideGroup, dt='string', ln='componentType')
                mc.setAttr(guideGroup+'.componentType', self.module.__name__.split('.')[-1], type='string', lock=True)
                self.applyBuildAttrs(buildAttrs, guideGroup, 'guide')

            def setBuildAttr(defaultVal, buildAttr, subGroup):
                if defaultVal != None:
                    buildAttrName = str(buildAttr)
                    buildAttr = subGroup+'.'+buildAttrName
                    buildAttr = Nodes.replaceSide(buildAttr, self.side, byString=True)
                    subGroup = Nodes.replaceSide(subGroup, self.side, byString=True)
                    if type(defaultVal) == str:
                        # NOTE special treatment for mgear side naming convention
                        if '_L0_' in defaultVal and self.side == Settings.rightSide:
                            defaultVal = defaultVal.replace('_L0_', '_R0_')
                        if '_R0_' in defaultVal and self.side == Settings.leftSide:
                            defaultVal = defaultVal.replace('_R0_', '_L0_')
                        if Settings.leftSide in defaultVal.split('_') or Settings.rightSide in defaultVal.split('_'):
                            # this is where we make the guide attr value mirroring
                            defaultVal = Nodes.replaceSide(defaultVal, self.side, byString=True)
                    if mc.objExists(buildAttr):
                        if Nodes.isAttrSettable(buildAttr):
                            if mc.attributeQuery(buildAttrName, node=subGroup, attributeType=True) == 'typed':
                                mc.setAttr(buildAttr, defaultVal, type='string')
                            else:
                                mc.setAttr(buildAttr, defaultVal)

            def setAllBuildAttrs():
                for subGroup in allAttrs.keys():
                    if subGroup == guideGroup:
                        for buildAttr in buildAttrs:
                            if buildAttr == 'name':
                                defaultVal = self.name
                            elif buildAttr in allAttrs[subGroup]:
                                defaultVal = allAttrs[subGroup][buildAttr]
                                if buildAttr == 'name':
                                    self.name = defaultVal
                                elif buildAttr == 'side' and self.side:
                                    defaultVal = self.side
                                else:
                                    defaultVal = str(allAttrs[subGroup][buildAttr]).replace("'", "").replace("[", "").replace("]", "")
                            else:
                                defaultVal = None
                            if defaultVal != None:
                                setBuildAttr(defaultVal, buildAttr, subGroup)
                    else:
                        for buildAttr in allAttrs[subGroup]:
                            if buildAttr in allAttrs[subGroup]:
                                defaultVal = allAttrs[subGroup][buildAttr]
                                setBuildAttr(defaultVal, buildAttr, subGroup)
                            
                        subCompAttr = subGroup+'.componentType'
                        if mc.objExists(subCompAttr):
                            subModuleName = mc.getAttr(subCompAttr)
                            subModule = sys.modules[subModuleName]
                            subBuildAttrs = DataStructure.getSignature(subModule)

                            for buildAttr in subBuildAttrs:
                                if not buildAttr in allAttrs[subGroup]:
                                    defaultVal = str(subBuildAttrs[buildAttr]).replace("'", "").replace("[", "").replace("]", "")
                                    setBuildAttr(defaultVal, buildAttr, subGroup)
            
            setAllBuildAttrs()
            
            buildAttrs = Guiding.getBuildAttrs(guideGroup)
            buildVals = Guiding.getBuildValues(buildAttrs, buildAttrsList, self.side)+[oldLimbRig]

            if self.definition:
                # we apply the build transforms that were retrieved earlier
                if buildTransforms and guideGroup:
                    Nodes.setTrs(guideGroup, trsVal=buildTransforms)
                return guideGroup
            
            if isCollection:
                guide = self.module.Build(*buildVals).createGuide(subComponents=subComponents, 
                                                                    allAttrs=allAttrs)
            else:
                guide = self.module.Build(*buildVals).createGuide()
            guideGroup = None if guide == None else guide['guideGroup']
            if guideGroup == None:
                return
            
            if mc.objExists('%s.globalScale'%guideGroup):
                mc.setAttr('%s.globalScale'%guideGroup, lock=False)

            # allowing guide root global scale if all components and modules are built
            if mc.objExists('%s.globalScale'%Settings.guideRoot):
                readyForRigBuild = True
                for node in Nodes.getAllChildren(Settings.guideRoot, nodeType=Settings.guideGroup):
                    if mc.objExists('%s.readyForRigBuild'%node):
                        if not mc.getAttr('%s.readyForRigBuild'%node):
                            readyForRigBuild = False
                if readyForRigBuild:
                    mc.setAttr('%s.globalScale'%Settings.guideRoot, lock=False)

            # NOTE This is causing guide side mirror values to not process correctly
            # we want to avoid recreating the ref file on every component build, so we check for tempFile
            if tempFile != None:
                if isCollection:
                    getFromSide = False if compGroup == None else compSide
                else:
                    getFromSide = False if compGroup == None else ('remove' if compSide == None else compSide)
                    # exception for some face modules since they have side building included
                    if Nodes.componentIsAutoSided(guideGroup):
                        getFromSide = None
                guideFile = DataStructure.Asset(loadFromFile=tempFile).guideSettings(guideGroup, 
                                                                                    getFromSide=getFromSide,
                                                                                    oldName=oldName,
                                                                                    newName=compName)
                                                                                    
                if guideFile in mc.file(reference=True, q=True):
                    mc.file(guideFile, removeReference=True)
                try:
                    os.remove(tempFile)
                except:
                    pass

            # exception for addToExisting
            if Nodes.getComponentType(guideGroup) == 'DeformTweak':
                currentSide = Nodes.getSide(guideGroup)
                mirAttrHolder = None
                if currentSide == Settings.leftSide:
                    mirAttrHolder = Nodes.replaceSide(guideGroup, Settings.rightSide)
                if currentSide == Settings.rightSide:
                    mirAttrHolder = Nodes.replaceSide(guideGroup, Settings.leftSide)
                if Nodes.exists(mirAttrHolder) and currentSide != compSide:
                    mc.setAttr('%s.addToExisting'%guideGroup, 'True', type='string')
            
            # mirror guide
            if compGroup != None:
                if (compSide != self.side and compSide) or (compSide == None and self.side == Settings.rightSide):
                    Guiding.mirrorGuide(guideGroup)
            
            # re-establishing connections needs to be done after complete guide build as output attrs are created there
            #ConnectionHandling.inputOutput(allAttrs)

            #setAllBuildAttrs()

            if mc.objExists(Settings.guideRoot) and Settings.loadSettings()[0]['showGuideAfterGuideBuild']:
                mc.showHidden(Settings.guideRoot)
                
            MessageHandling.printRigHierarchy(compName, guide, Nodes.getSide(guideGroup), 'guide')

            mc.select(clear=True)

            return guideGroup

        if self.buildStep == 'guideSettings':
            
            guideGroup = Nodes.createName(compName, self.side, 'guide')[0]
            guideFile = None
            if mc.objExists(guideGroup):
                guideFile = DataStructure.Asset(assetFolder=self.assetFolder,
                                                versionName=self.versionName).guideSettings(guideGroup,
                                                                                            alignGuideGroupSettings=self.alignGuideGroupSettings,
                                                                                            alignPivotPosition=self.alignGuidePositions,
                                                                                            alignPivotRotation=self.alignGuideOrientations,
                                                                                            alignShapeSettings=self.alignGuideShapeSettings,
                                                                                            alignShapeTransforms=self.alignGuideShapeTransforms)

            if mc.objExists(Settings.guideRoot) and Settings.loadSettings()[0]['showGuideAfterGuideBuild']:
                mc.showHidden(Settings.guideRoot)

            return guideFile

        if self.buildStep == 'rig':

            guideGroup = Nodes.createName(compName, self.side, 'guide')[0]
            if not MessageHandling.hasGuide(guideGroup, guideGroup):
                return
            
            isCollection = False
            compAttr = '%s.componentType'%guideGroup
            if mc.objExists(compAttr):
                isCollection = True if mc.getAttr(compAttr) == 'Collection' else False

            allAttrs, tempFile, compParent, orderIndex, subComponents, oldLimbRig = ConnectionHandling.recreateComponent(compName, 
                                                                                                            self.side,
                                                                                                            'rig', 
                                                                                                            guideGroup)
            
            buildAttrs = Guiding.getBuildAttrs(guideGroup)
            buildVals = Guiding.getBuildValues(buildAttrs, buildAttrsList, self.side)
            
            if isCollection:
                rig = self.module.Build(*buildVals).createRig(subComponents, allAttrs)
            else:
                rig = self.module.Build(*buildVals).createRig()
            
            self.module.Build(*buildVals).postRig(guideGroup)
            
            if not rig:
                return
            
            rigGroup = rig['rigGroup']
            if not rigGroup:
                return
            rigParent = Nodes.replaceNodeType(compParent, 'rig')
            if mc.objExists(rigParent):
                Nodes.setParent(rigGroup, rigParent)
                Nodes.putInOrder(rigGroup, orderIndex)
            if not mc.objExists(rigGroup+'.componentType'):
                mc.addAttr(rigGroup, dt='string', ln='componentType')
                mc.setAttr(rigGroup+'.componentType', self.module.__name__.split('.')[-1], type='string', lock=True)

            # connect global scale
            if isCollection:
                mc.setAttr('%s.globalScale'%rigGroup, lock=True)
            else:
                # we expect to have only one root component in the scene
                rootCompGroup = Nodes.getNodeByCompType('Root', nodeType=Settings.rigGroup)
                if rootCompGroup:
                    rootControl = Nodes.createName(Nodes.getComponent(rootCompGroup), nodeType=Settings.controlSuffix)[0]
                    rootGlobalScaleAttr = '%s.globalScale'%rootControl
                    rigGlobalScaleAttr = '%s.globalScale'%rigGroup
                    if mc.objExists(rootGlobalScaleAttr) and mc.objExists(rigGlobalScaleAttr):
                        mc.connectAttr(rootGlobalScaleAttr, rigGlobalScaleAttr)
                
            MessageHandling.printRigHierarchy(compName, rig, self.side, 'rig')

            mc.select(clear=True)

            return rig

        if self.buildStep == 'rigSettings':
            
            rigGroup = Nodes.createName(compName, self.side, 'rig')[0]
            
            setupFile = DataStructure.Asset(assetFolder=self.assetFolder,
                                            versionName=self.versionName).rigSettings()

            return setupFile
       
def customScript(buildStep=None, 
                 compGroup=None, 
                 forceRun=False, 
                 modelEnabled=False, 
                 guideEnabled=False, 
                 rigEnabled=False, 
                 postDeformEnabled=False):
    
    # global scripts
    loadedSettings = Settings.loadSettings()[0]
    if loadedSettings['enableScriptExecution'] or forceRun:
        for s, scriptFileName in enumerate([loadedSettings['modelScript'],
                                loadedSettings['guideScript'],
                                loadedSettings['rigScript'],
                                loadedSettings['postDeformScript'],
                                loadedSettings['deliveryScript']]):
            if scriptFileName == '':
                continue
            enabled = [modelEnabled and buildStep == 'model', 
                       guideEnabled and buildStep == 'guide', 
                       rigEnabled and buildStep == 'rig', 
                       postDeformEnabled and buildStep == 'postDeform',  
                       buildStep == 'delivery'][s]
            if not enabled:
                continue
            filePath = loadedSettings['globalScriptsFolder']+'/'+scriptFileName
            if MessageHandling.fileExists(filePath):
                scriptModule = imp.load_source('scriptModule', filePath)
                print('\nGlobal Script %s executed'%(filePath.split('/')[-1]))

        if buildStep == 'delivery':
            return True

    # script components
    if not Nodes.exists(Settings.guideRoot):
        return
    
    if compGroup:
        guideGroup = Nodes.replaceNodeType(compGroup, Settings.guideGroup)
    else:
        guideGroup = None

    fileLocation = mc.file(location=True, q=True)
    if fileLocation == 'unknown':
        setupFile = DataStructure.Asset().setupFile
        if setupFile:
            assetPath = '/'.join(setupFile.split('/')[:-1])
        else:
            assetPath = None
    else:
        assetPath = '/'.join(fileLocation.split('/')[:-1])
    if not assetPath:
        return
    
    globalRun = buildStep != 'guide' and buildStep != 'rig'
    
    if globalRun:
        guideGroups = Nodes.getChildren(Settings.guideRoot)
        scriptNodes = [x for x in guideGroups if Nodes.getComponentType(x) == 'Script']
        if not scriptNodes:
            return
    else:
        scriptNodes = [guideGroup]
        
    scriptModules = list()
    
    for guideGroup in scriptNodes:
        if not Nodes.exists(guideGroup):
            continue
        runOnBuildStep = mc.getAttr('%s.runOnBuildStep'%guideGroup).replace(' ', '').lower()

        if not buildStep:
            buildStep = ''

        if runOnBuildStep == buildStep.lower():
            scriptFileName = mc.getAttr('%s.fileName'%guideGroup)
            if mc.getAttr('%s.useAssetFolder'%guideGroup) == 'True':
                path = assetPath
            else:
                path = mc.getAttr('%s.customFolder'%guideGroup)
            if path == '':
                return
            filePath = path+'/'+scriptFileName
            if MessageHandling.fileExists(filePath):
                scriptModule = imp.load_source('scriptModule', filePath)
                scriptModules.append(scriptModule)

                print('Script %s executed by Script component: %s'%(filePath.split('/')[-1], guideGroup))

    return scriptModules