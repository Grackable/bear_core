
# ikFkMatch

import maya.api.OpenMaya as om
import maya.cmds as mc
import importlib, inspect
from bear.utilities import Nodes

try:
    module = importlib.import_module("bear")
    bearInstalled = True
except ImportError:
    bearInstalled = False

if bearInstalled:
    from bear.system import Settings
    namingOrder = Settings.namingOrder
    controlSuffix = Settings.controlSuffix
    leftSide = Settings.leftSide
    rightSide = Settings.rightSide
    skinJointSuffix = Settings.skinJointSuffix
    dummySuffix = Settings.dummySuffix
    scriptNodeSuffix = Settings.scriptNode
else:
    namingOrder = ["component", "side", "element", "indices", "specific", "nodeType"]
    controlSuffix = "control"
    leftSide = "L"
    rightSide = "R"
    skinJointSuffix = "skin"
    dummySuffix = "dummy"
    scriptNodeSuffix = "script"

def createName(component=None, 
                side=None, 
                nodeType=None, 
                element=None, 
                indices=None, 
                specific=None, 
                indexFill=2, 
                sourceNode=None, 
                useSourceIndexFill=False, 
                namingOrder=namingOrder):
    
    if sourceNode:

        # special case if sourceNode does not have naming convention. This may happen on space creation when other modules
        # haven't been built yet, or due to Maya auto-suffix like parentConstraints and such 

        if not mc.objExists('%s.namingConvention'%sourceNode):
            for n in range(10):
                split = sourceNode.split('_')
                if len(split) == 1:
                    dummyName = sourceNode
                else:
                    dummyName = '_'.join(split[:-n])
                dummyNamingOrder = getNamingOrder(dummyName)
                if dummyNamingOrder:
                    break
            return sourceNode, dummyNamingOrder

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

def getNamingOrder(node):

    namingAttrName = 'namingConvention'
    namingAttr = '%s.%s'%(node, namingAttrName)
    if not mc.objExists(namingAttr):
        return
    namingOrder = mc.getAttr(namingAttr).replace(' ', '').split(',')

    return namingOrder

def getToken(node, tokenType):
    
    namingAttrName = 'namingConvention'
    if not mc.objExists('%s.%s'%(node, namingAttrName)):
        return None, None
    
    namingOrder = mc.getAttr('%s.%s'%(node, namingAttrName)).replace(' ', '').split(',')
    tokens = node.split(':')[-1].split('_')
    
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

    myIndex = namingOrder.index(tokenType)
    myToken = cleanedTokens[myIndex].split(':')[-1]
    
    return myToken, myIndex

def getDistance(startNode, endNode):

    vector = getVector(startNode, endNode)

    distance = (vector[0]**2 + vector[1]**2 + vector[2]**2)**0.5

    return distance

def getVector(startNode, endNode):

    if type(startNode) == list:
        trs1 = startNode
    else:
        if '.vtx' in startNode or '.pt' in startNode or '.cv' in startNode:
            trs1 = mc.xform(startNode, q=True, translation=True, ws=True)
        else:
            trs1 = mc.xform(startNode, q=True, rp=True, ws=True)

    if type(endNode) == list:
        trs2 = endNode
    else:
        if '.vtx' in endNode or '.pt' in endNode or '.cv' in endNode:
            trs2 = mc.xform(endNode, q=True, translation=True, ws=True)
        else:
            trs2 = mc.xform(endNode, q=True, rp=True, ws=True)

    vector = (trs2[0]-trs1[0], trs2[1]-trs1[1], trs2[2]-trs1[2])

    return vector

def getSide(node):

    if node == None:
        return

    token = getToken(node, 'side')[0]
    if token == leftSide:
        return leftSide
    if token == rightSide:
        return rightSide

    return None

def getParents(node):

    fullName = mc.ls(node, l=True)[0]
    parentNodes = fullName.split('|')[1:-1]

    return parentNodes

def getComponent(node):

    if node == None:
        return
    token = getToken(node, 'component')[0]
    return token

def getComponentGroup(node):

    for parentNode in getParents(node)[::-1]:
        compType = getComponentType(parentNode)
        if compType:
            return parentNode

def getComponentType(compGroup):

    if mc.objExists('%s.componentType'%compGroup):
        return mc.getAttr('%s.componentType'%compGroup)
    return None

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

def setTrs(node, attr, value=0):

    for axis in 'XYZ':
        mc.setAttr(node+'.'+attr+axis, value)

def isAttrSettable(attr):

    if not mc.objExists(attr):
        return None
    if not mc.getAttr(attr, lock=True) and mc.listConnections(attr, source=True, destination=False, plugs=True) == None:
        return True
    else:
        return False

def getUpnodePosition(upperLimbNode, lowerLimbNode, endNode):

    upperArmPos = mc.xform(upperLimbNode, query=True, worldSpace=True, translation=True)
    lowerArmPos = mc.xform(lowerLimbNode, query=True, worldSpace=True, translation=True)
    wristPos = mc.xform(endNode, query=True, worldSpace=True, translation=True)

    upperArmVector = om.MVector(upperArmPos)
    lowerArmVector = om.MVector(lowerArmPos)
    wristVector = om.MVector(wristPos)

    armVector = wristVector - upperArmVector

    midArmLength = getDistance(upperArmPos, wristPos)*0.5

    upperLength = getDistance(upperArmPos, lowerArmPos)
    lowerLength = getDistance(lowerArmPos, wristPos)
    armRatio =  1.0 / ((upperLength+lowerLength) / upperLength)

    midVector = upperArmVector + armVector*armRatio
    upVector = lowerArmVector - midVector
    upVector.normalize()

    upnodePos = lowerArmVector + (upVector * midArmLength)

    return upnodePos

def ikFkMatch(node=None, setKeyframes=True):

    if node:
        sourceNode = node
    else:
        selection = mc.ls(sl=True)
        if not selection:
            mc.error("Nothing selected. Matching aborted.")
            return
        sourceNode = selection[0]

    refPrefix = sourceNode.split(':')[0]+':' if mc.referenceQuery(sourceNode, isNodeReferenced=True) else ''
    side = getSide(sourceNode)

    componentName = getComponent(sourceNode)
    componentGroup = getComponentGroup(sourceNode)
    componentType = getComponentType(componentGroup)
    
    attrControl = createName(component=componentName,
                                side=side,
                                element='attributes',
                                nodeType=controlSuffix)[0]

    ikControl = createName(component=componentName,
                                side=side,
                                element='ik',
                                nodeType=controlSuffix)[0]

    ikPivotControl = createName(component=componentName,
                                side=side,
                                element='ik',
                                specific='pivot',
                                nodeType=controlSuffix)[0]

    ikAnkleControl = createName(component=componentName,
                                side=side,
                                element='ankle',
                                specific='ik',
                                nodeType=controlSuffix)[0]

    ikToesControl = createName(component=componentName,
                                side=side,
                                element='toes',
                                specific='ik',
                                nodeType=controlSuffix)[0]

    fkAnkleControl = createName(component=componentName,
                                side=side,
                                element='ankle',
                                specific='fk',
                                nodeType=controlSuffix)[0]

    fkToesControl = createName(component=componentName,
                                side=side,
                                element='toes',
                                specific='fk',
                                nodeType=controlSuffix)[0]

    ikUpControl = createName(component=componentName,
                                side=side,
                                element='upnode',
                                nodeType=controlSuffix)[0]

    ikAnkleUpControl = createName(component=componentName,
                                side=side,
                                element='ankle',
                                specific='upnode',
                                nodeType=controlSuffix)[0]
    
    ikFrontPivotControl = createName(component=componentName,
                                side=side,
                                element='pivot',
                                specific='front',
                                nodeType=controlSuffix)[0]
    
    ikMidControl = createName(component=componentName,
                                side=side,
                                element='elbow' if componentType == 'Arm' else 'knee',
                                nodeType=controlSuffix)[0]
    
    ikHeelControl = createName(component=componentName,
                                side=side,
                                element='heel',
                                nodeType=controlSuffix)[0]

    fkEndControl = createName(component=componentName,
                                side=side,
                                element='wrist' if componentType == 'Arm' else 'ankle',
                                specific='fk',
                                nodeType=controlSuffix)[0]

    fkUpperControl = createName(component=componentName,
                                side=side,
                                element='upper',
                                specific='fk',
                                nodeType=controlSuffix)[0]

    fkLowerControl = createName(component=componentName,
                                side=side,
                                element='lower',
                                specific='fk',
                                nodeType=controlSuffix)[0]

    upperJoint = createName(component=componentName,
                                side=side,
                                element='upper',
                                nodeType='blend')[0]

    lowerJoint = createName(component=componentName,
                                side=side,
                                element='lower',
                                nodeType='blend')[0]

    ankleJoint = createName(component=componentName,
                                side=side,
                                element='ankle',
                                nodeType=skinJointSuffix)[0]

    matchAnkleDummy = createName(component=componentName,
                                side=side,
                                element='ik',
                                specific='ikFkMatch',
                                nodeType=dummySuffix)[0]

    matchToesDummy = createName(component=componentName,
                                side=side,
                                element='ik',
                                specific='ikFkMatchToes',
                                nodeType=dummySuffix)[0]
    
    attrControl = refPrefix+attrControl
    ikControl = refPrefix+ikControl
    ikPivotControl = refPrefix+ikPivotControl
    ikAnkleControl = refPrefix+ikAnkleControl
    ikToesControl = refPrefix+ikToesControl
    fkAnkleControl = refPrefix+fkAnkleControl
    fkToesControl = refPrefix+fkToesControl
    ikUpControl = refPrefix+ikUpControl
    ikAnkleUpControl = refPrefix+ikAnkleUpControl
    ikFrontPivotControl = refPrefix+ikFrontPivotControl
    ikMidControl = refPrefix+ikMidControl
    ikHeelControl = refPrefix+ikHeelControl
    fkEndControl = refPrefix+fkEndControl
    fkUpperControl = refPrefix+fkUpperControl
    fkLowerControl = refPrefix+fkLowerControl
    upperJoint = refPrefix+upperJoint
    lowerJoint = refPrefix+lowerJoint
    ankleJoint = refPrefix+ankleJoint
    matchAnkleDummy = refPrefix+matchAnkleDummy
    matchToesDummy = refPrefix+matchToesDummy

    if not mc.objExists(upperJoint):
        upperJoint = createName(component=componentName,
                                    side=side,
                                    element='upper',
                                    nodeType=skinJointSuffix)[0]

        lowerJoint = createName(component=componentName,
                                    side=side,
                                    element='lower',
                                    nodeType=skinJointSuffix)[0]
        upperJoint = refPrefix+upperJoint
        lowerJoint = refPrefix+lowerJoint
    if not mc.objExists(ankleJoint):
        ankleJoint = createName(component=componentName,
                                    side=side,
                                    element='ankle',
                                    nodeType='blend')[0]
        ankleJoint = refPrefix+ankleJoint

    toFk = False
    toIk = False
    if sourceNode in [ikControl,
                      ikUpControl,
                      ikAnkleUpControl,
                      ikMidControl,
                      ikHeelControl,
                      ikAnkleControl,
                      ikToesControl,
                      ikFrontPivotControl,
                      ikPivotControl]:
        toFk = True

    if sourceNode in [fkEndControl,
                      fkUpperControl,
                      fkLowerControl,
                      fkAnkleControl,
                      fkToesControl]:
        toIk = True

    ikFkAttr = '%s.ikFkBlend'%attrControl

    if not mc.objExists(ikFkAttr):
        mc.error("No limb control selected. Matching aborted.")

    ikFkState = mc.getAttr(ikFkAttr)

    if sourceNode == attrControl:
        if ikFkState == 1:
            toFk = True
        elif ikFkState == 0:
            toIk = True

    if ikFkState > 0 and ikFkState < 1:
        mc.error("Can't match inbetween state. Matching aborted.")
        return

    if not toFk and not toIk:
        mc.error("No limb control selected. Matching aborted.")
        
    if toFk:
        upperStretch = mc.getAttr('%s.scaleX'%upperJoint)
        lowerStretch = mc.getAttr('%s.scaleX'%lowerJoint)
        alignObject(fkUpperControl, upperJoint)
        alignObject(fkLowerControl, lowerJoint)
        if componentType == 'Arm':
            alignObject(fkEndControl, ikControl)
        else:
            alignObject(fkEndControl, ankleJoint)
            alignObject(fkToesControl, ikToesControl)
            if setKeyframes:
                mc.setKeyframe(fkToesControl, attribute='rotate')
        mc.setAttr('%s.scaleX'%fkUpperControl, upperStretch)
        mc.setAttr('%s.scaleX'%fkLowerControl, lowerStretch)

        if setKeyframes:
            mc.setKeyframe(fkUpperControl, attribute='rotate')
            mc.setKeyframe(fkLowerControl, attribute='rotate')
            mc.setKeyframe('%s.scaleX'%fkUpperControl)
            mc.setKeyframe('%s.scaleX'%fkLowerControl)
            mc.setKeyframe(fkEndControl, attribute='rotate')

        if mc.objExists(ankleJoint) and isAttrSettable('%s.scaleX'%fkAnkleControl):
            ankleStretch = mc.getAttr('%s.scaleX'%ankleJoint)
            alignObject(fkAnkleControl, ankleJoint)
            mc.setAttr('%s.scaleX'%fkAnkleControl, ankleStretch)
            if setKeyframes:
                mc.setKeyframe('%s.scaleX'%fkAnkleControl)

        mc.setAttr(ikFkAttr, 0)
        if setKeyframes:
            mc.setKeyframe(attrControl, attribute='ikFkBlend')
        mc.select(attrControl if sourceNode == attrControl else fkEndControl)

    if toIk:
        setTrs(ikPivotControl, 'translate')
        if setKeyframes:
            mc.setKeyframe(ikPivotControl, attribute='translate')
        if componentType == 'Arm':
            alignObject(ikControl, fkEndControl)
        else:
            mc.setAttr('%s.roll'%ikControl, 0)
            mc.setAttr('%s.bank'%ikControl, 0)
            mc.setAttr('%s.frontSpin'%ikControl, 0)
            mc.setAttr('%s.backSpin'%ikControl, 0)
            if setKeyframes:
                mc.setKeyframe('%s.roll'%ikControl)
                mc.setKeyframe('%s.bank'%ikControl)
                mc.setKeyframe('%s.frontSpin'%ikControl)
                mc.setKeyframe('%s.backSpin'%ikControl)
            setTrs(ikFrontPivotControl, 'rotate')
            if setKeyframes:
                mc.setKeyframe(ikFrontPivotControl, attribute='rotate')
            if mc.getAttr('%s.pivotToToes'%ikControl):
                if mc.objExists(matchToesDummy):
                    alignObject(ikControl, matchToesDummy)
                    alignObject(ikControl, matchToesDummy)
            else:
                alignObject(ikControl, matchAnkleDummy)
                alignObject(ikControl, matchAnkleDummy)
            alignObject(ikAnkleControl, fkAnkleControl)
            alignObject(ikToesControl, fkToesControl)
            if setKeyframes:
                mc.setKeyframe(ikAnkleControl, attribute='rotate')
                mc.setKeyframe(ikToesControl, attribute='rotate')
        upnodePos = getUpnodePosition(fkUpperControl, fkLowerControl, fkEndControl)
        mc.xform(ikUpControl, translation=upnodePos, ws=True)

        if setKeyframes:
            mc.setKeyframe(ikControl, attribute='translate')
            mc.setKeyframe(ikControl, attribute='rotate')
            mc.setKeyframe(ikUpControl, attribute='translate')

        if mc.objExists(ikMidControl):
            alignObject(ikMidControl, lowerJoint)
            if setKeyframes:
                mc.setKeyframe(ikMidControl, attribute='translate')
        if mc.objExists(ikHeelControl):
            alignObject(ikHeelControl, ankleJoint)
            if setKeyframes:
                mc.setKeyframe(ikHeelControl, attribute='translate')

        mc.setAttr(ikFkAttr, 1)
        if setKeyframes:
            mc.setKeyframe(attrControl, attribute='ikFkBlend')
        mc.select(attrControl if sourceNode == attrControl else ikControl)

############## attribute switch on attr node ###################        

def create_script_node(attrControlNode):

    matchIKtoFK_src = inspect.getsource(matchIKtoFK)
    matchFKtoIK_src = inspect.getsource(matchFKtoIK)
    attribute_changed_callback_src = inspect.getsource(attribute_changed_callback)
    add_attribute_change_callback_src = inspect.getsource(add_attribute_change_callback)
    # Create a scriptNode that re-establishes the callback when the scene is opened
    script = f"""
    import maya.cmds as mc
    import maya.api.OpenMaya as om

    {matchIKtoFK_src}
    {matchFKtoIK_src}
    {attribute_changed_callback_src}
    {add_attribute_change_callback_src}

    add_attribute_change_callback('{attrControlNode}')
    """

    name = createName(nodeType=scriptNodeSuffix, sourceNode=attrControlNode)[0]
    Nodes.delete(name)
    scriptNode = Nodes.scriptNode(script, sourceNode=attrControlNode)

    return scriptNode

def add_attribute_change_callback(attrControlNode):
    # Add the callback to monitor attribute changes
    selection_list = om.MSelectionList()
    selection_list.add(attrControlNode)
    node = selection_list.getDependNode(0)
    
    callback_id = om.MNodeMessage.addAttributeChangedCallback(node, attribute_changed_callback)
    return callback_id

def attribute_changed_callback(msg, plug, otherPlug, clientData):
    # Define the callback function
    attrControlNode = "arm_L_attributes_control"
    if msg & om.MNodeMessage.kAttributeSet:
        node = plug.node()
        fn_node = om.MFnDependencyNode(node)
        if fn_node.name() == attrControlNode and plug.partialName() == 'ikFkMatch':
            ik_fk_value = mc.getAttr('%s.ikFkMatch'%attrControlNode)
            if ik_fk_value == 0:
                matchIKtoFK()
            elif ik_fk_value == 1:
                matchFKtoIK()

# Define the IK to FK matching function
def matchIKtoFK():
    print("Matching IK to FK")
    # Your IK to FK matching logic here
    pass

# Define the FK to IK matching function
def matchFKtoIK():
    print("Matching FK to IK")
    # Your FK to IK matching logic here
    pass

def instantSwitch(attrControlNode):
    # Create IK/FK switch attribute if it doesn't exist
    if not mc.attributeQuery('ikFkMatch', node=attrControlNode, exists=True):
        mc.addAttr(attrControlNode, longName='ikFkMatch', niceName='IK/FK Match', attributeType='enum', enumName="FK:IK", min=0, max=1, defaultValue=0, keyable=True)
    add_attribute_change_callback(attrControlNode)
    print(create_script_node(attrControlNode))