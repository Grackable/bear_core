# DisplaySwitch

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import Tools
from bear.utilities import VisSwitch
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):
    
    def __init__(self,
                 name='displaySwitch',
                 side=None,
                 parentNode=None,
                 *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.parentNode = Nodes.getPivotCompensate(parentNode)

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, self.side, definition)
        
        if definition:
            return {'guideGroup': guideGroup}
        
        guide = Guide.createGuide(component=self.name, side=self.side)
        mc.setAttr('%s.sy'%guide['control'], 10)

        mc.setAttr(guide['control']+'.shape', Settings.shapes.index('Pyramid Needle'))

        mc.parent(guide['pivot'], guideGroup)

        return {'guideGroup': guideGroup,
                'control': guide['control'],
                'offset': guide['offset'],
                'pivot': guide['pivot']}
        
    def createRig(self):
        
        rigGroup = super(Build, self).createRig(self.name)

        self.parentNode = ConnectionHandling.inputExists(self.parentNode)
        
        guideNode = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix)[0]     
            
        targetGuideGroups = list()
        for targetGuideGroup in Nodes.getAllChildren(Settings.guideRoot, nodeType=Settings.guideGroup):
            displaySwitchAttr = targetGuideGroup+'.displaySwitch'
            if mc.objExists(displaySwitchAttr):
                if mc.getAttr(displaySwitchAttr) == self.name:
                    targetGuideGroups.append(targetGuideGroup)
        targetRigGroups = [Nodes.replaceNodeType(x, Settings.rigGroup) for x in targetGuideGroups]
        targetRigGroups = [x for x in targetRigGroups if mc.objExists(x)]
        controlRig = VisSwitch.parentVisSwitch(guideNode,
                                                self.name,
                                                self.side,
                                                targetRigGroups)

        mc.parent(controlRig['offset'], rigGroup)
        Tools.parentScaleConstraint(self.parentNode, controlRig['offset'])

        return {'rigGroup': rigGroup,
                'control': controlRig['control'],
                'offset': controlRig['offset']}