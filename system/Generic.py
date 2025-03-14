# Generic

import maya.cmds as mc

from bear.system import Settings
from bear.system import ConnectionHandling
from bear.system import Guiding
from bear.utilities import AddNode
from bear.utilities import Nodes
from bear.utilities import SpaceSwitch
       
class Build(object):
    
    def __init__(self, *args, **kwargs):
        
        pass

    def createGuide(self, component=None, side=None, definition=False, element=None, *args):
        
        def setDefState():
            defAttrName = 'readyForRigBuild'
            defAttr = guideGroup+'.'+defAttrName
            if not mc.objExists(defAttr):
                mc.addAttr(guideGroup, ln=defAttrName, at='bool', k=False)
            mc.setAttr(defAttr, lock=False)
            mc.setAttr(defAttr, not definition)
            mc.setAttr(defAttr, lock=True)
            
        guideGroup = Nodes.createName(component, side, 'guide', element=element)[0]
        
        if mc.objExists(guideGroup):
            setDefState()
            return guideGroup
        
        guideGroup = AddNode.compNode(component, side, 'guide', element=element, parentNode=Settings.guideRoot, root=Settings.guideRoot)
        setDefState()
        Nodes.applyGlobalScale(guideGroup, [guideGroup], lock=True)
        
        return guideGroup
    
    def createRig(self, component=None, side=None, element=None, *args):

        rigGroup = AddNode.compNode(component, side, 'rig', element=element, parentNode=Settings.rigRoot, root=Settings.rigRoot)

        return rigGroup

    def postRig(self, guideGroup):

        rigGroup = Nodes.replaceNodeType(guideGroup, 'rig')
        
        for guideNode in Nodes.getAllChildren(guideGroup, nodeType=Settings.guideShapeSuffix):

            guideData = Guiding.getGuideAttr(guideNode)

            parentNode = None
            orientNode = None
            parentType = None
            inheritScale = None
            spaceNodes = None
            spaceNames = None

            if 'parentNode' in guideData:
                parentNode = guideData['parentNode']
            if 'orientNode' in guideData:
                orientNode = guideData['orientNode']
            if 'parentType' in guideData:
                parentType = guideData['parentType']
            if 'inheritScale' in guideData:
                inheritScale = guideData['inheritScale']
            if 'spaceNodes' in guideData:
                spaceNodes = guideData['spaceNodes']
                if '' in spaceNodes:
                    spaceNodes = None
            if 'spaceNames' in guideData:
                spaceNames = guideData['spaceNames']
                if '' in spaceNames:
                    spaceNames = None

            controlNode = Nodes.replaceNodeType(guideNode, Settings.controlSuffix)
            jointNode = Nodes.replaceNodeType(guideNode, Settings.skinJointSuffix)
            offNode = Nodes.replaceNodeType(guideNode, Settings.offNodeSuffix)
            side = Nodes.getSide(controlNode)

            if parentNode:
                # we add skeleton parent
                if Nodes.exists(jointNode):
                    Nodes.addSkeletonParentAttr(jointNode, parentNode)
                # we look for pivot control since we want to parent to that one instead if it exists
                parentNode = Nodes.getPivotCompensate(parentNode)

            # because some components have no guide for right side, we check if
            # control exists to apply same parents on right side
            controlNodes = [controlNode]
            offNodes = [offNode]
            if side and Nodes.componentIsAutoSided(guideGroup):
                rightSideControlNode = Nodes.replaceSide(controlNode, Settings.rightSide)
                if mc.objExists(rightSideControlNode):
                    controlNodes = [controlNode, rightSideControlNode]
                    offNodes = [offNode, Nodes.replaceSide(offNode, Settings.rightSide)]

            # parent connections
            for c, controlNode in enumerate(controlNodes):
                ConnectionHandling.parentConnection(controlNode, offNodes[c], rigGroup, parentNode, orientNode, parentType, inheritScale)

            # space switch
            if spaceNodes:
                SpaceSwitch.createSpaceSwitch(offNode, spaceNodes, switchNames=spaceNames if spaceNames else spaceNodes)

        # joint and control selection sets

        joints = [x for x in Nodes.getAllChildren(rigGroup) if Nodes.getNodeType(x) == Settings.skinJointSuffix and Nodes.getShapeType(x) == 'joint']
        controls = [x for x in Nodes.getAllChildren(rigGroup) if Nodes.getNodeType(x) == Settings.controlSuffix]

        setNodesTypes = list()
        if joints:
            setNodesTypes.append(Settings.jointSetSuffix)
        if controls:
            setNodesTypes.append(Settings.controlSetSuffix)

        for setNodeType in setNodesTypes:
            
            mainSetNode = Nodes.createName(nodeType=setNodeType)[0]
            if not Nodes.exists(mainSetNode):
                AddNode.setNode(nodeType=setNodeType)

            setName = Nodes.replaceNodeType(rigGroup, setNodeType)
            if mc.objExists(setName):
                mc.delete(setName)
            nodes = joints if setNodeType == Settings.jointSetSuffix else controls
            isCollection = False
            if mc.objExists('%s.componentType'%guideGroup):
                if mc.getAttr('%s.componentType'%guideGroup) == 'Collection':
                    isCollection=True
                    nodes = []
            if len(nodes) > 0 or isCollection:
                setNode = AddNode.setNode(nodes,
                                            component=Nodes.getComponent(rigGroup),
                                            side=Nodes.getSide(rigGroup),
                                            nodeType=setNodeType)
                guideGroup = Nodes.replaceNodeType(rigGroup, Settings.guideGroup)
                if isCollection:
                    subGuideGroups= Nodes.getChildren(guideGroup)
                    for subGuideGroup in subGuideGroups:
                        setChild = Nodes.createName(sourceNode=subGuideGroup, nodeType=setNodeType)[0]
                        if mc.objExists(setChild):
                            mc.sets(setChild, fe=setNode, edit=True)
                            mc.sets(setNode, fe=mainSetNode, edit=True)
                else:
                    parentGuideGroup = Nodes.getParent(guideGroup)
                    if Nodes.getComponentType(parentGuideGroup) == 'Collection':
                        setParent = Nodes.createName(sourceNode=parentGuideGroup, nodeType=setNodeType)[0]
                        if mc.objExists(setParent):
                            mc.sets(setNode, fe=setParent, edit=True)
                            mc.sets(setParent, fe=mainSetNode, edit=True)
                    else:
                        mc.sets(setNode, fe=mainSetNode, edit=True)

    def cleanup(self, guideGroup=None, trashGuides=True, removeRightGuides=False, hierarchy=True, display=True, selectionSets=True, lockAndHideNonKeyable=False):

        if trashGuides:

            trashSide = Settings.leftSide if Settings.leftSide == Settings.rightSide else Settings.rightSide
            
            for nodeType in [Settings.guidePivotSuffix, Settings.guideOffSuffix, Settings.guideShapeSuffix, Settings.dupNodeSuffix, Settings.guideCurveSuffix,
                             'guideParent', 'guideAim', 'guideAimOff', 'guideQuadParent', 'guideQuadAim', 'guideQuadAimOff']:
                nodeType = '_'+nodeType
                if guideGroup == None:
                    nodeList = mc.ls('*'+nodeType+'*', type='transform')[::]
                else:
                    nodeList = [x for x in Nodes.getAllChildren(guideGroup) if nodeType in x]
                for node in nodeList:
                    trashSuffix = node.split(nodeType)[1]
                    if trashSuffix != '' and trashSuffix != 'Off' and trashSuffix != 'Cls' and trashSuffix != 'MirScl' and trashSuffix != 'Crv' and trashSuffix != 'Srf':
                        if mc.objExists(node):
                            mc.delete(node)
                    if nodeType[1:] == Settings.dupNodeSuffix:
                        if mc.objExists(node):
                            mc.delete(node)
                if removeRightGuides:
                    nodeList = [x for x in nodeList if x[:2] == trashSide+'_' and Nodes.getNodeType(x) == Settings.guidePivotSuffix]
                    for node in nodeList:
                        if mc.objExists(node):
                            mc.delete(node)

        if hierarchy:

            for rootNode in [self.guideRoot, self.templateRoot, self.layoutRoot, self.rigRoot, 'guidelines']:
                if mc.objExists(rootNode):
                    if rootNode != self.rigRoot:
                        mc.hide(rootNode)
                    parentNode = Nodes.getParent(rootNode)
                    if parentNode != None:
                        if not parentNode == self.assetNode:
                            mc.parent(rootNode, self.assetNode)
                    else:
                        mc.parent(rootNode, self.assetNode)

        if display:

            for rootNode in [self.skinTemplateRoot, self.skinMeshRoot]:
                if mc.objExists(rootNode):
                    mc.hide(rootNode)

            for geometryNode in [self.geometryRoot, self.layoutRoot]:
                if mc.objExists(geometryNode):
                    mc.setAttr(geometryNode+'.freezeSelection', True)

        if selectionSets:

            for vertexSet in mc.ls('*_stickyVertices'):
                mc.delete(vertexSet)
        
        if lockAndHideNonKeyable:
            for controlNode in mc.ls('*'+'_'+Settings.controlSuffix, type='transform'):
                userAttrs = mc.listAttr(controlNode, userDefined=True)
                if not userAttrs:
                    continue
                for attrName in userAttrs:
                    if not mc.attributeQuery(attrName, node=controlNode, keyable=True) and not mc.getAttr(controlNode+'.'+attrName, lock=True):
                        Nodes.lockAndHideAttributes(controlNode, attrName=attrName)

        mc.currentTime(0)

        mc.select(clear=True)