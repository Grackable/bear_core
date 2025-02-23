# Tongue

import maya.cmds as mc

from bear.system import Generic
from bear.system import Guiding
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import VisSwitch
from bear.utilities import Tools
from bear.utilities import Nodes
from bear.utilities import AddNode
from bear.components.basic import Control
from bear.components.basic import Guide
from bear.components.basic import Curve

class Build(Generic.Build):

    def __init__(self,
                name='tongue',
                side=None,
                controlCount=6,
                jointCount=12,
                parentNode=Nodes.createName('mouth', element='jaw', nodeType=Settings.controlSuffix)[0],
                hasJointGuides=False,
                displaySwitch='faceDisplaySwitch',
                *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.controlCount = controlCount
        self.jointCount = jointCount
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.hasJointGuides = hasJointGuides
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, None, definition)
        if definition:
            return {'guideGroup': guideGroup}

        curveGuide = Curve.Build(component=self.name, 
                                    side=None, 
                                    curveType='nurbsCurve', 
                                    controlCount=self.controlCount, 
                                    jointCount=self.jointCount,
                                    length=5,
                                    lengthAxis='Z',
                                    upAxis='X',
                                    size=1).createGuide(definition)

        for c, curvePivot in enumerate(curveGuide['guidePivots']):
            mc.move(0, 0, c, curvePivot)

        return {'guideGroup': guideGroup}

    def createRig(self):

        guideGroup = Nodes.createName(self.name, nodeType=Settings.guideGroup)[0]
        guideData = Guiding.getGuideAttr(Nodes.createName(self.name, indices=0, nodeType=Settings.guidePivotSuffix)[0])
        self.jointCount = Guiding.getBuildAttrs(guideGroup, 'jointCount')

        size = Tools.getDistance(Nodes.createName(self.name, indices=0, nodeType=Settings.guidePivotSuffix)[0],
                                Nodes.createName(self.name, indices=self.controlCount-1, nodeType=Settings.guidePivotSuffix)[0])

        self.parentNode = ConnectionHandling.inputExists(self.parentNode)

        upnode = AddNode.emptyNode(component=self.name, nodeType='upnode', objType='locator')
        Nodes.alignObject(upnode, Nodes.createName(self.name, indices=0, nodeType=Settings.guidePivotSuffix)[0])
        mc.move(0, size, 0, upnode, os=True, r=True)

        curveRig = Curve.Build(component=self.name,
                                lengthAxis='Z',
                                upAxis='X',
                                jointCount=self.jointCount,
                                hasJointGuides=self.hasJointGuides,
                                squashing=True,
                                upnode=upnode,
                                skeletonParent=self.parentNode,
                                displaySwitch=self.displaySwitch).createRig()

        Nodes.addAttrTitle(curveRig['controls'][0], 'squashStretch', niceName='Squash & Stretch')
        mc.addAttr(curveRig['controls'][0], at='float', ln='squashPower', k=True, dv=0.5)
        mc.connectAttr('%s.squashPower' % curveRig['controls'][0], '%s.scalePowerMid' % curveRig['rigGroup'])

        mc.delete(upnode)

        for node in curveRig['offsets']:
            for axis in 'xyz':
                Nodes.removeConnection('%s.s%s' % (node, axis))

        for g, groupNode in enumerate(curveRig['offsets']):
            if g == 0:
                Tools.parentScaleConstraint(self.parentNode, curveRig['offsets'][0], inbetweenObject=True, useMatrix=False)
            else:
                mc.parent(groupNode, curveRig['controls'][g-1])

        return {'rigGroup': curveRig['rigGroup'],
                'joints': curveRig['joints']}