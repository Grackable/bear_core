# Line

import maya.cmds as mc

from bear.system import Generic
from bear.system import ConnectionHandling
from bear.system import Settings
from bear.utilities import Tools
from bear.utilities import Nodes
from bear.utilities import NodeOnVertex
from bear.components.basic import Curve

class Build(Generic.Build):
    
    def __init__(self,
                    name='rope',
                    side=None,
                    controlCount=8,
                    jointCount=16,
                    curveType='nurbsCurve',
                    squashing=False,
                    chain=False,
                    chainParented=False,
                    segmenting=False,
                    lengthAxis='Y',
                    upAxis='Z',
                    hasJointGuides=False,
                    parentNode=None,
                    startParentNode=None,
                    endParentNode=None,
                    displaySwitch='displaySwitch',
                    *args, **kwargs):
        
        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.controlCount = controlCount
        self.jointCount = jointCount
        self.curveType = curveType
        self.lengthDirection = 1 if '-' in lengthAxis else -1
        self.squashing = squashing
        self.chain = chain
        self.chainParented = chainParented
        self.segmenting = segmenting
        self.lengthAxis = lengthAxis.lower()
        self.upAxis = upAxis.lower()
        self.hasJointGuides = hasJointGuides
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.startParentNode = Nodes.getPivotCompensate(startParentNode)
        self.endParentNode = Nodes.getPivotCompensate(endParentNode)
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        curveGuide = super(Build, self).createGuide(self.name, self.side, definition)

        curveGuide = Curve.Build(component=self.name, 
                                    side=self.side,
                                    curveType=self.curveType, 
                                    controlCount=self.controlCount,
                                    jointCount=self.jointCount,
                                    alignAxis=self.lengthAxis,
                                    lengthAxis=self.lengthAxis,
                                    upAxis=self.upAxis,
                                    hasJointGuides=self.hasJointGuides).createGuide(definition)
        if definition:
            return curveGuide

        return {'guideGroup': curveGuide['guideGroup']}

    def createRig(self):

        self.parentNode = ConnectionHandling.inputExists(self.parentNode)
        
        curveRig = Curve.Build(component=self.name,
                                side=self.side,
                                squashing=self.squashing,
                                chain=self.chain,                                                 
                                segmenting=self.segmenting,
                                jointCount=self.jointCount,
                                lengthAxis=self.lengthAxis,
                                upAxis=self.upAxis,
                                skeletonParent=self.parentNode).createRig()

        if self.chainParented:
            for c, offNode in enumerate(curveRig['offsets'][1:]):
                sclCmp = Nodes.replaceNodeType(curveRig['controls'][c], Settings.scaleCompensateNode)
                parent = sclCmp if Nodes.exists(sclCmp) else curveRig['controls'][c]
                Nodes.setParent(offNode, parent)
            Tools.parentScaleConstraint(self.parentNode, curveRig['offsets'][0])
        else:
            if self.parentNode and Nodes.getObjectType(self.parentNode) == 'mesh':
                NodeOnVertex.proximityPin(self.parentNode, curveRig['offsets'])
            else:
                [Tools.parentScaleConstraint(self.parentNode, x) for x in curveRig['offsets']]

        if self.startParentNode and Nodes.getObjectType(self.startParentNode) == 'mesh':
            NodeOnVertex.proximityPin(self.startParentNode, curveRig['offsets'][0])
        else:
            Tools.parentScaleConstraint(self.startParentNode, curveRig['offsets'][0])

        if self.endParentNode and Nodes.getObjectType(self.endParentNode) == 'mesh':
            NodeOnVertex.proximityPin(self.endParentNode, curveRig['offsets'][-1])
        else:
            Tools.parentScaleConstraint(self.endParentNode, curveRig['offsets'][-1])

        return {'controls': curveRig['controls'], 
                'offsets': curveRig['offsets'], 
                'controlRigs': curveRig['controlRigs'], 
                'joints': curveRig['joints'], 
                'rigGroup': curveRig['rigGroup']}