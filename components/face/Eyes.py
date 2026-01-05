# Eyes

import maya.cmds as mc
import math
import maya.mel as mel

from bear.system import Generic
from bear.system import Guiding
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import VisSwitch
from bear.utilities import SpaceSwitch
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import Nodes
if Settings.licenseVersion == 'full':
    from bear.utilities import Sealing
from bear.components.basic import Curve
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):

    def __init__(self,
                name='eye',
                hasEyelids=True,
                hasOuterLine=True,
                hasSquashStretch=False,
                hasCurveRig=True,
                hasIris=True,
                hasIrisSquash=False,
                hasHighlight=False,
                upperLidJointCount=12,
                lowerLidJointCount=12,
                upperLidVertexLoop=None,
                lowerLidVertexLoop=None,
                hasUpperLashes=False,
                hasLowerLashes=False,
                parentNode=Nodes.createName('head', nodeType=Settings.controlSuffix)[0],
                eyeballLeftGeo=None,
                eyeballRightGeo=None,
                eyeLeftNonUniformGeos=None,
                eyeRightNonUniformGeos=None,
                squashStretchLeftGeos=None,
                squashStretchRightGeos=None,
                eyeLeftScale=[1, 1, 1],
                eyeRightScale=[1, 1, 1],
                initialPupilSize=0.5,
                hasJointGuides=False,
                eyeDistanceMultiplier=5,
                eyeDistanceAutoDetect=True,
                spaceNodes=[Nodes.createName('root', nodeType=Settings.controlSuffix)[0], 
                        Nodes.createName('root', element='placement', nodeType=Settings.controlSuffix)[0],
                        Nodes.createName('root', element='main', specific='pivot', nodeType=Settings.controlSuffix)[0],
                        Nodes.createName('body', nodeType=Settings.controlSuffix)[0],
                        Nodes.createName('chest', nodeType=Settings.controlSuffix)[0],
                        Nodes.createName('head', nodeType=Settings.controlSuffix)[0]],
                spaceNames=['root',
                            'placement',
                            'main',
                            'body',
                            'chest',
                            'head'],
                displaySwitch='faceDisplaySwitch',
                *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.hasEyelids = hasEyelids
        self.hasOuterLine = hasOuterLine
        self.hasSquashStretch = hasSquashStretch
        self.hasCurveRig = hasCurveRig if upperLidJointCount > 0 and lowerLidJointCount > 0 else False
        self.hasIris = hasIris
        self.hasIrisSquash = hasIrisSquash
        self.hasHighlight = hasHighlight
        self.upperLidJointCount = upperLidJointCount
        self.lowerLidJointCount = lowerLidJointCount
        self.upperLidVertexLoop = upperLidVertexLoop
        self.lowerLidVertexLoop = lowerLidVertexLoop
        self.hasUpperLashes = hasUpperLashes
        self.hasLowerLashes = hasLowerLashes
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.eyeballLeftGeo = eyeballLeftGeo
        self.eyeballRightGeo = eyeballRightGeo
        if eyeLeftNonUniformGeos:
            self.eyeLeftNonUniformGeos = eyeLeftNonUniformGeos if type(eyeLeftNonUniformGeos) == list else [eyeLeftNonUniformGeos]
        else:
            self.eyeLeftNonUniformGeos = None
        if eyeRightNonUniformGeos:
            self.eyeRightNonUniformGeos = eyeRightNonUniformGeos if type(eyeRightNonUniformGeos) == list else [eyeRightNonUniformGeos]
        else:
            self.eyeRightNonUniformGeos = None
        if squashStretchLeftGeos:
            self.squashStretchLeftGeos = squashStretchLeftGeos if type(squashStretchLeftGeos) == list else [squashStretchLeftGeos]
        else:
            self.squashStretchLeftGeos = None
        if squashStretchRightGeos:
            self.squashStretchRightGeos = squashStretchRightGeos if type(squashStretchRightGeos) == list else [squashStretchRightGeos]
        else:
            self.squashStretchRightGeos = None
        self.eyeLeftScale = eyeLeftScale
        self.eyeRightScale = eyeRightScale
        self.initialPupilSize = initialPupilSize
        self.hasJointGuides = hasJointGuides
        self.eyeDistanceMultiplier = eyeDistanceMultiplier
        self.eyeDistanceAutoDetect = eyeDistanceAutoDetect
        self.hasOpenedClosedNodes = False
        self.spaceNodes = spaceNodes
        self.spaceNames = spaceNames
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, 'auto', definition)
        if definition:
            return {'guideGroup': guideGroup}

        if self.hasOuterLine:
            outerGroup = AddNode.emptyNode(component=self.name, side=Settings.leftSide, nodeType=Settings.guideGroup, element='outer')
            mc.parent(outerGroup, guideGroup)
        if self.hasOpenedClosedNodes:
            closedGroup = AddNode.emptyNode(component=self.name, side=Settings.leftSide, nodeType=Settings.guideGroup, element='closed')
            openedGroup = AddNode.emptyNode(component=self.name, side=Settings.leftSide, nodeType=Settings.guideGroup, element='opened')
            mc.hide(closedGroup)
            mc.hide(openedGroup)
            mc.parent([closedGroup, openedGroup], guideGroup)

        elementNames = ['ball']
        if self.hasEyelids:
            elementNames.extend(['innerlid', 'upperlidin', 'upperlid', 'upperlidout', 'outerlid', 'lowerlidout', 'lowerlid', 'lowerlidin'])

        if self.hasOuterLine:
            if self.hasCurveRig:
                elementNames.extend(['innerlidOuter', 'upperlidinOuter', 'upperlidOuter', 'upperlidoutOuter', 'outerlidOuter', 'lowerlidoutOuter', 'lowerlidOuter', 'lowerlidinOuter'])
            else:
                elementNames.extend(['upperlidinOuter', 'upperlidOuter', 'upperlidoutOuter', 'lowerlidoutOuter', 'lowerlidOuter', 'lowerlidinOuter'])

        if self.hasCurveRig:
            lidGuides = list()
            lidElementNames = ['upperlid', 'lowerlid']
            if self.hasOuterLine:
                lidElementNames.extend(['upperlidOuter', 'lowerlidOuter'])
            for n, lidElementName in enumerate(lidElementNames):
                lidGuide = Curve.Build(component=self.name,
                                        side=Settings.leftSide,
                                        size=1,
                                        element=lidElementName,
                                        controlCount=5,
                                        segmenting=False,
                                        jointCount=[self.upperLidJointCount, self.lowerLidJointCount, self.upperLidJointCount, self.lowerLidJointCount][n],
                                        hasJointGuides=self.hasJointGuides).createGuide(definition)
                lidGuides.append(lidGuide)
                mc.parent(lidGuide['guideGroup'], guideGroup)
            
        pupilGuide = Guide.createGuide(component=self.name,
                                                element='pupil',
                                                side=Settings.leftSide,
                                                size=1,
                                                alignAxis='Y',
                                                hasGuideShape=False)
        mc.parent(pupilGuide['pivot'], guideGroup)

        for n, elementName in enumerate(elementNames):
            
            guide = Guide.createGuide(component=self.name,
                                        element=elementName,
                                        side=Settings.leftSide,
                                        size=1,
                                        alignAxis='Y')
            
            if n == 0:
                mc.aimConstraint(pupilGuide['pivot'], guide['pivot'], aim=(0,0,1), wu=(0,1,0), wuo=pupilGuide['pivot'], wut='objectrotation', u=(0,1,0))
                Nodes.lockAndHideAttributes(guide['pivot'], r=[True, True, True])
            if n == 3:
                Nodes.addAttrTitle(guide['control'], 'blendShape')
                mc.addAttr(guide['control'], at='float', ln='bsh_translateY_pos', k=True, dv=-2)
                mc.addAttr(guide['control'], at='float', ln='bsh_translateY_neg', k=True, dv=-2)
            if n == 7:
                Nodes.addAttrTitle(guide['control'], 'blendShape')
                mc.addAttr(guide['control'], at='float', ln='bsh_translateY_pos', k=True, dv=-2)
                mc.addAttr(guide['control'], at='float', ln='bsh_translateY_neg', k=True, dv=-2)

            mc.parent(guide['pivot'], guideGroup)

            if self.hasOpenedClosedNodes:
                if n > 0 and n < 9:
                    closedEyeGuide = AddNode.emptyNode(component=self.name, side=Settings.leftSide, element=elementName, specific='closed', nodeType=Settings.guidePivotSuffix, objType='locator')
                    Nodes.addAttrTitle(closedEyeGuide, 'rigging')
                    mc.addAttr(closedEyeGuide, at='bool', ln='active', dv=True, k=True)
                    mc.parent(closedEyeGuide, closedGroup)

                if n == 3 or n == 7:
                    openedEyeGuide =  AddNode.emptyNode(component=self.name, side=Settings.leftSide, element=elementName, specific='opened', nodeType=Settings.guidePivotSuffix, objType='locator')
                    Nodes.addAttrTitle(openedEyeGuide, 'rigging')
                    mc.addAttr(openedEyeGuide, at='bool', ln='active', dv=True, k=True)
                    mc.parent(openedEyeGuide, openedGroup)

            if 'Outer' in elementName and self.hasOuterLine:
                mc.parent(guide['pivot'], outerGroup)

            positions = [(0, 0, -1),
                            (-3, 0, 0),
                            (-2, 1, 0),
                            (0, 2, 0),
                            (2, 1, 0),
                            (3, 0, 0),
                            (2, -1, 0),
                            (0, -2, 0),
                            (-2, -1, 0)]
            if self.hasOuterLine:
                if self.hasCurveRig:
                    positions.extend([(-5, 0, 0),
                                (-3, 3, 0),
                                (0, 4, 0),
                                (3, 3, 0),
                                (5, 0, 0),
                                (3, -3, 0),
                                (0, -4, 0),
                                (-3, -3, 0)])
                else:
                    positions.extend([
                                (-3, 3, 0),
                                (0, 4, 0),
                                (3, 3, 0),
                                (10, -3, 0),
                                (0, -4, 0),
                                (-3, -3, 0)])
            mc.move(positions[n][0], positions[n][1], positions[n][2], guide['pivot'])
            if n == 1:
                mc.rotate(0, 0, 90, guide['pivot'])
            if n == 5:
                mc.rotate(0, 0, -90, guide['pivot'])
            if n in [6, 7, 8]:
                mc.rotate(0, 0, 180, guide['pivot'])
            if self.hasOuterLine:
                if self.hasCurveRig:
                    if n == 9:
                        mc.rotate(0, 0, 90, guide['pivot'])
                    if n == 13:
                        mc.rotate(0, 0, -90, guide['pivot'])
                    if n in [14, 15, 16]:
                        mc.rotate(0, 0, 180, guide['pivot'])
                else:
                    if n in [12, 13, 14]:
                        mc.rotate(0, 0, 180, guide['pivot'])

            for side in [Settings.leftSide, Settings.rightSide]:
                ConnectionHandling.addOutput(guideGroup, Nodes.createName(self.name, side, Settings.skinJointSuffix, element=elementName)[0])

            if self.hasCurveRig:

                if n > 0 and n < 6:
                    mc.parent(lidGuides[0]['guidePivots'][n-1], guide['pivot'])
                    if n == 1:
                        mc.parent(lidGuides[1]['guidePivots'][0], guide['pivot'])
                    if n == 5:
                        mc.parent(lidGuides[1]['guidePivots'][4], guide['pivot'])

                if n == 6:
                    mc.parent(lidGuides[1]['guidePivots'][3], guide['pivot'])
                if n == 7:
                    mc.parent(lidGuides[1]['guidePivots'][2], guide['pivot'])
                if n == 8:
                    mc.parent(lidGuides[1]['guidePivots'][1], guide['pivot'])

                [Nodes.setTrs(x) for x in lidGuides[0]['guidePivots']]
                [Nodes.setTrs(x) for x in lidGuides[1]['guidePivots']]

                mc.hide(lidGuides[0]['guidePivots'])
                mc.hide(lidGuides[1]['guidePivots'])

                if self.hasOuterLine:

                    if n > 8 and n < 14:
                        mc.parent(lidGuides[2]['guidePivots'][n-9], guide['pivot'])
                        if n == 9:
                            mc.parent(lidGuides[3]['guidePivots'][0], guide['pivot'])
                        if n == 13:
                            mc.parent(lidGuides[3]['guidePivots'][4], guide['pivot'])

                    if n == 14:
                        mc.parent(lidGuides[3]['guidePivots'][3], guide['pivot'])
                    if n == 15:
                        mc.parent(lidGuides[3]['guidePivots'][2], guide['pivot'])
                    if n == 16:
                        mc.parent(lidGuides[3]['guidePivots'][1], guide['pivot'])

                    [Nodes.setTrs(x) for x in lidGuides[2]['guidePivots']]
                    [Nodes.setTrs(x) for x in lidGuides[3]['guidePivots']]

                    mc.hide(lidGuides[2]['guidePivots'])
                    mc.hide(lidGuides[3]['guidePivots'])

        mc.move(10, 18, 0, guideGroup)

        # we snap joints to edge loop after guide values have been applied
        # NOTE WIP
        '''
        if self.snapJointsLoop:
            for i, eyelidGuide in enumerate(eyelidGuides):
                edgeLoop = [self.upperLidLoop,
                            self.lowerLidLoop,
                            self.upperLidOuterLoop,
                            self.lowerLidOuterLoop][i]
                if edgeLoop:
                    Sealing.alignJointsToEdgeLoop(eyelidGuide['guideModule']['node'], edgeLoop)
        '''
        return {'guideGroup': guideGroup}

    def createRig(self):

        # on aim constraint creation a cycle error is thrown but doesn't happen in the final rig, so we ignore it
        mc.cycleCheck(e=False)

        eyeballGuide = Nodes.createName(self.name, Settings.leftSide, element='ball', nodeType=Settings.guidePivotSuffix)[0]
        pupilGuide = Nodes.createName(self.name, Settings.leftSide, element='pupil', nodeType=Settings.guidePivotSuffix)[0]
        innerlidGuide = Nodes.createName(self.name, Settings.leftSide, element='innerlid', nodeType=Settings.guidePivotSuffix)[0]
        upperlidinGuide = Nodes.createName(self.name, Settings.leftSide, element='upperlidin', nodeType=Settings.guidePivotSuffix)[0]
        upperlidGuide = Nodes.createName(self.name, Settings.leftSide, element='upperlid', nodeType=Settings.guidePivotSuffix)[0]
        upperlidoutGuide = Nodes.createName(self.name, Settings.leftSide, element='upperlidout', nodeType=Settings.guidePivotSuffix)[0]
        outerlidGuide = Nodes.createName(self.name, Settings.leftSide, element='outerlid', nodeType=Settings.guidePivotSuffix)[0]
        lowerlidoutGuide = Nodes.createName(self.name, Settings.leftSide, element='lowerlidout', nodeType=Settings.guidePivotSuffix)[0]
        lowerlidGuide = Nodes.createName(self.name, Settings.leftSide, element='lowerlid', nodeType=Settings.guidePivotSuffix)[0]
        lowerlidinGuide = Nodes.createName(self.name, Settings.leftSide, element='lowerlidin', nodeType=Settings.guidePivotSuffix)[0]
        innerlidOuterGuide = Nodes.createName(self.name, Settings.leftSide, element='innerlidOuter', nodeType=Settings.guidePivotSuffix)[0]
        upperlidinOuterGuide = Nodes.createName(self.name, Settings.leftSide, element='upperlidinOuter', nodeType=Settings.guidePivotSuffix)[0]
        upperlidOuterGuide = Nodes.createName(self.name, Settings.leftSide, element='upperlidOuter', nodeType=Settings.guidePivotSuffix)[0]
        upperlidoutOuterGuide = Nodes.createName(self.name, Settings.leftSide, element='upperlidoutOuter', nodeType=Settings.guidePivotSuffix)[0]
        outerlidOuterGuide = Nodes.createName(self.name, Settings.leftSide, element='outerlidOuter', nodeType=Settings.guidePivotSuffix)[0]
        lowerlidoutOuterGuide = Nodes.createName(self.name, Settings.leftSide, element='lowerlidoutOuter', nodeType=Settings.guidePivotSuffix)[0]
        lowerlidOuterGuide = Nodes.createName(self.name, Settings.leftSide, element='lowerlidOuter', nodeType=Settings.guidePivotSuffix)[0]
        lowerlidinOuterGuide = Nodes.createName(self.name, Settings.leftSide, element='lowerlidinOuter', nodeType=Settings.guidePivotSuffix)[0]
        
        self.hasOuterLine = Guiding.getBuildAttrs(Nodes.createName(self.name, nodeType=Settings.guideGroup)[0], 'hasOuterLine')

        rigGroup = super(Build, self).createRig(self.name, 'auto')
        controlGroup = AddNode.emptyNode(component=self.name, element='control', nodeType=Settings.rigGroup)
        mc.parent(controlGroup, rigGroup)

        eyeballSizeLeft = Nodes.getSize(self.eyeballLeftGeo)[0] if self.eyeballLeftGeo else 1
        eyeballSizeRight = Nodes.getSize(self.eyeballRightGeo)[0] if self.eyeballRightGeo else 1

        eyeballPivotGuide = Guiding.getGuideAttr(eyeballGuide)['pivotGuide']
        eyeballOffset = Guiding.getGuideAttr(eyeballGuide)['offset']

        if self.eyeDistanceAutoDetect:
            eyeWidth = abs(mc.xform(eyeballPivotGuide, q=True, ws=True, rp=True)[0])
        else:
            eyeWidth = 1
        mainTargetOffset = eyeWidth*self.eyeDistanceMultiplier

        # eye non-uniform scale

        for eyeGeos in [self.eyeLeftNonUniformGeos, self.eyeRightNonUniformGeos]:
            if not eyeGeos:
                continue
            degVals = mc.xform(eyeballGuide, q=True, rotation=True, ws=True)
            radVals = [math.radians(x) for x in degVals]
            posVals = mc.xform(eyeballGuide, q=True, translation=True, ws=True)
            if eyeGeos == self.eyeRightNonUniformGeos:
                radVals = [radVals[0], -radVals[1], radVals[2]]
                posVals = [-posVals[0], posVals[1], posVals[2]]
                scaleVals = self.eyeRightScale
            else:
                scaleVals = self.eyeLeftScale
            revertScale = [1.0 / x for x in scaleVals]
            for eyeGeo in eyeGeos:
                if not mc.objExists(eyeGeo) or mc.objExists('%s.hasReceivedScale'%eyeGeo):
                    continue
                # using maya command for correct rotation pivot
                #mc.scale(revertScale[0], revertScale[1], revertScale[2], '%s.vtx[*]'%eyeGeo, oa=radVals, p=posVals, r=True)
                mc.select('%s.vtx[*]'%eyeGeo)
                mel.eval("scale -oa %srad %srad %srad -r -p %s %s %s %s %s %s;" % \
                    (radVals[0], radVals[1], radVals[2], posVals[0], posVals[1], posVals[2], revertScale[0], revertScale[1], revertScale[2]))
                mc.addAttr(eyeGeo, ln='hasReceivedScale', at='bool', dv=True)
        mc.select(clear=True)
        
        self.parentNode = ConnectionHandling.inputExists(self.parentNode)

        controlRigSet = list()
        blinkControlRigSet = list()
        eyetargetControlNodesList = list()
        jointNodeList = list()
        outerInnerJointList = list()

        allEyelidControlNodesList = list()
        allOuterControlNodesList = list()

        eyeballAimList = list()

        eyeballJointList = list()

        # eyes target rig
        
        eyeDistance = abs(mc.xform(eyeballGuide, q=True, ws=True, rp=True)[0])*2
        
        mainTargetRig = Control.createControl(node=eyeballGuide,
                                                component=self.name,
                                                side=False,
                                                element='target',
                                                shape='Rectangle',
                                                alignAxis='Z',
                                                useGuideAttr=False,
                                                offset=[[0, 0, 0], [90, 0, 90], [eyeballOffset[2][0]*2, 1, eyeDistance+eyeballOffset[2][0]*2]],
                                                mirrorScale=None)

        Nodes.lockAndHideAttributes(mainTargetRig['control'], s=[True, True, True], v=True)

        mc.setAttr('%s.tx' % (mainTargetRig['offset']), 0)
        for axis in 'xyz':
            mc.setAttr('%s.r%s' % (mainTargetRig['offset'], axis), 0)

        blinkAttrName = 'blink'
        blinkHeightAttrName = 'blinkHeight'
        openBiasAttrName = 'openBalance'
        blinkPushAttrName = 'blinkPush'

        blinkAttr = mainTargetRig['control']+'.'+blinkAttrName
        blinkHeightAttr = mainTargetRig['control']+'.'+blinkHeightAttrName
        openBiasAttr = mainTargetRig['control']+'.'+openBiasAttrName
        blinkPushAttr = mainTargetRig['control']+'.'+blinkPushAttrName

        if self.hasEyelids:
            Nodes.addAttrTitle(mainTargetRig['control'], 'blinking')
            mc.addAttr(mainTargetRig['control'], at='float', ln=blinkAttrName, k=True, hasMinValue=True, minValue=-1, hasMaxValue=True, maxValue=1)
            mc.addAttr(mainTargetRig['control'], at='float', ln=blinkHeightAttrName, k=True, hasMinValue=True, minValue=0, hasMaxValue=True, maxValue=1, dv=0.5)
            mc.addAttr(mainTargetRig['control'], at='float', ln=openBiasAttrName, k=False, hasMinValue=True, minValue=-1, hasMaxValue=True, maxValue=1)
            mc.setAttr(openBiasAttr, channelBox=True)
            if not self.hasCurveRig:
                mc.addAttr(mainTargetRig['control'], at='float', ln=blinkPushAttrName, k=False, hasMinValue=True, minValue=0, hasMaxValue=True, maxValue=1000, dv=0)
                mc.setAttr(blinkPushAttr, channelBox=True)
        mc.move(0, 0, mainTargetOffset, mainTargetRig['offset'], r=True, ws=True)
        mc.parent(mainTargetRig['offset'], controlGroup)

        Tools.parentScaleConstraint(self.parentNode, mainTargetRig['offset'])

        guideList = [eyeballGuide]
        if self.hasEyelids:
            guideList.extend([innerlidGuide, upperlidinGuide, upperlidGuide, upperlidoutGuide, outerlidGuide, lowerlidoutGuide, lowerlidGuide, lowerlidinGuide])
        
        controlRigList = [mainTargetRig]

        allEyelidControlNodesListFlat = list()
        blinkControlRigListFlat = list()

        eyeballControlNodesList = list()
        rigNodeList = list()
        jointNodeList = list()
        lidRigsList = list()
        allLashJoints = list()

        for side in [Settings.leftSide, Settings.rightSide]:

            outerInnerJointList.append([])
            
            eyeballSize = eyeballSizeLeft if side == Settings.leftSide else eyeballSizeRight

            locNodeList = list()

            nodeList = [Guiding.convertGuide(guide, mirror=True if side == Settings.rightSide else False, 
                            mirrorRotate=(0, 180, 0) if g == 0 else (0, 0, 180))[0] for g, guide in enumerate(guideList)]

            eyeball = nodeList[0]

            eyelidControlNodesList = list()
            blinkControlRigList = list()

            if side == Settings.rightSide:
                parentNodeRightSide = Nodes.replaceSide(self.parentNode, Settings.rightSide)
                if Nodes.exists(parentNodeRightSide):
                    self.parentNode = Nodes.getPivotCompensate(parentNodeRightSide)
            
            eyeNode = AddNode.emptyNode(component=self.name, side=side, element='ball', nodeType='rig')
            Nodes.alignObject(eyeNode, eyeball)
            mc.parent(eyeNode, controlGroup)
            Tools.parentScaleConstraint(self.parentNode, eyeNode)

            eyelidGroup = AddNode.emptyNode(component=self.name, side=side, element='lids', nodeType='rig')
            Nodes.alignObject(eyelidGroup, eyeball)
            mc.parent(eyelidGroup, eyeNode)

            upnode = AddNode.emptyNode(component=self.name, side=side, nodeType='upnode')
            Nodes.alignObject(upnode, eyelidGroup)
            mc.move(eyeballSize*2, 0, 0, upnode, r=True, os=True)
            mc.parent(upnode, eyeNode)

            rigNodeList.append(upnode)

            fleshyNodeList = list()
            resNodeList = list()

            cntNodeList = list()

            if self.hasEyelids:
                for n, node in enumerate(nodeList[1:]):

                    element = ['innerlid', 'upperlidin', 'upperlid', 'upperlidout', 'outerlid', 'lowerlidout', 'lowerlid','lowerlidin'][n]

                    guideNode = Nodes.createName(self.name, Settings.leftSide, Settings.guidePivotSuffix, element=element)[0]
                    guideData = Guiding.getGuideAttr(guideNode)

                    offset = guideData['offset']
                    isVisible = guideData['isVisible']

                    node = mc.rename(node, Nodes.createName(self.name, side, Settings.baseNodeSuffix, element=element)[0])

                    locNodeList.append(node)
                    rigNodeList.append(node)

                    resNode = AddNode.emptyNode(component=self.name, side=side, element=element, nodeType='result')
                    mc.parent(resNode, eyelidGroup)
                    Nodes.alignObject(resNode, eyelidGroup)
                    resNodeList.append(resNode)

                    createJointNode = False
                    if self.hasCurveRig:
                        if n in [0, 4]:
                            createJointNode = True
                    else:
                        if isVisible:
                            createJointNode = True

                    if createJointNode:
                        jointNode = AddNode.jointNode(component=self.name, 
                                                        side=side, 
                                                        element=element, 
                                                        size=eyeballSize*0.1,
                                                        skeletonParent=self.parentNode)
                        jointNodeList.append(jointNode)
                        Nodes.alignObject(jointNode, node)
                        mc.parent(jointNode, node)

                    base = AddNode.emptyNode(component=self.name, side=side, element=element, nodeType='aimBase')
                    Nodes.alignObject(base, node)
                    mc.parent(base, eyelidGroup)
                    for axis in 'xyz':
                        mc.setAttr('%s.t%s' % (base, axis), 0)

                    aimtarget = AddNode.emptyNode(component=self.name, side=side, element=element, nodeType='aimTarget')
                    Nodes.alignObject(aimtarget, node)
                    aimtargetOff = AddNode.parentNode(aimtarget, nodeType='aimTargetOff')
                    mc.parent(aimtargetOff, eyelidGroup)
                    mc.aimConstraint(aimtarget, base, aim=(0,0,1), wu=(0,0,1), wuo=upnode, wut='object', u=(1,0,0))

                    target = AddNode.emptyNode(component=self.name, side=side, element=element, nodeType='target')
                    Nodes.alignObject(target, node)
                    targetOff = AddNode.parentNode(target, nodeType='targetOff')
                    mc.parentConstraint(base, target, mo=True)

                    for axis in 'xyz':
                        attr = '%s.r%s' % (target, axis)
                        Nodes.removeConnection(attr)

                    dif = AddNode.emptyNode(component=self.name, side=side, element=element, nodeType='dif')
                    Nodes.alignObject(dif, node)
                    mc.parent(dif, target)
                    
                    controlRig = Control.createControl(node=node,
                                                            component=self.name,
                                                            element=element,
                                                            side=side)

                    # locking rotateZ for now because the sec controls don't follow # unlocked again since it seems to work
                    Nodes.lockAndHideAttributes(controlRig['control'], t=[False, False, False], r=[True, True, n in [1, 3, 5, 7]], s=[True, True, True])

                    controlRigList.append(controlRig)
                    eyelidControlNodesList.append(controlRig)

                    # blink
                    offsetScale = offset[2]
                    if side == Settings.rightSide:
                        offsetScale = [-1*x for x in offsetScale]

                    blinkOffset = [[offset[0][0], offset[0][1], offset[0][2]+eyeballSize*0.1], 
                                    [offset[1][0], offset[1][1], offset[1][2]], 
                                    offsetScale]
                    
                    blinkControlRig = Control.createControl(node=guideNode,
                                                                component=self.name,
                                                                element=element+'Blink',
                                                                side=side,
                                                                shape='Cross',
                                                                offset=blinkOffset,
                                                                mirrorScale=[1, 1, 1] if n == 0 or n == 4 else [-1, 1, 1],
                                                                useGuideAttr=False,
                                                                isVisible=isVisible,
                                                                postDeformAlignment=True)

                    Nodes.lockAndHideAttributes(blinkControlRig['control'], t=[False, False, False], r=[True, True, False], s=[True, True, True])
                    Nodes.lockAndHideAttributes(blinkControlRig['offset'], t=[False, False, False], r=[False, False, False], s=[True, True, True])

                    blinkControlRigList.append(blinkControlRig)
                    allEyelidControlNodesListFlat.append(blinkControlRig)
                    blinkControlRigListFlat.append(blinkControlRig)

                    # blink control visibility
                    visAttr = '%s.visibility'%blinkControlRig['offset']
                    visDrv = '%s.blink'%mainTargetRig['control']
                    mc.setDrivenKeyframe(visAttr, cd=visDrv, dv=0, v=1, itt='linear', ott='linear')
                    mc.setDrivenKeyframe(visAttr, cd=visDrv, dv=1, v=0, itt='linear', ott='linear')
                    mc.setDrivenKeyframe(visAttr, cd=visDrv, dv=1, v=1, itt='linear', ott='linear')
                    mc.setDrivenKeyframe(visAttr, cd=visDrv, dv=0, v=0, itt='linear', ott='linear')

                    mc.parent(controlRig['offset'], controlGroup)
                    mc.parent(blinkControlRig['offset'], controlGroup)

                    cntNode = AddNode.inbetweenNode(controlRig['mirrorScale'], zeroValues=True)
                    cntNodeList.append(cntNode)

                    mc.aimConstraint(node, resNode, aim=(0, 0, 1), wu=(0, 1, 0), wuo=node, wut='objectrotation', u=(0, 1, 0))
                    AddNode.parentNode(resNode, nodeType='resultOff')
                    if createJointNode:
                        mc.parent(jointNode, resNode)
                    
                    fleshyNode = AddNode.emptyNode(component=self.name, side=side, nodeType=Settings.drivenNodeSuffix, element=element, specific='fleshy')
                    Nodes.alignObject(fleshyNode, eyelidGroup)
                    mc.parent(fleshyNode, eyelidGroup)
                    mc.parent(controlRig['offset'], fleshyNode)
                    fleshyNodeList.append(fleshyNode)

                    mc.parent(node, controlRig['control'])
                    
                    for axis in 'xyz':
                        Nodes.mulNode(input1='%s.t%s'%(controlRig['control'], axis), 
                                        input2=-1 if side == Settings.rightSide else 1, 
                                        output='%s.t%s'%(aimtarget, axis))

                    mc.parentConstraint(aimtarget, dif)
                    
                    for axis in 'xyz':
                        Nodes.mulNode(input1='%s.t%s'%(dif, axis), 
                                        input2=1 if side == Settings.rightSide else -1, 
                                        output='%s.t%s'%(cntNode, axis))

                    mc.parent(targetOff, eyelidGroup)

                    rigNodeList.extend([resNode, base, aimtarget, target, dif])
                    if createJointNode:
                        jointNodeList.append(jointNode)
                
                
                blinkControlRigSet.append(blinkControlRigList)

            # eyeball rig

            eyeballRig = Control.createControl(node=eyeball,
                                                component=self.name,
                                                element='ball',
                                                side=side,
                                                mirrorAxis='X',
                                                mirrorScale=None)

            eyeballControlNodesList.append(eyeballRig)

            mc.parent(eyeballRig['offset'], controlGroup)
            Nodes.lockAndHideAttributes(eyeballRig['control'], [True, True, True], [False, False, True], [True, True, True])
            mc.setAttr('%s.rotateOrder'%eyeballRig['control'], 2)
            
            srcNode, trgNode = [self.parentNode, eyeballRig['offset']]

            mc.parentConstraint(srcNode, trgNode, mo=True)
            mc.scaleConstraint(srcNode, trgNode, mo=True)

            eyeballJoint = AddNode.jointNode(eyeballRig['control'], 
                                            size=eyeballSize*0.1,
                                            skeletonParent=self.parentNode)
            eyeballJointList.append(eyeballJoint)
            
            # highlight rig

            if self.hasHighlight:

                highlightRig = Control.createControl(node=eyeball,
                                                    component=self.name,
                                                    element='highlight',
                                                    side=side,
                                                    shape='Rounded Rectangle',
                                                    offset=[eyeballOffset[0], 
                                                            eyeballOffset[1], 
                                                            [eyeballOffset[2][0]*0.25, eyeballOffset[2][1]*0.25, eyeballOffset[2][2]*0.25]],
                                                    useGuideAttr=False,
                                                    mirrorAxis='X',
                                                    mirrorScale=None)

                controlRigList.append(highlightRig)

                mc.parent(highlightRig['offset'], controlGroup)
                Nodes.lockAndHideAttributes(highlightRig['control'], [True, True, True], [False, False, True], [True, True, True])
                
                Tools.blendBetween([self.parentNode], 
                                    [eyeballRig['control']], 
                                    [highlightRig['offset']],
                                    attrNode=highlightRig['control'],
                                    attrName='followIris',
                                    attrTitle='highlight')

                highlightJoint = AddNode.jointNode(highlightRig['control'], 
                                                    size=eyeballSize*0.05,
                                                    skeletonParent=self.parentNode)
                jointNodeList.append(highlightJoint)

            # iris rig

            if self.hasIris:

                Nodes.addAttrTitle(eyeballRig['control'], 'iris')
                irisJoints = list()
                
                initLength = abs(eyeballOffset[2][0]*0.5)

                for n, name in enumerate(['iris', 'pupil']):
                    attrName = name+'Size'
                    attr = eyeballRig['control']+'.'+attrName
                    maxVal = [(eyeballSize*0.5)/initLength, 1/self.initialPupilSize][n]
                    mc.addAttr(eyeballRig['control'], at='float', ln=attrName, k=True, dv=1, 
                                hasMinValue=True, minValue=0.05, hasMaxValue=True, maxValue=maxVal)
                    jointNode = AddNode.jointNode(eyeballRig['control'], 
                                                element=name, 
                                                size=eyeballSize*0.05,
                                                skeletonParent=self.parentNode)
                    irisJoints.append(jointNode)
                    jointNodeList.append(jointNode)
                    jointOff = AddNode.parentNode(jointNode)
                    
                    if self.hasIrisSquash:
                        for axis in 'XY':
                            squashAttrName = name+'Squash'+axis
                            squashAttr = eyeballRig['control']+'.'+squashAttrName
                            Nodes.addAttr(squashAttr, dv=1, minVal=0, maxVal=1 if name == 'iris' else (1/self.initialPupilSize), k=True, d=True)
                            squashNode = Nodes.mulNode(attr,
                                                    squashAttr,
                                                    '%s.scale%s'%(jointNode, axis))

                        mc.connectAttr(attr, '%s.sz'%jointNode)
                    else:
                        for axis in 'xyz':
                            mc.connectAttr(attr, '%s.s%s'%(jointNode, axis))

                    if n == 0:
                        jointAttr = '%s.tz'%jointNode 
                        expr = '$attr = %s*%s;\n' % (attr, initLength) \
                            + '$calc = `pow %s 2`-`pow $attr 2`;\n' % (eyeballSize*0.5) \
                            + '%s = `pow $calc 0.5`\n' % (jointAttr)
                        Nodes.exprNode(jointAttr, expr)

                    if n == 1:
                        if side == Settings.rightSide:
                            pupilGuide = Tools.mirrorObject(pupilGuide)
                        Nodes.alignObject(jointOff, pupilGuide)
                        Nodes.setParent(jointOff, irisJoints[0])

            eyetargetRig = Control.createControl(node=eyeNode,
                                                    component=self.name,
                                                    element='target',
                                                    side=side,
                                                    shape='Circle',
                                                    alignAxis='Z',
                                                    mirrorAxis='Z',
                                                    offset=[[0, 0, 0], [90, 0, 0], eyeballOffset[2]],
                                                    useGuideAttr=False,
                                                    mirrorScale=None)

            Nodes.lockAndHideAttributes(eyetargetRig['control'], s=[True, True, True], v=True)

            for axis in 'xyz':
                mc.setAttr('%s.r%s' % (eyetargetRig['offset'], axis), 0)
            [controlRigList.append(i) for i in [eyeballRig, eyetargetRig]]

            mc.move(0, 0, mainTargetOffset, eyetargetRig['offset'], r=True, ws=True)
            mc.parent(eyetargetRig['offset'], mainTargetRig['control'])
            mc.parent(eyeballRig['offset'], eyeNode)

            eyetargetControlNodesList.append(eyetargetRig)

            eyeballAim = AddNode.inbetweenNode(eyeballRig['offset'], nodeType='aim')
            eyeballAimList.append(eyeballAim)
            mc.aimConstraint(eyetargetRig['control'], eyeballAim, aim=(0, 0, 1), wu=(0, 0, 1), wuo=upnode, wut='object',
                            u=(0, 0, 1), mo=True)

            captureNode = AddNode.emptyNode(component=self.name, side=side, element='ball', nodeType='capture')
            Nodes.alignObject(captureNode, eyelidGroup)
            mc.orientConstraint(eyeballRig['control'], captureNode)

            mc.parent(captureNode, eyeballRig['offset'])
            Nodes.setTrs(eyeballRig['offset'])

            # ik line

            helperGroup = AddNode.emptyNode(component=self.name, side=side, element='helper')
            Nodes.setParent(helperGroup, rigGroup)

            startNode = eyeballRig['control']
            endNode = eyetargetRig['control']

            lineNode = Nodes.curveNode(component=self.name,
                                        side=side,
                                        element='ikLine',
                                        nodeType=Settings.templateSuffix,
                                        curveType='linearCurve',
                                        pointCount=2)[0]
                                
            mc.setAttr('%s.overrideEnabled'%lineNode, True)
            mc.setAttr('%s.overrideDisplayType'%lineNode, 2)
            mc.setAttr('%s.overrideColor'%lineNode, mc.getAttr('%s.overrideColor'%mc.listRelatives(startNode, shapes=True)[0]))

            mc.setAttr('%s.inheritsTransform'%lineNode, False)

            for i, ikLineNode in enumerate([startNode, endNode]):
                ikLineClsNode = Nodes.clusterNode('%s.cv[%s]'%(lineNode, i),
                                                component=self.name,
                                                side=side,
                                                element='ikLine',
                                                specific=['start', 'end'][i])

                mc.pointConstraint(ikLineNode, ikLineClsNode, mo=False)
                mc.parent(ikLineClsNode, helperGroup)
                
                VisSwitch.connectVisSwitchGroup([ikLineClsNode], rigGroup, displayAttr='setupDisplay')

            VisSwitch.connectVisSwitchGroup([lineNode], rigGroup, displayAttr='ikLineControlDisplay')
                
            mc.parent(lineNode, eyetargetRig['control'])
                
            for trs in 'tr':
                for axis in 'xyz':
                    mc.setAttr('%s.%s%s'%(lineNode, trs, axis), 0)

            # fleshy eyelids
            if self.hasEyelids:
                Nodes.addAttrTitle(mainTargetRig['control'], 'fleshy')

                for a, attr in enumerate([['upperlidFleshyX', 0.2],
                                            ['upperlidFleshyY', 0.8],
                                            ['lowerlidFleshyX', 0.2],
                                            ['lowerlidFleshyY', 0.4],
                                            ['innerlidFleshyX', 0.1],
                                            ['innerlidFleshyY', 0.1],
                                            ['outerlidFleshyX', 0.1],
                                            ['outerlidFleshyY', 0.1],
                                            ['upperlidFleshyRotate', 0.1],
                                            ['lowerlidFleshyRotate', 0.1]]):

                    if a < 8:

                        if side == Settings.leftSide:
                            mc.addAttr(mainTargetRig['control'], at='float', ln=attr[0], dv=attr[1], keyable=False, hasMaxValue=True, maxValue=45.0, hasMinValue=True, minValue=0.0)
                            mc.setAttr(mainTargetRig['control']+'.'+attr[0], cb=True)

                        targetAxis = 'X' if attr[0][-1] == 'Y' else 'Y'

                        if a == 0 or a == 1:
                            f = 2
                        if a == 2 or a == 3:
                            f = 6
                        if a == 4 or a == 5:
                            f = 0
                        if a == 6 or a == 7:
                            f = 4

                        Nodes.mulNode(input1='%s.rotate%s' % (captureNode, targetAxis), 
                                        input2=mainTargetRig['control']+'.'+attr[0], 
                                        output='%s.rotate%s' % (fleshyNodeList[f], targetAxis))

                    else:

                        if side == Settings.leftSide:
                            mc.addAttr(mainTargetRig['control'], at='float', ln=attr[0], dv=attr[1], keyable=False, hasMaxValue=True, maxValue=10.0, hasMinValue=True, minValue=0.0)
                            mc.setAttr(mainTargetRig['control']+'.'+attr[0], cb=True)

                        # mul mir is required to compensate mirror scale
                        if a == 8:
                            f = 2
                        if a == 9:
                            f = 6

                        mulMirNode = Nodes.mulNode(input1='%s.rotateY' % captureNode, 
                                                    input2=(-1 if side == Settings.rightSide else 1) * (-1 if a == 9 else 1), 
                                                    output=None)

                        Nodes.mulNode(input1='%s.output' % mulMirNode, 
                                        input2=mainTargetRig['control']+'.'+attr[0], 
                                        output='%s.rotateZ' % cntNodeList[f])

            rigNodeList.append(captureNode)
            jointNodeList.append(eyeballJoint)

            if self.hasEyelids:
                
                blinkAddNegNode = Nodes.addNode(input1=blinkAttr, input2=-1)
                blinkMulNegNode = Nodes.mulNode(input1='%s.output'%blinkAddNegNode, input2=-1)

                # constraining for in and out eyelids
                for n, node in enumerate([eyelidControlNodesList[i] for i in [1, 3, 5, 7]]):

                    midNode = eyelidControlNodesList[2 if n == 0 or n == 1 else 6]['control']
                    midResNode = resNodeList[2 if n == 0 or n == 1 else 6]
                    cornerNode = eyelidControlNodesList[0 if n == 0 or n == 3 else 4]['control']
                    
                    Nodes.addAttrTitle(node['control'], 'influence')
                    mc.addAttr(node['control'],
                                at='float',
                                ln='cornerInfluence',
                                k=False,
                                dv=0.5,
                                hasMaxValue=True,
                                maxValue=1.0,
                                hasMinValue=True,
                                minValue=0.0)
                    mc.setAttr(node['control']+'.'+'cornerInfluence', cb=True)

                    # open close X and Y push

                    pushOpenNode = AddNode.inbetweenNode(node['mirrorScale'], nodeType='pushOpen', zeroValues=True)
                    for axis in 'xy':
                        pushAttrName = axis+'PushOpen'
                        pushAttr = node['control']+'.'+pushAttrName
                        mc.addAttr(node['control'],
                                    at='float',
                                    ln=pushAttrName,
                                    k=False,
                                    dv=1)
                        mc.setAttr(pushAttr, cb=True)

                        clampNode = Nodes.clampNode(input='%s.rx'%midResNode, 
                                        clampMin=0 if 'lower' in midNode else -100,
                                        clampMax=0 if 'upper' in midNode else 100)
                        mulNode = Nodes.mulNode(input1='%s.outputR'%clampNode, 
                                        input2=(-0.01 if 'upper' in midNode else 0.01) * 
                                        (-1 if 'lidin' in pushOpenNode and axis == 'x' else 1) * 
                                        (-1 if 'lower' in midNode and axis == 'x' else 1))
                        mulBlinkNode = Nodes.mulNode(input1='%s.output'%mulNode, 
                                        input2='%s.output'%blinkMulNegNode)
                        Nodes.mulNode(input1='%s.output'%mulBlinkNode, 
                                        input2=pushAttr, 
                                        output='%s.t%s'%(pushOpenNode, axis))

                    pushCloseNode = AddNode.inbetweenNode(pushOpenNode, nodeType='pushClose', zeroValues=True)
                    for axis in 'xy':
                        pushAttrName = axis+'PushClose'
                        pushAttr = node['control']+'.'+pushAttrName
                        mc.addAttr(node['control'],
                                    at='float',
                                    ln=pushAttrName,
                                    k=False,
                                    dv=1 if axis == 'y' else 0)
                        mc.setAttr(pushAttr, cb=True)

                        clampNode = Nodes.clampNode(input='%s.rx'%midResNode, 
                                        clampMin=0 if 'upper' in midNode else -100,
                                        clampMax=0 if 'lower' in midNode else 100)
                        mulNode = Nodes.mulNode(input1='%s.outputR'%clampNode, 
                                        input2=(-0.01 if 'upper' in midNode else 0.01) * 
                                        (-1 if 'lidin' in pushCloseNode and axis == 'x' else 1) * 
                                        (-1 if 'lower' in midNode and axis == 'x' else 1))
                        mulBlinkNode = Nodes.mulNode(input1='%s.output'%mulNode, 
                                        input2='%s.output'%blinkMulNegNode)
                        Nodes.mulNode(input1='%s.output'%mulBlinkNode, 
                                        input2=pushAttr, 
                                        output='%s.t%s'%(pushCloseNode, axis))

                # blink fleshy

                fleshyBlinkNodeList = list()
                fleshyBlinkDrvCaptureNodeList = list()
                for f, fleshyNode in enumerate(fleshyNodeList):
                    if f == 1 or f == 2 or f == 3:
                        n = 0 if f == 1 else 1 if f == 2 else 2
                        fleshyBlinkNode = AddNode.emptyNode(component=self.name, 
                                                            side=side, 
                                                            nodeType=Settings.drivenNodeSuffix, 
                                                            element=['lidin', 'lidmid', 'lidout'][n], 
                                                            specific='fleshyBlink')
                        Nodes.alignObject(fleshyBlinkNode, resNodeList[f])
                        mc.parent(fleshyBlinkNode, eyelidGroup)
                        fleshyBlinkNodeList.append(fleshyBlinkNode)
                        
                        fleshyBlinkDrvCaptureNode = AddNode.inbetweenNode(fleshyBlinkNode,
                                                            nodeType='drvCapture')
                        fleshyBlinkDrvCaptureNodeList.append(fleshyBlinkDrvCaptureNode)
                        for axis in 'xy':
                            if n == 1:
                                drvMul = 0.5
                            else:
                                drvMul = 0.3
                                #drvMul = '%s.cornerInfluence'%Nodes.createName(component=self.name, 
                                                                                #side=side, 
                                                                                #nodeType=Settings.controlSuffix, 
                                                                                #element='upper'+['lidin', 'lid', 'lidout'][n])[0]
                            mulNode = Nodes.mulNode('%s.r%s'%(fleshyNodeList[2], axis),
                                            drvMul)
                            Nodes.mulNode('%s.output'%mulNode,
                                            -1 if axis == 'y' else 1,
                                            '%s.r%s'%(fleshyBlinkDrvCaptureNode, 'x' if axis == 'y' else 'y'))

                for b, blinkControlRig in enumerate(blinkControlRigList):
                    srcNode = blinkControlRig['offset']
                    trgAlignNode = eyelidControlNodesList[[0, 1, 2, 3, 4, 3, 2, 1][b]]['control']
                    if b == 0 or b == 4:
                        trgParentNode = trgAlignNode
                    else:
                        trgParentNode = fleshyBlinkDrvCaptureNodeList[[None, 0, 1, 2, None, 2, 1, 0][b]]
                    Nodes.alignObject(srcNode, trgAlignNode)
                    mc.parent(srcNode, trgParentNode)
                    Nodes.setTrs(srcNode, 0, t=False, r=True, s=False)

                aimBaseList = [Nodes.replaceNodeType(x, 'aimBase') for x in resNodeList]
                for f, fleshyBlinkNode in enumerate(fleshyBlinkNodeList):
                    if f == 0:
                        upperNode = aimBaseList[1]
                        lowerNode = aimBaseList[7]
                    if f == 1:
                        upperNode = aimBaseList[2]
                        lowerNode = aimBaseList[6]
                    if f == 2:
                        upperNode = aimBaseList[3]
                        lowerNode = aimBaseList[5]
                    orientCnt = mc.orientConstraint([upperNode, lowerNode], fleshyBlinkNode, mo=False)[0]
                    mc.setAttr('%s.interpType'%orientCnt, 2)
                    mc.setDrivenKeyframe('%s.%sW0'%(orientCnt, upperNode), cd=blinkHeightAttr, dv=1, v=1, itt='linear', ott='linear')
                    mc.setDrivenKeyframe('%s.%sW1'%(orientCnt, lowerNode), cd=blinkHeightAttr, dv=1, v=0, itt='linear', ott='linear')
                    mc.setDrivenKeyframe('%s.%sW0'%(orientCnt, upperNode), cd=blinkHeightAttr, dv=0, v=0, itt='linear', ott='linear')
                    mc.setDrivenKeyframe('%s.%sW1'%(orientCnt, lowerNode), cd=blinkHeightAttr, dv=0, v=1, itt='linear', ott='linear')
                    
                # blink push
                if not self.hasCurveRig:
                    for r, resNode in enumerate([resNodeList[2], resNodeList[6]]):
                        blinkPushNode = AddNode.inbetweenNode(resNode, nodeType=blinkPushAttrName)
                        mc.transformLimits(blinkPushNode, tz=(0, 1000), etz=(1, 1))
                        mulNode = Nodes.mulNode(input1='%s.rotate%s' % (resNode, 'X'), 
                                                input2=blinkPushAttr, 
                                                output=None)
                        Nodes.mulNode(input1='%s.output' % mulNode, 
                                        input2=0.01, 
                                        output='%s.translate%s' % (blinkPushNode, 'Z'))

                        inOutNodes = [resNodeList[1], resNodeList[3]] if r == 0 else [resNodeList[5], resNodeList[7]]
                        for inOutNode in inOutNodes:
                            inOutBlinkPushNode = AddNode.inbetweenNode(inOutNode, nodeType=blinkPushAttrName)
                            mc.connectAttr('%s.translate%s' % (blinkPushNode, 'Z'), '%s.translate%s' % (inOutBlinkPushNode, 'Z'))
                
                allEyelidControlNodesList.append(eyelidControlNodesList)
                allEyelidControlNodesListFlat.extend(eyelidControlNodesList)
            
                # blink blending

                for n, node in enumerate(locNodeList):
                    blkNode = AddNode.parentNode(node, nodeType='blk', zeroValues=True)
                    blkOffset = AddNode.childNode(eyelidControlNodesList[n]['control'], nodeType='blkOffset', zeroValues=True)
                    pointCnt = mc.pointConstraint([blkOffset, blinkControlRigList[n]['control']], blkNode, mo=False)[0]
                    if n > 4 or (side == Settings.rightSide and n in [0, 4]):
                        mc.setAttr('%s.rz'%blkOffset, 180)
                    orientCnt = mc.orientConstraint([blkOffset, blinkControlRigList[n]['control']], blkNode, mo=False)[0]
                    mc.setAttr('%s.interpType'%orientCnt, 2)

                    for cnt in [pointCnt, orientCnt]:
                        for t, targetNode in enumerate([blkOffset, blinkControlRigList[n]['control']]):
                            blinkAttr = '%s.blink' % (mainTargetRig['control'])
                            for v in [t, 1 - t]:
                                mc.setDrivenKeyframe(cnt + '.' + targetNode + 'W' + str(t), cd=blinkAttr, dv=v,
                                                    v=1 if v == t else 0, itt='linear', ott='linear')

                    blinkGuide = Nodes.replaceNodeType(blinkControlRigList[n]['control'], Settings.guidePivotSuffix)
                    if mc.objExists(blinkGuide):
                        Nodes.alignObject(blinkControlRigList[n]['offset'], blinkGuide)
            
                # blink negate
                for n, name in enumerate(['upperlid', 'lowerlid']):

                    drvValue = Tools.getDistance(upperlidGuide, lowerlidGuide)

                    ctlNode = Nodes.createName(self.name, side, Settings.controlSuffix, element=name)[0]

                    openedDrvNode = AddNode.parentNode(ctlNode, nodeType='openDrv', lockScale=True, zeroValues=True)
                    mc.transformLimits(openedDrvNode, ty=(0, drvValue*10), ety=(1, 1))

                    mulNode = Nodes.mulNode(input1=blinkAttr, 
                                            input2=drvValue*-1, 
                                            output=None)
                                            
                    mulBiasNode = Nodes.mulNode(input1='%s.output' % mulNode, 
                                                input2=None, 
                                                output='%s.translateY' % openedDrvNode)

                    if n == 0:
                        mc.setDrivenKeyframe('%s.input2' % mulBiasNode, cd=openBiasAttr, dv=1, v=1, itt='linear', ott='linear')
                        mc.setDrivenKeyframe('%s.input2' % mulBiasNode, cd=openBiasAttr, dv=-1, v=0, itt='linear', ott='linear')
                    else:
                        mc.setDrivenKeyframe('%s.input2' % mulBiasNode, cd=openBiasAttr, dv=-1, v=1, itt='linear', ott='linear')
                        mc.setDrivenKeyframe('%s.input2' % mulBiasNode, cd=openBiasAttr, dv=1, v=0, itt='linear', ott='linear')

                # constraining for in and out eyelids
                for n, node in enumerate([eyelidControlNodesList[i] for i in [1, 3, 5, 7]]):
                    
                    midNode = eyelidControlNodesList[2 if n == 0 or n == 1 else 6]['control']
                    cornerNode = eyelidControlNodesList[0 if n == 0 or n == 3 else 4]['control']

                    targetNodes = list()
                    influenceAttr = '%s.cornerInfluence' % (node['control'])
                    for targetNode in [midNode, cornerNode]:
                        targetNodes.append(Nodes.replaceNodeType(targetNode, Settings.scaleCompensateNode))
                    parentCnt = mc.parentConstraint(targetNodes, node['offset'], mo=True)[0]
                    mc.setAttr('%s.interpType'%parentCnt, 2)
                    for t, targetNode in enumerate(targetNodes):
                        for v in [t, 1-t]:
                            mc.setDrivenKeyframe(parentCnt+'.'+targetNode+'W'+str(t), cd=influenceAttr, dv=v, v=1 if v == t else 0, itt='linear', ott='linear')

            # outer lid controls

            if self.hasOuterLine:
                outerGroup = AddNode.emptyNode(component=self.name, side=side, element='outer')
                Tools.parentScaleConstraint(self.parentNode, outerGroup)
                mc.parent(outerGroup, controlGroup)
                if self.hasCurveRig:
                    outerGuides = [innerlidOuterGuide,
                                    upperlidinOuterGuide,
                                    upperlidOuterGuide,
                                    upperlidoutOuterGuide,
                                    outerlidOuterGuide,
                                    lowerlidoutOuterGuide,
                                    lowerlidOuterGuide,
                                    lowerlidinOuterGuide]
                else:
                    outerGuides = [upperlidinOuterGuide,
                                    upperlidOuterGuide,
                                    upperlidoutOuterGuide,
                                    lowerlidoutOuterGuide,
                                    lowerlidOuterGuide,
                                    lowerlidinOuterGuide]

                outerControlNodesList = list()

                for n, node in enumerate(outerGuides):
                    
                    if self.hasCurveRig:
                        elementName = ['innerlidOuter', 'upperlidinOuter', 'upperlidOuter', 'upperlidoutOuter', 'outerlidOuter', 'lowerlidoutOuter', 'lowerlidOuter','lowerlidinOuter'][n]
                    else:
                        elementName = ['upperlidinOuter', 'upperlidOuter', 'upperlidoutOuter', 'lowerlidoutOuter', 'lowerlidOuter','lowerlidinOuter'][n]
                    
                    node = Guiding.convertGuide(node, mirror=True if side == Settings.rightSide else False)[0]

                    controlRig = Control.createControl(node=node,
                                                        side=side,
                                                        component=self.name,
                                                        element=elementName,
                                                        lockAndHide=[[False, False, False], [True, True, True], [True, True, True]])
                    if not self.hasCurveRig or (elementName == 'outerlidOuter' or elementName == 'innerlidOuter'):
                        jointNodeList.append(AddNode.jointNode(controlRig['control'], skeletonParent=self.parentNode))
                    outerControlNodesList.append(controlRig)
                    allOuterControlNodesList.append(controlRig)
                    mc.parent(controlRig['offset'], outerGroup)
                    
                    # outer lid push
                    if self.hasCurveRig:
                        cntNode = AddNode.parentNode(controlRig['control'], Settings.cntNodeSuffix, lockScale=True, zeroValues=True)
                        mc.transformLimits(cntNode, tx=(0, 0), etx=((0, 1) if 'out' in elementName else (1, 0)) if 'lower' in node else ((1, 0) if 'out' in elementName else (0, 1)))
                        mc.transformLimits(cntNode, ty=(0, 0), ety=(1, 0))
                        mc.transformLimits(cntNode, tz=(0, 0), etz=(0, 1))
                        mc.transformLimits(cntNode, rx=(0, 0), erx=(1, 0))
                        Nodes.addAttrTitle(controlRig['control'], 'influence')
                        for t, trs in enumerate(['translateX', 'translateY', 'translateZ', 'rotateX']):
                            if t == 0 and not 'lidin' in node and not 'lidout' in node:
                                continue
                            attrName = trs+'_push'
                            attr = controlRig['control']+'.'+attrName
                            mc.addAttr(controlRig['control'], at='float', ln=attrName, k=False, hasMinValue=True, minValue=0)
                            mc.setAttr(attr, channelBox=True)

                            mulInitNode = Nodes.mulNode(input1='%s.rotateX' % (resNodeList[n]), 
                                                    input2=-1 if 'lower' in node else 1, 
                                                    output=None)

                            mulNode = Nodes.mulNode(input1='%s.output'%mulInitNode, 
                                                    input2=attr, 
                                                    output=None)

                            mulBlinkNode = Nodes.mulNode(input1='%s.output'%mulNode, 
                                            input2='%s.output'%blinkMulNegNode)

                            Nodes.mulNode(input1='%s.output'%mulBlinkNode, 
                                            input2=[(-0.05 if 'out' in elementName else 0.05)*(-1 if 'lower' in node else 1), -0.05, 0.05, -0.5][t], 
                                            output='%s.%s'%(cntNode, trs))

                if not self.hasCurveRig:
                    for outerControlNodesPartList in [outerControlNodesList[0:3], outerControlNodesList[3:6]]:
                        for c, controlRig in enumerate([outerControlNodesPartList[0], outerControlNodesPartList[2]]):
                            Tools.blendBetween([self.parentNode], 
                                                [outerControlNodesPartList[1]['control']], 
                                                [controlRig['offset']],
                                                attrNode=controlRig['control'],
                                                attrName='mainInfluence', 
                                                attrTitle='follow', 
                                                scaleConstrained=False,
                                                defaultValue=[0.5, 0.5][c],
                                                attrIsKeyable=False)

            # eye squash

            if self.hasSquashStretch:
                
                self.squashGroup = AddNode.emptyNode(component=self.name, side=side, nodeType='squash')
                Nodes.setParent(self.squashGroup, eyeballRig['offset'])

                squashStretchGeos = self.squashStretchLeftGeos if side == Settings.leftSide else self.squashStretchRightGeos

                build = True
                for squashStretchGeo in squashStretchGeos:
                    if not Nodes.exists(squashStretchGeo):
                        mc.warning('Geo node for Eyes squash stretch lattice does not exist: %s'%squashStretchGeo)
                        build = False

                if build:
                    latNodes = Nodes.latticeNode(squashStretchGeos,
                                                component=self.name,
                                                side=side,
                                                element='squashMain')
                    rigNodeList.extend(latNodes[1:])
                    for latNode in latNodes[1:]:
                        Nodes.alignObject(latNode, eyeballRig['control'])
                        [mc.setAttr('%s.s%s'%(latNode, axis), eyeballSize) for axis in 'xyz']
                    if side == Settings.rightSide:
                        for latNode in latNodes:
                            mc.rotate(0, 180, 0, latNode, r=True, os=True)

                    mainSquashRig = Control.createControl(latNodes[1],
                                                            component=self.name,
                                                            element='squashMain',
                                                            side=side,
                                                            size=eyeballSize*1.1,
                                                            shape='Sphere',
                                                            deleteNode=False,
                                                            mirrorScale=[1, 1, -1],
                                                            parentNode=None)

                    Nodes.alignObject(mainSquashRig['offset'], eyeballRig['control'])
                    mc.parent(mainSquashRig['offset'], self.squashGroup)
                    mc.parent(latNodes, self.squashGroup)
                    squashRigs = list()

                    for u in range(2):
                        for v in range(2):

                            if u == 0 and v == 1:
                                i = 1
                                rotOffset = (0, 180, 0)
                                shapeNegate = -1
                            if u == 1 and v == 1:
                                i = 2
                                rotOffset = (0, 0, 0)
                                shapeNegate = 1
                            if u == 0 and v == 0:
                                i = 3
                                rotOffset = (180, 180, 0)
                                shapeNegate = 1
                            if u == 1 and v == 0:
                                i = 4
                                rotOffset = (180, 0, 0)
                                shapeNegate = -1
                            clusterNode = Nodes.clusterNode('%s.pt[%s][%s][0:1]'%(latNodes[1], u, v), 
                                                            component=self.name, 
                                                            side=side, 
                                                            indices=i-2)
                            rigNodeList.append(clusterNode)
                            squashRig = Control.createControl(clusterNode,
                                                                component=self.name,
                                                                element='squash',
                                                                indices=i,
                                                                side=side,
                                                                size=eyeballSize*0.05,
                                                                shape='Cross',
                                                                parentDirection='NodeToControl',
                                                                deleteNode=False,
                                                                mirrorScale=[-1, 1, 1],
                                                                offset=(0, 0, eyeballSize*shapeNegate))
                            squashRigs.append(squashRig)
                            mc.parent(squashRig['offset'], mainSquashRig['scaleCompensate'])
                            mc.rotate(rotOffset[0], rotOffset[1], rotOffset[2], squashRig['offset'], r=True, os=True)
                            mc.rotate(-rotOffset[0], -rotOffset[1], -rotOffset[2], clusterNode, r=True, os=True)

                    # applying eye non-uniform scale

                    eyeScale = self.eyeLeftScale if side == Settings.leftSide else self.eyeRightScale
                    [mc.setAttr('%s.s%s'%(mainSquashRig['offset'], axis), eyeScale[a]) for a, axis in enumerate('xyz')]

                    VisSwitch.connectVisSwitchGroup([x['control'] for x in squashRigs], rigGroup, displayAttr='squashControlDisplay')
                    VisSwitch.connectVisSwitchGroup([mainSquashRig['control']], rigGroup, displayAttr='mainSquashControlDisplay')

            lidRigs = list()
            if self.hasCurveRig and self.hasEyelids:
                names = ['upperlid', 'lowerlid']
                if self.hasOuterLine:
                    names.extend(['upperlidOuter', 'lowerlidOuter'])
                for n, name in enumerate(names):
                    guideCurve = Nodes.createName(self.name, Settings.leftSide, Settings.guideCurveSuffix, element=name)[0]
                    if side == Settings.rightSide:
                        guideCurve = Guiding.convertGuide(guideCurve, mirror=True)[0]
                    lidRig = Curve.Build(curveNode=guideCurve,
                                            component=self.name,
                                            element=name,
                                            side=side,
                                            controlCount=5,
                                            segmenting=False,
                                            scaling=False,
                                            squashing=False,
                                            upAxis='Z',
                                            jointCount=[self.upperLidJointCount, self.lowerLidJointCount, self.upperLidJointCount, self.lowerLidJointCount][n],
                                            skeletonParent=self.parentNode,
                                            skeletonParentToAllJoints=True).createRig()
                    if side == Settings.rightSide:
                        mc.delete(guideCurve)
                    lidRigs.append(lidRig)
                    rigNodeList.extend(lidRig['offsets'])
                    [Nodes.replaceNodeType(x) for x in lidRig['controls']]
                    mc.parent(lidRig['rigGroup'], rigGroup)

                    # alignment and parenting
                    if name == 'upperlid':
                        for s in range(5):
                            Nodes.alignObject(lidRig['offsets'][s], eyelidControlNodesList[s]['control'])
                            mc.parent(lidRig['offsets'][s], resNodeList[s])
                            Nodes.setTrs(lidRig['offsets'][s], value=0, t=False, s=False)
                    if name == 'lowerlid':
                        Nodes.alignObject(lidRig['offsets'][4], eyelidControlNodesList[4]['control'])
                        Nodes.alignObject(lidRig['offsets'][3], eyelidControlNodesList[5]['control'])
                        Nodes.alignObject(lidRig['offsets'][2], eyelidControlNodesList[6]['control'])
                        Nodes.alignObject(lidRig['offsets'][1], eyelidControlNodesList[7]['control'])
                        Nodes.alignObject(lidRig['offsets'][0], eyelidControlNodesList[0]['control'])
                        mc.parent(lidRig['offsets'][4], resNodeList[4])
                        mc.parent(lidRig['offsets'][3], resNodeList[5])
                        mc.parent(lidRig['offsets'][2], resNodeList[6])
                        mc.parent(lidRig['offsets'][1], resNodeList[7])
                        mc.parent(lidRig['offsets'][0], resNodeList[0])
                        Nodes.setTrs(lidRig['offsets'][4], value=0, t=False, s=False)
                        Nodes.setTrs(lidRig['offsets'][3], value=0, t=False, s=False)
                        Nodes.setTrs(lidRig['offsets'][2], value=0, t=False, s=False)
                        Nodes.setTrs(lidRig['offsets'][1], value=0, t=False, s=False)
                        Nodes.setTrs(lidRig['offsets'][0], value=0, t=False, s=False)
                    if name == 'upperlidOuter':
                        for s in range(5):
                            Nodes.alignObject(lidRig['offsets'][s], outerControlNodesList[s]['control'])
                            mc.parent(lidRig['offsets'][s], outerControlNodesList[s]['scaleCompensate'])
                            Nodes.setTrs(lidRig['offsets'][s], value=0, t=False, s=False)
                    if name == 'lowerlidOuter':
                        Nodes.alignObject(lidRig['offsets'][4], outerControlNodesList[4]['control'])
                        Nodes.alignObject(lidRig['offsets'][3], outerControlNodesList[5]['control'])
                        Nodes.alignObject(lidRig['offsets'][2], outerControlNodesList[6]['control'])
                        Nodes.alignObject(lidRig['offsets'][1], outerControlNodesList[7]['control'])
                        Nodes.alignObject(lidRig['offsets'][0], outerControlNodesList[0]['control'])
                        mc.parent(lidRig['offsets'][4], outerControlNodesList[4]['scaleCompensate'])
                        mc.parent(lidRig['offsets'][3], outerControlNodesList[5]['scaleCompensate'])
                        mc.parent(lidRig['offsets'][2], outerControlNodesList[6]['scaleCompensate'])
                        mc.parent(lidRig['offsets'][1], outerControlNodesList[7]['scaleCompensate'])
                        mc.parent(lidRig['offsets'][0], outerControlNodesList[0]['scaleCompensate'])
                        Nodes.setTrs(lidRig['offsets'][4], value=0, t=False, s=False)
                        Nodes.setTrs(lidRig['offsets'][3], value=0, t=False, s=False)
                        Nodes.setTrs(lidRig['offsets'][2], value=0, t=False, s=False)
                        Nodes.setTrs(lidRig['offsets'][1], value=0, t=False, s=False)
                        Nodes.setTrs(lidRig['offsets'][0], value=0, t=False, s=False)

                    # convert joints to eyeball aim setup
                    
                    if n < 2:
                        motionPathLocs = AddNode.emptyNode(component=self.name, side=side, nodeType='motionPathAim', element=name)
                        mc.parent(motionPathLocs, eyeballRig['offset'])
                        for m, mptNode in enumerate(lidRig['motionPathNodes']):
                            locNode = AddNode.emptyNode(node=mptNode, nodeType='mptAim')
                            eyeball = Guiding.convertGuide(guideList[0], mirror=True if side == Settings.rightSide else False, 
                                            mirrorRotate=(0, 180, 0))[0]
                            Nodes.alignObject(locNode, eyeball)
                            if Settings.rightSide:
                                mc.delete(eyeball)
                            mc.parent(locNode, motionPathLocs)
                            Nodes.aimConstraint(mptNode, locNode, aimAxis='z', upAxis='y')
                            mc.parent(lidRig['joints'][m], locNode)

                    # selection sets for jointName in ['innerlid', 'outerlid']:
                    for jointNode in [lidRig['joints'][0], lidRig['joints'][-1]]:
                        mc.delete(jointNode)
                for jointName in ['innerlid', 'outerlid']:
                    jointNode = Nodes.createName(self.name, side, Settings.skinJointSuffix, element=jointName)[0]
                    outerInnerJointList[0 if side == Settings.leftSide else 1].append(jointNode)
                if self.hasOuterLine:
                    for jointName in ['innerlidOuter', 'outerlidOuter']:
                        jointNode = Nodes.createName(self.name, side, Settings.skinJointSuffix, element=jointName)[0]
                lidRigsList.append(lidRigs)
            
            # eyelashes
            lashJoints = list()
            for n, lidRig in enumerate(lidRigs[:2]):
                if not self.hasUpperLashes and n == 0:
                    continue
                if not self.hasLowerLashes and n == 1:
                    continue
                lidControl = eyelidControlNodesList[2 if n == 0 else -2]['control']
                Nodes.addAttrTitle(lidControl, 'eyelash')
                Nodes.addAttr(lidControl+'.tilt')
                for jointNode in lidRig['joints'][1:-1]:
                    lashJoint = AddNode.jointNode(jointNode,
                                      specific='lash',
                                      parentNode=jointNode,
                                      resetTransforms=True)
                    lashJoints.append(lashJoint)
                    if side == Settings.leftSide:
                        mc.connectAttr('%s.tilt'%lidControl, '%s.rx'%lashJoint)
                    else:
                        Nodes.negateConnect('%s.tilt'%lidControl, '%s.rx'%lashJoint)
            allLashJoints.extend(lashJoints)

        controlRigSet.append([eyeballControlNodesList, allEyelidControlNodesListFlat])

        for rigNode in rigNodeList:
            shapeNodeList = mc.listRelatives(rigNode, shapes=True)
            if shapeNodeList != None:
                if mc.objectType(shapeNodeList[0]) == 'locator':
                    for axis in 'XYZ':
                        mc.setAttr('%s.localScale%s' % (shapeNodeList[0], axis), eyeballSize*0.1)

        if self.spaceNodes != [] and self.spaceNodes != None:

            SpaceSwitch.createSpaceSwitch(offNode=mainTargetRig['offset'],
                                        sourceObjs=self.spaceNodes,
                                        switchNames=self.spaceNames)

        Tools.parentScaleConstraint(self.parentNode, rigGroup)
        if Nodes.getSide(self.parentNode):
            for childNode in Nodes.getChildren(rigGroup):
                if Nodes.getSide(childNode) == Settings.leftSide:
                    Tools.parentScaleConstraint(Nodes.replaceSide(self.parentNode, Settings.leftSide), childNode)
                if Nodes.getSide(childNode) == Settings.rightSide:
                    Tools.parentScaleConstraint(Nodes.replaceSide(self.parentNode, Settings.rightSide), childNode)

        VisSwitch.connectVisSwitchGroup(rigNodeList, rigGroup, displayAttr='setupDisplay')
        VisSwitch.connectVisSwitchGroup(jointNodeList+eyeballJointList+allLashJoints, rigGroup, displayAttr='jointDisplay')
        VisSwitch.connectVisSwitchGroup([x['control'] for x in [controlRigSet[0][0][z] for z in range(2)]], rigGroup, displayAttr='ballControlDisplay')
        VisSwitch.connectVisSwitchGroup([x['control'] for x in [eyetargetControlNodesList[z] for z in range(2)]], rigGroup, displayAttr='targetControlDisplay')
        VisSwitch.connectVisSwitchGroup([mainTargetRig['control']], rigGroup, displayAttr='targetControlDisplay')
        for lidRigs in lidRigsList:
            for lidRig in lidRigs:
                for visAttr in ['setupDisplay', 'jointDisplay']:
                    mc.connectAttr('%s.%s'%(rigGroup, visAttr), '%s.%s'%(lidRig['rigGroup'], visAttr))
        if self.hasEyelids:
            [VisSwitch.connectVisSwitchGroup([x['control'] for x in allEyelidControlNodesList[z]], rigGroup, displayAttr='lidsControlDisplay') for z in range(2)]
        if self.hasOuterLine:
            VisSwitch.connectVisSwitchGroup([x['control'] for x in allOuterControlNodesList], rigGroup, displayAttr='outerlidsControlDisplay')
            
        self.cleanup(Nodes.replaceNodeType(rigGroup, 'guide'), trashGuides=True, removeRightGuides=True, hierarchy=False, display=False, selectionSets=False)

        # turning cycle check back on
        mc.cycleCheck(e=True)
            
        return {
            'rigGroup': rigGroup, 
            'joints': jointNodeList,
            'leftUpperCurveJoints': lidRigsList[0][0]['joints'][1:-1],
            'leftLowerCurveJoints': lidRigsList[0][1]['joints'][1:-1],
            'rightUpperCurveJoints': lidRigsList[1][0]['joints'][1:-1],
            'rightLowerCurveJoints': lidRigsList[1][1]['joints'][1:-1],
            'leftOuterInnerJoints': outerInnerJointList[0],
            'rightOuterInnerJoints': outerInnerJointList[1],
            'eyeballJoints': eyeballJointList,
            'mainTargetControl': mainTargetRig['control'],
            'mainTargetOffset': mainTargetRig['offset'],
            'leftLidControls': [x['control'] for x in allEyelidControlNodesList[0]] if allEyelidControlNodesList else [],
            'rightLidControls': [x['control'] for x in allEyelidControlNodesList[1]] if allEyelidControlNodesList else [],
            'outerLidControls': [x['control'] for x in allOuterControlNodesList] if allOuterControlNodesList else [],
            }