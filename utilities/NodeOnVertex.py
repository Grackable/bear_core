# NodeOnVertex

# NOTE the methods below proximity pin are outdated since we use the new proximity pin
# We keep the other methods though since proximity pin may have some issues

import maya.cmds as mc
import maya.mel as mel
import maya.api.OpenMaya as om

from bear.system import Settings
from bear.utilities import Nodes
from bear.utilities import AddNode

def proximityPin(geoNode,
                pinNodes,
                component=None,
                side=None,
                nodeType=Settings.proximityPinSuffix,
                element=None,
                indices=None,
                specific=None,
                indexFill=2,
                sourceNode=None,
                createPinLoc=False):

    if not sourceNode:
        sourceNode = pinNodes[0]

    pinName = Nodes.createName(component, side, nodeType, element, indices, indexFill=indexFill, specific=specific, sourceNode=sourceNode)
    proximityPinNode = mc.createNode('proximityPin', name=pinName[0])
    Nodes.addNamingAttr(proximityPinNode, pinName[1])

    # getting the orig and deformed shapes
    Nodes.createOrigShape(geoNode)
    shapeNodes = Nodes.getShapes(geoNode)
    for shapeNode in shapeNodes:
        if shapeNode.endswith('Orig'):
            outMesh = shapeNode
            break
        outMesh = None
    if not outMesh:
        outMesh = Nodes.createOrigShape(geoNode)
        if not outMesh:
            outMesh = shapeNodes[0]
            
    shapeDeformed = [x for x in shapeNodes if not 'Orig' in x][-1]
    
    # connecting the prox pin
    mc.setAttr('%s.imat'%proximityPinNode, s=len(pinNodes))
    mc.setAttr('%s.ostr'%proximityPinNode, 1)
    mc.setAttr('%s.osor'%proximityPinNode, 1)
    mc.setAttr('%s.tng'%proximityPinNode, 1)
    mc.connectAttr('%s.worldMesh[0]'%shapeDeformed, '%s.deformedGeometry'%proximityPinNode)
    mc.connectAttr('%s.outMesh'%outMesh, '%s.originalGeometry'%proximityPinNode)
    mc.setAttr('%s.omat'%proximityPinNode, s=len(pinNodes))

    pinLocs = list()
    for p, pinNode in enumerate(pinNodes):
        if createPinLoc:
            pinLoc = AddNode.emptyNode(pinNode, nodeType=Settings.proximityLocSuffix)
            mc.connectAttr('%s.matrix'%pinLoc, '%s.imat[%s]'%(proximityPinNode, p))
            pinLocs.append(pinLoc)
        else:
            pinNodeMatrix = (om.MMatrix(mc.getAttr("{}.worldMatrix[0]".format(pinNode))))
            mc.setAttr('%s.imat[%s]'%(proximityPinNode, p), pinNodeMatrix, type='matrix')
            pinLocs = None
        mc.connectAttr('%s.outputMatrix[%s]'%(proximityPinNode, p), '%s.offsetParentMatrix'%pinNode)
        for trs in 'tr':
            for axis in 'xyz':
                mc.setAttr('%s.%s%s'%(pinNode, trs, axis), 0)

    [mc.setAttr('%s.inheritsTransform'%pinNode, False) for pinNode in pinNodes]

    return pinLocs, proximityPinNode

def constrainToVertex(index, deleteConstraint=False, addJoint=False, geo='', geoShortName=''):
    
    locName = '_'.join(['body', str(index), 'cnt'])

    uv = mc.polyListComponentConversion('%s.vtx[%s]' % (geo, index), toUV=True)
    
    uvValue = mc.polyEditUV(uv, query=True)
    
    loc = mc.spaceLocator(name=locName)
    
    polyCnt = mc.pointOnPolyConstraint(geo, loc, mo=False)[0]
    
    mc.setAttr('%s.%sU0' % (polyCnt, geoShortName), uvValue[0])
    mc.setAttr('%s.%sV0' % (polyCnt, geoShortName), uvValue[1])
    
    mc.setAttr('%s.quadSplit' % (geo), 0)
    
    if deleteConstraint:
        mc.delete(polyCnt)

    if addJoint:
        jointName = '_'.join(['body', str(index), 'jnt'])
        jointNode = mc.joint(name=jointName)
        Nodes.alignObject(jointNode, loc)

    mc.delete(loc)

    return loc, uvValue

def constrainToFace(sel, index, name, addJoint=False, uvValue=[], vis=False):

    geo = sel.split('.')[0]

    vertexCount = mc.polyEvaluate(geo, vertex=True)

    faceIndex = 0

    for f in range(vertexCount):

        uv = mc.polyListComponentConversion('%s.vtx[%s]' % (geo, f), toUV=True)

        uvCheck = mc.polyEditUV(uv, query=True)

        if uvCheck[0] > 0 and uvCheck[0] < 1 and uvCheck[1] > 0 and uvCheck[1] < 1:
            faceIndex = f
            break

    face = '%s.f[%s]' % (geo, faceIndex)

    mc.select(face)

    folName = '_'.join([name, str(index).zfill(3), 'fol'])

    if mc.objExists(folName):
        return folName, True
    else:
        mel.eval('createHair 1 1 2 0 0 0 0 5 0 1 2 2;')

    hairSysShape = mc.ls(sl=True)[0]
    hairSysNode = mc.listRelatives(hairSysShape, parent=True)[0]
    conNodeList = mc.listConnections(hairSysShape)

    for conNode in conNodeList:
        conShape = mc.listRelatives(conNode, s=True)
        if conShape != None:

            if mc.objectType(conShape) == 'follicle':

                groupName = '_'.join([name, 'grp'])
                groupNode = mc.listRelatives(conNode, parent=True)[0]
                groupNode = mc.rename(groupNode, groupName)

                folNodeList = mc.listRelatives(groupNode, children=True, type='transform')

    for f, folNode in enumerate(folNodeList):

        if mc.objExists(folName):
            return folName, True

        folShape = mc.listRelatives(folNode, s=True)[0]

        # clean up channel box

        for fol in [folShape, folNode]:

            attrList = mc.listAttr(fol, keyable=True)

            for attr in attrList:

                if attr != 'parameterU' and attr != 'parameterV' and attr != 'visibility':
                    try:
                        mc.setAttr('%s.%s' % (fol, attr), keyable=False)
                    except:
                        pass

        mc.setAttr('%s.parameterU' % (folNode), uvValue[0])
        mc.setAttr('%s.parameterV' % (folNode), uvValue[1])

        mc.delete(mc.listRelatives(folNode, children=True, type='transform')[0])

        # naming and grouping

        folNode = mc.rename(folNode, folName)
        mc.select(folNode)

        # add joint

        if addJoint:
            jointName = '_'.join([name, str(index), 'jnt'])
            jointNode = mc.joint(name=jointName)
            Nodes.alignObject(jointNode, folNode)

    # delete redundant nodes

    for conNode in conNodeList:
        if conNode != folNode:
            try:
                if mc.objectType(conNode) != 'time':
                    mc.delete(conNode)
            except:
                pass

    # quad split - important for deformation / triangle flipping

    mc.parent(folNode, world=True)
    mc.delete(groupNode)

    folNode = folNode.split('|')[-1]

    mc.setAttr('%s.quadSplit' % (geo), 0)

    folShape = mc.listRelatives(folNode, shapes=True)[0]
    if not vis:
        mc.setAttr('%s.visibility' % (folShape), False)

    mc.delete(hairSysNode)

    return folNode, False

def createNodeOnVertex(selList=mc.ls(os=True), name='follicles', orient=True):

    folNodeList = []

    for sel in selList:

        selBase = sel.split('|')[-1]

        if selBase.split(':')[0] == selBase:
            firstIndex = selBase.split('[')[1][0:-1]
            lastIndex = firstIndex
        else:
            firstIndex = selBase.split('[')[1].split(':')[0]
            lastIndex = selBase.split('[')[1].split(':')[1][0:-1]

        geo = sel.split('.vtx')[0]

        geoShortName = selBase.split('.vtx')[0]

        for index in range(int(firstIndex), int(lastIndex) + 1):
            vertex = constrainToVertex(index, deleteConstraint=False, addJoint=False, geo=geo,
                                                          geoShortName=geoShortName)
            loc = vertex[0]
            uvValue = vertex[1]

            face, exists = constrainToFace(index, name=geoShortName, addJoint=False, uvValue=uvValue,
                                                      vis=False)

            if exists:
                return [face], mc.listRelatives(face, parent=True)[0], True

            folNode = face

            folNodeList.append(folNode)

            if not orient:
                mc.setAttr('%s.r'%folNode, lock=False, k=True)
                for axis in 'xyz':
                    folRotAttr = '%s.r%s'%(folNode, axis)
                    mc.setAttr(folRotAttr, lock=False, k=True)
                    Nodes.removeConnection('%s.r%s'%(folNode, axis))

    if not exists:
        groupName = '_'.join([name])
        groupNode = mc.group(name=groupName, empty=True)
        mc.parent(folNodeList, groupNode)

    return folNodeList, groupNode, exists

def createNodeByVertexWeight(vertexNode, size=1.0, alignOrientation=True):

    sourceObj = vertexNode.split('.')[0]
    
    if mc.objectType(sourceObj) != 'transform':
        sourceObj = mc.listRelatives(sourceObj, parent=True)[0]
    
    objType = mc.objectType(mc.listRelatives(sourceObj, shapes=True)[0])

    if objType == 'lattice':
        return None

    sourceSkinCluster = Nodes.getSkinCluster(sourceObj)[0]
    if sourceSkinCluster == None:
        return None
    else:
        sourceSkinWeight = mc.skinPercent(sourceSkinCluster, vertexNode, query=True, value=True)
        sourceSkinJoint = mc.skinPercent(sourceSkinCluster, vertexNode, query=True, transform=None)
    
    skinWeightList = []

    for i, weight in enumerate(sourceSkinWeight):
        if weight > 0.01:
            skinWeightList.append([sourceSkinJoint[i], weight])

    baseName = vertexNode.replace('.', '_').replace('[', '_').replace(']', '_')

    locNode = baseName+'_loc'

    if not mc.objExists(locNode):
        locNode = mc.spaceLocator(name=locNode)[0]

    if alignOrientation:
        folNode, exists = createFollicle(sourceObj, vtxID=vertexNode.split('[')[1].split(']')[0])
        Nodes.alignObject(locNode, folNode)
        mc.delete(folNode)
    else: 
        Nodes.alignObject(locNode, vertexNode)

    for axis in 'XYZ':
        mc.setAttr('%s.localScale%s' % (locNode, axis), size)

    for weightSet in skinWeightList:

        parentCnt = mc.parentConstraint(weightSet[0], locNode, weight=weightSet[1], mo=True)[0]
        mc.setAttr('%s.interpType' % (parentCnt), 2)

    return locNode, parentCnt

def createFollicle(surfaceNode, name='follicle', uPos=0.0, vPos=0.0, vtxID=None, orient=True, orientNode=None, parentNode=None):

    clsNodes = mc.cluster(surfaceNode)
    attrNode = '%s.quadSplit'%surfaceNode
    if mc.objExists(attrNode):
        mc.setAttr(attrNode, 0)
    mc.delete(clsNodes)
    
    mc.polyUVSet(surfaceNode, uvSet='map1', currentUVSet=True)

    if vtxID is not None:

        uvSel = mc.polyListComponentConversion('%s.vtx[%s]' % (surfaceNode, str(vtxID)), toUV=True)[0]
        if ':' in uvSel and '.' in uvSel.split(':')[0]:
            uvSel = uvSel.split(':')[0]+']'

        uPos, vPos = mc.polyEditUV(uvSel, q=True)

    if Nodes.getShapeType(surfaceNode) == 'transform':
        surfaceNode = surfaceNode.getShape()
        shapeType = surfaceNode.type()
    elif Nodes.getShapeType(surfaceNode) == 'nurbsSurface':
        shapeType = 'nurbsSurface'
        pass
    elif Nodes.getShapeType(surfaceNode) == 'mesh':
        shapeType = 'mesh'
        pass
    else:
        mc.error('Input node must be a nurbs surface or a mesh.')
        return False

    follicleName = '_'.join([Nodes.replaceNodeType(surfaceNode), name, 'vtxID', str(vtxID), Settings.folNodeSuffix])
    if mc.objExists(follicleName):
        return follicleName, True

    follicleShape = mc.createNode('follicle', name=follicleName+'Shape')
    mc.setAttr('%s.visibility'%follicleShape, False)
    if shapeType == 'nurbsSurface':
        mc.connectAttr('%s.local'%surfaceNode, '%s.inputSurface'%follicleShape)
    else:
        mc.connectAttr('%s.outMesh'%surfaceNode, '%s.inputMesh'%follicleShape)

    mc.connectAttr('%s.worldMatrix[0]'%surfaceNode, '%s.inputWorldMatrix'%follicleShape)
    mc.connectAttr('%s.outRotate'%follicleShape, '%s.rotate'%Nodes.getParent(follicleShape))
    mc.connectAttr('%s.outTranslate'%follicleShape, '%s.translate'%Nodes.getParent(follicleShape))
    mc.setAttr('%s.parameterU'%follicleShape, uPos)
    mc.setAttr('%s.parameterV'%follicleShape, vPos)
    Nodes.lockAndHideAttributes(Nodes.getParent(follicleShape), t=[True, True, True], r=[True, True, True])
    
    follicleNode = mc.listRelatives(follicleShape, parent=True)
    follicleNode = mc.rename(follicleNode, follicleName)

    if parentNode != None:
        mc.parent(follicleNode, parentNode)

    if orientNode != None:
        orient = False
        
    if not orient:
        mc.setAttr('%s.r'%follicleNode, lock=False, k=True)
        for axis in 'xyz':
            folRotAttr = '%s.r%s'%(follicleNode, axis)
            mc.setAttr(folRotAttr, lock=False, k=True)
            Nodes.removeConnection('%s.r%s'%(follicleNode, axis))
    
    if orientNode != None:
        orientCnt = mc.orientConstraint(orientNode, follicleNode, mo=False)
        mc.setAttr('%s.interpType'%orientCnt, 0)

    return follicleNode, False