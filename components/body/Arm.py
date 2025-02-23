# Arm

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import Nodes
from bear.utilities import AddNode
from bear.utilities import AttrConnect
from bear.components.body import Limb
from bear.components.body import Digits
from bear.components.body import Shoulder
from bear.components.basic import Guide

class Build(Generic.Build):

    def __init__(self,
                    name='arm',
                    side=Settings.leftSide,
                    topName='shoulder',
                    upperName='upper',
                    midName='elbow',
                    lowerName='lower',
                    endName='wrist',
                    upnodeName='upnode',
                    #hasShoulder=True,
                    upperTwistCount=5,
                    lowerTwistCount=5,
                    digits=[2, 3, 3, 3, 3], 
                    digitHasBase=[True, True, True, True, True],
                    digitsNumberedNaming=False,
                    hasTopDeformJoint=True,
                    hasMidDeformJoint=True,
                    hasKnuckleDeformJoint=True,
                    hasStretch=True,
                    hasMidControl=True,
                    hasSmoothIk=True,
                    parentNode=Nodes.createName('chest', nodeType=Settings.controlSuffix)[0],
                    spaceNodes=[Nodes.createName('root', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('root', element='placement', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('root', element='main', specific='pivot', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('body', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('body', element='hips', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('chest', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('head', nodeType=Settings.controlSuffix)[0],
                                ],
                    spaceNames=['root', 
                                'placement', 
                                'main',
                                'body', 
                                'hips', 
                                'chest', 
                                'head',
                                ],
                    #reverseSpaces=Nodes.createName('prop', nodeType=Settings.controlSuffix)[0],
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
        self.hasShoulder = True
        self.hasMidDeformJoint = hasMidDeformJoint
        self.hasTopDeformJoint = hasTopDeformJoint
        self.hasKnuckleDeformJoint = hasKnuckleDeformJoint
        self.hasStretch = hasStretch
        self.midControl = hasMidControl
        self.pinning = hasMidControl
        self.hasSmoothIk = hasSmoothIk
        self.bendy = False
        self.curved = True
        self.upperTwistCount = upperTwistCount
        self.lowerTwistCount = lowerTwistCount
        self.digits = digits
        self.digitHasBase = digitHasBase
        self.digitsNumberedNaming = digitsNumberedNaming
        self.spaceNodes = spaceNodes
        self.spaceNames = spaceNames
        self.defaultSpace = 'main' if 'main' in spaceNames else None
        self.reverseSpaces = None
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
        jointNames = [self.upperName, self.lowerName, self.endName, self.endName+'Tip']

        if self.hasShoulder:

            shoulderGuide = Guide.createGuide(component=self.name,
                                                side=self.side,
                                                element=self.topName,
                                                parentNode=guideGroup,
                                                alignAxis='X')
            
            if self.side == Settings.rightSide:
                mc.move(-10, 0, 0, shoulderGuide['pivot'], r=True, os=True)
                mc.rotate(0, 180, 0, shoulderGuide['pivot'], r=True, os=True)
            else:
                mc.move(-10, 0, 0, shoulderGuide['pivot'], r=True, os=True)
        
        for g in range(len(jointNames)):
            jointNode = AddNode.jointNode(component=self.name, side=self.side, element=jointNames[g], nodeType=Settings.guidePivotSuffix)
            jointNodes.append(jointNode)
            if g == 0:
                mc.parent(jointNode, guideGroup)
            else:
                mc.parent(jointNode, jointNodes[-2])
            mc.move((g*20)*mirVal, 0, 0, jointNode, r=True, os=True)

        mc.setAttr('%s.rotateY'%jointNodes[0], 10)
        mc.setAttr('%s.jointOrientX'%jointNodes[0], 180 if self.side == Settings.rightSide else 0)

        mc.setAttr('%s.jointOrientY'%jointNodes[1], -90)
        mc.setAttr('%s.rotateY'%jointNodes[1], 70)

        mc.setAttr('%s.rotateY'%jointNodes[2], 10)
            
        for j, jointNode in enumerate(jointNodes[:-1]):

            Nodes.lockAndHideAttributes(jointNode, s=[True, True, True])

            guide = Guide.createGuide(node=jointNode,
                                            side=self.side,
                                            alignAxis='X',
                                            hasAttrs=True,
                                            hasGuidePivot=False)

            if j == 1:
                mc.transformLimits(jointNode, ry=(-89.999, 89.999), ery=(1, 1))

            if j == 2:
                mc.addAttr(guide['control'], at='enum', ln='ikTargetShape', k=True, enumName=':'+':'.join(Settings.shapes))
                mc.addAttr(guide['control'], at='enum', ln='ikTargetColor', k=True, enumName=':'+':'.join(['Default']+Settings.colors))
                mc.addAttr(guide['control'], at='float', ln='knuckleDeformFactor', k=True, dv=0.1)
                mc.setAttr('%s.hasPivotControl'%guide['control'], True)

                if not self.hasShoulder:
                    mc.addAttr(guide['control'], at='enum', ln='armParentShape', k=True, enumName=':'+':'.join(Settings.shapes), dv=Settings.shapes.index('Rectangle'))
                    mc.addAttr(guide['control'], at='enum', ln='armParentColor', k=True, enumName=':'+':'.join(['Default']+Settings.colors))
                    mc.addAttr(guide['control'], at='float', ln='armParentOffset', k=True, dv=1)
                    mc.addAttr(guide['control'], at='float', ln='armParentSize', k=True, dv=1) 
        

        # guide placer
        sectionGuides = Limb.guidePlacer(guideGroup, 
                                        side=self.side,
                                        sectionNames=[self.upperName, self.lowerName, self.endName, self.endName+'Tip'],
                                        limbType='Arm')
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
                Nodes.lockAndHideAttributes(jointNode, t=[True, True, True], r=[True, True, True], s=[True, True, True])

        if self.digits != None:
            Digits.createGuide(self.digits, 
                                self.name, 
                                self.side, 
                                self.digitHasBase, 
                                guideGroup,
                                numberedNaming=self.digitsNumberedNaming,
                                oldLimbRig=self.oldLimbRig)

        # outputs
        ConnectionHandling.addOutput(guideGroup, Nodes.replaceNodeType(jointNodes[2], Settings.skinJointSuffix))
        if self.hasShoulder:
            ConnectionHandling.addOutput(guideGroup, Nodes.replaceNodeType(shoulderGuide['pivot'], Settings.skinJointSuffix))
        for j, jointNode in enumerate(jointNodes[:2]):
            for c in range([self.upperTwistCount, self.lowerTwistCount][j]):
                ConnectionHandling.addOutput(guideGroup, Nodes.createName(sourceNode=jointNode, indices=c, nodeType=Settings.skinJointSuffix)[0])
        ConnectionHandling.addOutput(guideGroup, Nodes.replaceNodeType(guideGroup), attrName=Nodes.replaceNodeType(guideGroup, 'component'))

        return {'guideGroup': guideGroup}

    def createRig(self):
        
        self.parentNode = ConnectionHandling.inputExists(self.parentNode)

        if self.hasShoulder:
            shoulderGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix, self.topName)[0]
        upperArmGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix, self.upperName)[0]
        lowerArmGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix, self.lowerName)[0]
        wristGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix, self.endName)[0]
        upnodeGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix, self.upnodeName)[0]
        
        limbType = 'arm'

        limbRig = Limb.createRig(upperLimbGuide=upperArmGuide,
                                    lowerLimbGuide=lowerArmGuide,
                                    endGuide=wristGuide,
                                    upnodeGuide=upnodeGuide,
                                    midName=self.midName,
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
                                    hasShoulder=self.hasShoulder,
                                    defaultSpace=self.defaultSpace,
                                    parentNode=None if self.hasShoulder else self.parentNode,
                                    skeletonParent=Nodes.createName(self.name, self.side, Settings.skinJointSuffix, self.topName)[0] \
                                        if self.hasShoulder else self.parentNode)
        
        if self.hasShoulder:
            shoulderRig = Shoulder.createRig(shoulderGuide=shoulderGuide,
                                                side=self.side,
                                                name=self.name,
                                                hasTopDeformJoint=self.hasTopDeformJoint,
                                                limbRig=limbRig,
                                                shoulderName=self.topName,
                                                parentNode=self.parentNode)
            
            mc.parent(shoulderRig['rigGroup'], limbRig['rigGroup'])
            AttrConnect.multiGroupConnect([shoulderRig['rigGroup']], limbRig['rigGroup'])
        else:
            shoulderRig = None
        
        if self.digits:
            handRig = Digits.createRig(digits=self.digits,
                                        side=self.side,
                                        name=self.name,
                                        limbRig=limbRig,
                                        hasKnuckleDeformJoint=self.hasKnuckleDeformJoint,
                                        numberedNaming=self.digitsNumberedNaming,
                                        digitHasBase=self.digitHasBase,
                                        skeletonParent=limbRig['endJoint'])          
                                              
            mc.parent(handRig['rigGroup'], limbRig['rigGroup'])
            AttrConnect.multiGroupConnect([handRig['rigGroup']], limbRig['rigGroup'])
        else:
            handRig = None
        
        mc.select(clear=True)

        return {'limb': limbRig,
                'hand': handRig,
                'shoulder': shoulderRig,
                'rigGroup': limbRig['rigGroup']}
