# Teeth

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.system import Guiding
from bear.utilities import VisSwitch
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):

    def __init__(self,
                name='teeth',
                upperParent=Nodes.createName('head', nodeType=Settings.controlSuffix)[0],
                lowerParent=Nodes.createName('mouth', element='jaw', nodeType=Settings.controlSuffix)[0],
                hasExtraControls=True,
                input_mouthName='mouth',
                displaySwitch='faceDisplaySwitch',
                *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.upperParent = upperParent
        self.lowerParent = lowerParent
        self.hasExtraControls = hasExtraControls
        self.input_mouthName = input_mouthName if input_mouthName != '' else None
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, 'auto', definition)
        if definition:
            return {'guideGroup': guideGroup}

        elementNames = ['upperMain', 
                        'upperMid', 
                        'upper', 
                        'lowerMain', 
                        'lowerMid', 
                        'lower']

        for n, elementName in enumerate(elementNames):

            if n != 0 and n != 3 and not self.hasExtraControls:
                continue
            
            guide = Guide.createGuide(component=self.name,
                                        element=elementName,
                                        side=Settings.leftSide if n == 2 or n == 5 else None,
                                        size=1)
            
            mc.parent(guide['pivot'], guideGroup)

            positions = [(0, 2, 0),
                            (0, 2, 2),
                            (5, 2, 0),
                            (0, -2, 0),
                            (0, -2, 2),
                            (5, -2, 0)]
            mc.move(positions[n][0], positions[n][1], positions[n][2], guide['pivot'])

        return {'guideGroup': guideGroup}

    def createRig(self):

        self.upperParent = ConnectionHandling.inputExists(self.upperParent)
        self.lowerParent = ConnectionHandling.inputExists(self.lowerParent)

        upperTeethMainGuide = Nodes.createName(self.name, element='upperMain', nodeType=Settings.guidePivotSuffix)[0]
        upperTeethSideGuide = Nodes.createName(self.name, side=Settings.leftSide, element='upper', nodeType=Settings.guidePivotSuffix)[0]
        lowerTeethMainGuide = Nodes.createName(self.name, element='lowerMain', nodeType=Settings.guidePivotSuffix)[0]
        lowerTeethSideGuide = Nodes.createName(self.name, side=Settings.leftSide, element='lower', nodeType=Settings.guidePivotSuffix)[0]
        upperTeethMidGuide = Nodes.createName(self.name, element='upperMid', nodeType=Settings.guidePivotSuffix)[0]
        lowerTeethMidGuide = Nodes.createName(self.name, element='lowerMid', nodeType=Settings.guidePivotSuffix)[0]
        
        rigGroup = super(Build, self).createRig(self.name, 'auto')
        controlGroup = AddNode.emptyNode(component=self.name, nodeType='controls')
        mc.parent(controlGroup, rigGroup)
        
        guideList = [upperTeethMainGuide, upperTeethSideGuide, lowerTeethMainGuide, lowerTeethSideGuide, upperTeethMidGuide, lowerTeethMidGuide]
        
        jointNodeList = list()

        def createTeethControl(guide, side):

            teethRig = Control.createControl(node=guide, side=side)

            if self.hasExtraControls and not 'Main' in guide:
                jointNode = AddNode.jointNode(teethRig['control'], 
                                            size=0.5, 
                                            nodeType=Settings.skinJointSuffix,
                                            skeletonParent=self.upperParent if 'upper' in guide else self.lowerParent)
                jointNodeList.append(jointNode)
            mc.parent(teethRig['offset'], controlGroup)

            return teethRig

        teethRigList = list()

        for g, guide in enumerate(guideList):
            
            if g == 0 or g == 2 or (g > 3 and self.hasExtraControls):
                teethRig = createTeethControl(guide, None)
                teethRigList.append(teethRig)

            if self.hasExtraControls:
                if g == 1 or g == 3:
                    for side in [Settings.leftSide, Settings.rightSide]:
                        if side == Settings.rightSide:
                            guide = Guiding.convertGuide(guide, mirror=True)[0]
                        teethRig = createTeethControl(guide, side)
                        teethRigList.append(teethRig)

        if self.hasExtraControls:
            mc.parent(teethRigList[1]['offset'], teethRigList[0]['control'])
            mc.parent(teethRigList[2]['offset'], teethRigList[0]['control'])
            mc.parent(teethRigList[4]['offset'], teethRigList[3]['control'])
            mc.parent(teethRigList[5]['offset'], teethRigList[3]['control'])
            mc.parent(teethRigList[6]['offset'], teethRigList[0]['control'])
            mc.parent(teethRigList[7]['offset'], teethRigList[3]['control'])

        teethMainUpper = teethRigList[0]
        teethMainLower = teethRigList[3 if self.hasExtraControls else 1]

        teethUpperSideRigs = [teethRigList[1]['offset'], teethRigList[2]['offset']]
        teethLowerSideRigs = [teethRigList[4]['offset'], teethRigList[5]['offset']]

        if self.upperParent != None:
            Tools.parentScaleConstraint(self.upperParent, teethMainUpper['offset'], inbetweenObject=True, useMatrix=False)
        if self.lowerParent != None:
            Tools.parentScaleConstraint(self.lowerParent, teethMainLower['offset'], inbetweenObject=True, useMatrix=False)

        VisSwitch.connectVisSwitchGroup(jointNodeList, rigGroup, displayAttr='jointDisplay')
        VisSwitch.connectVisSwitchGroup([x['control'] for x in teethRigList], rigGroup, displayAttr='controlDisplay')
        
        self.cleanup(Nodes.replaceNodeType(rigGroup, 'guide'), trashGuides=True, removeRightGuides=True, hierarchy=False, display=False, selectionSets=False)

        if self.input_mouthName:
            self.connectRig(self.input_mouthName, teethMainUpper, teethMainLower, teethUpperSideRigs, teethLowerSideRigs)

        return {'rigGroup': rigGroup, 
                'joints': jointNodeList}

    def connectRig(self, mouthName, teethMainUpper, teethMainLower, teethUpperSideRigs, teethLowerSideRigs):
        
        return # NOTE no follow lips in use
    
        for t, teethMain in enumerate([teethMainUpper, teethMainLower]):

            parentNode = Nodes.getPivotCompensate([self.upperParent, self.lowerParent][t])

            Nodes.addAttrTitle(teethMain['control'], 'followAttributes')
            followAttr = teethMain['control']+'.followLips'
            Nodes.addAttr(followAttr, minVal=0, maxVal=1)

            for s, side in enumerate([Settings.leftSide, Settings.rightSide]):
                
                mouthCornerControl = Nodes.createName(mouthName, side, element='lipcorner', nodeType=Settings.scaleCompensateNode)[0]
                ConnectionHandling.inputExists(mouthCornerControl)
                teethNode = [teethUpperSideRigs, teethLowerSideRigs][t][s]
                followNode = AddNode.inbetweenNode(Nodes.replaceNodeType(teethNode, Settings.offNodeSuffix), 'followLips', lockScale=True)
                Tools.blendBetween([parentNode],
                                    [mouthCornerControl],
                                    [followNode],
                                    attrNode=teethNode,
                                    attrName='followLips',
                                    attrIsKeyable=False,
                                    attrIsVisible=False,
                                    scaleConstrained=False)

                mc.connectAttr(followAttr, teethNode+'.followLips')