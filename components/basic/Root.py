# Root

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.system import Guiding
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.utilities import VisSwitch
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):

    def __init__(self, 
                    name='root',
                    side=None,
                    parentNode=None,
                    hasGlobalScale=True,
                    hasPlacement=True,
                    hasMain=True,
                    hasJoint=True,
                    displaySwitch='displaySwitch',
                    *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)
        
        self.name = name
        self.side = side
        self.rootSize = 1.8
        self.placementSize = 1.2
        self.mainSize = 1.0
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.hasGlobalScale = hasGlobalScale
        self.hasPlacement = hasPlacement
        self.hasMain = hasMain
        self.hasJoint = hasJoint
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, self.side, definition)
        if definition:
            return {'guideGroup': guideGroup}
        
        guide = Guide.createGuide(component=self.name,
                                    side=self.side,
                                    alignAxis='Y',
                                    hasLockAndHideAttrs=False)
        
        mc.setAttr('%s.sx' % (guide['control']), 50)
        mc.setAttr('%s.sy' % (guide['control']), 50)
        mc.setAttr('%s.sz' % (guide['control']), 50)

        mc.setAttr('%s.hasPivotControl'%guide['control'], True)
        mc.parent(guide['pivot'], guideGroup)

        mc.addAttr(guide['control'], at='enum', ln='rootShape', k=True, enumName=':'+':'.join(Settings.shapes), dv=Settings.shapes.index('Octagon'))
        if self.hasPlacement:
            mc.addAttr(guide['control'], at='enum', ln='placementShape', k=True, enumName=':'+':'.join(Settings.shapes), dv=Settings.shapes.index('Placement'))
        if self.hasMain:
            mc.addAttr(guide['control'], at='enum', ln='mainShape', k=True, enumName=':'+':'.join(Settings.shapes), dv=Settings.shapes.index('Circle'))
        mc.addAttr(guide['control'], at='float', ln='rootShapeSize', k=True, dv=self.rootSize)
        if self.hasPlacement:
            mc.addAttr(guide['control'], at='float', ln='placementShapeSize', k=True, dv=self.placementSize)

        for attrName in ['shape', 'secondaryDefaultColor', 'hasPivotControl']:
            mc.setAttr('%s.%s'%(guide['control'], attrName), k=False, lock=True)
        
        return {'guideGroup': guideGroup,
                'pivot': guide['pivot']}

    def createRig(self):

        rigGroup = super(Build, self).createRig(self.name)

        guide = Nodes.createName(self.name, self.side, Settings.guidePivotSuffix)[0]
        offset = Guiding.getGuideAttr(guide)['offset']
        color = Guiding.getGuideAttr(guide)['color']

        rootRig = Control.createControl(component=self.name,
                                            side=self.side,
                                            color=color,
                                            shape=Guiding.getGuideAttr(guide, attrPrefix='root')['shape'],
                                            parentNode=self.parentNode,
                                            deleteNode=True,
                                            offset=[offset[0], offset[1], [x*self.rootSize for x in offset[2]]],
                                            rigGroup=rigGroup,
                                            useGuideAttr=False,
                                            ignoreMissingGuideControlWarning=True)

        if self.hasPlacement:
            placementRig = Control.createControl(component=self.name,
                                                    side=self.side,
                                                    element='placement',
                                                    color=color,
                                                    shape=Guiding.getGuideAttr(guide, attrPrefix='placement')['shape'],
                                                    parentNode=self.parentNode,
                                                    deleteNode=True,
                                                    offset=[offset[0], offset[1], [x*self.placementSize for x in offset[2]]],
                                                    rigGroup=rigGroup,
                                                    useGuideAttr=False,
                                                    ignoreMissingGuideControlWarning=True)

            mc.parent(placementRig['offset'], rootRig['control'])
        else:
            placementRig = None

        if self.hasMain:
            mainRig = Control.createControl(component=self.name,
                                                side=self.side,
                                                element='main',
                                                color=color,
                                                shape=Guiding.getGuideAttr(guide, attrPrefix='main')['shape'],
                                                parentNode=self.parentNode,
                                                deleteNode=True,
                                                offset=[offset[0], offset[1], [x*self.mainSize for x in offset[2]]],
                                                hasPivot=True,
                                                rigGroup=rigGroup,
                                                useGuideAttr=False,
                                                ignoreMissingGuideControlWarning=True)

            mc.parent(mainRig['offset'], placementRig['control'] if self.hasPlacement else rootRig['control'])
        else:
            mainRig = None

        if self.hasJoint:
            jointNode = AddNode.jointNode(mainRig['pivotCompensate'] if self.hasMain else placementRig['control'] if self.hasPlacement else rootRig['control'])
        else:
            jointNode = None

        if self.hasGlobalScale:
            Nodes.applyGlobalScale(rootRig['control'], [rigGroup], connect=False)

        for n, rig in enumerate([rootRig, placementRig, mainRig]):
            if rig:
                VisSwitch.connectVisSwitchGroup([rig['control']], rigGroup, displayAttr=['root', 'placement', 'main'][n]+'ControlDisplay')
        VisSwitch.connectVisSwitchGroup([jointNode], rigGroup, displayAttr='jointDisplay')

        return {'rootRig': rootRig,
                'placementRig': placementRig,
                'mainRig': mainRig,
                'joint': jointNode,
                'rigGroup': rigGroup}