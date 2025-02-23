# Chassis

import maya.cmds as mc

from bear.system import Generic
from bear.system import ConnectionHandling
from bear.system import Settings
from bear.utilities import AddNode
from bear.utilities import VisSwitch
from bear.utilities import Nodes
from bear.utilities import Tools
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):
    
    def __init__(self,
                    name='chassis',
                    side=None,
                    parentNode=Nodes.createName('main', nodeType=Settings.controlSuffix)[0],
                    wheelFrontControl=None,
                    wheelBackControl=None,
                    displaySwitch='displaySwitch',
                    *args, **kwargs):
        
        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.wheelFrontControl = wheelFrontControl
        self.wheelBackControl = wheelBackControl
        self.displaySwitch = displaySwitch
        
    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, self.side, definition)
        if definition:
            return {'guideGroup': guideGroup}

        mainGuide = Guide.createGuide(component=self.name,
                                    side=self.side,
                                    parentNode=guideGroup)

        for elementName in ['front', 'back', 'in', 'out']:
            guide = Guide.createGuide(component=self.name,
                                        side=self.side,
                                        element=elementName,
                                        parentNode=guideGroup,
                                        hasGuideShape=False)

        return {'guideGroup': guideGroup,
                'guide': mainGuide}

    def createRig(self):
        
        self.parentNode = ConnectionHandling.inputExists(self.parentNode)

        self.rigGroup = super(Build, self).createRig(self.name, self.side)

        controlRig = Control.createControl(component=self.name,
                                            side=self.side,
                                            rigGroup=self.rigGroup,
                                            parentNode=self.parentNode)
        jointNode = AddNode.jointNode(controlRig['control'])

        self.squarePivot(controlRig)

        VisSwitch.connectVisSwitchGroup([controlRig['control']], self.rigGroup, displayAttr='controlDisplay')
        VisSwitch.connectVisSwitchGroup([jointNode], self.rigGroup, displayAttr='jointDisplay')

        return {'rigGroup': self.rigGroup,
                'control': controlRig['control'],
                'offset': controlRig['offset'],
                'joint': jointNode}
    
    def squarePivot(self, controlRig):

        if self.wheelFrontControl and self.wheelBackControl:
            wheelFrontGuide = ConnectionHandling.inputExists(Nodes.replaceNodeType(self.wheelFrontControl, Settings.guideShapeSuffix))
            wheelBackGuide = ConnectionHandling.inputExists(Nodes.replaceNodeType(self.wheelBackControl, Settings.guideShapeSuffix))

        squarePivotNodes = list()
        squarePivotSpaceNodes = list()
        squarePivotRadiusNodes = list()
        for elementName in ['in', 'out', 'front', 'back']:
            guide = Nodes.createName(component=self.name, 
                                            side=self.side,
                                            element=elementName,
                                            nodeType=Settings.guidePivotSuffix)[0]

            squarePivotNode = AddNode.emptyNode(node=guide, element=elementName, nodeType=Settings.locNodeSuffix)
            squarePivotSpaceNode = AddNode.parentNode(squarePivotNode, Settings.offNodeSuffix)
            squarePivotRadiusNode = AddNode.parentNode(squarePivotNode, 'pivotRadius')
            Nodes.setParent(squarePivotSpaceNode, self.rigGroup if elementName == 'in' else squarePivotNodes[-1])
            if elementName == 'in':
                Tools.parentScaleConstraint(self.parentNode, squarePivotSpaceNode)
            squarePivotNodes.append(squarePivotNode)
            squarePivotSpaceNodes.append(squarePivotSpaceNode)
            squarePivotRadiusNodes.append(squarePivotRadiusNode)
            
            if elementName == 'back':
                chassisHook = AddNode.parentNode(controlRig['control'], 'hook')
                mc.parentConstraint(squarePivotNode, chassisHook, mo=True, skipRotate=('x', 'y', 'z'))
            
            if self.wheelFrontControl and self.wheelBackControl:
                frontRadius = max([mc.getAttr('%s.scale%s'%(wheelFrontGuide, axis)) for axis in 'XYZ'])*0.5
                backRadius = max([mc.getAttr('%s.scale%s'%(wheelBackGuide, axis)) for axis in 'XYZ'])*0.5
            else:
                frontRadius = None
                backRadius = None
            rotXAttr = '%s.rx'%squarePivotNode
            rotZAttr = '%s.rz'%squarePivotNode
            if elementName == 'front':
                mc.transformLimits(squarePivotNode, rx=(0, 0), erx=(1, 0))
                mc.connectAttr('%s.rx'%controlRig['control'], rotXAttr)
                if frontRadius:
                    self.radiusExpr(squarePivotRadiusNode, rotXAttr, frontRadius, 1)
            if elementName == 'back':
                mc.transformLimits(squarePivotNode, rx=(0, 0), erx=(0, 1))
                mc.connectAttr('%s.rx'%controlRig['control'], rotXAttr)
                if backRadius:
                    self.radiusExpr(squarePivotRadiusNode, rotXAttr, backRadius, -1)
            if elementName == 'in':
                mc.transformLimits(squarePivotNode, rz=(0, 0), erz=(1, 0))
                mc.connectAttr('%s.rz'%controlRig['control'], rotZAttr)
            if elementName == 'out':
                mc.transformLimits(squarePivotNode, rz=(0, 0), erz=(0, 1))
                mc.connectAttr('%s.rz'%controlRig['control'], rotZAttr)

        Nodes.lockAndHideAttributes(controlRig['control'], t=[True, True, True], r=[False, False, False], s=[False, False, False])
        Nodes.lockAndHideAttributes(controlRig['control'], t=[False, False, False], r=[False, True, False], s=[False, False, False])
        Nodes.lockAndHideAttributes(controlRig['control'], t=[False, False, False], r=[False, False, False], s=[True, True, True])

    def radiusExpr(self, drivenNode, rotAttr, radius, direction=1):

        tYAttr = '%s.ty'%(drivenNode)
        tZAttr = '%s.tz'%(drivenNode)
        expr = '%s = (1 - cos (deg_to_rad(%s))) * %s;\n'%(tYAttr, rotAttr, radius) \
            + '%s = %s * ((3.14 * 0.25 * %s) / %s) * %s;\n'%(tZAttr, tYAttr, radius, radius, direction)

        Nodes.exprNode(tYAttr, expr)