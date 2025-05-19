# Head

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import Guiding
from bear.system import ConnectionHandling
from bear.utilities import VisSwitch
from bear.utilities import SpaceSwitch
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):

    def __init__(self,
                    name='head',
                    side=None,
                    hasNeck=True,
                    isScalable=True,
                    neckScaling=True,
                    neckSquashing=False,
                    spaceNodes=[Nodes.createName('root', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('root', element='placement', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('root', element='main', specific='pivot', nodeType=Settings.controlSuffix)[0], 
                                Nodes.createName('body', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('chest', nodeType=Settings.controlSuffix)[0],
                                Nodes.createName('head', element='neck', nodeType=Settings.controlSuffix)[0],
                                ],
                    spaceNames=['root', 
                                'placement', 
                                'main',
                                'body', 
                                'chest', 
                                'neck',
                                ],
                    displaySwitch='bodyDisplaySwitch',
                    input_chestName='chest',
                    input_neckName='neck',
                    parentNode=None,
                    *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)
        
        self.name = name
        self.side = side
        self.hasNeck = hasNeck
        self.isScalable = isScalable
        self.neckScaling = neckScaling
        self.neckSquashing = neckSquashing
        self.spaceNodes = [Nodes.getPivotCompensate(x) for x in spaceNodes]
        self.spaceNames = spaceNames
        self.defaultSpace = 'chest' if hasNeck and 'chest' in spaceNames else 'neck' if not hasNeck and 'neck' in spaceNames else None
        self.displaySwitch = displaySwitch
        self.input_chestName = input_chestName if input_chestName != '' else None
        self.input_neckName = input_neckName if input_neckName != '' else None
        self.parentNode = parentNode

    def createGuide(self, definition=False):

        guideGroup = super(Build, self).createGuide(self.name, self.side, definition)
        if definition:
            return {'guideGroup': guideGroup}
        
        guides = list()

        headGuide = Guide.createGuide(component=self.name, side=self.side, parentNode=guideGroup)
        guides.append(headGuide)

        Nodes.lockAndHideAttributes(headGuide['offset'], t=[True, True, True], r=[True, True, True],
                                        s=[True, True, True], v=True)

        mc.setAttr('%s.hasPivotControl'%headGuide['control'], True)

        if self.hasNeck:
            neckGuide = Guide.createGuide(component=self.name, side=self.side, element='neck', parentNode=guideGroup)
            guides.append(neckGuide)

            Nodes.lockAndHideAttributes(neckGuide['offset'], t=[True, True, True], r=[True, True, True],
                                            s=[True, True, True], v=True)

            ConnectionHandling.addOutput(guideGroup, Nodes.replaceNodeType(neckGuide['pivot'], Settings.skinJointSuffix))

        for g, guide in enumerate(guides):
            mc.move(0, 10-g*10, 0, guide['pivot'], r=True, ws=True)

        ConnectionHandling.addOutput(guideGroup, Nodes.replaceNodeType(headGuide['pivot'], Settings.skinJointSuffix))

        return {'guideGroup': guideGroup}

    def createRig(self):

        self.parentNode = ConnectionHandling.inputExists(Nodes.getPivotCompensate(self.parentNode))

        if self.input_chestName:
            chestControl = Nodes.createName(component=self.input_chestName, side=self.side, nodeType=Settings.controlSuffix)[0]
            chestControl = ConnectionHandling.inputExists(Nodes.getPivotCompensate(chestControl))
        if self.parentNode:
            chestControl = self.parentNode

        if self.hasNeck:
            neckGuide = Nodes.createName(component=self.name, side=self.side, element='neck', nodeType=Settings.guidePivotSuffix)[0]
            neckOffset = Guiding.getGuideAttr(neckGuide)['offset']
            neckShape = Guiding.getGuideAttr(neckGuide)['shape']
            if not Nodes.exists(neckGuide):
                mc.error('No neck guide defined. Rebuild the guide first.')

        headGroup = super(Build, self).createRig(self.name, self.side)

        headGuide = Nodes.createName(component=self.name, side=self.side, nodeType=Settings.guidePivotSuffix)[0]

        headOffset = Guiding.getGuideAttr(headGuide)['offset']
        headShape = Guiding.getGuideAttr(headGuide)['shape']
        headColor = Guiding.getGuideAttr(headGuide)['color']
        headHasPivot = Guiding.getGuideAttr(headGuide)['hasPivotControl']
        
        headRig = Control.createControl(component=self.name,
                                        side=self.side, 
                                        shape=headShape,
                                        color=headColor,
                                        rotateOrder='zxy',
                                        deleteNode=True,
                                        offset=headOffset,
                                        hasPivot=headHasPivot,
                                        hasRotateOrder=True)
        Nodes.alignObject(headRig['offset'], headGuide)

        if self.hasNeck:
            neckRig = Control.createControl(component=self.name,
                                            side=self.side, 
                                            element='neck',
                                            shape=neckShape,
                                            rotateOrder='zxy',
                                            deleteNode=True,
                                            offset=neckOffset)
        
            Nodes.alignObject(neckRig['offset'], neckGuide)
            neckJoint = AddNode.jointNode(neckRig['control'], 
                                        nodeType=Settings.setupJointSuffix if self.input_neckName else Settings.skinJointSuffix,
                                        skeletonParent=Nodes.createName(self.input_chestName, self.side, Settings.skinJointSuffix)[0],)
            Nodes.lockAndHideAttributes(neckRig['control'], t=[True, True, True], r=[False, False, False],
                                            s=[False, False, False] if self.isScalable else [True, True, True])

            # neck follow

            Nodes.addAttrTitle(headRig['control'], 'follow')

            followAttr = 'neckFollow'
            mc.addAttr(headRig['control'], at='float', ln=followAttr, keyable=True, hidden=False, hasMinValue=True,
                    minValue=0, hasMaxValue=True, maxValue=1, dv=0.4)

            neckCntNode = AddNode.inbetweenNode(neckRig['offset'])

            for axis in 'xyz':

                multNode = mc.shadingNode('multDoubleLinear',
                                        asUtility=True,
                                        name='_'.join(['neckFollow', axis, 'mul']))
                mc.connectAttr('%s.r%s' % (headRig['control'], axis), '%s.input1' % multNode)
                mc.connectAttr('%s.%s' % (headRig['control'], followAttr), '%s.input2' % multNode)

                mc.connectAttr('%s.output' % multNode, '%s.r%s' % (neckCntNode, axis))

        else:
            neckRig = None
            neckJoint = None

        skeletonParent = None
        if self.input_neckName:
            neckJointCount = int(mc.getAttr('%s.jointCount'%Nodes.createName(self.input_neckName, self.side, Settings.guideGroup)[0]))
            skeletonParent = Nodes.createName(self.input_neckName, self.side, Settings.skinJointSuffix, indices=neckJointCount-1)[0]
            ConnectionHandling.inputExists(skeletonParent)
        if self.input_chestName and not self.input_neckName:
            skeletonParent = Nodes.createName(self.input_chestName, self.side, Settings.skinJointSuffix)[0]
            ConnectionHandling.inputExists(skeletonParent)
        if self.hasNeck and not self.input_neckName:
            skeletonParent = neckJoint

        headJoint = AddNode.jointNode(headRig['pivotCompensate'], specific='remove', skeletonParent=skeletonParent)
        Nodes.lockAndHideAttributes(headRig['control'], t=[False, False, False], r=[False, False, False],
                                    s=[False, False, False] if self.isScalable else [True, True, True])
        if self.isScalable:
            Nodes.alignObject(headJoint, headGuide)
            mc.scaleConstraint(headRig['pivotCompensate'], headJoint, mo=True)
        
        # constraints

        mc.parentConstraint(headRig['pivotCompensate'], headJoint, maintainOffset=True)

        if self.hasNeck:

            mc.parentConstraint(neckRig['control'], headRig['offset'], mo=True, skipRotate=['x', 'y', 'z'])
            if self.input_chestName or self.parentNode:
                mc.parentConstraint(chestControl, neckJoint, mo=True, skipRotate=['x', 'y', 'z'])

            neckTarget = AddNode.emptyNode(component=self.name, side=self.side, element='neck', specific='target')
            Nodes.alignObject(neckTarget, headJoint)
            mc.delete(mc.aimConstraint(neckJoint, neckTarget,
                                    aim=(0, 1, 0),
                                    u=(0, 0, 1),
                                    wut='objectrotation',
                                    wuo=neckRig['control'],
                                    wu=(0, 0, 1),
                                    mo=False)[0])
            mc.parent(neckTarget, headRig['pivotCompensate'])

            neckUpnode = AddNode.emptyNode(component=self.name, side=self.side, element='neck', specific='upnode')
            Nodes.alignObject(neckUpnode, neckJoint)
            mc.move(0, 0, -Tools.getDistance(headGuide, neckGuide), neckUpnode, relative=True, objectSpace=True)
            
            if self.input_chestName or self.parentNode:
                Nodes.parentConstraint([chestControl, headRig['pivotCompensate']], neckUpnode)
            
            Nodes.aimConstraint(neckTarget, 
                                neckJoint, 
                                upNode=neckUpnode,
                                aimAxis='y',
                                upAxis='z')

            for node in [neckUpnode, headRig['offset'], neckJoint]:
                Nodes.setParent(node, neckRig['control'])
            if self.input_chestName or self.parentNode:
                Nodes.parentConstraint(chestControl, neckRig['offset'])
            
            # neck scaling
            if self.neckScaling:
                mc.parent(headJoint, neckRig['control'])
                mc.setAttr('%s.segmentScaleCompensate' % headJoint, 0)

                distanceRig = Tools.createDistanceDimension(neckJoint, headJoint)

                distanceNode = distanceRig[2]
                Nodes.setParent(distanceRig[0], neckRig['offset'])

                initialLength = mc.getAttr('%s.distance' % (distanceNode))

                initialLength = '$initialLength = %s;\n' % (initialLength)
                scaleFactor = '$scaleFactor = (%s.distance / $initialLength) / %s.globalScale;\n' % (distanceNode, headGroup)
                exprLength = '%s.scaleY = $scaleFactor' % (neckJoint)

                Nodes.exprNode('%s.scaleY' % neckJoint, initialLength + scaleFactor + exprLength, specific='scale')

                if self.neckSquashing:
                    exprSquash = '%s.scaleX = 1.0 / (1+(($scaleFactor-1)*0.5))' % neckJoint
                    Nodes.exprNode('%s.scaleX' % neckJoint, initialLength + scaleFactor + exprSquash, specific='squash')
                    mc.connectAttr('%s.scaleX' % neckJoint, '%s.scaleZ' % neckJoint)
            else:
                mc.parent(headJoint, neckJoint)
            mc.parent([neckRig['offset'], neckJoint], headGroup)
            VisSwitch.connectVisSwitchGroup([neckUpnode, neckTarget], headGroup, displayAttr='setupDisplay')
            VisSwitch.connectVisSwitchGroup([neckJoint], headGroup, displayAttr='jointDisplay')
            VisSwitch.connectVisSwitchGroup([neckRig['control']], headGroup, displayAttr='neckControlDisplay')

        else:
            if self.input_chestName or self.parentNode:
                mc.parentConstraint(chestControl, headRig['offset'], mo=True)
                mc.scaleConstraint(chestControl, headRig['offset'], mo=True)
            Nodes.setParent(headRig['offset'], headGroup)

        if self.spaceNodes != None:

            SpaceSwitch.createSpaceSwitch(offNode=headRig['offset'],
                                        sourceObjs=self.spaceNodes[::],
                                        switchNames=self.spaceNames[::],
                                        translation=False if self.hasNeck else True,
                                        rotation=True if self.hasNeck else False,
                                        scale=False,
                                        spaceAttrName=None if self.hasNeck else 'translationSpace',
                                        defaultSpace=self.defaultSpace)
            if not self.hasNeck:
                SpaceSwitch.createSpaceSwitch(offNode=headRig['offset'],
                                            sourceObjs=self.spaceNodes[::],
                                            switchNames=self.spaceNames[::],
                                            translation=False,
                                            rotation=True,
                                            scale=False,
                                            spaceAttrName=None if self.hasNeck else 'rotationSpace',
                                            defaultSpace=self.defaultSpace)

        VisSwitch.connectVisSwitchGroup([headJoint], headGroup, displayAttr='jointDisplay')
        if self.hasNeck and self.neckScaling:
            VisSwitch.connectVisSwitchGroup(distanceRig, headGroup, displayAttr='setupDisplay')
        VisSwitch.connectVisSwitchGroup([headRig['control']], headGroup, displayAttr='controlDisplay')

        if self.input_chestName or self.parentNode:
            self.connectRig(self.input_chestName, self.input_neckName, headRig, neckRig, chestControl if self.parentNode else None)
            
        return {'head': headRig,
                'neck': neckRig,
                'joints': ([neckJoint] if self.hasNeck else []) + [headJoint], 
                'rigGroup': headGroup}

    def connectRig(self,
                    chestName,
                    neckName,
                    headRig,
                    neckRig,
                    chestControl=None):

        if not chestControl:
            chestControl = Nodes.createName(chestName, side=self.side, nodeType=Settings.controlSuffix)[0]
        neckStartCurveOffset = Nodes.createName(neckName, side=self.side, element='start', nodeType=Settings.offNodeSuffix)[0]
        neckEndCurveOffset = Nodes.createName(neckName, side=self.side, element='end',nodeType=Settings.offNodeSuffix)[0]
        neckMainParent = Nodes.createName(neckName, side=self.side, element='main', nodeType='parent')[0]
        neckFkControlNode = Nodes.createName(neckName, side=self.side, element='fk', indices=0, indexFill=1, nodeType=Settings.controlSuffix)[0]
        neckFkOffNode = Nodes.createName(neckName, side=self.side, element='fk', indices=0, indexFill=1, nodeType=Settings.offNodeSuffix)[0]
        neckGroup = Nodes.createName(neckName, side=self.side, nodeType=Settings.rigGroup)[0]

        chestControl = ConnectionHandling.inputExists(chestControl)
        #neckStartCurveOffset = ConnectionHandling.inputExists(neckStartCurveOffset)
        #neckEndCurveOffset = ConnectionHandling.inputExists(neckEndCurveOffset)
        #neckMainParent = ConnectionHandling.inputExists(neckMainParent)

        if self.hasNeck:
            Tools.parentScaleConstraint(neckRig['control'], neckMainParent)
        else:
            if Nodes.exists(neckFkOffNode):
                Nodes.setParent(neckFkOffNode, neckGroup)
                Tools.parentScaleConstraint(chestControl, neckFkOffNode)
                Tools.parentScaleConstraint(neckFkControlNode, neckMainParent)
            else:
                Tools.parentScaleConstraint(chestControl, neckMainParent)
        Tools.parentScaleConstraint(headRig['pivotCompensate'], neckEndCurveOffset)

        if self.input_neckName:
            Nodes.addAttrTitle(headRig['control'], 'stretch')
            headStretchAttr = headRig['control']+'.'+neckName+'Stretch'
            Nodes.addAttr(headStretchAttr, k=False, d=True)
            neckStretchAttr = Nodes.createName(neckName, side=self.side, nodeType=Settings.rigGroup)[0]+'.'+neckName+'Stretch'
            if Nodes.exists(neckStretchAttr):
                Nodes.connectAttr(neckStretchAttr, headStretchAttr, lock=True)

        lowerParent = Nodes.createName(neckName, side=self.side, element='lower', nodeType='parent')[0]
        Tools.parentScaleConstraint(chestControl, lowerParent)