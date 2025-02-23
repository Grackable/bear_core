# Curve

import maya.cmds as mc

from bear.system import ConnectionHandling
from bear.system import MessageHandling
from bear.system import Generic
from bear.system import Settings
from bear.utilities import Tools
from bear.utilities import VisSwitch
from bear.utilities import AddNode
from bear.utilities import AnimFunctions
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):

    def __init__(self,
                    curveNode=None,
                    component=None,
                    side=None,
                    element=None,
                    index=None,
                    indexFill=2,
                    jointIndexFill=2,
                    size=10,
                    shape='Circle',
                    jointCount=None,
                    controlCount=6,
                    color='Default',
                    secondaryDefaultColor=False,
                    curveType='nurbsCurve',
                    alignAxis='x',
                    upAxis='y',
                    lengthAxis='x',
                    mirrorAxis=None,
                    offset=[[0, 0, 0], [0, 0, 0], [1, 1, 1]],
                    useGuideAttr=True,
                    closedCurve=False,
                    squashing=True,
                    scaling=True,
                    hasSinusWaveScaling=False,
                    hasSinusWaveTranslation=False,
                    chain=False,
                    segmenting=False,
                    controlPerJoint=False,
                    hasJointGuides=False,
                    upnode=None,
                    flipOrientation=False,
                    alignNodes=None,
                    visGroup=None,
                    parentNode=None,
                    hasJointRig=True,
                    ignoreMissingGuideControlWarning=True,
                    postDeformAlignment=False,
                    skeletonParent=None,
                    skeletonParentToAllJoints=False,
                    skeletonParentToFirst=False,
                    *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.curveNode = curveNode
        self.component = component
        self.side = side
        self.element = element
        self.index = index
        self.size = size
        self.shape = shape
        self.jointCount = jointCount
        self.controlCount = controlCount
        self.color = color
        self.secondaryDefaultColor = secondaryDefaultColor
        self.curveType = curveType
        self.alignAxis = alignAxis.lower() if alignAxis else None
        self.lengthAxis = lengthAxis.lower() if lengthAxis else None
        self.upAxis = upAxis.lower() if upAxis else None
        self.mirrorAxis = mirrorAxis.lower() if mirrorAxis else None
        self.offset = offset
        self.useGuideAttr = useGuideAttr
        self.closedCurve = closedCurve
        self.squashing = squashing
        self.scaling = scaling
        self.hasSinusWaveScaling = hasSinusWaveScaling
        self.hasSinusWaveTranslation = hasSinusWaveTranslation
        self.chain = chain
        self.segmenting = segmenting
        self.controlPerJoint = controlPerJoint
        self.hasJointGuides = hasJointGuides
        self.upnode = upnode
        self.flipOrientation = flipOrientation
        self.alignNodes = alignNodes
        self.visGroup = visGroup
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.hasJointRig = hasJointRig if self.jointCount else False
        self.ignoreMissingGuideControlWarning = ignoreMissingGuideControlWarning
        self.postDeformAlignment = postDeformAlignment
        self.skeletonParent = skeletonParent
        self.skeletonParentToAllJoints = skeletonParentToAllJoints
        self.skeletonParentToFirst = skeletonParentToFirst
        self.indexFill = indexFill
        self.jointIndexFill = jointIndexFill
        self.isGuide = None
        self.initialLength = None

    def createGuide(self, definition):
        
        self.isGuide = True

        self.guideGroup = AddNode.compNode(component=self.component, 
                                            side=self.side, 
                                            nodeType=Settings.guideGroup, 
                                            element=self.element, 
                                            indices=self.index, 
                                            parentNode=Settings.guideRoot,
                                            sourceNode=self.curveNode)

        if definition:
            return {'guideGroup': self.guideGroup}

        if self.controlCount < 2:
            MessageHandling.warning('controlCount is too low, minimum 2 controls are required.')
            MessageHandling.insufficientGuideInputs()
            return {'guideGroup': self.guideGroup}
            
        self.curveNode, self.cvCount = Nodes.curveNode(self.component, 
                                                        side=self.side, 
                                                        nodeType=Settings.guideCurveSuffix, 
                                                        element=self.element, 
                                                        indices=self.index,
                                                        pointCount=self.controlCount,
                                                        alignAxis=self.alignAxis,
                                                        curveType=self.curveType,
                                                        sourceNode=self.curveNode)

        allPivotGuides = None
        
        self.createCurveControls()
        
        if self.curveType == 'bezierCurve':
            bezierPivotGuideList = [mc.pickWalk(x, d='up')[0] for x in self.bezierHandleGroups]
        else:
            bezierPivotGuideList = None
        pivotGuideList = [mc.pickWalk(x, d='up')[0] for x in self.offs]
        allPivotGuides = list()
        step = 0
        for i, pivotGuide in enumerate(pivotGuideList[:-1]):
            allPivotGuides.append(pivotGuide)
            if self.curveType == 'bezierCurve':
                allPivotGuides.append(bezierPivotGuideList[i+step])
                allPivotGuides.append(bezierPivotGuideList[i+1+step])
                step =+ 1
        allPivotGuides.append(pivotGuideList[-1])
        
        if self.jointCount:
            self.jointGroup = AddNode.emptyNode(node=self.curveNode,
                                                component=self.component, 
                                                side=self.side, 
                                                nodeType=Settings.guideGroup,
                                                element=self.element,
                                                indices=self.index,
                                                specific='joints')
            mc.setAttr('%s.inheritsTransform'%self.jointGroup, False)
            if self.hasJointGuides and self.jointCount:
                self.createJointGuides(size=self.size*0.5)
            mc.parent(self.jointGroup, self.guideGroup)
        
        Nodes.lockAndHideAttributes(self.curveNode, t=[True, True, True], r=[True, True, True], s=[True, True, True])
        mc.parent([self.controlGroup, self.setupGroup], self.guideGroup)

        if self.jointCount:
            for i in range(self.jointCount):
                jointName = Nodes.createName(self.component, 
                                                self.side, 
                                                Settings.skinJointSuffix, 
                                                element=self.element, 
                                                indices=[self.index, i], 
                                                indexFill=self.jointIndexFill, 
                                                sourceNode=self.curveNode)
                ConnectionHandling.addOutput(self.guideGroup, jointName[0])

        mc.addAttr(self.curveNode, at='bool', ln='segmenting', dv=self.segmenting, k=False)

        return {'curve': self.curveNode, 
                'guidePivots': pivotGuideList, 
                'guideBezierPivots': bezierPivotGuideList,
                'guideControls': self.controls,
                'guideOffsets': self.offs,
                'guideJoints': self.guideJoints if self.hasJointGuides else None,
                'controlGroup': self.controlGroup,
                'guideGroup': self.guideGroup}

    def createJointGuides(self, jointGroup=None, size=5):

        self.guideJoints = list()
        self.isGuide = True

        if jointGroup != None:
            self.jointGroup = jointGroup

        if not mc.objExists(self.jointGroup) and self.jointCount:
            self.jointGroup = AddNode.emptyNode(node=self.curveNode,
                                                component=self.component, 
                                                side=self.side, 
                                                nodeType=Settings.guideGroup, 
                                                element=self.element,
                                                indices=self.index,
                                                specific='joints')
            self.guideGroup = Nodes.createName(self.component, 
                                                self.side, 
                                                Settings.guideGroup, 
                                                self.element, 
                                                self.index, 
                                                sourceNode=self.curveNode)[0]
            mc.setAttr('%s.inheritsTransform'%self.jointGroup, False)
            mc.parent(self.jointGroup, self.guideGroup)

        for j in range(self.jointCount):

            guide = Guide.createGuide(component=self.component,
                                        size=size,
                                        indices=[self.index, j],
                                        element=self.element,
                                        specific='joint',
                                        indexFill=self.jointIndexFill,
                                        side=self.side,
                                        hasGuideShape=False,
                                        pivotColor='Bright Blue')
            mc.parent(guide['pivot'], self.jointGroup)
            self.guideJoints.append(guide['pivot'])
            
            self.attachNodeToCurve(guide['pivot'],
                                    j,
                                    self.jointCount,
                                    upnode=self.upnode,
                                    upnodeType='object',
                                    createPositionAttr=True,
                                    alignByGuide=False)
            
            mc.setAttr('%s.displayLocalAxis' % (guide['pivot']), False)
            
    def createRig(self):

        self.isGuide = False

        self.rigGroup = AddNode.compNode(component=self.component, 
                                        side=self.side, 
                                        nodeType=Settings.rigGroup, 
                                        element=self.element, 
                                        indices=self.index, 
                                        parentNode=Settings.rigRoot,
                                        sourceNode=self.curveNode)
        guideCurve = Nodes.createName(self.component, 
                                        self.side, 
                                        Settings.guideCurveSuffix, 
                                        self.element, 
                                        self.index, 
                                        None, 
                                        sourceNode=self.curveNode)[0]

        if not mc.objExists(guideCurve):
            guideCurve = self.curveNode
        deleteGuideCurve = False
        if not guideCurve:
            guideCurve, self.cvCount = Nodes.curveNode(self.component, 
                                                            side=self.side, 
                                                            nodeType=Settings.guideCurveSuffix, 
                                                            element=self.element, 
                                                            indices=self.index,
                                                            pointCount=self.controlCount,
                                                            alignAxis=self.alignAxis,
                                                            curveType=self.curveType,
                                                            sourceNode=self.curveNode)
            deleteGuideCurve = True
        if not guideCurve:
            mc.error('No guide found: '+self.component)
            return
        self.curveType = mc.objectType(mc.listRelatives(guideCurve, shapes=True)[0])
        self.cvCount = len(mc.getAttr('%s.cv[*]' % guideCurve))
        self.controlCount = self.cvCount if self.curveType == 'nurbsCurve' else (self.cvCount+2)/3

        self.curveInfoNode = None
        
        self.curveNode = mc.duplicate(guideCurve, name=Nodes.replaceNodeType(guideCurve, Settings.curveSuffix))[0]

        if deleteGuideCurve:
            mc.delete(guideCurve)

        self.numSpans = mc.getAttr('%s.spans' % self.curveNode)
        
        self.createCurveControls()
        
        if self.hasJointRig:
                
            self.createOrientLocs()
            
            self.orientGroup = AddNode.emptyNode(node=self.curveNode,
                                                    component=self.component, 
                                                    side=self.side, 
                                                    nodeType=Settings.rigGroup,
                                                    element=self.element,
                                                    indices=self.index,
                                                    specific='orientLocs')
            mc.parent(self.orientLocs, self.orientGroup)

            self.jointGroup = AddNode.emptyNode(node=self.curveNode,
                                                component=self.component, 
                                                side=self.side, 
                                                nodeType=Settings.rigGroup,
                                                element=self.element,
                                                indices=self.index,
                                                specific='joints')            

            mc.parent([self.jointGroup, self.orientGroup], self.setupGroup)

            self.createJoints()
            
            if self.controlPerJoint:
                mc.parent(self.jointCnts, self.controlGroup)
            else:
                mc.parent(self.jointCnts, self.jointGroup)

            if self.chain:
                self.createChainConstraints()
            
            if self.squashing:
                self.createSquash()
            else:
                for c, cntNode in enumerate(self.jointCnts):
                    if self.scaling:
                        [mc.connectAttr('%s.s%s' % (self.orientLocs[c], axis), '%s.s%s' % (cntNode, axis)) for axis in 'xyz']
                    else:
                        [mc.connectAttr('%s.globalScale' % self.rigGroup, '%s.s%s' % (cntNode, axis)) for axis in 'xyz']
        
        if self.hasSinusWaveTranslation:
            sinusWave = AnimFunctions.createSinusWave(self.clusters, 
                                                        self.rigGroup,
                                                        attribute='translate',
                                                        axis='XYZ'.replace(self.lengthAxis.upper(), ''))
        else:
            sinusWave = None
        
        mc.setAttr('%s.inheritsTransform' % self.curveNode, 0)
        if self.hasJointRig:
            mc.setAttr('%s.inheritsTransform' % self.jointGroup, 0)
            VisSwitch.connectVisSwitchGroup([self.orientGroup], self.rigGroup, displayAttr='setupDisplay')
            VisSwitch.connectVisSwitchGroup(self.joints, self.rigGroup, displayAttr='jointDisplay')
    
        VisSwitch.connectVisSwitchGroup([self.curveNode], self.rigGroup, displayAttr='setupDisplay')
        VisSwitch.connectVisSwitchGroup(self.controls, self.rigGroup,
                                        displayAttr='controlDisplay', visGroup=self.visGroup)
        if self.bezierHandleControls != []:
            VisSwitch.connectVisSwitchGroup(self.bezierHandleControls, self.rigGroup,
                                            displayAttr='bezierHandleControlDisplay', 
                                            visGroup=None if self.visGroup == None else self.visGroup+'Bezier')
        if self.controlPerJoint and self.hasJointRig:
            VisSwitch.connectVisSwitchGroup(self.jointControls, self.rigGroup, displayAttr='singleControlDisplay',
            visGroup=None if self.visGroup == None else self.visGroup+'Single')

        if self.parentNode and Nodes.getObjectType(self.parentNode) != 'mesh':
            Tools.parentScaleConstraint(self.parentNode, self.controlGroup)
        
        for offNode in self.offs:
            if self.parentNode:
                if Nodes.getObjectType(self.parentNode) == 'mesh':
                    Tools.parentToClosestVertex(offNode, self.parentNode, parentNode=self.rigGroup, parentType='Hierarchy')
        
        mc.parent([self.controlGroup, self.setupGroup], self.rigGroup)
        
        return {'controls': self.controls, 
                'offsets': self.offs, 
                'controlRigs': self.controlRigs,
                'controlGroup': self.controlGroup, 
                'setupGroup': self.setupGroup, 
                'orientGroup': self.orientGroup if self.hasJointRig else None, 
                'curve': self.curveNode, 
                'rigGroup': self.rigGroup, 
                'joints': self.joints if self.hasJointRig else None, 
                'motionPathNodes': self.jointCnts if self.hasJointRig else None,
                'bezierHandleControls': self.bezierHandleControls, 
                'bezierHandleOffsets': self.bezierHandleGroups, 
                'singleControls': self.jointControls if self.hasJointRig else None, 
                'orientConstraints': self.orientConstraints if self.hasJointRig else None, 
                'scaleConstraints': self.scaleConstraints if self.hasJointRig else None,
                'clusters': self.clusters,
                'curveLength': self.initialLength,
                'curveInfoNode': self.curveInfoNode,
                'sinusWave': sinusWave}

    def createChainConstraints(self):

        aimVector = Nodes.convertAxisToVector(self.lengthAxis)
        upVector = Nodes.convertAxisToVector(self.upAxis)

        for j, jointCntNode in enumerate(self.jointCnts):

            if j > 0:
                mc.setAttr('%s.follow' % Nodes.replaceNodeType(jointCntNode, Settings.motionPathSuffix), False)
                mc.aimConstraint(jointCntNode, self.jointCnts[j-1], aimVector=aimVector,
                                wuo=self.orientLocs[j], wut='objectrotation', u=upVector, wu=upVector)

    def attachNodeToCurve(self, 
                            node,
                            n,
                            nodeCount,
                            upnodeType=None,
                            upnode=None,
                            alignByGuide=True,
                            createPositionAttr=True):

        
        val = 0 if self.closedCurve or nodeCount == 1 else 1
        fractionMode = False if self.segmenting else True

        motionPath = Nodes.motionPathNode(node=node,
                                            curveNode=self.curveNode, 
                                            nodeType=Settings.motionPathGuideSuffix if self.isGuide else Settings.motionPathSuffix,
                                            lengthAxis=self.lengthAxis,
                                            upAxis=self.upAxis,
                                            upNode=upnode,
                                            upNodeType=upnodeType,
                                            fractionMode=fractionMode)

        minMaxValue = [mc.getAttr('%s.minValue' % self.curveNode), mc.getAttr('%s.maxValue' % self.curveNode)]
        self.numSpans = minMaxValue[1] - minMaxValue[0]
        
        segMul = (self.numSpans if self.segmenting else 1) + (minMaxValue[0] if self.segmenting else 0)

        uValNorm = (1.0 / (nodeCount - val)) * n
        uVal = uValNorm * segMul

        if alignByGuide:
            motionPathGuide = Nodes.createName(self.component, 
                                                self.side, 
                                                Settings.motionPathGuideSuffix, 
                                                self.element, 
                                                [self.index, n], 
                                                'joint', 
                                                sourceNode=self.curveNode)[0]
            if not mc.objExists(motionPathGuide):
                # support for auto-sided guides (Eyes)
                motionPathGuide = Nodes.createName(self.component, 
                                                    Settings.leftSide, 
                                                    Settings.motionPathGuideSuffix, 
                                                    self.element, 
                                                    [self.index, n], 
                                                    'joint', 
                                                    sourceNode=self.curveNode)[0]
            if mc.objExists(motionPathGuide):
                uVal = mc.getAttr('%s.uValue'%motionPathGuide)
            elif mc.objExists(Nodes.createName(sourceNode=motionPathGuide, side=Settings.leftSide)[0]):
                uVal = mc.getAttr('%s.uValue'%(Nodes.createName(sourceNode=motionPathGuide, side=Settings.leftSide)[0]))
        
        if createPositionAttr:
            Nodes.lockAndHideAttributes(node, t=[True, True, True], r=[True, True, True])
            if not mc.objExists(node+'.curvePosition'):
                mc.addAttr(node, ln='curvePosition', dv=uVal, k=True)
            mc.setAttr(node+'.curvePosition', uVal)
            mc.connectAttr('%s.curvePosition'%node, '%s.uValue'%motionPath)
        else:
            mc.setAttr(motionPath+'.uValue', uVal)

        if self.flipOrientation:
            mc.setAttr('%s.inverseFront'%motionPath, 1)
            mc.setAttr('%s.inverseUp'%motionPath, 1)

        return motionPath

    def findPointLocOrientation(self,
                                c,
                                pointLocCount):

        loc = AddNode.emptyNode(node=self.curveNode,
                                component=self.component, 
                                side=self.side, 
                                nodeType=Settings.locNodeSuffix, 
                                element=self.element, 
                                indices=[self.index, c], 
                                indexFill=self.indexFill)

        motionPath = self.attachNodeToCurve(node=loc,
                                            n=c,
                                            nodeCount=pointLocCount,
                                            upnodeType='dummy' if self.upnode == None else 'object')
        mc.delete(motionPath)

        rotValue = mc.xform(loc, q=True, ws=True, ro=True)

        mc.delete(loc)

        return rotValue

    def createCurveControls(self):

        self.clusters = list()
        self.controls = list()
        self.offs = list()
            
        self.controlGroup = AddNode.emptyNode(node=self.curveNode,
                                                component=self.component, 
                                                side=self.side, 
                                                nodeType=Settings.guideGroup if self.isGuide else Settings.rigGroup,
                                                element=self.element,
                                                indices=self.index,
                                                specific='controls')

        self.setupGroup = AddNode.emptyNode(node=self.curveNode,
                                            component=self.component, 
                                            side=self.side, 
                                            nodeType=Settings.guideGroup if self.isGuide else Settings.rigGroup,
                                            element=self.element,
                                            indices=self.index,
                                            specific='setup')
        mc.parent(self.curveNode, self.setupGroup)
        mc.setAttr('%s.inheritsTransform'%self.setupGroup, False)
        
        if self.curveType == 'bezierCurve':
            add = 1
            step = 3
        else:
            add = 0
            step = 1

        for p in range(self.cvCount):
            
            clusterNode = Nodes.clusterNode('%s.cv[%s]'%(self.curveNode, p), 
                                            self.component, 
                                            self.side, 
                                            Settings.guideClusterHandleSuffix if self.isGuide else Settings.clusterHandleSuffix, 
                                            self.element, 
                                            [self.index, p], 
                                            indexFill=self.indexFill)
            
            mc.hide(clusterNode)
            self.clusters.append(clusterNode)

            rotValue = self.findPointLocOrientation(c=p, pointLocCount=self.cvCount)

            mc.xform(clusterNode, ws=True, ro=rotValue)
        
        self.orderedClusterList = self.clusters[::]

        if self.curveType == 'bezierCurve':
            bezierHandleList = [x for x in self.clusters]
            for b in range(0, self.cvCount + add, step):
                bezierHandleList.remove(self.clusters[b])
            bN = 0
            for b, bezierHandle in enumerate(bezierHandleList):
                handleName = 'B' if b % 2 == 0 else'A'
                bezierHandleName = Nodes.createName(self.component, 
                                                    self.side, 
                                                    Settings.guideClusterHandleSuffix if self.isGuide else Settings.clusterHandleSuffix, 
                                                    self.element, 
                                                    [self.index, bN], 
                                                    'bezierHandle'+handleName, 
                                                    self.indexFill, 
                                                    sourceNode=self.curveNode)
                bezierHandleList[b] = mc.rename(bezierHandle, bezierHandleName[0])
                Nodes.addNamingAttr(bezierHandleList[b], bezierHandleName[1])
                bezierCluster = Nodes.replaceNodeType(bezierHandleList[b], Settings.guideClusterSuffix if self.isGuide else Settings.clusterSuffix)
                bezierClusterName = Nodes.createName(self.component, 
                                                    self.side, 
                                                    Settings.guideClusterSuffix if self.isGuide else Settings.clusterSuffix, 
                                                    self.element, 
                                                    [self.index, bN], 
                                                    'bezierHandle'+handleName, 
                                                    self.indexFill, 
                                                    sourceNode=self.curveNode)
                bezierCluster = mc.rename(bezierCluster, bezierClusterName[0])
                Nodes.addNamingAttr(bezierCluster, bezierClusterName[1])
                if handleName == 'B':
                    bN += 1
            for i, p in enumerate(range(0, self.cvCount + add, step)):
                clusterNode = self.clusters[p]
                pointLocName = Nodes.createName(self.component, 
                                                self.side, 
                                                Settings.guideClusterHandleSuffix if self.isGuide else Settings.clusterHandleSuffix, 
                                                self.element, 
                                                indices=[self.index, i], 
                                                indexFill=self.indexFill, 
                                                sourceNode=self.curveNode)
                self.clusters[p] = mc.rename(clusterNode, pointLocName[0])
                Nodes.addNamingAttr(self.clusters[p], pointLocName[1])
        
        guidePivotNodeList = list() if self.isGuide else None
        self.controlRigs = list()
        
        for i, p in enumerate(range(0, self.cvCount + add, step)):
    
            if self.isGuide:
                guide = Guide.createGuide(component=self.component,
                                            size=self.size,
                                            side=self.side,
                                            element=self.element,
                                            indices=[self.index, i],
                                            indexFill=self.indexFill,
                                            alignAxis=self.alignAxis,
                                            hasAttrs=True)
                Nodes.alignObject(guide['pivot'], self.clusters[p])
                mc.parent(self.clusters[p], guide['pivot'])
                Nodes.setTrs(self.clusters[p], 0, t=False, r=True, s=False)
                guidePivotNodeList.append(guide['pivot'])

                self.controls.append(guide['control'])
                self.offs.append(guide['offset'])

            else:
                controlRig = Control.createControl(node=self.clusters[p],
                                                    component=self.component,
                                                    side=self.side,
                                                    element=self.element,
                                                    indices=[self.index, i],
                                                    indexFill=self.indexFill,
                                                    shape=self.shape,
                                                    color=self.color,
                                                    useGuideAttr=self.useGuideAttr,
                                                    offset=self.offset,
                                                    parentDirection='NodeToControl',
                                                    secondaryDefaultColor=self.secondaryDefaultColor,
                                                    rigGroup=self.rigGroup,
                                                    ignoreMissingGuideControlWarning=self.ignoreMissingGuideControlWarning,
                                                    postDeformAlignment=self.postDeformAlignment)
                
                self.controlRigs.append(controlRig)
                Nodes.setTrs(self.clusters[p], 0, t=False, r=True, s=False)
                Nodes.setParent(controlRig['offset'], self.controlGroup)

                guideNode =  Nodes.replaceNodeType(controlRig['offset'], Settings.guidePivotSuffix)
                if mc.objExists(guideNode):
                    Nodes.alignObject(controlRig['offset'], guideNode)

                if self.side == Settings.rightSide and self.flipOrientation and self.mirrorAxis != None:
                    if self.mirrorAxis == 'x':
                        axisRotate = [0, 0, 180]
                    if self.mirrorAxis == 'y':
                        axisRotate = [180, 0, 0]
                    if self.mirrorAxis == 'z':
                        axisRotate = [0, 180, 0]
                    mc.rotate(axisRotate[0], axisRotate[1], axisRotate[2], controlRig['offset'], r=True, os=True)

                self.controls.append(controlRig['control'])
                self.offs.append(controlRig['offset'])
        
        self.bezierHandleControls = list()
        self.bezierHandleGroups = list()
        
        if self.curveType == 'bezierCurve':
            bN = 0 
            for b, bezierHandle in enumerate(bezierHandleList):
                handleName = 'B' if b % 2 == 0 else'A'
                if self.isGuide:
                    bezierHandleGuide = Guide.createGuide(component=self.component,
                                                            side=self.side,
                                                            size=self.size,
                                                            element=self.element,
                                                            indices=[self.index, bN],
                                                            specific='bezierHandle'+handleName,
                                                            indexFill=self.indexFill,
                                                            node=self.curveNode)
                    mc.scale(0.5, 0.5, 0.5, bezierHandleGuide['control'], os=True, r=True)
                    Nodes.alignObject(bezierHandleGuide['pivot'], bezierHandle)
                    mc.parent(bezierHandle, bezierHandleGuide['pivot'])
                    mc.parent(bezierHandleGuide['pivot'], guidePivotNodeList[int((b + 1) / 2)])

                    self.bezierHandleControls.append(bezierHandleGuide['control'])
                    self.bezierHandleGroups.append(bezierHandleGuide['offset'])
                else:
                    
                    bezierHandleGuide = Nodes.createName(component=self.component,
                                                            side=self.side,
                                                            nodeType=Settings.guidePivotSuffix,
                                                            element=self.element,
                                                            indices=[self.index, bN],
                                                            specific='bezierHandle'+handleName,
                                                            indexFill=self.indexFill,
                                                            sourceNode=self.curveNode)[0]

                    bezierHandleRig = Control.createControl(node=bezierHandle,
                                                            component=self.component,
                                                            side=self.side,
                                                            element=self.element,
                                                            indices=[self.index, bN],
                                                            specific='bezierHandle'+handleName,
                                                            indexFill=self.indexFill,
                                                            shape=self.shape,
                                                            color=self.color,
                                                            useGuideAttr=self.useGuideAttr,
                                                            offset=self.offset,
                                                            parentDirection='NodeToControl',
                                                            secondaryDefaultColor=self.secondaryDefaultColor,
                                                            rigGroup=self.rigGroup,
                                                            deleteRightGuideNode=False,
                                                            ignoreMissingGuideControlWarning=True,
                                                            postDeformAlignment=self.postDeformAlignment)
                    Nodes.setTrs(bezierHandle, 0, t=False, r=True, s=False)
                                
                    Nodes.lockAndHideAttributes(bezierHandleRig['control'], 
                                                t=[False, False, False], 
                                                r=[True, True, True], 
                                                s=[True, True, True], 
                                                v=False,
                                                lock=True, 
                                                keyable=False, 
                                                lockVis=False)
                                                                
                    bezierParent = self.controls[int((b + 1) / 2)]
                    sclCmpNode = Nodes.replaceNodeType(bezierParent, Settings.scaleCompensateNode)
                    if mc.objExists(sclCmpNode):
                        bezierParent = sclCmpNode
                    mc.parent(bezierHandleRig['offset'], bezierParent)
                    if bezierHandleGuide != None:
                        Nodes.alignObject(bezierHandleRig['offset'], bezierHandleGuide)
                    self.bezierHandleControls.append(bezierHandleRig['control'])
                    self.bezierHandleGroups.append(bezierHandleRig['offset'])
                    
                if handleName == 'B':
                    bN += 1

        if self.isGuide:
            mc.parent(guidePivotNodeList, self.controlGroup)

    def createOrientLocs(self):
        
        jointsPerSeg = float(self.jointCount-1) / float(self.controlCount-1)
        if jointsPerSeg == 0:
            jointsPerSeg = 1
        
        self.orientLocs = list()
        self.orientConstraints = list()
        self.scaleConstraints = list()
        
        for p in range(self.jointCount):
            
            orientLoc = AddNode.emptyNode(node=self.curveNode,
                                            component=self.component, 
                                            side=self.side, 
                                            nodeType='orientLoc',
                                            element=self.element,
                                            indices=[self.index, p],
                                            indexFill=self.indexFill)

            iFloat = float(p / jointsPerSeg)
            i = int(iFloat)
            
            startNode = self.orderedClusterList[i]
            if i != self.controlCount - 1:
                endNode = self.orderedClusterList[i + 1]
            else:
                endNode = self.orderedClusterList[0]

            mc.delete(mc.pointConstraint([startNode, endNode], orientLoc, mo=False)[0])
            orientCnt = mc.orientConstraint([startNode, endNode], orientLoc, mo=False)[0]
            self.orientConstraints.append(orientCnt)
            if self.scaling:
                scaleCnt = mc.scaleConstraint([startNode, endNode], orientLoc, mo=False)[0]
                self.scaleConstraints.append(scaleCnt)

            weight = (1.0 / jointsPerSeg) * (p - (i * jointsPerSeg))

            if weight < 0:
                weight = 0
            if weight > 1:
                weight = 1

            startWeight = 1 - weight
            endWeight = weight

            for cnt in [orientCnt] + ([scaleCnt] if self.scaling else []):
                mc.setAttr('%s.%sW%s' % (cnt, startNode, '0'), startWeight)
                mc.setAttr('%s.%sW%s' % (cnt, endNode, '1'), endWeight)

            mc.setAttr('%s.interpType' % (orientCnt), 2)

            self.orientLocs.append(orientLoc)

    def createJoints(self):

        self.joints = list()
        self.jointControls = list()
        self.jointCnts = list()

        for j in range(self.jointCount):
            if j == 0 or self.skeletonParentToAllJoints:
                skeletonParent = self.skeletonParent
            elif self.skeletonParentToFirst:
                if j == 0:
                    skeletonParent = self.skeletonParent
                else:
                    skeletonParent = self.joints[0]
            else:
                skeletonParent = self.joints[-1]
            jointNode = AddNode.jointNode(node=self.curveNode,
                                            component=self.component, 
                                            side=self.side, 
                                            element=self.element, 
                                            indices=[self.index, j], 
                                            indexFill=self.jointIndexFill, 
                                            size=self.size*0.05,
                                            skeletonParent=skeletonParent)

            if self.controlPerJoint:
                controlRig = Control.createControl(node=self.curveNode,
                                                    component=self.component,
                                                    side=self.side,
                                                    element=self.element,
                                                    indices=[self.index, j],
                                                    specific='single',
                                                    indexFill=self.jointIndexFill,
                                                    shape='Sphere',
                                                    useGuideAttr=False,
                                                    ignoreMissingGuideControlWarning=True)
                mc.parent(jointNode, controlRig['control'])
                self.jointControls.append(controlRig)

            cntNode = AddNode.parentNode(controlRig['offset'] if self.controlPerJoint else jointNode, nodeType=Settings.motionPathNodeSuffix, specific='joint')
            self.jointCnts.append(cntNode)

            mc.setAttr('%s.displayLocalAxis' % (jointNode), True)

            self.attachNodeToCurve(node=cntNode,
                                    n=j,
                                    nodeCount=self.jointCount,
                                    upnodeType='objectrotation',
                                    upnode=self.orientLocs[j])

            self.joints.append(jointNode)

    def createSquash(self):
        
        if 'x' in self.lengthAxis:
            alignAxis = 'x'
            upAxis = 'y'
            otherAxis = 'z'
        if 'y' in self.lengthAxis:
            alignAxis = 'y'
            upAxis = 'z'
            otherAxis = 'x'
        if 'z' in self.lengthAxis:
            alignAxis = 'z'
            upAxis = 'x'
            otherAxis = 'y'

        self.curveInfoNode = Nodes.curveInfoNode(self.curveNode, Settings.curveInfoGuideSuffix if self.isGuide else Settings.curveInfoSuffix)

        attrList = [['startSquash', 0.0], ['midSquash', 1.0], ['midPosition', 0.5], ['endSquash', 0.0],
                    ['scalePowerStart', 0.0], ['tangentStart', 2.0], 
                    ['scalePowerMid', 1.0], ['tangentMid', 0.0],
                    ['tangentEnd', 2.0], ['scalePowerEnd', 0.0]]
        
        if self.hasSinusWaveScaling:
            attrList.extend([['strength', 0.0], 
                                ['travel', 0.0],
                                ['thickness', 0.0], 
                                ['size', 1.0], 
                                ['rootWeight', 0.0], 
                                ['rootOffset', 0.0], 
                                ['tipWeight', 1.0], 
                                ['rootBlending', 0], 
                                ['tipBlending', 0]])

        Nodes.addAttrTitle(self.rigGroup, 'squashStretch')

        for a, attr in enumerate(attrList):
            
            niceName = Tools.createNiceName(attr[0])

            if a > 9:
                Nodes.addAttrTitle(self.rigGroup, 'sinusScale')
                attrName = Tools.createUniqueName(attr[0], 'sinusScale')
            else:
                attrName = attr[0]

            if attr[0] == 'frequency':
                mc.addAttr(self.rigGroup, at='float', ln=attrName, nn=niceName, dv=attr[1], 
                        k=False if a > 11 else True,
                        hasMinValue=True,
                        minValue=0.01)
            elif 'Weight' in attr[0] or 'Blending' in attr[0]:
                mc.addAttr(self.rigGroup, at='float', ln=attrName, nn=niceName, dv=attr[1], 
                        k=False if a > 11 else True,
                        hasMinValue=True,
                        minValue=0)
            elif a == 0:
                mc.addAttr(self.rigGroup, at='float', ln=attrName, nn=niceName, dv=attr[1], 
                            k=False,
                            hasMinValue=True,
                            minValue=0)
                mc.setAttr(self.rigGroup+'.'+attrName, cb=True)
            elif a == 1:
                mc.addAttr(self.rigGroup, at='float', ln=attrName, nn=niceName, dv=attr[1], 
                            k=False,
                            hasMinValue=True,
                            minValue=0)
                mc.setAttr(self.rigGroup+'.'+attrName, cb=True)
            elif a == 2:
                mc.addAttr(self.rigGroup, at='float', ln=attrName, nn=niceName, dv=attr[1], 
                            k=False,
                            hasMinValue=True,
                            minValue=0.01,
                            hasMaxValue=True,
                            maxValue = 0.99)
                mc.setAttr(self.rigGroup+'.'+attrName, cb=True)
            elif a == 3:
                mc.addAttr(self.rigGroup, at='float', ln=attrName, nn=niceName, dv=attr[1], 
                            k=False,
                            hasMinValue=True,
                            minValue=0)
                mc.setAttr(self.rigGroup+'.'+attrName, cb=True)
            else:
                mc.addAttr(self.rigGroup, at='float', ln=attrName, nn=niceName, dv=attr[1], 
                            k=False if a > 13 or (a > 1 and a < 8) else True)
            if a > 13:
                mc.setAttr(self.rigGroup+'.'+attrName, cb=True)

        self.initialLength = mc.getAttr('%s.arcLength' % (self.curveInfoNode))
        
        for j, jointCntNode in enumerate(self.jointCnts):

            attrStretch = '%s.s%s' % (jointCntNode, alignAxis)
            attrSqueeze = '%s.s%s' % (jointCntNode, upAxis)
            attrOtherSqueeze = '%s.s%s' % (jointCntNode, otherAxis)
            
            chainCount = float(len(self.jointCnts))
            if chainCount == 1:
                squeezeExpr = '%s = 1' % attrSqueeze
            else:
                squashExpr = '$chainCount = %s;\n' % (chainCount) \
                            + '$midPosition = %s.%s;\n' % (self.rigGroup, attrList[2][0]) \
                            + '$hAchainCount = ($chainCount-1)*$midPosition+1;\n' \
                            + '$hBchainCount = ($chainCount-1)*(1.0-$midPosition)+1;\n' \
                            + '$c = (1.0/($chainCount-1))*%s;\n' % (float(j)) \
                            + '$hAc = $c/$midPosition;\n' \
                            + '$hBc = ($c-$midPosition)*(1.0/(1-$midPosition));\n' \
                            + '$pA0 = %s.%s;\n' % (self.rigGroup, attrList[0][0]) \
                            + '$pA1 = %s.%s;\n' % (self.rigGroup, attrList[1][0]) \
                            + '$tA0 = %s;\n' % (0) \
                            + '$tA1 = %s;\n' % (0) \
                            + '$pB0 = %s.%s;\n' % (self.rigGroup, attrList[1][0]) \
                            + '$pB1 = %s.%s;\n' % (self.rigGroup, attrList[3][0]) \
                            + '$tB0 = %s;\n' % (0) \
                            + '$tB1 = %s;\n' % (0) \
                            + '$hA = `hermite $pA0 $pA1 $tA0 $tA1 $hAc`;\n' \
                            + '$hB = `hermite $pB0 $pB1 $tB0 $tB1 $hBc`;\n' \
                            + '$h = 0.0;\n' \
                            + 'if ($c <= $midPosition) {$h = $hA;}\n' \
                            + 'if ($c > $midPosition) {$h = $hB;}\n' \
            
                squeezeExpr = squashExpr \
                            + '$val = (1 + ($h * (1 - (%s.arcLength / (%s*%s.globalScale)))));\n' % (self.curveInfoNode, self.initialLength, self.rigGroup) \
                            + '$smoothVal = $val;\n' \
                            + '$minVal = 1.0/(%s.%s+1);\n' % (self.rigGroup, attrList[1][0]) \
                            + 'if ($val < 1) {$smoothVal = `hermite $minVal 1 0 1 $val`;}\n' \
                            + 'if ($val < 0) {$smoothVal = $minVal;}\n' \
                            + '%s = $smoothVal' % attrSqueeze 

                if self.hasSinusWaveScaling:

                    offset = '%s.sinusScaleTravel' % (self.rigGroup)
                    manualScale = '%s.sinusScaleStrength' % (self.rigGroup)
                    scaleOffset = '%s.sinusScaleThickness' % (self.rigGroup)
                    frequency = '%s.sinusScaleSize' % (self.rigGroup)

                    rootWeight = '%s.sinusScaleRootWeight' % (self.rigGroup)
                    rootOffset = '%s.sinusScaleRootOffset' % (self.rigGroup)
                    tipWeight = '%s.sinusScaleTipWeight' % (self.rigGroup)
                    rootBlending = '%s.sinusScaleRootBlending' % (self.rigGroup)
                    tipBlending = '%s.sinusScaleTipBlending' % (self.rigGroup)

                    squeezeExpr = squeezeExpr+';\n' \
                                + '$chainCount = %s-%s;\n' % (float(chainCount), rootOffset) \
                                + '$c = (%s-%s)*(%s/$chainCount);\n' % (float(j), rootOffset, float(chainCount)) \
                                + 'if ($c < 0) {$c = 0;}\n' \
                                + '$sinusScaleVal = %s+%s*sin((%s-%s)/%s);\n' % (scaleOffset, manualScale, j, offset, frequency) \
                                + '$p0 = %s;\n' % (rootWeight)\
                                + '$p1 = %s;\n' % (tipWeight)\
                                + '$t0 = %s;\n' % (rootBlending)\
                                + '$t1 = -%s;\n' % (tipBlending)\
                                + '$sinusScaleBlend = $sinusScaleVal*`hermite $p0 $p1 $t0 $t1 (1.0/($chainCount-1)*$c)`;\n' \
                                + 'if ($c < 0) {$sinusScaleBlend = 0;}\n' \
                                + '%s = $val+$sinusScaleBlend' % attrSqueeze
            
            stretchExpr = '$val = %s.arcLength / (%s*%s.globalScale);\n' % (
            self.curveInfoNode, self.initialLength, self.rigGroup) \
                + '%s = $val' % attrStretch
            
            Nodes.removeConnection(attrStretch)
            Nodes.removeConnection(attrSqueeze)

            Nodes.exprNode(attrStretch, stretchExpr, specific='stretch')
            squeezeExprNode = Nodes.exprNode(attrSqueeze, squeezeExpr, specific='squeeze')
            '''
            Nodes.removeConnection(attrStretch)
            Nodes.removeConnection(attrSqueeze)
            squeezeName = attrSqueeze.replace('.', '_')
            squeezeExprName = squeezeName + '_' + Settings.expressionSuffix
            otherSqueezeName = attrOtherSqueeze.replace('.', '_')
            mc.expression(attrStretch, string=squeezeExpr, name=squeezeExprName, alwaysEvaluate=0)
            stretchName = attrStretch.replace('.', '_')
            stretchExprName = stretchName + '_' + Settings.expressionSuffix
            mc.expression(attrStretch, string=stretchExpr, name=stretchExprName, alwaysEvaluate=0)
            '''
            # this is for manual scaling per control
            Nodes.mulNode(input1='%s.output[0]' % squeezeExprNode, 
                            input2='%s.s%s' % (self.orientLocs[j], upAxis), 
                            output=attrSqueeze)

            Nodes.mulNode(input1='%s.output[0]' % squeezeExprNode, 
                            input2='%s.s%s' % (self.orientLocs[j], otherAxis), 
                            output=attrOtherSqueeze)

        # stretch display attr

        Nodes.addAttrTitle(self.rigGroup, 'stretch')
        mc.addAttr(self.rigGroup, at='float', ln=self.component+'Stretch', k=False)
        mc.setAttr(self.rigGroup+'.'+self.component+'Stretch', channelBox=True)

        Nodes.divNode(input1='%s.arcLength' % self.curveInfoNode, 
                        input2=self.initialLength, 
                        output=self.rigGroup+'.'+self.component+'Stretch')

    def subdivideBezierCurve(self, 
                                divisions=5, 
                                duplicateCurve=True, 
                                convertToNurbs=False,
                                name='subdividedCurve'):
        # method needs fixing
        minMaxValue = [mc.getAttr('%s.minValue' % self.curveNode), mc.getAttr('%s.maxValue' % self.curveNode)]
        numSpans = minMaxValue[1] - minMaxValue[0]

        totalKnotCount = int(numSpans*(divisions+1))+1
        divisionValue = numSpans/(totalKnotCount-1)
        knotValues = [divisionValue*d for d in range(totalKnotCount) if not float(divisionValue*d).is_integer()]

        subdividedCurve = mc.insertKnotCurve(self.curveNode, parameter=knotValues, ch=False, replaceOriginal=False if duplicateCurve else True)[0]
        if self.component != None:
            subdividedCurve = mc.rename(subdividedCurve, self.component)

        if convertToNurbs:
            curveGuide = self.createCurveGuide(name=name, curveType='nurbsCurve', controlCount=totalKnotCount)
            nurbsCurve = mc.rename(mc.duplicate(curveGuide[0])[0], name+'Nurbs')
            mc.parent(nurbsCurve, world=True)
            mc.delete(curveGuide)
            mc.move(1, 0, 0, '%s.cv[*]' % nurbsCurve, r=True, ws=True) # this is to refresh curve state
            mc.move(-1, 0, 0, '%s.cv[*]' % nurbsCurve, r=True, ws=True) # this is to refresh curve state
            mc.delete(subdividedCurve)
            subdividedCurve = nurbsCurve
        
        return subdividedCurve

    def alignNodesToCurve(self,
                            nodeList=None, 
                            offset=0, 
                            reverse=False,
                            gap=0, 
                            upnode=None,
                            upnodeType=None,
                            deleteMotionPath=True):

        if nodeList == None:
            nodeList = mc.ls(sl=True)
        if reverse:
            nodeList = nodeList[::-1]
        
        motionPathes = list()
        for n, node in enumerate(nodeList):
            for trs in 'trs':
                for axis in 'xyz':
                    Nodes.removeConnection('%s.%s%s'%(node, trs, axis))
            Nodes.removeConnection('%s.rotateOrder'%node)
            
            if n+offset > len(nodeList)-1:
                n = n-len(nodeList)+1-gap
            if n+offset < 0:
                n = n+len(nodeList)+1-gap
            
            n = n+offset

            if not upnodeType:
                upnodeType = 'dummy' if upnode == None else 'object'

            motionPath = self.attachNodeToCurve(node, n, len(nodeList), upnode=None, upnodeType=upnodeType, alignByGuide=False, createPositionAttr=False)
            motionPathes.append(motionPath)

            if type(upnode) == list:
                upnode_obj = Tools.getClosestNode(node, upnode)[0]
            else:
                upnode_obj = upnode
            mc.connectAttr(upnode_obj + ".worldMatrix[0]", motionPath + ".worldUpMatrix", force=True)
            
            if deleteMotionPath:
                for trs in 'trs':
                    for axis in 'xyz':
                        Nodes.removeConnection('%s.%s%s'%(node, trs, axis))
                Nodes.removeConnection('%s.rotateOrder'%node)

                mc.delete(motionPath)

        mc.select(nodeList)

        return motionPathes

    def alignJointGuides(self,
                            alignNodes=None,
                            segmenting=True,
                            reverse=False,
                            accuracy=0.01):
                            
        self.segmenting = segmenting
        if mc.objExists(self.curveNode+'.segmenting'):
            self.segmenting = mc.getAttr(self.curveNode+'.segmenting')
        
        alignCurve=None
        if '.e' in alignNodes[0]:
            geo = alignNodes[0].split('.')[0]
            mc.displaySmoothness(geo, divisionsU=0, divisionsV=0, pointsWire=4, pointsShaded=1, polygonObject=1)
            mc.select(alignNodes)
            alignCurve = mc.polyToCurve(form=2, degree=1)
            alignNodes = mc.ls('%s.cv[*]' % alignCurve[0], fl=True)
            if reverse:
                alignNodes = alignNodes[::-1]

        minMaxValue = [mc.getAttr('%s.minValue' % self.curveNode), mc.getAttr('%s.maxValue' % self.curveNode)]
        numSpans = minMaxValue[1] - minMaxValue[0]

        segMul = (numSpans if self.segmenting else 1) + (minMaxValue[0] if self.segmenting else 0)
        
        jointCountAttr = '%s.jointCount'%self.curveNode
        if mc.objExists(jointCountAttr):
            self.jointCount = mc.getAttr(jointCountAttr)
        self.component = Nodes.getComponent(self.curveNode)
        self.element = Nodes.getElement(self.curveNode)
        self.side = Nodes.getSide(self.curveNode)
        self.jointGroup = Nodes.createName(self.component, self.side, Settings.guideGroup, self.element, specific='joints')[0]
        hasJointGuides = mc.listRelatives(self.jointGroup, children=True)
        if not hasJointGuides:
            MessageHandling.noJointGuides()
            return
        self.jointCount = len(hasJointGuides)

        size = mc.getAttr('%s.pivotShapeSize'%Nodes.createName(self.component, self.side, Settings.guidePivotSuffix, self.element, indices=0, specific='joint')[0])*10

        for j in range(self.jointCount):
            mc.delete(Nodes.createName(self.component, self.side, Settings.guidePivotSuffix, self.element, indices=j, specific='joint')[0])
            mc.delete(Nodes.createName(self.component, self.side, Settings.motionPathGuideSuffix, self.element, indices=j, specific='joint')[0])

        self.createJointGuides(size=size)
        
        locArrayNodes = list()
        motionPathArrayNodes = list()
        arrayNodesCount = int(segMul/accuracy)
        for a in range(arrayNodesCount):
            locNode = mc.spaceLocator(name='motionPathArray_'+str(a))[0]
            motionPath = self.attachNodeToCurve(locNode, a, arrayNodesCount)
            locArrayNodes.append(locNode)
            motionPathArrayNodes.append(motionPath)
        
        for g, guideJoint in enumerate(self.guideJoints):
            if mc.objExists(guideJoint):
                locPosNode = AddNode.createLocOnSelection(alignNodes[g], g)
                closestNode, index = Tools.getClosestNode(locPosNode, locArrayNodes)
                uVal = mc.getAttr('%s.uValue'%motionPathArrayNodes[index])
                mc.delete(locPosNode)
                mc.setAttr('%s.curvePosition'%guideJoint, uVal)
        
        if alignCurve != None:
            mc.delete(alignCurve)
        mc.delete(locArrayNodes)
        mc.delete(motionPathArrayNodes)