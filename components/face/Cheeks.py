# Cheeks

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import Tools
from bear.utilities import VisSwitch
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):

    def __init__(self,
                name='cheek',
                hasSecondaryControls=True,
                hasExtraCheekControl=False, 
                parentNode=Nodes.createName('head', nodeType=Settings.controlSuffix)[0],
                displaySwitch='faceDisplaySwitch',
                *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.hasSecondaryControls = hasSecondaryControls
        self.hasExtraCheekControl = hasExtraCheekControl
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, 'auto', definition)
        if definition:
            return {'guideGroup': guideGroup}

        count = 1
        elementNames = ['main']
        indexNames = [None]
        if self.hasSecondaryControls:
            count += 2
            elementNames.extend([None, None])
            indexNames.extend([0, 1])
        if self.hasExtraCheekControl:
            count += 1
            elementNames.append('extra')
            indexNames.append(None)

        for n in range(count):

            guide = Guide.createGuide(component=self.name, side=Settings.leftSide, indices=indexNames[n], element=elementNames[n],
                                                                            size=1)
            
            mc.parent(guide['pivot'], guideGroup)

            mc.move([0, -3, 3, 3][n], 3 if n > 3 else 0, 0, guide['pivot'])
            
            # blendshape guiding
            
            if n == 0:
                    
                Nodes.addAttrTitle(guide['control'], 'blendShape')
            
                attrNames = ['translateY_pos', 'translateY_neg']
                defaultVal = [2, 2]
                for a, attrName in enumerate(attrNames):
                    mc.addAttr(guide['control'], at='float', ln='bsh_' + attrName, k=True, dv=defaultVal[a])

            for side in [Settings.leftSide, Settings.rightSide]:
                ConnectionHandling.addOutput(guideGroup, Nodes.createName(component=self.name, 
                                                                            side=side, 
                                                                            indices=indexNames[n], 
                                                                            element=elementNames[n], 
                                                                            nodeType=Settings.skinJointSuffix)[0])

        return {'guideGroup': guideGroup}

    def createRig(self):

        cheekMainGuide = Nodes.createName(component=self.name, side=Settings.leftSide, element='main', nodeType=Settings.guidePivotSuffix)[0]
        cheek1Guide = Nodes.createName(component=self.name, side=Settings.leftSide, indices=0, nodeType=Settings.guidePivotSuffix)[0]
        cheek2Guide = Nodes.createName(component=self.name, side=Settings.leftSide, indices=1, nodeType=Settings.guidePivotSuffix)[0]
        cheek3Guide = Nodes.createName(component=self.name, side=Settings.leftSide, element='extra', nodeType=Settings.guidePivotSuffix)[0]
        
        self.parentNode = ConnectionHandling.inputExists(self.parentNode)

        rigGroup = super(Build, self).createRig(self.name, 'auto')
        controlGroup = AddNode.emptyNode(component=self.name, element='control', nodeType=Settings.rigGroup)
        mc.parent(controlGroup, rigGroup)
        
        guides = [cheekMainGuide]
        if self.hasSecondaryControls:
            guides.extend([cheek1Guide, cheek2Guide])
        if self.hasExtraCheekControl:
            guides.append(cheek3Guide)

        for side in [Settings.leftSide, Settings.rightSide]:
            
            jointNodes = list()
            controlRigs = list()

            for g, guide in enumerate(guides):
                
                cheeksRig = Control.createControl(node=guide, side=side, ignoreMissingGuideControlWarning=True)

                controlRigs.append(cheeksRig)

                jointNode = AddNode.jointNode(cheeksRig['control'], nodeType=Settings.skinJointSuffix, skeletonParent=self.parentNode)
                jointNodes.append(jointNode)
                mc.parent(cheeksRig['offset'], controlGroup)
                
                if g == 0:
                    Nodes.addAttrTitle(cheeksRig['control'], 'cheek')
                    pushNode = AddNode.parentNode(cheeksRig['control'], nodeType='push', lockScale=True)
                    pushAttrName = 'pushOut'
                    pushAttr = cheeksRig['control'] + '.' + pushAttrName
                    mc.addAttr(cheeksRig['control'], at='float', ln=pushAttrName, dv=0, k=False)
                    mc.setAttr(pushAttr, cb=True)

                    Nodes.mulNode(input1=pushAttr, 
                                    input2='%s.ty'%cheeksRig['control'], 
                                    output='%s.tz'%pushNode)

                    mc.transformLimits(pushNode, tz=(0, 0), etz=[1, 0])
                    Tools.parentScaleConstraint(self.parentNode, cheeksRig['offset'])

                if g == 3 and self.hasExtraCheekControl:
                    Tools.parentScaleConstraint(self.parentNode, cheeksRig['offset'])

            if self.hasSecondaryControls:
                for c, controlRig in enumerate(controlRigs[1:3]):
                    Tools.blendBetween([self.parentNode], 
                                        [jointNodes[0]],
                                        [controlRig['offset']],
                                        attrNode=controlRig['control'],
                                        attrName='mainInfluence', 
                                        attrTitle='follow', 
                                        scaleConstrained=False,
                                        defaultValue=[0.5, 0.5][c],
                                        attrIsKeyable=False)

            VisSwitch.connectVisSwitchGroup([x['control'] for x in controlRigs], rigGroup, displayAttr='controlDisplay')
            VisSwitch.connectVisSwitchGroup(jointNodes, rigGroup, displayAttr='jointDisplay')

        return {'rigGroup': rigGroup, 
                'joints': jointNodes,
                'offsets': [x['offset'] for x in controlRigs],
                'controls': [x['control'] for x in controlRigs]}