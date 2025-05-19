# Tools

import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as OpenMaya

from bear.ui import UndoDec
from bear.system import Settings
from bear.system import MessageHandling
from bear.utilities import AddNode
from bear.utilities import NodeOnVertex
from bear.utilities import Nodes

def removeTurtle():

    mel.eval('lockNode - l off TurtleDefaultBakeLayer; \
             delete TurtleDefaultBakeLayer; \
             lockNode - l off TurtleBakeLayerManager; \
             delete TurtleBakeLayerManager; \
             lockNode - l off TurtleRenderOptions; \
             delete TurtleRenderOptions; \
             lockNode - l off TurtleUIOptions; \
             delete TurtleUIOptions;')

def removeSelectionSets():

    for setNode in mc.ls(sets=True):
        remove = False
        childNodes = mc.sets(setNode, q=True)
        if childNodes == None:
            continue
        for childNode in childNodes:
            if mc.objectType(childNode) == 'joint':
                remove = True
                mc.sets(childNode, remove=setNode)
        if remove:
            mc.delete(setNode)

def getAssignedMaterials(node):

    obj = mc.listConnections(node.getShape())
    shadingObj = mc.listConnections(obj)
    materialList = mc.ls(shadingObj, mat=True)

    return materialList

def setValue(timeRange=[0, 100], v=[0, 1], nodeType=Settings.controlSuffix):

    for i, t in enumerate(timeRange):
        mc.currentTime(t)
        for node in mc.ls('*_'+nodeType, type='transform'):
            for trs in 'tr':
                for axis in 'xyz':
                    attr = '%s%s'%(trs, axis)
                    mc.setKeyframe(node, at=attr, v=v[i])
            attrList = mc.listAttr(node, userDefined=True)
            if attrList != None:
                for attr in attrList:
                    if not 'Display' and not 'globalScale' in attr:
                        mc.setKeyframe(node, at=attr, v=v[i])

    mc.currentTime(0)

def connectTransforms(sourceNode, targetNode, translate=True, rotate=True, scale=True):

    trsList = []

    if translate:
        trsList.append('translate')
    if rotate:
        trsList.append('rotate')
    if scale:
        trsList.append('scale')
    
    [mc.connectAttr('%s.%s' % (sourceNode, trs), '%s.%s' % (targetNode, trs), f=True) for trs in trsList]

def resetTransforms(node, translate=True, rotate=True, scale=True):

    trsList = []

    if translate:
        trsList.append(['translate', 0])
    if rotate:
        trsList.append(['rotate', 0])
    if scale:
        trsList.append(['scale', 1])
    
    for t, trs in enumerate(trsList):
        for axis in 'XYZ':
            try:
                mc.setAttr('%s.%s%s'%(node, trs[0], axis), trs[1])
            except:
                pass

def removeConstraint(node, constraintType='parentConstraint'):

    # TODO: replace with proper type detection
    childNodes = mc.listRelatives(node, children=True, fullPath=True)
    if childNodes:
        for childNode in childNodes:
            if mc.objectType(childNode) == constraintType:
                mc.delete(childNode)

def parentConstraint(srcNode, 
                        trgNode, 
                        maintainOffset=True):

    return parentScaleConstraint(srcNode, trgNode, maintainOffset=maintainOffset, connectScale=False)[0]

def parentScaleConstraint(srcNode, 
                            trgNode, 
                            maintainOffset=True, 
                            force=False, 
                            inbetweenObject=False, 
                            useMatrix=False,
                            connectTranslate=True,
                            connectRotate=True,
                            connectScale=True,
                            targetInheritsTransform=False,
                            removeExistingConstraint=True):

    if srcNode == None or trgNode == None:
        return

    if not mc.objExists(srcNode) or not mc.objExists(trgNode):
        return

    # we prefer to parent to the pivot control if it exists
    srcNode = Nodes.getPivotCompensate(srcNode)

    for trs in 'trs':
        for axis in 'xyz':
            attr = '%s.%s%s'%(trgNode, trs, axis)
            if force:
                Nodes.removeConnection(attr)
            try:
                mc.setAttr(attr, lock=False)
            except:
                pass
    
    if removeExistingConstraint:
        if connectTranslate or connectRotate:
            removeConstraint(trgNode, constraintType='parentConstraint')
        if connectScale:
            removeConstraint(trgNode, constraintType='scaleConstraint')

    if Nodes.isConnected(trgNode, True, False, False):
        connectTranslate = False
    if Nodes.isConnected(trgNode, False, True, False):
        connectRotate = False
    if Nodes.isConnected(trgNode, False, False, True):
        connectScale = False

    
    if useMatrix:
        if maintainOffset:
            nodeType = Settings.matrixSuffix
            specific = Nodes.camelCase(trgNode)
            offsetNode = Nodes.createName(sourceNode=srcNode, specific=specific, nodeType=nodeType)[0]
            if not mc.objExists(offsetNode):
                offsetNode = AddNode.emptyNode(srcNode, specific=specific, nodeType=nodeType)
                mc.parent(offsetNode, srcNode)
            Nodes.alignObject(offsetNode, trgNode)
            mc.setAttr('%s.inheritsTransform'%trgNode, targetInheritsTransform)
        else:
            offsetNode = srcNode
        decompMtxNode = Nodes.utilityNode(nodeType='decomposeMatrix', sourceNode=trgNode)
        mc.connectAttr('%s.worldMatrix'%offsetNode, '%s.inputMatrix'%decompMtxNode)
        if connectTranslate:
            mc.connectAttr('%s.outputTranslate'%decompMtxNode, '%s.translate'%trgNode)
        if connectRotate:
            if mc.objectType(trgNode) == 'joint':
                [mc.setAttr('%s.jointOrient%s'%(trgNode, axis), 0) for axis in 'XYZ']
            mc.connectAttr('%s.outputRotate'%decompMtxNode, '%s.rotate'%trgNode)
        if connectScale:
            mc.connectAttr('%s.outputScale'%decompMtxNode, '%s.scale'%trgNode)

    else:

        if inbetweenObject:
            inbNode = Nodes.replaceNodeType(trgNode, Settings.parentSuffix)
            if mc.objExists(inbNode):
                mc.delete(inbNode)
            srcNode = AddNode.emptyNode(trgNode, parentNode=srcNode, nodeType=Settings.parentSuffix)
        parentCnt = mc.parentConstraint(srcNode, trgNode, maintainOffset=maintainOffset, 
                                        skipTranslate=[] if connectTranslate else ['x', 'y', 'z'], 
                                        skipRotate=[] if connectRotate else ['x', 'y', 'z'])[0]
        try:
            if connectScale:
                scaleCnt = mc.scaleConstraint(srcNode, trgNode, maintainOffset=maintainOffset)[0]
            else:
                scaleCnt = None
        except:
            scaleCnt = None
            MessageHandling.warning('scale constraint assignment skipped: '+trgNode)

        return parentCnt, scaleCnt

def pointConstraint(srcNode, 
                    trgNode, 
                    maintainOffset=False):

    pntCnt = mc.pointConstraint(srcNode, trgNode, mo=maintainOffset)[0]

    return pntCnt

def orientConstraint(srcNode, 
                    trgNode, 
                    skipRotate=None,
                    maintainOffset=False,
                    interpType=2):

    pntCnt = mc.orientConstraint(srcNode, trgNode, mo=maintainOffset, skip=skipRotate if skipRotate else 'none')[0]
    mc.setAttr('%s.interpType'%pntCnt, interpType)

    return pntCnt

def createOriginNode(controlNodes):
    
    controlNodes = list(controlNodes)
    ognNodes = list()

    dupNode = mc.duplicate(controlNodes[0])[0]
    
    ognNodes.append(mc.rename(controlNodes[0], Nodes.replaceNodeType(controlNodes[0], Settings.originNodeSuffix)))
    ognNodes.append(mc.rename(controlNodes[1], Nodes.replaceNodeType(controlNodes[1], Settings.originOffNodeSuffix)))

    controlNodes[0] = mc.rename(dupNode, Nodes.replaceNodeType(ognNodes[0], Settings.controlSuffix))
    controlNodes[1] = AddNode.parentNode(controlNodes[0])

    mc.parent(controlNodes[1], mc.listRelatives(ognNodes[1], parent=True)[0])

    mc.setAttr('%s.inheritsTransform'%ognNodes[1], False)

    for trs in 'trs':
        for axis in 'xyz':
            try:
                mc.connectAttr('%s.%s%s'%(controlNodes[0], trs, axis), '%s.%s%s'%(ognNodes[0], trs, axis))
            except:
                pass
    
    userAttrList = mc.listAttr(ognNodes[0], userDefined=True)
    if userAttrList != None:
        for userAttr in userAttrList:
            try:
                mc.connectAttr('%s.%s'%(controlNodes[0], userAttr), '%s.%s'%(ognNodes[0], userAttr))
            except:
                pass
    
    return ognNodes

def createOriginBsh(geoNode):

    deform = mc.rename(mc.duplicate(geoNode)[0], Nodes.replaceNodeType(geoNode, 'deform'))
    squashStretch = mc.rename(mc.duplicate(geoNode)[0], Nodes.v(geoNode, 'squashStretch'))

    mc.blendShape([deform, squashStretch], 
                    geoNode,
                    name=Nodes.replaceNodeType(geoNode, 'deformBlendshapes'), 
                    topologyCheck=False,
                    w=((0, 1), (1, 1)))

    return deform, squashStretch

def createDeformableControls(controlNodeList, geoNode, parentNode='head'+'_'+Settings.controlSuffix, customVertices={'jaw'+'_'+Settings.controlSuffix: 1842}, zLock=False):

    deformGeoNode = mc.rename(geoNode, Nodes.replaceNodeType(geoNode, Settings.deformGeoNodeSuffix))
    geoNode = mc.duplicate(deformGeoNode)[0]
    geoNode = mc.rename(geoNode, Nodes.replaceNodeType(geoNode, Settings.geoNodeSuffix))

    mc.blendShape(deformGeoNode, geoNode, name='faceBlendshape', w=(0, 1))
    parentScaleConstraint(parentNode, geoNode)

    controlGroup = mc.group(name='face_controls', empty=True)

    for controlNode in controlNodeList:

        controlNode = controlNode

        deformControlNode = mc.rename(controlNode, Nodes.replaceNodeType(controlNode, Settings.deformNodeSuffix))
        controlNode = mc.duplicate(deformControlNode, parentOnly=True)[0]
        controlNode = mc.rename(controlNode, Nodes.replaceNodeType(controlNode, Settings.controlSuffix))
        offNode = AddNode.parentNode(controlNode, Settings.deformOffNodeSuffix)
        shapeNodes = mc.listRelatives(deformControlNode, shapes=True)
        for shapeNode in shapeNodes:
            mc.parent(shapeNode, controlNode, s=True, r=True)

        if zLock:
            conNode = AddNode.inbetweenNode(deformControlNode, nodeType='zLock')
        connectTransforms(controlNode, deformControlNode)

        if controlNode in customVertices:
            vtxID = customVertices[controlNode]
        else:
            vtxID = getClosestVertex(controlNode, geoNode)[1]
        folNode, exists = NodeOnVertex.createFollicle(geoNode, 
                                                        name=Nodes.replaceNodeType(controlNode), 
                                                        vtxID=vtxID,
                                                        orient=False)
        mc.orientConstraint(parentNode, folNode, mo=True)
        mc.scaleConstraint(parentNode, folNode, mo=True)
        mc.parent(offNode, folNode)
        mc.parent(folNode, controlGroup)

        negNode = AddNode.inbetweenNode(offNode, nodeType='neg')
        mulNode = mc.shadingNode('multiplyDivide', asUtility=True, name=Nodes.replaceNodeType(controlNode, 'mul'))
        mc.setAttr('%s.operation' % mulNode, 1)
        for axis in 'XYZ':
            if axis == 'Z' and zLock: 
                Nodes.addAttrTitle(controlNode, 'deform')
                mc.addAttr(controlNode, at='float', ln='zLock', k=True, dv=1, hasMinValue=True, minValue=0, hasMaxValue=True, maxValue=1)

                conMulNode = mc.shadingNode('multiplyDivide', asUtility=True, name=Nodes.replaceNodeType(controlNode, 'conMul'))
                mc.setAttr('%s.operation' % conMulNode, 1)
                mc.connectAttr('%s.translate%s' % (controlNode, axis), '%s.input2.input2%s' % (conMulNode, axis))
                mc.connectAttr('%s.zLock' % (controlNode), '%s.input1.input1%s' % (conMulNode, axis))
                
                negMulNode = mc.shadingNode('multiplyDivide', asUtility=True, name=Nodes.replaceNodeType(controlNode, 'negMul'))
                mc.setAttr('%s.operation' % negMulNode, 1)
                mc.connectAttr('%s.output.output%s' % (conMulNode, axis), '%s.input1.input1%s' % (negMulNode, axis))
                mc.setAttr('%s.input2.input2%s' % (negMulNode, axis), -1)
                mc.connectAttr('%s.output.output%s' % (negMulNode, axis), '%s.translate%s' % (conNode, axis))

            mc.setAttr('%s.input2.input2%s' % (mulNode, axis), -1)
            mc.connectAttr('%s.translate%s' % (controlNode, axis), '%s.input1.input1%s' % (mulNode, axis))
            mc.connectAttr('%s.output.output%s' % (mulNode, axis), '%s.translate%s' % (negNode, axis))

def createControlDeformConnection(controlNodes, 
                                  deformNodes, 
                                  geoNode=None, 
                                  latticeNode=None, 
                                  orientNode=None, 
                                  drvType='geo', 
                                  zLock=False,
                                  controlGroup=None,
                                  deformGroup=None):
    
    folGroupNode= None
    latOffNode = None
    
    trsNode = AddNode.inbetweenNode(mc.listRelatives(deformNodes[0], parent=True)[0], nodeType='trs')
    if zLock:
        conNode = AddNode.inbetweenNode(trsNode, nodeType='zLock')

    connectTransforms(controlNodes[0], trsNode)
    
    latticeJointList = None
    if latticeNode != None:
        skinClusterNode = Nodes.getSkinCluster(latticeNode)[0]
        if skinClusterNode != None:
            latticeJointList = mc.skinCluster(skinClusterNode, query=True, inf=True)

    folNode = None

    if drvType == 'geo':
        latOffNode = None
        #folNodeList, folGroupNode, exists = NodeOnVertex.createNodeOnVertex([getClosestVertex(controlNodes[0], geoNode)],
                                                                            #name=Nodes.replaceNodeType(controlNodes[0], 'grp'),
                                                                            #orient=False)

        folNode, exists = NodeOnVertex.createFollicle(geoNode, 
                                                        name=Nodes.replaceNodeType(controlNodes[0], 'control'), 
                                                        vtxID=getClosestVertex(controlNodes[0], geoNode)[1],
                                                        orient=False)

        mc.parent(controlNodes[1], folNode)

        if exists:
            if orientNode == None and latticeNode != None:
                orientNode = getClosestNode(controlNodes[0], latticeJointList)[0]
            mc.orientConstraint(orientNode, folNode, mo=True)
            mc.scaleConstraint(orientNode, folNode, mo=True)
        else:
            mc.orientConstraint(orientNode, folNode, mo=True)
            mc.scaleConstraint(orientNode, folNode, mo=True)

        negNode = AddNode.inbetweenNode(mc.listRelatives(controlNodes[0], parent=True)[0], nodeType='neg')
        mulNode = mc.shadingNode('multiplyDivide', asUtility=True, name=Nodes.replaceNodeType(controlNodes[0], 'mul'))
        mc.setAttr('%s.operation' % mulNode, 1)
        for axis in 'XYZ':
            if axis == 'Z' and zLock: 
                Nodes.addAttrTitle(controlNodes[0], 'deform')
                mc.addAttr(controlNodes[0], at='float', ln='zLock', k=True, dv=1, hasMinValue=True, minValue=0, hasMaxValue=True, maxValue=1)

                conMulNode = mc.shadingNode('multiplyDivide', asUtility=True, name=Nodes.replaceNodeType(controlNodes[0], 'conMul'))
                mc.setAttr('%s.operation' % conMulNode, 1)
                mc.connectAttr('%s.translate%s' % (controlNodes[0], axis), '%s.input2.input2%s' % (conMulNode, axis))
                mc.connectAttr('%s.zLock' % (controlNodes[0]), '%s.input1.input1%s' % (conMulNode, axis))
                
                negMulNode = mc.shadingNode('multiplyDivide', asUtility=True, name=Nodes.replaceNodeType(controlNodes[0], 'negMul'))
                mc.setAttr('%s.operation' % negMulNode, 1)
                mc.connectAttr('%s.output.output%s' % (conMulNode, axis), '%s.input1.input1%s' % (negMulNode, axis))
                mc.setAttr('%s.input2.input2%s' % (negMulNode, axis), -1)
                mc.connectAttr('%s.output.output%s' % (negMulNode, axis), '%s.translate%s' % (conNode, axis))

            mc.setAttr('%s.input2.input2%s' % (mulNode, axis), -1)
            mc.connectAttr('%s.translate%s' % (controlNodes[0], axis), '%s.input1.input1%s' % (mulNode, axis))
            mc.connectAttr('%s.output.output%s' % (mulNode, axis), '%s.translate%s' % (negNode, axis))

    if drvType == 'lat' and latticeNode != None:
        latticePoint = getClosestPoint(controlNodes[0], latticeNode)
        locNode = NodeOnVertex.createNodeByVertexWeight(latticePoint, alignLocToNode=deformNodes[0])[0][0]
        latOffNode = AddNode.parentNode(locNode, nodeType='latOff')
        latDfmNode = AddNode.inbetweenNode(controlNodes[1], nodeType='latDfm')
        connectTransforms(locNode, latDfmNode)
    '''
    folGroupNode = None if folGroupNode == [] else folGroupNode

    if folGroupNode != None and controlGroup != None:
        if mc.listRelatives(folGroupNode, parent=True) == None:
            mc.parent(folGroupNode, controlGroup)
    if latOffNode != None and deformGroup != None:
        mc.parent(latOffNode, deformGroup)
    '''
    #folGroupNode = None if folGroupNode == [] else folGroupNode

    if folNode != None and controlGroup != None:
        mc.parent(folNode, controlGroup)
    if latOffNode != None and deformGroup != None:
        mc.parent(latOffNode, deformGroup)

    return folNode, latOffNode

def alignPivot(sourceObj, targetObj):

    if Nodes.isConnected(sourceObj):
        return

    parentNode = sourceObj.getParent()
    
    pivotTranslation = mc.xform(targetObj, q=True, ws=True, rotatePivot=True)
    mc.parent(sourceObj, targetObj)
    mc.makeIdentity(sourceObj, a=True, t=True, r=True, s=True)
    mc.xform(sourceObj, ws=True, pivots=pivotTranslation)

    sourceObj.setParent(parentNode)

    mc.select(clear=True)

def resetPivot(obj):
    
    tmpNode = AddNode.emptyNode(obj)
    
    childNodes = mc.listRelatives(obj, children=True, type='transform')

    if childNodes != []:
        mc.parent(childNodes, world=True)

    for axis in 'XYZ':
        for trs in ['rotate', 'scale']:
            mc.setAttr('%s.%sPivot%s'%(obj, trs, axis), 0)

    alignPivot(obj, tmpNode)
    mc.delete(tmpNode)

    if childNodes != []:
        mc.parent(childNodes, obj)
    mc.select(obj)

def getClosestPointOnCurve(curveNode, node, fractionMode=True):
    
    nodeTrs = mc.xform(node, q=True, rp=True, ws=True)
    
    nearestPointOnCurveNode = mc.createNode('nearestPointOnCurve')
    
    mc.connectAttr('%s.worldSpace[0]'%curveNode, '%s.inputCurve'%nearestPointOnCurveNode)
    mc.setAttr('%s.inPositionX'%nearestPointOnCurveNode, nodeTrs[0])
    mc.setAttr('%s.inPositionY'%nearestPointOnCurveNode, nodeTrs[1])
    mc.setAttr('%s.inPositionZ'%nearestPointOnCurveNode, nodeTrs[2])

    x = mc.getAttr('%s.positionX'%nearestPointOnCurveNode)
    y = mc.getAttr('%s.positionY'%nearestPointOnCurveNode)
    z = mc.getAttr('%s.positionZ'%nearestPointOnCurveNode)

    uValue = mc.getAttr('%s.parameter'%nearestPointOnCurveNode)
    if fractionMode:
        uValue /= mc.getAttr('%s.spans'%curveNode)

    Nodes.delete(nearestPointOnCurveNode)
    
    return uValue, [x, y, z]

def getClosestNode(sourceNode, targetNodeList):
    
    closestNode, index_min = parentToClosest([sourceNode], targetNodeList, parentType=None)

    return closestNode, index_min

def getNodesWithinRange(sourceNode, targetNodeList, rangeValue=10):

    nodeList = list()
    targetDistList = list()
    distList = list()

    for targetNode in targetNodeList:
        distValue = getDistance(sourceNode, targetNode)
        targetDistList.append([distValue, targetNode])

    targetDistList = sorted(targetDistList)
    
    for targetDist in targetDistList:
        if targetDist[0] <= rangeValue:
            nodeList.append(targetDist[1])
            distList.append(targetDist[0])

    return nodeList, distList

def parentToClosest(childNodeList, parentNodeList, removeEmptyNodes=False, parentType='Hierarchy'):

    for childNode in childNodeList:

        shapesList = mc.listRelatives(childNode, shapes=True)
        relList = mc.listRelatives(childNode, children=True, type='transform')
        if shapesList != None and relList != None:
            if mc.objectType(shapesList[0]) == 'follicle':
                childNode = '%s.cv[0]'%relList[0]

        distList = []

        for parentNode in parentNodeList:
            distValue = getDistance(childNode, parentNode)
            distList.append(distValue)

        index_min = min(iter(range(len(distList))), key=distList.__getitem__)
        
        if parentType != None:
            if parentType == 'Hierarchy':
                mc.parent(childNode, parentNodeList[index_min])
            else:
                mc.parentConstraint(parentNodeList[index_min], childNode, mo=True)
                mc.scaleConstraint(parentNodeList[index_min], childNode, mo=True)

    if removeEmptyNodes and parentType == 'Hierarchy':

        for parentNode in parentNodeList:

            relNodeList = mc.listRelatives(parentNode, children=True)
            if relNodeList != None:
                if len(relNodeList) == 1:
                    mc.delete(parentNode)

    return parentNodeList[index_min], index_min

def matchGuideToGeo(sourceGeo='Ref:head', targetGeo='head', guidePivots=None):

    if not guidePivots:
        guidePivots = mc.ls(sl=True)

    folNodes = list()
    cntNodes = list()
    for node in guidePivots:
        folNode, cntNode = parentToClosestVertex(node, sourceGeo, parentType='PointConstraint')
        folNodes.append(folNode)
        cntNodes.append(cntNode)
    Nodes.setTrs(sourceGeo)
    bshNode = mc.blendShape(targetGeo, sourceGeo, topologyCheck=False, weight=[0, 1])[0]
    mc.delete(cntNodes)
    mc.delete(folNodes)
    mc.delete(bshNode)

def pinNodesToGeo(nodes, geoNode):

    nodes = [x for x in nodes if Nodes.isNodeConstrainable(x, trs='tr')]
    NodeOnVertex.proximityPin(geoNode, nodes)

def parentToClosestVertex(node, geoNode, attrNode=None, name=None, parentNode=None, orientNode=None, parentType='Hierarchy', orient=True):

    if parentType == 'JointConstraint':
        output = NodeOnVertex.createNodeByVertexWeight(getClosestVertex(node, geoNode)[0], alignOrientation=orient)
        if output != None:
            locNode, parentCnt = output
            mc.parent(node, locNode)
            if attrNode != None:
                weightList = mc.parentConstraint(parentCnt, weightAliasList=True, q=True)
                jointList = mc.parentConstraint(parentCnt, targetList=True, q=True)
                Nodes.addAttrTitle(attrNode, 'parent')
                for j, jointNode in enumerate(jointList):
                    attrName = jointNode+'_weight'
                    mc.addAttr(attrNode, at='float', ln=attrName, k=True, dv=mc.getAttr(parentCnt+'.'+weightList[j]))
                    mc.connectAttr(attrNode+'.'+attrName, parentCnt+'.'+weightList[j])
    else:
        if orientNode != None:
            orient = False

        folNode, exists = NodeOnVertex.createFollicle(geoNode,
                                                        name=Nodes.replaceNodeType(node)+('_'+name if name != None else ''),
                                                        vtxID=getClosestVertex(node, geoNode)[1],
                                                        orient=orient)

        if orientNode != None:
            mc.orientConstraint(orientNode, folNode, mo=True)

        cntNode = None
        if parentType != None:
            if parentType == 'Hierarchy':
                mc.parent(node, folNode)
            else:
                if Nodes.isNodeConstrainable(node, trs='tr'):
                    if parentType == 'Constraint':
                        cntNode = mc.parentConstraint(folNode, node, mo=True)[0]
                    if parentType == 'PointConstraint':
                        cntNode = mc.pointConstraint(folNode, node, mo=True)[0]

        if parentNode != None:
            mc.parent(folNode, parentNode)

        locNode = folNode
        
    mc.select(clear=True)

    return locNode, cntNode

def getClosestVertex(sourceNode, geoNode):
    
    if mc.objectType(sourceNode) == 'mesh':
        tempLoc = mc.spaceLocator()
        Nodes.alignObject(tempLoc, sourceNode, oldStyle=True)
        loc = tempLoc
    else:
        tempLoc = None
        loc = sourceNode

    pos = mc.xform(loc, q=True, rp=True, ws=True)
    
    nodeDagPath = OpenMaya.MObject()
    try:
        selectionList = OpenMaya.MSelectionList()
        selectionList.add(geoNode)
        nodeDagPath = OpenMaya.MDagPath()
        selectionList.getDagPath(0, nodeDagPath)
    except:
        raise RuntimeError('OpenMaya.MDagPath() failed on %s' % geoNode)
    
    mfnMesh = OpenMaya.MFnMesh(nodeDagPath)
    
    pointA = OpenMaya.MPoint(pos[0], pos[1], pos[2])
    pointB = OpenMaya.MPoint()
    space = OpenMaya.MSpace.kWorld
    
    util = OpenMaya.MScriptUtil()
    util.createFromInt(0)
    idPointer = util.asIntPtr()
    
    mfnMesh.getClosestPoint(pointA, pointB, space, idPointer)  
    
    verts = ['%s.vtx[%s]'%(geoNode, i) for i in range(mc.polyEvaluate(geoNode, vertex=True))]
    closestVert = None
    minLength = None
    for v in verts:
        thisLength = getDistance(pos, mc.xform(v, q=True, translation=True, ws=True))
        if minLength is None or thisLength < minLength:
            minLength = thisLength
            closestVert = v.replace('Shape', '')

    closestVertID = int(closestVert.split('[')[1][:-1])

    if tempLoc != None:
        mc.delete(tempLoc)

    return closestVert, closestVertID

def getClosestPoint(sourceNode, latticeNode, detectionRadius=0.01):

    def getPoint(s, t, u):
        return '%s.pt[%s][%s][%s]' % (latticeNode, s, t, u)

    divisions = [mc.getAttr('%s.%sDivisions'%(latticeNode, d)) for d in 'stu']

    sourceTrs = mc.xform(sourceNode, q=True, ws=True, t=True)

    distCollection = []

    for s in range(divisions[0]):
        for t in range(divisions[1]):
            for u in range(divisions[2]):

                distValue = getDistance(sourceNode, getPoint(s, t, u))
                distCollection.append([[s, t, u], distValue])

    minLength = min([x[1] for x in distCollection])

    closestPoint = None

    for n, length in enumerate(distCollection):

        if length[1] >= minLength and length[1] < (minLength + detectionRadius):
            closestPoint = distCollection[n][0]

    return getPoint(closestPoint[0], closestPoint[1], closestPoint[2])

def getMirrorObject(node, objList, tolerance=0.1, bySuffix=False):

    if bySuffix:
        objList = [x for x in mc.ls(type='transform') if Nodes.getNodeType(x) == Nodes.getNodeType(node)]

    pos = mc.xform(node, translation=True, ws=True, q=True)
    mirPos = [-pos[0], pos[1], pos[2]]
    mirObj = None
    for obj in objList:
        objPos = mc.xform(obj, translation=True, ws=True, q=True)
        distValue = getDistance(mirPos, objPos)
        if distValue <= tolerance:
            mirObj = obj
            
    return mirObj

def mirrorObject(node, rotate=(0, 0, 180), removeNode=False, replaceExistingMirNode=True, uniqueCopy=False, byString=False, leftSide=Settings.leftSide, rightSide=Settings.rightSide):

    def renameNode(node, name):

        if Nodes.getSide(node, byString=byString, leftSide=leftSide, rightSide=rightSide) == side:
            mName = Nodes.replaceSide(name, leftSide if side == rightSide else rightSide, byString=byString)
        else:
            mName = node + '_mir'
        
        if mc.objExists(mName):
            if replaceExistingMirNode:
                mc.delete(mName)
            else:
                mName = mName + '_mir'

        mNode = mc.rename(node, mName)

        return mNode

    if Nodes.getSide(node, byString=byString) == leftSide:
        side = leftSide
    else:
        side = rightSide

    isGroup = True if Nodes.getShapeType(node) == None else False
    isJoint = False
    isCurve = False
    isSurface = True if Nodes.getShapeType(node) == 'nurbsSurface' else False
    if not isGroup:
        isJoint = True if Nodes.getShapeType(node) == 'joint' else False
        nodeType = Nodes.getNodeType(node)
        if nodeType:
            isCurve = True if Settings.guideCurveSuffix in nodeType and (Nodes.getShapeType(node) == 'bezierCurve' or Nodes.getShapeType(node) == 'nurbsCurve') else False
    isElse = True if not isJoint and not isCurve else False
    
    if not isJoint:
        
        dupNode = mc.duplicate(node, rc=True)[0]
        
        Nodes.lockAndHideAttributes(dupNode, t=[True, True, True], r=[True, True, True], s=[True, True, True], lock=False, keyable=True)

        if isCurve:
            
            mc.setAttr('%s.sx'%dupNode, -1)
            mc.makeIdentity(dupNode, a=True, s=True)
            mNode = renameNode(dupNode, node)
            mc.setAttr('%s.tx'%mNode, mc.getAttr('%s.tx'%mNode)*-1)
    
        if isGroup or isElse:
            
            origGrp = mc.group(empty=True)
        
            mc.parent(dupNode, origGrp)
        
            mGrp = mc.duplicate(origGrp, rc=True, ic=True)[0]
            mList = mc.listRelatives(mGrp, children=True, type='transform')
        
            mc.setAttr('%s.scaleX' % (mGrp), -1)
            mc.parent(dupNode, world=True)
        
            if mc.objectType(node) == 'joint':
        
                parentList = mc.listRelatives(node, parent=True)
                if parentList != None:
                    parentGrp = parentList[0]
        
                mJointList = mc.duplicate(node, rc=True, ic=True)
        
                mJointNodeParentList = []
                mNodeList = []
        
                for m, mNode in enumerate(mJointList[::-1]):
        
                    mJointNodeParent = mc.listRelatives(mNode, parent=True)[0]
                    mJointNodeParentList.append(mJointNodeParent)
        
                    mc.parent(mNode, world=True)
        
                    Nodes.alignObject(mNode, mList[m])
        
                    mNodeList.append(mNode)
        
                for m, mNode in enumerate(mNodeList):
        
                    if m < len(mNodeList)-1:
        
                        mc.parent(mNode, mJointNodeParentList[m])
        
                for m, mNode in enumerate(mNodeList):
                    mNode = renameNode(mNode, node)
        
                if parentList != None:
                    mc.parent(mNode, parentGrp)
        
            else:
        
                mc.parent(mList, world=True)
        
                for mNode in mList:
        
                    childList = mc.listRelatives(mNode, children=True, ad=True, type='transform')
        
                    if childList != None:
        
                        mc.delete(childList)

                    if not isSurface:
                        mc.makeIdentity(mNode, a=True, s=True)
        
                    mc.rotate(rotate[0], rotate[1], rotate[2], mNode, r=True, os=True)

                    mNode = renameNode(mNode, node)
        
            mc.delete(origGrp, mGrp, dupNode)
        
            Nodes.setParent(mNode, Nodes.getParent(node))

    else:

        mList = mc.mirrorJoint(node, mirrorYZ=True, mirrorBehavior=True)
        mList = [x for x in mList if mc.objectType(x) == 'transform' or mc.objectType(x) == 'joint']
        mList = [renameNode(m, m) for m in mList]
        mNode = mList[0]
 
    if not replaceExistingMirNode and not uniqueCopy:
        if Nodes.getSide(node, byString=byString) == side:
            existingMirNode = Nodes.replaceSide(node, leftSide if side == rightSide else rightSide)
        else:
            existingMirNode = node + '_mir'
        if mc.objExists(existingMirNode):
            Nodes.alignObject(existingMirNode, mNode)
            mc.delete(mNode)
            mNode = existingMirNode

    if removeNode:
        mc.delete(node)

    return mNode

def getMirrorVertex(geoNode, vtx, tolerance=0.02, space='object'):
    
    def getVertex(node, v):
        return '%s.vtx[%s]' % (node, v)
    
    objectSpace = True if space == 'object' else False
    worldSpace = True if space == 'world' else False
    
    vCount = mc.polyEvaluate(geoNode, vertex=True)

    leftVList = []
    rightVUnsortedList = []
    
    for v in range(vCount):

        p = mc.xform(getVertex(geoNode, v),
                     os=objectSpace,
                     ws=worldSpace,
                     q=True,
                     translation=True)
        
        rightVUnsortedList.append([v, p])
        
    vtxPos = mc.xform(getVertex(geoNode, vtx),
                      os=objectSpace,
                      ws=worldSpace,
                      q=True,
                      translation=True)    
    
    rightVList = []

    for rv in rightVUnsortedList:

        p = [vtxPos[0] + rv[1][0], vtxPos[1] - rv[1][1], vtxPos[2] - rv[1][2]]

        a = abs(p[0]) + abs(p[1]) + abs(p[2])

        if a < tolerance:
            mirVtx = rv[0]

    return mirVtx  

def mirrorVertices(nodeList,
                   leftVList=None,
                   rightVList=None,
                   midVList=None,
                   direction='-X',
                   swop=True,
                   setSource=False,
                   tolerance=0.001,
                   space='object'):

    def getVertex(node, v):
        return '%s.vtx[%s]' % (node, v)

    objectSpace = True if space == 'object' else False
    worldSpace = True if space == 'world' else False
    
    if setSource:

        vCount = mc.polyEvaluate(nodeList[0], vertex=True)

        leftVUnmatchedList = []
        leftVList = []
        rightVUnsortedList = []
        midVList = []
        unmatchedVList = []

        for v in range(vCount):

            p = mc.xform(getVertex(nodeList[0], v),
                         os=objectSpace,
                         ws=worldSpace,
                         q=True,
                         translation=True)
            if len(nodeList) == 2:
                r = mc.xform(getVertex(nodeList[1], v),
                             os=objectSpace,
                             ws=worldSpace,
                             q=True,
                             translation=True)

            if p[0] > tolerance:
                leftVUnmatchedList.append([v, p])
            if len(nodeList) == 1:
                if p[0] < -tolerance:
                    rightVUnsortedList.append([v, p])
                if p[0] < tolerance and p[0] > -tolerance:
                    midVList.append([v, p])
            if len(nodeList) == 2:
                rightVUnsortedList.append([v, r])

        rightVList = []

        for lv in leftVUnmatchedList:
            match = False
            for rv in rightVUnsortedList:

                p = [lv[1][0] + rv[1][0], lv[1][1] - rv[1][1], lv[1][2] - rv[1][2]]

                a = abs(p[0]) + abs(p[1]) + abs(p[2])

                if a < tolerance:
                    if rv in rightVList:
                        MessageHandling.warning('Target vertex already in list. Tolerance might be too high.')
                    else:
                        rightVList.append([rv[0], rv[1]])
                        match=True
            if match:
                if lv in leftVList:
                    MessageHandling.warning('Source vertex already in list.')
                else:
                    leftVList.append(lv)
            else:
                unmatchedVList.append(lv)

        return leftVList, rightVList, midVList, unmatchedVList

    else:

        if len(nodeList) == 2:
            node = nodeList[0]
            mNode = nodeList[1]
        else:
            node = nodeList[0]
            mNode = nodeList[0]

        if direction == '-X':
            svList = leftVList
            tvList = rightVList
        else:
            svList = rightVList
            tvList = leftVList

        if swop:

            psvList = [mc.xform(getVertex(node, sv[0]),
                                os=objectSpace,
                                ws=worldSpace,
                                q=True,
                                translation=True) for sv in svList]
            ptvList = [mc.xform(getVertex(mNode, tv[0]),
                                os=objectSpace,
                                ws=worldSpace,
                                q=True,
                                translation=True) for tv in tvList]
            pmvList = [mc.xform(getVertex(node, mv[0]),
                                os=objectSpace,
                                ws=worldSpace,
                                q=True,
                                translation=True) for mv in midVList]

            for i, sv in enumerate(svList):
                p = psvList[i]
                mp = (-p[0], p[1], p[2])
                try:
                    mc.xform(getVertex(mNode, tvList[i][0]),
                                    os=objectSpace,
                                    ws=worldSpace,
                                    translation=mp)
                except:
                    print('skipped: ', sv)
                    pass

            for i, tv in enumerate(tvList):
                p = ptvList[i]
                mp = (-p[0], p[1], p[2])
                try:
                    mc.xform(getVertex(node, svList[i][0]),
                                    os=objectSpace,
                                    ws=worldSpace,
                                    translation=mp)
                except:
                    print('skipped: ', tv)
                    pass

            for i, mv in enumerate(midVList):
                p = pmvList[i]
                mp = (-p[0], p[1], p[2])
                try:
                    mc.xform(getVertex(node, mv[0]),
                                    os=objectSpace,
                                    ws=worldSpace,
                                    translation=mp)
                except:
                    print('skipped: ', mv)
                    pass

        else:

            for i, sv in enumerate(svList):
                p = mc.xform(getVertex(node, sv[0]),
                                os=objectSpace,
                                ws=worldSpace,
                                q=True,
                                translation=True)
                mp = (-p[0], p[1], p[2])
                mc.xform(getVertex(mNode, tvList[i][0]),
                                os=objectSpace,
                                ws=worldSpace,
                                translation=mp)

            for mv in midVList:
                p = mv[1]
                mp = (0, p[1], p[2])

def mirrorBlendshapes(nodeList, tolerance=0.01):

    sourceMirror = Nodes.getNodesByAttr('sourceMirror')[0]

    if not mc.objExists(sourceMirror):
        return
    
    leftVList, rightVList, midVList, unmatchedVList = mirrorVertices([sourceMirror], swop=False, setSource=True, tolerance=float(tolerance))
    if not MessageHandling.symmetryOutput(len(leftVList), len(rightVList), len(midVList), len(unmatchedVList), popIfGood=False, query=True):
        return

    for node in nodeList:
        
        bshGroup = Nodes.getParent(node)
        geoName = node.split('__')[0]
        side = mc.getAttr('%s.side'%bshGroup)

        if side == Settings.leftSide or side == Settings.rightSide:

            if side == Settings.leftSide:
                targetSide = Settings.rightSide
                direction = '-X'
            else:
                targetSide = Settings.leftSide
                direction = 'X'

            mirBshGroup = '_'.join([targetSide if x == side else x for x in node.split('__')[1].split('_')])
            mirNode = geoName + '__' + mirBshGroup

            if not Nodes.exists(mirBshGroup):
                mc.duplicate(bshGroup, name=mirBshGroup)[0]
                Nodes.delete(Nodes.getChildren(mirBshGroup, longName=True))
                Nodes.setParent(mirBshGroup, Settings.faceBshGroup)
                mc.setAttr('%s.side'%mirBshGroup, Settings.rightSide, type='string')
                controlNodeValTokens = list()
                for x in mc.getAttr('%s.controlNode'%mirBshGroup).split('_'):
                    if x == Settings.leftSide:
                        controlNodeValTokens.append(Settings.rightSide)
                    else:
                        controlNodeValTokens.append(x)
                mc.setAttr('%s.controlNode'%mirBshGroup, '_'.join(controlNodeValTokens), type='string')
                mc.setAttr('%s.tx'%mirBshGroup, -mc.getAttr('%s.tx'%mirBshGroup))

            if not Nodes.exists(mirNode):
                mc.duplicate(node, name=mirNode)[0]
                Nodes.setParent(mirNode, mirBshGroup)
                mc.setAttr('%s.tx'%mirNode, 0)

            bshNode = mc.blendShape(node, mirNode)[0]
            mc.setAttr('%s.%s' % (bshNode, node), 1)
            mc.delete(mirNode, ch=True)

            mirrorVertices([mirNode], leftVList, rightVList, midVList, direction, swop=True)

        mc.refresh()

def clean_duplicate(original_mesh, suffix='dup'):
    # Duplicate the mesh without history
    dup = mc.duplicate(original_mesh, name=original_mesh + "_" + suffix, returnRootsOnly=True)[0]
    
    # List all shapes under the duplicated transform
    shapes = mc.listRelatives(dup, shapes=True, fullPath=True) or []
    
    for shape in shapes:
        # Check if shape is intermediateObject
        if mc.getAttr(shape + ".intermediateObject"):
            mc.delete(shape)

    # Ensure the duplicate has no construction history
    mc.delete(dup, constructionHistory=True)
    
    return dup

def copy_vertex_positions(source_mesh, target_mesh):
    """
    Copies vertex positions from the source mesh to the target mesh using OpenMaya.

    Args:
        source_mesh (str): Name of the source mesh (transform or shape).
        target_mesh (str): Name of the target mesh (transform or shape).
    """
    def get_dag_path(mesh_name):
        """
        Gets the DAG path for a given mesh.
        If a transform node is provided, its shape child is retrieved.

        Args:
            mesh_name (str): Name of the transform or shape node.
        
        Returns:
            MDagPath: DAG path to the shape node of the mesh.
        """
        sel = OpenMaya.MSelectionList()
        sel.add(mesh_name)
        dag_path = sel.getDagPath(0)
        
        # If the object is a transform, get its shape child
        if dag_path.node().hasFn(OpenMaya.MFn.kTransform):
            dag_path.extendToShape()
        
        # Ensure it's a mesh
        if not dag_path.node().hasFn(OpenMaya.MFn.kMesh):
            raise ValueError(f"{mesh_name} is not a valid mesh shape.")
        
        return dag_path

    # Get DAG paths for source and target shape nodes
    source_dag_path = get_dag_path(source_mesh)
    target_dag_path = get_dag_path(target_mesh)
    
    # Create mesh function sets
    source_mesh_fn = OpenMaya.MFnMesh(source_dag_path)
    target_mesh_fn = OpenMaya.MFnMesh(target_dag_path)
    
    # Get vertex positions from the source mesh
    source_points = source_mesh_fn.getPoints(OpenMaya.MSpace.kWorld)
    
    # Set vertex positions on the target mesh
    target_mesh_fn.setPoints(source_points, OpenMaya.MSpace.kWorld)

def blendShapeBlend(bshSrc='Ref:head__*_bshSrc', excludeVertices='excludeVertices', selList=None, weightValue=0, useBlendshape=True):

    bshTrg = bshSrc.split(':')[1]

    if selList == None:

        srcNodes = mc.ls(bshSrc, type='transform')
        trgNodes = mc.ls(bshTrg, type='transform')

    else:

        srcNodes = selList
        trgNodes = [sel.split(':')[1] for sel in selList]

    excludeIndices = list()
    
    if excludeVertices != None:
        if mc.objExists(excludeVertices):
            if mc.objectType(excludeVertices) == 'objectSet':
                setVertices = [x.split('[')[1].split(']')[0] for x in mc.sets(excludeVertices, q=True) if not 'bshSrc' in x]
                for setV in setVertices:
                    if ':' in setV:
                        for v in range(int(setV.split(':')[0]), int(setV.split(':')[1])+1):
                            excludeIndices.append(v)
                    else:
                        excludeIndices.append(setV)

    for srcNode in srcNodes:
        foundTrgNodes = [x for x in trgNodes if srcNode.split('|')[-1].split(':')[-1] in x]
        if len(trgNodes) > 0 and len(foundTrgNodes) > 0:
            trgNode = foundTrgNodes[0]
            
            if excludeIndices or useBlendshape:
                bshNode = mc.blendShape(srcNode, trgNode, w=(0, 1))[0]
                if excludeVertices != None:
                    if mc.objExists(excludeVertices):
                        for vSet in excludeIndices:
                            if type(vSet) == list:
                                v = vSet[0]
                            else:
                                v = vSet
                            mc.setAttr('%s.inputTarget[0].inputTargetGroup[0].targetWeights[%s]'%(bshNode, v), weightValue)
            else:
                copy_vertex_positions(srcNode, trgNode)

def grabSourceBlendshape(node, jawControl=Nodes.createName('mouth', element='jaw', nodeType=Settings.controlSuffix)[0], withCorrection=True):

    sourceGeo = node.split('__')[0]
    jawGuide = Nodes.replaceNodeType(jawControl, Settings.guideShapeSuffix)
    jawOpenVal = mc.getAttr('%s.bsh_rotateX_pos'%jawGuide)
    
    for inputType in ['wrap', 'proximityWrap', 'deltaMush', 'tension']:
        inputNodes = Nodes.getInputNodes(sourceGeo, inputType)[0]
        if inputNodes != []:
            if not Nodes.isConnected(inputNodes[0], customAttrName='envelope'):
                mc.setAttr('%s.envelope'%inputNodes[0], 0)
    
    bshNode = sourceGeo+'_poseCorrectionBlendshape'
    if mc.objExists(bshNode) and not withCorrection:
        mc.setAttr('%s.envelope'%bshNode, 0)

    attrHolder = Nodes.getParent(node)
    jawState = mc.getAttr('%s.jawState'%attrHolder)
    if jawState == 'jawOpen':
        mc.setAttr('%s.rx'%jawControl, jawOpenVal)
    else:
        mc.setAttr('%s.rx'%jawControl, 0)
        
    
    if mc.getAttr('%s.combine'%attrHolder):
        attrSplit = attrHolder.replace('combine_', '').split('_')
        attrHolder1 = '_'.join(attrSplit[:-3]+[Settings.bshSrcGeoNodeSuffix])
        attrHolder2 = '_'.join(attrSplit[:-5]+attrSplit[-3:-1]+[Settings.bshSrcGeoNodeSuffix])
        attrHolders = [attrHolder1, attrHolder2]
    else:
        attrHolders = [attrHolder]

    for attrHolder in attrHolders:
        controlNode = mc.getAttr('%s.controlNode'%attrHolder)
        bshAttr1 = mc.getAttr('%s.bshAttr1'%attrHolder)
        dirAttr1 =  mc.getAttr('%s.directionAttr1'%attrHolder)
        targetVal = mc.getAttr('%s.targetValue'%attrHolder) * (-1 if dirAttr1 == 'neg' else 1)
        mc.setAttr('%s.%s'%(controlNode, bshAttr1), targetVal)

    sourceDup = mc.duplicate(sourceGeo, name=sourceGeo+'_sourceShape')[0]
    mc.blendShape(sourceDup, node, name='sourceShape', w=(0, 1))[0]
    Nodes.delete(sourceDup)

    for attrHolder in attrHolders:
        controlNode = mc.getAttr('%s.controlNode'%attrHolder)
        bshAttr1 = mc.getAttr('%s.bshAttr1'%attrHolder)
        mc.setAttr('%s.%s'%(controlNode, bshAttr1), 0)
    mc.setAttr('%s.rx'%jawControl, 0)
    
    bshNode = sourceGeo+'_poseCorrectionBlendshape'
    if mc.objExists(bshNode) and not withCorrection:
        mc.setAttr('%s.envelope'%bshNode, 1)

def smoothSkinWeights(node=None, joints=None, iterations=1):

    currentTool = mc.currentCtx()
    
    mc.select(node)

    if not joints:
        joints = mc.skinCluster(Nodes.getSkinCluster(node)[0], q=True, inf=True)
    
    skinPaintTool = 'artAttrSkinContext'
    if not mc.artAttrSkinPaintCtx(skinPaintTool, ex=True):
        mc.artAttrSkinPaintCtx(skinPaintTool, i1='paintSkinWeights.xpm', whichTool='skinWeights')

    mc.setToolTo(skinPaintTool)
    mc.artAttrSkinPaintCtx(skinPaintTool, edit=True, sao='smooth')
    
    for influence in joints:
        for _ in range(iterations):
            mel.eval('artSkinSelectInfluence artAttrSkinPaintCtx "' + influence + '"')
            mc.artAttrSkinPaintCtx(skinPaintTool, e=True, clear=True)
    
    mc.setToolTo(currentTool)
    
def copySkinCluster(sourceObj, 
                    targetObjList, 
                    recreateSkinCluster=True, 
                    fromRef=False, 
                    refPrefix='Ref:',
                    refSuffix=False,
                    extendedSuffix=False,
                    influenceAssociation='closestJoint',
                    surfaceAssociation='closestPoint',
                    uv=False,
                    byVertexOrder=False):

    if byVertexOrder:

        for targetObj in targetObjList:
            
            if fromRef:
                sourceObj = refPrefix+targetObj
            if not mc.objExists(sourceObj):
                MessageHandling.warning('Source Object not found: '+sourceObj)
                continue

            sourceSkinCluster, skinMethod, skinJointList = Nodes.getSkinCluster(sourceObj)
                        
            if fromRef:
                skinJointList = [skinJoint.split(':')[1] for skinJoint in skinJointList]

            if sourceSkinCluster != None:
                
                normalizeWeights = mc.getAttr('%s.normalizeWeights' % sourceSkinCluster)    
                targetSkinCluster = Nodes.getSkinCluster(targetObj)[0]

                if recreateSkinCluster:
                    mc.delete(targetSkinCluster)
                    targetSkinCluster = mc.skinCluster(skinJointList, targetObj, tsb=True)[0]
                    mc.setAttr('%s.skinningMethod' % targetSkinCluster, skinMethod)
                    mc.setAttr('%s.normalizeWeights' % targetSkinCluster, normalizeWeights)
                    
                vtxCount = len(mc.getAttr('%s.vtx[*]' % (sourceObj)))

                for i in range(vtxCount):
                    sourceSkinWeight = mc.skinPercent(sourceSkinCluster, '%s.vtx[%s]' % (sourceObj, i), query=True,
                                                      value=True)
                    targetSkinJoint = mc.skinPercent(targetSkinCluster, '%s.vtx[%s]' % (targetObj, i), query=True,
                                                     transform=None)

                    skinSetList = []

                    for t in range(len(sourceSkinWeight)):
                        skinSet = (targetSkinJoint[t], sourceSkinWeight[t])
                        skinSetList.append(skinSet)

                    mc.skinPercent(targetSkinCluster, '%s.vtx[%s]' % (targetObj, i), transformValue=skinSetList)

    else:
        
        for targetObj in targetObjList:
            
            if fromRef:
                refNode = targetObj+'_'+refSuffix if extendedSuffix else targetObj
                sourceObj = refPrefix+(targetObj if not refSuffix else refNode)

            sourceSkinCluster, skinMethod, skinJointList = Nodes.getSkinCluster(sourceObj)

            if skinJointList != None:
                if fromRef:
                    if extendedSuffix:
                        skinJointList = [Nodes.replaceNodeType(skinJoint) for skinJoint in skinJointList]
                    else:
                        skinJointList = [skinJoint.split(':')[1] for skinJoint in skinJointList]
                
                if sourceSkinCluster != None:
                    
                    normalizeWeights = mc.getAttr('%s.normalizeWeights' % sourceSkinCluster)
                    
                    targetSkinCluster = Nodes.getSkinCluster(targetObj)[0]
                    if recreateSkinCluster:
                        if targetSkinCluster != None:
                            mc.delete(targetSkinCluster)

                        existingSkinJoints = list()
                        for skinJoint in skinJointList:
                            if mc.objExists(skinJoint):
                                existingSkinJoints.append(skinJoint)
                            else:
                                print('Skin Joint not found: '+skinJoint)

                        targetSkinCluster = mc.skinCluster(existingSkinJoints, targetObj, tsb=True)[0]
                        mc.setAttr('%s.normalizeWeights' % targetSkinCluster, normalizeWeights)
                        if skinMethod != None:
                            mc.setAttr('%s.skinningMethod' % targetSkinCluster, skinMethod)
                    
                    if not uv:
                        mc.copySkinWeights(ss=sourceSkinCluster, 
                                            ds=targetSkinCluster, 
                                            sm=True, 
                                            nm=True, 
                                            sa=surfaceAssociation, 
                                            ia=influenceAssociation)
                    else:
                        mc.copySkinWeights(ss=sourceSkinCluster, 
                                            ds=targetSkinCluster, 
                                            sm=True, 
                                            nm=True, 
                                            sa=surfaceAssociation, 
                                            ia=influenceAssociation, 
                                            uv=uv)
                
    mc.select(targetObjList)

def copyVertexSkinWeightsAlongLoops(skipRootVertexOffset=8, skipTipVertexOffset=8, sourceSkinVertexOffset=0):

    selList = mc.ls(sl=True, fl=True)
    geoNode = selList[0].split('.')[0]
    sourceSkinCluster = Nodes.getSkinCluster(geoNode)[0]

    if sourceSkinCluster == None:
        mc.error('Selected node has no skin cluster')

    mc.select('%s.vtx[0]'%geoNode, '%s.vtx[1]'%geoNode)
    mc.polySelectSp(loop=True)
    selList = mc.ls(sl=True, fl=True)
    frontLoop = [selList[x] for x in range(skipRootVertexOffset, (len(selList)-1)-skipTipVertexOffset, 2)]

    for c in range(len(frontLoop)-1):

        vertID = int(frontLoop[c].split('[')[1].split(']')[0])

        mc.select([frontLoop[c], '%s.vtx[%s]'%(geoNode, str(vertID+1))])
        mc.polySelectSp(loop=True)
        loopSelList = mc.ls(sl=True, fl=True)
        if loopSelList != []: 
            sourceSkinVertex = loopSelList[sourceSkinVertexOffset]

            skinWeight = mc.skinPercent(sourceSkinCluster, sourceSkinVertex, query=True,
                                                        value=True)
            skinJoint = mc.skinPercent(sourceSkinCluster, sourceSkinVertex, query=True,
                                                transform=None)
            
            skinSetList = []
            for t in range(len(skinWeight)):
                skinSet = (skinJoint[t], skinWeight[t])
                skinSetList.append(skinSet)  
            
            for loopSel in loopSelList:
                mc.skinPercent(sourceSkinCluster, transformValue=skinSetList)

    mc.select(geoNode)

def blendLoopSkinWeights(startLoop, endLoop, startWeight=1, endWeight=0, joints=[], detectClosestJoint=True):

    mel.eval("setToolTo $gSelect")

    singleBlendLoop = True if '.vtx' in startLoop[0] and '.vtx' in endLoop[0] else False

    startLoop = mc.ls(startLoop, fl=True)
    mc.select(startLoop)
    startLoopVertices = mc.polyListComponentConversion(startLoop, toVertex=True)
    startLoopVertices = mc.ls(startLoopVertices, fl=True)
    endLoop = mc.ls(endLoop, fl=True)
    mc.select(endLoop)
    endLoopVertices = mc.polyListComponentConversion(endLoop, toVertex=True)
    endLoopVertices = mc.ls(endLoopVertices, fl=True)
    
    geoNode = startLoopVertices[0].split('.vtx')[0]
    skinClusterNode = Nodes.getSkinCluster(geoNode)[0]
    
    for fVtx in startLoopVertices:

        if singleBlendLoop:
            sVtx = endLoop[0]
        else:
            mc.polySelect(geoNode, edgeLoop=int(startLoop[0].split('[')[1].split(']')[0]))
            startLoopInf = mc.ls(sl=True, fl=True)
            mc.polySelect(geoNode, edgeLoop=int(endLoop[0].split('[')[1].split(']')[0]))
            edges = mc.polyListComponentConversion(fVtx, toEdge=True)
            edges = mc.ls(edges, fl=True)
            mc.select(edges)
            perpLoop = [v for v in edges if v not in startLoopInf]
            mc.polySelect(geoNode, edgeLoop=int(perpLoop[0].split('[')[1].split(']')[0]))
            perpLoopVertices = mc.polyListComponentConversion(mc.ls(sl=True), toVertex=True)
            perpLoopVertices = mc.ls(perpLoopVertices, fl=True)
            mc.select(perpLoopVertices)
            sVtxs = sorted([v for v in perpLoopVertices if v in endLoopVertices], key=lambda k: getDistance(k, fVtx))
            if sVtxs == []:
                return None
            sVtx = sVtxs[0]
        
        mc.select([fVtx, sVtx])
        mel.eval('SelectEdgeLoopSp')
        fsVtxLoop = mc.ls(sl=True, fl=True)
        
        fullDistance = getDistance(fVtx, sVtx)
        lengths = list()
        for vtx in fsVtxLoop:
            vtxDict = dict()
            vtxDict['vertex'] = vtx
            distWeight = getDistance(fVtx, vtx)/fullDistance
            vtxDict['weight'] = distWeight*endWeight + (1-distWeight)*startWeight
            lengths.append(vtxDict)
        sortedLengths = sorted(lengths, key=lambda k: k['weight']) 
        
        if detectClosestJoint:
            # we create a temporary node to be used for detecting closest joint. This node lives inbetween
            # the start and end vertex positions
            posTmpNode = AddNode.emptyNode('posTmpNode')
            Nodes.alignObject(posTmpNode, fVtx, oldStyle=True)
            midVector = [x*0.5 for x in getVector(fVtx, sVtx)]
            mc.move(midVector[0], midVector[1], midVector[2], posTmpNode, r=True)

            skinJoint = getClosestNode(posTmpNode, joints)[0]

            mc.delete(posTmpNode)
        else:
            skinJoint = joints[0]
        
        for vtxDict in sortedLengths:
            mc.select(vtxDict['vertex'])
            mc.skinPercent(skinClusterNode, transformValue=(skinJoint, vtxDict['weight']))

    mc.select(geoNode)

    return True
        
def removeZeroWeights(node, tolerance=0.001):

    inputNode, skinMethod, skinJointList = Nodes.getSkinCluster(node)

    if inputNode == None:
        return MessageHandling.warning('No skin cluster found: %s - Aborted.'%node)

    vertexCount = mc.polyEvaluate(node, v=True)

    removeSkinJointList = list()

    mc.skinPercent(inputNode, prw=tolerance)
    keepSkinJointList = mc.skinCluster(inputNode, wi=True, q=True)

    for skinJoint in skinJointList:

        if not skinJoint in keepSkinJointList:

            removeSkinJointList.append(skinJoint)

    mc.skinCluster(inputNode, edit=True, removeInfluence=removeSkinJointList)

    return removeSkinJointList

def mirrorDeformerWeights(sourceDeformer, targetDeformer, sourceGeoNode, targetGeoNode, mirror=True, mirrorInverse=False):
    
    if mirror:
        mc.copyDeformerWeights(sd=sourceDeformer, dd=targetDeformer, ss=sourceGeoNode, ds=targetGeoNode, mirrorMode='YZ', mirrorInverse=mirrorInverse)
    else:
        if sourceGeoNode == targetGeoNode:
            # due to a maya bug / limitation, copying weights on the same geometry needs a custom method
            numVertices = mc.polyEvaluate(sourceGeoNode, vertex=True)
            for i in range(numVertices):
                weight = mc.getAttr('{}.weightList[0].weights[{}]'.format(sourceDeformer, i))
                mc.setAttr('{}.weightList[0].weights[{}]'.format(targetDeformer, i), weight)
        else:
            mc.copyDeformerWeights(sd=sourceDeformer, dd=targetDeformer, ss=sourceGeoNode, ds=targetGeoNode, noMirror=True)

def updateSkin(jawClosedNode='jaw_jawClosed', skinMeshNode='skin_skm', headTmpNode='head_tmp', bodyTmpNode='body_tmp', skinStaticTmpNode='skin_static_tmp', skinTransferUVSet='dataTransfer'):

    jawClosedVal = mc.getAttr('%s.rx'%jawClosedNode)
    mc.setAttr('%s.rx'%jawClosedNode, 0)
    skmSkin = Nodes.getSkinCluster(skinMeshNode)[0]
    headSkin = Nodes.getSkinCluster(headTmpNode)[0]
    bodySkin = Nodes.getSkinCluster(bodyTmpNode)[0]
    staticSkin = Nodes.getSkinCluster(skinStaticTmpNode)[0]

    skmUVSets = mc.polyUVSet(skinMeshNode, allUVSets=True, q=True)
    if skinTransferUVSet in skmUVSets:
        skmUVSet = skinTransferUVSet
    else:
        skmUVSet = skmUVSets[0]

    mc.setAttr('%s.envelope'%skmSkin, 0)
    mc.copySkinWeights(ss=skmSkin, ds=skmSkin, mirrorMode='YZ', sa='closestPoint', ia='closestJoint')
    for s, skinNode in enumerate([headSkin, bodySkin, staticSkin]):

        uvSets = mc.polyUVSet([headTmpNode, bodyTmpNode, skinStaticTmpNode][s], allUVSets=True, q=True)
        if skinTransferUVSet in uvSets:
            uvSet = skinTransferUVSet
        else:
            uvSet = uvSets[0]

        mc.copySkinWeights(ss=skmSkin, ds=skinNode, sa='closestPoint', uv=(skmUVSet, uvSet), ia='label', sm=True, nm=True)
    mc.setAttr('%s.rx'%jawClosedNode, jawClosedVal)
    mc.setAttr('%s.envelope'%skmSkin, 1)

def drivenConstraint(sourceNode, targetNodeList, attrName='value', addAttrTo='sourceNode', parentConstrained=True, scaleConstrained=True):
    # NOT IN USE, NEEDS WORK
    def addAttr(attrTarget, attrName=attrName):
        mc.addAttr(attrTarget, at='float', ln=attrName, dv=0.0, keyable=True, hasMaxValue=True, maxValue=1.0,
                   hasMinValue=True, minValue=0.0)

    attrTargetList = [sourceNode] if addAttrTo == 'sourceNode' else targetNodeList

    if len(attrTargetList) == 1:
        addAttr(sourceNode)

    for t, targetNode in enumerate(targetNodeList):

        if len(attrTargetList) > 1:
            addAttr(attrTargetList[t])

        sourceAttr = attrTargetList[t] + '.' + attrName

        parentNode = mc.listRelatives(targetNode, parent=True)[0]
        cntNode = AddNode.inbetweenNode(parentNode, nodeType='drivenConstraint')
        drvNode = AddNode.childNode(parentNode)

        constrainedList = []

        if parentConstrained:
            parentCnt = mc.parentConstraint([parentNode, drvNode], cntNode, mo=False)[0]
            mc.setAttr('%s.interpType' % (parentCnt), 2)
            constrainedList.append(parentCnt)
        if scaleConstrained:
            scaleCnt = mc.scaleConstraint([parentNode, drvNode], cntNode, mo=False)[0]
            constrainedList.append(scaleCnt)

        for constrained in constrainedList:
            for n, node in enumerate([parentNode, drvNode]):
                for v in [n, 1-n]:
                    mc.setDrivenKeyframe(constrained + '.' + node + 'W' + str(n),
                                         cd=sourceAttr, dv=v, v=1 if v == n else 0, itt='linear', ott='linear')

def drivenAttr(sourceNode, 
                sourceAttr, 
                drivenNode, 
                drivenAttr, 
                attrNode, 
                attrName, 
                attrTitle=None,
                defaultValue=0,
                attrIsKeyable=True,
                lowerLimit=None,
                upperLimit=None):

    if attrTitle != None:
        Nodes.addAttrTitle(attrNode, attrTitle)
    if not mc.objExists(attrNode+'.'+attrName):
        mc.addAttr(attrNode, at='float', ln=attrName, k=attrIsKeyable, dv=defaultValue,
                    hasMinValue=True if lowerLimit else False, hasMaxValue=True if upperLimit else False,
                    minValue=lowerLimit if lowerLimit else -1000, maxValue=upperLimit if upperLimit else 1000)
        if not attrIsKeyable:
            mc.setAttr(attrNode+'.'+attrName, cb=True)

    Nodes.mulNode(input1='%s.%s' % (attrNode, attrName), 
                    input2='%s.%s' % (sourceNode, sourceAttr), 
                    output='%s.%s' % (drivenNode, drivenAttr))

def multiplyTransforms(drvNode,
                        trgNode,
                        attrNode,
                        attrName,
                        titleName,
                        axis='xyz',
                        transforms='trs',
                        defaultValue=0):
    # NOT IN USE, NEEDS WORK
    Nodes.addAttrTitle(attrNode, titleName)
    for trs in transforms:
        for a in axis:
            attrName = axis+attrName
            attr = attrNode+'.'+attrName
            mc.addAttr(attrNode,
                        at='float',
                        ln=attrName,
                        k=False,
                        dv=defaultValue)
            mc.setAttr(attr, cb=True)
            mulNode = mc.shadingNode('multiplyDivide', asUtility=True, name=Nodes.replaceNodeType(attrNode, 'pushMul'))
            mc.connectAttr('%s.ty'%drvNode, '%s.input1%s'%(mulNode, a.capitalize()))
            mc.connectAttr(attr, '%s.input2%s'%(mulNode, a.capitalize()))
            mc.connectAttr('%s.output%s'%(mulNode, a.capitalize()), '%s.t%s'%(trgNode, a))

def blendBetween(
    sourceNodeList, 
    targetNodeList, 
    drivenNodeList, 
    attrNode=None, 
    attrName=None, 
    attrTitle=None,
    attr=None,
    parentConstrained=True, 
    parentConstrainedTranslate=False, 
    scaleConstrained=True, 
    positionConstrained=False, 
    pointConstrained=False,
    orientConstrained=False, 
    trsValues=False,
    maintainOffset=True, 
    defaultValue=0,
    createDrvObj=False, 
    rigGroup=None,
    attrIsKeyable=True,
    attrIsVisible=True,
    createHermiteBlending=False,
    attrKeys=None,
    drivenKeys0=None,
    drivenKeys1=None,
    ):
    
    def createAttr(attr, attrNode, attrName, drivenNode):
    
        if attr:
            sourceAttr = attr
        else:
            sourceAttr = attrNode + '.' + attrName
            if not mc.objExists(sourceAttr) and drivenNode != None:
                if attrTitle != None:
                    Nodes.addAttrTitle(attrNode, attrTitle)
                mc.addAttr(attrNode, at='float', ln=attrName, k=attrIsKeyable, dv=defaultValue, hasMinValue=True, minValue=0, hasMaxValue=True, maxValue=1)
                if not attrIsKeyable and attrIsVisible:
                    mc.setAttr(sourceAttr, cb=True)

        return sourceAttr

    if positionConstrained or pointConstrained:
        parentConstrained = False
        scaleConstrained = False
    if orientConstrained:
        parentConstrained = False
        scaleConstrained = False
    
    conNodes = list()
    
    for t, targetNode in enumerate(targetNodeList):
        
        drivenNode = drivenNodeList[t]

        if createDrvObj:
            targetNodeDrv = mc.group(name=Nodes.replaceNodeType(targetNode)+'_'+Nodes.replaceNodeType(drivenNode)+'_trgDrv', empty=True)
            sourceNodeDrv = mc.group(name=Nodes.replaceNodeType(sourceNodeList[t])+'_'+Nodes.replaceNodeType(drivenNode)+'_srcDrv', empty=True)
            Nodes.alignObject(targetNodeDrv, drivenNode)
            Nodes.alignObject(sourceNodeDrv, drivenNode)
            parentScaleConstraint(targetNode, targetNodeDrv)
            parentScaleConstraint(sourceNodeList[t], sourceNodeDrv)
            if rigGroup != None:
                mc.parent(targetNodeDrv, rigGroup)
                mc.parent(sourceNodeDrv, rigGroup)
            targetNode = targetNodeDrv
            sourceNode = sourceNodeDrv
        else:
            sourceNode = sourceNodeList[t]

        if trsValues:
            sourceAttr = createAttr(attr, attrNode, attrName, drivenNode)

        constrainedList = []
        
        if sourceNode and targetNode and drivenNode:

            if trsValues:
                for trs in ['translate', 'rotate']:
                    Nodes.divNode(
                        input1=sourceAttr,
                        input2='%s.%s'%(targetNode, trs),
                        output='%s.%s'%(drivenNode, trs),
                        axis='XYZ',
                        operation=1
                        )
                continue
            
            if parentConstrained:
                try:
                    parentCnt = mc.parentConstraint([sourceNode, targetNode], drivenNode, mo=maintainOffset)[0]
                    mc.setAttr('%s.interpType' % (parentCnt), 2)
                    constrainedList.append(parentCnt)
                except:
                    MessageHandling.warning('node not connectable: '+drivenNode)
            if parentConstrainedTranslate:
                try:
                    parentCnt = mc.parentConstraint([sourceNode, targetNode], drivenNode, mo=maintainOffset, skipRotate=['x', 'y', 'z'])[0]
                    mc.setAttr('%s.interpType' % (parentCnt), 2)
                    constrainedList.append(parentCnt)
                except:
                    MessageHandling.warning('node not connectable: '+drivenNode)
            if scaleConstrained:
                for axis in 'xyz':
                    Nodes.removeConnection('%s.s%s'%(drivenNode, axis))
                try:
                    scaleCnt = mc.scaleConstraint([sourceNode, targetNode], drivenNode, mo=maintainOffset)[0]
                    constrainedList.append(scaleCnt)
                except:
                    MessageHandling.warning('node not connectable: '+drivenNode)
            if positionConstrained:
                sourceCon = mc.group(name=Nodes.replaceNodeType(sourceNode)+'_'+Nodes.replaceNodeType(drivenNode, 'con'), empty=True)
                Nodes.alignObject(sourceCon, drivenNode)
                mc.parentConstraint(sourceNode, sourceCon, mo=True)
                conNodes.append(sourceCon)
                sourceNode = sourceCon
                targetCon = mc.group(name=Nodes.replaceNodeType(targetNode)+'_'+Nodes.replaceNodeType(drivenNode, 'con'), empty=True)
                Nodes.alignObject(targetCon, drivenNode)
                mc.parentConstraint(targetNode, targetCon, mo=True)
                conNodes.append(targetCon)
                targetNode = targetCon
                try:
                    posCnt = mc.pointConstraint([sourceNode, targetNode], drivenNode, mo=False)[0]
                    constrainedList.append(posCnt)
                except:
                    MessageHandling.warning('node not connectable: '+drivenNode)
                if rigGroup != None:
                    mc.parent(sourceCon, rigGroup)
                    mc.parent(targetCon, rigGroup)
            if pointConstrained:
                try:
                    pointCnt = mc.pointConstraint([sourceNode, targetNode], drivenNode, mo=maintainOffset)[0]
                    constrainedList.append(pointCnt)
                except:
                    MessageHandling.warning('node not connectable: '+drivenNode)
            if orientConstrained:
                try:
                    orientCnt = mc.orientConstraint([sourceNode, targetNode], drivenNode, mo=maintainOffset)[0]
                    mc.setAttr('%s.interpType' % (orientCnt), 2)
                    constrainedList.append(orientCnt)
                except:
                    MessageHandling.warning('node not connectable: '+drivenNode)

            if createHermiteBlending:

                if attrTitle != None:
                    Nodes.addAttrTitle(attrNode, attrTitle)
                
                for constrained in constrainedList:
                    
                    weight1Attr = constrained + '.' + sourceNode + 'W0'
                    weight2Attr = constrained + '.' + targetNode + 'W1'

                    attrList = [['rootWeight', 0.0], 
                                ['midWeight', 0.5], 
                                ['midPosition', 0.5], 
                                ['tipWeight', 1.0]]

                    for attr in attrList:
                        uniqueAttrName = createUniqueName(attr[0], attrName)
                        if not mc.objExists(attrNode+'.'+uniqueAttrName):
                            mc.addAttr(attrNode, at='float', ln=uniqueAttrName, dv=attr[1], 
                                        k=True,
                                        hasMinValue=True,
                                        minValue=0.01 if attr[0] == 'midPosition' else 0,
                                        hasMaxValue=True if attr[0] == 'midPosition' else False,
                                        maxValue=0.99 if attr[0] == 'midPosition' else 1)

                    rootWeight = '%s.%sRootWeight' % (attrNode, attrName)
                    midWeight = '%s.%sMidWeight' % (attrNode, attrName)
                    midPosition = '%s.%sMidPosition' % (attrNode, attrName)
                    tipWeight = '%s.%sTipWeight' % (attrNode, attrName)
                    rootBlending = 0
                    midBlending = 0
                    tipBlending = 0

                    blendExpr = '$chainCount = %s;\n' % (float(len(targetNodeList))) \
                                + '$midPosition = %s;\n' % (midPosition) \
                                + '$hAchainCount = ($chainCount-1)*$midPosition+1;\n' \
                                + '$hBchainCount = ($chainCount-1)*(1.0-$midPosition)+1;\n' \
                                + '$c = (1.0/($chainCount-1))*%s;\n' % (float(t)) \
                                + '$hAc = $c/$midPosition;\n' \
                                + '$hBc = ($c-$midPosition)*(1.0/(1-$midPosition));\n' \
                                + '$pA0 = %s;\n' % (rootWeight) \
                                + '$pA1 = %s;\n' % (midWeight) \
                                + '$tA0 = %s;\n' % (rootBlending) \
                                + '$tA1 = %s;\n' % (midBlending) \
                                + '$pB0 = %s;\n' % (midWeight) \
                                + '$pB1 = %s;\n' % (tipWeight) \
                                + '$tB0 = %s;\n' % (midBlending) \
                                + '$tB1 = %s;\n' % (tipBlending) \
                                + '$hA = `hermite $pA0 $pA1 $tA0 $tA1 $hAc`;\n' \
                                + '$hB = `hermite $pB0 $pB1 $tB0 $tB1 $hBc`;\n' \
                                + '$h = 0.0;\n' \
                                + 'if ($c <= $midPosition) {$h = $hA;}\n' \
                                + 'if ($c > $midPosition) {$h = $hB;}\n' \
                                + '%s = $h' % weight1Attr
                    
                    blendName = weight1Attr.replace('.', '_')
                    blendExprName = blendName + '_' + Settings.expressionSuffix
                    mc.expression(weight1Attr, string=blendExpr, name=blendExprName, alwaysEvaluate=0)
                    #
                    addNegNode = Nodes.addNode(input1=weight1Attr, 
                                                input2=-1, 
                                                output=None, 
                                                sourceNode=rigGroup)

                    Nodes.mulNode(input1='%s.output'%addNegNode, 
                                    input2=-1, 
                                    output=weight2Attr, 
                                    sourceNode=rigGroup)
            
            elif attrKeys and drivenKeys0 and drivenKeys1:
                sourceAttr = createAttr(attr, attrNode, attrName, drivenNode)
                for constrained in constrainedList:
                    for n, attrKey in enumerate(attrKeys):
                        mc.setDrivenKeyframe(f'{constrained}.{sourceNode}W0',
                                            cd=sourceAttr, 
                                            dv=attrKey, 
                                            v=drivenKeys0[n], 
                                            itt='flat', 
                                            ott='flat')
                        mc.setDrivenKeyframe(f'{constrained}.{targetNode}W1',
                                            cd=sourceAttr, 
                                            dv=attrKey, 
                                            v=drivenKeys1[n], 
                                            itt='flat', 
                                            ott='flat')

            else:

                sourceAttr = createAttr(attr, attrNode, attrName, drivenNode)

                for constrained in constrainedList:
                    Nodes.negateConnect(sourceAttr,
                                        constrained + '.' + sourceNode + 'W0',
                                        sourceNode=sourceNode)
                    mc.connectAttr(sourceAttr, constrained + '.' + targetNode + 'W1')
    
    return conNodes, constrainedList

def attachBlend(selList, geoNode, attrName='value', addAttrTo=None, parentLevel=2, constrainedLevel=1):

    def addAttr(attrTarget, attrName=attrName):
        mc.addAttr(attrTarget, at='float', ln=attrName, dv=0.0, keyable=True, hasMaxValue=True, maxValue=1.0,
                   hasMinValue=True, minValue=0.0)

    addAttr(addAttrTo, attrName)

    def getParentNode(node, level):
        for n in range(level):
            node = mc.pickWalk(node, d='up')[0]
        return node

    for sel in selList:

        cntNode = getParentNode(sel, constrainedLevel)
        parentNode = getParentNode(sel, parentLevel)
        attachNode = parentToClosestVertex([cntNode], geoNode, parentType=None)[0]

        parentCnt = mc.parentConstraint([parentNode, attachNode], cntNode, mo=True)[0]
        mc.setAttr('%s.interpType' % (parentCnt), 2)

        sourceAttr = addAttrTo + '.' + attrName

        for n, node in enumerate([parentNode, attachNode]):
            for v in [n, 1-n]:
                mc.setDrivenKeyframe(parentCnt + '.' + node + 'W' + str(n), cd=sourceAttr, dv=v, v=1 if v == n else 0, itt='linear', ott='linear')

def createTransformLimits(controlNode, trs='tr', axis='xyz', negDir=True, posDir=True, dv=100):

    Nodes.addAttrTitle(controlNode, 'transformLimits')
    
    enabled = (negDir, posDir)
    if 't' in trs:
        if 'x' in axis:
            mc.transformLimits(controlNode, tx=(0, 0), etx=enabled)
        if 'y' in axis:
            mc.transformLimits(controlNode, ty=(0, 0), ety=enabled)
        if 'z' in axis:
            mc.transformLimits(controlNode, tz=(0, 0), etz=enabled)
        for a in axis:
            for direction in ['negative', 'positive']:
                attrName = '%sT%s'%(direction, a)
                sourceAttr = controlNode+'.'+attrName
                targetAttr = '%s.%sTrans%sLimit'%(controlNode, 'min' if direction == 'negative' else 'max', a.upper())
                mc.addAttr(controlNode, ln=attrName, k=False, hasMinValue=True, minValue=0, dv=dv)
                mc.setAttr(sourceAttr, cb=True)
                if direction == 'negative':
                    Nodes.mulNode(input1=sourceAttr, 
                                    input2=-1,
                                    output=targetAttr,
                                    specific=trs+a)
                if direction == 'positive':
                    mc.connectAttr(sourceAttr, targetAttr)
    
    if 'r' in trs:
        if 'x' in axis:
            mc.transformLimits(controlNode, rx=(0, 0), erx=enabled)
        if 'y' in axis:
            mc.transformLimits(controlNode, ry=(0, 0), ery=enabled)
        if 'z' in axis:
            mc.transformLimits(controlNode, rz=(0, 0), erz=enabled)
        for a in axis:
            for direction in ['negative', 'positive']:
                attrName = '%sR%s'%(direction, a)
                sourceAttr = controlNode+'.'+attrName
                targetAttr = '%s.%sRot%sLimit'%(controlNode, 'min' if direction == 'negative' else 'max', a.upper())
                mc.addAttr(controlNode, ln=attrName, k=False, hasMinValue=True, minValue=0, dv=dv)
                mc.setAttr(sourceAttr, cb=True)
                if direction == 'negative':
                    Nodes.mulNode(input1=sourceAttr, 
                                    input2=-1,
                                    output=targetAttr,
                                    specific=trs+a)
                if direction == 'positive':
                    mc.connectAttr(sourceAttr, targetAttr)
    
    if 's' in trs:
        if 'x' in axis:
            mc.transformLimits(controlNode, sx=(0, 0), esx=enabled)
        if 'y' in axis:
            mc.transformLimits(controlNode, sy=(0, 0), esy=enabled)
        if 'z' in axis:
            mc.transformLimits(controlNode, sz=(0, 0), esz=enabled)
        for a in axis:
            for direction in ['negative', 'positive']:
                attrName = '%sS%s'%(direction, a)
                sourceAttr = controlNode+'.'+attrName
                targetAttr = '%s.%sScale%sLimit'%(controlNode, 'min' if direction == 'negative' else 'max', a.upper())
                mc.addAttr(controlNode, ln=attrName, k=False, hasMinValue=True, minValue=0, dv=dv)
                mc.setAttr(sourceAttr, cb=True)
                if direction == 'neg':
                    Nodes.mulNode(input1=sourceAttr, 
                                    input2=-1,
                                    output=targetAttr,
                                    specific=trs+a)
                if direction == 'pos':
                    mc.connectAttr(sourceAttr, targetAttr)

def disable_deformer_envelopes(obj, deformer_type):

    # Get all deformers of the specified type connected to the object
    deformers = mc.ls(mc.listHistory(obj), type=deformer_type)
    if not deformers:
        return []

    for deformer in deformers:
        envelope = f'{deformer}.envelope'
        if mc.objExists(envelope):
            mc.setAttr(envelope, 0)
            print(f'Deformer disabled: {deformer}')
    
    return deformers

def createCorrectiveBlendshape(sourceNode, targetNode, name):

    all_deformers = list()
    for node in [sourceNode, targetNode]:
        for deformer_type in ['deltaMush', 'tension']:
            deformers = disable_deformer_envelopes(node, deformer_type)
            all_deformers.extend(deformers)
        
    if not mc.pluginInfo('invertShape', q=True, loaded=True):
        mc.loadPlugin('invertShape')

    correctiveNode = mc.rename(mc.invertShape(sourceNode, targetNode), name)

    for deformer in all_deformers:
        mc.setAttr(f'{deformer}.envelope', 1)
        print(f'Deformer enabled: {deformer}')

    return correctiveNode

def connectSquashStretchAttributes(curveNode, controlNode):

    Nodes.addAttrTitle(controlNode, 'squashStretch', 'Squash & Stretch ')

    for attr in [['scalePowerStart', 0.0], ['tangentStart', 0.3], ['scalePowerMid', 0.5], ['tangentMid', 0.3],
                 ['tangentEnd', 0.3], ['scalePowerEnd', 0.0]]:
        mc.addAttr(controlNode, ln=attr[0], at='float', k=True, hasMinValue=True, minValue=0, dv=attr[1])
        mc.connectAttr('%s.%s' % (controlNode, attr[0]), '%s.%s' % (curveNode, attr[0]))

def createSkinWeightTemplate(geoList):

    templateGroup = mc.group(name='SkinWeightTemplate', empty=True)

    for geo in geoList:
        geoGroup = mc.group(name='%s_grp' % geo, empty=True)
        mc.parent(geoGroup, templateGroup)
        geoDup = mc.duplicate(geo)[0]
        srcSkinJointList = mc.skinCluster(Nodes.getSkinCluster(geo)[0], inf=True, q=True)
        skinJointList = []
        for srcSkinJoint in srcSkinJointList:
            mc.select(clear=True)
            skinJoint = mc.joint(name=Nodes.replaceNodeType(geo + '_' + srcSkinJoint, 'sknSrc'))
            mc.parent(skinJoint, geoGroup)
            Nodes.alignObject(skinJoint, srcSkinJoint)
            skinJointList.append(skinJoint)
        mc.skinCluster(skinJointList, geoDup, toSelectedBones=True)[0]
        mc.select([geo, geoDup])
        mc.copySkinWeights(ia='closestJoint', sa='closestPoint', sm=True, nm=True)
        mc.select(clear=True)
        mc.parent(geoDup, geoGroup)
        mc.rename(geoDup, geoDup[:-1] + '_src')

def transferSkinWeightTemplate():

    geoGroupList = mc.listRelatives('SkinWeightTemplate', children=True)

    for geoGroup in geoGroupList:

        sknSrcList = []
        for childNode in mc.listRelatives(geoGroup, children=True):
            shapeList = mc.listRelatives(childNode, shapes=True)
            if shapeList != None:
                if mc.objectType(shapeList[0]) == 'mesh':
                    geoNode = childNode
            else:
                if mc.objectType(childNode) == 'joint':
                    sknSrcList.append(childNode)

        trgSkinJointList = []
        for sknSrc in sknSrcList:
            trgSkinJoint = Nodes.replaceNodeType(sknSrc, Settings.skinJointSuffix)[len(geoGroup)-3:]
            Nodes.alignObject(sknSrc, trgSkinJoint)
            trgSkinJointList.append(trgSkinJoint)

        trgGeoNode = geoNode[:-4]
        if Nodes.getSkinCluster(trgGeoNode)[0] == None:
            mc.skinCluster(trgSkinJointList, trgGeoNode, toSelectedBones=True)[0]
        mc.select([geoNode, trgGeoNode])
        mc.copySkinWeights(ia='closestJoint', sa='closestPoint', sm=True, nm=True)

def getReferencePrefix():
    
    ref = mc.listReferences(refNodes=True)
    if ref != []:
        return ref [0][0][:-2]+':'
    else:
        return None

def getNodeByName(nodeName, getRef=True, prefix=''):

    if nodeName == None:
        return
    nodeList = [x for x in mc.ls(prefix+':'+nodeName) if mc.referenceQuery(x, isNodeReferenced=True) == getRef]
    if nodeList == []:
        return None
    return nodeList[0]

def alignSkinJoints(rigRoot='rig'):

    trgRigRoot= getNodeByName(rigRoot, getRef=False)

    for trgNode in Nodes.getAllChildren(trgRigRoot):
        
        node = trgNode.split('|')[-1]
        
        sourceNode = getNodeByName(getReferencePrefix()+node)
        
        if sourceNode != None:

            attrList = mc.listAttr(trgNode, userDefined=True)
            for trs in 'tr':
                for axis in 'xyz':
                    if mc.objExists(sourceNode):
                        Nodes.alignObject(sourceNode, node)
                    else:
                        MessageHandling.warning('Object %s not found in rig' % sourceNode)
        else:
            MessageHandling.warning('%s not found on ref rig.' % node)

def getCvCount(curveNode):

    return len(mc.getAttr('%s.cv[*]'%curveNode))

def refreshEvaluationMode(modeType='parallel'):

    mc.evaluationManager(mode='off')
    mc.evaluationManager(mode=modeType)
    mc.evaluationManager(invalidate=True)

def assignSidePrefix(name, side):

    if len(name.split('_')[0]) == 1:
        side = None
    pfx = side+'_' if side != None else ''

    return pfx+name

def createSurfaceConstraintNode(locNode=None, surfNode=None, indices=None, uPos=0, vPos=0, orientAlignment='v', borderAlign=False, nodeType=Settings.locNodeSuffix):

    if locNode != None:
        closestPointNode = Nodes.utilityNode(nodeType='closestPointOnSurface', indices=indices, sourceNode=surfNode)
        decompNode = Nodes.utilityNode(nodeType='decomposeMatrix', indices=indices, sourceNode=surfNode)
    else:
        closestPointNode = None
    pointOnSurfaceNode = Nodes.utilityNode(nodeType='pointOnSurfaceInfo', indices=indices, sourceNode=surfNode)
    fourByFourNode = Nodes.utilityNode(nodeType='fourByFourMatrix', indices=indices, sourceNode=surfNode)
    decompResultNode = Nodes.utilityNode(nodeType='decomposeMatrix', indices=indices, specific='result', sourceNode=surfNode)
    constraintNode = AddNode.emptyNode(locNode if locNode else surfNode, nodeType=nodeType, indices=indices, objType='locator', size=Nodes.getSize(surfNode)[0]*0.05)
    
    if locNode == None:
        mc.setAttr('%s.parameterU'%pointOnSurfaceNode, uPos)
        mc.setAttr('%s.parameterV'%pointOnSurfaceNode, vPos)

    uConnectValue = '1' if orientAlignment == 'u' else '2'
    vConnectValue = '2' if orientAlignment == 'u' else '1'

    if borderAlign:
        if uPos == 0 or uPos == 1:
            uConnectValue = '2'
            vConnectValue = '1'

    if locNode != None:
        mc.connectAttr('%s.worldMatrix'%locNode, '%s.inputMatrix'%decompNode)
        mc.connectAttr('%s.outputTranslate'%decompNode, '%s.inPosition'%closestPointNode)
        mc.connectAttr('%s.worldSpace'%surfNode, '%s.inputSurface'%closestPointNode)
        mc.connectAttr('%s.result.parameterU'%closestPointNode, '%s.parameterU'%pointOnSurfaceNode)
        mc.connectAttr('%s.result.parameterV'%closestPointNode, '%s.parameterV'%pointOnSurfaceNode)
    mc.connectAttr('%s.worldSpace'%surfNode, '%s.inputSurface'%pointOnSurfaceNode)
    mc.connectAttr('%s.normalizedNormalX'%pointOnSurfaceNode, '%s.in00'%fourByFourNode)
    mc.connectAttr('%s.normalizedNormalY'%pointOnSurfaceNode, '%s.in01'%fourByFourNode)
    mc.connectAttr('%s.normalizedNormalZ'%pointOnSurfaceNode, '%s.in02'%fourByFourNode)
    mc.connectAttr('%s.normalizedTangentUX'%pointOnSurfaceNode, '%s.in%s0'%(fourByFourNode, uConnectValue))
    mc.connectAttr('%s.normalizedTangentUY'%pointOnSurfaceNode, '%s.in%s1'%(fourByFourNode, uConnectValue))
    mc.connectAttr('%s.normalizedTangentUZ'%pointOnSurfaceNode, '%s.in%s2'%(fourByFourNode, uConnectValue))
    mc.connectAttr('%s.normalizedTangentVX'%pointOnSurfaceNode, '%s.in%s0'%(fourByFourNode, vConnectValue))
    mc.connectAttr('%s.normalizedTangentVY'%pointOnSurfaceNode, '%s.in%s1'%(fourByFourNode, vConnectValue))
    mc.connectAttr('%s.normalizedTangentVZ'%pointOnSurfaceNode, '%s.in%s2'%(fourByFourNode, vConnectValue))
    mc.connectAttr('%s.positionX'%pointOnSurfaceNode, '%s.in30'%fourByFourNode)
    mc.connectAttr('%s.positionY'%pointOnSurfaceNode, '%s.in31'%fourByFourNode)
    mc.connectAttr('%s.positionZ'%pointOnSurfaceNode, '%s.in32'%fourByFourNode)
    mc.connectAttr('%s.output'%fourByFourNode, '%s.inputMatrix'%decompResultNode)
    mc.connectAttr('%s.outputTranslate'%decompResultNode, '%s.translate'%constraintNode)
    mc.connectAttr('%s.outputRotate'%decompResultNode, '%s.rotate'%constraintNode)

    mc.setAttr('%s.inheritsTransform'%constraintNode, False)

    return {'constraintNode': constraintNode,
            'uPos': mc.getAttr('%s.parameterU'%pointOnSurfaceNode),
            'vPos': mc.getAttr('%s.parameterV'%pointOnSurfaceNode),
            'closestPointNode': closestPointNode}

def createSurfaceConstraintConnection(ctlNodes, 
                                        surfNode, 
                                        attrNode=None, 
                                        attrName='surfaceConstraint',
                                        defaultValue=1,
                                        lockScale=False,
                                        zNegate=True, 
                                        side=None,
                                        parentToSclCmp=True):

    attrTitle = 'constraint'
    constraintNodeList = list()
    inbNodeList = list()
    resultNodeList = list()
    mirrorScale = [-1, -1, -1] if side == Settings.rightSide else [1, 1, 1]
    
    for ctlNode in ctlNodes:
        
        if parentToSclCmp:
            sclCmpNode = Nodes.replaceNodeType(ctlNode, Settings.scaleCompensateNode)
            inbParent = ctlNode if not mc.objExists(sclCmpNode) else sclCmpNode
        else:
            inbParent = ctlNode
        inbNode = AddNode.inbetweenNode(inbParent, nodeType='surfaceConstraint', lockScale=lockScale)
        inbNodeList.append(inbNode)

        # for curve rigs, we need to parent the cluster node to the surfaceConstraint node
        clsNode = Nodes.replaceNodeType(ctlNode, Settings.clusterHandleSuffix)
        if mc.objExists(clsNode):
            Nodes.setParent(clsNode, inbNode)

        constraintNode = createSurfaceConstraintNode(ctlNode, surfNode)['constraintNode']
        for a, axis in enumerate('xyz'):
            mc.setAttr('%s.s%s'%(constraintNode, axis), mirrorScale[a])
        constraintNodeList.append(constraintNode)
        
        rotationNode = AddNode.childNode(constraintNode, nodeType='rotationConnect', lockScale=True)
        Nodes.alignObject(rotationNode, ctlNode)
        AddNode.parentNode(rotationNode, nodeType='rotationOff', lockScale=True)
        [mc.connectAttr('%s.rotate%s'%(ctlNode, axis), '%s.rotate%s'%(rotationNode, axis)) for axis in 'XYZ']

        blendBetween([inbParent], [rotationNode], [inbNode], 
                     attrNode=ctlNode, 
                     attrName=attrName, 
                     attrTitle=attrTitle, 
                     scaleConstrained=False, 
                     defaultValue=defaultValue,
                     maintainOffset=True)

        if zNegate:

            zNegateNode = AddNode.parentNode(ctlNode, nodeType='zNegate', lockScale=True)

            mulNode = Nodes.mulNode(input1='%s.tz' % ctlNode, 
                                    input2=-1, 
                                    output=None, 
                                    specific='zNegate')

            Nodes.mulNode(input1='%s.output' % mulNode, 
                            input2='%s.%s' % (ctlNode, attrName), 
                            output='%s.tz' % zNegateNode, 
                            specific='zNegateActivate')

    if attrNode != None:

        for ctlNode in [ctlNode for ctlNode in ctlNodes if ctlNode != attrNode]:
            
            mc.setAttr('%s.%s'%(ctlNode, attrName), k=False)
            mc.setAttr('%s.%s'%(ctlNode, attrTitle), channelBox=False) 
            mc.connectAttr('%s.%s'%(attrNode, attrName), '%s.%s'%(ctlNode, attrName))

    return constraintNodeList, resultNodeList, inbNodeList

def toggleDeformers(geoNode, value=0, deformerTypes=['skinCluster', 'blendShape', 'wrap', 'proximityWrap', 'deltaMush']):

    for inputType in deformerTypes:
        inputNodes = Nodes.getInputNodes(geoNode, inputType)[0]
        if inputNodes != []:
            mc.setAttr('%s.envelope'%inputNodes[0], value)

def splitGeo(geoNode, faceCount=None, outputName='head', component='geoSplit', nodeType=Settings.deformNodeSuffix, parentNode=None):

    name = Nodes.createName(component, element=outputName, nodeType=nodeType)

    toggleDeformers(geoNode, 0)
    outputNode = mc.rename(clean_duplicate(geoNode), name[0])
    toggleDeformers(geoNode, 1)

    Nodes.addNamingAttr(outputNode, name[1])
    
    if faceCount:
        for shape in Nodes.getShapes(outputNode):
            mc.delete('%s.f[%s:]'%(shape, faceCount))
    
    # when deleting faces, maya creates an unwanted additional orig shape for an unknown reason, so we remove it
    for shape in Nodes.getShapes(outputNode):
        if shape.endswith('Orig1'):
            mc.delete(shape)
    
    if nodeType == Settings.deformNodeSuffix:
        mc.addAttr(outputNode, at='bool', ln='blendshapeGeo', keyable=False, dv=True)
        mc.setAttr(outputNode+'.'+'blendshapeGeo', lock=True)
    
    Nodes.setParent(outputNode, parentNode)

    return outputNode

def createTwistNode(startNode,
                    endNode,
                    specific=None,
                    upAxis='Z',
                    rotateOrder=1):

    mc.select(clear=True)

    twistNode = AddNode.jointNode(node=startNode, nodeType='twistJoint', specific=specific, parentToNode=False)
    jointEnd = AddNode.jointNode(node=endNode, nodeType='twistJointEnd', specific=specific, parentToNode=False)

    Nodes.alignObject(twistNode, startNode)
    Nodes.alignObject(jointEnd, endNode)

    mc.parent(jointEnd, twistNode)
    mc.parent(twistNode, startNode)

    poleVectorNode = AddNode.emptyNode(node=startNode, nodeType='twistPole', specific=specific, objType='locator')
    Nodes.alignObject(poleVectorNode, endNode)
    mc.parent(poleVectorNode, endNode)
    mc.setAttr('%s.t%s'%(poleVectorNode, upAxis.lower()), 1)

    ikHandleNode = Nodes.ikHandleNode(startJoint=twistNode, endJoint=jointEnd, specific=specific)

    Nodes.alignObject(ikHandleNode, endNode)
    mc.parent(ikHandleNode, endNode)

    Nodes.poleVectorConstraint(poleVectorNode, ikHandleNode)

    AddNode.parentNode(twistNode)
    [mc.setAttr('%s.jointOrient%s'%(twistNode, axis), 0) for axis in 'XYZ']
    mc.setAttr('%s.rotateOrder'%twistNode, rotateOrder)
    mc.setAttr('%s.displayLocalAxis'%twistNode, True)

    return twistNode, ikHandleNode, poleVectorNode

@UndoDec.undo
def setPose(vals=None):

    poseVals = dict()

    for c, ctlNode in enumerate([x for x in mc.ls('*'+'_'+Settings.controlSuffix) if not mc.referenceQuery(x, isNodeReferenced=True)]):
        if mc.objExists('%s.postDeformAlignment'%ctlNode):
            if mc.getAttr('%s.postDeformAlignment'%ctlNode):
                continue
        if vals == None:
            poseVals[ctlNode] = Nodes.setTrs(ctlNode)
        else:
            Nodes.setTrs(ctlNode, trsVal=vals[ctlNode])
    
    return poseVals

@UndoDec.undo
def deleteComponent(compGroup):

    relatedNodes = Nodes.getRelatedNodes(compGroup)
    if relatedNodes:
        mc.delete(relatedNodes)
    mc.delete(compGroup)

def resetJawPose(jawVal=None):

    jawAttr = 'mouth_jaw_jawClosed.rotateX'

    if mc.objExists(jawAttr):
        
        if jawVal == None:
            jawVal = mc.getAttr('mouth_jaw_gdc.mouthClosed')
            if mc.objExists(jawAttr):
                mc.setAttr(jawAttr, 0)
        else:
            if mc.objExists(jawAttr):
                mc.setAttr(jawAttr, jawVal)

    return jawVal

def setBuildAttr(attrList):

    for attr in attrList:
        if attr == 'only':
            attrList = [(False if x != attr else True) for x in attrList]

    return attrList

def animSceneFix():

    selList = mc.ls(sl=True)

    for sel in selList:

        for trs in 't':
            for axis in 'xy':
                attr = '%s.%s%s'%(sel, trs, axis)
                keyFrames = mc.keyframe(attr, q=True)
                for k in keyFrames:
                    keyVal = mc.getAttr(attr, t=k)
                    mc.keyframe(attr, t=(k, k), valueChange=-1*keyVal)
                    
def animSceneFixLipCorner():

    selList = mc.ls(sl=True)

    keyValList = list()

    for sel in selList:

        for trs in 't':
            for axis in 'xy':
                keyValList.append(list())
                attr = '%s.%s%s'%(sel, trs, axis)
                keyFrames = mc.keyframe(attr, q=True)
                for k in keyFrames:
                    keyValList[-1].append([mc.getAttr(attr, t=k), k])
            for a, axis in enumerate('xy'):
                attr = '%s.%s%s'%(sel, trs, 'y' if axis == 'x' else 'x')
                for k, v in enumerate(keyValList[0]):
                    neg = -1 if a == 0 else 1
                    keyVal = keyValList[a][k][0]
                    timeVal = keyValList[a][k][1]
                    mc.keyframe(attr, t=(timeVal, timeVal), valueChange=neg*keyVal)

def animSceneFixSquashStretch():

    selList = mc.ls(sl=True)

    keyValList = list()

    for sel in selList:

        for trs in 't':
            for axis in 'xy':
                keyValList.append(list())
                attr = '%s.%s%s'%(sel, trs, axis)
                keyFrames = mc.keyframe(attr, q=True)
                for k in keyFrames:
                    keyValList[-1].append([mc.getAttr(attr, t=k), k])
            for a, axis in enumerate('xy'):
                attr = '%s.%s%s'%(sel, trs, 'y' if axis == 'x' else 'x')
                for k, v in enumerate(keyValList[0]):
                    neg = -1 if a == 0 else 1
                    keyVal = keyValList[a][k][0]
                    timeVal = keyValList[a][k][1]
                    mc.keyframe(attr, t=(timeVal, timeVal), valueChange=neg*keyVal)
        for trs in 't':
            for axis in 'xy':
                keyValList.append(list())
                attr = '%s.%s%s'%(sel, trs, axis)
                keyFrames = mc.keyframe(attr, q=True)
                for k in keyFrames:
                    keyValList[-1].append([mc.getAttr(attr, t=k), k])
            for a, axis in enumerate('xy'):
                attr = '%s.%s%s'%(sel, trs, 'y' if axis == 'x' else 'x')
                for k, v in enumerate(keyValList[0]):
                    neg = -1 if a == 0 else 1
                    keyVal = keyValList[a][k][0]
                    timeVal = keyValList[a][k][1]
                    mc.keyframe(attr, t=(timeVal, timeVal), valueChange=neg*keyVal)

def setDefaultPose(nodeList=None):

    if nodeList == None:

        nodeList = mc.ls('*Closed', type='transform') + mc.ls('*_opened', type='transform') 
    
    for node in nodeList:

        resetTransforms(node)

def createNiceName(name, splitIndex=0):
            
    glue = ' '
    niceName = ' '.join(''.join(glue + x if x.isupper() else x for x in name).strip(glue).split(glue)[splitIndex:])
    niceName = niceName[0].upper() + niceName[1:]

    return niceName

def createUniqueName(attrName, uniqueName):

    return uniqueName+attrName[0].upper()+attrName[1:]

def blendGuides(guideGroup='guide', refPrefix='Ref:'):

    nodes = [x for x in Nodes.getAllChildren(guideGroup) if not refPrefix in x and not Settings.guideOffSuffix in x]
    sourceNodeList = list()
    targetNodeList = list()
    drivenNodeList = list()
    bshNodeList = list()
    
    blendGroup = mc.group(name='blendGroup', empty=True)

    for node in nodes:
        for trs in 'trs':
            for axis in 'xyz':
                attr = '%s.%s%s'%(node, trs, axis)
                Nodes.removeConnection(attr)
                mc.setAttr(attr, lock=False)
        srcNode = node+'_src'
        trgNode = node+'_trg'
        if not mc.objExists(refPrefix+node):
            continue
        sourceNodeList.append(srcNode)
        targetNodeList.append(trgNode)
        drivenNodeList.append(node)
        
        srcNode = mc.group(name=srcNode, empty=True)
        trgNode = mc.group(name=trgNode, empty=True)
        Nodes.alignObject(srcNode, node, scale=True)
        Nodes.alignObject(trgNode, refPrefix+node, scale=True)
        mc.parent(srcNode, blendGroup)
        mc.parent(trgNode, blendGroup)

        if Nodes.getShapeType(node) == 'nurbsSurface':
            bshNode = mc.blendShape(refPrefix+node, node, name='blendshape', w=(0, 1))[0]
            bshNodeList.append(bshNode)

    blendBetween(sourceNodeList, 
                targetNodeList, 
                drivenNodeList, 
                attrNode=guideGroup, 
                attrName='blend', 
                attrTitle=None,
                parentConstrained=True, 
                scaleConstrained=True, 
                positionConstrained=False, 
                orientConstrained=False, 
                maintainOffset=False, 
                defaultValue=0,
                createDrvObj=False, 
                rigGroup=None,
                attrIsKeyable=True)

    for bshNode in bshNodeList:
        attr = '%s.envelope'%bshNode
        mc.connectAttr('%s.blend'%guideGroup, attr)

def compVisRow(frameSteps=5):

    selection = mc.ls(sl=True)

    for s, sel in enumerate(selection):
        t = s*frameSteps
        mc.currentTime(t)
        attr = sel+'.visibility'
        mc.setAttr(attr, 0)
        mc.setKeyframe(attr)
        mc.currentTime(t+1)
        mc.setAttr(attr, 1)
        mc.setKeyframe(attr)
        
def createDistanceDimension(startNode, endNode, parenting=True, parentType='pointConstraint', locNodeType=Settings.distanceLocSuffix, nodeType=Settings.distanceSuffix, hide=False):

    startLoc = AddNode.emptyNode(node=startNode, specific=Nodes.camelCase(endNode), nodeType=locNodeType, objType='locator')
    endLoc = AddNode.emptyNode(node=endNode, specific=Nodes.camelCase(startNode), nodeType=locNodeType, objType='locator')

    locList = [startLoc, endLoc]
    
    for c, loc in enumerate(locList):
        
        tObjTrs = mc.xform([startNode, endNode][c], q=True, translation=True, ws=True)
        tObjRot = mc.xform([startNode, endNode][c], q=True, rotation=True, ws=True)
        
        mc.xform(loc, translation=tObjTrs, ws=True)
        mc.xform(loc, rotation=tObjRot, ws=True)

    distanceShape = mc.distanceDimension(startLoc, endLoc)
    distanceNode = mc.listRelatives(distanceShape, parent=True)[0]
    distanceName = Nodes.createName(sourceNode=startNode, 
                                    specific=Nodes.camelCase(endNode),
                                    nodeType=nodeType)
    distanceNode = mc.rename(distanceNode, distanceName[0])
    Nodes.addNamingAttr(distanceNode, distanceName[1])

    if parenting:
        if parentType == 'HierarchyOnly':
            mc.parent(startLoc, startNode)
            mc.parent(endLoc, endNode)
            mc.parent(distanceNode, startNode)
        elif parentType == 'ParentConstraint':
            parentScaleConstraint(startNode, startLoc)
            parentScaleConstraint(endNode, endLoc)
            parentScaleConstraint(startNode, distanceNode)
        else:
            mc.parent(startLoc, startNode)
            mc.parent(endLoc, endNode)
            mc.parent(distanceNode, startNode)
            mc.pointConstraint(startNode, startLoc)
            mc.pointConstraint(endNode, endLoc)
            mc.pointConstraint(startNode, distanceNode)

    if hide:
        mc.hide([startLoc, endLoc, distanceNode])

    return startLoc, endLoc, distanceNode

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

def replaceFollicles(oldGeoNode='ace_body_tx001_oldGeo', newGeoNode='skin_geo'):

    for folNode in mc.ls('*_fol'):
        folShape = folNode+'Shape'
        geoNode = mc.listConnections('%s.inputMesh'%folShape)[0]
        orientNode = None
        offNodes = list()
        if geoNode == oldGeoNode:
            parentNode = Nodes.getParent(folNode)
            childNodes = mc.listRelatives(folNode, type='transform')
            for childNode in childNodes:
                Nodes.setParent(childNode, parentNode)
                if 'orientConstraint' in childNode:
                    orientNode = mc.orientConstraint(childNode, targetList=True, q=True)[0]
                    mc.delete(childNode)
                elif 'scaleConstraint' in childNode:
                    mc.delete(childNode)
                else:
                    offNodes.append(childNode)
        mc.delete(folNode)
        folNode = NodeOnVertex.createFollicle(newGeoNode, 
                                                vtxID=getClosestVertex(offNodes[0], newGeoNode)[1],
                                                orientNode=orientNode)[0]
        Nodes.setParent(folNode, parentNode)
        for offNode in offNodes:
            Nodes.setParent(offNode, folNode)

def replaceParentConstraints():

    for parentCnt in mc.ls(type='parentConstraint'):
        if len(mc.parentConstraint(parentCnt, targetList=True, q=True)) == 1:
            parentNode = mc.parentConstraint(parentCnt, targetList=True, q=True)[0]
            node = Nodes.getParent(parentCnt)
            mc.delete(parentCnt)
            Nodes.setParent(node, parentNode)

def displaySwitchAttr(sourceObjList, targetObj, displaySwitchName=None, visType='Geo', shape=True, show=False, defaultValue=True, lock=True):

    if displaySwitchName == None:
        displaySwitchName = 'all'
    else:
        if show:
            displaySwitchName = 'show%s%s' % (displaySwitchName, visType)
        else:
            displaySwitchName = '%s%sDisplay' % (displaySwitchName, visType)

    if not mc.attributeQuery(displaySwitchName, node=targetObj, exists=True):
        mc.addAttr(targetObj, at='bool', ln=displaySwitchName, keyable=False if lock else True, dv=defaultValue)
        if lock:
            mc.setAttr(targetObj + '.' + displaySwitchName, channelBox=True)

    for sourceObj in sourceObjList:
        
        if shape:
            nodeList = mc.listRelatives(sourceObj, type='shape')
        else:
            nodeList = [sourceObj]

        for node in nodeList:
            sourceVisAttr = '%s.visibility' % (node)
            targetVisAttr = '%s.%s' % (targetObj, displaySwitchName)
            if not mc.getAttr(sourceVisAttr, lock=True):
                try:
                    mc.connectAttr(targetVisAttr, sourceVisAttr, f=True)
                except:
                    pass

    mc.select(targetObj)

def selectNode(nodeType):
    
    nodes = list()
    guideSelection = list()
    for node in mc.ls(sl=True):
        if Nodes.getNodeType(node) == Settings.rigGroup:
            guideSelection.append(Nodes.replaceNodeType(node, Settings.guideGroup))
        else:
            guideSelection.append(node)
    for node in guideSelection:
        nodeByType = Nodes.replaceNodeType(node, nodeType)
        if mc.objExists(nodeByType):
            nodes.append(nodeByType)
        if Nodes.getNodeType(node) == Settings.guideGroup or node == Settings.guideRoot:
            nodes.extend(Nodes.getAllChildren(node, nodeType))
            nodes.extend([x for x in Nodes.getAllChildren(node, Settings.guidePivotSuffix) if not Nodes.exists(Nodes.replaceNodeType(x, nodeType))])
            nodes.extend([x for x in Nodes.getAllChildren(node, Settings.guidePivotSuffix) if Nodes.getSpecific(x) == 'joint'])
    mc.select(nodes)

def keepOut(geoNode, 
                collisionNode,
                vector=(1, 0, 0),
                component=None,
                side=None,
                nodeType=Settings.keepOutSuffix,
                element=None,
                indices=None,
                specific=None,
                indexFill=2,
                sourceNode=None):
    
    if sourceNode == None:
        sourceNode = collisionNode

    component = Nodes.getComponent(sourceNode)

    keepOutName = Nodes.createName(component, 
                                    side, 
                                    nodeType, 
                                    element, 
                                    indices, 
                                    indexFill=indexFill, 
                                    specific=specific, 
                                    sourceNode=sourceNode)
    muscleKeepOutShapeNode = mc.createNode('cMuscleKeepOut', name=keepOutName[0]+'Shape')
    Nodes.addNamingAttr(muscleKeepOutShapeNode, keepOutName[1])

    muscleKeepOutNode = mc.rename(Nodes.getParent(muscleKeepOutShapeNode), Nodes.replaceNodeType(muscleKeepOutShapeNode, nodeType))
    Nodes.addNamingAttr(muscleKeepOutNode, keepOutName[1])

    dummyNode = AddNode.emptyNode()
    Nodes.alignObject(dummyNode, collisionNode)
    dummyVectorNode = AddNode.emptyNode()
    Nodes.alignObject(dummyVectorNode, dummyNode, rotation=False)
    mc.move(vector[0], vector[1], vector[2], dummyVectorNode, r=True)
    mc.parent(dummyVectorNode, dummyNode)
    Nodes.setTrs(dummyNode)
    relativeVector = [mc.getAttr('%s.t%s'%(dummyVectorNode, axis)) for axis in 'xyz']
    mc.delete(dummyNode)

    mc.setAttr('%s.inDirectionX'%muscleKeepOutNode, relativeVector[0])
    mc.setAttr('%s.inDirectionY'%muscleKeepOutNode, relativeVector[1])
    mc.setAttr('%s.inDirectionZ'%muscleKeepOutNode, relativeVector[2])

    for childNode in Nodes.getChildren(collisionNode):
        Nodes.setParent(childNode, muscleKeepOutNode, zeroValues=True)
    Nodes.alignObject(muscleKeepOutNode, collisionNode)
    Nodes.setParent(muscleKeepOutNode, collisionNode, zeroValues=False)

    keepOutDrivenNode = AddNode.inbetweenNode(muscleKeepOutNode, Settings.keepOutDrivenSuffix, zeroValues=True)
    mc.connectAttr('%s.worldMatrix[0]'%muscleKeepOutNode, '%s.worldMatrixAim'%muscleKeepOutShapeNode)
    mc.connectAttr('%s.outputData.outTranslateLocal'%muscleKeepOutShapeNode, '%s.translate'%keepOutDrivenNode)
    
    muscleObjectName = Nodes.createName(component, 
                                        nodeType=Settings.collisionShapeSuffix, 
                                        specific=Nodes.camelCase(geoNode))
    if mc.objExists(muscleObjectName[0]):
        muscleObjectShapeNode = muscleObjectName[0]
    else:
        muscleObjectShapeNode = mc.createNode('cMuscleObject', name=muscleObjectName[0])
        Nodes.addNamingAttr(muscleObjectShapeNode, muscleObjectName[1])
        muscleObjectNode = Nodes.getParent(muscleObjectShapeNode)
        mc.parent(muscleObjectShapeNode, geoNode, s=True, r=True)
        geoShapeNode = Nodes.getShapes(geoNode)[0]
        mc.connectAttr('%s.worldMatrix[0]'%geoNode, '%s.worldMatrixStart'%muscleObjectShapeNode)
        mc.connectAttr('%s.worldMesh[0]'%geoShapeNode, '%s.meshIn'%muscleObjectShapeNode)
        mc.delete(muscleObjectNode)
    mc.connectAttr('%s.muscleData'%muscleObjectShapeNode, '%s.muscleData[0]'%muscleKeepOutShapeNode)

    return muscleKeepOutNode, muscleObjectShapeNode

def hideNonAnimAttrs():

    '''
    for controlNode in mc.ls('*'+'_'+Settings.controlSuffix, type='transform'):
        userAttrs = mc.listAttr(controlNode, userDefined=True)
        if not userAttrs:
            continue
        for attrName in userAttrs:
            if attrName in ['showPivotControl', 'maintainControlShapeOffset', 'spineStretch', 'neckStretch'] or 'Display' in attrName:
                continue
            if not mc.attributeQuery(attrName, node=controlNode, keyable=True) \
                and mc.getAttr(controlNode+'.'+attrName, cb=True) \
                and not mc.getAttr(controlNode+'.'+attrName, lock=True):
                Nodes.lockAndHideAttributes(controlNode, attrName=attrName)
    '''

def showControlsAnim(bySelection=False, locatorNode='control_appear', axis='z'):

    if bySelection:
        controls = mc.ls(sl=True)
    else:
        controls = mc.ls('*_%s'%Settings.controlSuffix)+mc.ls('*_ikLine_tmp')

    for control in controls:

        controlShape = Nodes.getShapes(control)[0]
        controlVis = '%s.visibility'%controlShape
        Nodes.removeConnection(controlVis)

        if not mc.getAttr(controlVis):
            continue

        expr = 'vector $locatorPosition = `xform -q -ws -t %s`;\n'%locatorNode \
            + 'vector $controlPosition = `xform -q -ws -t %s`;\n'%control \
            + '$controlVis = %s;\n'%controlVis \
            + '$visVal = 0;\n' \
            + 'if ($locatorPosition.%s > $controlPosition.%s) {$visVal = 1;}\n'%(axis, axis) \
            + '%s = $visVal;'%controlVis
        
        Nodes.exprNode(controlVis, expr, alwaysEvaluate=True)

def deleteComponents(compType=Settings.guideRoot, selection=None):

    if selection:
        if Settings.guideRoot in selection:
            selection = Nodes.getChildren(Settings.guideRoot)
        if Settings.rigRoot in selection:
            selection = Nodes.getChildren(Settings.rigRoot)
    else:
        if compType == Settings.guideRoot and Nodes.exists(Settings.guideRoot):
            selection = Nodes.getChildren(Settings.guideRoot)
        if compType == Settings.rigRoot and Nodes.exists(Settings.rigRoot):
            selection = Nodes.getChildren(Settings.rigRoot)

    if not selection:
        return
    for sel in selection:
        if Nodes.getComponentType(sel):
            deleteComponent(sel)
        else:
            MessageHandling.noComponentGroupSelected()
            return
    if Nodes.exists(Settings.guideRoot):
        if not Nodes.getChildren(Settings.guideRoot):
            Nodes.delete(Settings.guideRoot)
    if Nodes.exists(Settings.rigRoot):
        if not Nodes.getChildren(Settings.rigRoot):
            Nodes.delete(Settings.rigRoot)