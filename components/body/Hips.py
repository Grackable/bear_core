# Hips

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import VisSwitch
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):

    def __init__(self,
                    name='body',
                    side=None,
                    displaySwitch='bodyDisplaySwitch',
                    input_spineName='spine',
                    *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.displaySwitch = displaySwitch
        self.input_spineName = input_spineName if input_spineName != '' else None

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, self.side, definition)
        if definition:
            return {'guideGroup': guideGroup}

        for elementName in [None, 'hips']:
            guide = Guide.createGuide(component=self.name, side=self.side, element=elementName)
            mc.setAttr('%s.sy' % guide['control'], 0.1 if not elementName else -3)
            mc.setAttr('%s.hasPivotControl'%guide['control'], elementName == None)
            if not elementName:
                mc.setAttr('%s.color'%guide['control'], Settings.colors.index('Green'))

            mc.parent(guide['pivot'], guideGroup)

            ConnectionHandling.addOutput(guideGroup, Nodes.replaceNodeType(guide['pivot'], Settings.skinJointSuffix))
        
        return {'guideGroup': guideGroup}

    def createRig(self):

        hipsGroup = super(Build, self).createRig(self.name, self.side)

        bodyGuide = Nodes.createName(component=self.name, side=self.side, nodeType=Settings.guidePivotSuffix)[0]
        hipsGuide = Nodes.createName(component=self.name, side=self.side, element='hips', nodeType=Settings.guidePivotSuffix)[0]

        hipsJoint = AddNode.jointNode(component=self.name, side=self.side, element='hips', skeletonParent='root')
        Nodes.alignObject(hipsJoint, hipsGuide)

        bodyRig = Control.createControl(node=bodyGuide,
                                        rotateOrder='zxy',
                                        parentNode=None,
                                        deleteNode=False,
                                        hasRotateOrder=True)

        Nodes.alignObject(bodyRig['offset'], bodyGuide, rotation=False)

        Nodes.lockAndHideAttributes(bodyRig['control'], t=[False, False, False], r=[False, False, False], s=[True, True, True], v=True)

        hipsRig = Control.createControl(node=hipsGuide,
                                        rotateOrder='zxy',
                                        parentNode=None,
                                        deleteNode=False,
                                        hasRotateOrder=True)
        
        Nodes.alignObject(hipsRig['offset'], hipsGuide, rotation=False)
        Nodes.lockAndHideAttributes(hipsRig['control'], t=[False, False, False], r=[False, False, False], s=[True, True, True], v=True)

        Nodes.setParent(hipsJoint, hipsRig['control'])

        mc.parent(hipsRig['offset'], bodyRig['pivotCompensate'])
        mc.parent(bodyRig['offset'], hipsGroup)
        
        VisSwitch.connectVisSwitchGroup([hipsJoint], hipsGroup, displayAttr='jointDisplay')
        VisSwitch.connectVisSwitchGroup([hipsRig['control']], hipsGroup, displayAttr='hipsControlDisplay')
        VisSwitch.connectVisSwitchGroup([bodyRig['control']], hipsGroup, displayAttr='bodyControlDisplay')

        if self.input_spineName:
            self.connectRig(self.input_spineName, hipsRig, bodyRig)

        return {'hipsJoint': hipsJoint,
                'body': bodyRig,
                'hips': hipsRig,
                'rigGroup': hipsGroup}

    def connectRig(self,
                    spineName,
                    hipsRig,
                    bodyRig):

        spineLowerParent = Nodes.createName(spineName, side=self.side, element='lower', nodeType='parent')[0]
        spineMainParent = Nodes.createName(spineName, side=self.side, element='main', nodeType='parent')[0]
        spineRevFkEndControl = Nodes.createName(spineName, side=self.side, indices=3, indexFill=1, element='revFk', nodeType=Settings.controlSuffix)[0]

        spineLowerParent = ConnectionHandling.inputExists(spineLowerParent)
        spineMainParent = ConnectionHandling.inputExists(spineMainParent)
        spineRevFkEndControl = ConnectionHandling.inputExists(spineRevFkEndControl)

        spineLowerParentConstraint = spineLowerParent+'_parentConstraint1'
        if mc.objExists(spineLowerParentConstraint):
            mc.delete(spineLowerParentConstraint)
        Tools.parentScaleConstraint(hipsRig['pivotCompensate'], spineLowerParent)
        Tools.parentScaleConstraint(bodyRig['pivotCompensate'], spineMainParent)

        if mc.objExists(spineRevFkEndControl):
            Tools.parentScaleConstraint(spineRevFkEndControl, hipsRig['offset'])
        else:
            Tools.parentScaleConstraint(bodyRig['control'], hipsRig['offset'])

        Nodes.addAttrTitle(hipsRig['control'], 'stretch')
        hipsStretchAttr = hipsRig['control']+'.'+spineName+'Stretch'
        Nodes.addAttr(hipsStretchAttr, k=False, d=True)
        spineStretchAttr = Nodes.createName(spineName, side=self.side, nodeType='rig')[0]+'.'+spineName+'Stretch'
        if Nodes.exists(spineStretchAttr):
            Nodes.connectAttr(spineStretchAttr, hipsStretchAttr, lock=True)