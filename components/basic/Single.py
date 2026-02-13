# Single

import maya.cmds as mc
from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import Nodes
from bear.utilities import VisSwitch
from bear.utilities import AddNode
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):
    
    def __init__(self,
                 name='single',
                 side=None,
                 element=None,
                 parentNode=None,
                 parentType=None,
                 parentOrientNode=None,
                 count=1,
                 chainParented=False,
                 hasJoints=True,
                 inheritScale=True,
                 hasSecondaryControl=False,
                 displaySwitch='displaySwitch',
                 *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.element = element
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.parentType = parentType
        self.parentOrientNode = parentOrientNode
        self.count = count
        self.chainParented = chainParented
        self.hasJoints = hasJoints
        self.inheritScale = inheritScale
        self.hasSecondaryControl = hasSecondaryControl
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, self.side, definition, self.element)
        if definition:
            return {'guideGroup': guideGroup}

        guideList = list()
        
        if self.count:
            for n in range(self.count):
                index = n if self.count > 1 else None
                guide = Guide.createGuide(component=self.name,
                                            side=self.side,
                                            element=self.element,
                                            indices=index,
                                            size=10)
                mc.parent(guide['pivot'], guideGroup)
                guideList.append(guide)

        return {'guideGroup': guideGroup,
                'controls': [x['control'] for x in guideList] if self.count else None, 
                'guides': [x['pivot'] for x in guideList] if self.count else None}

    def createRig(self):

        rigGroup = super(Build, self).createRig(self.name, self.side, element=self.element)

        controlRigs = list()
        secControlRigs = list()
        jointNodes = list()
            
        for n in range(self.count):
            parentNode = None if self.chainParented and n > 0 else self.parentNode
            index = n if self.count > 1 else None
            controlRig = Control.createControl(component=self.name, 
                                                side=self.side, 
                                                element=self.element,
                                                indices=index,
                                                parentNode=parentNode, 
                                                parentType=self.parentType,
                                                rigGroup=rigGroup)
            controlRigs.append(controlRig)
            if self.hasSecondaryControl:
                secControlRig = Control.createControl(controlRig['control'], 
                                                        component=self.name,
                                                        side=self.side, 
                                                        element=self.element,
                                                        indices=index,
                                                        specific='secondary',
                                                        sizeMultiplier=0.9,
                                                        parentNode=controlRig['pivotCompensate'], 
                                                        parentType='Hierarchy',
                                                        rigGroup=rigGroup)
                secControlRigs.append(secControlRig)
                VisSwitch.connectVisSwitchGroup([secControlRig['control']], rigGroup, displayAttr='controlDisplay')
                Nodes.addAttrTitle(controlRig['control'], 'extra')
                mc.addAttr(controlRig['control'], at='bool', ln='showSecondaryControl', dv=False, k=False)
                mc.setAttr('%s.showSecondaryControl'%controlRig['control'], channelBox=True)
                mc.connectAttr('%s.showSecondaryControl'%controlRig['control'], '%s.visibility'%secControlRig['offset'])

            if self.hasJoints:
                jointNode = AddNode.jointNode(secControlRig['pivotCompensate'] if self.hasSecondaryControl else controlRig['pivotCompensate'], 
                                                specific='remove', 
                                                resetTransforms=True, 
                                                skeletonParent=self.parentNode)
                jointNodes.append(jointNode)
            if self.parentOrientNode:
                if not (n > 0 and self.chainParented):
                    [Nodes.removeConnection('%s.r%s'%(controlRig['offset'], axis)) for axis in 'xyz']
                    orientCnt = mc.orientConstraint(self.parentOrientNode, controlRig['offset'], mo=True)[0]
                    mc.setAttr('%s.interpType'%orientCnt, 2)

            if not self.inheritScale:
                [Nodes.removeConnection('%s.s%s'%(controlRigs[0]['offset'], axis)) for axis in 'xyz']

            VisSwitch.connectVisSwitchGroup([controlRig['control']], rigGroup, displayAttr='controlDisplay')
            if self.hasJoints:
                VisSwitch.connectVisSwitchGroup([jointNode], rigGroup, displayAttr='jointDisplay')

        if self.chainParented:
            for c, controlRig in enumerate(controlRigs):
                if c > 0:
                    Nodes.setParent(controlRig['offset'], controlRigs[c-1]['scaleCompensate'])

        return {'rigGroup': rigGroup, 
                'controls': [x['pivotCompensate'] for x in controlRigs] if self.count else None, 
                'offsets': [x['offset'] for x in controlRigs] if self.count else None,  
                'joints': None if jointNodes == [] else jointNodes}