# Guiding

import maya.cmds as mc
import ast

from bear.system import Settings
from bear.utilities import Tools
from bear.utilities import Nodes

def convertGuide(node, mirror=False, mirrorRotate=(0, 0, 180), nodeType=None, deleteNode=False, byString=False):

    nodeList = list()
    redundantNodes = list()

    if Nodes.getShapeType(node) == 'joint' and mirror:
        
        dupList = mc.mirrorJoint(Nodes.replaceSide(node, Settings.leftSide), mirrorYZ=True, mirrorBehavior=True)
        if deleteNode:
            mc.delete(node)
        dupList = [x for x in dupList if mc.objectType(x) == 'transform' or mc.objectType(x) == 'joint']
        dupList = [mc.rename(x, Nodes.replaceSide(x, Settings.rightSide)) for x in mc.ls(dupList)]
        for dup in dupList:
            if (Settings.guidePivotSuffix in dup or Settings.guideCurveSuffix in dup or Settings.guideSurfaceSuffix in dup) \
            and not Settings.guideClusterHandleSuffix+'Handle' in dup or mc.objectType(dup) == 'joint':
                if Settings.guideCurveSuffix in dup:
                    mirName = Nodes.replaceNodeType(dup, Settings.curveDupNodeSuffix)
                else:
                    mirName = Nodes.replaceNodeType(dup, Settings.dupNodeSuffix)
                dup = mc.rename(dup, mirName)
                Nodes.lockAndHideAttributes(dup, t=[True, True, True], r=[True, True, True], s=[True, True, True], lock=False, v=True, keyable=True)
                if Settings.guideCurveSuffix in dup and Nodes.getSide(dup) == Settings.rightSide:
                    mc.hide(dup)
                nodeList.append(dup)
            else:
                redundantNodes.append(dup)

    else:
        
        dupList = mc.duplicate(node, renameChildren=True)
        childList = mc.listRelatives(dupList, allDescendents=True, type='transform')
        
        if childList != None:
            dupList = [dupList[0]]
            for childNode in childList[::-1]:
                if mc.objExists(childNode):
                    if mc.objectType(childNode) != 'joint':
                        mc.delete(childNode)
                    else:
                        dupList.append(childNode)
        else:
            dupList = [dupList[0]]
        
        for dup in dupList:
            if (Settings.guidePoseSuffix in dup or Settings.guidePivotSuffix in dup or Settings.guideCurveSuffix in dup or Settings.guideSurfaceSuffix in dup) \
                and not Settings.guideClusterHandleSuffix+'Handle' in dup or mc.objectType(dup) == 'joint':
                if mirror:
                    dup = Tools.mirrorObject(dup, rotate=mirrorRotate, removeNode=True, byString=byString)
                    newSuffix = Settings.guidePivotSuffix
                    if Settings.guideCurveSuffix in dup:
                        newSuffix = Settings.guideCurveSuffix
                    if Settings.guideSurfaceSuffix in dup:
                        newSuffix = Settings.guideSurfaceSuffix
                    if Settings.guidePoseSuffix in dup:
                        newSuffix = Settings.guidePoseSuffix
                    try:
                        newName = Nodes.replaceNodeType(dup, newSuffix)
                    except:
                        newName = Nodes.replaceSuffix(dup, newSuffix)
                    if Nodes.getShapeType(dup) == 'nurbsSurface':
                        mc.reverseSurface(dup)
                else:
                    if Settings.guideCurveSuffix in dup:
                        newName = Nodes.replaceNodeType(dup, Settings.curveDupNodeSuffix)
                    else:
                        newName = Nodes.replaceNodeType(dup, Settings.dupNodeSuffix)
                if mc.objExists(newName):
                    Nodes.alignObject(newName, dup)
                    mc.delete(dup)
                    dup = newName
                dup = mc.rename(dup, newName)
                Nodes.lockAndHideAttributes(dup, t=[True, True, True], r=[True, True, True], s=[True, True, True], lock=False, v=True, keyable=True)
                nodeList.append(dup)
            else:
                if not mirror:
                    redundantNodes.append(dup)
        
    if redundantNodes != []:
        mc.delete(redundantNodes)

    if nodeType != None:
        nodeList = [mc.rename(node, Nodes.replaceNodeType(node, nodeType)) for node in nodeList]
    
    for node in nodeList:
        if mc.objectType(node) == 'joint':
            pass
            #Nodes.convertJointRotToOrient(node)

    return nodeList

def mirrorGuide(guideGroup):
    '''
    this mirror method works on an existing side guide (guideGroup) and tries to find a source guide with opposite side or
    none side. If found, a mirror will be applied based on the source guide and applied to the guideGroup
    NOTE: only mirrors gde transforms. shape transforms and settings (gdc) are applied through the reference process
    NOTE: This should be recoded since it's a mess. It works though.
    '''
    targetSide = Nodes.getSide(guideGroup)
    if targetSide == None:
        return
    sourceSide = Settings.leftSide if targetSide == Settings.rightSide else Settings.rightSide
    sourceGuideGroup = Nodes.replaceSide(guideGroup, sourceSide)
    if not mc.objExists(sourceGuideGroup):
        sourceGuideGroup = Nodes.replaceSide(guideGroup, False)
        if not mc.objExists(sourceGuideGroup):
            return

    guideChildNodes = mc.listRelatives(guideGroup, children=True, type='transform')
    mc.parent(guideChildNodes, world=True)
    
    sourceXOffset = mc.getAttr('%s.tx'%sourceGuideGroup)
    mc.setAttr('%s.tx'%guideGroup, -sourceXOffset)

    for sourceNode in Nodes.getAllChildren(sourceGuideGroup, nodeType=Settings.guidePivotSuffix):
        if Nodes.getShapeType(Nodes.getParent(sourceNode)) != 'joint':
            targetNode = Nodes.replaceSide(sourceNode, targetSide)
            mirNode = Tools.mirrorObject(sourceNode, rotate=(0, 0, 180), replaceExistingMirNode=False, uniqueCopy=True)
            if Nodes.getShapeType(targetNode) == 'joint':
                for axis in 'XYZ':
                    mirRot = mc.getAttr('%s.rotate%s'%(mirNode, axis))
                    mirJointRot = mc.getAttr('%s.jointOrient%s'%(mirNode, axis))
                    jointRotAttr = '%s.rotate%s'%(targetNode, axis)
                    if Nodes.isAttrSettable(jointRotAttr):
                        mc.setAttr(jointRotAttr, mirRot)
                    mc.setAttr('%s.jointOrient%s'%(targetNode, axis), mirJointRot)
            Nodes.alignObject(targetNode, mirNode)
            mc.delete(mirNode)
            
    mc.parent(guideChildNodes, guideGroup)
    
    tVals = list()
    for sourceNode in Nodes.getAllChildren(sourceGuideGroup, nodeType=Settings.guidePivotSuffix):
        tVal = mc.xform(sourceNode, ws=True, translation=True, q=True)
        tVals.append(tVal)
        targetNode = Nodes.replaceSide(sourceNode, targetSide)
        if Nodes.getShapeType(Nodes.getParent(sourceNode)) != 'joint':
            mirNode = Tools.mirrorObject(sourceNode, rotate=(0, 0, 180), replaceExistingMirNode=False, uniqueCopy=True)
            if Nodes.getShapeType(targetNode) == 'joint':
                tAttr = '%s.tx'%targetNode
                if Nodes.isAttrSettable(tAttr):
                    mc.setAttr(tAttr, mc.getAttr('%s.tx'%mirNode))
                for trgChildJoint in [x for x in Nodes.getAllChildren(targetNode) if Nodes.getShapeType(x) == 'joint']:
                    srcChildJoint = Nodes.replaceSide(trgChildJoint, sourceSide)
                    for axis in 'xyz':
                        trgAttr = '%s.t%s'%(trgChildJoint, axis)
                        srcAttr = '%s.t%s'%(srcChildJoint, axis)
                        if not mc.getAttr(trgAttr, lock=True) and mc.objExists(srcAttr):
                            mc.setAttr(trgAttr, -mc.getAttr(srcAttr))
            mc.delete(mirNode)
    for n, sourceNode in enumerate(Nodes.getAllChildren(sourceGuideGroup, nodeType=Settings.guidePivotSuffix)):
        targetNode = Nodes.replaceSide(sourceNode, targetSide)
        tVal = tVals[n]
        mc.xform(targetNode, translation=[-tVal[0], tVal[1], tVal[2]], ws=True)

    mc.select(clear=True)

def getGuideAttr(node, attrPrefix='', specialAttr=None):
    
    pivotGuide = Nodes.replaceNodeType(node, Settings.guidePivotSuffix)
    controlGuide = Nodes.replaceNodeType(node, Settings.guideShapeSuffix)
    
    if not mc.objExists(controlGuide):
        mSide = Settings.rightSide if Nodes.getSide(node) == Settings.leftSide else Settings.leftSide
        newSideNode = Nodes.replaceSide(node, mSide)
        controlGuide = Nodes.replaceNodeType(newSideNode, Settings.guideShapeSuffix)
    if not mc.objExists(controlGuide):
        controlGuide = pivotGuide

    if not mc.objExists(pivotGuide):
        pivotGuide = None
    
    if specialAttr == None:
        
        shapeName = 'shape' if attrPrefix == '' else attrPrefix+'Shape'
        colorName = 'color' if attrPrefix == '' else attrPrefix+'Color'
        hasPivotName = 'hasPivotControl' if attrPrefix == '' else attrPrefix+'HasPivotControl'
        secondaryDefaultColorName = 'secondaryDefaultColor' if attrPrefix == '' else attrPrefix+'secondaryDefaultColor'
        isVisibleName = 'isVisible' if attrPrefix == '' else attrPrefix+'IsVisible'
        
        spaceNodes = 'spaceNodes'
        spaceNames = 'spaceNames'
        defaultSpaceName = 'defaultSpace'
        reverseSpacesName = 'reverseSpaces'
        reverseOffName = 'reverseOff'

        parentNodeName = 'parentNode'
        orientNodeName = 'orientNode'
        parentTypeName = 'parentType'

        lockAndHideNames = list()
        for trs in 'trs':
            for axis in 'xyz':
                lockAndHideNames.append('lockAndHide%s%s'%(trs.upper(), axis))

        hasTransformLimitsName = 'hasTransformLimits'

        hasRotateOrderName = 'hasRotateOrder'
        
        postDeformAlignmentName = 'postDeformAlignment'
        
        try:
            offset = [[mc.getAttr('%s.%s%s' % (controlGuide, t, x)) for x in 'xyz'] for t in 'trs']
        except:
            offset = None
        try:
            shape = Settings.shapes[mc.getAttr('%s.%s' % (controlGuide, shapeName))]
        except:
            shape = None
        try:
            colorValue = mc.getAttr('%s.%s' % (controlGuide, colorName))
            if colorValue == 0:
                color = 'Default'
            else:
                color = Settings.colors[colorValue-1]
        except:
            color = None
        try:
            hasPivot = mc.getAttr('%s.%s' % (controlGuide, hasPivotName))
        except:
            hasPivot = None
        try:
            secondaryDefaultColor = mc.getAttr('%s.%s' % (controlGuide, secondaryDefaultColorName))
        except:
            secondaryDefaultColor = None
        try:
            isVisible = mc.getAttr('%s.%s' % (controlGuide, isVisibleName))
        except:
            isVisible = None
        try:
            postDeformAlignment = mc.getAttr('%s.%s' % (controlGuide, postDeformAlignmentName))
        except:
            postDeformAlignment = None
        
        if None in [offset, shape]:
            return None
        
        try:
            spaceNodes = getBuildAttrs(controlGuide, spaceNodes)
        except:
            spaceNodes = None
        try:
            spaceNames = getBuildAttrs(controlGuide, spaceNames)
        except:
            spaceNames = None
        try:
            defaultSpace = mc.getAttr('%s.%s' % (controlGuide, defaultSpaceName))
        except:
            defaultSpace = None
        try:
            reverseSpaces = getBuildAttrs(controlGuide, reverseSpacesName)
        except:
            reverseSpaces = None
        try:
            reverseOff = getBuildAttrs(controlGuide, reverseOffName)
        except:
            reverseOff = None
        try:
            parentNode = mc.getAttr('%s.%s' % (controlGuide, parentNodeName))
        except:
            parentNode = None
        try:
            orientNode = mc.getAttr('%s.%s' % (controlGuide, orientNodeName))
        except:
            orientNode = None
        try:
            parentType = mc.getAttr('%s.%s' % (controlGuide, parentTypeName))
        except:
            parentType = None
        try:
            lockAndHides = list()
            for lockAndHideName in lockAndHideNames:
                lockAndHides.append(mc.getAttr('%s.%s' % (controlGuide, lockAndHideName)))
        except:
            lockAndHides = None
        try:
            hasTransformLimits = mc.getAttr('%s.%s' % (controlGuide, hasTransformLimitsName))
        except:
            hasTransformLimits = None
        try:
            hasRotateOrder = mc.getAttr('%s.%s' % (controlGuide, hasRotateOrderName))
        except:
            hasRotateOrder = None
        
        if spaceNodes != None:
            if spaceNodes == '':
                spaceNodes = None
        if spaceNames != None:
            if spaceNames == '':
                spaceNames = None
        if reverseSpaces != None:
            if reverseSpaces == '':
                reverseSpaces = None
        if reverseOff != None:
            if reverseOff == '':
                reverseOff = None
        if parentNode != None:
            if parentNode == '':
                parentNode = None
        if orientNode != None:
            if orientNode == '':
                orientNode = None
        if parentType != None:
            if parentType == '':
                parentType = None
        if lockAndHides != None:
            if lockAndHides == '':
                lockAndHides = None
        
        guide = {'pivotGuide':pivotGuide, 
                    'offset':offset, 
                    'shape':shape, 
                    'color':color, 
                    'hasPivotControl':hasPivot, 
                    'secondaryDefaultColor':secondaryDefaultColor, 
                    'isVisible':isVisible, 
                    'spaceNodes':spaceNodes, 
                    'spaceNames':spaceNames, 
                    'hasTransformLimits':hasTransformLimits, 
                    'hasRotateOrder':hasRotateOrder, 
                    'postDeformAlignment':postDeformAlignment, 
                    'defaultSpace':defaultSpace, 
                    'reverseSpaces':reverseSpaces, 
                    'reverseOff':reverseOff, 
                    'parentNode':parentNode, 
                    'orientNode':orientNode, 
                    'parentType':parentType, 
                    'lockAndHides':lockAndHides}
        
        return guide
        
    else:
        
        controlAttr = '%s.%s' % (controlGuide, specialAttr)
        pivotAttr = '%s.%s' % (pivotGuide, specialAttr)
        specialValue = None
        if mc.objExists(controlAttr):
            specialValue = mc.getAttr(controlAttr)
        if mc.objExists(pivotAttr):
            specialValue = mc.getAttr(pivotAttr)
            
        return specialValue

def copyGuideAttrValues(sourceNode, targetNodes, oneToOne=False):

    if oneToOne:
        allNodes = targetNodes+[sourceNode]
        targetNodes = allNodes[len(allNodes)/2:]
        sourceNodes = allNodes[:len(allNodes)/2]
    for t, targetNode in enumerate(targetNodes):
        if not Nodes.exists(targetNode):
            continue
        if oneToOne:
            sourceNode = sourceNodes[t]
        attrList = mc.listAttr(targetNode, userDefined=True)
        if attrList == None:
            attrList = []
        for trs in 'trs':
            for axis in 'xyz':
                attrList.append('%s%s'%(trs, axis))
        if attrList != None:
            for attr in attrList:
                sourceAttr = '%s.%s' % (sourceNode, attr)
                if mc.objExists(sourceAttr):
                    targetAttr = '%s.%s' % (targetNode, attr)
                    if Nodes.isAttrSettable(sourceAttr) and Nodes.isAttrSettable(targetAttr):
                        attrType = mc.getAttr('%s.%s' % (sourceNode, attr), type=True)
                        sourceValue = mc.getAttr('%s.%s' % (sourceNode, attr))
                        if attrType == 'string':
                            if sourceValue != None:
                                mc.setAttr(targetAttr, sourceValue, type='string')
                        elif attrType == 'enum':
                            srcEnumList = mc.attributeQuery(attr, n=sourceNode, listEnum=True)[0].split(':')
                            trgEnumList = mc.attributeQuery(attr, n=targetNode, listEnum=True)[0].split(':')
                            enumName = srcEnumList[sourceValue]
                            targetValue = None
                            for enumIndex in range(len(srcEnumList)):
                                if enumIndex < len(trgEnumList)-1:
                                    if trgEnumList[enumIndex] == enumName:
                                        targetValue = enumIndex
                            if targetValue != None:
                                mc.setAttr(targetAttr, targetValue)
                        else:
                            try:
                                mc.setAttr(targetAttr, sourceValue)
                            except:
                                mc.warning(f'Attribute value could not be set: {targetAttr}')
                    element = Nodes.getElement(sourceNode)
                    if Nodes.getNodeType(sourceNode) == Settings.controlSuffix:
                        if element:
                            if 'Squash' in element:
                                continue
                        offsetParentMtx = Nodes.getOffsetParentMatrix(sourceNode)
                        Nodes.setOffsetParentMatrix(targetNode, matrix=offsetParentMtx)

def getBuildAttrs(attrHolder, attrName=None):
    
    buildAttrs = dict()

    if attrName == None:
        attrNames = mc.listAttr(attrHolder, userDefined=True)
        if attrNames == None:
            return None
    else:
        attrNames = [attrName]
    
    for a in attrNames:
        
        if a in ['globalScale', 'global', 'readyForRigBuild', 'guide']:
            continue

        attr = attrHolder+'.'+a
        if not Nodes.exists(attr):
            attrHolder = Nodes.replaceNodeType(attrHolder, Settings.guidePivotSuffix)
            attr = attrHolder+'.'+a
            if not Nodes.exists(attr):
                return buildAttrs
        
        attrVal = mc.getAttr(attr)

        # NOTE this section needs fixing, it doesn't updated the value in the guide
        if attrVal == 'unsupported' and Settings.licenseVersion == 'full':
            attrVal = True

        if type(attrVal) == int or type(attrVal) == float or type(attrVal) == bool:
            val = attrVal
        elif ',' in attrVal:
            attrVal = attrVal.replace(' ', '')
            attrVal = attrVal.split(',')
            val = list()
            for v in attrVal:
                try:
                    if v.isdigit():
                        val.append(int(v))
                    else:
                        val.append(float(v))
                except:
                    if v == 'False':
                        v = False
                    if v == 'True':
                        v = True
                    if v == 'None':
                        v = None
                    val.append(v)
        else:
            val = attrVal
        try:
            val = ast.literal_eval(val)
        except:
            pass
        if type(val) == str:
            val = val.replace('\\', '/')
        if attrName:
            buildAttrs = val
        else:
            buildAttrs[a] = val
        
    return buildAttrs

def getBuildValues(buildAttrs, buildAttrsList, side):
    
    for buildAttr in buildAttrs:
        if buildAttr == 'side':
            if side != None:
                buildAttrs[buildAttr] = side

    buildVals = list()
    for buildAttrVal in buildAttrsList:
        buildAttr = buildAttrVal[0]
        buildVal = buildAttrVal[1]
        if buildAttr in buildAttrs:
            buildVal = buildAttrs[buildAttr]
        if buildAttr == 'oldLimbRig':
            continue
        buildVals.append(buildVal)
    
    return buildVals

def setGuideBshValues(control, tolerance=0.001):

    if control == None:
        return False
    guideControl = Nodes.replaceSuffix(control, Settings.guideShapeSuffix)
    if not mc.objExists(guideControl):
        return False
    targetAttrs = [x for x in mc.listAttr(guideControl, userDefined=True) if not '_combine_' in x and 'bsh_' in x]
    if targetAttrs == []:
        return None
    for trs in ['translate', 'rotate']:
        for axis in 'XYZ':
            trsAttr = trs+axis
            value = mc.getAttr('%s.%s'%(control, trsAttr))
            if value < tolerance and value > -tolerance:
                continue
            direction = 'neg' if value < 0 else 'pos'
            value = abs(value)
            for attr in targetAttrs:
                if attr.split('_')[-2:] == [trsAttr, direction]:
                    mc.setAttr('%s.%s'%(guideControl, attr), value)
            mc.setAttr('%s.%s'%(control, trsAttr), 0)
    mc.select(guideControl)
    return True