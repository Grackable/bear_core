# Control

import maya.cmds as mc
import maya.mel as mel

from bear.system import ConnectionHandling
from bear.system import MessageHandling
from bear.system import Guiding
from bear.system import Settings
from bear.utilities import Tools
from bear.utilities import Color
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.components.basic import Shapes

def createControl(node=None,
                  component=None,
                  size=1,
                  sizeMultiplier=1,
                  side=None,
                  element=None,
                  indices=None,
                  specific=None,
                  indexFill=2,
                  color='Default',
                  parentDirection=None,
                  parentNode=None,
                  orientNode=None,
                  parentType='Constraint',
                  inheritScale=True,
                  pivotNode=None,
                  deleteNode=False,
                  alignAxis=None,
                  mirrorAxis=None,
                  mirrorScale=[-1, -1, -1],
                  shape='Circle',
                  offset=[[0, 0, 0], [0, 0, 0], [1, 1, 1]],
                  rotateOrder='xyz',
                  lockAndHide=[[False, False, False], [False, False, False], [False, False, False]],
                  isGuide=False,
                  createShapes=True,
                  useGuideAttr=True,
                  controlNodeType=Settings.controlSuffix,
                  offNodeType=Settings.offNodeSuffix,
                  hasPivot=False,
                  hasRotateOrder=False,
                  isDeformControl=False,
                  secondaryDefaultColor=False,
                  isVisible=True,
                  rigGroup=None,
                  hideVisibility=True,
                  correctedPivot=True,
                  deleteRightGuideNode=False,
                  ignoreMissingGuideControlWarning=True,
                  addControlTag=Settings.createControllerTag,
                  postDeformAlignment=False):
    
    mc.symmetricModelling(symmetry=False)
    mc.softSelect(softSelectEnabled=False)
    
    guideName = Nodes.createName(component, side, Settings.guidePivotSuffix, element, indices, specific, indexFill, node)
    guideNode = guideName[0]
    guideData = None
    
    if not mc.objExists(guideNode) and node:
        guideNode = Nodes.replaceNodeType(node, Settings.guidePivotSuffix)
    
    rightGuideNode = None
    if side == Settings.rightSide and not isGuide:
        leftGuideName = Nodes.createName(component, Settings.leftSide, Settings.guidePivotSuffix, element, indices, specific, indexFill, node)
        leftGuideNode = leftGuideName[0]
        rightGuideName = Nodes.createName(component, Settings.rightSide, Settings.guidePivotSuffix, element, indices, specific, indexFill, node)
        rightGuideNode = rightGuideName[0]
        if mc.objExists(leftGuideNode) and not mc.objExists(rightGuideNode):
            guideNode = leftGuideNode
            if not mc.objExists(rightGuideNode):
                rightGuideNode = Tools.mirrorObject(leftGuideNode)
        if mc.objExists(rightGuideNode) and not mc.objExists(leftGuideNode):
            guideNode = rightGuideNode
            if not mc.objExists(leftGuideNode):
                rightGuideNode = Tools.mirrorObject(rightGuideNode)
    
    if node or mc.objExists(guideNode):

        if useGuideAttr and not isGuide:
            
            guideData = Guiding.getGuideAttr(guideNode if mc.objExists(guideNode) else node)
            
            if guideData:
                guideNode = guideData['pivotGuide']
                offset = guideData['offset']
                shape = guideData['shape']
                color = guideData['color']
                hasPivot = None
                secondaryDefaultColor = None
                lockAndHides = None
                guideParentNode = None
                guideOrientNode = None
                guideParentType = None
                guideInheritScale = True
                guideSpaces = None
                guideSpaceNames = None # spaces are applied in post process Generic.Build().postRig()
                isVisible = None
                if 'hasPivotControl' in guideData:
                    hasPivot = guideData['hasPivotControl']
                if 'secondaryDefaultColor' in guideData:
                    secondaryDefaultColor = guideData['secondaryDefaultColor']
                if 'parentNode' in guideData:
                    guideParentNode = guideData['parentNode']
                if 'orientNode' in guideData:
                    guideOrientNode = guideData['orientNode']
                if 'parentType' in guideData:
                    guideParentType = guideData['parentType']
                if 'inheritScale' in guideData:
                    guideInheritScale = guideData['inheritScale']
                if 'spaceNodes' in guideData:
                    guideSpaces = guideData['spaceNodes']
                    if '' in guideSpaces:
                        guideSpaces = None
                if 'spaceNames' in guideData:
                    guideSpaceNames = guideData['spaceNames'] # spaces are applied in post process Generic.Build().postRig()
                    if '' in guideSpaceNames:
                        guideSpaceNames = None
                if 'isVisible' in guideData:
                    isVisible = guideData['isVisible']
                if 'lockAndHides' in guideData:
                    lockAndHides = guideData['lockAndHides']
                if 'hasTransformLimits' in guideData:
                    hasTransformLimits = guideData['hasTransformLimits']
                if 'hasRotateOrder' in guideData:
                    hasRotateOrder = guideData['hasRotateOrder']

                if guideParentNode:
                    parentNode = guideParentNode
                if guideOrientNode:
                    orientNode = guideOrientNode
                if guideParentType:
                    parentType = guideParentType
                if guideInheritScale:
                    inheritScale = guideInheritScale

                if parentNode == '':
                    parentNode = None
                if orientNode == '':
                    orientNode = None
                if parentType == '':
                    parentType = None

                if guideNode:
                    pivotNode = guideNode

            if rightGuideNode:
                pivotNode = rightGuideNode

    if parentType == None:
        parentType = 'Constraint'
        
    if isDeformControl:
        shape='Circle'
        controlNodeType = Settings.deformNodeSuffix
        offNodeType = Settings.deformOffNodeSuffix
        hasPivot=False
        
    if isGuide:
        controlNodeType = Settings.guideShapeSuffix if controlNodeType == Settings.guideShapeSuffix else Settings.guidePivotSuffix
        offNodeType = Settings.guideOffSuffix

    if type(offset[0]) != list:
        offset = [offset, [0, 0, 0], [1, 1, 1]]

    ctrlName = Nodes.createName(component, side, controlNodeType, element, indices, specific, indexFill, node)
    groupName = Nodes.createName(component, side, offNodeType, element, indices, specific, indexFill, node)
    
    AddNode.replaceTempNode(ctrlName[0])

    if pivotNode == None or not mc.objExists(pivotNode):
        pivotNode = node

    if createShapes:

        ctrlNode, ctrlShape = Shapes.createShape(shape, size, ctrlName[0])
    
        mc.select('%s.cv[*]' % (ctrlShape))

        x = sizeMultiplier
        y = sizeMultiplier
        z = sizeMultiplier
        mc.scale(x, y, z)

        # shape offsets
        
        if mirrorAxis == None:
            xFlip, yFlip, zFlip = [1, 1, 1]
        else:
            if type(mirrorAxis) == list:
                xFlip, yFlip, zFlip = mirrorAxis
            else:
                xFlip = -1 if mirrorAxis == 'X' else 1
                yFlip = -1 if mirrorAxis == 'Y' else 1
                zFlip = -1 if mirrorAxis == 'Z' else 1

        mc.scale(offset[2][0],
                offset[2][1],
                offset[2][2], r=True, ws=True)

        mc.rotate(offset[1][0], 
                offset[1][1],
                offset[1][2], r=True, ws=True)

        mc.move(offset[0][0] * (xFlip if side == Settings.rightSide else 1),
                offset[0][1] * (yFlip if side == Settings.rightSide else 1),
                offset[0][2] * (zFlip if side == Settings.rightSide else 1), r=True, ws=True)

        groupNode = mc.group(name=groupName[0], empty=True)

        mc.makeIdentity(ctrlNode, a=True, t=True, r=True, s=True)

        mc.delete(ctrlNode, ch=True)

    else:
        ctrlNode = mc.group(name=ctrlName[0], empty=True)
        groupNode = mc.group(name=groupName[0], empty=True)

    # naming convention

    Nodes.addNamingAttr(ctrlNode, ctrlName[1])
    Nodes.addNamingAttr(groupNode, ctrlName[1])
        
    # rotate order

    if rotateOrder == 'xyz':
        rotateOrderIndex = 0
    if rotateOrder == 'yzx':
        rotateOrderIndex = 1
    if rotateOrder == 'zxy':
        rotateOrderIndex = 2
    if rotateOrder == 'xzy':
        rotateOrderIndex = 3
    if rotateOrder == 'yxz':
        rotateOrderIndex = 4
    if rotateOrder == 'zyx':
        rotateOrderIndex = 5

    if hasRotateOrder:
        rotateOrderAttr = ctrlNode+'.rotationOrder'
        Nodes.addAttr(rotateOrderAttr, at='enum', enums=['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx'], k=False, d=True)
        mc.connectAttr(rotateOrderAttr, '%s.rotateOrder'%ctrlNode)

    mc.setAttr('%s.%s' % (ctrlNode, 'rotationOrder' if hasRotateOrder else 'rotateOrder'), rotateOrderIndex)

    # pivot control

    if hasPivot and specific:
        MessageHandling.warning('Control cannot have a pivot control because it is flagged specific. It is created without pivot control: '+ctrlNode)

    if hasPivot and not specific:

        pvtControlName = Nodes.createName(component, side, controlNodeType, element, indices, 'pivot', indexFill, node)
        pvtCompensateName = Nodes.createName(component, side, Settings.pivotCompensateSuffix, element, indices, None, indexFill, node)

        AddNode.replaceTempNode(pvtControlName[0])

        pvtNodeList = list()

        for pvtName in [pvtControlName, pvtCompensateName]:
            
            pivotSize = max(offset[2][0], offset[2][1], offset[2][2])*1.5
            pvtNode, pvtShape = Shapes.createShape('Cross', ctrlName=pvtName[0])

            mc.select('%s.cv[*]' % (pvtShape))
            mc.scale(pivotSize, pivotSize, pivotSize)

            pvtNodeList.append(pvtNode)

            if pvtName == pvtCompensateName:
                mc.hide(pvtShape)

            mc.parent(pvtNode, ctrlNode)
            Nodes.alignObject(pvtNode, ctrlNode)
            if pvtName[0] == pvtCompensateName[0]:
                mc.setAttr('%s.template' % pvtShape, True)
                Nodes.lockAndHideAttributes(pvtNode, t=[True, True, True], r=[True, True, True],
                                            s=[True, True, True], v=True)
            else:
                Nodes.lockAndHideAttributes(pvtNode, t=[False, False, False], r=[True, True, True],
                                            s=[True, True, True], v=True)

            mc.setAttr('%s.overrideEnabled' % (pvtShape), True)
            mc.setAttr('%s.overrideColor' % (pvtShape), Color.getColor('Bright Green'))

            Nodes.addNamingAttr(pvtNode, pvtName[1])

        pivotControlNode = pvtNodeList[0]
        pivotCompensateNode = pvtNodeList[1]

        if correctedPivot:
            # use with care since it's not working very well with rotations when animated
            for axis in 'XYZ':
                for trs in ['rotate', 'scale']:
                    mc.connectAttr('%s.translate%s'%(pivotControlNode, axis), '%s.%sPivot%s'%(ctrlNode, trs, axis))

        Nodes.addAttrTitle(ctrlNode, 'pivot')
        Tools.displaySwitchAttr([pivotControlNode], ctrlNode, displaySwitchName='Pivot', visType='Control',
                            show=True, defaultValue=False)

        mc.delete(pivotCompensateNode, ch=True)
        mc.delete(pivotControlNode, ch=True)

    else:

        pivotControlNode = None
        pivotCompensateNode = None
        
    if hasPivot and not specific:
        Nodes.addNamingAttr(pivotControlNode, pvtControlName[1])
        Nodes.addNamingAttr(pivotCompensateNode, pvtCompensateName[1])

    # ctrl placement

    if pivotNode == None:
        posValue = [0, 0, 0]
        rotValue = [0, 0, 0]
    else:
        if mc.objExists(pivotNode):
            posValue = mc.xform(pivotNode, q=True, ws=True, rp=True)
            rotValue = mc.xform(pivotNode, q=True, ws=True, ro=True)
        else:
            posValue = [0, 0, 0]
            rotValue = [0, 0, 0]

    mc.xform(ctrlNode, ws=True, t=posValue)
    mc.xform(ctrlNode, ws=True, ro=rotValue)

    mc.xform(groupNode, ws=True, t=posValue)
    mc.xform(groupNode, ws=True, ro=rotValue)

    # visibility

    if not isVisible:
        shapeList = mc.listRelatives(ctrlNode, s=True)
        for shapeNode in shapeList:
            mc.setAttr('%s.visibility'%shapeNode, False)
            mc.setAttr('%s.visibility'%shapeNode, lock=True)
    
    # parenting

    if rigGroup != None:
        Nodes.setParent(groupNode, rigGroup)
    
    if parentDirection == 'ControlToNode':
        Nodes.setParent(groupNode, node)
    if parentDirection == 'NodeToControl':
        Nodes.setParent(node, ctrlNode)

    if node != None:
        if Nodes.getNodeType(node) == Settings.clusterHandleSuffix:
            for axis in 'xyz':
                mc.setAttr('%s.r%s'%(node, axis), 0)

    if mc.listRelatives(ctrlNode, parent=True) == None:
        Nodes.setParent(ctrlNode, groupNode)
    
    # advanced constraining
    
    ConnectionHandling.parentConnection(ctrlNode, groupNode, rigGroup, parentNode, orientNode, parentType, inheritScale)

    # shape color

    Color.setColor(ctrlNode, color, side, secondaryDefaultColor)
    
    if deleteNode:
        if node != None:
            mc.delete(node)

    if hideVisibility:
        Nodes.lockAndHideAttributes(ctrlNode, v=True)
        
    # mirror scale
    if mirrorScale != None and not isGuide and side != None:

        mirSclNode = AddNode.inbetweenNode(groupNode, nodeType=Settings.mirrorScaleSuffix)
        sclCmpNode = AddNode.childNode(pivotControlNode if hasPivot else ctrlNode, nodeType=Settings.scaleCompensateNode)

        for childNode in Nodes.getChildren(pivotControlNode if hasPivot else ctrlNode):
            if childNode != sclCmpNode:
                Nodes.setParent(childNode, sclCmpNode)
        
        if side == Settings.rightSide:
            for sclNode in [mirSclNode, sclCmpNode]:
                for a, axis in enumerate('xyz'):
                    attr = '%s.s%s'%(sclNode, axis)
                    mc.setAttr(attr, lock=False)
                    mc.setAttr(attr, mirrorScale[a])
                    mc.setAttr(attr, lock=True)

        for sclNode in [mirSclNode, sclCmpNode]:
            Nodes.lockAndHideAttributes(sclNode, t=[True, True, True], r=[True, True, True], s=[True, True, True], lock=True, keyable=True)

        if hasPivot and correctedPivot:
            mc.parent(sclCmpNode, pivotCompensateNode)

    elif mirrorScale != None and isGuide and side != None:

        mirSclNode = groupNode
        sclCmpNode = None
        
        if side == Settings.rightSide:
            for sclNode in [mirSclNode]:
                for a, axis in enumerate('xyz'):
                    mc.setAttr('%s.s%s'%(sclNode, axis), mirrorScale[a])

        for sclNode in [mirSclNode]:
            Nodes.lockAndHideAttributes(sclNode, t=[True, True, True], r=[True, True, True], s=[True, True, True], lock=True, keyable=True)
    else:
        mirSclNode = None
        sclCmpNode = ctrlNode

    # guide offsets from align axis (used in createGuide methods), only effects for guide control
    rotateX = 0
    rotateY = 0
    rotateZ = 0

    if alignAxis == 'X':
        rotateZ = 90
    if alignAxis == 'Z':
        rotateX = 90

    if alignAxis == '-X':
        rotateZ = -90
    if alignAxis == '-Z':
        rotateX = -90
    if isGuide:
        mc.rotate(rotateX, rotateY, rotateZ, ctrlNode, r=True, os=True)
    if rightGuideNode and deleteRightGuideNode:
        if mc.objExists(rightGuideNode):
            mc.delete(rightGuideNode)

    if not guideData and useGuideAttr and not isGuide and not ignoreMissingGuideControlWarning:
        MessageHandling.warning('Missing guide control: '+guideNode)
        mc.addAttr(ctrlNode, ln='missingGuideControl', at='bool', dv=True, k=False)
        mc.setAttr('%s.missingGuideControl'%ctrlNode, lock=True)

    mc.setAttr('%s.selectionChildHighlighting'%ctrlNode, False)

    if not isGuide:
        mc.addAttr(ctrlNode, at='bool', ln='postDeformAlignment', k=False, dv=postDeformAlignment)

    Nodes.lockAndHideAttributes(ctrlNode, t=lockAndHide[0], r=lockAndHide[1], s=lockAndHide[2])

    # lock and hide from guide
    if guideData:
        if lockAndHides:
            Nodes.lockAndHideAttributes(ctrlNode, t=[lockAndHides[0], lockAndHides[1], lockAndHides[2]],
                                                    r=[lockAndHides[3], lockAndHides[4], lockAndHides[5]],
                                                    s=[lockAndHides[6], lockAndHides[7], lockAndHides[8]])
        if hasTransformLimits:
            Tools.createTransformLimits(ctrlNode)

    if addControlTag:
        mc.select(ctrlNode)
        mel.eval("TagAsController {};".format(ctrlNode))
        mc.select(clear=True)
    
    return {'control': ctrlNode,
            'offset': groupNode,
            'pivotControl': pivotControlNode,
            'pivotCompensate': ctrlNode if pivotCompensateNode == None else pivotCompensateNode,
            'mirrorScale': groupNode if mirSclNode == None else mirSclNode,
            'scaleCompensate': ctrlNode if sclCmpNode == None else sclCmpNode}