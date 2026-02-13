# AddNode

import maya.cmds as mc

from bear.system import Settings
from bear.utilities import Nodes
from bear.utilities import Color

def replaceTempNode(nodeName):

    if mc.objExists(nodeName+'.placeholderNode'):
        mc.delete(nodeName)

def inbetweenNode(node, nodeType=Settings.cntNodeSuffix, specific=None, objType='group', reparentChildNode=True, lockScale=False, byName=None, zeroValues=False):

    name = Nodes.createName(sourceNode=byName if byName else node, nodeType=nodeType, specific=specific)[0]

    replaceTempNode(name)

    if objType == 'group':
        inbetweenNode = mc.group(name=name, empty=True)
    if objType == 'locator':
        inbetweenNode = mc.spaceLocator(name=name)[0]
    
    Nodes.alignObject(inbetweenNode, node, oldStyle=True)
    if lockScale:
        for axis in 'xyz':
            mc.setAttr('%s.s%s'%(inbetweenNode, axis), lock=True)

    if reparentChildNode:
        childList = mc.listRelatives(node, children=True, type='transform')
        if childList != None:
            for childNode in childList:
                if not 'Constraint' in mc.objectType(childNode):
                    Nodes.setParent(childNode, inbetweenNode, lockScale=False, zeroValues=zeroValues)

    Nodes.setParent(inbetweenNode, node, lockScale=lockScale, zeroValues=zeroValues)

    Nodes.addNamingAttr(inbetweenNode, Nodes.getNamingOrder(byName if byName else node))

    mc.select(clear=True)

    return inbetweenNode

def parentNode(node, nodeType=Settings.offNodeSuffix, lockScale=False, byName=None, specific=None, zeroValues=False):
    
    name = Nodes.createName(sourceNode=byName if byName else node, nodeType=nodeType, specific=specific)
    
    replaceTempNode(name[0])

    offNode = mc.group(name=name[0], empty=True)

    if lockScale:
        for axis in 'xyz':
            mc.setAttr('%s.s%s'%(offNode, axis), lock=True)

    parentNodeList = mc.listRelatives(node, parent=True)
    if parentNodeList != None:
        Nodes.setParent(offNode, parentNodeList[0], lockScale=lockScale)

    Nodes.alignObject(offNode, node, oldStyle=True)

    Nodes.setParent(node, offNode, lockScale=lockScale, zeroValues=zeroValues)

    for axis in 'xyz':
        mc.setAttr('%s.s%s'%(node, axis), lock=False)

    Nodes.addNamingAttr(offNode, name[1])

    mc.select(clear=True)

    return offNode

def childNode(node, nodeType=Settings.drivenNodeSuffix, lockScale=False, byName=None, zeroValues=False, location=None):
    
    name = Nodes.replaceNodeType(byName if byName else node, nodeType)

    replaceTempNode(name)

    childNode = mc.group(name=name, empty=True)

    if lockScale:
        for axis in 'xyz':
            mc.setAttr('%s.s%s'%(childNode, axis), lock=True)

    Nodes.alignObject(childNode, location or node, oldStyle=True)
    Nodes.setParent(childNode, node, lockScale=lockScale, zeroValues=zeroValues)

    Nodes.addNamingAttr(childNode, Nodes.getNamingOrder(byName if byName else node))
    
    mc.select(clear=True)

    return childNode

def emptyNode(node=None, 
                component=None, 
                side=None, 
                nodeType=None, 
                element=None, 
                indices=None, 
                specific=None, 
                indexFill=2, 
                parentNode=None, 
                objType='transform', 
                color='Dark Blue', 
                lockScale=False, 
                hasMirror=False,
                alignToGuide=False,
                location=None,
                size=1):

    name = Nodes.createName(component, side, nodeType, element, indices, specific, indexFill, node)

    if alignToGuide:
        node = Nodes.replaceNodeType(name[0], Settings.guidePivotSuffix)
    
    replaceTempNode(name[0])

    if objType == 'transform':
        emptyNode = mc.group(name=name[0], empty=True)
    if objType == 'locator':
        emptyNode = mc.spaceLocator(name=name[0])[0]
        [mc.setAttr('%s.localScale%s'%(emptyNode, axis), size) for axis in 'XYZ']
        Color.setColor(emptyNode, color)

    if lockScale:
        for axis in 'xyz':
            mc.setAttr('%s.s%s'%(emptyNode, axis), lock=True)

    if hasMirror and side == Settings.rightSide:
        for axis in 'xyz':
            mc.setAttr('%s.s%s'%(emptyNode, axis), -1)

    Nodes.addNamingAttr(emptyNode, name[1])
    
    if '|' in emptyNode:
        return emptyNode

    if node and mc.objExists(node):
        Nodes.alignObject(emptyNode, location or node, oldStyle=True)
    if not parentNode:
        if Nodes.getParent(emptyNode):
            Nodes.setParent(emptyNode, world=True, lockScale=lockScale)
    else:
        Nodes.setParent(emptyNode, parentNode, lockScale=lockScale)

    mc.select(clear=True)

    return emptyNode

def jointNode(node=None, 
                component=None, 
                side=None, 
                nodeType=Settings.skinJointSuffix, 
                element=None, 
                indices=None, 
                specific=None,
                indexFill=2, 
                size=1, 
                offset=None, 
                offsetAxis='X',
                parentNode=None,
                parentToNode=True,
                alignToNode=True,
                resetTransforms=False,
                convertRotToOrient=False,
                alignByRotationValues=True,
                skeletonParent=None,
                namingOrder=Settings.namingOrder):
    
    # NOTE we don't have specific input because specific is used for pivot control in control module only
    # joints will be named irrespectively of having pivot control
    
    mc.select(clear=True)

    name = Nodes.createName(component, side, nodeType, element, indices, specific, indexFill, node, namingOrder=namingOrder)

    if not side and node:
        side = Nodes.getSide(node)

    replaceTempNode(name[0])
    jointNode = mc.joint(name=name[0], radius=size)

    Nodes.addNamingAttr(jointNode, name[1])

    if nodeType == Settings.guidePivotSuffix:
        pivotShapeSizeAttr = jointNode+'.pivotShapeSize'
        Nodes.addAttr(pivotShapeSizeAttr, dv=size*0.1, minVal=0, d=True, k=True)
        Nodes.addAttr(jointNode+'.pivotInitialShapeSize', dv=size*0.1, minVal=0, d=False, k=False)
        mc.setAttr(jointNode+'.radius', cb=False)

    if Nodes.getShapeType(node) == 'joint':
        Nodes.setParent(jointNode, parentNode)

    if node != None:
        sclCmpNode = Nodes.replaceNodeType(node, Settings.scaleCompensateNode)
        if mc.objExists(sclCmpNode):
            parentNode = sclCmpNode
        else:
            if parentToNode and not parentNode:
                parentNode = node
        if alignToNode:
            Nodes.alignObject(jointNode, node, oldStyle=False)
            if Nodes.getShapeType(node) == 'joint' and alignByRotationValues:
                Nodes.setTrs(jointNode, t=False, trsVal=Nodes.getTrs(node))

    if Nodes.getShapeType(node) != 'joint':
        Nodes.setParent(jointNode, parentNode)
    
    if nodeType == Settings.skinJointSuffix:
        Nodes.addJointLabel(jointNode, side)
    
    if offset:
        offsetAxis = offsetAxis.lower()
        direction = -1 if '-' in offsetAxis else 1
        mc.setAttr('%s.t%s'%(jointNode, offsetAxis), offset*direction)

    if resetTransforms:
        Nodes.setTrs(jointNode)

    if convertRotToOrient:
        Nodes.convertJointRotToOrient(jointNode)
    
    if skeletonParent:
        Nodes.addSkeletonParentAttr(jointNode, skeletonParent)

    mc.select(clear=True)

    return jointNode

def compNode(component=None, 
            side=None, 
            nodeType=Settings.rigGroup,
            element=None, 
            indices=None, 
            parentNode=None, 
            inheritsTransform=True,
            sourceNode=None,
            hasGlobalScale=True, 
            root=None,
            createRootOnly=False):
    
    if root:
        compRoot = emptyNode(nodeType=root) if not mc.objExists(root) else root
    else:
        root = parentNode
        compRoot = root
    if compRoot:
        compRoot = emptyNode(nodeType=root) if not mc.objExists(root) else root
        Nodes.addNamingToRigNode(compRoot)
        Nodes.applyGlobalScale(compRoot, [compRoot], lock=True)
    if createRootOnly:
        return

    name = Nodes.createName(component, None if side == 'auto' else side, nodeType, element, indices, sourceNode=sourceNode)
    
    compGroup = name[0]
    if not mc.objExists(compGroup):
        compGroup = mc.group(name=name[0], empty=True)
        if parentNode != None:
            if mc.objExists(parentNode):
                Nodes.setParent(compGroup, parentNode)
        if not inheritsTransform:
            mc.setAttr('%s.inheritsTransform'%compGroup, False)

        if nodeType == Settings.guideGroup:
            readyForRigBuildAttrName = 'readyForRigBuild'
            readyForRigBuildAttr = compGroup+'.'+readyForRigBuildAttrName
            if not mc.objExists(readyForRigBuildAttr):
                mc.addAttr(compGroup, ln=readyForRigBuildAttrName, at='bool', k=False, dv=False)
            mc.setAttr(readyForRigBuildAttr, lock=True)
            Nodes.lockAndHideAttributes(compGroup, r=[True, True, True])

        Nodes.setParent(compGroup, compRoot)
        Nodes.setParent(compRoot, Nodes.getAssetNode()[0])
    
    if hasGlobalScale:
        Nodes.applyGlobalScale(compGroup, [compGroup], lock=compRoot==Settings.guideRoot)
    Nodes.addNamingAttr(compGroup, name[1])
    if side != 'auto':
        Nodes.addAttr(compGroup+'.side', dv=side if side else 'None', at='string', lock=True)
    Nodes.addBearVersion(compGroup)

    return compGroup

def placeholderNode(inputNode):

    mc.select(clear=True)

    placeHolderGroup = emptyNode(nodeType=Settings.placeHolderGroup) if not mc.objExists(Settings.placeHolderGroup) else Settings.placeHolderGroup
    mc.hide(placeHolderGroup)
    
    tokens = inputNode.split('_')

    if Settings.skinJointSuffix in tokens:
        placeholderNode = mc.joint(name=inputNode, radius=1)
    else:
        placeholderNode = mc.spaceLocator(name=inputNode)[0]

    mc.addAttr(placeholderNode, at='bool', ln='placeholderNode', dv=True)
    mc.setAttr(placeholderNode+'.placeholderNode', lock=True)
    
    # we add an incorrect naming convention since we need to have a workaround for the name
    # in order to support working with the node in the rig build
    Nodes.addNamingAttr(placeholderNode, ['component', 'nodeType'])

    Nodes.setParent(placeholderNode, placeHolderGroup)

    return placeholderNode

def createLocOnSelection(sel, n, nodeType=Settings.locNodeSuffix):

    if type(sel) == list:
        name = sel[0]
    else:
        name = sel

    locPosNode = emptyNode(component=Nodes.camelCase(name.split('.')[0]), nodeType=nodeType, indices=n)
    mc.select(sel)

    clusterNodes = mc.cluster()
    Nodes.alignObject(locPosNode, clusterNodes[1])
    mc.delete(clusterNodes)
    
    return locPosNode

def setNode(nodes=None,
            component=None,
            side=None,
            nodeType=Settings.setSuffix):
    
    setName = Nodes.createName(component, side, nodeType)
    mc.sets(name=setName[0], empty=True)
    if nodes:
        if len(nodes) > 0:
            mc.sets(nodes, addElement=setName[0])
    Nodes.addNamingAttr(setName[0], setName[1])

    return setName[0]