# Nose

import maya.cmds as mc

from bear.system import Generic
from bear.system import Guiding
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
                name='nose',
                controlCount=2,
                hasNostril=True,
                hasTurnup=True,
                turnupParentIndex=0,
                parentNode=Nodes.createName('head', nodeType=Settings.controlSuffix)[0],
                displaySwitch='faceDisplaySwitch',
                *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.controlCount = controlCount
        self.hasNostril = hasNostril
        self.hasTurnup = hasTurnup
        self.turnupParentIndex = turnupParentIndex
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, 'auto', definition)
        if definition:
            return {'guideGroup': guideGroup}
        
        for c in range(self.controlCount):

            guide = Guide.createGuide(component=self.name,
                                        indices=c,
                                        size=1)
            
            mc.parent(guide['pivot'], guideGroup)
            mc.setAttr('%s.ty'%guide['pivot'], 2-(2*c))

        if self.hasNostril:

            guide = Guide.createGuide(component=self.name,
                                        side=Settings.leftSide,
                                        element='nostril',
                                        size=1)
            
            mc.parent(guide['pivot'], guideGroup)
            mc.setAttr('%s.tx'%guide['pivot'], 2)
            mc.setAttr('%s.ty'%guide['pivot'], -2)

            Nodes.addAttrTitle(guide['control'], 'blendShape')
            attrNames = ['bsh_puffout_pos', 'bsh_puffout_neg']
            for attrName in attrNames:
                mc.addAttr(guide['control'], at='float', ln=attrName, k=True, dv=1)

        if self.hasTurnup:

            guide = Guide.createGuide(component=self.name,
                                        side=Settings.leftSide,
                                        element='turnup',
                                        size=1)
            
            mc.parent(guide['pivot'], guideGroup)
            mc.setAttr('%s.tx'%guide['pivot'], 2)
            mc.setAttr('%s.ty'%guide['pivot'], 0)

            Nodes.addAttrTitle(guide['control'], 'blendShape')
            attrNames = ['bsh_translateY_pos', 'bsh_translateY_neg']
            defaultVal = [3, 2]
            for d in range(len(attrNames)):
                mc.addAttr(guide['control'], at='float', ln=attrNames[d], k=True, dv=defaultVal[d])

        return {'guideGroup': guideGroup}

    def createRig(self):
        
        noseGuides = list()
        extraGuides = list()
        if self.controlCount > 0:
            noseGuides.extend([Nodes.createName(self.name, indices=n, nodeType=Settings.guidePivotSuffix)[0] for n in range(self.controlCount)])
        if self.hasNostril:
            nostrilName = Nodes.createName(self.name, side=Settings.leftSide, element='nostril', nodeType=Settings.guidePivotSuffix)[0]
            extraGuides.append(nostrilName)
        if self.hasTurnup:
            turnupName = Nodes.createName(self.name, side=Settings.leftSide, element='turnup', nodeType=Settings.guidePivotSuffix)[0]
            extraGuides.append(turnupName)

        self.parentNode = ConnectionHandling.inputExists(self.parentNode)
        
        rigGroup = super(Build, self).createRig(self.name, 'auto')

        controlRigs = list()
        joints = list()
        controls = list()
        for n, noseGuide in enumerate(noseGuides):

            noseRig = Control.createControl(node=noseGuide)

            controlRigs.append(noseRig)
            controls.append(noseRig['control'])

            if n == 0:
                mc.parent(noseRig['offset'], rigGroup)
                Tools.parentScaleConstraint(self.parentNode, noseRig['offset'])
            else:
                mc.parent(noseRig['offset'], controlRigs[n-1]['control'])

            jointNode = AddNode.jointNode(noseRig['control'], 
                                            nodeType=Settings.skinJointSuffix,
                                            skeletonParent=self.parentNode)
            joints.append(jointNode)

        for side in [Settings.leftSide, Settings.rightSide]:
            for g, extraGuide in enumerate(extraGuides[::-1]):

                guide = Guiding.convertGuide(extraGuide, mirror=True if side == Settings.rightSide else False)[0]

                noseRig = Control.createControl(node=guide,
                                                side=side)

                mc.parent(noseRig['offset'], controlRigs[self.turnupParentIndex]['control'] if g == 0 else rigGroup)
                if g == 1:
                    Tools.parentScaleConstraint(self.parentNode, noseRig['offset'])

                jointNode = AddNode.jointNode(noseRig['control'], 
                                                nodeType=Settings.skinJointSuffix,
                                                skeletonParent=joints[self.turnupParentIndex] if g == 0 else self.parentNode)

                VisSwitch.connectVisSwitchGroup([jointNode], rigGroup, displayAttr='jointDisplay')
                if Nodes.getElement(noseRig['control']) == 'nostril':
                    VisSwitch.connectVisSwitchGroup([noseRig['control']], rigGroup, displayAttr='nostrilControlDisplay')
                elif Nodes.getElement(noseRig['control']) == 'turnup':
                    VisSwitch.connectVisSwitchGroup([noseRig['control']], rigGroup, displayAttr='turnupControlDisplay')
                else:
                    VisSwitch.connectVisSwitchGroup([noseRig['control']], rigGroup, displayAttr='controlDisplay')

        VisSwitch.connectVisSwitchGroup(joints, rigGroup, displayAttr='jointDisplay')
        VisSwitch.connectVisSwitchGroup([x['control'] for x in controlRigs], rigGroup, displayAttr='controlDisplay')
        
        self.cleanup(Nodes.replaceNodeType(rigGroup, 'guide'), trashGuides=True, removeRightGuides=True, hierarchy=False, display=False, selectionSets=False)

        return {'rigGroup': rigGroup, 
                'joints': joints,
                'controls': controls}