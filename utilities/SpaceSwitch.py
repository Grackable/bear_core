# SpaceSwitch

import maya.cmds as mc

from bear.system import ConnectionHandling
from bear.system import Settings
from bear.utilities import AddNode
from bear.utilities import Nodes

Settings.loadSettings()

def createSpaceSwitch(offNode,
                      sourceObjs=None,
                      switchNames=None,
                      translation=True,
                      rotation=True,
                      scale=False,
                      defaultSpace=None,
                      maintainOffset=True,
                      spaceAttrName=None):
    
    ctrlNode = Nodes.replaceNodeType(offNode, Settings.controlSuffix)
    spaceNode = Nodes.replaceNodeType(offNode, Settings.spaceNodeSuffix)
    
    if spaceAttrName == None:
        spaceAttrName = Settings.spaceAttrName

    Nodes.addAttrTitle(ctrlNode, 'spaceSwitch')

    if not mc.objExists(spaceNode):
        spaceNode = AddNode.inbetweenNode(offNode, nodeType=Settings.spaceNodeSuffix, lockScale=True)

    sourceObjList = [] if sourceObjs == None else sourceObjs
    switchNameList = [] if switchNames == None else switchNames
    if type(sourceObjList) != list:
        sourceObjList = [sourceObjList]
    if type(switchNameList) != list:
        switchNameList = [switchNameList]

    sourceObjList = [Nodes.getPivotCompensate(x) if Nodes.getNodeType(x) != Settings.offNodeSuffix else x for x in sourceObjList]

    if not mc.objExists(ctrlNode+'.'+spaceAttrName):
        mc.addAttr(ctrlNode, at='enum', ln=spaceAttrName, k=True, enumName=':'.join(switchNameList))

    for a in (x+y for x in 'tr' for y in 'xyz'):
        try:
            mc.setAttr('%s.%s' % (spaceNode, a), lock=False)
        except:
            pass
    
    spaceLocList = []

    for p, sourceObj in enumerate(sourceObjList):
        
        sourceObj = ConnectionHandling.inputExists(sourceObj)

        specific = Nodes.getSpecific(offNode)
        if specific:
            specific = Nodes.camelCase(specific+'_'+sourceObj)
        else:
            specific = Nodes.camelCase(sourceObj)
        
        spaceLoc = Nodes.createName(component=Nodes.getComponent(offNode), 
                                    side=Nodes.getSide(offNode), 
                                    indices=Nodes.getIndices(offNode), 
                                    element=Nodes.getElement(offNode), 
                                    specific=specific, 
                                    nodeType=Settings.spaceLocSuffix)[0]
        if not mc.objExists(spaceLoc):
            spaceLoc = AddNode.emptyNode(component=Nodes.getComponent(offNode), 
                                    side=Nodes.getSide(offNode), 
                                    indices=Nodes.getIndices(offNode), 
                                    element=Nodes.getElement(offNode), 
                                    specific=specific, 
                                    nodeType=Settings.spaceLocSuffix)
            Nodes.alignObject(spaceLoc, ctrlNode)
    
            mc.parent(spaceLoc, sourceObj)
    
        spaceLocList.append(spaceLoc)

    cntList = []
    
    if spaceLocList != []:
        
        if translation:
            pointCnt = mc.pointConstraint(spaceLocList, spaceNode, mo=maintainOffset)[0]
            cntList.append(pointCnt)
        if rotation:
            orientCnt = mc.orientConstraint(spaceLocList, spaceNode, mo=maintainOffset)[0]
            cntList.append(orientCnt)
        if scale:
            scaleCnt = mc.scaleConstraint(spaceLocList, spaceNode, mo=maintainOffset)[0]
            cntList.append(scaleCnt)

    nodeDrv = '%s.%s' % (ctrlNode, spaceAttrName)
    
    for p, spaceLoc in enumerate(spaceLocList):

        for cnt in cntList:

            targetDrv = '.'.join([cnt, spaceLoc.split(':')[-1]]) + 'W' + str(p)
            
            mc.setDrivenKeyframe(targetDrv, cd=nodeDrv, dv=p, v=1)

            for s in range(len(spaceLocList)):

                if s != p:

                    mc.setDrivenKeyframe(targetDrv, cd=nodeDrv, dv=s, v=0)

            if len(spaceLocList) == 1:

                mc.setDrivenKeyframe(targetDrv, cd=nodeDrv, dv=-1, v=0)
    
    if defaultSpace != None:
        mc.setAttr('%s.%s' % (ctrlNode, spaceAttrName), switchNames.index(defaultSpace))

    return spaceNode