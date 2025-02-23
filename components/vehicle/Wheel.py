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
                    name='wheel',
                    side=None,
                    spinAxis='x',
                    forwardAxis='z',
                    driveControl=Nodes.createName('drive', nodeType=Settings.controlSuffix)[0],
                    parentNode=Nodes.createName('chassis', nodeType=Settings.controlSuffix)[0],
                    useVectorSpin=False,
                    displaySwitch='displaySwitch',
                    *args, **kwargs):
        
        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.spinAxis = spinAxis.lower()
        self.forwardAxis = forwardAxis.lower()
        self.driveControl = driveControl
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.useVectorSpin = useVectorSpin
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

    def wheelSpin(self, wheelRig, wheelJoint, driveControl, spinAxis='x', forwardAxis='z'):

        Nodes.addAttrTitle(driveControl, 'wheels')
        autoSpinActiveAttr = Nodes.addAttr(driveControl+'.autoSpinEnabled', at='bool', k=False)
        autoSpinAnimateAttr = Nodes.addAttr(driveControl+'.autoSpinAnimate', minVal=0, maxVal=1)

        if self.useVectorSpin:

            spinNode = AddNode.inbetweenNode(node=wheelRig['control'], 
                                    nodeType='spin')
            prevNode = AddNode.emptyNode(node=wheelRig['control'], 
                                    nodeType='prev', 
                                    parentNode=self.rigGroup)
            mc.setAttr('%s.inheritsTransform'%prevNode, False)
            forwardNode = AddNode.emptyNode(node=wheelRig['control'], 
                                    nodeType='forward', 
                                    parentNode=self.rigGroup)
            mc.setAttr('%s.inheritsTransform'%forwardNode, False)

            spaceChild = Nodes.getChildren(wheelRig['offset'])[0]
            offsetNode = spaceChild if spaceChild != wheelRig['control'] else spaceChild
            radius = max([mc.getAttr('%s.scale%s'%(Nodes.replaceNodeType(wheelRig['control'], Settings.guideShapeSuffix), axis)) for axis in 'XYZ'])

            attr = '%s.r%s'%(spinNode, spinAxis)
            expr = 'float $radius = %s;\n'%(radius) \
                + 'vector $wheelPrevVector = `xform -q -t -ws %s`;\n'%(prevNode) \
                + 'vector $wheelVector = `xform -q -t -ws %s`;\n'%(offsetNode) \
                + 'if (%s == 1)'%(autoSpinActiveAttr) \
                + '{xform -t ($wheelVector.x) ($wheelVector.y) ($wheelVector.z) %s;\n'%(forwardNode) \
                + 'xform -os -r -t %s %s %s %s;}\n'%(1 if forwardAxis == 'x' else 0, 1 if forwardAxis == 'y' else 0, 1 if forwardAxis == 'z' else 0, forwardNode) \
                + 'vector $forwardVector = `xform -q -t -ws %s`;\n'%(forwardNode) \
                + 'vector $wheelDirVector = ($forwardVector - $wheelVector);\n' \
                + 'vector $translateVector = ($wheelVector - $wheelPrevVector);\n' \
                + 'float $distance = mag($translateVector);\n' \
                + 'float $dot = dotProduct($translateVector, $wheelDirVector, 1);\n' \
                + '%s = %s + (360 * (($distance * $dot) / (3.14 * $radius))) * %s;\n'%(attr, attr, autoSpinAnimateAttr) \
                + 'if (%s == 1)'%(autoSpinActiveAttr) \
                + '{xform -t ($wheelVector.x) ($wheelVector.y) ($wheelVector.z) %s;}\n'%(prevNode) \
                + 'if (frame == 1) { %s = 0;}'%(attr)

            Nodes.exprNode(attr, expr)

        else:

            spinNode = AddNode.parentNode(node=wheelJoint, 
                                        nodeType='spin',
                                        lockScale=True)

            rotationNode = Nodes.createName(sourceNode=driveControl, nodeType='rotationCapture')[0]
            if not mc.objExists(rotationNode):
                AddNode.childNode(node=Nodes.replaceNodeType(driveControl, Settings.offNodeSuffix), 
                                        nodeType='rotationCapture',
                                        lockScale=True)
                mc.orientConstraint(driveControl, rotationNode)

            positionNode = Nodes.createName(sourceNode=driveControl, nodeType='positionCapture')[0]
            if not mc.objExists(positionNode):
                AddNode.childNode(node=rotationNode, 
                                        nodeType='positionCapture',
                                        lockScale=True)
                mc.pointConstraint(driveControl, positionNode)

            spaceChild = Nodes.getChildren(wheelRig['offset'])[0]
            offsetNode = spaceChild if spaceChild != wheelRig['control'] else spaceChild
            radius = max([mc.getAttr('%s.scale%s'%(Nodes.replaceNodeType(wheelRig['control'], Settings.guideShapeSuffix), axis)) for axis in 'XYZ'])

            attr = '%s.r%s'%(spinNode, spinAxis)
            expr = '%s = %s.translateZ/(%s*3.14)*360*%s*%s;\n'%(attr, positionNode, radius, autoSpinAnimateAttr, autoSpinActiveAttr)

            Nodes.exprNode(attr, expr)