# Limb

import maya.cmds as mc
import math

from bear.system import Settings
from bear.system import Guiding
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import Color
from bear.utilities import SpaceSwitch
from bear.utilities import VisSwitch
from bear.utilities import Nodes
from bear.utilities import ikFkMatch
from bear.components.basic import Control
from bear.components.basic import Guide
from bear.components.basic import Curve

def upnodeGuideSetup(node1, node2, node3, name, side, guideGroup, prefix='guide'):

    upnodeParent = AddNode.emptyNode(component=name,
                                    side=side,
                                    element='upnode',
                                    nodeType=prefix+'Parent',
                                    parentNode=guideGroup)
    upnodeAim = AddNode.emptyNode(component=name,
                                    side=side,
                                    element='upnode',
                                    nodeType=prefix+'Aim',
                                    parentNode=upnodeParent)

    upnodeAimOff = AddNode.childNode(upnodeAim,
                                         prefix+'AimOff')
    
    pointCnt = mc.pointConstraint([node1, node3], upnodeParent, mo=False)[0]
    Nodes.lockAndHideAttributes(upnodeParent, lock=True)

    Nodes.aimConstraint(node2, 
                    upnodeAim,
                    node1, 
                    aimAxis='z',
                    upAxis='x',
                    upType='object')
    Nodes.lockAndHideAttributes(upnodeAim, t=[True, True, True], r=[True, True, True], s=[True, True, True], lock=True)

    return upnodeAim, upnodeAimOff, pointCnt

def guidePlacer(guideGroup, 
                side=Settings.leftSide,
                sectionNames=['upper', 'lower', 'ankle', 'toes', 'toesTip'],
                limbType='Arm',
                invertKnee=False):
    
    aimAxis = '-x' if side == Settings.rightSide else 'x'
    upAxis = ('z' if side == Settings.rightSide else '-z') if invertKnee else ('-z' if side == Settings.rightSide else 'z')
    
    name = Nodes.getComponent(guideGroup)
    
    sectionGuides = list()
    for n, sectionName in enumerate(sectionNames):
        sectionGuide = Guide.createGuide(component=name,
                                        element=sectionName,
                                        specific='placer',
                                        side=side,
                                        parentNode=guideGroup,
                                        hasGuideShape=False)
        if n < 2:
            Nodes.lockAndHideAttributes(sectionGuide['pivot'], r=[True, True, True], lock=False)
        sectionGuides.append(sectionGuide)

    upnodeAim, upnodeAimOff, pointCnt = upnodeGuideSetup(sectionGuides[0]['pivot'], 
                                                sectionGuides[1]['pivot'], 
                                                sectionGuides[2]['pivot'], 
                                                name, 
                                                side, 
                                                guideGroup)
    upnodeGuideNode = Guide.createGuide(component=name,
                                        element='upnode',
                                        side=side,
                                        parentNode=upnodeAimOff)
    mc.setAttr(upnodeGuideNode['control']+'.shape', Settings.shapes.index('Sphere'))
    Nodes.setTrs(upnodeGuideNode['control'], 5, t=False, r=False)
    Nodes.lockAndHideAttributes(upnodeGuideNode['pivot'], r=[True, True, True], lock=True)
    Nodes.lockAndHideAttributes(upnodeGuideNode['pivot'], t=[True, True, False], lock=True)

    upperDistanceNode = Tools.createDistanceDimension(sectionGuides[0]['pivot'], 
                                            sectionGuides[1]['pivot'], 
                                            nodeType=Settings.distanceGuideSuffix)[2]
    lowerDistanceNode = Tools.createDistanceDimension(sectionGuides[1]['pivot'], 
                                            sectionGuides[2]['pivot'], 
                                            nodeType=Settings.distanceGuideSuffix)[2]
    mc.connectAttr('%s.distance'%lowerDistanceNode, '%s.%sW0'%(pointCnt, sectionGuides[0]['pivot']))
    mc.connectAttr('%s.distance'%upperDistanceNode, '%s.%sW1'%(pointCnt, sectionGuides[2]['pivot']))

    Nodes.aimConstraint(sectionGuides[1]['pivot'], 
                    sectionGuides[0]['pivot'],
                    sectionGuides[2]['pivot'], 
                    aimAxis=aimAxis,
                    upAxis=upAxis,
                    upType='object')
    Nodes.aimConstraint(sectionGuides[2]['pivot'], 
                    sectionGuides[1]['pivot'],
                    sectionGuides[0]['pivot'], 
                    aimAxis=aimAxis,
                    upAxis=upAxis,
                    upType='object')
    
    addNode = Nodes.addNode('%s.distance'%upperDistanceNode,
                            '%s.distance'%lowerDistanceNode)
    Nodes.mulNode('%s.output'%addNode,
                            0.75,
                            '%s.tz'%upnodeAimOff)
    Nodes.lockAndHideAttributes(upnodeAimOff, t=[True, True, True], r=[True, True, True], s=[True, True, True], lock=True)
    
    # adding limb length ratio display attribute
    divNode = Nodes.divNode('%s.distance'%upperDistanceNode,
                        '%s.distance'%lowerDistanceNode)
    for sectionGuide in sectionGuides[:3]:
        attr = sectionGuide['pivot']+'.limbLengthRatio'
        Nodes.addAttr(attr, k=False, d=True)
        mc.connectAttr('%s.outputX'%divNode, attr)
    
    # end guide setup
    if len(sectionGuides) > 3:
        constraintNode = Nodes.aimConstraint(sectionGuides[3]['pivot'], 
                        sectionGuides[2]['pivot'],
                        aimAxis=aimAxis,
                        upAxis=('z' if side == Settings.rightSide else '-z') if limbType == 'Leg' else ('-y' if side == Settings.rightSide else 'y'),
                        upType='scene')
        twistAttr = sectionGuides[2]['pivot']+'.twist'
        Nodes.addAttr(twistAttr)
        mc.connectAttr(twistAttr, '%s.offsetX'%constraintNode)
        Nodes.lockAndHideAttributes(sectionGuides[2]['pivot'], t=[False, False, False], r=[True, True, True], s=[True, True, True], lock=True)
        if limbType == 'Leg':
            tipConstraintNode = Nodes.aimConstraint(sectionGuides[4]['pivot'], 
                            sectionGuides[3]['pivot'],
                            aimAxis=aimAxis,
                            upAxis='z' if side == Settings.rightSide else '-z',
                            upType='scene')
            twistAttr = sectionGuides[3]['pivot']+'.twist'
            Nodes.addAttr(twistAttr)
            mc.connectAttr(twistAttr, '%s.offsetX'%tipConstraintNode)
            Nodes.lockAndHideAttributes(sectionGuides[4]['pivot'], t=[False, False, False], r=[True, True, True], s=[True, True, True], lock=True)
        Nodes.lockAndHideAttributes(sectionGuides[3]['pivot'], t=[False, False, False], r=[True, True, True], s=[True, True, True], lock=True)

    return sectionGuides

def ikLine(midRigs, sectionName, midControl, ikJoint, ikUpnodeRig, name, side, limbGroup, limbType):

    startNode = midRigs[sectionName]['control'] if midControl else ikJoint
    endNode = ikUpnodeRig['control']

    lineName = Nodes.createName(name, side, Settings.templateSuffix, specific='ikLine', element=sectionName)
    lineNode = mc.curve(name=lineName[0],
                        d=1,
                        p=[(0, 0, 0),
                           (1, 0, 0)],
                        k=[0, 1])
    Nodes.addNamingAttr(lineNode, lineName[1])

    mc.setAttr('%s.overrideEnabled' % lineNode, True)
    mc.setAttr('%s.overrideDisplayType' % lineNode, 2)
    mc.setAttr('%s.overrideColor' % lineNode,
               mc.getAttr('%s.overrideColor' % mc.listRelatives(ikUpnodeRig['control'], shapes=True)[0]))

    mc.setAttr('%s.inheritsTransform' % lineNode, False)

    for i, ikLineNode in enumerate([startNode, endNode]):
        ikLineClsNode = Nodes.clusterNode('%s.cv[%s]' % (lineNode, i), specific=sectionName+['Start', 'End'][i])

        Nodes.pointConstraint(ikLineNode, ikLineClsNode)
        mc.parent(ikLineClsNode, limbGroup)

        VisSwitch.connectVisSwitchGroup([ikLineClsNode], limbGroup, displayAttr='setupDisplay')

    VisSwitch.connectVisSwitchGroup([lineNode], limbGroup, displayAttr='ikLineControlDisplay', visGroup=limbType)

    mc.parent(lineNode, limbGroup)
    mc.connectAttr('%s.visibility' % endNode, '%s.visibility' % lineNode)

    for trs in 'tr':
        for axis in 'xyz':
            mc.setAttr('%s.%s%s' % (lineNode, trs, axis), 0)

def applySmoothIkOffset(midCntNode, smoothIkAttr, smoothIkOffsetAttr, quadrupedAttr=None):

    # this is for maintaining the initial limb pose when smoothIK is activated
    # we use the knee/ankle controls to store the difference and activate the offset
    # when smoothIK is active

    # we need to have this method separated since we need to call it for quadruped in the foot module
    # in order to receive correct offset with quadruped setup completed
    
    midDrvNode = AddNode.inbetweenNode(midCntNode, nodeType=Settings.drivenNodeSuffix)

    dum1 = mc.group(empty=True, world=True)
    dum2 = mc.group(empty=True, world=True)

    mc.setAttr(smoothIkAttr, 0)
    Nodes.alignObject(dum1, midDrvNode)
    mc.setAttr(smoothIkAttr, 1)
    Nodes.alignObject(dum2, midDrvNode)

    mc.parent(dum1, dum2)

    for axis in 'xyz':
        offsetVal = mc.getAttr('%s.t%s' % (dum1, axis))
        midDrvAttr = '%s.t%s' % (midDrvNode, axis)
        expr = '%s = %s*%s*%s*%s' % (midDrvAttr, smoothIkAttr, offsetVal, smoothIkOffsetAttr, quadrupedAttr if quadrupedAttr else 1)
        Nodes.exprNode(midDrvAttr, specific='smoothIkOffset', expr=expr)
    
    mc.delete(dum2)
    mc.setAttr(smoothIkAttr, 0)

def createRig(upperLimbGuide,
                lowerLimbGuide,
                endGuide,
                upnodeGuide,
                midName,
                side,
                limbType,
                name,
                quadrupedGuide=None,
                digitsName=None,
                hasMidDeformJoint=False,
                hasStretch=True,
                midControl=True,
                pinning=True,
                smoothIk=True,
                curved=True,
                bendy=False,
                alignFootIkForward=True,
                squashing=False,
                hasShoulder=True,
                quadruped=False,
                platformPivotGuides=None,
                defaultSpace=None,
                parentNode=None,
                skeletonParent=None):
    
    if quadruped:
        if not mc.pluginInfo('ikSpringSolver', q=True, loaded=True):
            mc.loadPlugin('ikSpringSolver')

    guideGroup = Nodes.createName(name, side, 'guide')[0]

    limbGroup = AddNode.compNode(component=name, 
                                side=side, 
                                nodeType='rig', 
                                parentNode=Settings.rigRoot)
    if not mc.objExists(limbGroup+'.componentType'):
        mc.addAttr(limbGroup, dt='string', ln='componentType')
        mc.setAttr(limbGroup+'.componentType', limbType.capitalize(), type='string', lock=True)
    
    rigNodes = list()
    jointNodes = list()

    upperLimbOffset = Guiding.getGuideAttr(upperLimbGuide)['offset']
    upperLimbShape = Guiding.getGuideAttr(upperLimbGuide)['shape']

    spaceNodes = Guiding.getBuildAttrs(guideGroup, 'spaceNodes')
    if '' in spaceNodes:
        spaceNodes = None
    spaceNames = Guiding.getBuildAttrs(guideGroup, 'spaceNames')
    if '' in spaceNames:
        spaceNames = None
    #reverseSpaces = Guiding.getBuildAttrs(guideGroup, 'reverseSpaces')

    lowerLimbOffset = Guiding.getGuideAttr(lowerLimbGuide)['offset']
    lowerLimbShape = Guiding.getGuideAttr(lowerLimbGuide)['shape']

    endOffset = Guiding.getGuideAttr(endGuide)['offset']
    endShape = Guiding.getGuideAttr(endGuide)['shape']
    hasPivot = Guiding.getGuideAttr(endGuide)['hasPivotControl']

    upperLimbTwistCount = Guiding.getBuildAttrs(guideGroup, 'upperTwistCount')
    lowerLimbTwistCount = Guiding.getBuildAttrs(guideGroup, 'lowerTwistCount')
    if quadruped:
        endLimbTwistCount = Guiding.getBuildAttrs(guideGroup, 'ankleTwistCount')

    ikTargetOffset = Guiding.getGuideAttr(endGuide, attrPrefix='ikTarget')['offset']
    ikTargetShape = Guiding.getGuideAttr(endGuide, attrPrefix='ikTarget')['shape']
    ikTargetColor = Guiding.getGuideAttr(endGuide, attrPrefix='ikTarget')['color']
    ikTargetOvershootSize = Guiding.getGuideAttr(endGuide, specialAttr='ikTargetOvershootSize')
    ikTargetLiftOff = Guiding.getGuideAttr(endGuide, specialAttr='ikTargetLiftoff')

    if not hasShoulder:
        limbParentShape = Guiding.getGuideAttr(endGuide, attrPrefix=limbType+'Parent')['shape']
        limbParentColor = Guiding.getGuideAttr(endGuide, attrPrefix=limbType+'Parent')['color']
        limbParentOffset = Guiding.getGuideAttr(endGuide, specialAttr=limbType+'ParentOffset')
        limbParentSize = Guiding.getGuideAttr(endGuide, specialAttr=limbType+'ParentSize')

    upperLimbJoint = AddNode.jointNode(upperLimbGuide, nodeType=False, parentToNode=False, convertRotToOrient=True)
    lowerLimbJoint = AddNode.jointNode(lowerLimbGuide, nodeType=False, parentNode=upperLimbJoint, parentToNode=False, convertRotToOrient=True)
    endJoint = AddNode.jointNode(endGuide, parentNode=lowerLimbJoint, parentToNode=False, convertRotToOrient=True, nodeType='blend' if quadruped else Settings.skinJointSuffix)

    upperLimbSize = Nodes.getSize(Nodes.replaceNodeType(upperLimbGuide, Settings.guideShapeSuffix))[0]
    lowerLimbSize = Nodes.getSize(Nodes.replaceNodeType(lowerLimbGuide, Settings.guideShapeSuffix))[0]
    endSize = Nodes.getSize(Nodes.replaceNodeType(endGuide, Settings.guideShapeSuffix))[0]

    upperName = Nodes.getElement(upperLimbGuide)
    lowerName = Nodes.getElement(lowerLimbGuide)
    endName = Nodes.getElement(endGuide)
    
    if quadruped:
        quadrupedEndJoint = AddNode.jointNode(quadrupedGuide, parentNode=endJoint, parentToNode=False, convertRotToOrient=True)
    
    # lengths

    upperLimbLength = Tools.getDistance(upperLimbJoint, lowerLimbJoint)
    lowerLimbLength = Tools.getDistance(lowerLimbJoint, endJoint)
    fullLimbLength = upperLimbLength + lowerLimbLength
    if quadruped:
        endLimbLength = Tools.getDistance(endJoint, quadrupedEndJoint)
        quadLimbLength = fullLimbLength + endLimbLength

    # limb attribute node

    limbAttrSize = (endOffset[2][0]+endOffset[2][1]+endOffset[2][2])/3

    limbAttrRig = Control.createControl(component=name,
                                        element='attributes',
                                        size=limbAttrSize * 1.5,
                                        side=side,
                                        shape='Marker',
                                        offset=[[0, 0, 0], [-90, 90, 0], [1, 1, 1]] if limbType == 'arm' else [[0, 0, 0], [90, 0 if quadruped else 90, 0], [1, 1, 1]],
                                        ignoreMissingGuideControlWarning=True)

    controlVisAttr = 'controlVis'
    
    mc.addAttr(limbAttrRig['control'], at='bool', ln=controlVisAttr, dv=1)
    mc.connectAttr('%s.%s' % (limbAttrRig['control'], controlVisAttr),
                   '%s.visibility' % (limbAttrRig['control']))
    Nodes.lockAndHideAttributes(limbAttrRig['control'], t=[True, True, True], r=[True, True, True], s=[True, True, True])
    
    Nodes.addAttrTitle(limbAttrRig['control'], 'ikFk', niceName='IK/FK')
    # NOTE WIP
    #ikFkMatch.instantSwitch(limbAttrRig['control'])

    ikFkBlendAttrName = 'ikFkBlend'
    ikFkBlendAttr = limbAttrRig['control']+'.'+ikFkBlendAttrName
    # important to have default value 1 for further setup
    mc.addAttr(limbAttrRig['control'], at='float', ln=ikFkBlendAttrName, nn='IK/FK Blend', keyable=True,
               hidden=False, hasMinValue=True, minValue=0, hasMaxValue=True, maxValue=1, dv=1)

    ikChain = mc.duplicate(upperLimbJoint, renameChildren=True)
    fkChain = mc.duplicate(upperLimbJoint, renameChildren=True)
    
    if pinning or midControl:
        modChain = mc.duplicate(upperLimbJoint, renameChildren=True)
    else:
        modChain = []
    
    # remove redundant joints
    if limbType == 'arm':
        for chain in [ikChain, fkChain, modChain]:
            if len(chain) > 3:
                redundantNodes = mc.listRelatives(chain[2], children=True, type='joint', allDescendents=True)
                try:
                    mc.delete(redundantNodes)
                except:
                    pass
                if chain == ikChain:
                    ikChain = chain[0:3]
                if chain == fkChain:
                    fkChain = chain[0:3]
                if chain == modChain:
                    modChain = chain[0:3]
                    
    blendChain = [upperLimbJoint, lowerLimbJoint, endJoint]
    if quadruped:
        blendChain.append(quadrupedEndJoint)

    ikChain = Nodes.renameLimbChain(ikChain, 'ik', side, name, upperName, lowerName, endName, digitsName)
    fkChain = Nodes.renameLimbChain(fkChain, 'fk', side, name, upperName, lowerName, endName, digitsName)
    blendChain = Nodes.renameLimbChain(blendChain, 'blend', side, name, upperName, lowerName, endName, digitsName, quadruped)
    modChain = Nodes.renameLimbChain(modChain, 'mod', side, name, upperName, lowerName, endName, digitsName)
    
    rigNodes.extend(ikChain)
    rigNodes.extend(fkChain)
    if upperLimbTwistCount == 0:
        jointNodes.append(blendChain[0])
        Nodes.addJointLabel(blendChain[0], side)
    else:
        rigNodes.append(blendChain[0])
    if lowerLimbTwistCount == 0:
        jointNodes.append(blendChain[1])
        Nodes.addJointLabel(blendChain[1], side)
    else:
        rigNodes.append(blendChain[1])
    if quadruped:
        if endLimbTwistCount == 0:
            jointNodes.append(blendChain[2])
            Nodes.addJointLabel(blendChain[2], side)
        else:
            rigNodes.append(blendChain[2])
    rigNodes.extend(modChain)

    if limbType == 'arm':
        scaleNode = AddNode.parentNode(endJoint, nodeType='manualScale')
        Nodes.addAttrTitle(limbAttrRig['control'], 'hand')
        handScaleAttrName = 'handScale'
        mc.addAttr(limbAttrRig['control'], at='float', ln=handScaleAttrName, keyable=True, dv=1)
        [mc.connectAttr(limbAttrRig['control'] + '.' + handScaleAttrName, '%s.s%s' % (scaleNode, axis)) for axis in 'xyz']
        Nodes.setParent(scaleNode, limbGroup)

    # ik alignment

    dummyPosNode = AddNode.emptyNode(component='dummyPosNode')
    Nodes.alignObject(dummyPosNode, blendChain[3 if quadruped else 2], 
                        rotation=False if limbType == 'leg' and alignFootIkForward else True)
    if not alignFootIkForward:
        mc.rotate(-90, 0, -90, dummyPosNode, r=True, os=True)
    
    if limbType == 'leg':
        if alignFootIkForward:
            for axis in 'xyz':
                mc.setAttr('%s.r%s' % (dummyPosNode, axis), 0)
        else:
            a = mc.xform(endGuide, q=True, translation=True, worldSpace=True)
            b = mc.xform(mc.listRelatives(endGuide, children=True)[0], q=True, translation=True, worldSpace=True)
            x = b[0] - a[0]
            z = b[2] - a[2]

            rotationOffsetY = math.degrees(math.asin(x / z)) if z > 0 else 0
            mc.setAttr('%s.rotateY' % (dummyPosNode), rotationOffsetY)
        if side == Settings.rightSide and alignFootIkForward:
            mc.rotate(0, 180, 180, dummyPosNode, r=True, objectSpace=True)

    if platformPivotGuides and limbType == 'leg' and alignFootIkForward:

        platformOffset = [list(), list(), list()]
        shapePosNode = AddNode.emptyNode(component='shapePosNode')
        parentCnt = mc.parentConstraint([platformPivotGuides[0], platformPivotGuides[1]], shapePosNode, mo=False)[0]
        mc.setAttr('%s.interpType'%parentCnt, 2)
        mc.delete(parentCnt)
        mc.parent(shapePosNode, dummyPosNode)

        xSize = Tools.getDistance(platformPivotGuides[2], platformPivotGuides[3])
        zSize = Tools.getDistance(platformPivotGuides[0], platformPivotGuides[1])
        footSize = (xSize+zSize)*0.5
        
        overshoot = footSize*ikTargetOvershootSize
        platformOffset[0] = [mc.getAttr('%s.t%s'%(shapePosNode, axis)) for axis in 'xyz']
        platformOffset[0][1] += footSize * ikTargetLiftOff * (-1 if side == Settings.rightSide else 1)
        if side == Settings.rightSide:
            platformOffset[0][0] *= -1
            platformOffset[0][1] *= -1
            platformOffset[0][2] *= -1

        platformOffset[1] = [mc.getAttr('%s.r%s'%(shapePosNode, axis)) for axis in 'xyz']

        platformOffset[2] = [xSize+overshoot,
                            1,
                            zSize+overshoot]

        ikTargetOffset = platformOffset
        
        mc.delete(shapePosNode)
    else:
        ikTargetOffset = endOffset
    
    # ik rig
    
    ikTargetRig = Control.createControl(node=dummyPosNode,
                                        component=name,
                                        element='ik',
                                        side=side,
                                        deleteNode=True,
                                        shape=ikTargetShape,
                                        color=ikTargetColor,
                                        offset=ikTargetOffset,
                                        hasPivot=hasPivot,
                                        useGuideAttr=False,
                                        hasRotateOrder=True)

    Nodes.lockAndHideAttributes(ikTargetRig['control'], t=[False, False, False], r=[False, False, False],
                                s=[True, True, True], v=True)
    
    if quadruped:
        # quadruped attributes
        Nodes.addAttrTitle(ikTargetRig['control'], 'quadruped')

        quadrupedAttrName = 'quadrupedEnabled'
        weightBalanceAttrName = 'weightBalance'
        heelPivotAttrName = 'heelPivotOffset'

        mc.addAttr(ikTargetRig['control'], at='bool', k=True, dv=True, ln=quadrupedAttrName)
        mc.addAttr(ikTargetRig['control'], at='float', k=True, dv=0.5, ln=weightBalanceAttrName, hasMinValue=True, minValue=0, hasMaxValue=True, maxValue=1)
        mc.addAttr(ikTargetRig['control'], at='float', k=True, dv=0, ln=heelPivotAttrName, hasMinValue=True, minValue=0)

        quadrupedAttr = ikTargetRig['control']+'.'+quadrupedAttrName
    else:
        quadrupedAttr = None

    if smoothIk or hasStretch:
        Nodes.addAttrTitle(ikTargetRig['control'], 'ik', niceName='IK')
    
    # ik handle node
    
    ikHandleNode = Nodes.ikHandleNode(ikChain[0], ikChain[2])
    
    rigNodes.append(ikHandleNode)
    if not quadruped and midControl:
        mc.parent(modChain[2], ikChain[2])
    
    # ik upnode
    
    mc.parent(ikHandleNode, ikTargetRig['scaleCompensate'])

    ikUpnodeRig = Control.createControl(node=upnodeGuide,
                                        component=name,
                                        element='upnode',
                                        deleteNode=False,
                                        side=side,
                                        parentType=None,
                                        alignAxis=None)
    
    Nodes.lockAndHideAttributes(ikUpnodeRig['control'], t=[False, False, False], r=[True, True, True],
                                s=[True, True, True], v=True)
    
    # elbow/knee control

    if quadruped:
        midNames = [midName, 'heel']
    else:
        midNames = [midName]
    
    if midControl:

        midRigs = dict()
        midCntNodes = list()
        midPntNodes = list()

        if quadruped:
            midParentNodes = [ikChain[1], ikHandleNode]
            midStartNodes = [ikChain[0], ikChain[1]]
            tagNames = [upperName, lowerName]
        else:
            midParentNodes = [ikChain[1]]
            midStartNodes = [ikChain[0]]
            tagNames = [upperName]

        for m , midName in enumerate(midNames):
            midRig = Control.createControl(node=midParentNodes[m],
                                            component=name,
                                            element=midName, 
                                            side=side,
                                            deleteNode=False,
                                            parentType=None,
                                            shape='Rectangle',
                                            offset=[[0, 0, 0], [0, 0, 90], endOffset[2] if quadruped else lowerLimbOffset[2]],
                                            useGuideAttr=False,
                                            mirrorScale=[-1, -1, -1])
            
            midPntNode = AddNode.inbetweenNode(midRig['offset'], nodeType='pnt')
            midPntNodes.append(midPntNode)
            Nodes.orientConstraint([midStartNodes[m], midParentNodes[m]], midPntNode)
            if side != Settings.rightSide and limbType == 'leg':
                mc.rotate(0, 180, 0, midPntNode, r=True, os=True)
            parentCnt = Nodes.parentConstraint(midParentNodes[m], midPntNode, skipRotate=['x', 'y', 'z'])
            
            midCntNode = AddNode.inbetweenNode(midPntNode)
            midCntNodes.append(midCntNode)

            mc.parent(midRig['offset'], limbGroup)

            Nodes.lockAndHideAttributes(midRig['control'], t=[False, False, False], r=[True, True, True],
                                        s=[True, True, True], v=True)

            midRigs[tagNames[m]] = midRig
            
        if quadruped:
            Nodes.pointConstraint(midRigs[lowerName]['control'], modChain[2])
    else:
        midRigs = None
    
    ikRigs = [ikTargetRig, ikUpnodeRig]
    if midControl:
        ikRigs.append(midRigs[upperName])
    if quadruped and midControl:
        ikRigs.append(midRigs[lowerName])

    endLocChild = AddNode.emptyNode(component=name, side=side, element='endChild', nodeType=Settings.locNodeSuffix, objType='locator')
    rigNodes.append(endLocChild)
    Nodes.alignObject(endLocChild, blendChain[2])
    mc.parent(endLocChild, blendChain[1])

    endLoc = AddNode.emptyNode(component=name, side=side, element='end', nodeType=Settings.locNodeSuffix, objType='locator')
    rigNodes.append(endLoc)
    Nodes.alignObject(endLoc, blendChain[2])
    mc.parent(endLoc, limbGroup)
    mc.pointConstraint(endLocChild, endLoc)
    if quadruped and midControl:
        Nodes.pointConstraint(modChain[2], blendChain[2])
    
    Nodes.orientConstraint(ikRigs[0]['scaleCompensate'], endLoc)
    
    Nodes.poleVectorConstraint(ikRigs[1]['control'], ikHandleNode)

    ikLine(midRigs, upperName, midControl, ikChain[1], ikUpnodeRig, name, side, limbGroup, limbType)
    
    # fk controls
    
    fkRigs = list()

    for p, part in enumerate([upperName, lowerName, endName]):
        fkRig = Control.createControl(node=fkChain[p],
                                         component=name, 
                                         element=part,
                                         specific='fk',
                                         side=side,
                                         parentType=None,
                                         alignAxis=None,
                                         shape=[upperLimbShape, lowerLimbShape, endShape][p],
                                         useGuideAttr=False,
                                         offset=[upperLimbOffset, lowerLimbOffset, endOffset][p])

        fkRigs.append(fkRig)

        Nodes.lockAndHideAttributes(fkRig['control'], t=[True, True, True], r=[False, False, False],
                                    s=[True if p == 2 and not quadruped else False, True, True], v=True)

    # extra parent control for first fk control to avoid gimbal lock issues
    fkParentRig = Control.createControl(node=fkRigs[0]['mirrorScale'],
                                        component=name, 
                                        element='parent', 
                                        specific='fk',
                                        side=side,
                                        alignAxis=None,
                                        shape='Rectangle',
                                        useGuideAttr=False,
                                        offset=upperLimbOffset)
    
    Nodes.lockAndHideAttributes(fkParentRig['control'], t=[True, True, True], r=[False, False, False], s=[True, True, True])
    if not hasShoulder:
        Tools.parentScaleConstraint(parentNode, fkParentRig['offset'], useMatrix=False)
    Nodes.setParent(fkParentRig['control'], fkRigs[0]['mirrorScale'])
    mc.delete(fkParentRig['offset'])
    if side != None:
        mc.delete(fkParentRig['scaleCompensate'])
    Nodes.setParent(fkRigs[0]['control'], fkParentRig['control'])
    VisSwitch.connectVisSwitchGroup([fkParentRig['control']], limbGroup, displayAttr='fkParentControlDisplay', visGroup=limbType)
    mc.setAttr('%s.fkParentControlDisplay' % limbGroup, False)
    
    limbParent = AddNode.emptyNode(None, name, side, Settings.locNodeSuffix, 'parent')
    Nodes.alignObject(limbParent, blendChain[0])
    mc.parent([blendChain[0], ikChain[0], fkChain[0]], limbParent)
    if midControl:
        mc.parent(modChain[0], ikChain[0])
        mc.parent(modChain[1], ikChain[1])
        if quadruped: 
            mc.parent(modChain[2], ikChain[2])
            mc.parent(modChain[3], ikChain[3])
    
    # middeform

    midDeformJoints = list()

    if hasMidDeformJoint:

        midDeformLocDrvs = list()
        midDeformName = 'elbow' if limbType == 'arm' else 'knee'
        Nodes.addAttrTitle(limbAttrRig['control'], midDeformName)
        attr = midDeformName+'Push'
        mc.addAttr(limbAttrRig['control'], at='float', ln=attr, dv=1, hasMinValue=True, minValue=0, keyable=False)
        mc.setAttr(limbAttrRig['control']+'.'+attr, cb=True)

        for m, midName in enumerate(midNames):

            resChain = modChain if midControl else blendChain

            midDeformJoint = AddNode.jointNode(component=name, side=side, element=midName, specific='knuckle')
            Nodes.alignObject(midDeformJoint, resChain[1+m])
            mc.move(0, 0, lowerLimbSize * 0.1 * (1 if side == Settings.rightSide else -1), midDeformJoint, relative=True, objectSpace=True)
            jointNodes.append(midDeformJoint)
            midDeformJoints.append(midDeformJoint)

            midDeformLoc = AddNode.emptyNode(node=midDeformJoint, nodeType=Settings.locNodeSuffix, objType='locator')
            rigNodes.append(midDeformLoc)

            Nodes.alignObject(midDeformLoc, midDeformJoint, rotation=True)
            mc.parent(midDeformLoc, blendChain[1+m])
            Nodes.parentConstraint([blendChain[m], blendChain[1+m]], midDeformLoc)

            midDeformLocDrv = AddNode.emptyNode(midDeformJoint, nodeType=Settings.drivenNodeSuffix, objType='locator')
            midDeformLocDrvs.append(midDeformLocDrv)
            rigNodes.append(midDeformLocDrv)
            Nodes.alignObject(midDeformLocDrv, midDeformLoc)
            mc.parent(midDeformLocDrv, midDeformLoc)

            mc.parent(midDeformJoint, midDeformLocDrv)

            if m < 2:

                deformFactor = limbAttrRig['control'] + '.' + attr
                param = '%s.translateZ' % (midDeformLocDrv)

                mulNode = Nodes.mulNode(input1='%s.rotateY' % blendChain[1], 
                                        input2=0.01 * (-1 if side == Settings.rightSide else 1), 
                                        output=None, 
                                        specific='midDeform')

                Nodes.mulNode(input1='%s.output' % mulNode, 
                                input2=deformFactor, 
                                output=param, 
                                specific='midDeformFactor')
        
    else:
        midDeformLocDrvs = None
        midDeformJoint = None

    if not quadruped:
        jointNodes.append(blendChain[2])
    
    Nodes.alignObject(limbAttrRig['offset'], blendChain[2])
    Tools.parentScaleConstraint(blendChain[2], limbAttrRig['offset'])

    # ik/fk blend
    
    for b, blendJoint in enumerate(blendChain[:3]):

        ikResChain = modChain if midControl else ikChain

        if b == 2 and limbType == 'arm':
            #ikSource = ikRigs[0]['scaleCompensate']
            ikSource = endLoc
            fkSource = fkRigs[2]['scaleCompensate']
        else:
            ikSource = ikResChain[b]
            fkSource = fkChain[b]

        ikFkBlendCnts = list()
        if b == 2 or (b == 3 and quadruped):
            ikFkBlendPointCnt = Nodes.pointConstraint([ikSource, fkSource], blendJoint)
            ikFkBlendCnts.append(ikFkBlendPointCnt)
        ikFkBlendOrientCnt = Nodes.orientConstraint([ikSource, fkSource], blendJoint)
        ikFkBlendCnts.append(ikFkBlendOrientCnt)

        for ikFkBlendCnt in ikFkBlendCnts:
            ikBlendParam = '%s.%sW0' % (ikFkBlendCnt, ikSource)
            fkBlendParam = '%s.%sW1' % (ikFkBlendCnt, fkSource)

            mc.setDrivenKeyframe(ikBlendParam, cd=ikFkBlendAttr, dv=0, v=0, itt='linear', ott='linear')
            mc.setDrivenKeyframe(ikBlendParam, cd=ikFkBlendAttr, dv=1, v=1, itt='linear', ott='linear')
            mc.setDrivenKeyframe(fkBlendParam, cd=ikFkBlendAttr, dv=0, v=1, itt='linear', ott='linear')
            mc.setDrivenKeyframe(fkBlendParam, cd=ikFkBlendAttr, dv=1, v=0, itt='linear', ott='linear')
    
    if limbType == 'arm':
        Nodes.orientConstraint(ikRigs[0]['scaleCompensate'], ikChain[2])

    for n in range(len(fkRigs)):
        Nodes.parentConstraint(fkRigs[n]['scaleCompensate'], fkChain[n])

    mc.parent(fkRigs[2]['offset'], limbGroup)
    mc.parent(fkRigs[1]['offset'], limbGroup)
    mc.parentConstraint(fkRigs[1]['scaleCompensate'], fkRigs[2]['offset'], mo=True)
    mc.parentConstraint(fkRigs[0]['scaleCompensate'], fkRigs[1]['offset'], mo=True)

    for ikNode in ikRigs:
        param = '%s.visibility' % (ikNode['control'])
        mc.setDrivenKeyframe(param, cd=ikFkBlendAttr, dv=0, v=0, itt='linear', ott='linear')
        mc.setDrivenKeyframe(param, cd=ikFkBlendAttr, dv=1, v=1, itt='linear', ott='linear')

    for fkNode in fkRigs+[fkParentRig]:
        param = '%s.visibility' % (fkNode['control'])
        mc.setDrivenKeyframe(param, cd=ikFkBlendAttr, dv=0, v=1, itt='linear', ott='linear')
        mc.setDrivenKeyframe(param, cd=ikFkBlendAttr, dv=1, v=0, itt='linear', ott='linear')
    
    # upnode follow and pin
    Nodes.addAttrTitle(ikUpnodeRig['control'], 'Elbow' if limbType == 'arm' else 'Knee')
    followAttrName = 'follow%s' % ('Hand' if limbType == 'arm' else 'Foot')
    followAttr = ikUpnodeRig['control']+'.'+followAttrName
    mc.addAttr(ikUpnodeRig['control'], at='float', ln=followAttrName, keyable=True, hidden=False, hasMinValue=True,
            minValue=0, hasMaxValue=True, maxValue=1, dv=0)
    if pinning:
        pinAttr = 'upnodePin'
        mc.addAttr(ikUpnodeRig['control'], at='float', ln=pinAttr,
                   nn='Pin Elbow' if limbType == 'arm' else 'Pin Knee',
                   keyable=True, hidden=False, hasMinValue=True, minValue=0, hasMaxValue=True, maxValue=1, dv=0)

    # stretch scale / smooth ik

    if smoothIk:

        smoothIkAttrName = 'smoothIk'
        smoothIkIn1Attr = 'smoothIkIn1'
        smoothIkIn2Attr = 'smoothIkIn2'
        smoothIkScaleInAttr = 'smoothIkScaleIn'
        smoothIkOut1Attr = 'smoothIkOut1'
        smoothIkOut2Attr = 'smoothIkOut2'
        smoothIkScaleOutAttr = 'smoothIkScaleOut'
        smoothIkOffsetAttrName = 'smoothIkOverstretch'

        smoothIkAttr = ikTargetRig['control']+'.'+smoothIkAttrName
        smoothIkOffsetAttr = ikTargetRig['control']+'.'+smoothIkOffsetAttrName

        mc.addAttr(ikTargetRig['control'], at='float', ln=smoothIkAttrName, keyable=True, hidden=False,
                   hasMinValue=True,
                   minValue=0, hasMaxValue=True, maxValue=1, dv=0)
        mc.addAttr(ikTargetRig['control'], at='float', ln=smoothIkIn1Attr, keyable=False, hidden=False, dv=-60)
        mc.addAttr(ikTargetRig['control'], at='float', ln=smoothIkIn2Attr, keyable=False, hidden=False, dv=60)
        mc.addAttr(ikTargetRig['control'], at='float', ln=smoothIkOut1Attr, keyable=False, hidden=False, dv=-4)
        mc.addAttr(ikTargetRig['control'], at='float', ln=smoothIkOut2Attr, keyable=False, hidden=False, dv=0)
        mc.addAttr(ikTargetRig['control'], at='float', ln=smoothIkScaleInAttr, keyable=False, hidden=False, dv=6)
        mc.addAttr(ikTargetRig['control'], at='float', ln=smoothIkScaleOutAttr, keyable=False, hidden=False, dv=4)
        if midControl:
            mc.addAttr(ikTargetRig['control'], at='float', ln=smoothIkOffsetAttrName, keyable=True, hidden=False, dv=1)
    else:
        smoothIkAttr = None
        smoothIkOffsetAttr = None

    # quadruped switch

    if quadruped:
        quadSwitchOffNode = AddNode.emptyNode(ikHandleNode, parentNode=ikTargetRig['pivotCompensate'], nodeType='quadSwitchOff', lockScale=True)
        quadSwitchOnNode = AddNode.emptyNode(ikTargetRig['pivotCompensate'], parentNode=ikTargetRig['pivotCompensate'], nodeType='quadSwitchOn', lockScale=True)
        quadSwitchNode = AddNode.emptyNode(ikTargetRig['pivotCompensate'], parentNode=ikTargetRig['pivotCompensate'], nodeType='quadSwitch', lockScale=True)
        Nodes.alignObject(quadSwitchOnNode, ikChain[3])
        distanceEnd = quadSwitchNode
    else:
        distanceEnd = ikHandleNode
    distanceNodes = Tools.createDistanceDimension(limbParent, distanceEnd, parentType='pointConstraint')
    rigNodes.extend(distanceNodes)

    if hasStretch:
        autoStretchAttr = 'autoStretch'
        mc.addAttr(ikTargetRig['control'], at='float', ln=autoStretchAttr, keyable=True, hidden=False,
                hasMinValue=True,
                minValue=0, hasMaxValue=True, maxValue=1, dv=1)

        manualStretchAttr = 'manualStretch'
        mc.addAttr(ikTargetRig['control'], at='float', ln=manualStretchAttr, keyable=False, hidden=False,
                hasMinValue=True,
                minValue=0.1, dv=1)

        manualStretch = ikTargetRig['control'] + '.' + manualStretchAttr
    
    if quadruped:
        
        # quadruped distance swop
        pointCnt = mc.pointConstraint([quadSwitchOffNode, quadSwitchOnNode], quadSwitchNode)[0]
        mc.setDrivenKeyframe(pointCnt + '.' + quadSwitchOffNode + 'W0', cd=quadrupedAttr, dv=0, v=1, itt='linear', ott='linear')
        mc.setDrivenKeyframe(pointCnt + '.' + quadSwitchOffNode + 'W0', cd=quadrupedAttr, dv=1, v=0, itt='linear', ott='linear')
        mc.setDrivenKeyframe(pointCnt + '.' + quadSwitchOnNode + 'W1', cd=quadrupedAttr, dv=1, v=1, itt='linear', ott='linear')
        mc.setDrivenKeyframe(pointCnt + '.' + quadSwitchOnNode + 'W1', cd=quadrupedAttr, dv=0, v=0, itt='linear', ott='linear')
        
    def applyStretchScale(node):

        attr = '%s.sx' % (node)
        if quadruped:
            quadLine1 = '$quadruped = %s;\n' % quadrupedAttr
            quadLine2 = 'if ($quadruped > 0) {$limbLength = %s;}\n' % quadLimbLength
        else:
            quadLine1 = ''
            quadLine2 = ''
        expr = '$curDistance = %s.distance / (%s.globalScale);\n' % (distanceNodes[2], limbGroup) \
                + quadLine1 \
                + '$limbLength = %s;\n' % fullLimbLength \
                + quadLine2 \
                + '$ikScaleValue = 1 + (($curDistance / $limbLength)-1) * %s;\n' % (ikTargetRig['control'] + '.' + autoStretchAttr) \
                + '$ikVal = 1.0;\n' \
                + 'if ($curDistance > $limbLength) {$ikVal = $ikScaleValue;}\n'  \
                + '$res = $ikVal;\n'

        if smoothIk:
            expr = expr \
                    + '$x = 0.0;\n' \
                    + 'if ($ikScaleValue < 1) {$x = ($ikScaleValue - 1) * %s.%s;}\n' % (ikTargetRig['control'], smoothIkScaleInAttr) \
                    + 'if ($ikScaleValue > 1) {$x = ($ikScaleValue - 1) * %s.%s;}\n' % (ikTargetRig['control'], smoothIkScaleOutAttr) \
                    + 'if ($x < -1) {$x = -1;}\n' \
                    + 'if ($x > 1) {$x = 1;}\n' \
                    + '$hermVal = 1.0;\n' \
                    + '$in1 = %s.%s;\n' % (ikTargetRig['control'], smoothIkIn1Attr) \
                    + '$in2= %s.%s;\n' % (ikTargetRig['control'], smoothIkIn2Attr) \
                    + '$out1= %s.%s;\n' % (ikTargetRig['control'], smoothIkOut1Attr) \
                    + '$out2= %s.%s;\n' % (ikTargetRig['control'], smoothIkOut2Attr) \
                    + 'if ($curDistance < $limbLength) {$hermVal = `hermite 0 1 $in1 $in2 (1+$x)`;}\n' \
                    + 'if ($curDistance > $limbLength) {$hermVal = `hermite 1 0 $out1 $out2 $x`;}\n' \
                    + '$res = $res + (%s * $hermVal * 0.0025);\n'%smoothIkAttr \

        expr = expr + '%s = $res*%s' % (attr, manualStretch)

        Nodes.exprNode(attr, specific='stretchScale', expr=expr)

    if hasStretch:
        applyStretchScale(ikChain[0])
        mc.connectAttr('%s.sx' % ikChain[0], '%s.sx' % ikChain[1])
        if quadruped:
            attr = '%s.sx' % ikChain[2]
            expr = '$ikScaleValue = 1.0;\n' \
                + '$quadruped = %s;\n' % quadrupedAttr \
                + 'if ($quadruped > 0) {$ikScaleValue = %s.sx;}\n' % ikChain[0] \
                + '%s = $ikScaleValue' % attr
            Nodes.exprNode(attr, specific='quadrupedScale', expr=expr)
        
        scaleChain = [blendChain[0], blendChain[1]]
        if quadruped:
            scaleChain.append(blendChain[2])
        for n, node in enumerate(scaleChain):
            attr = '%s.sx' % (node)

            expr = '$ikScaleValue = %s.sx;\n' % (modChain[n] if midControl else ikChain[n]) \
                + '$fkVal = %s.scaleX * (1 - %s);\n'%(fkRigs[n]['control'], ikFkBlendAttr) \
                + '$ikVal = $ikScaleValue * %s;\n'%ikFkBlendAttr \
                + '$res = $ikVal + $fkVal;\n' \
                + '%s = $res' % (attr)
            Nodes.exprNode(attr, specific='quadrupedScaleIkFk', expr=expr)

    if midControl and smoothIk and not quadruped:
        applySmoothIkOffset(midCntNodes[0], smoothIkAttr, smoothIkOffsetAttr)
    
    # bendy not supported at the moment, needs update
    '''
    if bendy:

        curveName = sidePfx+('_'.join([name, 'bendy', Settings.guidePivotSuffix]))

        # for an unknown reason the python method does not return a correct shape, using the mel command instead
        curveNode = mel.eval(
            'curve -d 3 -p 0 0 0 -p ({0}/3*1) 0 0 -p ({0}/3*2) 0 0 -p {0} 0 0 -k 0 -k 0 -k 0 -k 1 -k 1 -k 1'.format(
                quadLimbLength if quadruped else fullLimbLength))
        curveNode = mc.rename(curveNode, curveName)
        mc.rename(mc.listRelatives(curveNode, shapes=True)[0], curveName + 'Shape')

        curveRig = Curve.Build(curveNode=curveNode,
                                       name='_'.join([name, 'bendy']),
                                       size=upperLimbOffset[2][1],
                                       side=side,
                                       shape='Sphere',
                                       jointCount=limbTwistCount * 2 + 1,
                                       alignAxis='X',
                                       upAxis='Y',
                                       offset=[0, 0, 0],
                                       closedCurve=False,
                                       squashing=squashing,
                                       scaling=True,
                                       chain=True,
                                       flipChainDirection=True if side == Settings.rightSide else False,
                                       segmenting=False,
                                       controlPerJoint=False,
                                       upnode=None).createRig()

        mc.delete(curveNode)

        cntList = [mc.pickWalk(x, d='up')[0] for x in curveRig['joints']][:-1]
        # we need to add one more joint on curve creation and substract the last one to keep the arrangement
        # consistent with the twist joints
        mc.delete(curveRig['joints'])

        if side == Settings.rightSide:
            [mc.setAttr(Nodes.replaceNodeType(cnt, Settings.motionPathSuffix) + '.inverseFront', 1) for cnt in cntList]

        Nodes.addAttrTitle(limbAttrRig['control'], 'bendy')

        bendyAttrName = 'bendy'
        bendyAttr = limbAttrRig['control'] + '.' + bendyAttrName
        mc.addAttr(limbAttrRig['control'], at='float', ln=bendyAttrName, k=True, dv=0,
                   hasMinValue=True, minValue=0, hasMaxValue=True, maxValue=1)

        bendyOffsetAttrName = 'maintain%sLength' % limbType.capitalize()
        bendyOffsetAttr = limbAttrRig['control'] + '.' + bendyOffsetAttrName
        mc.addAttr(limbAttrRig['control'], at='float', ln=bendyOffsetAttrName, k=True, dv=1,
                   hasMinValue=True, minValue=0, hasMaxValue=True, maxValue=1)

        locList = twistNodes[0]['locs'] + twistNodes[1]['locs']
        twistJointList = twistNodes[0]['joints'] + twistNodes[1]['joints']

        jointParentList = [AddNode.parentNode(x) for x in twistJointList]

        # [mc.setAttr('%s.inheritsTransform' % t, 0) for t in twistJointList]

        Tools.blendBetween(locList, cntList, jointParentList,
                           attrNode=limbAttrRig['control'], attrName=bendyAttrName, maintainOffset=False)

        mc.addAttr(limbAttrRig['control'], at='float', ln='squashPower', k=True, dv=0.5)
        mc.connectAttr(limbAttrRig['control'] + '.squashPower', '%s.scalePowerMid' % bendyRigGroup)

        mc.parentConstraint(limbParent, curveRig['offsets'][0], maintainOffset=False)
        bezierDrvList = []
        for p in [0, 3]:
            mc.hide(curveRig['offsets'][p])
        for p in [1, 2]:
            Nodes.alignObject(curveRig['offsets'][p], blendChain[1])
            mc.move((fullLimbLength / 6 if p == 2 else -fullLimbLength / 6) * (-1 if side == Settings.rightSide else 1), 0, 0,
                    curveRig['offsets'][p], r=True, os=True)
            bezierDrv = AddNode.inbetweenNode(curveRig['offsets'][p], nodeType='drv')
            bezierDrvList.append(bezierDrv)
            mc.transformLimits(bezierDrv, tz=(0, 0),
                               etz=[1, 0] if side == Settings.rightSide else [0, 1])
            weightValues = [0.67, 0.33] if p == 1 else [0.33, 0.67]
            parentCnt = mc.parentConstraint(blendChain[0], curveRig['offsets'][p],
                                            maintainOffset=True, weight=weightValues[0])[0]
            mc.parentConstraint(blendChain[1], curveRig['offsets'][p],
                                maintainOffset=True, weight=weightValues[1])
            mc.setAttr('%s.interpType' % parentCnt, 2)
        mc.parentConstraint(blendChain[2], curveRig['offsets'][3], maintainOffset=False)

        # add blending for hasMidDeformJoint, so it attaches to the curve in bendy mode
        parentCnt = mc.parentConstraint(twistNodes[1]['joints'][0], hasMidDeformJoint, mo=True)[0]
        mc.setAttr('%s.interpType' % parentCnt, 2)

        mc.setDrivenKeyframe(parentCnt + '.' + midDeformLocDrvs[0] + 'W0', cd=bendyAttr, dv=0, v=1, itt='linear',
                             ott='linear')
        mc.setDrivenKeyframe(parentCnt + '.' + midDeformLocDrvs[0] + 'W0', cd=bendyAttr, dv=1, v=0, itt='linear',
                             ott='linear')
        mc.setDrivenKeyframe(parentCnt + '.' + twistNodes[1]['joints'][0] + 'W1', cd=bendyAttr, dv=1, v=1, itt='linear',
                             ott='linear')
        mc.setDrivenKeyframe(parentCnt + '.' + twistNodes[1]['joints'][0] + 'W1', cd=bendyAttr, dv=0, v=0, itt='linear',
                             ott='linear')

        # creating ik and fk distance nodes seperately as blend chain gives cycle error
        ikDistanceNodes = Tools.createDistanceDimension(limbParent, ikChain[2], uniqueName='ik',
                                                           parentType='pointConstraint')
        fkDistanceNodes = Tools.createDistanceDimension(limbParent, fkChain[2], uniqueName='fk',
                                                           parentType='pointConstraint')
        rigNodes.extend(ikDistanceNodes)
        rigNodes.extend(fkDistanceNodes)
        mulIkFkDistNodeList = []
        for i, ikFkDistanceNodes in enumerate([ikDistanceNodes, fkDistanceNodes]):
            mulIkFkName = ['ik', 'fk'][i]
            blendExpr = [ikExprName, fkExprName][i]
            mulIkFkDistNode = mc.shadingNode('multDoubleLinear', asUtility=True,
                                             name=sidePfx+('_'.join([limbType, '%sDistance_mul' % mulIkFkName])))
            mc.connectAttr('%s.output[0]' % blendExpr, '%s.input1' % mulIkFkDistNode)
            mc.connectAttr('%s.distance' % ikFkDistanceNodes[2], '%s.input2' % mulIkFkDistNode)
            mulIkFkDistNodeList.append(mulIkFkDistNode)

        addIkFkResDistNode = mc.shadingNode('addDoubleLinear', asUtility=True,
                                            name=sidePfx+('_'.join([limbType, 'ikFkResDistance_add'])))
        mc.connectAttr('%s.output' % mulIkFkDistNodeList[0], '%s.input1' % addIkFkResDistNode)
        mc.connectAttr('%s.output' % mulIkFkDistNodeList[1], '%s.input2' % addIkFkResDistNode)

        # this is for controlling bendy deformation on bezier handles
        addDistNode = mc.shadingNode('addDoubleLinear', asUtility=True,
                                     name=sidePfx+('_'.join([limbType, 'bendyDistance_add'])))
        mc.connectAttr('%s.output' % addIkFkResDistNode, '%s.input1' % addDistNode)
        mc.setAttr('%s.input2' % (addDistNode), -fullLimbLength)

        mulBendyNode = mc.shadingNode('multDoubleLinear',
                                      asUtility=True,
                                      name=sidePfx+('_'.join([limbType, 'bendy_mul'])))
        mc.connectAttr('%s.output' % addDistNode, '%s.input1' % mulBendyNode)
        mc.connectAttr(bendyAttr, '%s.input2' % mulBendyNode)

        for d, attr in enumerate([bendyRoundnessAttr, bendyOffsetAttr]):
            mulName = ['BendyRoundness', 'BendyOffset'][d]
            mulValue = (-1 if side == Settings.rightSide else 1) * (0.4 if d == 1 else 1)
            mulAxis = 'xz'[d]

            mulFactorNode = mc.shadingNode('multDoubleLinear', asUtility=True,
                                           name=sidePfx+('_'.join([limbType, 'bendyFactor%s_mul' % mulName])))
            mc.connectAttr('%s.output' % mulBendyNode, '%s.input1' % mulFactorNode)
            mc.connectAttr(attr, '%s.input2' % (mulFactorNode))

            mulDistNode = mc.shadingNode('multDoubleLinear', asUtility=True,
                                         name=sidePfx+('_'.join([limbType, 'bendyDistance%s_mul' % mulName])))
            mc.connectAttr('%s.output' % mulFactorNode, '%s.input1' % mulDistNode)
            mc.setAttr('%s.input2' % (mulDistNode), mulValue)

            mc.connectAttr('%s.output' % mulDistNode, '%s.t%s' % (bezierDrvList[0], mulAxis))

        mulInverseNode = mc.shadingNode('multDoubleLinear', asUtility=True,
                                        name=sidePfx+('_'.join([limbType, 'bendyInverse_mul'])))
        mc.connectAttr('%s.tx' % bezierDrvList[0], '%s.input1' % mulInverseNode)
        mc.setAttr('%s.input2' % (mulInverseNode), -1)

        mc.connectAttr('%s.output' % mulInverseNode, '%s.tx' % bezierDrvList[1])
        mc.connectAttr('%s.tz' % bezierDrvList[0], '%s.tz' % bezierDrvList[1])

        for controlNode in curveRig['controls']:
            param = '%s.visibility' % (controlNode)
            expr = '%s = %s*%s.%s' % (param, bendyAttr, limbAttrRig['control'], controlVisAttr)
            mc.expression(alwaysEvaluate=0,
                          name='_'.join([Nodes.replaceNodeType(controlNode), controlVisAttr, Settings.expressionSuffix]),
                          object=param,
                          string=expr)

    else:

        curveRig = None
        ikDistanceNodes = None
        fkDistanceNodes = None
        bendyRigGroup = None
    '''
    if curved:

        twistNodes = []
        curveRigGroupList = []
        curveRigs = []

        parts = [upperName, lowerName]
        if quadruped:
            parts.append(endName)

        for p, part in enumerate(parts):

            limbLengths = [upperLimbLength, lowerLimbLength]
            twistCounts  = [upperLimbTwistCount, lowerLimbTwistCount]
            if quadruped:
                limbLengths.append(endLimbLength)
                twistCounts.append(endLimbTwistCount)

            if twistCounts[p] > 0:

                curveNode = Nodes.curveNode(component=name, side=side, nodeType=Settings.guideCurveSuffix, element=part, pointCount=4)[0]
                # putting all cvs to 0 in order to avoid cluster offsets since we have no guide pivots
                for axis in 'xyz':
                    [mc.setAttr('%s.controlPoints[%s].%sValue'%(Nodes.getShapes(curveNode)[0], c, axis), 0) for c in range(4)]

                curveRig = Curve.Build(curveNode=curveNode,
                                        side=side,
                                        offset=[[0, 0, 0], [90, 90, 0]] + [[upperLimbOffset[2], lowerLimbOffset[2], endOffset[2]][p]],
                                        shape='Rectangle',
                                        jointCount=twistCounts[p],
                                        alignAxis='X',
                                        upAxis='Y',
                                        squashing=squashing,
                                        scaling=True,
                                        chain=False,
                                        flipOrientation=False,
                                        controlPerJoint=False,
                                        upnode=None,
                                        visGroup=limbGroup,
                                        ignoreMissingGuideControlWarning=True,
                                        skeletonParent=skeletonParent if p == 0 else curveRigs[-1]['joints'][-1],
                                        skeletonParentToFirst=True).createRig()
                mc.delete(curveNode)
                
                cntList = [Nodes.getParent(x) for x in curveRig['joints']][:-1]

                # making sure the start and end joints are not at the very start/end position of the curve, so skin mirroring works fine
                for j, jointNode in enumerate([curveRig['joints'][0], curveRig['joints'][-1]]):
                    mc.setAttr('%s.tx' % jointNode, limbLengths[p] * 0.05 * (1 if j == 0 else -1))

                VisSwitch.connectVisSwitchGroup(curveRig['offsets'], limbGroup, displayAttr='CurveControlDisplay',
                                                visGroup=limbType)
                curveRigGroupList.append(curveRig['rigGroup'])
                curveRigs.append(curveRig)

                if squashing:
                    Nodes.addAttrTitle(limbAttrRig['control'], part + 'SquashStretch',
                                    niceName='Squash & Stretch')
                    innerAttrName = part + 'InnerSquash'
                    outerAttrName = part + 'OuterSquash'
                    mc.addAttr(limbAttrRig['control'], at='float', ln=innerAttrName, k=True)
                    mc.addAttr(limbAttrRig['control'], at='float', ln=outerAttrName, k=True)
                    for attrName in ['scalePowerStart', 'scalePowerEnd']:
                        mc.connectAttr('%s.%s' % (limbAttrRig['control'], outerAttrName),
                                    '%s.%s' % (curveRig['rigGroup'], attrName))
                    mc.connectAttr('%s.%s' % (limbAttrRig['control'], innerAttrName),
                                '%s.%s' % (curveRig['rigGroup'], 'scalePowerMid'))

                [Color.setColor(x, color='Bright Blue' if side == Settings.leftSide else 'Bright Red' if side == Settings.rightSide else 'Bright Yellow') for x in curveRig['controls']]

                mc.parent(curveRig['rigGroup'], limbGroup)

                startParent = blendChain[p]
                endParent = blendChain[p+1]
                
                for g, pointLocGroup in enumerate(curveRig['offsets']):
                    Nodes.alignObject(pointLocGroup, startParent)
                    mc.move(limbLengths[p] / 3 * g * (-1 if side == Settings.rightSide else 1), 0, 0, pointLocGroup, r=True, os=True)
                    mc.parent(pointLocGroup, curveRig['rigGroup'])
                    if g == 0 or g == 3:
                        mc.hide(curveRig['controls'][g])
                        Nodes.alignObject(pointLocGroup, startParent if g == 0 else endParent,
                                        rotation=True if limbType == 'arm' else False)
                    else:
                        cntNode = AddNode.inbetweenNode(curveRig['offsets'][g], nodeType='twistBlend', lockScale=True)
                        Tools.blendBetween([curveRig['controls'][0]], [curveRig['controls'][3]], [cntNode],
                                        attrNode=limbAttrRig['control'],
                                        attrName=part + 'Twist' + str(g + 1).zfill(2),
                                        attrTitle=part + 'Twist',
                                        orientConstrained=True, 
                                        maintainOffset=False, 
                                        defaultValue=[0, 0.33, 0.67, 0][g],
                                        attrIsKeyable=False)

                    parentCaptureNode = AddNode.emptyNode(node=pointLocGroup, nodeType='parentCapture')
                    Nodes.alignObject(parentCaptureNode, pointLocGroup)
                    Nodes.setParent(parentCaptureNode, startParent)
                    Tools.parentScaleConstraint(parentCaptureNode, pointLocGroup, useMatrix=True)

                if p == 0:
                    for t, twistSet in enumerate([[startParent, endParent], [limbParent, blendChain[1]]]):
                        twistNode, twistIKHandle, poleVectorNode = Tools.createTwistNode(twistSet[0],
                                                                                        twistSet[1],
                                                                                        specific='twist' if t == 0 else 'twistInverse',
                                                                                        upAxis='Y' if t == 0 else 'Z',
                                                                                        rotateOrder=2)
                        rigNodes.extend([twistIKHandle, poleVectorNode, twistNode])

                        if t == 0:
                            mc.connectAttr('%s.rx' % twistNode,
                                        '%s.rx' % AddNode.parentNode(curveRig['controls'][3], nodeType='twistCnt',
                                                                        lockScale=True))
                        else:
                            mc.parent([twistIKHandle, poleVectorNode], blendChain[0])

                            Nodes.mulNode(input1='%s.rx' % twistNode, 
                                            input2=-1, 
                                            output='%s.rx' % AddNode.parentNode(curveRig['controls'][0], nodeType='twistCnt', lockScale=True), 
                                            specific='twistInverse')
                else:
                    twistNode, twistIKHandle, poleVectorNode = Tools.createTwistNode(startParent,
                                                                                    endParent,
                                                                                    upAxis='Z' if limbType == 'arm' else 'Y')

                    rigNodes.extend([twistIKHandle, poleVectorNode, twistNode])
                    mc.connectAttr('%s.rx' % twistNode,
                                '%s.rx' % AddNode.parentNode(curveRig['controls'][3], nodeType='twistCnt',
                                                                lockScale=True))

                twistDict = {
                    'locs': cntList,
                    'joints': curveRig['joints'],
                }
                twistNodes.append(twistDict)
            else:
                twistNodes.append([])
    
    # space switch

    if spaceNodes:
        
        SpaceSwitch.createSpaceSwitch(offNode=fkRigs[0]['offset'],
                                        sourceObjs=spaceNodes[::],
                                        switchNames=spaceNames[::],
                                        translation=False,
                                        defaultSpace=defaultSpace)
        
        #if reverseSpaces != None: # not building reverse spaces for now for stability tests
            #spaces.extend(reverseSpaces)
        
        for n, node in enumerate([ikRigs[0]['offset'], ikRigs[1]['offset']]):
            spaceNode = SpaceSwitch.createSpaceSwitch(offNode=node,
                                                        # sourceObjs=[x + Settings.sfx for x in spaces], # not building reverse spaces for now for stability tests
                                                        # switchNames=spaces, # not building reverse spaces for now for stability tests
                                                        sourceObjs=spaceNodes[::],
                                                        switchNames=spaceNames[::],
                                                        defaultSpace=defaultSpace)

            # not building reverse spaces for now for stability tests
            '''
            if reverseSpaces != '' and n == 0:
                # reverse space switch
                spaceNode = SpaceSwitch.createSpaceSwitch(offNode=node,
                                                    sourceObjs=[x + Settings.sfx for x in reverseSpaces],
                                                    switchNames=reverseSpaces,
                                                    defaultSpace=defaultSpace,
                                                    rigGroup=limbGroup)
            ###
            '''
    else:
        spaceNode = None
    
    # upnode follow
    
    cntNode = AddNode.inbetweenNode(spaceNode if spaceNode is not None else node)
    if spaceNodes:

        driverNode = ikRigs[1]['offset'] if spaceNode == None else spaceNode

        parentCnt = Nodes.parentConstraint([ikRigs[0]['control'], driverNode], cntNode)

        mc.setDrivenKeyframe('%s.%sW0' % (parentCnt, ikRigs[0]['control']), cd=followAttr, dv=1, v=1, itt='linear', ott='linear')
        mc.setDrivenKeyframe('%s.%sW0' % (parentCnt, ikRigs[0]['control']), cd=followAttr, dv=0, v=0, itt='linear', ott='linear')
        mc.setDrivenKeyframe('%s.%sW1' % (parentCnt, driverNode), cd=followAttr, dv=1, v=0, itt='linear', ott='linear')
        mc.setDrivenKeyframe('%s.%sW1' % (parentCnt, driverNode), cd=followAttr, dv=0, v=1, itt='linear', ott='linear')

    # upnode pin
    
    if pinning or midControl:

        upperLimbDistanceNodes = Tools.createDistanceDimension(limbParent, midRigs[upperName]['control'],
                                                                  parentType='pointConstraint')
        lowerLimbDistanceNodes = Tools.createDistanceDimension(midRigs[upperName]['control'], modChain[2],
                                                                  parentType='pointConstraint')
        rigNodes.extend(upperLimbDistanceNodes)
        rigNodes.extend(lowerLimbDistanceNodes)
        if quadruped:
            endLimbDistanceNodes = Tools.createDistanceDimension(midRigs[lowerName]['control'], modChain[3],
                                                                    parentType='pointConstraint')
            rigNodes.extend(endLimbDistanceNodes)

        Nodes.pointConstraint(limbParent, modChain[0])

        Nodes.aimConstraint(midRigs[upperName]['control'], 
                            modChain[0],
                            upNode=ikChain[0],
                            aimAxis='-x' if side == Settings.rightSide else 'x',
                            upAxis='y',
                            mo=True)

        Nodes.aimConstraint(modChain[2], 
                            modChain[1],
                            upNode=ikChain[1],
                            aimAxis='-x' if side == Settings.rightSide else 'x',
                            upAxis='y',
                            mo=True)

        Nodes.pointConstraint(midRigs[upperName]['control'], modChain[1])
        [mc.setAttr('%s.t%s'%(modChain[2], axis), 0) for axis in 'xyz'] # hard fix
        
        distChain = [modChain[0], modChain[1]]
        sectionDistanceNodes = [upperLimbDistanceNodes, lowerLimbDistanceNodes]
        limbLengths = [upperLimbLength, lowerLimbLength]
        if quadruped:
            distChain.append(modChain[2])
            sectionDistanceNodes.append(endLimbDistanceNodes)
            limbLengths.append(endLimbLength)
        for n, node in enumerate(distChain):

            attr = '%s.sx' % (node)

            expr = '$curDistance = %s.distance / %s.globalScale;\n' % (sectionDistanceNodes[n][2], limbGroup) \
                   + '$scaleValue = $curDistance / %s;\n' % (limbLengths[n]) \
                   + '%s = $scaleValue' % (attr)

            Nodes.exprNode(attr, specific='dist', expr=expr)
        
        if pinning:
            parentCnt = Nodes.parentConstraint([midPntNodes[0], ikUpnodeRig['control']], midCntNodes[0], mo=False)

            influenceAttr = ikUpnodeRig['control'] + '.' + pinAttr

            mc.setDrivenKeyframe(parentCnt + '.' + midPntNodes[0] + 'W0', cd=influenceAttr, dv=0, v=1, itt='linear', ott='linear')
            mc.setDrivenKeyframe(parentCnt + '.' + midPntNodes[0] + 'W0', cd=influenceAttr, dv=1, v=0, itt='linear', ott='linear')
            mc.setDrivenKeyframe(parentCnt + '.' + ikUpnodeRig['control'] + 'W1', cd=influenceAttr, dv=1, v=1, itt='linear', ott='linear')
            mc.setDrivenKeyframe(parentCnt + '.' + ikUpnodeRig['control'] + 'W1', cd=influenceAttr, dv=0, v=0, itt='linear', ott='linear')

            cntNodeAttr = '%s.sx' % (cntNode)

            pinDisplayExpr = '$val = 1;\n' \
                             + 'if (%s > 0.5) {$val = 3;}\n' % (influenceAttr) \
                             + '%s = $val' % (cntNodeAttr)

            Nodes.exprNode(cntNodeAttr, specific='pin', expr=pinDisplayExpr)
            [mc.connectAttr(cntNodeAttr, '%s.s%s' % (cntNode, axis)) for axis in 'yz']

            midCntNodeAttr = '%s.visibility' % (midCntNodes[0])

            midDisplayExpr = '$val = 1;\n' \
                             + 'if (%s > 0.5) {$val = 0;}\n' % (influenceAttr) \
                             + '%s = $val' % (midCntNodeAttr)

            Nodes.exprNode(midCntNodeAttr, specific='display', expr=midDisplayExpr)
        else:
            Nodes.parentConstraint(ikChain[1], midCntNodes[0])
    
    # limb parent

    if not hasShoulder:

        hipsWidth = mc.getAttr('%s.tx' % upperLimbGuide)
        hipsOffset = hipsWidth * limbParentOffset * (-1 if side == Settings.rightSide else 1)

        parentRig = Control.createControl(component=name,
                                            element='parent',
                                            size=hipsWidth * limbParentSize,
                                            side=side,
                                            shape=limbParentShape,
                                            color=limbParentColor,
                                            parentType=None,
                                            deleteNode=True,
                                            useGuideAttr=False,
                                            mirrorScale=[-1, 1, 1],
                                            offset=[[hipsOffset, 0, 0], [90, 90, 0], [1, 1, 1]])

        Nodes.alignObject(parentRig['offset'], fkRigs[0]['offset'], rotation=False)
        Tools.parentScaleConstraint(parentNode, parentRig['offset'], useMatrix=False)
        Tools.parentScaleConstraint(parentRig['control'], fkRigs[0]['offset'], useMatrix=False)
        Tools.parentScaleConstraint(parentRig['control'], ikChain[0], useMatrix=False)
        Tools.parentScaleConstraint(parentRig['control'], limbParent, useMatrix=False)
        Nodes.setParent(parentRig['offset'], limbGroup)

        Nodes.lockAndHideAttributes(parentRig['control'], r=[True, True, True], s=[True, True, True])

    else:

        parentRig = None
    
    mc.parent(fkRigs[0]['offset'], limbGroup)
    
    for axis in 'XYZ':
        mc.setAttr('%s.jointOrient%s' % (blendChain[2], axis), 0)

    extraNodeList = [limbAttrRig['control'], limbParent, hasMidDeformJoint, ikHandleNode]

    mc.parent([limbParent, limbAttrRig['offset'], ikRigs[0]['offset'], ikRigs[1]['offset']], limbGroup)

    mc.setAttr('%s.rotateOrder' % (blendChain[0]), 4)
    mc.setAttr('%s.rotateOrder' % (blendChain[1]), 4)
    mc.setAttr('%s.rotateOrder' % (blendChain[2]), 4)
    
    VisSwitch.connectVisSwitchGroup(rigNodes, limbGroup, displayAttr='setupDisplay')
    VisSwitch.connectVisSwitchGroup(jointNodes, limbGroup, displayAttr='jointDisplay')

    controlNodeList = [ikRigs[x]['control'] for x in range(len(ikRigs))] \
                      + [fkRigs[x]['control'] for x in range(len(fkRigs))] \
                      + [extraNodeList[0]]

    [mc.connectAttr('%s.setupDisplay' % limbGroup, '%s.setupDisplay' % curveRigGroup) for curveRigGroup in curveRigGroupList]
    [mc.connectAttr('%s.jointDisplay' % limbGroup, '%s.jointDisplay' % curveRigGroup) for curveRigGroup in curveRigGroupList]
    [mc.connectAttr('%s.CurveControlDisplay' % limbGroup, '%s.controlDisplay' % curveRigGroup) for curveRigGroup in curveRigGroupList]
    if curveRigGroupList:
        mc.setAttr('%s.CurveControlDisplay' % limbGroup, False)
    if parentRig:
        VisSwitch.connectVisSwitchGroup([parentRig['control']], limbGroup, displayAttr='parentControlDisplay', visGroup=limbType)
    VisSwitch.connectVisSwitchGroup(controlNodeList, limbGroup, displayAttr='controlDisplay', visGroup=limbType)

    # rename blend joints to skin joints if there are no twist joints
    for t in range(3 if quadruped else 2):
        if len(twistNodes[t]) == 0:
            blendChain[t] = mc.rename(blendChain[t], Nodes.replaceNodeType(blendChain[t], Settings.skinJointSuffix))
            Nodes.addSkeletonParentAttr(blendChain[t], skeletonParent if t == 0 else blendChain[t-1])

    if len(twistNodes[2 if quadruped else 1]) > 0:
        Nodes.addSkeletonParentAttr(endJoint, twistNodes[2 if quadruped else 1]['joints'][-1])
    else:
        if not quadruped:
            Nodes.addSkeletonParentAttr(endJoint, blendChain[1])
    
    if quadruped:
        ankleJoints = twistNodes[2]['joints'] if len(twistNodes[2]) > 0 else None
        Nodes.addSkeletonParentAttr(blendChain[3], ankleJoints[-1] if ankleJoints else blendChain[2])
    else:
        ankleJoints = None

    # add skeletonParent attribute for mid deform joints
    for m, midDeformJoint in enumerate(midDeformJoints):
        midSkeletonParent = twistNodes[m+1]['joints'][0] if len(twistNodes[m+1]) > 0 else blendChain[m+1][0]
        Nodes.addSkeletonParentAttr(midDeformJoint, midSkeletonParent)

    if smoothIk:
        mc.setAttr(smoothIkAttr, 1)

    if limbType == 'arm':
        mc.setAttr(ikFkBlendAttr, 0)
    
    mc.select(clear=True)
    
    return {'attr': limbAttrRig,
            'limbType': limbType,
            'ik': ikTargetRig,
            'ikUpnode': ikUpnodeRig,
            'mids': midRigs,
            'fkUpper': fkRigs[0],
            'fkLower': fkRigs[1],
            'fkEnd': fkRigs[2],
            'ikHandle': ikHandleNode,
            'upperJoints': twistNodes[0]['joints'] if len(twistNodes[0]) > 0 else None,
            'lowerJoints': twistNodes[1]['joints'] if len(twistNodes[1]) > 0 else None,
            'ankleJoints': ankleJoints,
            'middleJoint': hasMidDeformJoint,
            'endJoint': endJoint,
            'parentRig': parentRig,
            'fkParentRig': fkParentRig,
            'limbParent': limbParent,
            'ikFkBlendAttr': ikFkBlendAttr,
            'blendJoints': blendChain,
            'ikJoints': ikChain,
            'fkJoints': fkChain,
            'modJoints': modChain if midControl else None,
            'midCntNodes': midCntNodes if midControl else None,
            'quadrupedAttr': quadrupedAttr if quadrupedAttr else None,
            'smoothIkAttr': smoothIkAttr if smoothIk else None,
            'smoothIkOffsetAttr': smoothIkOffsetAttr if smoothIk else None,
            #'bendyRigGroup': bendyRigGroup,
            'limbLength': quadLimbLength if quadruped else fullLimbLength,
            'limbDistanceAttr': '%s.distance'%distanceNodes[2],
            'spaceNodes': spaceNode,
            'rigGroup': limbGroup}