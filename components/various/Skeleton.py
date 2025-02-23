# Skeleton

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import Tools
from bear.utilities import Nodes
from bear.utilities import VisSwitch
from bear.utilities import AddNode

class Build(Generic.Build):
    
    def __init__(self,
                 name='skeleton',
                 tokenOrder=Settings.namingOrder,
                 leftSideToken=Settings.leftSide,
                 rightSideToken=Settings.rightSide,
                 skinJointToken=Settings.skinJointSuffix,
                 createRootJoint=True,
                 rootJointName='root',
                 rootJointParent=Nodes.createName('root', element='main', nodeType=Settings.controlSuffix)[0],
                 useCustomConstraint=True,
                 useScaleConstraining=False,
                 displaySwitch='bodyDisplaySwitch',
                 *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)
        
        self.name = name
        self.tokenOrder = tokenOrder
        self.leftSideToken = leftSideToken
        self.rightSideToken = rightSideToken
        self.skinJointToken = skinJointToken
        self.createRootJoint = createRootJoint
        self.rootJointName = rootJointName
        self.rootJointParent = rootJointParent
        self.useCustomConstraint = useCustomConstraint
        self.useScaleConstraining = useScaleConstraining
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):

        guideGroup = super(Build, self).createGuide(self.name, None, definition=False)

        return {'guideGroup': guideGroup}

    def createRig(self):

        rigGroup = super(Build, self).createRig(self.name)

        self.rootJointParent = ConnectionHandling.inputExists(self.rootJointParent)

        cntsGroup = AddNode.emptyNode(rigGroup, nodeType='parentConstraints')

        setupSkinJoints = list()
        skeletonParents = list()
        skeletonJoints = list()
        cnts = list()
        for skinJoint in [x for x in Nodes.getAllChildren(Settings.rigGroup, nodeType=Settings.skinJointSuffix)] \
                        + [x for x in Nodes.getAllChildren(Settings.rigGroup, nodeType=Settings.setupSkinJointSuffix)]:
            
            if not mc.objExists('%s.skeletonParent'%skinJoint):
                continue
                
            skeletonParent = mc.getAttr('%s.skeletonParent'%skinJoint).split(',')[0]
            skeletonParents.append(Nodes.replaceNodeType(skeletonParent, Settings.skinJointSuffix))
            setupSkinJoint = mc.rename(skinJoint, Nodes.replaceNodeType(skinJoint, Settings.setupSkinJointSuffix))
            setupSkinJoints.append(setupSkinJoint)
            skeletonJoint = AddNode.jointNode(setupSkinJoint, nodeType=Settings.skinJointSuffix, resetTransforms=False)
            skeletonJoints.append(skeletonJoint)
            Nodes.alignObject(skeletonJoint, setupSkinJoint)
            Nodes.convertJointRotToOrientSkeleton(skeletonJoint)
            mc.makeIdentity(skeletonJoint, a=True, t=True, r=True, s=True)
            if self.useScaleConstraining:   
                cnts.extend(Tools.parentScaleConstraint(setupSkinJoint, skeletonJoint, useMatrix=self.useCustomConstraint))
            else:
                cnts.extend(mc.parentConstraint(setupSkinJoint, skeletonJoint, mo=True))
            mc.setAttr('%s.segmentScaleCompensate'%skeletonJoint, False)

        if self.createRootJoint:
            rootJoint = mc.joint(name=self.rootJointName, radius=mc.getAttr('%s.radius'%setupSkinJoints[0]) if setupSkinJoints else 1)
            Nodes.setParent(rootJoint, rigGroup)
            if self.rootJointParent:
                if self.useScaleConstraining:
                    cnts.extend(Tools.parentScaleConstraint(self.rootJointParent, rootJoint, useMatrix=self.useCustomConstraint))
                else:
                    print(self.rootJointParent, rootJoint)
                    pnt = mc.parentConstraint(self.rootJointParent, rootJoint, mo=True)
                    print(pnt)
                    cnts.extend(mc.parentConstraint(self.rootJointParent, rootJoint, mo=True))

        for n, setupSkinJoint in enumerate(setupSkinJoints):
            
            if not mc.objExists('%s.skeletonParent'%setupSkinJoint):
                continue
            
            skeletonJoint = skeletonJoints[n]
            skeletonParent = skeletonParents[n]
            if mc.objExists(skeletonParent):
                mc.parent(skeletonJoint, skeletonParent)
            elif skeletonParent == 'root' and self.createRootJoint:
                mc.parent(skeletonJoint, rootJoint)
            else:
                mc.parent(skeletonJoint, rigGroup)

        for skeletonJoint in Nodes.getAllChildren(rigGroup):
            skeletonJoint = mc.rename(skeletonJoint, Nodes.replaceNodeType(skeletonJoint, self.skinJointToken))
            side = Nodes.getSide(skeletonJoint)
            if side:
                if side == Settings.leftSide:
                    side = self.leftSideToken
                if side == Settings.rightSide:
                    side = self.rightSideToken
                mc.rename(skeletonJoint, Nodes.replaceSide(skeletonJoint, side))
        Nodes.renameToNamingConvention(self.tokenOrder, rigGroup)
        Nodes.setParent(cnts, cntsGroup)
        Nodes.setParent(cntsGroup, rigGroup)

        VisSwitch.connectVisSwitchGroup([rigGroup], rigGroup, displayAttr='jointDisplay')

        return {'rigGroup': rigGroup}