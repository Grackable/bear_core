# Steering

import maya.cmds as mc
from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import Nodes
from bear.utilities import VisSwitch
from bear.utilities import AddNode
from bear.utilities import Tools
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):
    
    def __init__(self,
                    name='steering',
                    side=None,
                    hasFrontSteering=True,
                    hasBackSteering=False,
                    frontWheels=[Nodes.createName('wheelFront', side=Settings.leftSide, nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('wheelFront', side=Settings.rightSide, nodeType=Settings.controlSuffix)[0]],
                    backWheels=[Nodes.createName('wheelBack', side=Settings.leftSide, nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('wheelBack', side=Settings.rightSide, nodeType=Settings.controlSuffix)[0]],
                    steeringAxis='y',
                    wheelTurnAxis='y',
                    parentNode=None,
                    hasJoint=True,
                    displaySwitch='displaySwitch',
                    *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.hasFrontSteering = hasFrontSteering
        self.hasBackSteering = hasBackSteering
        self.frontWheels = frontWheels
        self.backWheels = backWheels
        self.steeringAxis = steeringAxis.lower()
        self.wheelTurnAxis = wheelTurnAxis.lower()
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.hasJoint = hasJoint
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, self.side, definition)
        if definition:
            return {'guideGroup': guideGroup}
        
        guide = Guide.createGuide(component=self.name,
                                    side=self.side)
        mc.parent(guide['pivot'], guideGroup)

        return {'guideGroup': guideGroup}

    def createRig(self):

        rigGroup = super(Build, self).createRig(self.name, self.side)
            
        self.steeringRig = Control.createControl(component=self.name, 
                                            side=self.side, 
                                            parentNode=self.parentNode, 
                                            rigGroup=rigGroup)

        if self.hasJoint:
            jointNode = AddNode.jointNode(self.steeringRig['pivotCompensate'], 
                                            specific='remove', 
                                            resetTransforms=True, 
                                            skeletonParent=self.parentNode)
        else:
            jointNode = None

        self.steeringSetup(self.frontWheels if self.hasFrontSteering else None, self.backWheels if self.hasBackSteering else None)

        VisSwitch.connectVisSwitchGroup([self.steeringRig['control']], rigGroup, displayAttr='controlDisplay')
        if self.hasJoint:
            VisSwitch.connectVisSwitchGroup([jointNode], rigGroup, displayAttr='jointDisplay')

        return {'rigGroup': rigGroup, 
                'control': self.steeringRig['pivotCompensate'], 
                'offsets': self.steeringRig['offset'], 
                'joint': jointNode}

    def steeringSetup(self, 
                        frontWheels, 
                        backWheels):

        Nodes.lockAndHideAttributes(self.steeringRig['control'], 
                                    t=[True, True, True], 
                                    r=[self.steeringAxis!='x', self.steeringAxis!='y', self.steeringAxis!='z'], 
                                    s=[True, True, True])
        Tools.createTransformLimits(self.steeringRig['control'], trs='r', axis=self.steeringAxis, dv=60)
        Nodes.addAttrTitle(self.steeringRig['control'], 'Steering')

        for wheelRigs in [frontWheels, backWheels]:
            if not wheelRigs:
                continue
            attr = self.steeringRig['control']+'.%s'%('frontWheelMultiplier' if wheelRigs == frontWheels else 'backWheelMultiplier')
            Nodes.addAttr(attr, dv=0.5 if wheelRigs == frontWheels else 0, k=False, d=True)
            for wheelRig in wheelRigs:
                steeringNode = Nodes.replaceNodeType(wheelRig, 'steering')
                if Nodes.getSide(wheelRig) == Settings.rightSide:
                    negNode = Nodes.mulNode(input1=attr,
                                            input2=-1,
                                            specific='wheelNeg')
                    input1Attr = '%s.output'%negNode
                else:
                    input1Attr = attr
                Nodes.mulNode(input1=input1Attr, 
                                input2='%s.r%s'%(self.steeringRig['control'], self.steeringAxis),
                                output='%s.r%s'%(steeringNode, self.wheelTurnAxis),
                                specific='wheel')