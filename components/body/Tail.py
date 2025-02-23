# Tail

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.system import Guiding
from bear.utilities import Tools
from bear.utilities import Nodes
from bear.utilities import AddNode
from bear.utilities import SpaceSwitch
from bear.components.basic import Curve
from bear.components.basic import Control

class Build(Generic.Build):

    def __init__(self,
                name='tail',
                side=None,
                controlCount=12,
                jointCount=24,
                ikControlCount=4,
                lengthAxis='Z',
                upAxis='X',
                spaceNodes=[Nodes.createName('root', nodeType=Settings.controlSuffix)[0],
                            Nodes.createName('root', element='placement', nodeType=Settings.controlSuffix)[0],
                            Nodes.createName('root', element='main', specific='pivot', nodeType=Settings.controlSuffix)[0],
                            Nodes.createName('body', nodeType=Settings.controlSuffix)[0],
                            Nodes.createName('body', element='hips', nodeType=Settings.controlSuffix)[0],
                            ],
                spaceNames=['root',
                            'placement',
                            'main',
                            'body',
                            'hips',
                            ],
                parentNode=Nodes.createName('hips', nodeType=Settings.skinJointSuffix)[0],
                displaySwitch='bodyDisplaySwitch',
                *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.controlCount = controlCount
        self.jointCount = jointCount
        self.ikControlCount = ikControlCount
        self.lengthAxis = lengthAxis
        self.upAxis = upAxis
        self.spaceNodes = spaceNodes
        self.spaceNames = spaceNames
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, self.side, definition)
        if definition:
            return {'guideGroup': guideGroup}

        curveGuide = Curve.Build(component=self.name, 
                                    side=None, 
                                    element='ik',
                                    controlCount=self.ikControlCount, 
                                    jointCount=0,
                                    length=5,
                                    lengthAxis=self.lengthAxis,
                                    alignAxis=self.lengthAxis,
                                    upAxis=self.upAxis).createGuide(definition)
        
        mc.parent(curveGuide['guideGroup'], guideGroup)

        for c, curvePivot in enumerate(curveGuide['guidePivots']):
            tOffset = [0, 0, -c*10]
            rOffset = [90, 0, 0]
            [mc.setAttr('%s.t%s'%(curvePivot, axis), tOffset[a]) for a, axis in enumerate('xyz')]
            [mc.setAttr('%s.r%s'%(curvePivot, axis), rOffset[a]) for a, axis in enumerate('xyz')]

        mc.addAttr(curveGuide['guideControls'][0], at='enum', ln='fkShape', k=True, enumName=':'+':'.join(Settings.shapes))
        mc.addAttr(curveGuide['guideControls'][0], at='float', ln='fkShapeSize', k=True, dv=0.5)
        mc.addAttr(curveGuide['guideControls'][0], at='enum', ln='fkColor', k=True, enumName=':'+':'.join(['Default']+Settings.colors), dv=Settings.colors.index('Green')+1)

        mc.addAttr(curveGuide['guideControls'][0], at='enum', ln='attrShape', k=True, enumName=':'+':'.join(Settings.shapes), dv=Settings.shapes.index('Marker'))
        mc.addAttr(curveGuide['guideControls'][0], at='float', ln='attrShapeSize', k=True, dv=2)
        mc.addAttr(curveGuide['guideControls'][0], at='enum', ln='attrColor', k=True, enumName=':'+':'.join(['Default']+Settings.colors))

        return {'guideGroup': guideGroup}

    def createRig(self):

        guideNode = Nodes.createName(component=self.name, side=self.side, element='ik', indices=0, nodeType=Settings.guidePivotSuffix)[0]
        guideShape = Nodes.createName(component=self.name, side=self.side, element='ik', indices=0, nodeType=Settings.guideShapeSuffix)[0]
        size = Nodes.getSize(Nodes.replaceNodeType(guideNode, Settings.guideShapeSuffix))[0]

        self.parentNode = ConnectionHandling.inputExists(self.parentNode)
        
        dummyUpnode = AddNode.emptyNode(guideNode, component=self.name, side=self.side, element='upnode')
        mc.move(10*size if self.upAxis == 'X' else 0, 10*size if self.upAxis == 'Y' else 0, 10*size if self.upAxis == 'Z' else 0, dummyUpnode, r=True, os=True)

        fkShape = Guiding.getGuideAttr(guideShape, attrPrefix='fk')['shape']
        fkShapeSize = mc.getAttr('%s.fkShapeSize'%guideShape)
        fkColor = Guiding.getGuideAttr(guideShape, attrPrefix='fk')['color']
        shapeOffset = Guiding.getGuideAttr(guideShape)['offset']

        attrShape = Guiding.getGuideAttr(guideShape, attrPrefix='attr')['shape']
        attrShapeSize = mc.getAttr('%s.attrShapeSize'%guideShape)
        attrColor = Guiding.getGuideAttr(guideShape, attrPrefix='attr')['color']
        
        curveRig = Curve.Build(component=self.name,
                                    side=self.side,
                                    lengthAxis=self.lengthAxis,
                                    upAxis=self.upAxis,
                                    controlCount=self.controlCount,
                                    jointCount=self.jointCount,
                                    squashing=True,
                                    useGuideAttr=False,
                                    shape=fkShape,
                                    color=fkColor,
                                    offset=[shapeOffset[0], shapeOffset[1], [fkShapeSize*shapeOffset[2][0], fkShapeSize*shapeOffset[2][1], fkShapeSize*shapeOffset[2][2]]],
                                    upnode=dummyUpnode,
                                    displaySwitch=self.displaySwitch,
                                    skeletonParent=self.parentNode).createRig()

        ikCurveRig = Curve.Build(component=self.name,
                                    side=self.side,
                                    element='ik',
                                    lengthAxis=self.lengthAxis,
                                    upAxis=self.upAxis,
                                    controlCount=self.ikControlCount,
                                    jointCount=0,
                                    upnode=dummyUpnode,
                                    displaySwitch=self.displaySwitch,
                                    parentNode=self.parentNode,
                                    skeletonParent=self.parentNode).createRig()
        
        mc.parent(ikCurveRig['rigGroup'], curveRig['rigGroup'])

        attrRig = Control.createControl(ikCurveRig['controls'][0],
                                    element='attributes',
                                    shape=attrShape,
                                    color=attrColor,
                                    useGuideAttr=False,
                                    offset=[shapeOffset[0], shapeOffset[1], [attrShapeSize*shapeOffset[2][0], attrShapeSize*shapeOffset[2][1], attrShapeSize*shapeOffset[2][2]]],
                                    lockAndHide=[[True, True, True], [True, True, True], [True, True, True]],
                                    parentNode=ikCurveRig['controls'][0])
        mc.parent(attrRig['offset'], ikCurveRig['rigGroup'])

        curveAttachGroup = AddNode.emptyNode(component=self.name, side=self.side, nodeType='curveAttach', parentNode=curveRig['rigGroup'])
        mc.setAttr('%s.inheritsTransform'%curveAttachGroup, False)
        curveAttachNodes = [AddNode.emptyNode(x, nodeType='curveAttach') for x in curveRig['controls']]
        mc.parent(curveAttachNodes, curveAttachGroup)
        Curve.Build(ikCurveRig['curve'], 
                    alignAxis=self.lengthAxis,
                    lengthAxis=self.lengthAxis,
                    upAxis=self.upAxis).alignNodesToCurve(nodeList=curveAttachNodes, 
                                            offset=0, 
                                            reverse=False,
                                            gap=0, 
                                            upnode=ikCurveRig['controls'],
                                            upnodeType='objectrotation',
                                            deleteMotionPath=False)
        for c, curveOff in enumerate(curveRig['offsets']):
            Nodes.alignObject(curveOff, curveAttachNodes[c])
        blendNodes = [AddNode.parentNode(x, 'blend') for x in curveRig['controls']]
        Tools.blendBetween(curveRig['offsets'],
                           curveAttachNodes,
                           blendNodes,
                           attrNode=attrRig['control'],
                           attrName='attachToIk',
                           attrTitle='ikAttributes',
                           scaleConstrained=False,
                           defaultValue=1)

        Nodes.addAttrTitle(curveRig['controls'][0], 'squashStretch', niceName='Squash & Stretch')
        mc.addAttr(curveRig['controls'][0], at='float', ln='squashPower', k=True, dv=0.5)
        mc.connectAttr('%s.squashPower' % curveRig['controls'][0], '%s.scalePowerMid' % curveRig['rigGroup'])

        mc.delete(dummyUpnode)

        for node in curveRig['offsets']:
            for axis in 'xyz':
                Nodes.removeConnection('%s.s%s' % (node, axis))

        for g, groupNode in enumerate(ikCurveRig['offsets']):
            if g > 0:
                parentNode = ikCurveRig['controls'][g-1]
                mc.parent(groupNode, parentNode)

                SpaceSwitch.createSpaceSwitch(offNode=groupNode,
                                        sourceObjs=self.spaceNodes[::]+[parentNode],
                                        switchNames=self.spaceNames[::]+['parent'],
                                        defaultSpace='parent')
            else:
                Tools.parentScaleConstraint(self.parentNode, groupNode)

        return {'rigGroup': curveRig['rigGroup'],
                'joints': curveRig['joints'],
                'tail': curveRig,
                'ikTail': ikCurveRig,
                'attr': attrRig}