# Spine

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.system import Guiding
from bear.utilities import Tools
from bear.utilities import VisSwitch
from bear.utilities import AddNode
from bear.utilities import AttrConnect
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.basic import Guide
from bear.components.basic import Curve

class Build(Generic.Build):

    def __init__(self,
                    name='spine',
                    side=None,
                    jointCount=6, 
                    bellyControlCount=0,
                    hasFkRig=True,
                    hasReverseRig=True,
                    isNeck=False,
                    lengthAxis='Y',
                    upAxis='Z',
                    hasJointGuides=False,
                    defaultAlignment='biped',
                    parentNode=Nodes.createName('body', nodeType=Settings.skinJointSuffix, element='hips')[0],
                    displaySwitch='bodyDisplaySwitch',
                    *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.jointCount = jointCount
        self.bellyControlCount = bellyControlCount
        self.controlCount = 4
        self.fkCount = 4
        self.revFkCount = 4
        self.hasFkRig = hasFkRig
        self.hasReverseRig = hasReverseRig
        self.hasLowerParent = not isNeck
        self.isNeck = isNeck
        self.lengthAxis = lengthAxis
        self.upAxis = upAxis
        self.hasJointGuides = hasJointGuides
        self.defaultAlignment = defaultAlignment
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):

        guideGroup = super(Build, self).createGuide(self.name, self.side, definition)
        if definition:
            return {'guideGroup': guideGroup}
        
        curveGuide = Curve.Build(component=self.name,
                                side=self.side,
                                controlCount=self.controlCount,
                                jointCount=self.jointCount,
                                lengthAxis=self.lengthAxis,
                                alignAxis=self.lengthAxis,
                                upAxis=self.upAxis,
                                indexFill=1,
                                hasJointGuides=self.hasJointGuides).createGuide(definition)

        for c, curvePivot in enumerate(curveGuide['guidePivots']):
            if self.defaultAlignment == 'biped':
                tOffset = [0, c*10, 0]
                rOffset = [0, 0, 0]
            if self.defaultAlignment == 'bipedNeck':
                tOffset = [0, c*(10.0/3), 0]
                rOffset = [0, 0, 0]
            if self.defaultAlignment == 'quadruped':
                tOffset = [0, 0, -30+c*20]
                rOffset = [90, 0, 0]
            if self.defaultAlignment == 'quadrupedNeck':
                tOffset = [0, 0, c*10]
                rOffset = [90, 0, 0]
            [mc.setAttr('%s.t%s'%(curvePivot, axis), tOffset[a]) for a, axis in enumerate('xyz')]
            [mc.setAttr('%s.r%s'%(curvePivot, axis), rOffset[a]) for a, axis in enumerate('xyz')]

            if c == 1:
                mc.addAttr(curveGuide['guideControls'][c], at='float', ln='midShapeSize', k=True, dv=1.0)
            if c == 2:
                mc.addAttr(curveGuide['guideControls'][c], at='float', ln='upperShapeSize', k=True, dv=1.0)

            mc.addAttr(curveGuide['guideControls'][c], at='enum', ln='fkShape', k=True, enumName=':'+':'.join(Settings.shapes), dv=Settings.shapes.index('Circle'))
            mc.addAttr(curveGuide['guideControls'][c], at='enum', ln='fkColor', k=True, enumName=':'+':'.join(['Default']+Settings.colors), dv=Settings.colors.index('Bright Orange'))
            mc.addAttr(curveGuide['guideControls'][c], at='float', ln='fkShapeSize', k=True, dv=1.1)
            mc.addAttr(curveGuide['guideControls'][c], at='enum', ln='reverseFkShape', k=True, enumName=':'+':'.join(Settings.shapes), dv=Settings.shapes.index('Rectangle'))
            mc.addAttr(curveGuide['guideControls'][c], at='enum', ln='reverseFkColor', k=True, enumName=':'+':'.join(['Default']+Settings.colors), dv=Settings.colors.index('Purple'))
            mc.addAttr(curveGuide['guideControls'][c], at='float', ln='reverseFkShapeSize', k=True, dv=1.2)
        
        if self.bellyControlCount:
            for n in range(self.bellyControlCount):
                bellyGuide = Guide.createGuide(component=self.name,
                                                            element='belly',
                                                            side=self.side,
                                                            indices=None if self.bellyControlCount == 1 else n)
                if self.defaultAlignment == 'biped':
                    mc.move(0, (self.jointCount/2)+10, 10, bellyGuide['pivot'])
                if self.defaultAlignment == 'bipedNeck':
                    mc.move(0, (self.jointCount/2), 10, bellyGuide['pivot'])
                if self.defaultAlignment == 'quadruped':
                    mc.move(0, (self.jointCount/2)-10, 0, bellyGuide['pivot'])
                if self.defaultAlignment == 'quadrupedNeck':
                    mc.move(0, (self.jointCount/2), 10, bellyGuide['pivot'])

                mc.setAttr('%s.parentNode'%bellyGuide['control'], self.name+'_02_'+Settings.skinJointSuffix, type='string')
                mc.setAttr('%s.parentType'%bellyGuide['control'], 'Constraint', type='string')

                mc.parent(bellyGuide['pivot'], guideGroup)

        return {'guideGroup': guideGroup}
            
    def createRig(self):

        curveGuide = Nodes.createName(component=self.name, nodeType=Settings.guideCurveSuffix)[0]
        bellyGuides = list()
        if self.bellyControlCount:
            for n in range(self.bellyControlCount):
                bellyGuides.append(Nodes.createName(component=self.name, 
                                                    side=self.side, 
                                                    element='belly', 
                                                    indices=None if self.bellyControlCount == 1 else n, 
                                                    nodeType=Settings.guidePivotSuffix)[0])

        curveGuides = [Nodes.createName(component=self.name, side=self.side, indices=x, indexFill=1, nodeType=Settings.guidePivotSuffix)[0] for x in range(4)]
        curveGuideValues = [Guiding.getGuideAttr(x) for x in curveGuides]
        
        curveRig = Curve.Build(curveNode=curveGuide,
                                component=self.name,
                                side=self.side,
                                size=10,
                                indexFill=1,
                                controlCount=self.controlCount,
                                jointCount=self.jointCount,
                                segmenting=True,
                                lengthAxis=self.lengthAxis,
                                upAxis=self.upAxis,
                                skeletonParent=self.parentNode).createRig()
        
        mc.hide(curveRig['offsets'][0])
        mc.hide(curveRig['offsets'][-1])

        midSize = Guiding.getGuideAttr(Nodes.replaceNodeType(curveRig['controls'][1], Settings.guidePivotSuffix), specialAttr='midShapeSize')
        mc.scale(midSize, midSize, midSize, '%s.cv[*]'%curveRig['controls'][1], os=True, r=True)
        upperSize = Guiding.getGuideAttr(Nodes.replaceNodeType(curveRig['controls'][2], Settings.guidePivotSuffix), specialAttr='upperShapeSize')
        mc.scale(upperSize, upperSize, upperSize, '%s.cv[*]'%curveRig['controls'][2], os=True, r=True)

        spineGroup = curveRig['rigGroup']

        startControlName = Nodes.createName(component=self.name, side=self.side, element='start', nodeType=Settings.controlSuffix)
        lowerControlName = Nodes.createName(component=self.name, side=self.side, element='lower', nodeType=Settings.controlSuffix)
        upperControlName = Nodes.createName(component=self.name, side=self.side, element='upper', nodeType=Settings.controlSuffix)
        endControlName = Nodes.createName(component=self.name, side=self.side, element='end', nodeType=Settings.controlSuffix)
        startOffsetName = Nodes.createName(component=self.name, side=self.side, element='start', nodeType=Settings.offNodeSuffix)
        lowerOffsetName = Nodes.createName(component=self.name, side=self.side, element='lower', nodeType=Settings.offNodeSuffix)
        upperOffsetName = Nodes.createName(component=self.name, side=self.side, element='upper', nodeType=Settings.offNodeSuffix)
        endOffsetName = Nodes.createName(component=self.name, side=self.side, element='end', nodeType=Settings.offNodeSuffix)
        AddNode.replaceTempNode(startControlName[0])
        AddNode.replaceTempNode(lowerControlName[0])
        AddNode.replaceTempNode(upperControlName[0])
        AddNode.replaceTempNode(endControlName[0])
        AddNode.replaceTempNode(startOffsetName[0])
        AddNode.replaceTempNode(lowerOffsetName[0])
        AddNode.replaceTempNode(upperOffsetName[0])
        AddNode.replaceTempNode(endOffsetName[0])
        Nodes.rename(curveRig['controls'][0], startControlName[0], startControlName[1])
        Nodes.rename(curveRig['controls'][1], lowerControlName[0], lowerControlName[1])
        Nodes.rename(curveRig['controls'][2], upperControlName[0], upperControlName[1])
        Nodes.rename(curveRig['controls'][3], endControlName[0], endControlName[1])
        Nodes.rename(curveRig['offsets'][0], startOffsetName[0], startOffsetName[1])
        Nodes.rename(curveRig['offsets'][1], lowerOffsetName[0], lowerOffsetName[1])
        Nodes.rename(curveRig['offsets'][2], upperOffsetName[0], upperOffsetName[1])
        Nodes.rename(curveRig['offsets'][3], endOffsetName[0], endOffsetName[1])
        curveRig['controls'][0] = startControlName[0]
        curveRig['controls'][1] = lowerControlName[0]
        curveRig['controls'][2] = upperControlName[0]
        curveRig['controls'][3] = endControlName[0]
        curveRig['offsets'][0] = startOffsetName[0]
        curveRig['offsets'][1] = lowerOffsetName[0]
        curveRig['offsets'][2] = upperOffsetName[0]
        curveRig['offsets'][3] = endOffsetName[0]

        # spine stretch attr connect

        for n in [1, 2]:
            Nodes.addAttrTitle(curveRig['controls'][n], 'stretch')
            Nodes.addAttr(curveRig['controls'][n]+'.'+self.name+'Stretch', k=False, d=True)
            Nodes.connectAttr(curveRig['rigGroup']+'.'+self.name+'Stretch', curveRig['controls'][n]+'.'+self.name+'Stretch', lock=True)

        # belly
        
        if len(bellyGuides) > 0:
            if mc.objExists(bellyGuides[0]):
                for n, bellyGuide in enumerate(bellyGuides):
                    bellyRig = Control.createControl(node=bellyGuide)
                    bellyShapeGuide = Nodes.replaceNodeType(bellyGuide, Settings.guideShapeSuffix)
                    bellyJoint = AddNode.jointNode(bellyRig['control'], skeletonParent=mc.getAttr('%s.parentNode'%bellyShapeGuide))
                    mc.parent(bellyRig['offset'], spineGroup)

                    VisSwitch.connectVisSwitchGroup([bellyJoint], spineGroup, displayAttr='jointDisplay')
                    VisSwitch.connectVisSwitchGroup([bellyRig['control']], spineGroup, displayAttr='bellyControlDisplay')

        # stretch&squash attribute mapping

        Nodes.addAttrTitle(curveRig['controls'][1], 'squash')
        AttrConnect.copyAttr(curveRig['rigGroup'], curveRig['controls'][1], attr='startSquash')
        AttrConnect.copyAttr(curveRig['rigGroup'], curveRig['controls'][1], attr='midSquash')
        AttrConnect.copyAttr(curveRig['rigGroup'], curveRig['controls'][1], attr='midPosition')
        AttrConnect.copyAttr(curveRig['rigGroup'], curveRig['controls'][1], attr='endSquash')

        def alignToSpine(node, upnode, ikCurve, segCount, segNum):

            pathDummy = mc.spaceLocator()[0]

            motionPath = mc.shadingNode('motionPath', asUtility=True)
        
            mc.connectAttr('%s.worldSpace[0]'%ikCurve, '%s.geometryPath'%motionPath)
            mc.connectAttr('%s.allCoordinates'%motionPath, '%s.translate'%node)
            mc.connectAttr('%s.rotate'%motionPath, '%s.rotate'%node)
            mc.connectAttr('%s.rotateOrder'%motionPath, '%s.rotateOrder'%node)
            mc.setAttr('%s.fractionMode'%motionPath, True)
            mc.setAttr('%s.worldUpType'%motionPath, 2)
            mc.setAttr('%s.worldUpVectorX'%motionPath, 0)
            mc.setAttr('%s.worldUpVectorY'%motionPath, 0)
            mc.setAttr('%s.worldUpVectorZ'%motionPath, 1)
            mc.connectAttr('%s.worldMatrix[0]'%upnode, '%s.worldUpMatrix'%motionPath)
            mc.setAttr('%s.frontAxis'%motionPath, 1)
            mc.setAttr('%s.upAxis'%motionPath, 2)

            mc.setAttr('%s.uValue' % (motionPath), (1.0 / segCount) * segNum)

            Nodes.alignObject(node, pathDummy)
            mc.delete([pathDummy, motionPath])

        mainParent = AddNode.emptyNode(curveRig['controls'][0], indices='remove', component=self.name, element='main', nodeType='parent', parentNode=spineGroup)

        # fkNodes

        if self.hasFkRig:

            fkRigs = list()

            for f in range(self.fkCount):
                size = Guiding.getGuideAttr(curveGuides[f], specialAttr='fkShapeSize')
                fkRig = Control.createControl(component=self.name,
                                                element='fk',
                                                indices=f,
                                                indexFill=1,
                                                side=self.side,
                                                parentNode=None,
                                                deleteNode=True,
                                                shape=Guiding.getGuideAttr(curveGuides[f], attrPrefix='fk')['shape'],
                                                color=Guiding.getGuideAttr(curveGuides[f], attrPrefix='fk')['color'],
                                                offset=[curveGuideValues[f]['offset'][0], curveGuideValues[f]['offset'][1], 
                                                        [curveGuideValues[f]['offset'][2][0]*size,
                                                        curveGuideValues[f]['offset'][2][1]*size,
                                                        curveGuideValues[f]['offset'][2][2]*size]],
                                                ignoreMissingGuideControlWarning=True)

                alignToSpine(node=fkRig['offset'], upnode=curveRig['controls'][0], ikCurve=curveRig['curve'], segCount=self.fkCount-1, segNum=f)
                fkRigs.append(fkRig)

                Nodes.lockAndHideAttributes(fkRig['control'], t=[False, False, False], r=[False, False, False], s=[True, True, True], v=True)

            for f, fkRig in enumerate(reversed(fkRigs)):
                if f > 0:
                    mc.parent(fkRigs[-f]['offset'], fkRig['control'])

            mc.parent(curveRig['offsets'][-1], fkRigs[-1]['control'])
            mc.parent(fkRigs[0]['offset'], mainParent)

            VisSwitch.connectVisSwitchGroup([x['control'] for x in fkRigs], spineGroup, displayAttr='fkControlDisplay')
        else:
            fkRigs = None

        # middle blends

        Tools.blendBetween([fkRigs[0]['control'] if self.hasFkRig else curveRig['controls'][0]], [curveRig['controls'][-1]], [curveRig['offsets'][-2]], 
                            attrNode=curveRig['controls'][-2],
                            attrName='followHead' if self.isNeck else 'followChest',
                            attrTitle='follow',
                            defaultValue=0.5)

        if self.hasLowerParent:
            lowerParent = AddNode.emptyNode(curveRig['controls'][0], indices='remove', component=self.name, element='lower', nodeType='parent', parentNode=spineGroup)
            Nodes.setParent(curveRig['offsets'][0], lowerParent)
        else:
            lowerParent = None
            Nodes.setParent(curveRig['offsets'][0], mainParent)
        Tools.blendBetween([mainParent], [lowerParent if self.hasLowerParent else curveRig['controls'][-1]], [curveRig['offsets'][1]], 
                            attrNode=curveRig['controls'][1],
                            attrName='followChest' if self.isNeck else 'followHips',
                            attrTitle='follow',
                            defaultValue=0.5)

        # revFkRig

        if self.hasReverseRig:

            revFkRigs = list()

            for f in range(self.revFkCount):
                size = Guiding.getGuideAttr(curveGuides[f], specialAttr='reverseFkShapeSize')
                revFkRig = Control.createControl(component=self.name,
                                                    element='revFk',
                                                    indices=f,
                                                    indexFill=1,
                                                    side=self.side,
                                                    parentNode=None,
                                                    deleteNode=True,
                                                    shape=Guiding.getGuideAttr(curveGuides[f], attrPrefix='reverseFk')['shape'],
                                                    color=Guiding.getGuideAttr(curveGuides[f], attrPrefix='reverseFk')['color'],
                                                    offset=[curveGuideValues[f]['offset'][0], curveGuideValues[f]['offset'][1], 
                                                            [curveGuideValues[f]['offset'][2][0]*size,
                                                            curveGuideValues[f]['offset'][2][1]*size,
                                                            curveGuideValues[f]['offset'][2][2]*size]],
                                                    ignoreMissingGuideControlWarning=True)

                alignToSpine(node=revFkRig['offset'], upnode=curveRig['controls'][0], ikCurve=curveRig['curve'], segCount=self.revFkCount-1, segNum=self.revFkCount-1-f)
                revFkRigs.append(revFkRig)

                Nodes.lockAndHideAttributes(revFkRig['control'], t=[False, False, False], r=[False, False, False], s=[True, True, True], v=True)

            for f, revFkRig in enumerate(reversed(revFkRigs)):
                if f > 0:
                    mc.parent(revFkRigs[0 - f]['offset'], revFkRig['control'])
            
            #if self.hasLowerParent:
                #Tools.parentScaleConstraint(revFkRigs[-1]['control'], lowerParent)

            mc.parent(revFkRigs[0]['offset'], mainParent)
            VisSwitch.connectVisSwitchGroup([x['control'] for x in revFkRigs], spineGroup, displayAttr='revFkControlDisplay')
        else:
            revFkRigs = None
        
        mc.deleteAttr(spineGroup, attribute='controlDisplay')
        VisSwitch.connectVisSwitchGroup([curveRig['controls'][1]], spineGroup, displayAttr='lowerControlDisplay')
        VisSwitch.connectVisSwitchGroup([curveRig['controls'][2]], spineGroup, displayAttr='upperControlDisplay')

        mc.select(clear=True)

        return {'lowerParent': lowerParent,
                'mainParent': mainParent,
                'curveRig': curveRig,
                'fkRigs': fkRigs,
                'revFkRigs': revFkRigs,
                'rigGroup': spineGroup,
                'name': self.name}