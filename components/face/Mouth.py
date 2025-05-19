# Mouth

import maya.cmds as mc
import itertools

from bear.system import Generic
from bear.system import Guiding
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import VisSwitch
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.utilities import AttrConnect
from bear.components.basic import Curve
from bear.components.basic import Control
from bear.components.basic import Guide
if Settings.licenseVersion == 'full':
    from bear.utilities import Squash

class Build(Generic.Build):

    def __init__(self,
                name='mouth',
                upperLipJointCount=15,
                lowerLipJointCount=15,
                wrinkleJointCount=12,
                parentNode=Nodes.createName('head', nodeType=Settings.controlSuffix)[0],
                headJointNode=Nodes.createName('head', nodeType=Settings.skinJointSuffix)[0],
                #lipSqueezing=False,
                hasAnchorRig='unsupported' if Settings.licenseVersion == 'free' else True,
                anchorUpAxis='X',
                anchorUpAxisCorner='X',
                hasSurfaceRig='unsupported' if Settings.licenseVersion == 'free' else True,
                hasLipsRig=True,
                hasNoRollJoints=False,
                hasWrinkleRig=True,
                hasJointGuides=False,
                #hasStickyLips='unsupported' if Settings.licenseVersion == 'free' else True,
                input_noseName='nose',
                input_cheeksName='cheeks',
                displaySwitch='faceDisplaySwitch',
                *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)
        
        self.name = name
        self.upperLipJointCount = upperLipJointCount
        self.lowerLipJointCount = lowerLipJointCount
        self.wrinkleJointCount = wrinkleJointCount
        self.hasNoRollJoints = hasNoRollJoints
        self.hasLipsRig = upperLipJointCount != 0 and lowerLipJointCount != 0 and hasLipsRig
        self.hasWrinkleRig = wrinkleJointCount != 0 and hasWrinkleRig
        self.wrinkleJointCount = wrinkleJointCount
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.headJointNode = headJointNode
        self.lipSqueezing = False
        self.hasAnchorRig = hasAnchorRig
        self.anchorUpAxis = anchorUpAxis
        self.anchorUpAxisCorner = anchorUpAxisCorner
        self.hasSurfaceRig = hasSurfaceRig
        self.hasJointGuides = hasJointGuides
        self.hasStickyLips = False
        #self.hasStickyLips = hasStickyLips if upperLipJointCount > 0 and lowerLipJointCount > 0 and hasLipsRig else False
        self.input_noseName = input_noseName
        self.input_cheeksName = input_cheeksName
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, 'auto', definition)
        if definition:
            return {'guideGroup': guideGroup}

        if self.hasAnchorRig == True:
            outerGroup = AddNode.emptyNode(component=self.name, element='outer', nodeType=Settings.guidePivotSuffix)

        upperLowerLipElements = list()
        lipSides = list()
        for lip in ['upperlip', 'lowerlip']:
            upperLowerLipElements.append([lip+'corner', 
                                            lip+'out', 
                                            lip+'mid', 
                                            lip+'in', 
                                            lip+'in', 
                                            lip+'mid', 
                                            lip+'out', 
                                            lip+'corner'])
            lipSides.append([Settings.rightSide,
                            Settings.rightSide,
                            Settings.rightSide,
                            Settings.rightSide,
                            Settings.leftSide,
                            Settings.leftSide,
                            Settings.leftSide,
                            Settings.leftSide])

        mouthGuideList = list()
        guideCollection = list()

        if self.hasAnchorRig == True:
            mc.parent(outerGroup, guideGroup)
        
        for m, mouthName in enumerate(['jaw', 'main', 'jawTip', 'upperlip', 'lowerlip']):
            if not self.hasLipsRig and m > 0 and m != 2:
                continue

            mouthGuide = Guide.createGuide(component=self.name, element=mouthName)
            mouthGuideList.append(mouthGuide)

            mc.move(0, [6, 6, 6, 7, 5][m], [-12, -6, 0, 0, 0][m], mouthGuide['pivot'])
            if m == 4:
                mc.rotate(0, 0, 180, mouthGuide['pivot'], r=True, os=True)

            mc.parent(mouthGuide['pivot'], guideGroup)

        cornerGuideList = list()

        if self.hasLipsRig:
            for side in [Settings.leftSide, Settings.rightSide]:
                cornerGuide = Guide.createGuide(component=self.name,
                                                    element='lipcorner',
                                                    side=side,
                                                    size=1,
                                                    hasGuideShape=True if side == Settings.leftSide else False)
                mc.parent(cornerGuide['pivot'], guideGroup)
                cornerGuideList.append(cornerGuide)

            if self.hasAnchorRig == True:
                cornerOuterGuide = Guide.createGuide(component=self.name, 
                                                        side=Settings.leftSide, 
                                                        element='lipcornerOuter', 
                                                        hasGuideShape=False)['pivot']
                mc.addAttr(cornerOuterGuide, dt='string', ln='parentNode')
                mc.setAttr(f'{cornerOuterGuide}.parentNode', 'None', type='string')
                mc.move(9, 6, 0, cornerOuterGuide)
                mc.rotate(0, 0, -90, cornerOuterGuide)
                mc.parent(cornerOuterGuide, outerGroup)

            for p, lipElements in enumerate(upperLowerLipElements):

                guideCollection.append([])

                for n, lipElement in enumerate(lipElements):

                    guide = Guide.createGuide(component=self.name,
                                                side=lipSides[p][n],
                                                element=lipElement,
                                                size=1,
                                                hasGuideShape=lipSides[p][n] == Settings.leftSide)
                    
                    if n == 0 or n == 7:
                        mc.parent(guide['pivot'], cornerGuideList[1 if n == 0 else 0]['pivot'])
                        Nodes.lockAndHideAttributes(guide['pivot'], t=[True, True, True], r=[True, True, True], s=[True, True, True])
                        mc.hide(guide['pivot'])
                    else:
                        mc.parent(guide['pivot'], guideGroup)
                        if self.hasAnchorRig == True:
                            if Nodes.getSide(guide['pivot']) == Settings.leftSide:
                                outerGuide = Guide.createGuide(node=guide['pivot'],
                                                                element=lipElement+'Outer', 
                                                                hasGuideShape=False)['pivot']
                                mc.addAttr(outerGuide, dt='string', ln='parentNode')
                                mc.setAttr(f'{outerGuide}.parentNode', 'None', type='string')
                                if lipElement == 'upperlipin' and Nodes.getSide(guide['pivot']) == Settings.leftSide:
                                    position = (1, 4, 0)
                                    rotationZ = 0
                                if lipElement == 'upperlipmid' and Nodes.getSide(guide['pivot']) == Settings.leftSide:
                                    position = (4, 4, 0)
                                    rotationZ = 0
                                if lipElement == 'upperlipout' and Nodes.getSide(guide['pivot']) == Settings.leftSide:
                                    position = (7, 3, 0)
                                    rotationZ = -45
                                if lipElement == 'lowerlipin' and Nodes.getSide(guide['pivot']) == Settings.leftSide:
                                    position = (1, -4, 0)
                                    rotationZ = -180
                                if lipElement == 'lowerlipmid' and Nodes.getSide(guide['pivot']) == Settings.leftSide:
                                    position = (4, -4, 0)
                                    rotationZ = -180
                                if lipElement == 'lowerlipout' and Nodes.getSide(guide['pivot']) == Settings.leftSide:
                                    position = (7, -3, 0)
                                    rotationZ = -135
                                mc.move(position[0], position[1], position[2], outerGuide)
                                mc.rotate(0, 0, rotationZ, outerGuide)
                                mc.parent(outerGuide, outerGroup)

                    guideCollection[-1].append(guide)
                
            # lips curve

            lipPointLocCtrlCol = list()

            for i, lip in enumerate(['upperlip', 'lowerlip']):
                jointCount = [self.upperLipJointCount, self.lowerLipJointCount][i]
                if jointCount == 0:
                    continue
                lipCurveGuide = Curve.Build(component=self.name,
                                            element=lip, 
                                            controlCount=8, 
                                            size=1,
                                            jointCount=jointCount,
                                            segmenting=True,
                                            hasJointGuides=self.hasJointGuides,
                                            alignAxis='Y',
                                            upAxis='Z',
                                            curveType='nurbsCurve').createGuide(definition)
                mc.parent(lipCurveGuide['guideGroup'], guideGroup)

                lipPointLocCtrlCol.append(lipCurveGuide['guideControls'])

                for p, curvePivotGuide in enumerate(lipCurveGuide['guidePivots']):
                    Nodes.alignObject(curvePivotGuide, guideCollection[i][p]['pivot'])
                    mc.parent(curvePivotGuide, guideCollection[i][p]['pivot'])
                    if p != 0 and p != len(lipCurveGuide['guidePivots'])-1:
                        mc.parent(guideCollection[i][p]['pivot'], lipCurveGuide['controlGroup'])

                for g, guide in enumerate(guideCollection[i]):

                    yPos = [1, -1][i]
                    positions = [(7, 0, 0), 
                                    (5, yPos, 0), 
                                    (3, yPos, 0), 
                                    (1, yPos, 0), 
                                    (1, yPos, 0), 
                                    (3, yPos, 0), 
                                    (5, yPos, 0), 
                                    (7, 0, 0)]
                    if lip == 'upperlip':
                        rotations = [(0, 0, 180),
                                        (0, 0, 180),
                                        (0, 0, 180),
                                        (0, 0, 180),
                                        (0, 0, 0),
                                        (0, 0, 0),
                                        (0, 0, 0),
                                        (0, 0, 0)]
                    else:
                        rotations = [(0, 0, 180),
                                        (0, 0, 0),
                                        (0, 0, 0),
                                        (0, 0, 0),
                                        (0, 0, 180),
                                        (0, 0, 180),
                                        (0, 0, 180),
                                        (0, 0, 0)]
                    mc.move(positions[g][0], positions[g][1], positions[g][2], guide['pivot'])
                    mc.rotate(rotations[g][0], rotations[g][1], rotations[g][2], guide['pivot'])
                    
                    if g != 0 and g != 7:
                        if Nodes.getSide(guide['pivot']) == Settings.rightSide:
                            autoMirrorNode = AddNode.parentNode(guide['pivot'], nodeType='autoMirror')
                            Nodes.setOffsetParentMatrix(autoMirrorNode, -1)
                            if lip == 'lowerlip':
                                mc.rotate(0, 0, 180, autoMirrorNode)
                    if g > 0 and g < 4:
                        mc.connectAttr('%s.translate'%guideCollection[i][[6, 5, 4][g-1]]['pivot'], '%s.translate'%autoMirrorNode)
                        mc.connectAttr('%s.rotate'%guideCollection[i][[6, 5, 4][g-1]]['pivot'], '%s.rotate'%autoMirrorNode)
                
                for lipGuidePivot in lipCurveGuide['guidePivots']:
                    Nodes.lockAndHideAttributes(lipGuidePivot, t=[True, True, True], r=[True, True, True], s=[True, True, True])
                mc.hide(lipCurveGuide['guidePivots'])
                
            for c, cornerGuide in enumerate(cornerGuideList):

                mc.move([positions[-1], positions[0]][c][0], 
                        [positions[-1], positions[0]][c][1], 
                        [positions[-1], positions[0]][c][2], cornerGuide['pivot'])
                mc.rotate([rotations[-1], rotations[0]][c][0], 
                            [rotations[-1], rotations[0]][c][1], 
                            [rotations[-1], rotations[0]][c][2], cornerGuide['pivot'])
                
                if Nodes.getSide(cornerGuide['pivot']) == Settings.rightSide:
                    autoMirrorNode = AddNode.parentNode(cornerGuide['pivot'], nodeType='autoMirror')
                    Nodes.setOffsetParentMatrix(autoMirrorNode, -1)
                    mc.connectAttr('%s.translate'%cornerGuideList[0]['pivot'], '%s.translate'%autoMirrorNode)
                    mc.connectAttr('%s.rotate'%cornerGuideList[0]['pivot'], '%s.rotate'%autoMirrorNode)
        
        # wrinkle curve
        
        if self.hasWrinkleRig and self.hasLipsRig:
            wrinkleCurveGuide = Curve.Build(component=self.name,
                                                side=Settings.leftSide,
                                                element='wrinkle', 
                                                curveType='bezierCurve',
                                                size=1,
                                                jointCount=self.wrinkleJointCount,
                                                controlCount=3, 
                                                segmenting=True,
                                                hasJointGuides=self.hasJointGuides,
                                                alignAxis='-Y',
                                                upAxis='Z').createGuide(definition)
            mc.parent(wrinkleCurveGuide['guideGroup'], guideGroup)
            for w, wrinklePivot in enumerate(wrinkleCurveGuide['guidePivots']):
                positions = [(4, 5, 0),
                                (9, 0, 0), 
                                (4, -5, 0)]
                mc.move(positions[w][0], positions[w][1], positions[w][2], wrinklePivot, os=True, r=False)
                mc.rotate(0, 0, [0, 0, 0, -90, 0, 0, -180][w], wrinklePivot, os=True, r=False)
            for b, wrinkleBezierPivot in enumerate(wrinkleCurveGuide['guideBezierPivots']):
                positions = [(2, 0, 0),
                                (0, 2, 0), 
                                (0, -2, 0), 
                                (2, 0, 0)]
                mc.setAttr('%s.tx'%wrinkleBezierPivot, positions[b][0])
                mc.setAttr('%s.ty'%wrinkleBezierPivot, positions[b][1])
                mc.setAttr('%s.tz'%wrinkleBezierPivot, positions[b][2])

        # surface guide
        if self.hasSurfaceRig == True and self.hasLipsRig:
            
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
            mc.move(7, 0, 0, surfaceGuide[0])
            mc.rotate(0, -90, 0, '%s.cv[0:*][0:*]'%surfaceGuide[0])
            scaleValue = 10
            mc.scale(scaleValue, scaleValue, scaleValue, '%s.cv[0:*][0:*]'%surfaceGuide[0])

        # blendshape guiding

        jaw = mouthGuideList[0]['control']
        
        if self.hasLipsRig:
            mouthcorner = cornerGuideList[0]['control']
            Nodes.addAttrTitle(mouthcorner, 'blendShape')

        if self.hasWrinkleRig:
            Nodes.addAttrTitle(wrinkleCurveGuide['guideControls'][0], 'blendShape')

        Nodes.addAttrTitle(jaw, 'blendShape')

        if self.hasLipsRig:
            for node in [mouthcorner]:

                attrName = ['bsh_puffout_pos', 'bsh_puffout_neg']
                for d in range(len(attrName)):
                    mc.addAttr(node, at='float', ln=attrName[d], k=True, dv=1)

            for jawState in ['jawClose', 'jawOpen']:

                attrNames = ['translateX_pos', 'translateX_neg', 'translateY_pos', 'translateY_neg']
                defaultVal = [8, 3, 4, 4]
                for a, attrName in enumerate(attrNames):
                    mc.addAttr(mouthcorner, at='float', ln='bsh_' + jawState + '_' + attrName, k=True, dv=defaultVal[a])

                attrNames = ['translateX_pos_translateY_pos', 'translateX_neg_translateY_pos', 'translateX_pos_translateY_neg', 'translateX_neg_translateY_neg']
                [mc.addAttr(mouthcorner, at='float', ln='bsh_' + jawState + '_combine_' + attrName, k=True, dv=0) for attrName in attrNames]

            attrName = ['bsh_rotateX_pos']
            for d in range(len(attrName)):
                mc.addAttr(jaw, at='float', ln=attrName[d], k=True, dv=[30, 0][d])

            for c, count in enumerate([self.upperLipJointCount, self.lowerLipJointCount]):
                [ConnectionHandling.addOutput(guideGroup, Nodes.createName(self.name, side, Settings.skinJointSuffix, ['upperlip', 'lowerlip'][c], n)[0]) for n in range(count)]
            if self.hasWrinkleRig:
                for side in [Settings.leftSide, Settings.rightSide]:
                    [ConnectionHandling.addOutput(guideGroup, Nodes.createName(self.name, side, Settings.skinJointSuffix, 'wrinkle', n)[0]) for n in range(self.wrinkleJointCount)]

        return {'guideGroup': guideGroup}

    def createRig(self):

        guideGroup = Nodes.createName(self.name, nodeType=Settings.guideGroup)[0]

        jawGuide=Nodes.createName(self.name, nodeType=Settings.guidePivotSuffix, element='jaw')[0]
        jawTipGuide=Nodes.createName(self.name, nodeType=Settings.guidePivotSuffix, element='jawTip')[0]
        mouthMainPivotGuide=Nodes.createName(self.name, nodeType=Settings.guidePivotSuffix, element='main')[0]
        upperlipPivotGuide=Nodes.createName(self.name, nodeType=Settings.guidePivotSuffix, element='upperlip')[0]
        lowerlipPivotGuide=Nodes.createName(self.name, nodeType=Settings.guidePivotSuffix, element='lowerlip')[0]
        upperlipinGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='upperlipin')[0]
        upperlipmidGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='upperlipmid')[0]
        upperlipoutGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='upperlipout')[0]
        lipcornerGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='lipcorner')[0]
        lowerlipoutGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='lowerlipout')[0]
        lowerlipmidGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='lowerlipmid')[0]
        lowerlipinGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='lowerlipin')[0]
        upperlipCurveGuide=Nodes.createName(self.name, nodeType=Settings.guideCurveSuffix, element='upperlip')[0]
        lowerlipCurveGuide=Nodes.createName(self.name, nodeType=Settings.guideCurveSuffix, element='lowerlip')[0]
        upperlipinOuterGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='upperlipinOuter')[0]
        upperlipmidOuterGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='upperlipmidOuter')[0]
        upperlipoutOuterGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='upperlipoutOuter')[0]
        lipcornerOuterGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='lipcornerOuter')[0]
        lowerlipoutOuterGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='lowerlipoutOuter')[0]
        lowerlipmidOuterGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='lowerlipmidOuter')[0]
        lowerlipinOuterGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guidePivotSuffix, element='lowerlipinOuter')[0]
        wrinkleCurveGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guideCurveSuffix, element='wrinkle')[0]
        surfaceGuide=Nodes.createName(self.name, Settings.leftSide, nodeType=Settings.guideSurfaceSuffix, element='surfaceNode')[0]

        self.upperLipJointCount = Guiding.getBuildAttrs(guideGroup, 'upperLipJointCount')
        self.lowerLipJointCount = Guiding.getBuildAttrs(guideGroup, 'lowerLipJointCount')
        self.wrinkleJointCount = Guiding.getBuildAttrs(guideGroup, 'wrinkleJointCount')
        self.hasAnchorRig = Guiding.getBuildAttrs(guideGroup, 'hasAnchorRig')

        self.parentNode = ConnectionHandling.inputExists(self.parentNode)
        self.headJointNode = ConnectionHandling.inputExists(self.headJointNode)
        
        rigGroup = super(Build, self).createRig(self.name, 'auto')
        if self.hasLipsRig:
            controlGroup = AddNode.compNode(self.name, element='controls', nodeType=Settings.rigGroup, hasGlobalScale=False)
            mc.parent(controlGroup, rigGroup)
            Tools.parentScaleConstraint(self.parentNode, controlGroup)

        pinGroup = AddNode.compNode(self.name, nodeType='pin', hasGlobalScale=False)
        mc.parent(pinGroup, rigGroup)
        Tools.parentScaleConstraint(self.parentNode, pinGroup)
        
        lipGuideList = [upperlipinGuide, upperlipmidGuide, upperlipoutGuide, lipcornerGuide, lowerlipoutGuide, lowerlipmidGuide, lowerlipinGuide]

        locList = list()
        locOffList = list()

        if self.hasLipsRig:
            for n, locName in enumerate(['head', 'cheeks', 'jaw']):

                loc = AddNode.emptyNode(component=self.name,
                                        element=locName,
                                        nodeType=Settings.locNodeSuffix,
                                        objType='locator')
                locOff = AddNode.parentNode(loc, nodeType='locOff')
                Nodes.alignObject(locOff, mouthMainPivotGuide)
                mc.parent(locOff, pinGroup)
                locList.append(loc)
                locOffList.append(locOff)

            headLoc, cheeksLoc, jawLoc = locList
            headLocOff, cheeksLocOff, jawLocOff = locOffList
            Tools.parentScaleConstraint(self.parentNode, cheeksLocOff)

            radius = Tools.getDistance(lowerlipinGuide, jawGuide)

        jointNodeList = list()
        upperLipJoints = list()
        lowerLipJoints = list()

        jawRig = Control.createControl(node=jawGuide)

        if self.hasLipsRig:
            mc.parent(jawLocOff, jawRig['control'])
        mc.parent(jawRig['offset'], pinGroup)
        jawJointNode = AddNode.jointNode(jawRig['control'], 
                                        size=0.1, 
                                        nodeType=Settings.skinJointSuffix,
                                        skeletonParent=self.parentNode)
        jointNodeList.append(jawJointNode)

        # jaw aim control
        jawTipRig = Control.createControl(node=jawTipGuide,
                                        lockAndHide=[[False, False, True], [True, True, False], [True, True, True]],)
        mc.parent(jawTipRig['offset'], pinGroup)
        jawTipNode = AddNode.parentNode(jawRig['control'], 'aim')
        aimCnt = Nodes.aimConstraint(jawTipRig['control'], 
                                        jawTipNode,
                                        upNode=jawRig['offset'],
                                        aimAxis='z',
                                        upAxis='x',
                                        upType='objectrotation',
                                        mo=True)

        # rotate capture to get jaw rotation independant of control
        rotCapNode = AddNode.childNode(jawRig['offset'], 'rotationCapture')
        Nodes.orientConstraint(jawRig['control'], rotCapNode)

        shiftNode = AddNode.inbetweenNode(jawRig['offset'], 'shift')
        shiftTipNode = AddNode.inbetweenNode(jawTipRig['offset'], 'shift')
        pullOutAttr = jawTipRig['control']+'.pullOut'
        shiftAttr = jawTipRig['control']+'.shift'
        autoShiftAttr = jawTipRig['control']+'.autoShift'
        autoShiftRotateAttr = jawTipRig['control']+'.autoShiftRotate'
        jawDownPullInAttr = jawTipRig['control']+'.jawDownPullIn'
        jawDownPullVertAttr = jawTipRig['control']+'.jawDownPullVert'
        Nodes.addAttrTitle(jawTipRig['control'], 'shiftAttributes')
        Nodes.addAttr(pullOutAttr)
        Nodes.addAttr(shiftAttr)
        Nodes.addAttr(autoShiftAttr, dv=0.5, d=True, k=False)
        Nodes.addAttr(autoShiftRotateAttr, dv=3, d=True, k=False)
        Nodes.addAttr(jawDownPullInAttr, d=True, k=False)
        Nodes.addAttr(jawDownPullVertAttr, d=True, k=False)
        mulNode = Nodes.mulNode('%s.tx'%jawTipRig['control'],
                                autoShiftAttr)
        resNode = Nodes.addNode('%s.output'%mulNode,
                                shiftAttr)
        mc.connectAttr('%s.output'%resNode, '%s.tx'%shiftNode)
        mc.connectAttr(shiftAttr, '%s.tx'%shiftTipNode)
        
        mulRotateNode = Nodes.mulNode('%s.tx'%jawTipRig['control'],
                                autoShiftRotateAttr)
        Nodes.addNode('%s.output'%mulRotateNode,
                                '%s.rz'%jawTipRig['control'],
                                '%s.offsetZ'%aimCnt)
        mc.connectAttr(pullOutAttr, '%s.tz'%shiftNode)
        
        jawDownPullNode = AddNode.inbetweenNode(jawRig['control'], 'jawDownPullIn')
        jawDownPullInClamp = Nodes.clampNode('%s.rx'%rotCapNode,
                                             clampMin=0)
        jawMulNode = Nodes.mulNode('%s.outputR'%jawDownPullInClamp,
                                         -0.02)
        Nodes.mulNode('%s.output'%jawMulNode,
                                         jawDownPullInAttr, 
                                        '%s.tz'%jawDownPullNode)
        
        jawDownPullVertClamp = Nodes.clampNode('%s.rx'%rotCapNode,
                                             clampMin=0)
        mulNode = Nodes.mulNode('%s.outputR'%jawDownPullVertClamp,
                                         -0.02)
        Nodes.mulNode('%s.output'%mulNode,
                                         jawDownPullVertAttr, 
                                        '%s.ty'%jawDownPullNode)
        
        def createStickyLips(stickyLipsNode, side, s):
            
            if not stickyLipsNode:
                return
            
            ctlNode = Nodes.replaceNodeType(stickyLipsNode, Settings.controlSuffix)

            lip = 'upperlip' if 'upperlip' in Nodes.getElement(ctlNode) else 'lowerlip'
            stickyLipsAttrName = 'stickyLipsLeft' if side == Settings.leftSide else 'stickyLipsRight'

            sclCmpNode = Nodes.replaceNodeType(stickyLipsNode, Settings.scaleCompensateNode)
            stickyCtlNode = Nodes.replaceToken(ctlNode, Nodes.getElement(ctlNode)+'Sticky', 'element')
            stickyOffNode = Nodes.replaceNodeType(stickyCtlNode, Settings.offNodeSuffix)
            clsHandleNode = Nodes.getChildren(stickyCtlNode)[0]
            stickyParentNode = Nodes.getParent(stickyCtlNode)
            elementSectionName = Nodes.getElement(ctlNode).replace(lip, '')
            upperlipCtlNode = Nodes.replaceToken(ctlNode, 'upperlip'+elementSectionName, 'element')
            lowerlipCtlNode = Nodes.replaceToken(ctlNode, 'lowerlip'+elementSectionName, 'element')
                                
            Nodes.setParent(stickyOffNode, ctlNode, lockScale=True, lockRotate=True)
            Nodes.setParent(sclCmpNode, stickyCtlNode)
            stickyActivateNode = AddNode.parentNode(sclCmpNode, 'stickyActivate', lockScale=True)
            Nodes.setParent(clsHandleNode, sclCmpNode, lockScale=True, lockRotate=False)
            for axis in 'xyz':
                mc.setAttr('%s.r%s'%(clsHandleNode, axis), 0)

            stickyLipsDriven = AddNode.parentNode(stickyCtlNode, nodeType='stickyDriven', lockScale=True)
            for axis in 'xyz':
                mc.setAttr('%s.s%s'%(stickyCtlNode, axis), lock=False)

            if side == Settings.rightSide:
                mc.setAttr('%s.rx'%(clsHandleNode), 180)
                mc.setAttr('%s.ry'%(clsHandleNode), 0)
                mc.setAttr('%s.rz'%(clsHandleNode), 0)
            
            Tools.blendBetween([upperlipCtlNode], 
                                [lowerlipCtlNode], 
                                [stickyLipsNode], 
                                attrNode=stickyLipsNode, 
                                attrName='stickyHeight', 
                                attrTitle='mouth',
                                parentConstrained=False, 
                                scaleConstrained=False, 
                                pointConstrained=True, 
                                maintainOffset=False, 
                                defaultValue=0.5)

            stickyConNode = AddNode.childNode(stickyLipsNode, lip.replace('lip', ''), lockScale=True)
            Nodes.alignObject(stickyConNode, ctlNode)
            for axis in 'xyz':
                mc.setAttr('%s.r%s'%(stickyConNode, axis), 0)

            mc.addAttr(stickyLipsNode, ln=stickyLipsAttrName, at='float')
            mc.addAttr(stickyLipsNode, ln='stickyness', at='float')
            
            n = s
            if s > 2:
                n = 6-s
            n = -1*(2-n)

            # non-sticky
            stickynessNegate = Nodes.addNode(stickyLipsNode+'.'+'stickyness',
                                    -1)
            stickynessRevert = Nodes.mulNode('%s.output'%stickynessNegate,
                                    -1)

            nonSticky = Nodes.mulNode(stickyLipsNode+'.'+stickyLipsAttrName,
                                    '%s.output'%stickynessRevert)

            # sticky
            mulNode = Nodes.mulNode(stickyLipsNode+'.'+stickyLipsAttrName,
                                    3)
            stickyOffsetNode = Nodes.mulNode(stickyLipsNode+'.'+'stickyness',
                                    n)

            stickynessNode = Nodes.addNode('%s.output'%mulNode,
                                    '%s.output'%stickyOffsetNode)

            stickynessActivate = Nodes.mulNode(stickyLipsNode+'.'+'stickyness',
                                    '%s.output'%stickynessNode)

            clampNode = Nodes.clampNode('%s.output'%stickynessActivate,
                                    0, 
                                    1)

            # combine
            resNode = Nodes.addNode('%s.outputR'%clampNode,
                                    '%s.output'%nonSticky)
                
            Tools.blendBetween([stickyParentNode], 
                                [stickyConNode], 
                                [stickyLipsDriven], 
                                attrNode=resNode, 
                                attrName='output', 
                                attrTitle='mouth',
                                parentConstrained=True, 
                                scaleConstrained=False, 
                                positionConstrained=False, 
                                maintainOffset=False, 
                                defaultValue=0)
            
            Tools.blendBetween([stickyLipsDriven], 
                                [stickyCtlNode], 
                                [stickyActivateNode], 
                                attrNode=stickyLipsNode, 
                                attrName=stickyLipsAttrName, 
                                attrTitle='mouth',
                                parentConstrained=True, 
                                scaleConstrained=False, 
                                positionConstrained=False, 
                                maintainOffset=False, 
                                defaultValue=0)

            visAttr = stickyOffNode+'.visibility'
            visDrv = resNode+'.output'
            mc.setDrivenKeyframe(visAttr, cd=visDrv, dv=0, v=1, itt='linear', ott='linear')
            mc.setDrivenKeyframe(visAttr, cd=visDrv, dv=1, v=0, itt='linear', ott='linear')
            mc.setDrivenKeyframe(visAttr, cd=visDrv, dv=1, v=1, itt='linear', ott='linear')
            mc.setDrivenKeyframe(visAttr, cd=visDrv, dv=0, v=0, itt='linear', ott='linear')
        
        stickyLipsNodesSideSet = list()

        upperlowerlipNodesList = list()
        lipNodesCol = list()

        upperlowerlipGuideList = list()

        upperlowerlipTiltNodesList = list()
        lipTiltRigs = list()

        # center lip controls

        if self.hasLipsRig:
            upperlowerlipGuideList = [upperlipPivotGuide, lowerlipPivotGuide]
        
        upperLowerLipOffsets = list()
        
        if self.hasLipsRig:
            for n, node in enumerate(upperlowerlipGuideList):

                guideNode = [upperlipinGuide, lowerlipinGuide][n]

                size = Nodes.getSize(Nodes.replaceNodeType(guideNode, Settings.guideShapeSuffix))[0]
                offset = Guiding.getGuideAttr(guideNode)['offset']
                color = Guiding.getGuideAttr(guideNode)['color']

                lipPosOffset = [offset[0][0], offset[0][1], offset[0][2]+(size*0.5)]
                lipRotOffset = [-90, 0, 0] # hard coding to be independent on lip control orientations
                lipSclOffset = [offset[2][0], offset[2][1], offset[2][2]]

                upperLowerLipOffsets.append([lipPosOffset, lipRotOffset, lipSclOffset])

                name = ['upperlip', 'lowerlip'][n]

                lipMainRig = Control.createControl(node=node)

                lipTiltRig = Control.createControl(node=node,
                                                component=self.name,
                                                element=name,
                                                specific='tilt',
                                                size=size,
                                                offset=[[0, 0, 0], [0, 0, 90], [lipSclOffset[0]*5, lipSclOffset[1]*5, lipSclOffset[2]*5]],
                                                shape='Circle',
                                                color=color,
                                                useGuideAttr=False,
                                                deleteNode=False)
                if n == 1:
                    mc.rotate(180, 0, 0, lipTiltRig['offset'], r=True, os=True)
                
                Nodes.lockAndHideAttributes(lipTiltRig['control'], t=[True, True, True], r=[False, True, True], s=[True, False, False])
                tiltNeighbor1Attr = lipTiltRig['control']+'.neighbor1Influence'
                tiltNeighbor2Attr = lipTiltRig['control']+'.neighbor2Influence'
                tiltNeighbor3Attr = lipTiltRig['control']+'.neighbor3Influence'
                Nodes.addAttr(tiltNeighbor1Attr, minVal=0, maxVal=1, d=True, k=False, dv=1)
                Nodes.addAttr(tiltNeighbor2Attr, minVal=0, maxVal=1, d=True, k=False, dv=0.5)
                Nodes.addAttr(tiltNeighbor3Attr, minVal=0, maxVal=1, d=True, k=False, dv=0)
                lipTiltRigs.append(lipTiltRig)

                Tools.parentScaleConstraint(headLoc if n == 0 else jawLoc, lipMainRig['offset'])
                mc.parent(lipMainRig['offset'], controlGroup)
                if lipTiltRig:
                    mc.parent(lipTiltRig['offset'], controlGroup)

                upperlowerlipNodesList.append(lipMainRig)
                upperlowerlipTiltNodesList.append(lipTiltRig)

            else:
                lipTiltRig = None

        if self.hasLipsRig:

            # sticky lips distance
            upperDistTracker = AddNode.childNode(upperlowerlipNodesList[0]['control'], 'distanceTracker')
            lowerDistTracker = AddNode.childNode(upperlowerlipNodesList[1]['control'], 'distanceTracker')
            Nodes.alignObject(upperDistTracker, lowerDistTracker)
            Nodes.setParent(upperDistTracker, controlGroup)
            Nodes.setParent(lowerDistTracker, upperDistTracker)
            mc.pointConstraint(upperlowerlipNodesList[0]['control'], upperDistTracker, mo=True)
            lowerDistTrackerParentCnt = mc.pointConstraint(upperlowerlipNodesList[1]['control'], lowerDistTracker)[0]
            mc.transformLimits(lowerDistTracker, ty=(0, 0), ety=(1, 0))
            
            lipsRigGroups = list()
            wrinkleControls = list()
            surfaceNodeList = list()
            outerMouthRigGroupList = list()
            allConstraintNodes = list()
            
            # lip controls creation

            parentsSide = []
            allTargetNodesSide = []
            for side in [Settings.leftSide, Settings.rightSide]:

                nodeList = [Guiding.convertGuide(lipGuide, mirror=True, mirrorRotate=(0, 0, 0))[0] if side == Settings.rightSide else lipGuide for lipGuide in lipGuideList]

                sideNodesList = []
                cntNodeList = []
                stickyLipsNodesList = []
                mouthRigs = []
                parents = []
                allTargetNodes = []

                parentsSide.append(parents)
                allTargetNodesSide.append(allTargetNodes)

                for n, node in enumerate(nodeList):
                    
                    mouthRig = Control.createControl(node=node, side=side)
                    
                    mouthRigs.append(mouthRig)
                    sideNodesList.append(mouthRig)

                    cntNode = AddNode.parentNode(mouthRig['control'], nodeType=Settings.cntNodeSuffix, lockScale=True)
                    cntNodeList.append(cntNode)
                    if n == 3:
                        stickyLipsNode = cntNode
                    else:
                        stickyLipsNode = AddNode.childNode(cntNode, nodeType='stickyLips', lockScale=True)
                    stickyLipsNodesList.append(stickyLipsNode)
                    # no skin joints created for curve controls
                    if n == 3:
                        jointNode = AddNode.jointNode(mouthRig['control'], 
                                                        size=0.1, 
                                                        nodeType=Settings.skinJointSuffix,
                                                        skeletonParent=self.parentNode)
                        jointNodeList.append(jointNode)
            
                    Tools.resetTransforms(mouthRig['control'], translate=False, rotate=False, scale=True)
                    if side == Settings.rightSide:
                        Nodes.setTrs(node)
                        
                stickyLipsNodesSideSet.append(stickyLipsNodesList)

                drvNode = AddNode.inbetweenNode(stickyLipsNodesSideSet[0 if side == Settings.leftSide else 1][3], nodeType='inwardDrv', lockScale=True)
                
                for n, mouthRig in enumerate(sideNodesList):

                    if n == 3:
                        firstNode = headLoc
                        secNode = jawLoc
                        attrName = 'jawInfluence'
                    else:
                        lipControlNode = upperlowerlipNodesList[0 if (n >= 0 and n <= 2) else 1]['control']
                        lipGuideNode = Nodes.createName(sourceNode=cntNodeList[n], side=Settings.leftSide, nodeType=Settings.guideShapeSuffix)[0]
                        lipParentNode = Nodes.getAttr('%s.parentNode'%lipGuideNode)
                        if lipParentNode != 'None' and lipParentNode != '':
                            firstNode = lipParentNode
                        else:
                            firstNode = lipControlNode
                        secNode = sideNodesList[3]['control']
                        attrName = 'cornerInfluence'
                        inXAttrName = 'inShiftX'
                        inYAttrName = 'inShiftY'
                        inZAttrName = 'inShiftZ'
                        inTiltAttrName = 'inTilt'
                        vertShiftAttrName = 'vertShift'
                        vertShiftBlendOutXAttrName = 'vertShiftBlendOutX'
                        jawOpenXAttrName = 'jawOpenShiftX'
                        jawOpenYAttrName = 'jawOpenShiftY'
                        jawOpenZAttrName = 'jawOpenShiftZ'

                    Nodes.addAttrTitle(mouthRig['control'], 'lip')
                                            
                    defaultValue = [0, 0.1, 0.3, 0.5, 0.3, 0.1, 0][n]

                    mc.addAttr(mouthRig['control'], at='float', ln=attrName, k=False, dv=defaultValue)
                    mc.setAttr(mouthRig['control']+'.'+attrName, channelBox=True)

                    targetNodes = list()
                    parents.append([firstNode, secNode])
                    for t in range(2):
                        guideNode = Nodes.createName(sourceNode=cntNodeList[n], side=side, nodeType=Settings.guidePivotSuffix)[0]
                        targetNode = AddNode.emptyNode(guideNode, specific=['first', 'second'][t], nodeType='parentHolder')
                        Nodes.alignObject(targetNode, guideNode)
                        targetNodes.append(targetNode)
                    allTargetNodes.append(targetNodes)

                    for t, targetNode in enumerate(targetNodes):

                        influenceAttr = '%s.%s' % (mouthRig['control'], attrName)

                        parentCnt = mc.parentConstraint(targetNode, cntNodeList[n], mo=False)[0]
                        mc.setAttr('%s.interpType' % parentCnt, 2)

                        for v in [t, 1 - t]:
                            mc.setDrivenKeyframe(parentCnt + '.' + targetNode + 'W' + str(t), cd=influenceAttr, dv=v,
                                                v=1 if v == t else 0, itt='linear', ott='linear')

                    if n == 3:
                        for axis in 'xz':
                            attrName = 'inwardPush%s' % (axis.upper())
                            mc.addAttr(mouthRig['control'], at='float', ln=attrName, k=False, dv=1, hasMinValue=True, minValue=0.0)
                            mc.setAttr(mouthRig['control']+'.'+attrName, channelBox=True)

                            negNode = Nodes.mulNode(input1='%s.rx' % rotCapNode, 
                                                    input2=radius * -0.001)

                            Nodes.mulNode(input1='%s.output' % negNode, 
                                            input2=mouthRig['control'] + '.' + attrName, 
                                            output='%s.t%s' % (drvNode, axis))
                        if not self.hasSurfaceRig == True:
                            outerPushNode = AddNode.parentNode(mouthRig['control'], 'outerPush', lockScale=True)
                            for attrName in ['outerPushIn', 'outerPushInRotate']:
                                outerPushAttr = mouthRig['control']+'.'+attrName
                                Nodes.addAttr(outerPushAttr, k=False, d=True, minVal=0)

                                clampNode = Nodes.clampNode(input='%s.tx' % mouthRig['control'], 
                                                        clampMin=0)

                                negNode = Nodes.mulNode(input1='%s.outputR' % clampNode, 
                                                        input2=-1 if attrName == 'outerPushIn' else 10)

                                Nodes.mulNode(input1='%s.output' % negNode, 
                                                input2=outerPushAttr, 
                                                output='%s.%s'%(outerPushNode, 'tz' if attrName == 'outerPushIn' else 'ry'))
                    else:

                        inShiftNode = AddNode.inbetweenNode(cntNodeList[n], nodeType='inShift', lockScale=True)

                        for i, inAttrName in enumerate([inXAttrName, inYAttrName, inZAttrName, inTiltAttrName]):
                            
                            # in shift
                            if inAttrName == inXAttrName:
                                defaultValue = [0, 0.25, 0.5, 1, 0.5, 0.25, 0][n]
                            else:
                                defaultValue = 0
                            
                            mc.addAttr(mouthRig['control'], at='float', ln=inAttrName, k=False, dv=defaultValue)
                            mc.setAttr(mouthRig['control']+'.'+inAttrName, channelBox=True)

                            addInwardPushNode = Nodes.addNode(input1='%s.tx' % sideNodesList[3]['control'],
                                                    input2='%s.tx' % Nodes.replaceNodeType(sideNodesList[3]['control'], 'inwardDrv'),
                                                    output=None)
                            
                            clampNode = Nodes.clampNode(input='%s.output' % addInwardPushNode, 
                                                    clampMax=0)

                            mulNode = Nodes.mulNode(input1='%s.outputR' % clampNode, 
                                                    input2=mouthRig['control'] + '.' + inAttrName, 
                                                    output=None)
                            
                            Nodes.mulNode(input1='%s.output' % mulNode, 
                                            input2=-1 if 'lower' in mouthRig['control'] and not 'Tilt' in inAttrName and 'X' in inAttrName or 'Z' in inAttrName else 1, 
                                            output='%s.%s%s' % (inShiftNode, 'r' if 'Tilt' in inAttrName else 't', 'x' if 'Tilt' in inAttrName else 'xyz'[i]))

                        jawShiftNode = AddNode.inbetweenNode(cntNodeList[n], nodeType='jawShift', lockScale=True)

                        for i, jawAttrName in enumerate([jawOpenXAttrName, jawOpenYAttrName, jawOpenZAttrName]):
                            
                            # jaw shift
                            
                            mc.addAttr(mouthRig['control'], at='float', ln=jawAttrName, k=False, dv=0)
                            mc.setAttr(mouthRig['control']+'.'+jawAttrName, channelBox=True)
                            
                            clampNode = Nodes.clampNode(input='%s.rx' % rotCapNode, 
                                                    clampMin=0)

                            mulNode = Nodes.mulNode(input1='%s.outputR' % clampNode, 
                                                    input2=mouthRig['control'] + '.' + jawAttrName, 
                                                    output=None)

                            Nodes.mulNode(input1='%s.output' % mulNode, 
                                            input2=0.1, 
                                            output='%s.%s%s' % (jawShiftNode, 't', 'xyz'[i]))

                        # vertical shift
                        mc.addAttr(mouthRig['control'], at='float', ln=vertShiftAttrName, k=False, dv=[0, 0.25, 0.5, 1, 0.5, 0.25, 0][n])
                        mc.setAttr(mouthRig['control']+'.'+vertShiftAttrName, channelBox=True)
                        mc.addAttr(mouthRig['control'], at='float', ln=vertShiftBlendOutXAttrName, k=False, dv=2)
                        mc.setAttr(mouthRig['control']+'.'+vertShiftBlendOutXAttrName, channelBox=True)

                        vertShiftNode = AddNode.inbetweenNode(cntNodeList[n], nodeType='vertShift', lockScale=True)
                        
                        clampNode = Nodes.clampNode(input='%s.tx' % sideNodesList[3]['control'], 
                                                clampMin=0)
                        
                        divNode = Nodes.divNode('%s.outputR'%clampNode,
                                                mouthRig['control'] + '.' + vertShiftBlendOutXAttrName)
                        
                        subNode = Nodes.addNode('%s.output.outputX'%divNode,
                                                -1)
                        
                        mulNode = Nodes.mulNode('%s.output'%subNode,
                                                -1 if 'upperlip' in mouthRig['control'] else 1)
                        
                        mulShiftNode = Nodes.mulNode('%s.output'%mulNode,
                                                mouthRig['control'] + '.' + vertShiftAttrName)
                        
                        mulNode = Nodes.mulNode('%s.output'%mulShiftNode,
                                                '%s.ty' % sideNodesList[3]['control'],
                                                '%s.ty'%vertShiftNode)

                lipNodesCol.append(sideNodesList)

            lipNodesList = list(itertools.chain.from_iterable(lipNodesCol))

        # upper lower lip shift attrs
        
        if self.hasLipsRig:
            mouthCornerLeft = lipNodesCol[0][3]['control']
            mouthCornerRight = lipNodesCol[1][3]['control']
            initDist = Tools.getDistance(mouthCornerLeft, mouthCornerRight)
            distNodes = Tools.createDistanceDimension(mouthCornerLeft, mouthCornerRight, parentType='parent')
            locList.extend(distNodes)

            for lipRig in upperlowerlipNodesList:
                
                lipControl = lipRig['control']
                shiftNode = AddNode.parentNode(lipControl, 'shift', lockScale=True)

                Nodes.addAttrTitle(lipControl, 'shiftAttributes')
                lipSqueezeShift = lipControl+'.lipSqueezeShift'
                lipStretchShift = lipControl+'.lipStretchShift'
                jawDownShift = lipControl+'.jawDownShift'
                jawUpShift = lipControl+'.jawUpShift'

                Nodes.addAttr(lipSqueezeShift, k=False, d=True)
                zeroNode = Nodes.addNode('%s.distance'%distNodes[2],
                                            -initDist)
                clampNode = Nodes.clampNode('%s.output'%zeroNode,
                                            clampMax=0)
                mulNode = Nodes.mulNode('%s.outputR'%clampNode,
                                        -0.1)
                lipSqueezeNode = Nodes.mulNode('%s.output'%mulNode,
                                            lipSqueezeShift)

                Nodes.addAttr(lipStretchShift, k=False, d=True)
                zeroNode = Nodes.addNode('%s.distance'%distNodes[2],
                                            -initDist)
                clampNode = Nodes.clampNode('%s.output'%zeroNode,
                                            clampMin=0)
                mulNode = Nodes.mulNode('%s.outputR'%clampNode,
                                        -0.1)
                lipStretchNode = Nodes.mulNode('%s.output'%mulNode,
                                            lipStretchShift)

                Nodes.addAttr(jawDownShift, k=False, d=True)
                clampNode = Nodes.clampNode('%s.rx'%rotCapNode,
                                            clampMin=0)
                mulNode = Nodes.mulNode('%s.outputR'%clampNode,
                                        -0.02)
                jawDownNode = Nodes.mulNode('%s.output'%mulNode,
                                            jawDownShift)

                Nodes.addAttr(jawUpShift, k=False, d=True)
                clampNode = Nodes.clampNode('%s.rx'%rotCapNode,
                                            clampMax=0)
                mulNode = Nodes.mulNode('%s.outputR'%clampNode,
                                        -0.02)
                jawUpNode = Nodes.mulNode('%s.output'%mulNode,
                                            jawUpShift)

                addLipNode = Nodes.addNode('%s.output'%lipSqueezeNode,
                            '%s.output'%lipStretchNode)

                addJawNode = Nodes.addNode('%s.output'%jawDownNode,
                            '%s.output'%jawUpNode)

                Nodes.addNode('%s.output'%addLipNode,
                            '%s.output'%addJawNode,
                            '%s.tz'%shiftNode)

        # lips curve

        allPointLocGroups = list()
        allLipJointList = list()
        if self.hasNoRollJoints:
            allNoRollJoints = list()
        
        for c, lipsCurveGuide in enumerate([upperlipCurveGuide, lowerlipCurveGuide]):
            
            jointCount = [self.upperLipJointCount, self.lowerLipJointCount][c]

            if jointCount == 0:
                continue

            if self.hasNoRollJoints:
                noRollGroup = AddNode.emptyNode(component=self.name, element=['upperlip', 'lowerlip'][c], specific='noRoll', parentNode=rigGroup)
                if self.parentNode:
                    Tools.parentScaleConstraint([self.headJointNode, jawJointNode][c], noRollGroup)

            lipsCurveRig = Curve.Build(curveNode=lipsCurveGuide,
                                        jointCount=jointCount,
                                        squashing=self.lipSqueezing,
                                        scaling=True,
                                        chain=False,
                                        segmenting=True,
                                        controlPerJoint=False,
                                        hasJointGuides=True,
                                        shape='Cross',
                                        offset=upperLowerLipOffsets[c],
                                        useGuideAttr=False,
                                        alignAxis='X',
                                        upAxis='Z',
                                        postDeformAlignment=True,
                                        skeletonParent=[self.parentNode, jawJointNode][c],
                                        skeletonParentToAllJoints=True).createRig()
            
            jointNodeList.extend(lipsCurveRig['joints'][1:-1])
            if c == 0:
                upperLipJoints = lipsCurveRig['joints'][1:-1]
            if c == 1:
                lowerLipJoints = lipsCurveRig['joints'][1:-1]
            
            AttrConnect.multiGroupConnect([lipsCurveRig['rigGroup']], rigGroup)
            lipsRigGroups.append(lipsCurveRig['rigGroup'])
            mc.parent(lipsCurveRig['rigGroup'], rigGroup)
            for jointNode in [lipsCurveRig['joints'][0], lipsCurveRig['joints'][-1]]:
                mc.delete(jointNode)

            if self.hasNoRollJoints:
                for jointNode in lipsCurveRig['joints'][1:-1]:
                    noRollJoint = AddNode.jointNode(jointNode, specific='noRoll', parentNode=noRollGroup)
                    allNoRollJoints.append(noRollJoint)
                    jointNodeList.append(noRollJoint)
                    mc.move(size*[-0.1, 0.1][c], noRollJoint, moveY=True, os=True, r=True)
                    mc.pointConstraint(jointNode, noRollJoint, mo=True)

            allLipJointList.extend(lipsCurveRig['joints'][1:-1])

            parentNodeCol = [[Nodes.createName(self.name, Settings.rightSide, Settings.controlSuffix, 'lipcorner')[0],
                                Nodes.createName(self.name, Settings.rightSide, Settings.controlSuffix, 'upperlipout')[0],
                                Nodes.createName(self.name, Settings.rightSide, Settings.controlSuffix, 'upperlipmid')[0],
                                Nodes.createName(self.name, Settings.rightSide, Settings.controlSuffix, 'upperlipin')[0],
                                Nodes.createName(self.name, Settings.leftSide, Settings.controlSuffix, 'upperlipin')[0],
                                Nodes.createName(self.name, Settings.leftSide, Settings.controlSuffix, 'upperlipmid')[0],
                                Nodes.createName(self.name, Settings.leftSide, Settings.controlSuffix, 'upperlipout')[0],
                                Nodes.createName(self.name, Settings.leftSide, Settings.controlSuffix, 'lipcorner')[0]],
                                [Nodes.createName(self.name, Settings.rightSide, Settings.controlSuffix, 'lipcorner')[0],
                                Nodes.createName(self.name, Settings.rightSide, Settings.controlSuffix, 'lowerlipout')[0],
                                Nodes.createName(self.name, Settings.rightSide, Settings.controlSuffix, 'lowerlipmid')[0],
                                Nodes.createName(self.name, Settings.rightSide, Settings.controlSuffix, 'lowerlipin')[0],
                                Nodes.createName(self.name, Settings.leftSide, Settings.controlSuffix, 'lowerlipin')[0],
                                Nodes.createName(self.name, Settings.leftSide, Settings.controlSuffix, 'lowerlipmid')[0],
                                Nodes.createName(self.name, Settings.leftSide, Settings.controlSuffix, 'lowerlipout')[0],
                                Nodes.createName(self.name, Settings.leftSide, Settings.controlSuffix, 'lipcorner')[0]]]

            for p, pointLocGroup in enumerate(lipsCurveRig['offsets']):
                for axis in 'xyz':
                   Nodes.removeConnection('%s.s%s'%(pointLocGroup, axis))
                Nodes.setParent(pointLocGroup, Nodes.replaceNodeType(parentNodeCol[c][p], Settings.scaleCompensateNode))
                for axis in 'xyz':
                    mc.setAttr('%s.s%s'%(pointLocGroup, axis), 1)
                for axis in 'xyz':
                    mc.setAttr('%s.r%s'%(pointLocGroup, axis), 0)
                clsHandleNode = Nodes.replaceNodeType(pointLocGroup, Settings.clusterHandleSuffix)
                if p == 7 and c == 1:
                    mc.setAttr('%s.rz'%(clsHandleNode), 180)
                if p == 0 and c == 0:
                    mc.setAttr('%s.ry'%(clsHandleNode), 180)
                    mc.setAttr('%s.rz'%(clsHandleNode), 180)
                if p == 0 and c == 1:
                    mc.setAttr('%s.ry'%(clsHandleNode), 180)

                if Nodes.getElement(parentNodeCol[c][p]) == 'lipcorner':
                    lipsCurveRig['controls'][p] = mc.rename(lipsCurveRig['controls'][p], Nodes.replaceNodeType(lipsCurveRig['controls'][p], Settings.dummySuffix))
                else:
                    stickyName = Nodes.replaceToken(parentNodeCol[c][p], Nodes.getElement(parentNodeCol[c][p])+'Sticky', 'element')
                    Nodes.addNamingAttr(lipsCurveRig['controls'][p], Nodes.getNamingOrder(parentNodeCol[c][p]))
                    lipsCurveRig['controls'][p] = mc.rename(lipsCurveRig['controls'][p], stickyName)
                    Nodes.addNamingAttr(lipsCurveRig['offsets'][p], Nodes.getNamingOrder(parentNodeCol[c][p]))
                    lipsCurveRig['offsets'][p] = mc.rename(lipsCurveRig['offsets'][p], Nodes.replaceNodeType(lipsCurveRig['controls'][p], Settings.offNodeSuffix))
                    for colorRGB in 'RGB':
                        mc.setAttr('%s.overrideColor%s'%(lipsCurveRig['controls'][p], colorRGB), mc.getAttr('%s.overrideColor%s'%(parentNodeCol[c][p], colorRGB)))

            if not self.hasStickyLips:
                for offNode in [lipsCurveRig['offsets'][0], lipsCurveRig['offsets'][-1]]:
                    allPointLocGroups.append(offNode)
            else:
                allPointLocGroups.extend(lipsCurveRig['offsets'])

            # lip tilt setup
            for n, lipControl in enumerate(lipsCurveRig['controls'][1:-1]):
                tiltNode = AddNode.parentNode(lipControl, 'tilt', lockScale=True)
                for axis in 'xyz':
                    mc.setAttr('%s.s%s'%(tiltNode, axis), lock=False)
                if n == 2 or n == 3:
                    infAttr = tiltNeighbor1Attr
                if n == 1 or n == 4:
                    infAttr = tiltNeighbor2Attr
                if n == 0 or n == 5:
                    infAttr = tiltNeighbor3Attr
                Nodes.mulNode('%s.rx'%upperlowerlipTiltNodesList[c]['control'],
                                infAttr,
                                '%s.rx'%tiltNode)
                subNode = Nodes.addNode('%s.sy'%upperlowerlipTiltNodesList[c]['control'],
                                -1)
                mulNode = Nodes.mulNode('%s.output'%subNode,
                                infAttr)
                Nodes.addNode('%s.output'%mulNode,
                                1,
                                '%s.sy'%tiltNode)
                subNode = Nodes.addNode('%s.sz'%upperlowerlipTiltNodesList[c]['control'],
                                -1)
                mulNode = Nodes.mulNode('%s.output'%subNode,
                                infAttr)
                Nodes.addNode('%s.output'%mulNode,
                                1,
                                '%s.sz'%tiltNode)
                centerJoint = lipsCurveRig['joints'][int([self.upperLipJointCount, self.lowerLipJointCount][c]/2)]
                Nodes.alignObject(upperlowerlipTiltNodesList[c]['offset'], centerJoint, rotation=False, scale=False)
                Tools.parentScaleConstraint(centerJoint, upperlowerlipTiltNodesList[c]['offset'])
            
        # sticky mouth

        if self.hasStickyLips and self.hasLipsRig:
            for side in [Settings.leftSide, Settings.rightSide]:
                for s, stickyLipsNode in enumerate(stickyLipsNodesSideSet[0 if side == Settings.leftSide else 1]):
                    if Nodes.getElement(stickyLipsNode) == 'lipcorner':
                        continue
                    createStickyLips(stickyLipsNode, side, s)

        allWrinkleJointList = list()

        for s, side in enumerate([Settings.leftSide, Settings.rightSide]):
            
            # wrinkle
            if self.hasWrinkleRig and self.hasLipsRig:
                if side == Settings.rightSide:
                    wrinkleCurveGuide = Tools.mirrorObject(wrinkleCurveGuide, rotate=(0, 0, 0))
                    for c in range(3):
                        Guiding.convertGuide(Nodes.createName(self.name, 
                                                                Settings.leftSide,
                                                                Settings.guidePivotSuffix,
                                                                'wrinkle',
                                                                c)[0], 
                                                                mirror=True)[0]
                        if c != 0:
                            Guiding.convertGuide(Nodes.createName(self.name, 
                                                                    Settings.leftSide,
                                                                    Settings.guidePivotSuffix,
                                                                    'wrinkle',
                                                                    c,
                                                                    'bezierHandleA')[0], 
                                                                    mirror=True)[0]
                        if c != 2:
                            Guiding.convertGuide(Nodes.createName(self.name, 
                                                                    Settings.leftSide,
                                                                    Settings.guidePivotSuffix,
                                                                    'wrinkle',
                                                                    c,
                                                                    'bezierHandleB')[0], 
                                                                    mirror=True)[0]
                
                wrinkleCurveRig = Curve.Build(curveNode=wrinkleCurveGuide,
                                                side=side,
                                                jointCount=self.wrinkleJointCount,
                                                squashing=False,
                                                scaling=False,
                                                chain=False,
                                                segmenting=True,
                                                hasJointGuides=True,
                                                alignAxis='Y',
                                                upAxis='Z',
                                                skeletonParent=self.parentNode,
                                                skeletonParentToAllJoints=True).createRig()

                mc.parent(wrinkleCurveRig['rigGroup'], rigGroup)
                allWrinkleJointList.extend(wrinkleCurveRig['joints'])
                AttrConnect.multiGroupConnect([wrinkleCurveRig['rigGroup']], rigGroup)
                
                for wrinkleOffset in wrinkleCurveRig['bezierHandleOffsets'][1:3]:
                    Nodes.lockAndHideAttributes(wrinkleOffset, t=[True, True, True], r=[True, True, True], s=[True, True, True])
                    mc.hide(wrinkleOffset)
                Nodes.lockAndHideAttributes(wrinkleCurveRig['offsets'][-1], t=[True, True, True], r=[True, True, True], s=[True, True, True])
                mc.hide(wrinkleCurveRig['offsets'][-1])

                wrinkleControls.extend(wrinkleCurveRig['controls'])
                wrinkleControls.extend(wrinkleCurveRig['bezierHandleControls'])
                
                Tools.parentScaleConstraint(jawRig['control'], wrinkleCurveRig['offsets'][2])

                wrinkleCntNode = AddNode.inbetweenNode(wrinkleCurveRig['offsets'][1], nodeType='drv')

                mouthCornerControl = lipNodesCol[s][3]['control']
                wrinkleCornerControl = wrinkleCurveRig['controls'][1]

                conNodes = Tools.blendBetween([self.parentNode], 
                                            [mouthCornerControl], 
                                            [wrinkleCntNode], 
                                            attrNode=wrinkleCornerControl, 
                                            attrName='cornerInfluence', 
                                            attrTitle='follow', 
                                            positionConstrained=True,
                                            defaultValue=0.8,
                                            attrIsKeyable=False)[0]

                # additional influence attributes
                
                for d, direction in enumerate(['up', 'down', 'inner', 'outer', 'rotateUp', 'rotateDown', 'pushOut']):
                    inbNode = AddNode.parentNode(wrinkleCornerControl, nodeType=direction+'Inf', lockScale=True)
                    drivenAttr = 'ty' if d < 2 else 'tx'
                    sourceAttr = drivenAttr
                    if 'rotate' in direction:
                        drivenAttr = 'rz'
                        sourceAttr = 'ty'
                    if d == 6:
                        drivenAttr = 'tz'
                        sourceAttr = 'tx'
                    clampNode = Nodes.clampNode('%s.%s'%(mouthCornerControl, sourceAttr),
                                                clampMin=[0, None, None, 0, 0, None, 0][d],
                                                clampMax=[None, 0, 0, None, None, 0, None][d])
                    Tools.drivenAttr(sourceNode=clampNode, 
                                    sourceAttr='outputR', 
                                    drivenNode=inbNode, 
                                    drivenAttr=drivenAttr, 
                                    attrNode=wrinkleCornerControl, 
                                    attrName=direction+'Influence', 
                                    attrTitle='influence',
                                    attrIsKeyable=False,
                                    lowerLimit=0,
                                    defaultValue=defaultValue)
                
                Tools.parentScaleConstraint(self.parentNode, wrinkleCurveRig['offsets'][1])
                
                mc.parent(conNodes, wrinkleCurveRig['rigGroup'])

            # surface constraint
            if self.hasSurfaceRig == True:
                surfaceNode = Guiding.convertGuide(surfaceGuide, mirror=True if side == Settings.rightSide else False, mirrorRotate=(0, 0, 0), nodeType=Settings.surfaceSuffix)[0]
                surfaceNodeList.append(surfaceNode)
                mc.parent(surfaceNode, rigGroup)
                mc.setAttr('%s.inheritsTransform'%surfaceNode, False)
                if self.hasWrinkleRig:
                    wrinkleConstraintNodeList = Tools.createSurfaceConstraintConnection([wrinkleCurveRig['controls'][1]] + wrinkleCurveRig['bezierHandleControls'][1:3],
                                                                                        surfaceNode, 
                                                                                        attrNode=wrinkleCurveRig['controls'][1], 
                                                                                        attrName='stickToSkull',
                                                                                        defaultValue=0,
                                                                                        side=side,
                                                                                        lockScale=False,
                                                                                        zNegate=True)[0]
                    mc.parent(wrinkleConstraintNodeList, rigGroup)
                    allConstraintNodes.extend(wrinkleConstraintNodeList)
                ctlNodeList = [ctlNodes['control'] for ctlNodes in [lipNodesCol[s][x] for x in [1, 2, 3, 4, 5]]]
                constraintNodeList, resultNodeList, inbNodeList = Tools.createSurfaceConstraintConnection(ctlNodeList, 
                                                                                                            surfaceNode, 
                                                                                                            attrNode=lipNodesCol[s][3]['control'],
                                                                                                            attrName='stickToSkull',
                                                                                                            defaultValue=1,
                                                                                                            side=side,
                                                                                                            lockScale=True,
                                                                                                            zNegate=True,
                                                                                                            parentToSclCmp=False)
                mc.parent(constraintNodeList, rigGroup)
                allConstraintNodes.extend(constraintNodeList)

                zBlendNode = AddNode.inbetweenNode(inbNodeList[2], nodeType='zBlend', lockScale=True)

                Nodes.mulNode(input1='%s.tz'%Nodes.replaceNodeType(zBlendNode, 'inwardDrv'), 
                                    input2='%s.stickToSkull'%lipNodesCol[s][3]['control'], 
                                    output='%s.tz'%zBlendNode)

            zNegateNode = Nodes.createName(self.name, side=side, element='lipcorner', nodeType='zNegate')[0]
            inwardDrvNode = Nodes.createName(self.name, side=side, element='lipcorner', nodeType='inwardDrv')[0]
            if mc.objExists(zNegateNode) and mc.objExists(inwardDrvNode):
                Nodes.setParent(zNegateNode, inwardDrvNode)
                
        # anchors

        if self.hasAnchorRig == True and self.upperLipJointCount > 0 and self.lowerLipJointCount > 0 and self.hasLipsRig:
            allWrinkleJointList, outerMouthRigGroupList = Squash.createMouth(
                anchorGuides=[
                [upperlipinGuide, upperlipinOuterGuide],
                [upperlipmidGuide, upperlipmidOuterGuide],
                [upperlipoutGuide, upperlipoutOuterGuide],
                [lipcornerGuide, lipcornerOuterGuide],
                [lowerlipoutGuide, lowerlipoutOuterGuide],
                [lowerlipmidGuide, lowerlipmidOuterGuide],
                [lowerlipinGuide, lowerlipinOuterGuide]
                ],
                upperLipJoints=upperLipJoints,
                lowerLipJoints=lowerLipJoints,
                lipNodesCol=lipNodesCol,
                allWrinkleJointList=allWrinkleJointList,
                parentNode=self.parentNode,
                jawRig=jawRig,
                pinGroup=pinGroup,
                outerMouthRigGroupList=outerMouthRigGroupList,
                upAxis=self.anchorUpAxis,
                anchorUpAxisCorner=self.anchorUpAxisCorner,
                jawMulNode=jawMulNode,
                rigGroup=rigGroup,
                )

        # mouth main

        if self.hasLipsRig:
            mouthMainRig = Control.createControl(node=mouthMainPivotGuide, lockAndHide=[[False, False, False], [False, False, False], [True, True, True]])
        
        if self.hasStickyLips and self.hasLipsRig:

            Nodes.addAttrTitle(mouthMainRig['control'], 'stickyLips')
            
            mc.addAttr(mouthMainRig['control'], at='float', ln='stickyLipsLeft', k=True, dv=0, 
                    hasMinValue=True, minValue=0,
                    hasMaxValue=True, maxValue=1)
            mc.addAttr(mouthMainRig['control'], at='float', ln='stickyLipsRight', k=True, dv=0, 
                    hasMinValue=True, minValue=0,
                    hasMaxValue=True, maxValue=1)
            mc.addAttr(mouthMainRig['control'], at='float', ln='stickyness', k=True, dv=0, 
                    hasMinValue=True, minValue=0,
                    hasMaxValue=True, maxValue=1)
            mc.addAttr(mouthMainRig['control'], at='bool', ln='autoSticky', k=True, dv=False)
            mc.addAttr(mouthMainRig['control'], at='float', ln='autoStickyRange', k=True, dv=0.02, 
                    hasMinValue=True, minValue=0.01)
            mc.addAttr(mouthMainRig['control'], at='float', ln='distanceOffset', k=True, dv=0)
            mc.addAttr(mouthMainRig['control'], at='float', ln='stickyHeight', k=True, dv=0.5,
                    hasMinValue=True, minValue=0,
                    hasMaxValue=True, maxValue=1)
            distanceOffsetAttr = '%s.%s'%(mouthMainRig['control'], 'distanceOffset')
            mc.connectAttr(distanceOffsetAttr, '%s.offsetY'%lowerDistTrackerParentCnt)
            autoStickyAttr = '%s.%s'%(mouthMainRig['control'], 'autoSticky')
            rangeAttr = '%s.%s'%(mouthMainRig['control'], 'autoStickyRange')
            distAttr = lowerDistTracker+'.ty'
            for s, stickyLipsSideSet in enumerate([stickyLipsNodesSideSet[0], stickyLipsNodesSideSet[1]]):
                stickyLipsAttrName = ['stickyLipsLeft', 'stickyLipsRight'][s]
                stickyAttr = '%s.%s'%(mouthMainRig['control'], stickyLipsAttrName)
                for stickyLipsNode in stickyLipsSideSet:
                    if not stickyLipsNode:
                        continue
                    if Nodes.getElement(stickyLipsNode) == 'lipcorner':
                        continue
                    stickyLipsNodeAttr = '%s.%s'%(stickyLipsNode, stickyLipsAttrName)
                    # adding auto sticky
                    expr = '$sticky = %s;\n'%stickyAttr \
                        + '$autoSticky = %s;\n'%autoStickyAttr \
                        + '$distAttr = %s;\n'%distAttr \
                        + '$range = %s;\n'%rangeAttr \
                        + '$res = $sticky;\n' \
                        + '$distTravel = $distAttr;\n' \
                        + 'if ($distTravel > $range) {$distTravel = $range;}\n' \
                        + '$autoRes = abs(($distTravel/$range)-1);\n' \
                        + 'if ($autoSticky == 1) {$res = $autoRes*$sticky;}\n' \
                        + '%s = $res;'%stickyLipsNodeAttr
                    Nodes.exprNode(stickyLipsNodeAttr, expr)
                    #
                    mc.connectAttr('%s.stickyness'%mouthMainRig['control'], '%s.stickyness'%stickyLipsNode)
                    mc.connectAttr('%s.stickyHeight'%mouthMainRig['control'], '%s.stickyHeight'%stickyLipsNode)
            ''' # visibility
            for lipTiltRig in lipTiltRigs:
                stickyMulNode = Nodes.mulNode('%s.stickyLipsLeft'%mouthMainRig['control'],
                                                '%s.stickyLipsRight'%mouthMainRig['control'])
                visAttr = '%s.visibility'%lipTiltRig['control']
                visDrv = '%s.output'%stickyMulNode
                mc.setDrivenKeyframe(visAttr, cd=visDrv, dv=0, v=0, itt='linear', ott='linear')
                mc.setDrivenKeyframe(visAttr, cd=visDrv, dv=1, v=1, itt='linear', ott='linear')
                mc.setDrivenKeyframe(visAttr, cd=visDrv, dv=1, v=0, itt='linear', ott='linear')
                mc.setDrivenKeyframe(visAttr, cd=visDrv, dv=0, v=1, itt='linear', ott='linear')
            '''
        if self.lipSqueezing and self.hasLipsRig:
            
            # TODO needs to be redone according to upper/lower lip
            
            attrName = 'lipSqueeze'
            trgAttrNames = ['scalePowerStart', 'scalePowerEnd', 'scalePowerMid']
            mc.addAttr(mouthMainRig['control'], at='float', ln=attrName, k=True, dv=0, 
                        hasMinValue=True, minValue=0,
                        hasMaxValue=True, maxValue=1)
            for t, trgAttrName in enumerate(trgAttrNames):
                mc.connectAttr('%s.%s'%(mouthMainRig['control'], attrName), '%s.%s'%(rigGroup, trgAttrName))
        
        if self.hasLipsRig:
            mc.parent(mouthMainRig['offset'], controlGroup)

            for node in [headLoc, jawLoc]:
                Tools.connectTransforms(mouthMainRig['control'], node)

        # surface skin cluster
        if mc.objExists(self.headJointNode) and mc.objExists(jawJointNode) and self.hasLipsRig and self.hasSurfaceRig == True:
            for surfaceNode in surfaceNodeList:
                skinClusterNode = mc.skinCluster([self.headJointNode, jawJointNode], surfaceNode, tsb=True)[0]
                for u in range(4):
                    for v in range(4):
                        weightValue = [0, 0.33, 0.67, 1][v]
                        mc.skinPercent(skinClusterNode, '%s.cv[%s][%s]'%(surfaceNode, u, v), tv=(self.headJointNode, weightValue))
                        mc.skinPercent(skinClusterNode, '%s.cv[%s][%s]'%(surfaceNode, u, v), tv=(jawJointNode, abs(1-weightValue)))

        if self.hasLipsRig:
            mc.parent([x['offset'] for x in lipNodesList], controlGroup)
            for x in lipNodesList:
                for axis in 'xyz':
                    mc.setAttr('%s.s%s'%(x['control'], axis), lock=False)

        if self.hasLipsRig:
            VisSwitch.connectVisSwitchGroup(locList + 
                                                allConstraintNodes + 
                                                allPointLocGroups, 
                                                rigGroup, 
                                                displayAttr='setupDisplay')
        VisSwitch.connectVisSwitchGroup(jointNodeList,
                                            rigGroup, 
                                            displayAttr='jointDisplay')
        if self.hasLipsRig and self.hasAnchorRig == True:
            VisSwitch.connectVisSwitchGroup(outerMouthRigGroupList,
                                                rigGroup, 
                                                displayAttr='squashControlDisplay', 
                                                forceConnection=True)
        if self.hasSurfaceRig == True and self.hasLipsRig:
            VisSwitch.connectVisSwitchGroup(surfaceNodeList,
                                                rigGroup, 
                                                displayAttr='setupDisplay')
        VisSwitch.connectVisSwitchGroup([jawRig['control']], rigGroup, displayAttr='jawControlDisplay')
        VisSwitch.connectVisSwitchGroup([jawTipRig['control']], rigGroup, displayAttr='jawTipControlDisplay')
        if self.hasLipsRig:
            VisSwitch.connectVisSwitchGroup([x['control'] for x in lipNodesList], rigGroup, displayAttr='controlDisplay')
            VisSwitch.connectVisSwitchGroup([x['control'] for x in upperlowerlipTiltNodesList], rigGroup, displayAttr='controlDisplay')
            VisSwitch.connectVisSwitchGroup([x['control'] for x in upperlowerlipNodesList], rigGroup, displayAttr='controlDisplay')
        if self.hasWrinkleRig:
            VisSwitch.connectVisSwitchGroup(wrinkleControls, rigGroup, displayAttr='wrinkleControlDisplay', forceConnection=True)
        if self.hasLipsRig:
            VisSwitch.connectVisSwitchGroup([mouthMainRig['control']], rigGroup, displayAttr='mainControlDisplay')
            
        # making sure no negative scale values are on controls
        if self.hasLipsRig:
            for controlNode in [mouthRig['control'] for mouthRig in mouthRigs]+lipsCurveRig['controls']+(wrinkleCurveRig['controls'] if self.hasWrinkleRig else []):
                Nodes.setTrs(controlNode)
        
        self.cleanup(Nodes.replaceNodeType(rigGroup, 'guide'), trashGuides=True, removeRightGuides=False, hierarchy=False, display=False, selectionSets=False)

        if self.input_noseName and self.input_cheeksName:
            self.connectRig(self.input_noseName, self.input_cheeksName)

        if self.hasLipsRig:
            for s, side in enumerate([Settings.leftSide, Settings.rightSide]):
                parents = parentsSide[s]
                allTargetNodes = allTargetNodesSide[s]
                for n, parent in enumerate(parents):
                    for p in range(2):
                        sclCmpNode = Nodes.replaceNodeType(parent[p], Settings.scaleCompensateNode)
                        parentNode = sclCmpNode if Nodes.exists(sclCmpNode) else parent[p]
                        Nodes.setParent(allTargetNodes[n][p], parentNode)

        return {
            'rigGroup': rigGroup, 
            'joints': jointNodeList,
            'upperLipJoints': upperLipJoints,
            'lowerLipJoints': lowerLipJoints,
            }

    def connectRig(self,
                    noseName,
                    cheeksName):
        
        for side in [Settings.leftSide, Settings.rightSide]:
            
            surfaceConstraintNode = Nodes.createName(self.name, side, nodeType='surfaceConstraint', element='lipcorner')[0]
            
            for n, node in enumerate([Nodes.createName(noseName, side, Settings.offNodeSuffix)[0],
                                            Nodes.createName(cheeksName, side, Settings.offNodeSuffix, 'main')[0],
                                            Nodes.createName(cheeksName, side, Settings.offNodeSuffix, indices=2)[0]]):
                
                if mc.objExists(node):
    
                    controlNode = Nodes.replaceSuffix(node, Settings.controlSuffix)
                    offNode = Nodes.replaceSuffix(node, Settings.offNodeSuffix)
                    cntNode = AddNode.inbetweenNode(node, suffix='cnt')
                    srcOffsetNode = AddNode.childNode(surfaceConstraintNode, byName=node, nodeType='srcOffset')
                    mc.parent(srcOffsetNode, Nodes.createName(self.name, side, Settings.offNodeSuffix, 'lipcorner')[0])
                    Nodes.alignObject(srcOffsetNode, node)
                    Tools.parentScaleConstraint(surfaceConstraintNode, srcOffsetNode, connectRotate=False, connectScale=False)

                    Nodes.addAttrTitle(controlNode, 'follow')
                    mc.addAttr(controlNode, at='float', ln='cornerInfluence', k=True, dv=0,
                            hasMinValue=True, minValue=0, hasMaxValue=True, maxValue=1)
    
                    srcNodeList = [offNode, srcOffsetNode]

                    influenceAttr = controlNode+'.cornerInfluence'
    
                    for t, srcNode in enumerate(srcNodeList):
                        if mc.objExists(srcNode):
                            pointCnt = mc.pointConstraint(srcNodeList, cntNode, mo=True)
                            for v in [t, 1 - t]:
                                mc.setDrivenKeyframe(pointCnt + '.' + srcNode + 'W' + str(t), cd=influenceAttr, dv=v,
                                                    v=1 if v == t else 0, itt='linear', ott='linear')

                    if n == 0:
                        Tools.parentScaleConstraint(Nodes.createName(self.name, side, Settings.controlSuffix, 'wrinkle', 0)[0], node, useMatrix=False)