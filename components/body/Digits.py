# Digits

import maya.cmds as mc
import itertools

from bear.system import Settings
from bear.system import Guiding
from bear.system import ConnectionHandling
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import VisSwitch
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.basic import Guide

def guidePlacer(guideGroup, 
                side=Settings.leftSide,
                guideNodes=[],
                upNode=None):
    
    name = Nodes.getComponent(guideGroup)
    aimAxis = '-x' if side == Settings.rightSide else 'x' 
    upAxis = 'y' if side == Settings.rightSide else '-y' 
    sectionGuides = list()
    for n, guideNode in enumerate(guideNodes):
        sectionGuide = Guide.createGuide(component=name,
                                        element=Nodes.getElement(guideNode),
                                        indices=Nodes.getIndices(guideNode),
                                        specific='placer',
                                        side=side,
                                        parentNode=guideGroup,
                                        hasGuideShape=False)
        Nodes.lockAndHideAttributes(sectionGuide['pivot'], r=[True, True, True], lock=False)
        sectionGuides.append(sectionGuide)

    for n, sectionGuide in enumerate(sectionGuides[:-1]):
        constraintNode = Nodes.aimConstraint(sectionGuides[n+1]['pivot'], 
                        sectionGuide['pivot'],
                        aimAxis=aimAxis,
                        upAxis=upAxis,
                        upNode=upNode,
                        upType='objectrotation')
        twistAttr = sectionGuide['pivot']+'.twist'
        Nodes.addAttr(twistAttr)
        mc.connectAttr(twistAttr, '%s.offsetX'%constraintNode)
        Nodes.lockAndHideAttributes(sectionGuide['pivot'], t=[False, False, False], r=[True, True, True], s=[True, True, True], lock=True)
    Nodes.lockAndHideAttributes(sectionGuides[-1]['pivot'], t=[False, False, False], r=[True, True, True], s=[True, True, True], lock=True)

    return sectionGuides

def createGuide(digits,
                name,
                side,
                digitHasBase,
                guideGroup,
                limbType='arm',
                numberedNaming=False,
                oldLimbRig=False):

    mirVal = -1 if side == Settings.rightSide else 1
    
    digitJointNodesList = list()
    
    for g in range(len(digits)):

        digitJointNodesList.append([])

        shiftVal = ((len(digits)/2)*5-g*5)
        
        if limbType == 'leg':
            shiftVal = (shiftVal-5)*-1
        
        segCount = digits[g]+(2 if digitHasBase[g] else 1)
        for s in range(segCount):
            
            pushVal = (s+(1 if digitHasBase[g] else 0))*5

            if limbType == 'arm':
                tOffset = [(40+pushVal)*mirVal, 0, shiftVal]
                rOffset = [180, 0, 0]
            if limbType == 'leg':
                zVal = 20
                tOffset = [(shiftVal)*mirVal, 10, zVal+pushVal]
                rOffset = [180, -90, 0]
            
            if numberedNaming:
                segIndex = (s-1) if digitHasBase[g] else s
                element = 'digit'+('Tip' if s == segCount-1 else '')
                indices = [g, None if s == segCount-1 else segIndex]
            else:
                segIndex = (s-1) if digitHasBase[g] else s
                element = ['thumb', 'index', 'middle', 'ring', 'pinky'][g]+('Tip' if s == segCount-1 else '')
                indices = None if s == segCount-1 else segIndex

            digitJointNode = AddNode.jointNode(component=name,
                                                side=side, 
                                                nodeType=Settings.guidePivotSuffix,
                                                element=element,
                                                indices=indices,
                                                convertRotToOrient=True)
            digitJointNodesList[-1].append(digitJointNode)

            [mc.setAttr('%s.t%s'%(digitJointNode, axis), tOffset[a]) for a, axis in enumerate('xyz')]
            [mc.setAttr('%s.r%s'%(digitJointNode, axis), rOffset[a]) for a, axis in enumerate('xyz')]

            if side == Settings.rightSide:
                mc.setAttr('%s.jointOrientX'%digitJointNode, -180)

            Nodes.lockAndHideAttributes(digitJointNode, s=[True, True, True])
            if s == 0:
                mc.parent(digitJointNode, guideGroup)
            else:
                mc.parent(digitJointNode, digitJointNodesList[-1][-2])

    parentGuide = AddNode.jointNode(component=name,
                                    element='digits',
                                    side=side, 
                                    nodeType=Settings.guidePivotSuffix, 
                                    parentNode=guideGroup,
                                    convertRotToOrient=True)
    Nodes.lockAndHideAttributes(parentGuide, s=[True, True, True])
    if limbType == 'arm':
        mc.setAttr('%s.tx'%parentGuide, 40*mirVal)
        mc.setAttr('%s.tz'%parentGuide, 2.5)
    if limbType == 'leg':
        mc.setAttr('%s.ty'%parentGuide, 10)
        mc.setAttr('%s.tz'%parentGuide, 15)

    for j, jointNodes in enumerate(digitJointNodesList):

        Guide.createGuide(node=jointNodes[1 if digitHasBase[j] else 0],
                            size=5,
                            side=side,
                            alignAxis='X',
                            hasAttrs=True,
                            hasGuidePivot=False)

        Nodes.setParent(jointNodes[0], parentGuide)
    
    # guide placer
    for digitJointNodes in digitJointNodesList:
        sectionGuides = guidePlacer(guideGroup, 
                                        side=side,
                                        guideNodes=digitJointNodes,
                                        upNode=parentGuide)
        for jointNode in digitJointNodes:
            mc.setAttr('%s.overrideEnabled'%jointNode, True)
            mc.setAttr('%s.overrideDisplayType'%jointNode, 2)
        for n, sectionGuide in enumerate(sectionGuides):
            jointNode = digitJointNodes[n]
            sectionGuideNode = sectionGuide['pivot']
            Nodes.alignObject(sectionGuideNode, jointNode)
            Nodes.setParent(sectionGuideNode, parentGuide)
        for n, sectionGuide in enumerate(sectionGuides):
            jointNode = digitJointNodes[n]
            sectionGuideNode = sectionGuide['pivot']
            if oldLimbRig:
                Nodes.pointConstraint(jointNode, sectionGuideNode)
            else:
                Nodes.delete(sectionGuideNode+'_pointConstraint1')
                Nodes.parentConstraint(sectionGuideNode, jointNode, mo=False)
                Nodes.lockAndHideAttributes(jointNode, t=[True, True, True], r=[True, True, True], s=[True, True, True])

    for jointNode in list(itertools.chain.from_iterable(digitJointNodesList)):
        ConnectionHandling.addOutput(guideGroup, Nodes.replaceNodeType(jointNode, Settings.skinJointSuffix))

def createRig(digits,
                side,
                name,
                limbRig,
                parentJoint=None,
                attrNode=None,
                footRig=None,
                hasKnuckleDeformJoint=True,
                numberedNaming=False,
                digitHasBase=True,
                addDigitAttributes=False,
                skeletonParent=None):
    
    digitsGroup = AddNode.compNode(name, side, element='digits', hasGlobalScale=False)

    if not parentJoint:
        parentJoint = footRig['toesJoint'] if footRig else limbRig['endJoint']
    if not attrNode:
        limbAttrNode = limbRig['attr']['control']

    if hasKnuckleDeformJoint:
        Nodes.addAttrTitle(limbAttrNode, 'knuckles')
        knuckleDeformAttrName = 'knucklePush'
        mc.addAttr(limbAttrNode, at='float', ln=knuckleDeformAttrName, dv=1, hasMinValue=True, minValue=0, keyable=False)
        mc.setAttr(limbAttrNode+'.'+knuckleDeformAttrName, cb=True)

    digitCtrlList = list()
    digitSclCmpList = list()
    digitOffList = list()
    digitCntList = list()
    digitJointNodesList = list()
    
    for g in range(len(digits)):

        digitJointNodesList.append([])

        digitCtrls = list()
        digitSclCmps = list()
        digitOffs = list()
        digitCnts = list()

        if numberedNaming:
            element = 'digit'
            indices = [g, 0]
        else:
            element = ['thumb', 'index', 'middle', 'ring', 'pinky'][g]
            indices = 0

        digitGuide = Nodes.createName(component=name,
                                        side=side, 
                                        nodeType=Settings.guidePivotSuffix,
                                        element=element,
                                        indices=indices)[0]
        
        offset = Guiding.getGuideAttr(digitGuide)['offset']
        shape = Guiding.getGuideAttr(digitGuide)['shape']
        parentNode = Guiding.getGuideAttr(digitGuide)['parentNode']
        
        for s in range(digits[g]+(1 if digitHasBase[g] else 0)):
            
            segIndex = (s-1) if digitHasBase[g] else s
            if numberedNaming:
                indices = [g, segIndex]
            else:
                indices = segIndex

            digitPosGuide = Nodes.createName(component=name,
                                                side=side, 
                                                nodeType=Settings.guidePivotSuffix,
                                                element=element,
                                                indices=indices)[0]
            
            digitRig = Control.createControl(node=digitPosGuide,
                                                component=name,
                                                side=side,
                                                element=element,
                                                indices=indices,
                                                shape=shape,
                                                deleteNode=False,
                                                parentNode=parentNode if s == 0 else None,
                                                offset=offset,
                                                ignoreMissingGuideControlWarning=True)

            cntNode = AddNode.inbetweenNode(digitRig['offset'])

            Nodes.lockAndHideAttributes(digitRig['control'], t=[False, False, False], r=[False, False, False], s=[False, False, False], v=True)
            
            digitCtrls.append(digitRig['control'])
            digitSclCmps.append(digitRig['scaleCompensate'])
            digitOffs.append(digitRig['offset'])
            digitCnts.append(cntNode)

            digitJointNode = AddNode.jointNode(digitRig['scaleCompensate'], 
                                                skeletonParent=skeletonParent if s == 0 else digitJointNodesList[-1][-1], 
                                                convertRotToOrient=True)
            digitJointNodesList[-1].append(digitJointNode)

            VisSwitch.connectVisSwitchGroup([digitJointNode], digitsGroup, displayAttr='jointDisplay')

        digitCtrlList.append(digitCtrls)
        digitSclCmpList.append(digitSclCmps)
        digitOffList.append(digitOffs)
        digitCntList.append(digitCnts)

        for c, zero in enumerate(digitOffs):
            if c > 0:
                Nodes.setParent(zero, digitSclCmps[c-1])

        Tools.parentScaleConstraint(parentJoint, digitOffs[0])

    knuckleJoints = list()

    if hasKnuckleDeformJoint:

        for digitChain in digitJointNodesList:

            for s, digitJoint in enumerate(digitChain):

                if s > 0:

                    knuckleOff = AddNode.emptyNode(node=digitJoint, nodeType=Settings.offNodeSuffix, specific='knuckle')

                    Nodes.setParent(knuckleOff, digitJoint)
                    Nodes.alignObject(knuckleOff, digitJoint)

                    knuckleCnt = AddNode.inbetweenNode(node=knuckleOff, nodeType=Settings.cntNodeSuffix, specific='knuckle')
                    drvNode = AddNode.inbetweenNode(knuckleCnt, nodeType='drv', zeroValues=True)

                    knuckleJoint = AddNode.jointNode(node=drvNode, specific='knuckle', skeletonParent=digitJoint, convertRotToOrient=True)
                    knuckleJoints.append(knuckleJoint)

                    parentSize = Tools.getDistance(digitChain[s-1], digitChain[s])

                    mc.move(0, parentSize * (-0.1 if side == Settings.rightSide else 0.1), 0, knuckleOff, r=True, os=True)
                    mc.delete(mc.orientConstraint([digitChain[s - 1], digitJoint], knuckleOff, mo=False))
                    orientCnt = mc.orientConstraint([digitChain[s - 1], digitJoint], knuckleCnt, mo=False)[0]
                    mc.setAttr('%s.interpType'%orientCnt, 2)

                    mult1Node = Nodes.mulNode(input1='%s.rotateZ' % knuckleCnt, 
                                                input2=-0.01 if side == Settings.rightSide else 0.01, 
                                                output=None, 
                                                specific='conversion')

                    Nodes.mulNode(input1='%s.output' % mult1Node, 
                                    input2='%s.%s' % (limbAttrNode, knuckleDeformAttrName), 
                                    output='%s.translateY' % drvNode, 
                                    specific='attribute')

                    mc.transformLimits(drvNode, ty=(0, 0), ety=(0, 1) if side == Settings.rightSide else (1, 0))

    if addDigitAttributes:

        for axis in 'yzx':

            labelAttrName = 'twist' if axis == 'x' else 'spread' if axis == 'y' else 'roll'
            Nodes.addAttrTitle(limbAttrNode, 'digits'+labelAttrName)

            for digitCnts in digitCntList:

                weightAttrName = (cntNode if side == None else Nodes.replaceNodeType(cntNode, labelAttrName)) + '_weight'
                weightAttr = f'{limbAttrNode}.{weightAttrName}'
                Nodes.addAttr(weightAttr)

                for c, cntNode in enumerate(digitCnts):

                    attrName = (cntNode if side == None else Nodes.replaceNodeType(cntNode, axis))
                    attr = f'{limbAttrNode}.{attrName}'
                    Nodes.addAttr(attr)
                    Nodes.mulNode(
                        f'{limbAttrNode}.{attrName}',
                        weightAttr,
                        f'{cntNode}.r{axis}'
                    )

    mc.parent([x[0] for x in digitOffList], digitsGroup)

    for axis in 'XYZ':
        mc.setAttr('%s.jointOrient%s'%(parentJoint, axis), 0)
    
    [mc.setAttr('%s.segmentScaleCompensate' % x[0], 0) for x in digitJointNodesList + [[parentJoint]]]

    VisSwitch.connectVisSwitchGroup([parentJoint] + knuckleJoints, digitsGroup, displayAttr='jointDisplay')
    VisSwitch.connectVisSwitchGroup([x for y in digitCtrlList for x in y], digitsGroup, displayAttr='controlDisplay', visGroup='arm')

    mc.select(clear=True)

    return {'controls': digitCtrlList,
            'offsets': digitOffList,
            'joints': digitJointNodesList,
            'rigGroup': digitsGroup}