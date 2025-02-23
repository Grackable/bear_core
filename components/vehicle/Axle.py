# Wheel

import maya.cmds as mc

from bear.system import Generic
from bear.system import ConnectionHandling
from bear.system import Settings
from bear.utilities import AddNode
from bear.utilities import VisSwitch
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):
    
    def __init__(self,
                    name='axle',
                    side=None,
                    parentNode=Nodes.createName('chassis', nodeType=Settings.controlSuffix)[0],
                    displaySwitch='displaySwitch',
                    *args, **kwargs):
        
        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.displaySwitch = displaySwitch
        
    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, self.side, definition)
        if definition:
            return {'guideGroup': guideGroup}

        guide = Guide.createGuide(component=self.name,
                                    side=self.side,
                                    parentNode=guideGroup)

        return {'guideGroup': guideGroup,
                'guide': guide}

    def createRig(self):
        
        self.driveControl = ConnectionHandling.inputExists(self.driveControl)
        self.parentNode = ConnectionHandling.inputExists(self.parentNode)

        self.rigGroup = super(Build, self).createRig(self.name, self.side)

        controlRig = Control.createControl(component=self.name,
                                            side=self.side, 
                                            rigGroup=self.rigGroup,
                                            parentNode=self.parentNode)
        jointNode = AddNode.jointNode(controlRig['control'])

        steeringNode = AddNode.inbetweenNode(controlRig['offset'], 'steering')

        self.wheelSpin(controlRig, jointNode, self.driveControl)

        VisSwitch.connectVisSwitchGroup([controlRig['control']], self.rigGroup, displayAttr='controlDisplay')
        VisSwitch.connectVisSwitchGroup([jointNode], self.rigGroup, displayAttr='jointDisplay')

        return {'rigGroup': self.rigGroup,
                'control': controlRig['control'],
                'offset': controlRig['offset'],
                'steering': steeringNode,
                'joint': jointNode}