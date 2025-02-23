# Collection

import sys

from bear.system import Generic
from bear.system import Component
from bear.utilities import Tools
from bear.utilities import Nodes

import maya.cmds as mc
       
class Build(Generic.Build):
    
    def __init__(self,
                    name='collection',
                    *args, **kwargs):
        
        super(Build, self).__init__(*args, **kwargs)
        
        self.name = name

    def createGuide(self, definition=False, subComponents=None, allAttrs=None):

        guideGroup = super(Build, self).createGuide(self.name, None, definition)
        
        buildStep = 'definition' if definition else 'guide'

        if subComponents and allAttrs:
            for subComponent in subComponents:
                subModule = sys.modules[allAttrs[subComponent]['componentType']]
                name = allAttrs[subComponent]['name']
                if 'side' in allAttrs[subComponent].keys():
                    side = None if allAttrs[subComponent]['side'] == 'None' else allAttrs[subComponent]['side']
                else:
                    side = None
                guide = Component.Build(subModule, name, side, buildStep, definition=definition).create()
                Nodes.setParent(guide, guideGroup)

        mc.setAttr('%s.readyForRigBuild'%guideGroup, lock=False)
        mc.setAttr('%s.readyForRigBuild'%guideGroup, True)
        mc.setAttr('%s.readyForRigBuild'%guideGroup, lock=True)

        return {'guideGroup': guideGroup}

    def createRig(self, subComponents=None, allAttrs=None):

        self.rigGroup = super(Build, self).createRig(self.name)
        
        buildStep = 'rig'

        rig = dict()
        rootNode = None

        if subComponents and allAttrs:
            for subComponent in subComponents:
                subModuleName = allAttrs[subComponent]['componentType']
                subModule = sys.modules[subModuleName]
                name = allAttrs[subComponent]['name']
                if 'side' in allAttrs[subComponent].keys():
                    side = None if allAttrs[subComponent]['side'] == 'None' else allAttrs[subComponent]['side']
                else:
                    side = None
                subRig = Component.Build(subModule, name, side, buildStep).create()

                # connect global scale
                if subModuleName == 'Root':
                    rootNode = subRig['mainRig']['pivotCompensate']
                else:
                    if subRig:
                        Tools.parentScaleConstraint(rootNode, subRig['rigGroup'])

                rig[Nodes.replaceNodeType(subComponent)] = subRig
                if subRig:
                    Nodes.setParent(subRig['rigGroup'], self.rigGroup)

        rig['rigGroup'] = self.rigGroup

        return rig