# Connection Handling

import maya.cmds as mc
import ast

from bear.system import Settings
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.utilities import Tools
from bear.utilities import NodeOnVertex

loadedSettings = Settings.loadSettings()[0]

def applyConstraint(parentNode, offNode, side, controlNode, rigGroup, parent=True, translate=False, orient=False, scale=True, removeExistingConstraint=True):
    
    if ',' in parentNode:
        parentNodeList = parentNode.replace(' ', '').split(',')
        for p, parentMember in enumerate(parentNodeList):
            parentNodeList[p] = getSideParent(parentMember, side)
            if Nodes.getObjectType(parentNodeList[p]) == 'mesh':
                pinLocs = NodeOnVertex.proximityPin(parentNodeList[p], 
                                                [offNode])[0]
                for axis in 'xyz':
                    if Nodes.isAttrSettable(f'{offNode}.s{axis}'):
                        mc.connectAttr(f'{rigGroup}.globalScale', f'{offNode}.s{axis}')
                if pinLocs and rigGroup:
                    mc.parent(pinLocs, rigGroup)
        
        sclCmpNode = Nodes.replaceNodeType(parentNodeList[0], Settings.scaleCompensateNode)
        if mc.objExists(sclCmpNode) and Nodes.getNodeType(parentNodeList[0]) != Settings.skinJointSuffix:
            parent1Node = sclCmpNode
        else:
            parent1Node = parentNodeList[0]
        sclCmpNode = Nodes.replaceNodeType(parentNodeList[1], Settings.scaleCompensateNode)
        if mc.objExists(sclCmpNode) and Nodes.getNodeType(parentNodeList[1]) != Settings.skinJointSuffix:
            parent2Node = sclCmpNode
        else:
            parent2Node = parentNodeList[1]
            
        Tools.blendBetween(
            [parent1Node], 
            [parent2Node], 
            [offNode],
            attrNode=controlNode, 
            attrName='orientBlend' if orient else 'parentBlend',
            attrTitle='blendAttributes',
            defaultValue=0.5,
            createDrvObj=False,
            attrIsKeyable=False,
            scaleConstrained=False,
            parentConstrained=parent,
            parentConstrainedTranslate=translate,
            orientConstrained=orient,
            )
    else:
        sideParentNode = getSideParent(parentNode, side)
        sclCmpNode = Nodes.replaceNodeType(sideParentNode, Settings.scaleCompensateNode)
        if mc.objExists(sclCmpNode) and Nodes.getNodeType(sideParentNode) != Settings.skinJointSuffix:
            sideParentNode = sclCmpNode
        inheritScale = True
        if rigGroup:
            guideGroup = Nodes.replaceNodeType(rigGroup, Settings.guideGroup)
            inheritScaleAttr = '%s.inheritScale'%guideGroup
            if mc.objExists(inheritScaleAttr):
                inheritScale = mc.getAttr(inheritScaleAttr)
                inheritScale = ast.literal_eval(inheritScale)
        if inheritScale:
            Tools.parentScaleConstraint(
                sideParentNode, 
                offNode, 
                inbetweenObject=False,
                connectTranslate=parent or translate,
                connectRotate=parent or orient,
                connectScale=scale,
                removeExistingConstraint=removeExistingConstraint
                )
        else:
            mc.parentConstraint(sideParentNode, offNode, mo=True)

def getSideParent(parentNode, side):
    
    memberSide = Nodes.getSide(parentNode)
    sideParentNode = parentNode
    
    if side == memberSide and Nodes.getSide(parentNode) == Settings.leftSide:
        if side != Settings.leftSide and side != None:
            sideParentNode = Nodes.replaceSide(parentNode, side)
    else:
        if side != None:
            sideParentNode = Nodes.replaceSide(parentNode, side)
    
    sideParentNode = inputExists(sideParentNode)
                
    return sideParentNode

def getParentAttrs(parentNode, offNode, parentType):
    
    if parentType == None or parentType == '':
        parentType = 'Constraint'
    if type(parentNode) == list:
        parentNode = ','.join(parentNode)
    
    if ',' in parentNode:
        for c in parentNode.replace(' ', '').split(','):
            c = inputExists(c)
    else:
        sclCmpNode = Nodes.replaceNodeType(parentNode, Settings.scaleCompensateNode)
        if mc.objExists(sclCmpNode) and Nodes.getNodeType(parentNode) != Settings.skinJointSuffix:
            parentNode = sclCmpNode
        parentNode = inputExists(parentNode)
        if parentType == 'Hierarchy' and not ',' in parentNode:
            Nodes.setParent(offNode, parentNode)
        if Nodes.getObjectType(parentNode) == 'mesh':
            parentType = 'Mesh'

    return parentNode, parentType

def parentConnection(controlNode, offNode, rigGroup, parentNode, orientNode, parentType, inheritScale):
    '''
    sets the parent connection for the parentNode attribute for guide group and guide shape
    '''
    side = Nodes.getSide(controlNode) if Nodes.getSide(parentNode) != None else None

    # check if offNode already has connections applied from Control.createControl
    if parentNode or orientNode:
        conNodes = mc.listConnections(offNode)
        if conNodes:
            for conNode in conNodes:
                if mc.objExists(conNode) and conNode != rigGroup:
                    mc.delete(conNode)
        
    if (orientNode != None and orientNode != ''):
        orientNode, parentType = getParentAttrs(orientNode, offNode, parentType)
    if (parentNode != None and parentNode != ''):
        parentNode, parentType = getParentAttrs(parentNode, offNode, parentType)
    
    if (parentNode != None and parentNode != '') or (orientNode != None and orientNode != ''):

        if parentType == 'JointConstraint':
            locNode = Tools.parentToClosestVertex(offNode, 
                                                    getSideParent(parentNode, side), 
                                                    attrNode=controlNode, 
                                                    parentType=parentType, 
                                                    orientNode=orientNode)[0]
            if locNode and rigGroup:
                mc.parent(locNode, rigGroup)
            return

        if parentType == 'Mesh':
            pinLocs = NodeOnVertex.proximityPin(getSideParent(parentNode, side), 
                                                    [offNode])[0]
            for axis in 'xyz':
                if Nodes.isAttrSettable(f'{offNode}.s{axis}'):
                    mc.connectAttr(f'{rigGroup}.globalScale', f'{offNode}.s{axis}')
            if pinLocs and rigGroup:
                mc.parent(pinLocs, rigGroup)

            if orientNode:
                parentType = 'Constraint'
                parentNode = True
                
        if parentType == 'Constraint':
            if parentNode and not orientNode:
                applyConstraint(parentNode, offNode, side, controlNode, rigGroup, parent=True, translate=False, orient=False, scale=inheritScale)
            if not parentNode and orientNode:
                applyConstraint(orientNode, offNode, side, controlNode, rigGroup, parent=False, translate=False, orient=True, scale=inheritScale)
            if parentNode and orientNode:
                if parentNode != True:
                    applyConstraint(parentNode, offNode, side, controlNode, rigGroup, parent=False, translate=True, orient=False, scale=inheritScale)
                applyConstraint(orientNode, offNode, side, controlNode, rigGroup, parent=False, translate=False, orient=True, scale=inheritScale, removeExistingConstraint=False)

def inputExists(connectionInput):
    '''
    this is used to create a temporary / placeholder node if a connection is missing
    on component building (for instance if another component is not in the scene)
    '''
    if connectionInput != None and connectionInput != '':
        if type(connectionInput) == list:
            inputList = list()
            for inputNode in connectionInput:
                if not mc.objExists(inputNode):
                    AddNode.placeholderNode(inputNode)
                    #MessageHandling.placeholderCreated(inputNode)
                inputList.append(inputNode)
            return inputList
        else:
            if not mc.objExists(connectionInput):
                AddNode.placeholderNode(connectionInput)
                #MessageHandling.placeholderCreated(connectionInput)

            return connectionInput

def getAllComponentAttrs(compGroup, rigType, definition=False):
    '''
    combines all the attrs of all nested components into one dict
    if the component has been renamed on the name attr, the compName
    will be keyed into the dict instead of the compGroup
    '''
    allAttrs = dict()
    subGroups = list()
    if compGroup != None:
        subGroups = getSubComponents(compGroup, rigType)
        for subGroup in subGroups+[compGroup]:
            subCompAttr = subGroup+'.name'
            if mc.objExists(subCompAttr):
                subCompName = mc.getAttr(subCompAttr)
            else:
                subCompName = None
            attrs = getComponentAttrs(subGroup, subCompName, definition)
            # rename component with name from attr
            if subCompName == None:
                subGroupName = subGroup
            else:
                side = Nodes.getSide(subGroup)
                subGroupName = Nodes.createName(component=subCompName,
                                                side=side,
                                                nodeType='guide')[0]
            allAttrs[subGroupName] = attrs
            # add guide control attrs
            for guideControlNode in Nodes.getAllChildren(subGroup, nodeType=Settings.guideShapeSuffix):
                attrs = getComponentAttrs(guideControlNode)
                allAttrs[guideControlNode] = attrs

    return allAttrs, subGroups

def getComponentAttrs(attrHolder, compName=None, definition=False):
    '''
    gets all attrs of a component
    input and output connections are additional custom attributes that are used
    to save the actual connected source and destination attributes in order to
    recreate connections between components
    '''
    attrs = dict()
    if mc.objExists(attrHolder):
        attrNames = mc.listAttr(attrHolder, userDefined=True)
        if attrNames != None:
            attrVals = [mc.getAttr(attrHolder+'.'+attrName) for attrName in attrNames]
            for a, attrName in enumerate(attrNames):
                attrVal = attrVals[a] if compName == None or attrName != 'name' else compName
                inputCon = mc.listConnections(attrHolder+'.'+attrName, source=True, destination=False, plugs=True)
                outputCon = mc.listConnections(attrHolder+'.'+attrName, source=False, destination=True, plugs=True)
                attrs[attrName] = attrVal
                attrs['in_'+attrName] = inputCon[0] if inputCon != None else None
                attrs['out_'+attrName] = outputCon[0] if outputCon != None else None
    
    # add the guide group transforms, NOTE: getting the definition through is a bit of a hack but it seems to work
    if definition:
        attrs.update(Nodes.getTrs(attrHolder))

    return attrs

def getSubComponents(compGroup, rigType):
    '''
    loops through the child nodes of a guideGroup to find all sub guideGroups
    '''
    children = mc.listRelatives(compGroup, children=True)
    if children == None:
        return []
    subGroups = [x for x in children if mc.objExists(x+'.componentType')]
    if rigType == 'guide':
        subGroups = [x for x in subGroups if mc.listAttr(x, userDefined=True) != None]

    return subGroups

def recreateComponent(compName, side, rigType, compGroup, definition=False):
    '''
    stores all builds attrs of compGroup and sub groups and saves a temporary guide file
    if side is different from compName, a new component will be created
    '''
    
    oldLimbRig = False
    if compGroup:
        if mc.objExists(compGroup):
            allAttrs, subGroups = getAllComponentAttrs(compGroup, rigType, definition=definition)
        else:
            allAttrs = {}
            subGroups = []
        bearVersion = mc.getAttr('%s.bearVersion'%compGroup).split('.')
        if int(bearVersion[0]) == 0:
            oldLimbRig = True
        else:
            oldLimbRig = int(bearVersion[1]) < 2
    else:
        allAttrs = {}
        subGroups = []

    compParent = Nodes.getParent(compGroup)
    if compParent:
        compOrder = [x for x in mc.listRelatives(compParent, children=True) if mc.objExists('%s.componentType'%x)]
    orderIndex = None
    tempFile = None
    
    if compGroup:
        if mc.objExists(compGroup):
            guideGroup = Nodes.replaceNodeType(compGroup, Settings.guideGroup)
            orderIndex = compOrder.index(guideGroup)
            if Nodes.getSide(guideGroup) == None and (not mc.objExists(Nodes.createName(sourceNode=guideGroup, side=side)[0]) or side):
                orderIndex += 1
            if rigType == 'guide':
                if mc.objExists(guideGroup):
                    mc.select(guideGroup)
                    tempFolder = Settings.getPath(['system'])
                    tempFileName = tempFolder+guideGroup
                    tempFile = mc.file(tempFileName, type=loadedSettings['mayaFileType'], exportSelected=True, f=True)
                if Nodes.getSide(compGroup) == side:
                    relatedNodes = Nodes.getRelatedNodes(compGroup)
                    if mc.getAttr('%s.componentType'%compGroup) == 'Collection':
                        compChildNodes = mc.listRelatives(compGroup, children=True)
                        if compChildNodes:
                            compSubGroups = [x for x in compChildNodes if mc.objExists('%s.componentType'%x)]
                            [relatedNodes.extend(Nodes.getRelatedNodes(x)) for x in compSubGroups]
                    if relatedNodes != []:
                        mc.delete(relatedNodes)
                    mc.delete(compGroup)
                targetCompGroup = Nodes.createName(component=compName, side=side, nodeType=rigType)[0]
                if mc.objExists(targetCompGroup):
                    mc.delete(targetCompGroup)
            if rigType == 'rig':
                rigGroup = compGroup.replace('guide', 'rig')
                if mc.objExists(rigGroup):
                    relatedNodes = Nodes.getRelatedNodes(rigGroup)
                    if mc.getAttr('%s.componentType'%compGroup) == 'Collection':
                        rigSubGroups = [x for x in mc.listRelatives(rigGroup, children=True) if mc.objExists('%s.componentType'%x)]
                        [relatedNodes.extend(Nodes.getRelatedNodes(x)) for x in rigSubGroups]
                    if relatedNodes != []:
                        mc.delete(relatedNodes)
                    mc.delete(rigGroup)
    
    return allAttrs, tempFile, compParent, orderIndex, subGroups, oldLimbRig

def addOutput(guideGroup, node=None, name=None, attrName=None):
    '''
    adds a custom attribute to the guideGroup to be used as an output
    for connecting a node to an input of another component like parentNode
    '''
    if not mc.objExists(guideGroup):
        return

    if attrName != None:
        attrName = 'output_'+attrName
    if node != None:
        if attrName == None:
            attrName = 'output_'+node
        attrValue = node
    if name != None:
        if attrName == None:
            attrName = 'output_'+name
        attrValue = name
    
    mc.addAttr(guideGroup, dt='string', ln=attrName)
    mc.setAttr(guideGroup+'.'+attrName, attrValue, type='string', lock=True)