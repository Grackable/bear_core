# Shoulder

import maya.cmds as mc

from bear.system import Settings
from bear.utilities import Tools
from bear.utilities import VisSwitch
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.components.basic import Control

def createRig(shoulderGuide,
                side,
                name,
                limbRig,
                shoulderName='shoulder',
                hasJoint=True,
                hasTopDeformJoint=False,
                parentNode=None):

    shoulderGroup = AddNode.compNode(component=name, side=side, element=shoulderName, hasGlobalScale=False)

    size = Nodes.getSize(Nodes.replaceNodeType(shoulderGuide, Settings.guideShapeSuffix))[0]
    
    controlRig = Control.createControl(node=shoulderGuide, side=side, rigGroup=limbRig['rigGroup'])
    
    if hasJoint:
        shoulderJoint = AddNode.jointNode(controlRig['scaleCompensate'], skeletonParent=parentNode, resetTransforms=True)
    
    Nodes.lockAndHideAttributes(controlRig['control'], t=[False, False, False], r=[False, False, False], s=[True, True, True], v=True)
    
    limbJoints = limbRig['ikJoints'] if limbRig['ikJoints'] else limbRig['fkJoints']

    shoulderNode = shoulderJoint if hasJoint else controlRig['control']

    Tools.parentScaleConstraint(shoulderNode, limbJoints[0], useMatrix=False)
    Tools.parentScaleConstraint(controlRig['control'], limbRig['fkUpper']['offset'], useMatrix=False)

    Tools.parentScaleConstraint(shoulderNode, limbRig['limbParent'], useMatrix=False)
    
    if hasTopDeformJoint:
        if limbRig['upperJoints'] == None:
            upperJoint = limbRig['blendJoints'][0] if limbRig['blendJoints'] else limbRig['fkJoints'][0]
        else:
            upperJoint = limbRig['upperJoints'][0]
        deformJointNode = AddNode.jointNode(component=name, side=side, element=shoulderName, specific='knuckle', skeletonParent=upperJoint)
        deformOffNode = AddNode.parentNode(deformJointNode)
        deformCntNode = AddNode.inbetweenNode(deformOffNode, nodeType='cnt')
        Nodes.alignObject(deformOffNode, limbJoints[0])
        mc.move(0, size * (-0.1 if side == Settings.rightSide else 0.1), 0, deformOffNode, relative=True, objectSpace=True)
        oriNode = AddNode.emptyNode(upperJoint, parentNode=shoulderNode, nodeType='ori')
        Nodes.orientConstraint([oriNode, upperJoint], deformCntNode)
        mc.parent(deformOffNode, mc.listRelatives(upperJoint, parent=True)[0])
    else:
        deformJointNode = None

    mc.parent(controlRig['offset'], shoulderGroup)
    Tools.parentScaleConstraint(parentNode, controlRig['offset'], useMatrix=False)

    VisSwitch.connectVisSwitchGroup(([shoulderJoint] if hasJoint else []) + ([deformJointNode] if hasTopDeformJoint else []), shoulderGroup, displayAttr='jointDisplay')
    VisSwitch.connectVisSwitchGroup([controlRig['control']], shoulderGroup, displayAttr=shoulderName+'ControlDisplay', visGroup='arm')

    mc.select(clear=True)

    return {'joints': ([shoulderJoint] if hasJoint else []) + ([deformJointNode] if hasTopDeformJoint else []),
            'control': controlRig['control'],
            'offset': controlRig['offset'],
            'mirrorScale': controlRig['mirrorScale'],
            'rigGroup': shoulderGroup}