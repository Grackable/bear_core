# Foot

import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om

from bear.system import Settings
from bear.system import Guiding
from bear.utilities import VisSwitch
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.body import Limb

def createRig(platformPivotGuides, 
                upperLimbGuide,
                lowerLimbGuide,
                ankleGuide,
                toesGuide,
                upnodeGuide,
                side,
                name, 
                limbRig,
                shoulderRig=None,
                quadruped=False,
                hasPlatform=True,
                invertKnee=False):

    if limbRig['smoothIkAttr']:
        mc.setAttr(limbRig['smoothIkAttr'], 0)

    ankleJoint = limbRig['blendJoints'][2]
    ikJoint = limbRig['ikJoints'][2]
    fkJoint = limbRig['fkJoints'][2]

    rigGroup = AddNode.compNode(name, side, element='foot', hasGlobalScale=False)

    if quadruped:
        toesJoint = limbRig['blendJoints'][3]
        toesIkJoint = limbRig['ikJoints'][3]
        toesFkJoint = limbRig['fkJoints'][3]
    else:
        toesJoint = AddNode.jointNode(None, name, side, element='toes', skeletonParent=limbRig['ankleJoints'][-1] if quadruped else ankleJoint)
        toesIkJoint = AddNode.jointNode(toesGuide, name, side, specific='ik', element='toes', nodeType=Settings.setupJointSuffix, alignByRotationValues=False)
        toesFkJoint = AddNode.jointNode(toesGuide, name, side, specific='fk', element='toes', nodeType=Settings.setupJointSuffix, alignByRotationValues=False)
    
    mc.parent(toesJoint, rigGroup)

    ankleOffset = Guiding.getGuideAttr(ankleGuide)['offset']

    toesOffset = Guiding.getGuideAttr(toesGuide)['offset']
    shape = Guiding.getGuideAttr(toesGuide)['shape']

    ikFkBlendCnt = mc.orientConstraint([toesIkJoint, toesFkJoint], toesJoint)[0]
    mc.setAttr('%s.interpType' % (ikFkBlendCnt), 2)

    ikBlendParam = '%s.%sW0' % (ikFkBlendCnt, toesIkJoint)
    fkBlendParam = '%s.%sW1' % (ikFkBlendCnt, toesFkJoint)

    mc.connectAttr(limbRig['ikFkBlendAttr'], ikBlendParam)
    negNode = Nodes.addNode(limbRig['ikFkBlendAttr'],
                    -1)
    Nodes.mulNode('%s.output'%negNode,
                    -1,
                    fkBlendParam)
    
    toesFkRig = Control.createControl(toesGuide,
                                        element='toes',
                                        specific='fk',
                                        side=side,
                                        offset=toesOffset,
                                        shape=shape)

    Nodes.lockAndHideAttributes(toesFkRig['control'], t=[True, True, True], r=[False, False, False], s=[True, True, True], v=True)
    Nodes.parentConstraint(toesFkRig['control'], toesFkJoint)
    Nodes.setParent(toesFkRig['offset'], rigGroup)
    mc.parentConstraint(limbRig['fkEnd']['scaleCompensate'], toesFkRig['offset'], mo=True)
    
    # attributes
    Nodes.addAttrTitle(limbRig['ik']['control'], 'foot')

    for attrName in ['roll', 'breakAngleFront', 'breakAngleBack', 'bank', 'frontSpin', 'backSpin']:
        mc.addAttr(limbRig['ik']['control'], at='float', ln=attrName, keyable=True, dv=45 if attrName == 'breakAngleFront' else 0,
                    hasMinValue=True if attrName == 'breakAngleFront' else False,
                    minValue=0 if attrName == 'breakAngleFront' else -180,
                    hasMaxValue=True if attrName == 'breakAngleBack' else False,
                    maxValue=0 if attrName == 'breakAngleBack' else 180,)
    pivotSwopAttrName = 'pivotToToes'
    mc.addAttr(limbRig['ik']['control'], at='bool', k=True, dv=quadruped, ln=pivotSwopAttrName)
    pivotSwopAttr = limbRig['ik']['control']+'.'+pivotSwopAttrName

    if quadruped:
        # quadruped attributes already added in limb
        weightBalanceAttrName = 'weightBalance'
        heelPivotAttrName = 'heelPivotOffset'

        quadrupedAttr = limbRig['quadrupedAttr']
        weightBalanceAttr = limbRig['ik']['control']+'.'+weightBalanceAttrName
        heelPivotAttr = limbRig['ik']['control']+'.'+heelPivotAttrName

    if hasPlatform:
        platformPivots = [AddNode.emptyNode(node, nodeType=Settings.locNodeSuffix, objType='locator') for node in platformPivotGuides]
        platformFront, platformBack, platformInner, platformOuter, spinFront, spinBack = platformPivots
        platformFrontOff, platformBackOff, platformInnerOff, platformOuterOff, spinFrontOff, spinBackOff = [AddNode.parentNode(x) for x in platformPivots]
        if side == Settings.rightSide:
            mc.rotate(0, 0, 180, Nodes.getParent(platformBack), os=True, r=True)
            #[mc.rotate(0, 180, 0, platformOff, os=True, r=True) for platformOff in platformOffList]
            #mc.rotate(0, 0, 180, Nodes.getParent(spinFront), os=True, r=True)
            #mc.rotate(0, 0, 180, Nodes.getParent(spinBack), os=True, r=True)
    
    ankleDrv = AddNode.emptyNode(component=name, side=side, nodeType='drv', element='ankle')
    
    Nodes.alignObject(ankleDrv, toesFkJoint, rotation=False)
    Nodes.alignObject(ankleDrv, limbRig['fkJoints'][2], translation=False)

    ankleIkRig = Control.createControl(ankleDrv,
                                        component=name,
                                        element='ankle',
                                        specific='ik',
                                        side=side,
                                        offset=[[(Tools.getDistance(ankleGuide, toesGuide)-ankleOffset[0][0])*-1, 
                                                                                            -ankleOffset[0][1], 
                                                                                            ankleOffset[0][2]], 
                                                                                            ankleOffset[1], 
                                                                                            ankleOffset[2]],
                                        shape=shape,
                                        parentNode=spinBack if hasPlatform else None,
                                        useGuideAttr=False,
                                        hasPivot=False)
    
    mc.connectAttr(limbRig['ikFkBlendAttr'], '%s.visibility'%ankleIkRig['offset'])
    Nodes.setParent(ankleIkRig['offset'], rigGroup)
    
    Nodes.lockAndHideAttributes(ankleIkRig['control'], t=[True, True, True], r=[False, False, False], s=[not quadruped, True, True], v=True)
    if ankleIkRig['mirrorScale']:
        Nodes.setParent(ankleDrv, ankleIkRig['mirrorScale'])
        Nodes.setTrs(ankleDrv)
        Nodes.setParent(ankleIkRig['control'], ankleDrv)
        Nodes.setTrs(ankleIkRig['control'])
    
    if limbRig['modJoints']:
        Nodes.aimConstraint(ankleIkRig['pivotCompensate'], 
                            limbRig['modJoints'][2], 
                            aimAxis='-x' if side == Settings.rightSide else 'x',
                            upAxis='y', 
                            upNode=limbRig['ikJoints'][2])
    
    Nodes.alignObject(toesJoint, toesGuide) # hard fix
    toesIkRig = Control.createControl(toesGuide,
                                        component=name,
                                        element='toes',
                                        specific='ik',
                                        side=side,
                                        offset=[[toesOffset[0][0], toesOffset[0][1]*-1, toesOffset[0][2]*-1], 
                                                    toesOffset[1], 
                                                    toesOffset[2]],
                                        shape=shape,
                                        parentNode=rigGroup,
                                        parentType='Hierarchy')
    Nodes.alignObject(toesIkRig['offset'], toesGuide) # hard fix
    
    Nodes.lockAndHideAttributes(toesIkRig['control'], t=[True, True, True], r=[False, False, False], s=[True, True, True], v=True)
    
    mc.parentConstraint(toesIkRig['control'], toesIkJoint)
    mc.parent(toesIkJoint, rigGroup)

    mc.parent(toesIkRig['offset'], spinBack if hasPlatform else ankleIkRig['control'])
    mc.parent(toesFkJoint, toesFkRig['scaleCompensate'])
    
    if hasPlatform:
        frontPivotRig = Control.createControl(node=platformFront,
                                                component=name,
                                                element='pivot',
                                                specific='front',
                                                side=side,
                                                shape='Sphere',
                                                offset=[[0, 0, 0], [0, 0, 0], [ankleOffset[2][0]*0.3 for x in range(3)]],
                                                parentNode=limbRig['ik']['scaleCompensate'],
                                                parentType='Hierarchy',
                                                parentDirection='NodeToControl',
                                                ignoreMissingGuideControlWarning=True)

        Nodes.lockAndHideAttributes(frontPivotRig['control'], t=(True, True, True), s=(True, True, True))

    mc.delete(mc.parentConstraint(fkJoint, limbRig['ikHandle']))
    if side == Settings.rightSide:
        mc.rotate(0, 0, 180, limbRig['ikHandle'], os=True, r=True)
    
    mc.parent(limbRig['ikHandle'], ankleIkRig['scaleCompensate'])
    Nodes.setTrs(limbRig['ikHandle'], 0, t=False, r=True, s=False)
    if hasPlatform:
        mc.parent(spinBackOff, spinFront)
        mc.parent(spinFrontOff, platformInner)
        mc.parent(platformInnerOff, platformOuter)
        mc.parent(platformOuterOff, platformBack)
        mc.parent(platformFront, frontPivotRig['mirrorScale'])
        Nodes.setTrs(platformFront)
        mc.parent(frontPivotRig['control'], platformFront)
        mc.parent(platformBackOff, frontPivotRig['scaleCompensate'])
        mc.delete(platformFrontOff)
    
    mc.orientConstraint(limbRig['ikHandle'], ikJoint)
    
    if hasPlatform:
        rollParam = '%s.roll' % (limbRig['ik']['control'])
        breakAngleFrontParam = '%s.breakAngleFront' % (limbRig['ik']['control'])
        breakAngleBackParam = '%s.breakAngleBack' % (limbRig['ik']['control'])
        ankleParam = '%s.rotateY' % (ankleDrv)
        frontParam = '%s.rotateX' % (platformFront)
        backParam = '%s.rotateX' % (platformBack)

        ankleExpr = '$rollVal = %s;\n' % (rollParam) \
                + '$breakAngleFrontVal = %s;\n' % (breakAngleFrontParam) \
                + '$breakAngleBackVal = %s;\n' % (breakAngleBackParam) \
                + '$val = -$rollVal;\n'\
                + 'if ($rollVal > $breakAngleFrontVal) {$val = -$breakAngleFrontVal;}\n'\
                + 'if ($rollVal < $breakAngleBackVal) {$val = -$breakAngleBackVal;}\n'\
                + '%s = $val;\n' % (ankleParam)
        
        Nodes.exprNode(attr=ankleParam, expr=ankleExpr, specific='roll')
    
    if quadruped:
        quadAddition = '$quadruped = %s;\n' % quadrupedAttr \
                     + 'if ($quadruped > 0) {$breakAngleVal = 0;}\n'
    else:
        quadAddition = ''
    
    if hasPlatform:
        frontExpr = '$rollVal = %s;\n' % (rollParam) \
                + '$breakAngleVal = %s;\n' % (breakAngleFrontParam) \
                + '$val = 0.0;\n' + quadAddition \
                + 'if ($rollVal > $breakAngleVal) {$val = $rollVal-$breakAngleVal;}\n' \
                + '%s = $val;\n' % (frontParam)

        Nodes.exprNode(attr=frontParam, expr=frontExpr, specific='rollFront')

        backExpr = '$rollVal = %s;\n' % (rollParam) \
                + '$breakAngleVal = %s;\n' % (breakAngleBackParam) \
                + '$val = 0.0;\n' + quadAddition \
                + 'if ($rollVal < $breakAngleVal) {$val = $rollVal-$breakAngleVal;}\n' \
                + '%s = $val*%s;\n' % (backParam, -1 if side == Settings.rightSide else 1)
        
        Nodes.exprNode(attr=backParam, expr=backExpr, specific='rollBack')

        mc.connectAttr('%s.bank' % (limbRig['ik']['control']), '%s.rotateZ' % (platformInner))
        mc.transformLimits(platformInner, rz=(0, 0), erz=[1, 0])

        mc.connectAttr('%s.bank' % (limbRig['ik']['control']), '%s.rotateZ' % (platformOuter))
        mc.transformLimits(platformOuter, rz=(0, 0), erz=[0, 1])

        mc.connectAttr('%s.frontSpin' % (limbRig['ik']['control']), '%s.rotateY' % (spinFront))
        mc.connectAttr('%s.backSpin' % (limbRig['ik']['control']), '%s.rotateY' % (spinBack))
    
    mc.connectAttr(limbRig['ikFkBlendAttr'], '%s.visibility'%toesIkRig['offset'])
    negNode = Nodes.addNode(limbRig['ikFkBlendAttr'],
                    -1)
    Nodes.mulNode('%s.output'%negNode,
                    -1,
                    '%s.visibility'%toesFkRig['offset'])
    
    Nodes.addAttrTitle(limbRig['attr']['control'], 'foot')
    footScaleAttrName = 'footScale'
    mc.addAttr(limbRig['attr']['control'], at='float', ln=footScaleAttrName, keyable=True, dv=1, hasMinValue=True, minValue=0.1)
    
    mc.parent(ankleJoint, rigGroup)
    
    for b, blendJoint in enumerate([ankleJoint, toesJoint]):
        scaleNode = AddNode.parentNode(blendJoint, nodeType='manualScale')
        [mc.connectAttr(limbRig['attr']['control'] + '.' + footScaleAttrName, '%s.s%s' % (scaleNode, axis)) for axis in 'xyz']
        mc.parentConstraint(limbRig['blendJoints'][b+1], scaleNode, mo=True)
        for axis in 'XYZ':
            mc.setAttr('%s.jointOrient%s'%(blendJoint, axis), 0)

    # pivot swop
    
    ikChildren = mc.listRelatives(limbRig['ik']['pivotCompensate'], children=True, type='transform')
    pivotSwopNode = AddNode.parentNode(limbRig['ik']['control'], nodeType='pivotSwop', lockScale=True)
    pivotSwopRevNode = AddNode.emptyNode(pivotSwopNode, nodeType='pivotSwopReverse', lockScale=True)

    dummyPosNode = mc.group(empty=True)
    Nodes.alignObject(dummyPosNode, ankleGuide)
    
    Nodes.alignObject(pivotSwopNode, dummyPosNode if quadruped else toesGuide, rotation=False)
    Nodes.alignObject(pivotSwopRevNode, toesGuide if quadruped else dummyPosNode, rotation=False)
    
    Nodes.setParent(pivotSwopRevNode, pivotSwopNode)
    
    mc.delete(dummyPosNode)

    pivotTranslateOffset = [mc.getAttr('%s.t%s'%(pivotSwopNode, axis)) for axis in 'xyz']
    pivotRevTranslateOffset = [mc.getAttr('%s.t%s'%(pivotSwopRevNode, axis)) for axis in 'xyz']
    pivotRotateOffset = [mc.getAttr('%s.r%s'%(pivotSwopNode, axis)) for axis in 'xyz']
    pivotRevRotateOffset = [mc.getAttr('%s.r%s'%(pivotSwopRevNode, axis)) for axis in 'xyz']

    Nodes.setParent(pivotSwopRevNode, limbRig['ik']['pivotCompensate'])
    [mc.setAttr('%s.t%s'%(pivotSwopRevNode, axis), 0) for axis in 'xyz']
    [mc.setAttr('%s.r%s'%(pivotSwopRevNode, axis), 0) for axis in 'xyz']
    if ikChildren:
        mc.parent(ikChildren, pivotSwopRevNode)

    for q, quadNode in enumerate([pivotSwopNode, pivotSwopRevNode]):
        for t, trs in enumerate('t'):
            for a, axis in enumerate('xyz'):
                param = '%s.%s%s'%(quadNode, trs, axis)
                offset = [[pivotTranslateOffset, pivotRevTranslateOffset][q], [pivotRotateOffset, pivotRevRotateOffset][q]][t][a]
                expr = '$offset = %s;\n' % offset\
                        + '$pivotSwop = %s;\n' % pivotSwopAttr \
                        + 'if ($pivotSwop %s 0) {$offset = 0;}\n' % ('>' if quadruped else '==') \
                        + '%s = $offset;\n' % param
                Nodes.exprNode(attr=param, expr=expr, specific='quadruped')
    
    # pivot swop shape offset
    controlParent = Nodes.getParent(limbRig['ik']['control'])
    mc.parent(limbRig['ik']['control'], world=True)
    [mc.setAttr('%s.t%s'%(limbRig['ik']['control'], axis), 0) for axis in 'xyz']
    [mc.setAttr('%s.r%s'%(limbRig['ik']['control'], axis), 0) for axis in 'xyz']
    clusterNode = Nodes.clusterNode('%s.cv[*]'%limbRig['ik']['control'], specific='pivotSwop')
    mc.setAttr('%s.inheritsTransform'%clusterNode, False)
    Nodes.setParent(clusterNode, limbRig['ik']['control'], lockRotate=False, lockScale=False)
    mc.hide(clusterNode)
    [mc.setAttr('%s.t%s'%(clusterNode, 'xyz'[a]), v) for a, v in enumerate(pivotRevTranslateOffset)]
    mc.setDrivenKeyframe('%s.envelope'%clusterNode.replace('Handle', 'HandleCluster'), cd=pivotSwopAttr, dv=0 if quadruped else 1, v=1, itt='linear', ott='linear')
    mc.setDrivenKeyframe('%s.envelope'%clusterNode.replace('Handle', 'HandleCluster'), cd=pivotSwopAttr, dv=1 if quadruped else 0, v=0, itt='linear', ott='linear')
    Nodes.setParent(limbRig['ik']['control'], controlParent)
    [mc.setAttr('%s.t%s'%(limbRig['ik']['control'], axis), 0) for axis in 'xyz']
    [mc.setAttr('%s.r%s'%(limbRig['ik']['control'], axis), 0) for axis in 'xyz']
    
    if quadruped:

        # spring ik setup
        quadrupedGroup = AddNode.compNode(name, side, element='quadruped')
        Nodes.setParent(quadrupedGroup, limbRig['rigGroup'])

        upperLimbJoint = AddNode.jointNode(upperLimbGuide, element='upper', nodeType='quadruped', parentToNode=False)
        lowerLimbJoint = AddNode.jointNode(lowerLimbGuide, element='lower', nodeType='quadruped', parentNode=upperLimbJoint, parentToNode=False)
        ankleJoint = AddNode.jointNode(ankleGuide, element='ankle', nodeType='quadruped', parentNode=lowerLimbJoint, parentToNode=False)
        if quadruped:
            quadrupedEndJoint = AddNode.jointNode(toesGuide, element='toes', nodeType='quadruped', parentNode=ankleJoint, parentToNode=False)

        quadrupedChain = [upperLimbJoint, lowerLimbJoint, ankleJoint, quadrupedEndJoint]
        Nodes.setParent(upperLimbJoint, quadrupedGroup)
        if not mc.objExists('ikSpringSolver'):
            mc.createNode('ikSpringSolver')

        mel.eval("setToolTo $gSelect")
        quadIkHandle = Nodes.ikHandleNode(startJoint=upperLimbJoint, endJoint=quadrupedChain[3], ikType='ikSpringSolver', specific='quadruped')
        
        
        dummyUpnode = AddNode.emptyNode(ankleGuide, nodeType='dummyUpnode')
        Nodes.aimConstraint(upperLimbGuide, 
                            dummyUpnode, 
                            aimAxis='x',
                            upAxis='y',
                            upNode=toesGuide)

        Nodes.setParent(quadIkHandle, spinBack)
        
        parentControlRig = limbRig['parentRig'] if shoulderRig == None else shoulderRig
        Nodes.parentConstraint(parentControlRig['control'], upperLimbJoint)
        
        # upnode setup
        ikUpnodeOffset = Guiding.getGuideAttr(upnodeGuide)['offset']
        ikUpnodeShape = Guiding.getGuideAttr(upnodeGuide)['shape']
        
        upnodeOffset = Tools.getDistance(quadrupedChain[1], quadrupedChain[3]) * (1 if invertKnee else -1) * 0.75
        
        quadUpnodeRig = Control.createControl(node=dummyUpnode,
                                                component=name, 
                                                element='ankle', 
                                                specific='upnode',
                                                offset=ikUpnodeOffset,
                                                side=side,
                                                deleteNode=True,
                                                shape=ikUpnodeShape,
                                                useGuideAttr=False)
        
        mc.move(upnodeOffset, quadUpnodeRig['offset'], z=True, r=True, os=True)
        Nodes.setParent(quadUpnodeRig['offset'], rigGroup)
        Nodes.lockAndHideAttributes(quadUpnodeRig['control'], t=[False, False, False], r=[True, True, True],
                                    s=[True, True, True], v=True)
        
        # upnode ik line
        Limb.ikLine(limbRig['mids'],'lower', True, ikJoint, quadUpnodeRig, name, side, rigGroup, 'leg')

        # upnode follow
        followAttrName = 'AnkleFollowFoot'
        followAttr = quadUpnodeRig['control']+'.'+followAttrName
        Nodes.addAttrTitle(quadUpnodeRig['control'], 'Ankle')
        mc.addAttr(quadUpnodeRig['control'], at='float', ln=followAttrName, keyable=True, hidden=False, hasMinValue=True,
                minValue=0, hasMaxValue=True, maxValue=1, dv=1)

        Nodes.parentConstraint(parentControlRig['offset'], quadUpnodeRig['offset'])
        ikFollowParent = AddNode.childNode(quadUpnodeRig['control'], 'ikFollow')
        shoulderFollowParent = AddNode.childNode(quadUpnodeRig['control'], 'shoulderFollow')
        mc.parent(ikFollowParent, limbRig['ik']['offset'])
        mc.pointConstraint(limbRig['ik']['control'], ikFollowParent, mo=True)[0]
        mc.parent(shoulderFollowParent, parentControlRig['offset'])
        followNode = AddNode.inbetweenNode(quadUpnodeRig['offset'], 'follow')
        parentCnt = mc.parentConstraint([ikFollowParent, shoulderFollowParent], followNode, mo=False, skipRotate=['x', 'y', 'z'])[0]
        mc.parentConstraint(shoulderFollowParent, limbRig['ik']['offset'], mo=True)[0]

        mc.setDrivenKeyframe('%s.%sW0' % (parentCnt, ikFollowParent), cd=followAttr, dv=1, v=1, itt='linear', ott='linear')
        mc.setDrivenKeyframe('%s.%sW0' % (parentCnt, ikFollowParent), cd=followAttr, dv=0, v=0, itt='linear', ott='linear')
        mc.setDrivenKeyframe('%s.%sW1' % (parentCnt, shoulderFollowParent), cd=followAttr, dv=1, v=0, itt='linear', ott='linear')
        mc.setDrivenKeyframe('%s.%sW1' % (parentCnt, shoulderFollowParent), cd=followAttr, dv=0, v=1, itt='linear', ott='linear')
        
        poleVectorCnt = Nodes.poleVectorConstraint(quadUpnodeRig['control'], quadIkHandle)

        for axis in 'xyz':
            Nodes.divNode(input1='%s.constraintTranslate%s'%(poleVectorCnt, axis.upper()), 
                            input2=-1, 
                            output='%s.poleVector%s'%(quadIkHandle, axis.upper()), 
                            axis=axis)
        
        # disable vis for ankle upnode rig if quadruped is turned off
        mc.connectAttr(quadrupedAttr, '%s.visibility'%quadUpnodeRig['offset'])
        
        # switch setup
        drvNode = Nodes.getParent(ankleIkRig['control'])
        Nodes.setParent(ankleIkRig['control'], ankleIkRig['mirrorScale'])
        quadNode = AddNode.childNode(ankleIkRig['mirrorScale'], nodeType='quadruped')
        Nodes.alignObject(quadNode, drvNode)
        quadSwitch = AddNode.parentNode(ankleIkRig['control'], nodeType='quadrupedSwitch', lockScale=False)
        Nodes.lockAndHideAttributes(ankleIkRig['control'], t=[True, True, True], r=[False, False, False], s=[False, True, True], v=True)
        Nodes.alignObject(quadSwitch, drvNode)
        mc.orientConstraint(quadrupedChain[2], quadNode, mo=True)
        Tools.blendBetween([drvNode], [quadNode], [quadSwitch], attrNode=limbRig['ik']['control'], attrName='quadrupedEnabled', scaleConstrained=True)
        Nodes.alignObject(limbRig['ikHandle'], ankleGuide)
        Nodes.setTrs(limbRig['ikHandle'], 0, t=False, r=True, s=False)
        
        # weight balance
        mc.setDrivenKeyframe('%s.springAngleBias[0].springAngleBias_FloatValue'%quadIkHandle, cd=weightBalanceAttr, dv=0, v=1, itt='linear', ott='linear')
        mc.setDrivenKeyframe('%s.springAngleBias[0].springAngleBias_FloatValue'%quadIkHandle, cd=weightBalanceAttr, dv=1, v=0, itt='linear', ott='linear')
        mc.setDrivenKeyframe('%s.springAngleBias[1].springAngleBias_FloatValue'%quadIkHandle, cd=weightBalanceAttr, dv=0, v=0, itt='linear', ott='linear')
        mc.setDrivenKeyframe('%s.springAngleBias[1].springAngleBias_FloatValue'%quadIkHandle, cd=weightBalanceAttr, dv=1, v=1, itt='linear', ott='linear')

        # platform pivot shift
        for platform in [platformBack, spinBack]:
            platformChildren = mc.listRelatives(platform, children=True, type='transform')
            platformRev = AddNode.childNode(platform, nodeType='pivotReverse')
            mc.parent(platformChildren, platformRev)
            mc.connectAttr(heelPivotAttr, '%s.tz'%platform)

            Nodes.mulNode(input1=heelPivotAttr, 
                            input2=-1, 
                            output='%s.tz'%platformRev)
        Tools.parentScaleConstraint(platformRev, ankleIkRig['offset'])

        # quadruped smooth ik
        # this solution is not perfect since the spingSolverIK doesn't like scaling on the first joint
        # the result is an offseted rotation for the ankle but it's good enough
        for limbNode in [upperLimbJoint, lowerLimbJoint, ankleJoint, quadNode]:
            mc.connectAttr('%s.sx'%limbRig['ikJoints'][0], '%s.sx'%limbNode)

        if limbRig['midCntNodes']:
            if quadruped and limbRig['smoothIkAttr']:
                Limb.applySmoothIkOffset(limbRig['midCntNodes'][0], limbRig['smoothIkAttr'], limbRig['smoothIkOffsetAttr'])
            if limbRig['smoothIkAttr']:
                Limb.applySmoothIkOffset(limbRig['midCntNodes'][1], limbRig['smoothIkAttr'], limbRig['smoothIkOffsetAttr'], quadrupedAttr if quadruped else None)
    else:
        Tools.parentScaleConstraint(spinBack if hasPlatform else limbRig['ik']['control'], ankleIkRig['offset'])
        quadrupedChain = None
        quadUpnodeRig = None

    # ik fk match dummy node
    if quadruped:
        mc.setAttr('%s.pivotToToes'%limbRig['ik']['control'], False)
    matchDummy = AddNode.emptyNode(limbRig['ik']['control'],
                                   specific='ikFkMatch',
                                   nodeType=Settings.dummySuffix)
    Nodes.setParent(matchDummy, limbRig['fkEnd']['control'])
    if quadruped:
        mc.setAttr('%s.pivotToToes'%limbRig['ik']['control'], True)
        matchDummy = AddNode.emptyNode(limbRig['ik']['control'],
                                    specific='ikFkMatchToes',
                                    nodeType=Settings.dummySuffix)
        Nodes.setParent(matchDummy, toesFkRig['control'])
    
    if hasPlatform:
        for locNode in [platformFront, platformBack, platformInner, platformOuter, spinFront, spinBack]:
            VisSwitch.connectVisSwitchGroup(mc.listRelatives(locNode, shapes=True), rigGroup, displayAttr='setupDisplay')
    if quadruped:
        VisSwitch.connectVisSwitchGroup(quadrupedChain+[quadIkHandle], rigGroup, displayAttr='setupDisplay')
    VisSwitch.connectVisSwitchGroup([toesIkJoint, toesFkJoint, matchDummy], rigGroup, displayAttr='setupDisplay')
    VisSwitch.connectVisSwitchGroup([toesJoint, ankleJoint], rigGroup, displayAttr='jointDisplay')
    VisSwitch.connectVisSwitchGroup([x['control'] for x in [toesFkRig, toesIkRig, ankleIkRig] + \
                                     ([frontPivotRig] if hasPlatform else []) + ([quadUpnodeRig] if quadruped else [])], 
                                    rigGroup, 
                                    displayAttr='controlDisplay', 
                                    visGroup='leg')

    if limbRig['smoothIkAttr']:
        mc.setAttr(limbRig['smoothIkAttr'], 1)

    mc.select(clear=True)

    return {'toesFk': toesFkRig,
            'toesIk': toesIkRig,
            'toesJoint': toesJoint,
            'ankleIk': ankleIkRig,
            'frontPivot': frontPivotRig if hasPlatform else None,
            'quadrupedJoints': quadrupedChain,
            'rigGroup': rigGroup}