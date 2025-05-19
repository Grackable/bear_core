# Leg

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import AttrConnect
from bear.utilities import Nodes
from bear.components.body import Limb
from bear.components.body import Digits
from bear.components.body import Shoulder
from bear.components.body import Foot
from bear.components.basic import Guide

class Build(Generic.Build):

    def __init__(self,
                    name='leg',
                    side=Settings.leftSide,
                    topName='shoulder',
                    upperName='upper',
                    midName='knee',
                    lowerName='lower',
                    endName='ankle',
                    upnodeName='upnode',
                    digitsName='toes',
                    hasFoot=True,
                    upperTwistCount=5,
                    lowerTwistCount=5,
                    ankleTwistCount=5,
                    digits=None, 
                    digitHasBase=[False, False, False, False, False],
                    digitsNumberedNaming=True,
                    hasTopDeformJoint=True,
                    hasMidDeformJoint=True,
                    hasKnuckleDeformJoint=True,
                    hasStretch=True,
                    hasMidControl=True,
                    hasParentJoint=True,
                    hasSmoothIk=True,
                    hasPlatform=True,
                    spaceNodes=[Nodes.createName('root', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('root', element='placement', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('root', element='main', specific='pivot', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('body', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('body', element='hips', nodeType=Settings.controlSuffix)[0],
                                ],
                    spaceNames=['root',
                                'placement',
                                'main',
                                'body',
                                'hips',
                                ],
                    #reverseSpaces=None,
                    #hasShoulder=False,
                    quadruped=False,
                    invertKnee=False,
                    alignFootIkForward=True,
                    shoulderHasLegInfluence=False,
                    defaultAlignment='biped',
                    parentNode=Nodes.createName('body', element='hips', nodeType=Settings.controlSuffix)[0],
                    displaySwitch='bodyDisplaySwitch',
                    oldLimbRig=False,
                    *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.side = side
        self.name = name
        self.topName = topName
        self.upperName = upperName
        self.midName = midName
        self.lowerName = lowerName
        self.endName = endName
        self.upnodeName = upnodeName
        self.digitsName = digitsName
        self.hasFoot = hasFoot
        self.hasMidDeformJoint = hasMidDeformJoint
        self.hasTopDeformJoint = hasTopDeformJoint
        self.hasKnuckleDeformJoint = hasKnuckleDeformJoint
        self.hasStretch = hasStretch
        self.midControl = hasMidControl
        self.hasParentJoint = hasParentJoint
        self.pinning = hasMidControl
        self.hasSmoothIk = hasSmoothIk
        self.bendy = False
        self.curved = True
        self.upperTwistCount = upperTwistCount
        self.lowerTwistCount = lowerTwistCount
        self.ankleTwistCount = ankleTwistCount
        self.digits = digits
        self.digitHasBase = digitHasBase
        self.digitsNumberedNaming = digitsNumberedNaming
        self.spaceNodes = spaceNodes
        self.spaceNames = spaceNames
        self.defaultSpace = 'main' if 'main' in spaceNames else None
        self.reverseSpaces = None
        self.hasShoulder = True
        self.quadruped = quadruped
        self.hasPlatform = hasPlatform
        self.invertKnee = invertKnee
        self.alignFootIkForward = alignFootIkForward
        self.shoulderHasLegInfluence = shoulderHasLegInfluence
        self.defaultAlignment = defaultAlignment
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.displaySwitch = displaySwitch
        self.oldLimbRig = oldLimbRig

        # pinning, curved, bendy switch are not fully supported, so the flags are set hard and attr are hidden in guide
            
    def createGuide(self, definition=False):

        mirVal = -1 if self.side == Settings.rightSide else 1

        guideGroup = super(Build, self).createGuide(self.name, self.side, definition)
        if definition:
            return {'guideGroup': guideGroup}
        
        jointNodes = list()

        limbNames = [self.upperName, self.lowerName, self.endName]
        if self.hasFoot:
            limbNames.extend([self.digitsName, self.digitsName+'Tip'])

        if self.hasShoulder:

            shoulderGuide = Guide.createGuide(component=self.name,
                                                element=self.topName,
                                                side=self.side,
                                                parentNode=guideGroup)

            if self.defaultAlignment == 'biped':
                tOffset = [0, 70, 0]
            if self.defaultAlignment == 'quadruped':
                tOffset = [0, 80, 0]
            if 'hexapod' in self.defaultAlignment or 'arachnid' in self.defaultAlignment:
                tOffset = [0, 60, 0]

            [mc.setAttr('%s.t%s'%(shoulderGuide['pivot'], axis), tOffset[a]) for a, axis in enumerate('xyz')]
            if self.side == Settings.rightSide:
                mc.rotate(0, 180, 0, shoulderGuide['pivot'], r=True, os=True)

        # guide joints
        for g in range(len(limbNames)):

            jointNode = AddNode.jointNode(component=self.name, side=self.side, element=limbNames[g], nodeType=Settings.guidePivotSuffix)
            jointNodes.append(jointNode)

            tOffset = [g*20*mirVal, 70, 0]

            [mc.setAttr('%s.t%s'%(jointNode, axis), tOffset[a]) for a, axis in enumerate('xyz')]

            if g == 0:
                mc.parent(jointNode, guideGroup)
            else:
                mc.parent(jointNode, jointNodes[-2])

        if self.defaultAlignment == 'biped' or (self.defaultAlignment == 'quadruped' and self.name == 'backLeg'):
            mc.setAttr('%s.jointOrientX'%jointNodes[0], 0 if self.side == Settings.rightSide else 180)
            mc.setAttr('%s.jointOrientZ'%jointNodes[0], 90 if self.side == Settings.rightSide else -90)
            mc.setAttr('%s.rotateY'%jointNodes[0], 10 if self.defaultAlignment == 'biped' else 20)
            mc.setAttr('%s.jointOrientY'%jointNodes[1], -90)
            mc.setAttr('%s.rotateY'%jointNodes[1], 70 if self.defaultAlignment == 'biped' else 40)
            mc.setAttr('%s.rotateY'%jointNodes[2], 60 if self.defaultAlignment == 'biped' else 40)
            if self.hasFoot:
                mc.setAttr('%s.rotateY'%jointNodes[3], 40 if self.defaultAlignment == 'biped' else 40)
        if self.defaultAlignment == 'quadruped' and self.name == 'frontLeg':
            mc.setAttr('%s.jointOrientX'%jointNodes[0], 0 if self.side == Settings.rightSide else 180)
            mc.setAttr('%s.jointOrientZ'%jointNodes[0], 90 if self.side == Settings.rightSide else -90)
            mc.setAttr('%s.rotateY'%jointNodes[0], -20)
            mc.setAttr('%s.jointOrientY'%jointNodes[1], 90)
            mc.setAttr('%s.rotateY'%jointNodes[1], -40)
            mc.setAttr('%s.rotateY'%jointNodes[2], -40)
            if self.hasFoot:
                mc.setAttr('%s.rotateY'%jointNodes[3], 40)
        if 'hexapod' in self.defaultAlignment or 'arachnid' in self.defaultAlignment:
            mc.setAttr('%s.jointOrientX'%jointNodes[0], 0 if self.side == Settings.rightSide else 180)
            mc.setAttr('%s.jointOrientZ'%jointNodes[0], 90 if self.side == Settings.rightSide else -90)
            mc.setAttr('%s.rotateY'%jointNodes[0], 10 if self.defaultAlignment == 'biped' else 20)
            mc.setAttr('%s.jointOrientY'%jointNodes[1], -90)
            mc.setAttr('%s.rotateY'%jointNodes[1], 70 if self.defaultAlignment == 'biped' else 40)
            mc.setAttr('%s.rotateY'%jointNodes[2], 60 if self.defaultAlignment == 'biped' else 40)
            if self.hasFoot:
                mc.setAttr('%s.rotateY'%jointNodes[3], 40 if self.defaultAlignment == 'biped' else 40)
        
        upperLegJoint = jointNodes[0]
        lowerLegJoint = jointNodes[1]
        ankleJoint = jointNodes[2]
        toesJoint = jointNodes[3] if self.hasFoot else None
        toesTipJoint = jointNodes[4] if self.hasFoot else None

        # guide placer
        sectionNames = [self.upperName, self.lowerName, self.endName] 
        if self.hasFoot:
            sectionNames.extend([self.digitsName, self.digitsName+'Tip'])
        sectionGuides = Limb.guidePlacer(guideGroup, 
                                        side=self.side,
                                        sectionNames=sectionNames,
                                        limbType='Leg',
                                        invertKnee=self.invertKnee)
        jointNodes = [upperLegJoint, lowerLegJoint, ankleJoint]
        if self.hasFoot:
            jointNodes.extend([toesJoint, toesTipJoint])
        for jointNode in jointNodes:
            mc.setAttr('%s.overrideEnabled'%jointNode, True)
            mc.setAttr('%s.overrideDisplayType'%jointNode, 2)
        for n, sectionGuide in enumerate(sectionGuides):
            jointNode = jointNodes[n]
            sectionGuideNode = sectionGuide['pivot']
            Nodes.alignObject(sectionGuideNode, jointNode)
        for n, sectionGuide in enumerate(sectionGuides):
            jointNode = jointNodes[n]
            sectionGuideNode = sectionGuide['pivot']
            if self.oldLimbRig:
                Nodes.pointConstraint(jointNode, sectionGuideNode)
            else:
                Nodes.delete(sectionGuideNode+'_pointConstraint1')
                Nodes.parentConstraint(sectionGuideNode, jointNode, mo=False)
                if n == 2 and self.quadruped:
                    aimAxis = '-x' if self.side == Settings.rightSide else 'x'
                    upAxis = 'z' if self.side == Settings.rightSide else '-z'
                    Nodes.lockAndHideAttributes(jointNode, t=[False, False, False], r=[False, False, False], s=[True, True, True])
                    Nodes.delete(sectionGuideNode+'_aimConstraint1')
                    Nodes.delete(jointNode+'_parentConstraint1')
                    aimCnt = Nodes.aimConstraint(
                        sectionGuides[3]['pivot'], 
                        jointNode,
                        aimAxis=aimAxis,
                        upAxis=upAxis,
                        upType='objectrotation')
                    twistAttr = sectionGuides[2]['pivot']+'.twist'
                    mc.connectAttr(twistAttr, '%s.offsetX'%aimCnt)
                    Nodes.pointConstraint(sectionGuideNode, jointNode)
                    Nodes.lockAndHide(sectionGuideNode, trs='r', lock=False)
                    Nodes.setTrs(sectionGuideNode, 0, t=False, s=False)
                    Nodes.lockAndHide(sectionGuideNode, trs='r', lock=True)
                else:
                    Nodes.lockAndHideAttributes(jointNode, t=[True, True, True], r=[True, True, True], s=[True, True, True])
        if self.quadruped:
            upnodeAim, upnodeAimOff, pointCnt = Limb.upnodeGuideSetup(sectionGuides[0]['pivot'], 
                                                                    sectionGuides[1]['pivot'], 
                                                                    sectionGuides[2]['pivot'], 
                                                                    self.name, 
                                                                    self.side, 
                                                                    guideGroup,
                                                                    'guideQuad')
            mc.setAttr('%s.%sW0'%(pointCnt, sectionGuides[0]['pivot']), 0)
            mc.setAttr('%s.%sW1'%(pointCnt, sectionGuides[2]['pivot']), 1)
            Nodes.setParent(sectionGuides[3]['pivot'], upnodeAimOff)
            Nodes.lockAndHideAttributes(sectionGuides[3]['pivot'], t=[False, True, False])
        
        # guide platform
        if self.hasPlatform:
            platformPivotLocList = list()
            for specName in ['front', 'back', 'inner', 'outer', 'frontSpin', 'backSpin']:
                footPivotGuide = Guide.createGuide(component=self.name,
                                                                element='pivot',
                                                                specific=specName,
                                                                side=self.side,
                                                                hasGuideShape=False)['pivot']
                platformPivotLocList.append(footPivotGuide)
            offset = 0
            if self.quadruped:
                offset = 10
                outerVal = 10
                innerVal = 5
            else:
                outerVal = 15
                innerVal = 10
            if self.defaultAlignment == 'quadruped':
                mc.move(0, 0, outerVal+offset, platformPivotLocList[0])
                mc.move(0, 0, -outerVal+offset, platformPivotLocList[1])
                mc.move(-5, 0, offset, platformPivotLocList[2])
                mc.move(5, 0, offset, platformPivotLocList[3])
                mc.move(0, 0, innerVal+offset, platformPivotLocList[4])
                mc.move(0, 0, -innerVal+offset, platformPivotLocList[5])
            else:
                mc.move(0, 0, outerVal+offset, platformPivotLocList[0])
                mc.move(0, 0, -outerVal+offset, platformPivotLocList[1])
                mc.move(-5, 0, offset, platformPivotLocList[2])
                mc.move(5, 0, offset, platformPivotLocList[3])
                mc.move(0, 0, innerVal+offset, platformPivotLocList[4])
                mc.move(0, 0, -innerVal+offset, platformPivotLocList[5])
            if self.side == Settings.rightSide:
                [mc.rotate(180, 0, 0, platformPivotLoc, r=True, os=True) for platformPivotLoc in platformPivotLocList]
            
            mc.parent(platformPivotLocList, guideGroup)
        
        jointNodes = [upperLegJoint, lowerLegJoint, ankleJoint]
        if self.hasFoot:
            jointNodes.append(toesJoint)
        
        for j, jointNode in enumerate(jointNodes):
            
            Nodes.lockAndHideAttributes(jointNode, s=[True, True, True])
            Nodes.lockAndHideAttributes(jointNode, t=[True, True, True], r=[True, True, True], lock=False)

            guide = Guide.createGuide(node=jointNode,
                                                side=self.side,
                                                alignAxis='X',
                                                hasAttrs=True,
                                                hasGuidePivot=False)

            if jointNode == ankleJoint:
                mc.addAttr(guide['control'], at='enum', ln='ikTargetShape', k=True, enumName=':'+':'.join(Settings.shapes),
                                                dv=Settings.shapes.index('Quadruped Leg IK' if self.quadruped else 'Biped Leg IK'))
                mc.addAttr(guide['control'], at='enum', ln='ikTargetColor', k=True, enumName=':'+':'.join(['Default']+Settings.colors))
                mc.addAttr(guide['control'], at='float', ln='ikTargetOvershootSize', k=True, dv=0.1)
                mc.addAttr(guide['control'], at='float', ln='ikTargetLiftoff', k=True, dv=0.1)
                mc.setAttr('%s.hasPivotControl'%guide['control'], True)

                if not self.hasShoulder:
                    mc.addAttr(guide['control'], at='enum', ln='legParentShape', k=True, enumName=':'+':'.join(Settings.shapes), dv=Settings.shapes.index('Rectangle'))
                    mc.addAttr(guide['control'], at='enum', ln='legParentColor', k=True, enumName=':'+':'.join(['Default']+Settings.colors))
                    mc.addAttr(guide['control'], at='float', ln='legParentOffset', k=True, dv=1)
                    mc.addAttr(guide['control'], at='float', ln='legParentSize', k=True, dv=1)

        if self.digits != None:
            Digits.createGuide(self.digits, 
                                self.name, 
                                self.side, 
                                self.digitHasBase, 
                                guideGroup, 
                                limbType='leg',
                                numberedNaming=self.digitsNumberedNaming,
                                oldLimbRig=self.oldLimbRig)

        # outputs
        for jointNode in [ankleJoint, toesJoint]:
            if jointNode:
                ConnectionHandling.addOutput(guideGroup, jointNode)
        jointNodes = [upperLegJoint, lowerLegJoint]
        twistCounts = [self.upperTwistCount, self.lowerTwistCount]
        if self.hasShoulder:
            ConnectionHandling.addOutput(guideGroup, shoulderGuide['pivot'])
        if self.quadruped:
            jointNodes.append(ankleJoint)
            twistCounts.append(self.ankleTwistCount)
        for j, jointNode in enumerate(jointNodes):
            for c in range(twistCounts[j]):
                ConnectionHandling.addOutput(guideGroup, Nodes.createName(sourceNode=jointNode, indices=c, nodeType=Settings.skinJointSuffix)[0])
        ConnectionHandling.addOutput(guideGroup, Nodes.replaceNodeType(guideGroup), attrName=Nodes.replaceNodeType(guideGroup, 'component'))
        ConnectionHandling.addOutput(guideGroup, Nodes.createName(component=self.name, side=self.side, element='parent', nodeType=Settings.locNodeSuffix)[0])
        ConnectionHandling.addOutput(guideGroup, upperLegJoint)
        ConnectionHandling.addOutput(guideGroup, lowerLegJoint)
                            
        return {'guideGroup': guideGroup}

    def createRig(self):
        
        self.parentNode = ConnectionHandling.inputExists(self.parentNode)

        if self.hasShoulder:
            shoulderGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix, self.topName)[0]
        upperLegGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix, self.upperName)[0]
        lowerLegGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix, self.lowerName)[0]
        ankleGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix, self.endName)[0]
        toesGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix, self.digitsName)[0]
        upnodeGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix, self.upnodeName)[0]
        
        platformPivotGuides = list()
        if self.hasPlatform:
            for specName in ['front', 'back', 'inner', 'outer', 'frontSpin', 'backSpin']:
                platformPivotGuides.append(Nodes.createName(component=self.name,
                                                    element='pivot',
                                                    specific=specName,
                                                    side=self.side, 
                                                    nodeType=Settings.guidePivotSuffix)[0])
        
        limbType = 'leg'

        limbRig = Limb.createRig(upperLimbGuide=upperLegGuide,
                                    lowerLimbGuide=lowerLegGuide,
                                    endGuide=ankleGuide,
                                    quadrupedGuide=toesGuide,
                                    upnodeGuide=upnodeGuide,
                                    midName=self.midName,
                                    digitsName=self.digitsName,
                                    side=self.side,
                                    name=self.name,
                                    limbType=limbType,
                                    hasMidDeformJoint=self.hasMidDeformJoint,
                                    hasStretch=self.hasStretch,
                                    pinning=self.pinning,
                                    smoothIk=self.hasSmoothIk,
                                    midControl=self.midControl,
                                    bendy=self.bendy,
                                    curved=self.curved,
                                    quadruped=self.quadruped,
                                    hasShoulder=self.hasShoulder,
                                    alignFootIkForward=self.alignFootIkForward,
                                    platformPivotGuides=platformPivotGuides,
                                    defaultSpace=self.defaultSpace,
                                    parentNode=None if self.hasShoulder else self.parentNode,
                                    skeletonParent=Nodes.createName(self.name, self.side, Settings.skinJointSuffix, self.topName)[0] \
                                        if self.hasShoulder and self.hasParentJoint else self.parentNode)

        if self.hasShoulder:
            shoulderRig = Shoulder.createRig(shoulderGuide=shoulderGuide,
                                                side=self.side,
                                                name=self.name,
                                                hasTopDeformJoint=self.hasTopDeformJoint,
                                                hasJoint=self.hasParentJoint,
                                                limbRig=limbRig,
                                                shoulderName=self.topName,
                                                parentNode=self.parentNode)
            
            mc.parent(shoulderRig['rigGroup'], limbRig['rigGroup'])
            AttrConnect.multiGroupConnect([shoulderRig['rigGroup']], limbRig['rigGroup'])

            # shoulder influence attributes
            if self.shoulderHasLegInfluence:
                # aim constraint
                aimNode = AddNode.childNode(shoulderRig['mirrorScale'], 'aim', zeroValues=True)
                aimResultNode = AddNode.parentNode(shoulderRig['control'], 'aimResult', zeroValues=True)
                
                Nodes.aimConstraint(limbRig['ik']['control'],
                                    aimNode,
                                    upNode=shoulderRig['mirrorScale'],
                                    aimAxis='-y' if self.side == Settings.rightSide else 'y',
                                    upAxis='z',
                                    mo=True)
                Tools.blendBetween([shoulderRig['mirrorScale']],
                                [aimNode],
                                [aimResultNode],
                                attrNode=shoulderRig['control'],
                                attrName='ikFollow',
                                attrTitle='%sInfluenceAttributes'%limbType,
                                orientConstrained=True)
                
                # ik lift influence
                liftNode = AddNode.childNode(shoulderRig['mirrorScale'], 'lift', zeroValues=True)
                liftResultNode = AddNode.parentNode(shoulderRig['mirrorScale'], 'liftResult', zeroValues=True)
                mc.pointConstraint(limbRig['ik']['control'], liftNode, skip=['x'])
                initLift = mc.getAttr('%s.ty'%liftNode)
                initPush = mc.getAttr('%s.tx'%liftNode)
                liftAttr = '%s.ikLift'%shoulderRig['control']
                pushAttr = '%s.ikPush'%shoulderRig['control']
                Nodes.addAttr(liftAttr, minVal=0)
                Nodes.addAttr(pushAttr, minVal=0)
                addNode = Nodes.addNode('%s.ty'%liftNode,
                                        -initLift)
                mulNode = Nodes.mulNode('%s.output'%addNode,
                            0.1*(-1 if self.side == Settings.rightSide else 1))
                Nodes.mulNode('%s.output'%mulNode,
                            liftAttr,
                            '%s.ty'%liftResultNode)
                addNode = Nodes.addNode('%s.tz'%liftNode,
                                        -initPush)
                mulNode = Nodes.mulNode('%s.output'%addNode,
                            0.1*(-1 if self.side == Settings.rightSide else 1))
                Nodes.mulNode('%s.output'%mulNode,
                            pushAttr,
                            '%s.tz'%liftResultNode)
        else:
            shoulderRig = None

        if self.hasFoot:
            
            footRig = Foot.createRig(platformPivotGuides=platformPivotGuides,
                                            upperLimbGuide=upperLegGuide,
                                            lowerLimbGuide=lowerLegGuide,
                                            ankleGuide=ankleGuide,
                                            toesGuide=toesGuide,
                                            upnodeGuide=upnodeGuide,
                                            side=self.side,
                                            name=self.name,
                                            limbRig=limbRig,
                                            shoulderRig=shoulderRig,
                                            quadruped=self.quadruped,
                                            hasPlatform=self.hasPlatform,
                                            invertKnee=self.invertKnee)

            mc.parent(footRig['rigGroup'], limbRig['rigGroup'])
            AttrConnect.multiGroupConnect([footRig['rigGroup']], limbRig['rigGroup'])

        else:
            mc.parent(limbRig['blendJoints'][2], limbRig['rigGroup'])
            Tools.parentScaleConstraint(limbRig['ik']['control'], limbRig['ikHandle'])
            footRig = None

        if self.digits != None:
            toesRig = Digits.createRig(digits=self.digits,
                                            side=self.side,
                                            name=self.name,
                                            limbRig=limbRig,
                                            footRig=footRig if self.hasFoot else None,
                                            hasKnuckleDeformJoint=self.hasKnuckleDeformJoint,
                                            digitHasBase=self.digitHasBase,
                                            numberedNaming=self.digitsNumberedNaming,
                                            skeletonParent=footRig['toesJoint'])
            
            mc.parent(toesRig['rigGroup'], limbRig['rigGroup'])
            AttrConnect.multiGroupConnect([toesRig['rigGroup']], limbRig['rigGroup'])
        else:
            toesRig=None
        
        mc.select(clear=True)

        return {'limb': limbRig,
                'foot': footRig,
                'toes': toesRig,
                'shoulder': shoulderRig,
                'rigGroup': limbRig['rigGroup']}
