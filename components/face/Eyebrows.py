# Eyebrows

import maya.cmds as mc

from bear.system import Generic
from bear.system import Guiding
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.system import MessageHandling
from bear.utilities import VisSwitch
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import AttrConnect
from bear.utilities import Nodes
from bear.utilities import NodeOnVertex
from bear.components.basic import Control
from bear.components.basic import Guide
from bear.components.basic import Curve
if Settings.licenseVersion == 'full':
    from bear.utilities import Squash

class Build(Generic.Build):

    def __init__(self,
                name='eyebrow',
                geoNode=None,
                jointCount=8,
                parentNode=Nodes.createName('head', nodeType=Settings.controlSuffix)[0],
                hasCurveRig=True,
                hasSurfaceRig='unsupported' if Settings.licenseVersion == 'free' else True,
                hasFollicleRig='unsupported' if Settings.licenseVersion == 'free' else True,
                hasAnchorRig='unsupported' if Settings.licenseVersion == 'free' else True,
                hasEyebrowMid=True,
                hasJointGuides=True,
                displaySwitch='faceDisplaySwitch',
                *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.geoNode = geoNode if geoNode != '' else None
        self.jointCount = jointCount
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.hasCurveRig = hasCurveRig if jointCount > 0 else False
        self.hasSurfaceRig = hasSurfaceRig
        self.hasFollicleRig = hasFollicleRig
        self.hasAnchorRig = hasAnchorRig
        self.hasEyebrowMid = hasEyebrowMid
        self.hasJointGuides = hasJointGuides
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, 'auto', definition)
        if definition:
            return {'guideGroup': guideGroup}
        
        if self.hasCurveRig:
            curveGuide = Curve.Build(component=self.name, 
                                            side=Settings.leftSide,
                                            controlCount=5, 
                                            jointCount=self.jointCount,
                                            segmenting=True,
                                            hasJointGuides=self.hasJointGuides,
                                            curveType='nurbsCurve',
                                            size=1,
                                            skeletonParent=self.parentNode,
                                            skeletonParentToAllJoints=True).createGuide(definition)
        
            mc.parent(curveGuide['guideGroup'], guideGroup)
            for c, curvePivot in enumerate(curveGuide['guidePivots']):
                mc.move(-6+3*c, 0, 0, curvePivot)
        
        guideNodes = list()
        elementNames = ['main']
        if self.hasEyebrowMid:
            elementNames.append('mid')

        for g, elementName in enumerate(elementNames):

            guide = Guide.createGuide(component=self.name,
                                        element=elementName,
                                        side=None if elementName == 'mid' else Settings.leftSide,
                                        size=1)
            guideNodes.append(guide)
            mc.parent(guide['pivot'], guideGroup)
            mc.move([0, -10][g], 0, 0, guide['pivot'])

        if self.hasAnchorRig == True == True:
            for g, indexName in enumerate([0, 2, 4, 0, None]):
                elementNames = ['upperAnchor',
                                'upperAnchor',
                                'upperAnchor',
                                'lowerAnchor',
                                'center']
                                
                guide = Guide.createGuide(component=self.name, 
                                            side=Settings.leftSide, 
                                            indices=indexName, 
                                            element=elementNames[g],
                                            hasGuideShape=False)['pivot']
                mc.parent(guide, guideGroup)
                if g == 4:
                    mc.move(0, 0, -6, guide)
                elif g == 3:
                    mc.move(-6, -6, 0, guide)
                else:
                    mc.move([-6, 0, 6][g], 6, 0, guide)

        # surface guide
        if self.hasSurfaceRig == True:

            surfaceName = Nodes.createName(self.name, Settings.leftSide, Settings.guideSurfaceSuffix, specific='surfaceNode')
            surfaceGuide = mc.nurbsPlane(name=surfaceName[0])
            mc.setAttr('%s.w'%surfaceGuide[1], lock=True)
            mc.setAttr('%s.lr'%surfaceGuide[1], lock=True)
            mc.setAttr('%s.u'%surfaceGuide[1], lock=True)
            mc.setAttr('%s.v'%surfaceGuide[1], lock=True)
            mc.setAttr('%s.d'%surfaceGuide[1], lock=True)
            Nodes.addNamingAttr(surfaceGuide[0], surfaceName[1])

            mc.setAttr('%s.curvePrecision'%surfaceGuide[0], 12)
            mc.setAttr('%s.curvePrecisionShaded'%surfaceGuide[0], 12)
            mc.parent(surfaceGuide[0], guideGroup)
            mc.rotate(0, -90, 0, '%s.cv[0:*][0:*]'%surfaceGuide[0])
            scaleValue = 8
            mc.scale(scaleValue, scaleValue, scaleValue, '%s.cv[0:*][0:*]'%surfaceGuide[0])
            
        # blendshape guiding
        if self.hasCurveRig:
            for guideNode in [guideNodes[0]['control'], curveGuide['guideControls'][0]]:

                Nodes.addAttrTitle(guideNode, 'blendShape')
                attrName = ['bsh_translateX_neg', 'bsh_translateY_pos', 'bsh_translateY_neg', 'bsh_combine_translateX_neg_translateY_pos', 'bsh_combine_translateX_neg_translateY_neg']
                defaultVal = [3, 5, 5, 0, 0]
                for d in range(len(attrName)):
                    mc.addAttr(guideNode, at='float', ln=attrName[d], k=True, dv=defaultVal[d])
            
            for guideNode in [guideNodes[0]['control'], curveGuide['guideControls'][0], curveGuide['guideControls'][2]]:
                Nodes.addAttrTitle(guideNode, 'blendShape')
            
            for guideNode in [curveGuide['guideControls'][2], curveGuide['guideControls'][4]]:
                
                Nodes.addAttrTitle(guideNode, 'blendShape')
                attrName = ['bsh_translateY_pos', 'bsh_translateY_neg']
                defaultVal = [5, 5]
                for d in range(len(attrName)):
                    mc.addAttr(guideNode, at='float', ln=attrName[d], k=True, dv=defaultVal[d])

        if self.hasEyebrowMid:
            Nodes.addAttrTitle(guideNodes[1]['control'], 'blendShape')
            attrName = ['bsh_translateY_pos', 'bsh_translateY_neg']
            for d in range(len(attrName)):
                mc.addAttr(guideNodes[1]['control'], at='float', ln=attrName[d], k=True, dv=5)

        return {'guideGroup': guideGroup}

    def createRig(self):
        
        guideGroup = Nodes.createName(self.name, nodeType=Settings.guideGroup)[0]

        curveGuide = Nodes.createName(self.name, Settings.leftSide, Settings.guideCurveSuffix)[0]
        mainGuide = Nodes.createName(self.name, Settings.leftSide, Settings.guidePivotSuffix, element='main')[0]
        foreheadGuide = Nodes.createName(self.name, None, Settings.guidePivotSuffix, element='mid')[0]
        anchorGuides = [Nodes.createName(self.name, Settings.leftSide, Settings.guidePivotSuffix, indices=0, element='upperAnchor')[0], 
                    Nodes.createName(self.name, Settings.leftSide, Settings.guidePivotSuffix, indices=2, element='upperAnchor')[0], 
                    Nodes.createName(self.name, Settings.leftSide, Settings.guidePivotSuffix, indices=4, element='upperAnchor')[0],
                    Nodes.createName(self.name, Settings.leftSide, Settings.guidePivotSuffix, indices=0, element='lowerAnchor')[0]]
        surfaceGuide = Nodes.createName(self.name, Settings.leftSide, Settings.guideSurfaceSuffix, element='surfaceNode')[0]
        centerGuide = Nodes.createName(self.name, Settings.leftSide, Settings.guidePivotSuffix, element='center')[0]

        self.jointCount = Guiding.getBuildAttrs(guideGroup, 'jointCount')
        self.hasFollicleRig = Guiding.getBuildAttrs(guideGroup, 'hasFollicleRig')
        self.hasAnchorRig == Guiding.getBuildAttrs(guideGroup, 'hasAnchorRig')

        self.parentNode = ConnectionHandling.inputExists(self.parentNode)

        rigGroup = super(Build, self).createRig(self.name, 'auto')
        controlGroup = AddNode.emptyNode(component=self.name, element='control', nodeType=Settings.rigGroup)
        mc.parent(controlGroup, rigGroup)

        surfaceNodeList = list()
        allConstraintNodes = list()

        controlRigSide = list()
        allJointNodes = list()

        eyebrowMainRigSide = list()

        outerEyebrowRigGroupList = list()

        for side in [Settings.leftSide, Settings.rightSide]:

            follicleJointList = list()
            jointNodeList = list()

            # main node

            mainNode = Tools.mirrorObject(mainGuide) if side == Settings.rightSide else mainGuide
            
            eyebrowMainRig = Control.createControl(node=mainNode,
                                                        side=side)
            Nodes.lockAndHideAttributes(eyebrowMainRig['control'], s=(True, True, True))
            Tools.parentScaleConstraint(self.parentNode, eyebrowMainRig['offset'])
            
            # if curve joint count is 0 or none, we create a skin joint for the main control
            if self.jointCount < 1:
                jointNodeList.append(AddNode.jointNode(eyebrowMainRig['control']))

            eyebrowMainRigSide.append(eyebrowMainRig)

            mc.parent(eyebrowMainRig['offset'], controlGroup)
            
            if self.hasCurveRig:
                if side == Settings.rightSide:
                    curveGuide = Guiding.convertGuide(curveGuide, mirror=True)[0]
                    for c in range(Tools.getCvCount(curveGuide)):
                        Guiding.convertGuide(Nodes.createName(self.name, Settings.leftSide, Settings.guidePivotSuffix, indices=c)[0], mirror=True)[0]

                curveRig = Curve.Build(curveNode=curveGuide,
                                        component=self.name,
                                        side=side,
                                        jointCount=self.jointCount,
                                        squashing=False,
                                        chain=False,
                                        segmenting=True,
                                        hasJointGuides=True,
                                        upAxis='Z',
                                        skeletonParent=self.parentNode,
                                        skeletonParentToAllJoints=True).createRig()

                controlRigSide.append(curveRig)

                for pointLocCtrl in curveRig['controls'][1:]:
                    Nodes.lockAndHideAttributes(pointLocCtrl, r=(True, True, True), s=(True, True, True))
                Nodes.lockAndHideAttributes(curveRig['controls'][0], s=(True, True, True))

            # follicle joints for eyebrow hair template, this is needed as skin is influenced by blendshape and pushes eyebrow out on certain poses

            if self.hasFollicleRig == True and self.hasCurveRig and self.geoNode:
                if not Nodes.exists(self.geoNode):
                    MessageHandling.warning('Geo node does not exist, eyebrow follicle creation skipped')
                for curveJointNode in curveRig['joints']:
                    follicleJoint = AddNode.jointNode(curveJointNode, element='follicle', nodeType=Settings.skinJointSuffix)
                    mc.setAttr('%s.inheritsTransform'%follicleJoint, False)
                    follicleJointList.append(follicleJoint)
                mc.parent(follicleJointList, rigGroup)
                pinLocs = NodeOnVertex.proximityPin(self.geoNode, 
                                            follicleJointList,
                                            createPinLoc=True)[0]
                mc.parent(pinLocs, curveRig['setupGroup'])
                for n, curveJointNode in enumerate(curveRig['joints']):
                    Nodes.orientConstraint(curveJointNode, follicleJointList[n], mo=True)

            # driven attr main control
            if self.hasCurveRig:
                for d, direction in enumerate(['Up', 'Down', 'Out']):
                    inbNodeList = [AddNode.parentNode(pointLocCtrl, nodeType='main'+direction+'Inf', lockScale=True) for pointLocCtrl in curveRig['controls']]
                    for i, inbNode in enumerate(inbNodeList):
                        clampNode = Nodes.clampNode('%s.%s'%(eyebrowMainRig['control'], 'ty'),
                                                    clampMin=[0, None, None][d],
                                                    clampMax=[None, 0, 0][d])
                        Tools.drivenAttr(sourceNode=clampNode, 
                                        sourceAttr='outputR', 
                                        drivenNode=inbNode, 
                                        drivenAttr='translateZ' if d == 2 else 'translateY', 
                                        attrNode=curveRig['controls'][i], 
                                        attrName='main'+direction+'Influence', 
                                        attrTitle='influence',
                                        attrIsKeyable=False,
                                        defaultValue=[0, 0.2, 0.3, 0.2, 0][i] if d == 1 else 0)

                # driven attr sub controls

                for g, groupNode in enumerate([curveRig['controls'][1], curveRig['controls'][3]]):
                    for n, neighbor in enumerate(['neighborInner', 'neighborOuter']):
                        for d, direction in enumerate(['Up', 'Down']):

                            defaultValue = 0
                            if g == 0 and n == 0 and d == 0:
                                defaultValue = 0.5
                            if g == 0 and n == 0 and d == 1:
                                defaultValue = 1.0
                            if g == 0 and n == 1 and d == 1:
                                defaultValue = 0.5
                            if g == 1 and n == 0 and d == 1:
                                defaultValue = 0.5
                            if g == 1 and n == 0 and d == 0:
                                defaultValue = 0.5

                            neighborNode = [[curveRig['controls'][0], curveRig['controls'][2]][n], [curveRig['controls'][2], curveRig['controls'][4]][n]][g]
                            inbNode = AddNode.parentNode(groupNode, nodeType=neighbor+direction+'Inf', lockScale=True)
                            clampNode = Nodes.clampNode('%s.%s'%(neighborNode, 'ty'),
                                                        clampMin=[0, None][d],
                                                        clampMax=[None, 0][d])
                            Tools.drivenAttr(sourceNode=clampNode, 
                                            sourceAttr='outputR', 
                                            drivenNode=inbNode, 
                                            drivenAttr='translateY', 
                                            attrNode=curveRig['controls'][[1, 3][g]], 
                                            attrName=neighbor+direction+'Influence', 
                                            attrTitle='influence',
                                            attrIsKeyable=False,
                                            lowerLimit=0,
                                            defaultValue=defaultValue)
                                            
                AttrConnect.multiGroupConnect([curveRig['rigGroup']], rigGroup)
                
                mc.parent(curveRig['rigGroup'], rigGroup)
                
            if self.hasSurfaceRig == True and self.hasCurveRig:
                
                if self.hasAnchorRig == True:
                    # center joint
                    centerNode = Tools.mirrorObject(centerGuide) if side == Settings.rightSide else centerGuide
                    
                    eyebrowCenterJoint = AddNode.jointNode(centerNode)
                    for axis in 'XYZ':
                        mc.setAttr('%s.jointOrient%s'%(eyebrowCenterJoint, axis), 0)

                    Tools.parentScaleConstraint(self.parentNode, eyebrowCenterJoint, connectRotate=False)
                    midCurveJoint = curveRig['joints'][int(len(curveRig['joints'])/2)-1]
                    mc.aimConstraint(midCurveJoint, eyebrowCenterJoint, aimVector=(-1 if side == Settings.rightSide else 1, 0, 0),
                                    wuo=self.parentNode, wut='objectrotation', u=(0, 1, 0))

                    eyebrowCenterParent = AddNode.parentNode(eyebrowCenterJoint)
                                                                
                    jointNodeList.append(eyebrowCenterJoint)
                    mc.parent(eyebrowCenterParent, controlGroup)

                # surface constraint
                surfaceNode = Guiding.convertGuide(surfaceGuide, mirror=True if side == Settings.rightSide else False, mirrorRotate=(0, 0, 0), nodeType=Settings.surfaceSuffix)[0]
                surfaceNodeList.append(surfaceNode)
                Tools.parentScaleConstraint(self.parentNode, surfaceNode, useMatrix=False)
                mc.parent(surfaceNode, rigGroup)

                constraintNodeList, resultNodeList, inbNodeList = Tools.createSurfaceConstraintConnection([eyebrowMainRig['control']]+curveRig['controls'], 
                                                                                                            surfaceNode, 
                                                                                                            side=side,
                                                                                                            attrNode=eyebrowMainRig['control'],
                                                                                                            attrName='stickToSkull')
                mc.parent(constraintNodeList, rigGroup)
                allConstraintNodes.extend(constraintNodeList)
                mc.parentConstraint(curveRig['controls'][0], curveRig['offsets'][1], mo=True)

                for p, pointLocGroup in enumerate(curveRig['offsets']):
                    if p != 1:
                        mc.parentConstraint(inbNodeList[0], pointLocGroup, mo=True)

            else:
                if self.hasCurveRig:
                    for c, curveOff in enumerate(curveRig['offsets']):
                        if c == 1:
                            Tools.parentScaleConstraint(Nodes.replaceNodeType(curveRig['controls'][0], 'sclCmp'), curveOff)
                        else:
                            Tools.parentScaleConstraint(eyebrowMainRig['scaleCompensate'], curveOff)

            # anchors
            
            if self.hasAnchorRig == True and self.hasCurveRig:
                outerEyebrowRigGroupList = Squash.createBrows(
                    anchorGuides=anchorGuides,
                    curveRig=curveRig,
                    side=side,
                    parentNode=self.parentNode,
                    outerEyebrowRigGroupList=outerEyebrowRigGroupList,
                    rigGroup=rigGroup,
                    )
                
            # first joint orient blend
            if self.hasCurveRig:
                jointMptNode = mc.listRelatives(curveRig['joints'][0], parent=True)[0]
                oriNode = AddNode.inbetweenNode(jointMptNode, nodeType='ori')
                controlSclCmpNode = Nodes.replaceNodeType(curveRig['controls'][0], Settings.scaleCompensateNode)
                Nodes.alignObject(oriNode, controlSclCmpNode, oldStyle=True)
                jointCntNode = AddNode.parentNode(curveRig['joints'][0], nodeType=Settings.cntNodeSuffix)
                if side == Settings.rightSide:
                    mc.rotate(0, 0, 180, oriNode, r=True, os=True)
                Tools.blendBetween([controlSclCmpNode], 
                                    [oriNode], 
                                    [jointCntNode], 
                                    orientConstrained=True, 
                                    attrNode=curveRig['controls'][0],
                                    attrName='tipOrientFollow', 
                                    attrTitle='orient', 
                                    defaultValue=1,
                                    attrIsKeyable=False,
                                    maintainOffset=False)

            allJointNodes.extend(jointNodeList+follicleJointList)

        # eyebrow mid
        if self.hasEyebrowMid:
            pivotGuide = Guiding.getGuideAttr(foreheadGuide)['pivotGuide']
            offset = Guiding.getGuideAttr(foreheadGuide)['offset']

            eyebrowMidRig = Control.createControl(node=pivotGuide,
                                                    component=self.name,
                                                    element='mid')

            jointNode = AddNode.jointNode(eyebrowMidRig['control'], size=offset[2][0] * 0.5, nodeType=Settings.skinJointSuffix)
            jointNodeList.append(jointNode)
            allJointNodes.append(jointNode)

            Tools.parentScaleConstraint(self.parentNode, eyebrowMidRig['offset'])
            mc.parent(eyebrowMidRig['offset'], controlGroup)

            cntNode = AddNode.inbetweenNode(eyebrowMidRig['offset'])
            
            if self.hasCurveRig:
                if self.hasSurfaceRig == True:
                    parentCnt = mc.parentConstraint([Nodes.replaceNodeType(controlRigSide[0]['controls'][0], 'surfaceConstraint'), 
                                    Nodes.replaceNodeType(controlRigSide[1]['controls'][0], 'surfaceConstraint')],
                                    cntNode, maintainOffset=True)[0]
                    mc.setAttr('%s.interpType'%parentCnt, 2)
                else:
                    mc.pointConstraint([Nodes.replaceNodeType(controlRigSide[0]['controls'][0], Settings.scaleCompensateNode), 
                                        Nodes.replaceNodeType(controlRigSide[1]['controls'][0], Settings.scaleCompensateNode)],
                                        cntNode, maintainOffset=True)
                [Nodes.removeConnection('%s.translate%s'%(cntNode, axis)) for axis in 'XZ']

                blendNode = AddNode.inbetweenNode(cntNode, 'blend')
                Tools.blendBetween([eyebrowMidRig['offset']],
                                    [cntNode],
                                    [blendNode],
                                    attrNode=eyebrowMidRig['control'],
                                    attrName='followEyebrows',
                                    attrTitle='follow',
                                    defaultValue=0,
                                    attrIsKeyable=False)

        VisSwitch.connectVisSwitchGroup(surfaceNodeList + allConstraintNodes, rigGroup, displayAttr='setupDisplay')
        VisSwitch.connectVisSwitchGroup(allJointNodes, rigGroup, displayAttr='jointDisplay')
        controls = [eyebrowMainRigSide[0]['control'], eyebrowMainRigSide[1]['control']]
        if self.hasCurveRig:
            controls.extend([controlRigSide[0]['controls'], controlRigSide[1]['controls']])
        if self.hasEyebrowMid:
            controls.append(eyebrowMidRig['control'])
        VisSwitch.connectVisSwitchGroup(controls,
                                        rigGroup, 
                                        displayAttr='controlDisplay')
        VisSwitch.connectVisSwitchGroup(outerEyebrowRigGroupList,
                                        rigGroup, 
                                        displayAttr='squashControlDisplay', 
                                        forceConnection=True)
            
        self.cleanup(Nodes.replaceNodeType(rigGroup, 'guide'), trashGuides=True, removeRightGuides=True, hierarchy=False, display=False, selectionSets=False)

        return {
            'rigGroup': rigGroup, 
            'joints': jointNodeList,
            'midControl': eyebrowMidRig['control'],
            'leftControls': controlRigSide[0]['controls'] if self.hasCurveRig else None,
            'rightControls': controlRigSide[1]['controls'] if self.hasCurveRig else None,
            }