# Deform Tweak

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import MessageHandling
from bear.utilities import VisSwitch
from bear.utilities import NodeOnVertex
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.basic import Guide

class Build(Generic.Build):

    def __init__(self,
                 name='deformTweak',
                 side=None,
                 geo=None,
                 setName=None,
                 count=0,
                 addToExisting=False,
                 supportScale=False,
                 displaySwitch='displaySwitch',
                 *args, **kwargs):
                 
        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.side = side
        self.geo = geo
        if self.geo != None:
            self.driver = Nodes.addSuffix(self.geo, suffix=Settings.deformNodeSuffix)
        else:
            self.driver = None
        self.setName = None if setName == '' else setName
        self.count = count
        self.addToExisting = addToExisting
        self.supportScale = supportScale
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):

        guideGroup = super(Build, self).createGuide(self.name, self.side, definition)
        if definition:
            return {'guideGroup': guideGroup}
        
        if self.setName:
            if not Nodes.exists(self.setName):
                MessageHandling.warning('Set does not exist: %s'%self.setName)
                self.setName = None

        if self.setName:
            clothSet = mc.sets(self.setName, q=True)
            vtxSel = mc.ls(clothSet, fl=True)
            i = 0
            while i < len(vtxSel):
                for vtx in vtxSel:
                    value = mc.pointPosition(vtx)
                    guide = Guide.createGuide(component=self.name, side=self.side, indices=i)

                    mc.setAttr('{}{}'.format(guide['pivot'], '.tx'), value[0])
                    mc.setAttr('{}{}'.format(guide['pivot'], '.ty'), value[1])
                    mc.setAttr('{}{}'.format(guide['pivot'], '.tz'), value[2])

                    orient = mc.normalConstraint(self.geo, guide['pivot'])
                    mc.delete(orient)

                    if guideGroup:
                        mc.parent(guide['pivot'], guideGroup)

                    i += 1

        if self.count > 0:
            for c in range(self.count):
                if not mc.objExists(Nodes.createName(component=self.name, side=self.side, indices=c, nodeType=Settings.guidePivotSuffix)[0]):
                    guide = Guide.createGuide(component=self.name, side=self.side, indices=c)
                    if guideGroup:
                        mc.parent(guide['pivot'], guideGroup)

        return {'guideGroup': guideGroup}

    def createRig(self):

        if not Nodes.exists(self.geo):
            MessageHandling.noNodeDefined('DeformTweak')
            return

        self.rigGroup = super(Build, self).createRig(self.name, self.side)
        mc.setAttr('%s.inheritsTransform'%self.rigGroup, False)

        controlList = []
        controlParent = []
        jointsList = []

        skinClusterNode = Nodes.createName(component=self.name, side=self.side, element='deformTweak', nodeType='skinCluster')[0]

        # delete existing skin cluster if it's not the deform layer skin cluster
        # make sure to save the weights before and apply them to the deform geo skin cluster instead
        existingSkinCluster = Nodes.getSkinCluster(self.geo)[0]
        if not self.addToExisting:
            Nodes.delete(existingSkinCluster)
            existingSkinCluster = None

        if not self.addToExisting:
            createBlendshape(self.driver, self.name, self.side, self.geo, self.rigGroup)

        guideGrp = Nodes.createName(component=self.name, side=self.side, nodeType='guide')[0]

        if guideGrp:
            
            for child in mc.listRelatives(guideGrp, c=True):

                controlRig = Control.createControl(child, side=self.side, parentType='Constraint')
                controlList.append(controlRig['control'])
                controlParent.append(controlRig['offset'])

                mc.parent(controlRig['offset'], self.rigGroup)

                VisSwitch.connectVisSwitchGroup([controlRig['control']], self.rigGroup, displayAttr='controlDisplay')

            for ctrl in controlList:
                jointNode = AddNode.jointNode(ctrl)
                parent_ctrl = mc.listRelatives(ctrl, parent=True)[0]
                mc.parent(jointNode, parent_ctrl, r=True)
                jointsList.append(jointNode)

                VisSwitch.connectVisSwitchGroup([jointNode], self.rigGroup, displayAttr='jointDisplay')

            # add root skin joint to have ability to tweak only certain parts of the geo
            rootJoint = AddNode.jointNode(component=self.name, side=self.side, element='rigid')
            jointsList.append(rootJoint)
            mc.parent(rootJoint, self.rigGroup)
            VisSwitch.connectVisSwitchGroup([rootJoint], self.rigGroup, displayAttr='setupDisplay')

            for jnt in jointsList:
                mc.makeIdentity(jnt, a=True, t=True, r=True, s=True, jo=True)

            for ctrl, jnt in zip(controlList, jointsList):
                if self.side == Settings.rightSide:
                    Nodes.divNode('%s.translate'%(ctrl),
                                -1,
                                '%s.translate'%(jnt),
                                axis='XYZ',
                                operation=1)
                else:
                    mc.connectAttr('{}{}'.format(ctrl, '.translate'), ('{}{}'.format(jnt, '.translate')))
                mc.connectAttr('{}{}'.format(ctrl, '.rotate'), ('{}{}'.format(jnt, '.rotate')))
                if self.supportScale:
                    mc.connectAttr('{}{}'.format(ctrl, '.scale'), ('{}{}'.format(jnt, '.scale')))

            NodeOnVertex.proximityPin(self.driver, controlParent, side=self.side)

        if not existingSkinCluster:
            Tools.copySkinCluster(self.geo, [self.driver])

        if existingSkinCluster:
            jointInfCount = len(mc.skinCluster(existingSkinCluster, inf=True, q=True))
            mc.skinCluster(existingSkinCluster,
                            ai=jointsList,
                            edit=True)
            connectBindPreMatrix(jointsList, existingSkinCluster, jointInfCount)
            skinClusterNode = existingSkinCluster
        else:
            jointInfCount = 0
            skinClusterNode = mc.skinCluster(jointsList, 
                                                self.geo, 
                                                sm=0, 
                                                tsb=True, 
                                                nw=2, 
                                                mi=5, 
                                                dr=4, 
                                                name=skinClusterNode)[0]
            connectBindPreMatrix(jointsList, skinClusterNode, jointInfCount)

        addCompAttrs(self.driver, self.name, self.side, self.geo, self.rigGroup)

        return {'rigGroup': self.rigGroup,
                'joints': jointsList,
                'controls': controlList}

def connectBindPreMatrix(joints, skinClusterNode, jointInfCount):

    for n in range(jointInfCount, jointInfCount+len(joints)):

        jointNode = joints[n-jointInfCount]
        jointParent = Nodes.getParent(jointNode)

        spaceNode = Nodes.replaceNodeType(jointNode, Settings.offNodeSuffix)
        if Nodes.exists(spaceNode):
            Nodes.setTrs(spaceNode)
        jointParent = Nodes.getParent(jointNode)
        compensateNode = Nodes.replaceNodeType(jointNode, Settings.scaleCompensateNode)
        if Nodes.exists(compensateNode):
            Nodes.setParent(compensateNode, jointParent)
            mc.parent(jointNode, compensateNode, r=True)
            jointParent = compensateNode
        
        mc.connectAttr('%s.worldInverseMatrix[0]'%jointParent,
                       '%s.bindPreMatrix[%s]'%(skinClusterNode, n))

def getDeformGeo(driver):

    if driver.split('_')[-1] != 'deform':
        driver = driver.split('|')[-1]+'_deform'

    return driver

def createBlendshape(driver, name, side, geo, rigGroup):

    driver = getDeformGeo(driver)

    blendshapeName = Nodes.createName(component=name, side=side, element='deformTweak', nodeType='blendshape')[0]
    if not Nodes.exists(driver):
        mc.duplicate(geo, name=driver)
        mc.parent(driver, rigGroup)
        mc.setAttr('{}{}'.format(driver, '.v'), 0)
    if mc.objExists(blendshapeName):
        mc.delete(blendshapeName)
    mc.blendShape(driver, geo, w=[(0, 1)], name=blendshapeName, foc=True)

def addCompAttrs(driver, name, side, geo, rigGroup):
    
    driver = getDeformGeo(driver)

    for v, attrVal in enumerate([name, side, geo, rigGroup]):
        attrName = ['name', 'side', 'geo', 'rigGroup'][v]
        attr = driver+'.'+attrName
        Nodes.addAttr(attr, at='string', dv=attrVal)

def getCompAttrs(driver):
    
    driver = getDeformGeo(driver)

    attrVals = list()
    for attrName in ['name', 'side', 'geo', 'rigGroup']:
        attr = '%s.%s'%(driver, attrName)
        if not Nodes.exists(attr):
            mc.warning('Target geo for Deform Tweak not found: %s'%driver)
        else:
            attrVal = mc.getAttr(attr)
            if attrVal == '':
                attrVal = None
            attrVals.append(attrVal)

    return attrVals