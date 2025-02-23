# Chest

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import Tools
from bear.utilities import SpaceSwitch
from bear.utilities import VisSwitch
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):

    def __init__(self,
                    name='chest',
                    side=None,
                    spaceNodes=[Nodes.createName('root', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('root', element='placement', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('root', element='main', specific='pivot', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('body', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('spine', element='fk', indices=3, indexFill=1, nodeType=Settings.controlSuffix)[0],
                                ],
                    spaceNames=['root', 
                                'placement', 
                                'main',
                                'body',
                                'spine', 
                                ],
                    defaultAlignment='biped',
                    hasBreathControl=False,
                    parentNode=None,
                    skeletonParent=None,
                    displaySwitch='bodyDisplaySwitch',
                    input_spineName='spine',
                    *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.spaceNodes = spaceNodes
        self.spaceNames = spaceNames
        self.defaultSpace = 'spine' if 'spine' in spaceNames else None
        self.defaultAlignment = defaultAlignment
        self.hasBreathControl = hasBreathControl
        self.parentNode = Nodes.getPivotCompensate(parentNode) if parentNode != '' else None
        self.skeletonParent = skeletonParent if skeletonParent != '' else None
        self.displaySwitch = displaySwitch
        self.input_spineName = input_spineName if input_spineName != '' else None

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, self.side, definition)
        if definition:
            return {'guideGroup': guideGroup}

        for n in range(2 if self.hasBreathControl else 1):

            guide = Guide.createGuide(component=self.name, side=self.side, element='breath' if n == 1 else None)
            if self.defaultAlignment == 'biped':
                mc.move(0, 0, [0, 10][n], guide['pivot'])
            if self.defaultAlignment == 'quadruped':
                mc.move(0, [0, -10][n], 0, guide['pivot'])
            mc.parent(guide['pivot'], guideGroup)

            if n == 0:
                mc.setAttr('%s.sy' % guide['control'], 6)
                
                ConnectionHandling.addOutput(guideGroup, Nodes.replaceNodeType(guide['pivot'], Settings.skinJointSuffix))

        return {'guideGroup': guideGroup}

    def createRig(self):

        [ConnectionHandling.inputExists(space) for space in self.spaceNodes]
        ConnectionHandling.inputExists(self.parentNode)
        
        chestGroup = super(Build, self).createRig(self.name, self.side)

        chestGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix)[0]

        chestRig = Control.createControl(node=chestGuide,
                                            rotateOrder='zxy',
                                            parentNode=self.parentNode,
                                            hasRotateOrder=True)

        Nodes.setParent(chestRig['offset'], chestGroup)

        skeletonParent = self.parentNode
        if self.input_spineName and not self.parentNode and not self.skeletonParent:
            spineJointCount = int(mc.getAttr('%s.jointCount'%Nodes.createName(self.input_spineName, self.side, Settings.guideGroup)[0]))
            skeletonParent = Nodes.createName(self.input_spineName, self.side, Settings.skinJointSuffix, indices=spineJointCount-1)[0]
            ConnectionHandling.inputExists(skeletonParent)
        if self.skeletonParent:
            skeletonParent = self.skeletonParent
            
        chestJoint = AddNode.jointNode(chestRig['control'], skeletonParent=skeletonParent)

        Nodes.lockAndHideAttributes(chestRig['control'], t=[False, False, False], r=[False, False, False], s=[True, True, True], v=True)

        if self.hasBreathControl:

            breathGuide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix, 'breath')[0]
            breathRig = Control.createControl(node=breathGuide,
                                                parentNode=chestRig['pivotCompensate'],
                                                parentType='Hierarchy')
            breathJoint = AddNode.jointNode(breathRig['pivotCompensate'], skeletonParent=chestJoint)
        else:
            breathGuide = None
            breathRig = None

        if self.spaceNodes != None:

            SpaceSwitch.createSpaceSwitch(offNode=chestRig['offset'],
                                        sourceObjs=self.spaceNodes[::],
                                        switchNames=self.spaceNames[::],
                                        translation=False,
                                        scale=False,
                                        defaultSpace=self.defaultSpace)

        VisSwitch.connectVisSwitchGroup([chestJoint], chestGroup, displayAttr='jointDisplay')
        VisSwitch.connectVisSwitchGroup([chestRig['control']], chestGroup, displayAttr='controlDisplay')
        if breathGuide != None:
            VisSwitch.connectVisSwitchGroup([breathJoint], chestGroup, displayAttr='jointDisplay')
            VisSwitch.connectVisSwitchGroup([breathRig['control']], chestGroup, displayAttr='breathControlDisplay')

        if self.input_spineName:
            self.connectRig(self.input_spineName, chestRig)

        return {'control': chestRig['control'],
                'offset': chestRig['offset'],
                'joint': chestJoint,
                'breath': breathRig,
                'rigGroup': chestGroup}

    def connectRig(self,
                    spineName,
                    chestRig):
        
        spineEndCurveOffset = Nodes.createName(spineName, side=self.side, element='end', nodeType=Settings.offNodeSuffix)[0]
        spineEndFkControl = Nodes.createName(spineName, side=self.side, indices=3, element='fk', indexFill=1, nodeType=Settings.controlSuffix)[0]

        spineEndCurveOffset = ConnectionHandling.inputExists(spineEndCurveOffset)
        spineEndFkControl = ConnectionHandling.inputExists(spineEndFkControl)

        Tools.parentScaleConstraint(chestRig['pivotCompensate'], spineEndCurveOffset, useMatrix=False)
        Tools.parentScaleConstraint(spineEndFkControl, chestRig['offset'])

        Nodes.addAttrTitle(chestRig['control'], 'stretch')
        chestStretchAttr = chestRig['control']+'.'+spineName+'Stretch'
        Nodes.addAttr(chestStretchAttr, k=False, d=True)
        spineStretchAttr = Nodes.createName(spineName, side=self.side, nodeType='rig')[0]+'.'+spineName+'Stretch'
        if Nodes.exists(spineStretchAttr):
            Nodes.connectAttr(spineStretchAttr, chestStretchAttr, lock=True)