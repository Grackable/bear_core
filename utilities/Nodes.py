# Nodes

import maya.cmds as mc
import maya.mel as mel
import maya.api.OpenMaya as om
import os

from re import sub

from bear.system import MessageHandling
from bear.system import Settings
from bear.utilities import Color

def addAttrTitle(node, titleName, niceName=None):

    if not mc.objExists('%s.%s'%(node, titleName)):
        if niceName == None:
            upperIndices = [0]
            upperIndices.extend([i for i, c in enumerate(titleName) if c.isupper()])
            upperCaseParts = [titleName[i:j].capitalize() for i,j in zip(upperIndices, upperIndices[1:]+[None])]
            mc.addAttr(node, 
                        at='enum', 
                        ln=titleName, 
                        nn=' '.join(['<']+upperCaseParts+['>']), 
                        enumName='---------------',
                        keyable=False, 
                        hidden=False, 
                        dv=0)
        else:
            mc.addAttr(node, 
                        at='enum', 
                        ln=titleName, 
                        nn=' '.join(['<', niceName, '>']), 
                        enumName='---------------',
                        keyable=False, 
                        hidden=False, 
                        dv=0)
        mc.setAttr('%s.%s' % (node, titleName), channelBox=True, lock=True)

def addAttr(attr, dv=0, k=True, d=True, minVal=None, maxVal=None, at='float', enums=[], lock=False):

    node = attr.split('.')[0]
    attrName = attr.split('.')[1]

    if not mc.objExists('%s.%s'%(node, attrName)):
        if at == 'float':
            if minVal != None and maxVal == None:
                mc.addAttr(node, ln=attrName, at=at, k=k, dv=dv, hasMinValue=True, minValue=minVal)
            elif maxVal != None and minVal == None:
                mc.addAttr(node, ln=attrName, at=at, k=k, dv=dv, hasMaxValue=True, maxValue=maxVal)
            elif minVal != None and maxVal != None:
                mc.addAttr(node, ln=attrName, at=at, k=k, dv=dv, hasMinValue=True, minValue=minVal, hasMaxValue=True, maxValue=maxVal)
            else:
                mc.addAttr(node, ln=attrName, at=at, k=k, dv=dv)
        if at == 'bool':
            mc.addAttr(node, ln=attrName, at=at, k=k, dv=dv)
        if at == 'long':
            mc.addAttr(node, ln=attrName, at=at, k=k, dv=dv)
        if at == 'string':
            if type(dv) != str:
                dv = ''
            mc.addAttr(node, ln=attrName, dt=at)
            mc.setAttr(node+'.'+attrName, dv, type=at)
        if at == 'enum':
            mc.addAttr(node, ln=attrName, at=at, dv=dv, enumName=':'.join(enums), k=k)
    
    if isAttrSettable(node+'.'+attrName):

        if d and not k:
            mc.setAttr(node+'.'+attrName, cb=d)

        if lock:
            mc.setAttr(node+'.'+attrName, lock=True)

    return attr

def setAttr(attr, value, type=None):

    if not mc.objExists(attr):
        return
    if not isAttrSettable(attr):
        return
    try:
        if type == 'string':
            mc.setAttr(attr, value, type=type)
        else:
            mc.setAttr(attr, value)
    except:
        mc.warning(f"Attribute could not be set: {attr}")

def getAttr(attr):

    if not mc.objExists(attr):
        return
    value = mc.getAttr(attr)

    return value

def connectAttr(sourceAttr, targetAttr, lock=False):

    if mc.listConnections(targetAttr, source=True, destination=False, plugs=True) != None:
        removeConnection(targetAttr)
        
    mc.connectAttr(sourceAttr, targetAttr)
    if lock:
        mc.setAttr(targetAttr, lock=True)

def delete(nodes):

    if not nodes:
        return

    if type(nodes) != list:
        nodes = [nodes]

    for node in nodes:
        if mc.objExists(node):
            mc.delete(node)

def exists(node):

    if not node:
        return False
    
    return mc.objExists(node)

def lockAndHide(node, trs='trs', axis='xyz', other=None, lock=True, keyable=False, visible=False):

    for t in trs:
        for a in axis:
            attr = '%s.%s%s'%(node, t, a)
            mc.setAttr(attr, k=keyable)
            mc.setAttr(attr, lock=lock)
            if not keyable:
                mc.setAttr(attr, cb=visible)
    if other:
        attr = '%s.%s'%(node, other)
        mc.setAttr(attr, k=keyable)
        mc.setAttr(attr, lock=lock)
        if not keyable:
            mc.setAttr(attr, cb=visible)

def lockAndHideAttributes(obj, t=[False, False, False], r=[False, False, False], s=[False, False, False], v=False,
                          lock=True, keyable=False, lockVis=False, hide=True, attrName=None):

    for s, lockSet in enumerate([t, r, s]):

        if s == 0:
            trm = 'translate'
        if s == 1:
            trm = 'rotate'
        if s == 2:
            trm = 'scale'

        for a, axisState in enumerate(lockSet):

            if a == 0:
                axis = 'X'
            if a == 1:
                axis = 'Y'
            if a == 2:
                axis = 'Z'

            if axisState:
                mc.setAttr('%s.%s%s' % (obj, trm, axis), lock=lock)
                mc.setAttr('%s.%s%s' % (obj, trm, axis), keyable=keyable)
                if not hide:
                    mc.setAttr('%s.%s%s' % (obj, trm, axis), channelBox=True)
                    
    if v:
        mc.setAttr('%s.visibility' % (obj), lock=lockVis)
        mc.setAttr('%s.visibility' % (obj), keyable=keyable)
        if not hide:
            mc.setAttr('%s.visibility' % (obj), channelBox=True)
    
    if attrName:
        mc.setAttr('%s.%s' % (obj, attrName), lock=lock)
        mc.setAttr('%s.%s' % (obj, attrName), channelBox=False if hide else True)

def getSkinJoints(nodes):

    joints = list()

    for node in nodes:
        joints.extend(mc.skinCluster(getSkinCluster(node)[0], q=True, inf=True))

    return joints

def getSkinCluster(node):

    if getObjectType(node) != 'mesh':
        return None, None, None
    
    inputNodes, skinMethod, skinJoints = getInputNodes(node, inputType='skinCluster')
    if inputNodes == []:
        return None, None, None
    else:
        return inputNodes[0], skinMethod, skinJoints

def getInputNodes(node, inputType='ffd'):

    inputNodes = list()
    skinMethod = None
    skinJoints = None

    hist = mc.listHistory(node, gl=True, pdo=True)
    
    if hist != None:
        for h in hist:
            if h != 'defaultLastHiddenSet':
                if mc.objectType(h) == inputType:
                    inputNodes.append(h)
                    if inputType == 'skinCluster':
                        inputNodes = [h]
                        skinMethod = mc.getAttr('%s.skinningMethod' % h)
                        skinJoints = mc.skinCluster(h, query=True, inf=True)
                        break
                    if inputType in ['wrap', 'blendShape', 'makeNurbPlane']:
                        break

    return inputNodes, skinMethod, skinJoints

def getNodeByInput(inputNode):

    for shapeNode in mc.listConnections(inputNode, shapes=True):
        if mc.objectType(shapeNode) == 'lattice':
            latticeNode = mc.listRelatives(shapeNode, parent=True)[0]
        if mc.objectType(shapeNode) == 'baseLattice':
            baseLatticeNode = mc.listRelatives(shapeNode, parent=True)[0]

    return latticeNode, baseLatticeNode

def getNodesByAttr(attrName):

    nodes = list()

    for node in mc.ls(type='transform'):
        userAttrs = mc.listAttr(node, userDefined=True)
        if not userAttrs:
            continue
        if attrName in userAttrs:
            nodes.append(node)

    return nodes

def getNodeByCompType(compType, nodeType=None, returnAll=False):

    nodes = list()
    for node in getNodesByAttr('componentType'):
        if mc.getAttr('%s.componentType'%node) == compType:
            if nodeType:
                if getNodeType(node) == nodeType:
                    nodes.append(node)
            else:
                nodes.append(node)

    if len(nodes) > 0 and not returnAll:
        return nodes[0]

    return nodes if nodes != [] else None

def removeConnection(attr):

    mel.eval('source channelBoxCommand; CBdeleteConnection \"%s\"' % attr)

def isConnected(node, translate=True, rotate=True, scale=True, customAttrName=None):

    if customAttrName:
        attr = '%s.%s'%(node, customAttrName)
        if mc.listConnections(attr, source=True, destination=False, plugs=True) != None:
            return True
        else:
            return False

    trsList = list()
    if translate:
        trsList.append('t')
    if rotate:
        trsList.append('r')
    if scale:
        trsList.append('s')
    
    translateConnected = False
    rotateConnected = False
    scaleConnected = False

    for t, trs in enumerate(trsList):
        for axis in 'xyz':
            attr = '%s.%s%s'%(node, trs, axis)
            if mc.listConnections(attr, source=True, destination=False, plugs=True) != None:
                if trs == 't':
                    translateConnected = True
                if trs == 'r':
                    rotateConnected = True
                if trs == 's':
                    scaleConnected = True
        if mc.listConnections('%s.%s'%(node, ['translate', 'rotate', 'scale'][t]), source=True, destination=False, plugs=True) != None:
            if trs == 't':
                translateConnected = True
            if trs == 'r':
                rotateConnected = True
            if trs == 's':
                scaleConnected = True

    if translateConnected:
        return True
    if rotateConnected:
        return True
    if scaleConnected:
        return True

    return False

def addJointLabel(jointNode, side):
    
    if side == None:
        sideValue = 0
    if side == Settings.leftSide:
        sideValue = 1
    if side == Settings.rightSide:
        sideValue = 2

    mc.setAttr('%s.side'%jointNode, sideValue)
    mc.setAttr('%s.type'%jointNode, 18)
    jointLabel = createName(sourceNode=jointNode, side='remove', nodeType='remove')[0]
    mc.setAttr('%s.otherType'%jointNode, jointLabel, type='string')
    mc.setAttr('%s.displayLocalAxis'%jointNode, True)

def addNamingAttr(node, tokenTypes, namingOrder=Settings.namingOrder):

    if tokenTypes == None:
        return
    
    namingAttrName = 'namingConvention'
    namingAttr = '%s.%s'%(node, namingAttrName)
    if not mc.objExists(namingAttr):
        mc.addAttr(node, ln=namingAttrName, dt='string')
    mc.setAttr(namingAttr, lock=False)
    mc.setAttr(namingAttr, ', '.join(orderNaming(tokenTypes, namingOrder)), type='string', lock=True)

def getNamingOrder(node):

    namingAttrName = 'namingConvention'
    namingAttr = '%s.%s'%(node, namingAttrName)
    if not mc.objExists(namingAttr):
        return
    namingOrder = mc.getAttr(namingAttr).replace(' ', '').split(',')

    return namingOrder

def orderNaming(tokenTypes, namingOrder):

    if tokenTypes == None:
        return None
    
    orderedTokenTypes = list()

    for naming in namingOrder:
        for tokenType in tokenTypes:
            if naming == tokenType:
                orderedTokenTypes.append(naming)

    return orderedTokenTypes

def createTokenTypes(variables):

    tokens = list()
    for v, var in enumerate(variables):
        if var != None:
            tokens.append(['component', 'side', 'nodeType', 'element', 'indices', 'specific', 'indexFill'][v])

    return tokens

def getToken(node, tokenType):
        
    namingAttrName = 'namingConvention'
    if not mc.objExists('%s.%s'%(node, namingAttrName)):
        return None, None
    
    try:
        namingOrder = mc.getAttr('%s.%s'%(node, namingAttrName)).replace(' ', '').split(',')
        tokens = node.split(':')[-1].split('|')[-1].split('_')
    except:
        mc.error('Possible duplicate node: %s'%node)
        return
    
    # since we can have any number of index tokens, we find all tokens with digits and combine them to specify the indices token
    indexIndices = list()
    cleanedTokens = tokens[::]
    i = 0
    for t, token in enumerate(tokens):
        if token.isdigit():
            indexIndices.append(t)
            cleanedTokens.pop(t-i)
            i += 1

    if indexIndices != []:
        cleanedTokens.insert(indexIndices[0], '_'.join([tokens[x] for x in indexIndices]))
    
    if not tokenType in namingOrder:
        return None, None
    
    try:
        myIndex = namingOrder.index(tokenType)
        myToken = cleanedTokens[myIndex].split(':')[-1]
    except:
        return None, None
    
    return myToken, myIndex

def addBearVersion(node):

    sourceDir = Settings.getPath(['system', 'version.txt'])
    bearVersion = open(sourceDir).read()

    rigVersionName = 'bearVersion'
    rigVersionAttr = '%s.%s'%(node, rigVersionName)
    if not mc.objExists(rigVersionAttr):
        mc.addAttr(node, ln=rigVersionName, dt='string')
    mc.setAttr(rigVersionAttr, lock=False)
    mc.setAttr(rigVersionAttr, bearVersion, type='string', lock=True)

def camelCase(string, capitalFirst=False):
    
    string = sub(r"(_|-)+", " ", string).title().replace(" ", "")
    return ''.join([string[0] if capitalFirst else string[0].lower(), string[1:]])

def createName(component=None, 
                side=None, 
                nodeType=None, 
                element=None, 
                indices=None, 
                specific=None, 
                indexFill=2, 
                sourceNode=None, 
                useSourceIndexFill=False, 
                namingOrder=Settings.namingOrder):
    
    if sourceNode:

        # special case if sourceNode does not have naming convention. This may happen on space creation when other modules
        # haven't been built yet, or due to Maya auto-suffix like parentConstraints and such 

        if not mc.objExists('%s.namingConvention'%sourceNode):
            return sourceNode, None

        # getting the source node tokens
        
        sourceComponent = getToken(sourceNode, 'component')[0]
        sourceSide = getToken(sourceNode, 'side')[0]
        sourceNodeType = getToken(sourceNode, 'nodeType')[0]
        sourceElement = getToken(sourceNode, 'element')[0]
        sourceIndices = getToken(sourceNode, 'indices')[0]
        sourceSpecific = getToken(sourceNode, 'specific')[0]

        if useSourceIndexFill and sourceIndices:
            indexFill = len(sourceIndices)

        # if a token flag is set to False, it will be removed from the sourceNode naming

        sourceComponent = None if component == 'remove' else sourceComponent
        sourceSide = None if side == 'remove' else sourceSide
        sourceNodeType = None if nodeType == 'remove' else sourceNodeType
        sourceElement = None if element == 'remove' else sourceElement
        sourceIndices = None if indices == 'remove' else sourceIndices
        sourceSpecific = None if specific == 'remove' else sourceSpecific

        # if we have token flags, they will replace the sourceNode token

        component = component if component != None and component != 'remove' else sourceComponent
        side = side if side != None and side != 'remove' else sourceSide
        nodeType = nodeType if nodeType != None and nodeType != 'remove' else sourceNodeType
        element = element if element != None and element != 'remove' else sourceElement
        indices = indices if indices != None and indices != 'remove' else sourceIndices
        specific = specific if specific != None and specific != 'remove' else sourceSpecific

    if indices == None:
        indicesName = None
    else:
        
        if mc.about(v=True) >= '2022':
            indicesCheck = type(indices) == str
        else:
            indicesCheck = type(indices) == str or type(indices) == unicode
        if indicesCheck:
            indicesName = indices
        else:
            indexNames = list()
            if not type(indices) == list:
                if type(indices) == int:
                    indices = [indices]
                else:
                    indices = [int(indices)-1]
            for index in indices:
                if index != None:
                    indexNames.append(str(index+1).zfill(indexFill))
            indicesName = '_'.join(indexNames)

    tokens = list()
    tokenTypes = list()

    for naming in namingOrder:
        if naming == 'component' and component:
            tokens.append(component)
            tokenTypes.append(naming)
        if naming == 'side' and side:
            tokens.append(side)
            tokenTypes.append(naming)
        if naming == 'nodeType' and nodeType:
            tokens.append(nodeType)
            tokenTypes.append(naming)
        if naming == 'element' and element:
            tokens.append(element)
            tokenTypes.append(naming)
        if naming == 'indices' and indices:
            tokens.append(indicesName)
            tokenTypes.append(naming)
        if naming == 'specific' and specific:
            tokens.append(specific)
            tokenTypes.append(naming)
                
    name = '_'.join(tokens)
    
    return name, tokenTypes

def rename(node, newName, tokenTypes):

    addNamingAttr(node, tokenTypes)
    mc.rename(node, newName)

def getComponent(node):

    if node == None:
        return
    token = getToken(node, 'component')[0]
    return token

def getSide(node, byString=False, leftSide=Settings.leftSide, rightSide=Settings.rightSide):

    if node == None:
        return

    if byString:
        token = None
        if leftSide in node.split('_'):
            token = leftSide
        if rightSide in node.split('_'):
            token = rightSide
    else:
        token = getToken(node, 'side')[0]
        
    if token == leftSide:
        return leftSide
    if token == rightSide:
        return rightSide

    return None

def getNodeType(node):

    if node == None:
        return
    token = getToken(node, 'nodeType')[0]
    return token

def getElement(node):

    if node == None:
        return
    token = getToken(node, 'element')[0]
    return token

def getIndices(node):

    if node == None:
        return
    token = getToken(node, 'indices')[0]
    return token

def getSpecific(node):

    if node == None:
        return
    token = getToken(node, 'specific')[0]
    return token

def replaceToken(node, token=None, tokenType=None):

    if not node:
        return

    if '.' in node:
        tokens = node.split('|')[-1].split('.')
        node = node.split('.')
        attrName = '.'+tokens[1]
    else:
        attrName = ''

    replacedName = createName(side=token if tokenType == 'side' else None,
                                specific=token if tokenType == 'specific' else None,
                                nodeType=token if tokenType == 'nodeType' else None, 
                                element=token if tokenType == 'element' else None, 
                                indices=token if tokenType == 'indices' else None, 
                                component=token if tokenType == 'component' else None, 
                                sourceNode=node,
                                useSourceIndexFill=True)
    
    return replacedName[0]+attrName

def replaceSpecific(node, specific=None):

    return replaceToken(node, token=specific, tokenType='specific')

def replaceSide(node, side=None, byString=False):
    
    if '.' in node:
        tokens = node.split('.')
        node = tokens[0]
        attrName = '.'+tokens[1]
    else:
        attrName = ''

    # byString is used if node doesn't exist in the scene (can't use naming convention)
    if byString:
        tokens = node.split('_')
        for t, token in enumerate(tokens[::]):
            sideIndex = Settings.namingOrder.index('side')
            # NOTE output is not allowed to be used as a name
            if 'output' in tokens:
                sideIndex += 1
            if side:
                if token in [Settings.leftSide, Settings.rightSide]:
                    tokens[t] = side
                else:
                    if not Settings.leftSide in tokens and not Settings.rightSide in tokens:
                        tokens.insert(sideIndex, side)
            if side == False:
                if len(tokens) > sideIndex:
                    tokens.pop(sideIndex)
        return '_'.join(tokens)+attrName
    else:
        return replaceToken(node, token='remove' if side == None else side, tokenType='side')+attrName

def replaceNodeType(node, nodeType=None):
    
    return replaceToken(node, token=nodeType, tokenType='nodeType')

def replaceSuffix(node, suffix=None):

    nodeSplit = node.split('_')
    if len(nodeSplit) == 1:
        return node
    return '_'.join(node.split('_')[:-1]+([suffix] if suffix else []))

def addSuffix(node, suffix=None):

    if not suffix:
        return node

    node = node.split('|')[-1]

    return '_'.join(node.split('_')+[suffix])

def getSuffix(node):

    suffix = node.split('_')[-1]

    return suffix

def addNamingToRigNode(rigRoot):
    
    if not mc.objExists(rigRoot+'.namingConvention'):
        addNamingAttr(rigRoot, ['nodeType'])
    if not mc.objExists('%s.globalNamingConvention'%rigRoot):
        mc.addAttr(rigRoot, ln='globalNamingConvention', dt='string')
        mc.setAttr('%s.globalNamingConvention'%rigRoot, ', '.join(Settings.namingOrder), type='string', lock=True)
    for tokenName in [['guideRoot', Settings.guideRoot],
                        ['rigRoot', Settings.rigRoot],
                        ['geometryGroup', Settings.geometryGroup],
                        ['geometryToken', Settings.geoNodeSuffix],
                        ['guidePivotToken', Settings.guidePivotSuffix],
                        ['guideShapeToken', Settings.guideShapeSuffix],
                        ['spaceToken', Settings.offNodeSuffix],
                        ['controlToken', Settings.controlSuffix],
                        ['skinJointToken', Settings.skinJointSuffix],
                        ['leftSideToken', Settings.leftSide],
                        ['rightSideToken', Settings.rightSide]]:
        if mc.objExists('%s.%s'%(rigRoot, tokenName[0])):
            mc.setAttr('%s.%s'%(rigRoot, tokenName[0]), lock=False)
            mc.setAttr('%s.%s'%(rigRoot, tokenName[0]), tokenName[1], type='string', lock=True)
        else:
            mc.addAttr(rigRoot, ln=tokenName[0], dt='string')
            mc.setAttr('%s.%s'%(rigRoot, tokenName[0]), tokenName[1], type='string', lock=True)

def getPivotCompensate(node):
    
    if not node:
        return
    
    if not exists(node):
        return node
    
    try:
        controlNode = replaceNodeType(node, Settings.controlSuffix)
        if exists(controlNode):
            pivotCompensateNode = replaceNodeType(controlNode, Settings.pivotCompensateSuffix)
            if exists(pivotCompensateNode):
                node = pivotCompensateNode
    except:
        return node
    
    return node

def hide(node, lodVis=False):

    if mc.objExists(node):
        if lodVis:
            mc.setAttr('%s.lodVisibility'%node, False)
        else:
            mc.hide(node)

def unhide(node):

    if mc.objExists(node):
        mc.showHidden(node)

def getSize(node):

    if not exists(node):
        return 1, 1, 1, 1
    
    shapeNodes = mc.listRelatives(node, shapes=True, fullPath=True)

    sizeMinX = max([mc.getAttr(s + '.boundingBoxMinX') for s in shapeNodes])
    sizeMaxX = max([mc.getAttr(s + '.boundingBoxMaxX') for s in shapeNodes])
    sizeMinY = max([mc.getAttr(s + '.boundingBoxMinY') for s in shapeNodes])
    sizeMaxY = max([mc.getAttr(s + '.boundingBoxMaxY') for s in shapeNodes])
    sizeMinZ = max([mc.getAttr(s + '.boundingBoxMinZ') for s in shapeNodes])
    sizeMaxZ = max([mc.getAttr(s + '.boundingBoxMaxZ') for s in shapeNodes])
    
    width = abs(sizeMaxX - sizeMinX)
    height = abs(sizeMaxY - sizeMinY)
    depth = abs(sizeMaxZ - sizeMinZ)
    
    size = max(width, height, depth)
    
    return size, width, height, depth

def getObjectType(node):

    shapeList = mc.listRelatives(node, shapes=True, fullPath=True)
    if shapeList == None:
        return 'transform'
    else:
        return mc.objectType(shapeList[0])

def getComponentFromNode(node, guide=False, rig=False):

    for x in mc.ls(node, long=True)[0].split('|'):
        if mc.objExists(x):
            if 'componentType' in mc.listAttr(x, userDefined=True):
                if guide:
                    compNode = replaceNodeType(x, 'guide')
                if rig:
                    compNode = replaceNodeType(x, 'rig')
                return compNode
    return

def getComponentType(compGroup):

    if mc.objExists('%s.componentType'%compGroup):
        return mc.getAttr('%s.componentType'%compGroup)
    return None

def getComponentGroupByType(node, nodeType=Settings.guideGroup):

    for parentNode in getParents(node)+[node]:
        compType = getComponentType(parentNode)
        if compType and compType != 'Collection':
            guideComp = replaceNodeType(parentNode, nodeType)
            if guideComp:
                break
            
    return guideComp

def getComponentGroup(node):

    for parentNode in getParents(node)[::-1]:
        compType = getComponentType(parentNode)
        if compType:
            return parentNode

def componentIsAutoSided(compGroup):

    # support for older versions where rig group had no side attribute
    if not mc.objExists('%s.side'%compGroup):
        compGroup = replaceNodeType(compGroup, Settings.guideGroup)
    #
        
    if not mc.objExists('%s.side'%compGroup) and not getComponentType(compGroup) == 'Collection':
        return True
    else:
        return False

def getParent(node):

    if not exists(node):
        return
    parentNodeList = mc.listRelatives(node, parent=True)

    if parentNodeList != None:
        parentNode = parentNodeList[0]
    else:
        parentNode = None

    return parentNode

def getParents(node):

    fullName = mc.ls(node, l=True)[0]
    parentNodes = fullName.split('|')[1:-1]

    return parentNodes

def setParent(nodes, parentNode, lockRotate=False, lockScale=False, zeroValues=False):
    
    if type(nodes) != list:
        nodes = [nodes]

    parentedNodes = list()

    for node in nodes:
        
        if node == None or parentNode == None:
            return
        if not exists(node):
            return
        if mc.referenceQuery(node, isNodeReferenced=True):
            return
        
        if lockRotate:
            for axis in 'xyz':
                mc.setAttr('%s.r%s'%(node, axis), lock=True)

        if lockScale:
            for axis in 'xyz':
                mc.setAttr('%s.s%s'%(node, axis), lock=True)

        if parentNode == 'world':
            if getParent(node) != None:
                parentedNode = mc.parent(node, world=True)
                parentedNodes.extend(parentedNode)
        else:
            if getParent(node) != parentNode and parentNode != None and node != None and parentNode != []:
                if not exists(parentNode):
                    MessageHandling.warning('Parent Node does not exist: %s'%parentNode)
                    return
                parentedNode = mc.parent(node, parentNode)
                parentedNodes.extend(parentedNode)

        if zeroValues:
            setTrs(node)
            setTrs(parentNode)
            
    if len(parentedNodes) == 1:
        parentedNodes = parentedNodes[0]
    
    return parentedNodes

def isAttrSettable(attr, excludeRef=True):

    if not mc.objExists(attr):
        return None
    if excludeRef and mc.referenceQuery(attr, isNodeReferenced=True):
        return False
    if not mc.getAttr(attr, lock=True) and mc.listConnections(attr, source=True, destination=False, plugs=True) == None:
        return True
    else:
        return False
    
def isNodeConstrainable(node, trs='trs'):

    isConstrainable = True
    for t in trs:
        for axis in 'xyz':
            if not isAttrSettable('%s.%s%s'%(node, t, axis)):
                isConstrainable = False

    return isConstrainable

def getTrs(node, mirrorScale=(1, 1, 1)):
    
    trsVal = dict()
    for trs in 'trs':
        for a, axis in enumerate('xyz'):
            val = mc.getAttr('%s.%s%s'%(node, trs, axis))
            if trs == 'r':
                if getShapeType(node) == 'joint':
                    orientVal = mc.getAttr('%s.jointOrient%s'%(node, axis.upper()))
                else:
                    orientVal = 0
                trsVal['jointOrient'+axis.upper()] = orientVal
            if trs == 't':
                trsVal[trs+axis] = val * mirrorScale[a]
            if trs == 'r':
                trsVal[trs+axis] = val + (-180 if mirrorScale[a] == -1 else 0)
            if trs == 's':
                trsVal[trs+axis] = val
    
    return trsVal

def setTrs(node, value=None, trsVal=None, t=True, r=True, s=True):

    trs = ''
    if t:
        trs += 't'
    if r:
        trs += 'r'
    if s:
        trs += 's'
        
    vals = dict()

    for x in trs:
        for axis in 'xyz':
            attrName = '%s%s'%(x, axis)
            attr = '%s.%s'%(node, attrName)
            if isAttrSettable(attr, excludeRef=False):
                vals[attrName] = mc.getAttr(attr)
                v = value
                if value == None and t == True and r == True and s == True:
                    v = 1 if x == 's' else 0
                if trsVal != None:
                    if attrName in trsVal:
                        v = trsVal[attrName]
                if v != None:
                    mc.setAttr(attr, v)

    if mc.objectType(node) == 'joint' and r:
        for axis in 'XYZ':
            if trsVal:
                orientVal = trsVal['jointOrient'+axis]
            else:
                orientVal = 0
            mc.setAttr('%s.jointOrient%s'%(node, axis), orientVal)

    return vals

def getChildGuideJoint(node, nodeType=Settings.guidePivotSuffix):
    
    childNode = getChild(node, nodeType)
    if getShapeType(childNode) != 'joint':
        return
    return childNode

def getChild(node, nodeType=None):

    childNodes = getChildren(node)
    childNode = childNodes[0] if childNodes else None
    if getNodeType(childNode) != nodeType:
        return
    return childNode

def getChildren(node, longName=False):

    if not node:
        return
    childNodes = mc.listRelatives(node, children=True, type='transform', fullPath=longName)
    if not childNodes:
        childNodes = []
    return childNodes

def putInOrder(node, orderIndex):

    parentNode = getParent(node)
    if parentNode == None or orderIndex == None:
        return
    childOrder = mc.listRelatives(parentNode, children=True)
    mc.reorder(node, r=orderIndex-len(childOrder)+1)

def fixDuplicateNames(nodeList=mc.ls(long=True, dag=True)):

    for n, node in enumerate(reversed(nodeList)):

        if len(mc.ls(node.split('|')[-1])) > 1:

            renamedNode = mc.rename(node, node.split('|')[-1]+str(n).zfill(2)+'_')

            print(node.split('|')[-1], ' renamed to ', renamedNode)

def convertToBezier(curveNode):

    numSpans = mc.getAttr('%s.spans'%curveNode)

    trsList = [mc.xform('%s.ep[%s]'%(curveNode, p), translation=True, worldSpace=True, query=True)
               for p in range(numSpans)]

    mc.curve()

def convertJointRotToOrientSkeleton(jointNode):
        
    local_rot = mc.getAttr(jointNode + '.rotate')
    mc.setAttr(jointNode + '.jointOrient', *local_rot[0])
    mc.setAttr(jointNode + '.rotate', 0, 0, 0)

def convertJointRotToOrient(jointNode):
    
    mc.makeIdentity(jointNode, a=True, r=True)

def convertAxisToVector(axis, direction=None):

    axis = axis.lower()
    if not direction:
        direction = -1 if '-' in axis else 1

    if 'x' in axis:
        vector = (direction, 0, 0)
    if 'y' in axis:
        vector = (0, direction, 0)
    if 'z' in axis: 
        vector = (0, 0, direction)

    return vector

def convertAimAxis(lengthAxis, upAxis):

    lengthAxis = lengthAxis.upper()
    upAxis = upAxis.upper()

    upVal = -1 if '-' in upAxis else 1

    aimVal = -1 if '-' in lengthAxis else 1

    if 'X' in upAxis:
        upVector = (upVal, 0, 0)
    if 'Y' in upAxis:
        upVector = (0, upVal, 0)
    if 'Z' in upAxis: 
        upVector = (0, 0, upVal)
    
    if 'X' in lengthAxis:
        aimVector = (aimVal, 0, 0)
    if 'Y' in lengthAxis:
        aimVector = (0, aimVal, 0)
    if 'Z' in lengthAxis: 
        aimVector = (0, 0, aimVal)

    return aimVector, upVector

def getRotateOrder(lengthAxis, upAxis, getIndex=True):

    lengthAxis = lengthAxis.replace('-', '')
    upAxis = upAxis.replace('-', '')
    secAxis = 'xyz'.replace(lengthAxis, '').replace(upAxis, '')
    rotateOrder = upAxis+secAxis+lengthAxis
    
    if getIndex:
        return ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx'].index(rotateOrder)
    else:
        return rotateOrder

def alignObject(sourceObj, targetObj, translation=True, rotation=True, scale=False, oldStyle=False):

    if '.vtx' in targetObj or '.pt' in targetObj or '.cv' in targetObj:
        tObjTrs = mc.xform(targetObj, q=True, translation=True, ws=True)
    else:
        tObjTrs = mc.xform(targetObj, q=True, rp=True, ws=True)

    tObjRot = mc.xform(targetObj, q=True, rotation=True, ws=True)
    tObjScl = mc.xform(targetObj, q=True, scale=True, os=True, r=True)

    if type(rotation) is list:

        if not rotation[0]:
            tObjRot[0] = 0
        if not rotation[1]:
            tObjRot[1] = 0
        if not rotation[2]:
            tObjRot[2] = 0

        mc.xform(sourceObj, rotation=tObjRot, ws=True)
    
    if oldStyle:
        if translation:
            mc.xform(sourceObj, translation=tObjTrs, ws=True)
        if rotation:
            mc.xform(sourceObj, rotation=tObjRot, ws=True)
        if scale:
            mc.xform(sourceObj, scale=tObjScl, os=True, r=True)
    else:
        mc.matchTransform(sourceObj, targetObj, position=translation, rotation=rotation, scale=scale)
        
    mc.select(clear=True)

def connectGlobalScale(globalScaleNode, trgNodes, geoNodes=None):

    for trgNode in trgNodes:
        mc.connectAttr(f'{globalScaleNode}.globalScale', f'{trgNode}.globalScale')

    if geoNodes:
        for geoNode in geoNodes:
            for inputType in ['proximityWrap', 'deltaMush']:
                inputNodes = getInputNodes(geoNode, inputType)[0]
                if inputNodes:
                    for inputNode in inputNodes:
                        if inputType == 'proximityWrap':
                            mc.connectAttr(f'{globalScaleNode}.globalScale', f'{inputNode}.scaleCompensation')
                        if inputType == 'deltaMush':
                            for axis in 'XYZ':
                                mc.connectAttr(f'{globalScaleNode}.globalScale', f'{inputNode}.scale{axis}')

def multiplyGlobalScale(globalScaleNode, trgAttr):

    globalScaleAttr = f'{globalScaleNode}.globalScale'

    destConns = mc.listConnections(trgAttr, source=False, destination=True, plugs=True, connections=True) or []

    for i in range(0, len(destConns), 2):
        sourceAttr = destConns[i]
        destAttr = destConns[i+1]
        childNode = destAttr.split('.')[0]
        sourceNode = sourceAttr.split('.')[0]
        if sourceNode == childNode:
            continue
        mc.disconnectAttr(trgAttr, destAttr)
        mulNode(trgAttr,
                globalScaleAttr,
                destAttr)

def applyGlobalScale(globalScaleNode, trgNodes=[], lock=False, connect=True):

    if not mc.objExists(globalScaleNode+'.globalScale'):
        mc.addAttr(globalScaleNode, at='float', ln='globalScale', dv=1, hasMinValue=True, minValue=0.01, keyable=True)
    if connect:
        for axis in 'xyz':
            mc.setAttr('%s.s%s' % (globalScaleNode, axis), lock=False)
            if not isConnected(globalScaleNode, customAttrName='s%s'%axis):
                mc.connectAttr('%s.globalScale' % (globalScaleNode), '%s.s%s' % (globalScaleNode, axis))
    for trgNode in trgNodes+[globalScaleNode]:
        lockAndHideAttributes(trgNode, s=[True, True, True])
    mc.setAttr(globalScaleNode+'.globalScale', lock=lock)

def getAssetNode(assetName=None):

    assetNode = None

    for topLevelNode in mc.ls(assemblies=True)[::-1]:
        assetAttr = topLevelNode+'.asset'
        if mc.objExists(assetAttr) and not mc.referenceQuery(topLevelNode, isNodeReferenced=True):
            if assetName == None:
                if mc.getAttr(assetAttr):
                    assetNode = topLevelNode
                    assetName = mc.getAttr(assetAttr)
            else:
                if mc.getAttr(assetAttr) == assetName:
                    assetNode = topLevelNode

    return assetNode, assetName

def getTransformNode(shapeNode):

    shapeList = mc.listRelatives(shapeNode, parent=True, fullPath=True)
    if shapeList != None:
        return shapeList[0]
    return None

def getShapes(node):

    shapeList = mc.listRelatives(node, shapes=True, fullPath=True)
    if shapeList != None:
        return shapeList
    return None

def getShapeType(node):

    if node == None:
        return None

    shapeList = mc.listRelatives(node, shapes=True, fullPath=True)
    if shapeList != None:
        return mc.objectType(shapeList[0])
    else:
        if mc.objectType(node) == 'joint':
            return 'joint'
        else:
            return 'transform'

def getAllParents(childNode):

    if childNode == None:
        return []
    selNodes = mc.ls(childNode, l=True)
    if selNodes != []:
        parentNodes = selNodes[0].split('|')
        parentNodes.pop(0)

    return parentNodes

def getParentNodeByString(startswith=None, endswith=None, node=None):
    
    if node:
        selection = [node]
    else:
        selection = mc.ls(sl=True)
        if not selection:
            return
    targetNode = None
    for selNode in selection:
        for parent in getAllParents(selNode)+[selNode]:
            if startswith:
                starthit = parent.startswith(startswith)
            else:
                starthit = True
            if endswith:
                endhit = parent.endswith(endswith)
            else:
                endhit = True
            if starthit and endhit:
                targetNode = parent 
                break

    return targetNode
    
def renameHierarchy(rootNode, name, newName, includeRoot=True):

    nodes = getAllChildren(rootNode, includeRoot=includeRoot, fullPath=True, type=['transform', 'nurbsCurve'])
    mc.select(nodes)
    mel.eval("searchReplaceNames %s %s selected"%(name, newName))

def renameToNamingConvention(namingOrder, parentGroup=None):

    if parentGroup:
        nodes = [x for x in getAllChildren(parentGroup) if mc.objExists('%s.namingConvention'%x)][::-1]
    else:
        nodes = [x for x in mc.ls() if mc.objExists('%s.namingConvention'%x)][::-1]

    for node in nodes:
        namingConvention = mc.getAttr('%s.namingConvention'%node)
        if len(node.split('_')) != len(namingConvention.split(',')):
            continue
        newName = createName(sourceNode=node,
                                    namingOrder=namingOrder)
        node = mc.rename(node, newName[0])
        addNamingAttr(node, newName[1], namingOrder=namingOrder)
    
    for rigNode in [Settings.guideRoot, Settings.rigRoot]:
        if mc.objExists('%s.globalNamingConvention'%rigNode):
            mc.setAttr('%s.globalNamingConvention'%rigNode, lock=False)
            mc.setAttr('%s.globalNamingConvention'%rigNode, ', '.join(namingOrder), type='string', lock=True)

def isBearNode(node):

    if mc.objExists('%s.namingConvention'%node):
        return True

def getAllChildren(node, nodeType=None, fullPath=False, includeRoot=False, type=['transform']):
    
    if not exists(node):
        return []
    
    childNodes = mc.listRelatives(node, allDescendents=True, type=type, fullPath=fullPath)

    if childNodes == None:
        childNodes = []
    
    if nodeType != None:
        childNodes = [x for x in childNodes if getToken(x, 'nodeType')[0] == nodeType]

    if includeRoot and node:
        childNodes.append(mc.ls(node, l=fullPath)[0])

    return childNodes

def getAllRelatedChildNodes(rootNode):

    # was in use once for performance rig
    allNodes = list()
    childNodes = getAllChildren(rootNode, allNodes=True)
    allNodes.extend(childNodes)
    for childNode in childNodes:
        inputNodesFuture = mc.listHistory(childNode, future=True, pruneDagObjects=True)
        inputNodesAllFuture = mc.listHistory(childNode, allFuture=True, pruneDagObjects=True)
        inputNodesGroupLevels = mc.listHistory(childNode, groupLevels=True, pruneDagObjects=True)
        if inputNodesFuture != None:
            allNodes.extend(inputNodesFuture)
        if inputNodesAllFuture != None:
            allNodes.extend(inputNodesAllFuture)
        if inputNodesGroupLevels != None:
            allNodes.extend(inputNodesGroupLevels)

    return allNodes

def renameLimbChain(chain, chainType, side, component, upperName, lowerName, endName, digitsName, quadruped=False):

    renamedChain = []

    for o, obj in enumerate(chain):

        partName = [upperName, lowerName, endName, digitsName][o]

        nodeType = chainType
        if chainType == 'blend':
            if (partName == endName and not quadruped) or partName == digitsName:
                nodeType = Settings.skinJointSuffix

        name = createName(component, side, nodeType, element=partName)
        renamedObj = mc.rename(obj, name[0])
        addNamingAttr(renamedObj, name[1])

        renamedChain.append(renamedObj)

    return renamedChain

def negateConnect(sourceAttr, targetAttr, sourceNode=None):
    
    neg = mulNode(sourceAttr,
                -1,
                sourceNode=sourceNode)
    addNode('%s.output'%neg,
                1,
                targetAttr,
                sourceNode=sourceNode)

def addNode(input1, 
            input2, 
            output=None, 
            specific=None,
            sourceNode=None):

    node = mulNode(input1, 
                    input2, 
                    output, 
                    specific=specific, 
                    utilityType='addDoubleLinear',
                    sourceNode=sourceNode)

    return node

def plusNode(input1, 
             input2, 
             output=None, 
             axis='XYZ',
             operation=1,  # 1: Sum, 2: Subtract
             specific=None,
             sourceNode=None):
    """
    Creates a plusMinusAverage node to process scalar or vector (XYZ) inputs dynamically in Maya.

    Args:
        input1 (str/int/float): First input attribute or value (scalar/vector).
        input2 (str/int/float): Second input attribute or value (scalar/vector).
        output (str): Optional output attribute to connect the result.
        axis (str): Specifies the axis to operate on ('X', 'Y', 'Z', or 'XYZ').
        operation (int): Operation mode of the node (default is 1: sum).
        specific (str): Specific name for the node (if not autogenerated).
        sourceNode (str): Optional source node for name generation.

    Returns:
        str: The name of the created plusMinusAverage node.
    """
    # Normalize the axis input
    if axis:
        axis = axis.upper()
    else:
        axis = 'XYZ'

    # Determine naming specifics
    if output:
        if not sourceNode:
            sourceNode = output.split('.')[0]
        attrName = output.split('.')[1]
        specific = makeUniqueSpecific(sourceNode, specific, attrName)
    else:
        if not sourceNode:
            sourceNode = input1.split('.')[0]
        attrName = input1.split('.')[1]
        specific = makeUniqueSpecific(sourceNode, specific, attrName)

    # Create a unique name for the node
    name = createName(nodeType="plusMinusAverage", specific=specific, sourceNode=sourceNode)
    node = name[0]

    # Create the node if it doesn't exist
    if not mc.objExists(node):
        mc.shadingNode('plusMinusAverage', asUtility=True, name=node)
        mc.setAttr(f'{node}.operation', operation)

    # Add naming attributes for metadata
    addNamingAttr(node, name[1])

    # Helper function to connect or set attributes
    def connect_or_set(attr, value, index):
        if isinstance(value, (int, float)):  # Scalar input
            mc.setAttr(f'{node}.{attr}[{index}]', value, value, value, type='double3')
        elif isinstance(value, (list, tuple)):  # Vector input
            mc.setAttr(f'{node}.{attr}[{index}]', *value, type='double3')
        else:  # Attribute connection
            if any(keyword in value for keyword in ['translate', 'rotate', 'scale']):
                mc.connectAttr(value, f'{node}.{attr}[{index}]', force=True)
            else:
                raise ValueError(f"Invalid value for attribute: {value}")

    # Connect input1 and input2 to the node
    if input1:
        connect_or_set('input3D', input1, 0)
    if input2:
        connect_or_set('input3D', input2, 1)

    # Connect the output if specified
    if output:
        mc.connectAttr(f'{node}.output3D', output, force=True)

    return node

def mulNode(input1, 
            input2, 
            output=None, 
            specific=None,
            utilityType='multDoubleLinear',
            sourceNode=None):

    nodeType = Settings.mulNodeSuffix if utilityType == 'multDoubleLinear' else Settings.addNodeSuffix
    if output:
        if not sourceNode:
            sourceNode = output.split('.')[0]
        attrName = output.split('.')[1]
        specific = makeUniqueSpecific(sourceNode, specific, attrName)
    else:
        if not sourceNode:
            sourceNode = input1.split('.')[0]
        attrName = input1.split('.')[1]
        specific = makeUniqueSpecific(sourceNode, specific, attrName)

    name = createName(nodeType=nodeType, specific=specific, sourceNode=sourceNode)
    node = mc.shadingNode(utilityType, asUtility=True, name=name[0])
    addNamingAttr(node, name[1])
    
    if input1:
        if type(input1) == int or type(input1) == float:
            mc.setAttr('%s.input1'%node, input1)
        else:
            mc.connectAttr(input1, '%s.input1' % node)
    if input2:
        if type(input2) == int or type(input2) == float:
            mc.setAttr('%s.input2'%node, input2)
        else:
            mc.connectAttr(input2, '%s.input2' % node)
    if output:
        mc.connectAttr('%s.output' % node, output, f=True)

    return node

def divNode(input1, 
            input2, 
            output=None, 
            axis='X',
            operation=2, # 0: no operation, 1: multiply, 2: divide, 3:power
            specific=None,
            sourceNode=None):

    if axis:
        axis = axis.upper()
    else:
        axis = 'XYZ'

    if output:
        if not sourceNode:
            sourceNode = output.split('.')[0]
        attrName = output.split('.')[1]
        specific = makeUniqueSpecific(sourceNode, specific, attrName)
    else:
        if not sourceNode:
            sourceNode = input1.split('.')[0]
        attrName = input1.split('.')[1]
        specific = makeUniqueSpecific(sourceNode, specific, attrName)

    name = createName(nodeType=Settings.divNodeSuffix, specific=specific, sourceNode=sourceNode)
    
    node = name[0]
    if not mc.objExists(node):
        mc.shadingNode('multiplyDivide', asUtility=True, name=node)
        mc.setAttr('%s.operation'%node, operation)
        
    addNamingAttr(node, name[1])

    if len(axis) == 1:
            
        if input1:
            if type(input1) == int or type(input1) == float:
                if axis:
                    mc.setAttr('%s.input1.input1%s'%(node, axis), input1)
                else:
                    [mc.setAttr('%s.input1.input1%s'%(node, a), input1) for a in 'XYZ']
            else:
                if axis:
                    mc.connectAttr(input1, '%s.input1.input1%s'%(node, axis))
                else:
                    mc.connectAttr(input1, '%s.input1'%(node))
        if input2:
            if type(input2) == int or type(input2) == float:
                if axis:
                    mc.setAttr('%s.input2.input2%s'%(node, axis), input2)
                else:
                    [mc.setAttr('%s.input2.input2%s'%(node, a), input2) for a in 'XYZ']
            else:
                if axis:
                    mc.connectAttr(input2, '%s.input2.input2%s'%(node, axis))
                else:
                    mc.connectAttr(input2, '%s.input2'%(node))
        if output:
            if axis:
                mc.connectAttr('%s.output.output%s'%(node, axis), output, f=True)
            else:
                mc.connectAttr('%s.output'%(node), output, f=True)

    else:
    
        if input1:
            if isinstance(input1, (int, float)):
                [mc.setAttr('%s.input1.input1%s'%(node, a), input1) for a in axis]
            elif any(keyword in input1 for keyword in ['translate', 'rotate', 'scale']):
                if 'output3D' in input1:
                    [mc.connectAttr(input1+a.lower(), '%s.input1.input1%s'%(node, a)) for a in axis]
                else:
                    [mc.connectAttr(input1+a, '%s.input1.input1%s'%(node, a)) for a in axis]
            else:
                [mc.connectAttr(input1, '%s.input1.input1%s'%(node, a)) for a in axis]
        if input2:
            if isinstance(input2, (int, float)):
                [mc.setAttr('%s.input2.input2%s'%(node, a), input2) for a in axis]
            elif any(keyword in input2 for keyword in ['translate', 'rotate', 'scale']):
                if 'output3D' in input2:
                    [mc.connectAttr(input2+a.lower(), '%s.input1.input1%s'%(node, a)) for a in axis]
                else:
                    [mc.connectAttr(input2+a, '%s.input2.input2%s'%(node, a)) for a in axis]
            elif axis:
                [mc.connectAttr(input2, '%s.input2.input2%s'%(node, a)) for a in axis]
        if output:
            [mc.connectAttr('%s.output.output%s'%(node, a), output+a) for a in axis]

    return node

def clampNode(input, 
            clampMin=None,
            clampMax=None, 
            output=None, 
            specific=None,
            sourceNode=None):

    nodeType = Settings.clampNodeSuffix
    if output:
        if not sourceNode:
            sourceNode = output.split('.')[0]
        attrName = output.split('.')[1]
        specific = makeUniqueSpecific(sourceNode, specific, attrName)
    else:
        if not sourceNode:
            sourceNode = input.split('.')[0]
        attrName = input.split('.')[1]
        specific = makeUniqueSpecific(sourceNode, specific, attrName)

    name = createName(nodeType=nodeType, specific=specific, sourceNode=sourceNode)
    node = mc.shadingNode('clamp', asUtility=True, name=name[0])
    addNamingAttr(node, name[1])

    if clampMin == None:
        clampMin = -10000
    if clampMax == None:
        clampMax = 10000
    mc.setAttr('%s.minR' % node, clampMin)
    mc.setAttr('%s.maxR' % node, clampMax)
    
    if input:
        mc.connectAttr(input, '%s.inputR' % node)
    if output:
        mc.connectAttr('%s.outputR' % node, output, f=True)

    return node

def conditionNode(firstTerm,
                    secondTerm,
                    input1, 
                    input2, 
                    output=None, 
                    sourceNode=None):

    nodeType = Settings.conditionNodeSuffix
    if output:
        if not sourceNode:
            sourceNode = output.split('.')[0]
        attrName = output.split('.')[1]
        specific = makeUniqueSpecific(sourceNode, specific, attrName)
    else:
        if not sourceNode:
            sourceNode = input.split('.')[0]
        attrName = input.split('.')[1]
        specific = makeUniqueSpecific(sourceNode, specific, attrName)

    name = createName(nodeType=nodeType, specific=specific, sourceNode=sourceNode)
    node = mc.shadingNode('condition', asUtility=True, name=name[0])
    addNamingAttr(node, name[1])
    
    if type(firstTerm) == int or type(firstTerm) == float:
        mc.setAttr('%s.firstTerm'%node, firstTerm)
    else:
        mc.connectAttr(firstTerm, '%s.firstTerm'%node)

    if type(secondTerm) == int or type(secondTerm) == float:
        mc.setAttr('%s.secondTerm'%node, secondTerm)
    else:
        mc.connectAttr(secondTerm, '%s.secondTerm'%node)

    for n, v in enumerate('RGB'):
        if type(input1) == int or type(input1) == float:
            mc.setAttr('%s.colorIfTrue%s'%(node, v), input1[n])
        else:
            mc.connectAttr(input1[n], '%s.colorIfTrue%s'%(node, v))
        if type(input2) == int or type(input2) == float:
            mc.setAttr('%s.colorIfFalse%s'%(node, v), input2[n])
        else:
            mc.connectAttr(input2[n], '%s.colorIfFalse%s'%(node, v))
        if output:
            mc.connectAttr('%s.outColor.outColor%s'%(node, v), output[n])

def scriptNode(script,
               sourceNode=None):

    nodeType = Settings.scriptNode

    name = createName(nodeType=nodeType, sourceNode=sourceNode)
    node = mc.scriptNode(beforeScript=script, name=name[0], sourceType=1)
    mc.setAttr('%s.sourceType'%node, 1)
    addNamingAttr(node, name[1])

    return node

def pointOnCurveNode(node,
                    curveNode, 
                    nodeType=Settings.motionPathSuffix,
                    lengthAxis='X',
                    upAxis='Z',
                    upNode=None,
                    upNodeType='object',
                    fractionMode=True,
                    uValue=None):

    upVal = -1 if '-' in upAxis else 1
    frontVal = -1 if '-' in lengthAxis else 1
    lengthAxis = lengthAxis.lower()
    upAxis = upAxis.lower()

    if upNodeType == 'objectrotation':
        worldUpType = 2
        worldUpObjectNode = upNode
    elif upNodeType == 'object':
        worldUpType = 1
        worldUpObjectNode = upNode
    else:
        worldUpType = 0
        worldUpObjectNode = None

    name = createName(nodeType=nodeType, sourceNode=node)

    pointOnCurveNode = mc.shadingNode('pointOnCurveInfo', 
                                asUtility=True,
                                name=name[0])

    addNamingAttr(pointOnCurveNode, name[1])
    
    mc.connectAttr('%s.worldSpace[0]'%curveNode, '%s.inputCurve'%pointOnCurveNode)
    mc.connectAttr('%s.position'%pointOnCurveNode, '%s.translate'%node)

    if worldUpObjectNode:
        mc.tangentConstraint(curveNode, 
                            node,
                            aimVector=convertAxisToVector(lengthAxis, frontVal),
                            upVector=convertAxisToVector(upAxis, upVal),
                            worldUpObject=worldUpObjectNode,
                            worldUpType=worldUpType,
                            worldUpVector=convertAxisToVector(upAxis, upVal))
    else:
        mc.tangentConstraint(curveNode, 
                            node,
                            aimVector=convertAxisToVector(lengthAxis, frontVal),
                            upVector=convertAxisToVector(upAxis, upVal),
                            worldUpType=worldUpType,
                            worldUpVector=convertAxisToVector(upAxis, upVal))
    
    if uValue != None:
        mc.setAttr('%s.parameter'%pointOnCurveNode, uValue)

    return pointOnCurveNode

def motionPathNode(node,
                    curveNode, 
                    nodeType=Settings.motionPathSuffix,
                    lengthAxis='X',
                    upAxis='Z',
                    upNode=None,
                    upNodeType='object',
                    fractionMode=True,
                    uValue=None):
    
    upVal = -1 if '-' in upAxis else 1
    frontVal = True if '-' in lengthAxis else False
    lengthAxis = lengthAxis.lower()
    upAxis = upAxis.lower()
    
    if 'x' in upAxis:
        worldUpVector = (upVal, 0, 0)
        upAxisVal = 0
    if 'y' in upAxis:
        worldUpVector = (0, upVal, 0)
        upAxisVal = 1
    if 'z' in upAxis: 
        worldUpVector = (0, 0, upVal)
        upAxisVal = 2
        
    if 'x' in lengthAxis:
        lengthAxisVal = 0
    if 'y' in lengthAxis:
        lengthAxisVal = 1
    if 'z' in lengthAxis: 
        lengthAxisVal = 2

    if upNodeType == 'objectrotation':
        worldUpType = 2
        worldUpObjectNode = upNode
        followState = True
    elif upNodeType == 'object':
        worldUpType = 1
        worldUpObjectNode = upNode
        followState = True
    else:
        worldUpType = 0
        worldUpObjectNode = None
        followState = False

    name = createName(nodeType=nodeType, sourceNode=node)

    motionPath = mc.shadingNode('motionPath', 
                                asUtility=True,
                                name=name[0])

    addNamingAttr(motionPath, name[1])
    
    mc.connectAttr('%s.worldSpace[0]'%curveNode, '%s.geometryPath'%motionPath)
    mc.connectAttr('%s.allCoordinates'%motionPath, '%s.translate'%node)
    if followState:
        mc.connectAttr('%s.rotate'%motionPath, '%s.rotate'%node)
        mc.connectAttr('%s.rotateOrder'%motionPath, '%s.rotateOrder'%node)
    mc.setAttr('%s.fractionMode'%motionPath, fractionMode)
    mc.setAttr('%s.worldUpType'%motionPath, worldUpType)
    mc.setAttr('%s.worldUpVectorX'%motionPath, worldUpVector[0])
    mc.setAttr('%s.worldUpVectorY'%motionPath, worldUpVector[1])
    mc.setAttr('%s.worldUpVectorZ'%motionPath, worldUpVector[2])
    if worldUpObjectNode:
        mc.connectAttr('%s.worldMatrix[0]'%worldUpObjectNode, '%s.worldUpMatrix'%motionPath)
    mc.setAttr('%s.frontAxis'%motionPath, lengthAxisVal)
    mc.setAttr('%s.inverseFront'%motionPath, frontVal)
    mc.setAttr('%s.upAxis'%motionPath, upAxisVal)

    if uValue != None:
        mc.setAttr('%s.uValue'%motionPath, uValue)

    return motionPath

def curveInfoNode(curveNode, nodeType=Settings.curveInfoSuffix):
    
    name = createName(nodeType=nodeType, sourceNode=curveNode)

    curveShape = mc.listRelatives(curveNode, shapes=True)[0]
    curveInfoNode = mc.shadingNode('curveInfo', asUtility=True, name=name[0])
    mc.connectAttr('%s.worldSpace[0]' % (curveShape), '%s.inputCurve' % (curveInfoNode))

    addNamingAttr(curveInfoNode, name[1])

    return curveInfoNode

def makeUniqueSpecific(sourceNode=None, specific=None, customName=None):
    
    if sourceNode:
        nodeType = getNodeType(sourceNode)
    else:
        nodeType = None
    specificUnique = nodeType if nodeType else ''
    if customName:
        specificUnique = specificUnique + customName[0].upper() + customName[1:]
    if specific:
        specificUnique = specificUnique + specific[0].upper() + specific[1:]

    return specificUnique

def exprNode(attr, expr, specific=None, alwaysEvaluate=False):

    sourceNode = attr.split('.')[0]
    attrName = attr.split('.')[1]

    exprName = createName(nodeType=Settings.expressionSuffix, specific=makeUniqueSpecific(sourceNode, specific, attrName), sourceNode=sourceNode)
    node = mc.expression(attr, string=expr, name=exprName[0], alwaysEvaluate=alwaysEvaluate)
    addNamingAttr(node, exprName[1])

    return node

def utilityNode(sourceNode=None,
                component=None,
                side=None,
                nodeType='closestPointOnSurface',
                element=None,
                indices=None,
                specific=None,
                indexFill=2):

    name = createName(component, side, nodeType, element, indices, makeUniqueSpecific(sourceNode, specific), indexFill, sourceNode)
    node = mc.createNode(nodeType, name=name[0])
    addNamingAttr(node, name[1])

    return node

def clusterNode(node=None,
                component=None,
                side=None,
                nodeType=Settings.clusterHandleSuffix,
                element=None,
                indices=None,
                specific=None,
                indexFill=2):

    sourceNode = node.split('.')[0]
    if not mc.objExists('%s.namingConvention'%sourceNode):
        sourceNode = None
    
    handleName = createName(component, side, nodeType, element, indices, specific, indexFill, sourceNode)
    
    clusterName = createName(component, 
                            side, 
                            Settings.clusterSuffix if nodeType == Settings.clusterHandleSuffix else Settings.guideClusterSuffix, 
                            element, 
                            indices, 
                            specific, 
                            indexFill, 
                            sourceNode)
    clusterNodes = mc.cluster(node, name=handleName[0])
    clusterNode = mc.rename(clusterNodes[0], clusterName[0])
    addNamingAttr(clusterNode, clusterName[1])
    handleNode = mc.rename(clusterNodes[1], handleName[0])
    addNamingAttr(handleNode, handleName[1])

    return handleNode

def curveNode(component=None,
                side=None,
                nodeType=Settings.curveSuffix,
                element=None,
                indices=None,
                indexFill=2,
                pointCount=8,
                alignAxis='x',
                curveType='nurbsCurve',
                inheritsTransform=False,
                sourceNode=None):

    alignAxis = alignAxis.lower()

    curveName = createName(component, side=side, nodeType=nodeType, element=element, indices=indices, indexFill=indexFill, sourceNode=sourceNode)
    
    cvCount = pointCount*3-2 if curveType == 'bezierCurve' else pointCount
    keyCount = pointCount-4 if curveType == 'nurbsCurve' else pointCount
    curveTypeFlag = '-bezier' if curveType == 'bezierCurve' else ''
    pointFlag = ''
    keyFlag = ''
    
    for p in range(cvCount):
        pos = str((float(10)/cvCount)*p)
        if 'x' in alignAxis:
            pointFlag += '-p %s 0 0 ' % pos
        if 'y' in alignAxis:
            pointFlag += '-p 0 %s 0 ' % pos
        if 'z' in alignAxis:
            pointFlag += '-p 0 0 %s ' % pos
            
    if curveType == 'bezierCurve':
        degreeVal = 3
        for k in range(keyCount):
            keyFlag += '-k {0} -k {0} -k {0} '.format(k)
    elif curveType == 'nurbsCurve':
        degreeVal = 3
        for k in range(keyCount):
            keyFlag += '-k {0} '.format(k+1)
        keyFlag = '-k 0 -k 0 -k 0 ' + keyFlag + '-k {0} -k {0} -k {0} '.format(keyCount+1)
    else:
        degreeVal = 1
        for k in range(keyCount):
            keyFlag += '-k {0} '.format(k)
            
    curveVal = 'curve {0} -d {3} {1} {2}'.format(curveTypeFlag, pointFlag, keyFlag, degreeVal)
    curveNode = mel.eval(curveVal)
    
    curveNode = mc.rename(curveNode, curveName[0])
    addNamingAttr(curveNode, curveName[1])

    Color.setColor(curveNode, 'Bright Orange')
    
    mc.setAttr('%s.inheritsTransform'%curveNode, inheritsTransform)

    return curveNode, cvCount

def ikHandleNode(startJoint,
                    endJoint,
                    component=None,
                    side=None,
                    nodeType=Settings.ikHandleSuffix,
                    element=None,
                    specific=None,
                    indices=None,
                    indexFill=2,
                    ikType='ikRPsolver'):

    mel.eval("setToolTo $gSelect")
    ikHandleName = createName(component, side, nodeType, element, indices, indexFill=indexFill, specific=specific, sourceNode=startJoint)
    ikHandleNode = mc.ikHandle(startJoint=startJoint, 
                                endEffector=endJoint, 
                                solver=ikType,
                                name=ikHandleName[0])[0]
    addNamingAttr(ikHandleNode, ikHandleName[1])

    alignObject(ikHandleNode, endJoint)

    return ikHandleNode

def latticeNode(geoNodes=None,
                component=None,
                side=None,
                nodeType=Settings.latticeNodeSuffix,
                element=None,
                indices=None,
                specific=None,
                indexFill=2,
                sourceNode=None,
                divisions=(2, 2, 2)):

    latName = createName(component, side, nodeType, element, indices, indexFill=indexFill, specific=specific, sourceNode=sourceNode)

    latNodes = mc.lattice(geoNodes, 
                            divisions=divisions, 
                            name=latName[0], 
                            objectCentered=False)
    mc.setAttr('%s.outsideLattice'%latNodes[0], 1)
    mc.setAttr('%s.inheritsTransform'%latNodes[1], False)

    addNamingAttr(latNodes[1], latName[1])

    return latNodes

def orientConstraint(sourceNodes, targetNode, nodeType=Settings.orientConstraintSuffix, mo=False):
    
    constraintName = createName(sourceNode=targetNode, nodeType=nodeType)
    constraintNode = mc.orientConstraint(sourceNodes, targetNode, mo=mo)[0]
    mc.setAttr('%s.interpType'%constraintNode, 2)
    addNamingAttr(constraintNode, constraintName[1])

    return constraintNode

def pointConstraint(sourceNodes, targetNode, nodeType=Settings.pointConstraintSuffix):

    constraintName = createName(sourceNode=targetNode, nodeType=nodeType)
    constraintNode = mc.pointConstraint(sourceNodes, targetNode, mo=False)[0]
    addNamingAttr(constraintNode, constraintName[1])

    return constraintNode

def parentConstraint(sourceNodes, targetNode, skipTranslate=[], skipRotate=[], nodeType=Settings.parentConstraintSuffix, mo=True):

    constraintName = createName(sourceNode=targetNode, nodeType=nodeType)
    constraintNode = mc.parentConstraint(sourceNodes, targetNode, skipTranslate=skipTranslate, skipRotate=skipRotate, mo=mo)[0]
    mc.setAttr('%s.interpType'%constraintNode, 2)
    addNamingAttr(constraintNode, constraintName[1])

    return constraintNode

def poleVectorConstraint(sourceNode, targetNode, nodeType=Settings.poleVectorConstraintSuffix):

    constraintName = createName(sourceNode=targetNode, nodeType=nodeType)
    constraintNode = mc.poleVectorConstraint(sourceNode, targetNode)[0]
    addNamingAttr(constraintNode, constraintName[1])

    return constraintNode

def aimConstraint(sourceNode, 
                    targetNode, 
                    upNode=None,
                    aimAxis='x',
                    upAxis='y',
                    targetUpAxis=None,
                    upType='objectrotation',
                    nodeType=Settings.aimConstraintSuffix,
                    skipRotate=None,
                    mo=False):

    aimVector, upVector = convertAimAxis(aimAxis, upAxis)
    targetUpVector = convertAxisToVector(targetUpAxis) if targetUpAxis else upVector

    constraintName = createName(sourceNode=targetNode, nodeType=nodeType)
    constraintNode = mc.aimConstraint(sourceNode, 
                                        targetNode, 
                                        aim=aimVector,
                                        u=upVector, 
                                        wu=targetUpVector, 
                                        wuo=upNode if upNode else sourceNode, 
                                        wut=upType, 
                                        skip=skipRotate if skipRotate else 'none',
                                        mo=mo)[0]
    addNamingAttr(constraintNode, constraintName[1])

    return constraintNode
    
def createOrigShape(geo):

    shapeNodes = getShapes(geo)

    for shapeNode in shapeNodes:
        if 'Orig' in shapeNode:
            return shapeNode
        
    # this seems to be needed in some cases for proximityWrap and proximityPin
    # couldnt figure out why exactly
    dummy = mc.blendShape(geo)
    mc.delete(dummy)

    for shapeNode in shapeNodes:
        if 'Orig' in shapeNode:
            return shapeNode
        
def getOutMeshes(geoNode):

    shapeNodes = getShapes(geoNode)

    shapeMesh = shapeNodes[0]

    origNode = createOrigShape(geoNode)
    if origNode:
        outMesh = origNode
    else:
        outMesh = [x for x in shapeNodes if not 'Orig' in x][-1]
        
    deformedMeshes = [x for x in shapeNodes if 'Deformed' in x and not 'Orig' in x]

    deformedMesh = deformedMeshes[-1] if deformedMeshes else None
    if not deformedMesh:
        deformedMesh = shapeNodes[0]

    return shapeMesh, deformedMesh, outMesh

def proximityWrap(driverGeoNode, geoNodes, wrapMode=1, falloff=10, sourceNode=None):
    
    if type(geoNodes) != list:
        geoNodes = [geoNodes]

    driverMeshes = getOutMeshes(driverGeoNode)

    if sourceNode:
        pxwDeformerName = createName(sourceNode=sourceNode, component=driverGeoNode.split('|')[-1], nodeType=Settings.proximityWrapSuffix)
        pxwDeformer = mc.deformer(geoNodes, name=pxwDeformerName[0], type='proximityWrap')[0]
    else:
        pxwDeformerName = '%s_%s'%(driverGeoNode.split('|')[-1], Settings.proximityWrapSuffix)
        pxwDeformer = mc.deformer(geoNodes, name=pxwDeformerName, type='proximityWrap')[0]
    mc.connectAttr('%s.worldMesh[0]'%driverMeshes[1], '%s.drivers[0].driverGeometry'%pxwDeformer)
    mc.connectAttr('%s.outMesh'%driverMeshes[2], '%s.drivers[0].driverBindGeometry'%pxwDeformer)
    
    mc.setAttr('%s.wrapMode'%pxwDeformer, wrapMode)
    mc.setAttr('%s.falloffScale'%pxwDeformer, falloff)

    if sourceNode:
        addNamingAttr(pxwDeformer, pxwDeformerName[1])

    return pxwDeformer

def getOffsetParentMatrix(node):
    """Return the offsetParentMatrix as an MMatrix."""
    return om.MMatrix(mc.getAttr(f"{node}.offsetParentMatrix"))

def getMatrix(node, includeOffsetParentMatrix=False):
    """Return the node's matrix (optionally multiplied by the offsetParentMatrix)."""
    localMtx = om.MMatrix(mc.getAttr(f"{node}.matrix"))
    if includeOffsetParentMatrix:
        return localMtx * getOffsetParentMatrix(node)
    return localMtx

def decomposeMatrix(matrix):
    transform = om.MTransformationMatrix(matrix)

    # Translation
    translation = transform.translation(om.MSpace.kWorld)

    # Force a quaternion from MTransformationMatrix, then convert to Euler
    rotation_quat = transform.rotation(asQuaternion=True)
    euler_rot = rotation_quat.asEulerRotation()

    rx = om.MAngle(euler_rot.x).asDegrees()
    ry = om.MAngle(euler_rot.y).asDegrees()
    rz = om.MAngle(euler_rot.z).asDegrees()

    # Scale
    sx, sy, sz = transform.scale(om.MSpace.kWorld)

    sx = cleanFloatValues(sx)
    sy = cleanFloatValues(sy)
    sz = cleanFloatValues(sz)

    return {
        "tx": translation.x,
        "ty": translation.y,
        "tz": translation.z,
        "rx": rx,
        "ry": ry,
        "rz": rz,
        "sx": sx,
        "sy": sy,
        "sz": sz
    }

def cleanFloatValues(value, decimals=6):
    return round(value, decimals)

def getTransformValues(node, includeOffsetParentMatrix=False):
    """Get a dictionary of T, R, S values (ignoring joint attributes)."""
    # 1. Compute the relevant matrix (local or local*offsetParentMatrix)
    combinedMtx = getMatrix(node, includeOffsetParentMatrix)

    # 2. Decompose it into translation, rotation (in degrees), and scale
    values = decomposeMatrix(combinedMtx)

    return values

def setOffsetParentMatrix(node, mirrorValue=1, matrix=None):

    offsetParentMatrixAttr = '%s.offsetParentMatrix'%node
    
    if not mc.objExists(offsetParentMatrixAttr):
        return
    
    if matrix:
        parentMtx = matrix
    else:
        parentMtx = getOffsetParentMatrix(node)
        for x in range(16):
            parentMtx[x] = 0
        parentMtx[0], parentMtx[5], parentMtx[10], parentMtx[15] = mirrorValue, 1, 1, 1
    
    mc.setAttr(offsetParentMatrixAttr, parentMtx, type='matrix')

def addSkeletonParentAttr(jointNode, skeletonParent):
    
    if mc.objExists('%s.namingConvention'%skeletonParent):
        skeletonParent = replaceNodeType(skeletonParent, Settings.skinJointSuffix)
    skeletonParentAttr = jointNode+'.skeletonParent'
    if not exists(skeletonParentAttr):
        mc.addAttr(jointNode, ln='skeletonParent', dt='string')
    mc.setAttr(jointNode+'.skeletonParent', type='string', lock=False)
    mc.setAttr(jointNode+'.skeletonParent', skeletonParent, type='string', lock=True)

def getRelatedNodes(compGroup):
    '''
    gets all the non-dag nodes that are connected to the component group
    '''
    # Aim creates a node inbetween another component, so we have to skip
    if getComponentType(compGroup) == 'Aim':
        return []

    component = getComponent(compGroup)
    side = getSide(compGroup)
    compType = getNodeType(compGroup)
    
    # special case for face modules which have side nodes but are no side components
    respectSides = not componentIsAutoSided(compGroup)
    
    connectedNodes = list()
    for node in mc.ls():
        if not mc.objExists('%s.namingConvention'%node):
            continue
        
        if respectSides:
            sideCheck = getSide(node) == side
        else:
            sideCheck = True

        if getComponent(node) == component and sideCheck:
            if mc.ls(node, dagObjects=True) == []:
                transformNodes = mc.ls(mc.listHistory(node), type='transform')
                if not transformNodes:
                    continue
                for transformNode in transformNodes:
                    if compGroup in getParents(transformNode)+[transformNode]:
                        connectedNodes.append(node)
            if compType == 'rig':
                if not getNodeType(node) in [Settings.guideGroup,
                                                    Settings.guidePivotSuffix,
                                                    Settings.guideShapeSuffix,
                                                    Settings.guideCurveSuffix,
                                                    Settings.guideSurfaceSuffix,
                                                    Settings.guideOffSuffix,
                                                    Settings.guideClusterSuffix,
                                                    Settings.guideClusterHandleSuffix,
                                                    Settings.motionPathGuideSuffix,
                                                    Settings.curveInfoGuideSuffix,
                                                    'guideParent', 
                                                    'guideAim', 
                                                    'guideAimOff',
                                                    'guideQuadParent', 
                                                    'guideQuadAim', 
                                                    'guideQuadAimOff',
                                                    'autoMirror']:
                    if not node == compGroup and not compGroup in getParents(node):
                        connectedNodes.append(node)
    
    return connectedNodes

def create_local_cumulative_transforms(nodes, root_node, target_node):
    
    # Create a multMatrix node for cumulative local transformation
    mult_matrix_node = mc.createNode('multMatrix', name=replaceSuffix(target_node, 'cumulativeLocalMultMatrix'))
    
    # Get the inverse matrix of the root node
    root_inverse_node = mc.createNode('inverseMatrix', name=f'{root_node}_inverseMatrix')
    mc.connectAttr(f'{root_node}.worldMatrix[0]', f'{root_inverse_node}.inputMatrix')
    
    for i, node in enumerate(nodes):
        # Multiply each child's world matrix by the root's inverse matrix to get local transforms
        local_mult_matrix = mc.createNode('multMatrix', name=replaceSuffix(node, 'localMultMatrix'))
        mc.connectAttr(f'{node}.worldMatrix[0]', f'{local_mult_matrix}.matrixIn[0]')
        mc.connectAttr(f'{root_inverse_node}.outputMatrix', f'{local_mult_matrix}.matrixIn[1]')
        
        # Connect the resulting local matrix to the cumulative multMatrix
        mc.connectAttr(f'{local_mult_matrix}.matrixSum', f'{mult_matrix_node}.matrixIn[{i}]')
    
    # Create a decomposeMatrix node to extract translation, rotation, and scale
    decompose_matrix_node = mc.createNode('decomposeMatrix', name=replaceSuffix(target_node, 'cumulativeLocalDecomposeMatrix'))
    mc.connectAttr(f'{mult_matrix_node}.matrixSum', f'{decompose_matrix_node}.inputMatrix')
    
    # Connect the decomposed outputs to the target node
    mc.connectAttr(f'{decompose_matrix_node}.outputTranslate', f'{target_node}.translate')
    mc.connectAttr(f'{decompose_matrix_node}.outputRotate', f'{target_node}.rotate')
    mc.connectAttr(f'{decompose_matrix_node}.outputScale', f'{target_node}.scale')

def combine_multiple_transforms(nodes, 
                                target_node, 
                                attribute='translate', 
                                axis='XYZ', 
                                specific=None):
    """
    Combines multiple transform attributes into a single cumulative local transform 
    on the target node using plusNode.

    Args:
        nodes (list): List of node names to combine transforms from.
        target_node (str): The node to which the cumulative transform will be applied.
        attribute (str): The transform attribute to combine ('translate', 'rotate', etc.).
        axis (str): The axis to operate on ('X', 'Y', 'Z', or 'XYZ').
        specific (str): Specific name suffix for the created plusNodes.
    
    Returns:
        str: The name of the final plusNode used for the combination.
    """
    if not nodes or len(nodes) < 2:
        raise ValueError("At least two nodes are required to combine transforms.")
    
    side = getSide(target_node)

    # Initialize the first input for the cumulative operation
    cumulative_input = None

    for i, node in enumerate(nodes):
        # Build the attribute path (e.g., 'node.translate')
        current_input = f"{node}.{attribute}"
        
        if i == 0:
            # Use the first node's transform as the initial cumulative input
            cumulative_input = current_input
            continue

        # Create a specific name for this operation
        op_specific = f"{specific or 'combine'}_{attribute}_{i}"

        if side == Settings.rightSide and attribute == 'translate':
            negate_node = divNode(
                input1=cumulative_input,
                input2=-1,
                axis=axis,
                specific=op_specific,
                operation=1,
                sourceNode=target_node
            )
            cumulative_input = f"{negate_node}.output"
        # Use plusNode to add the current node's transform to the cumulative input
        cumulative_node = plusNode(
            input1=cumulative_input,
            input2=current_input,
            axis=axis,
            specific=op_specific,
            sourceNode=target_node
        )
        # Update cumulative_input to the output of the current plusNode
        cumulative_input = f"{cumulative_node}.output3D"

    # Connect the final cumulative transform to the target node
    final_output = f"{target_node}.{attribute}"
    mc.connectAttr(cumulative_input, final_output, force=True)

    return cumulative_node