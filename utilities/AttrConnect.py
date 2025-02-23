# Attr Connect

import maya.cmds as mc

from bear.system import Settings
from bear.utilities import Tools
from bear.utilities import Nodes

def connectAttr(sourceNode, targetNode, sourceAttrName, targetAttrName=None, defaultValue=True, attrIsKeyable=True, hideTargetAttr=False):
    
    # needs more work
    if not targetAttrName:
        targetAttrName = sourceAttrName

    if not mc.objExists(sourceNode+'.'+sourceAttrName):
        attrType = mc.attributeQuery(targetAttrName, n=targetNode, at=True)
        mc.addAttr(sourceNode, ln=sourceAttrName, at=attrType, k=True, dv=defaultValue)
    if not mc.objExists(targetNode+'.'+targetAttrName):
        attrType = mc.attributeQuery(sourceAttrName, n=sourceNode, at=True)
        mc.addAttr(targetNode, ln=targetAttrName, at=attrType, k=True, dv=defaultValue)
    if not attrIsKeyable:
        mc.setAttr('%s.%s'%(sourceNode, sourceAttrName), keyable=False)
        mc.setAttr('%s.%s'%(sourceNode, sourceAttrName), channelBox=True)
        
    mc.connectAttr('%s.%s'%(sourceNode, sourceAttrName), '%s.%s'%(targetNode, targetAttrName))

    if hideTargetAttr:
        mc.setAttr(targetNode+'.'+targetAttrName, channelBox=False, k=False)

def copyAttr(sourceNode, targetNode, attr=None, uniqueAttr=None, hideSourceAttr=False, connect=True, ignoreStringAttrs=False):
    
    if attr == 'displaySwitch' or attr == 'componentType':
        return
    if attr == None:
        attrList = mc.listAttr(sourceNode, userDefined=True)
    else:
        attrList = [attr]

    if attrList == None:
        return
    for attr in attrList:
        if uniqueAttr:
            newAttr = uniqueAttr
        else:
            newAttr = attr
        sourceAttr = '%s.%s'%(sourceNode, attr)
        
        if sourceAttr != None:
            if mc.objExists(sourceAttr):
                if mc.getAttr(sourceAttr, lock=True):
                    Nodes.addAttrTitle(targetNode, newAttr)
                else:
                    attrNode = targetNode+'.'+newAttr
                    if not mc.objExists(attrNode):
                        attrType = mc.attributeQuery(attr, n=sourceNode, at=True)
                        if attrType == 'typed' and ignoreStringAttrs:
                            continue
                        attrValue = mc.getAttr(sourceAttr)
                        minExists = mc.attributeQuery(attr, n=sourceNode, minExists=True)
                        maxExists = mc.attributeQuery(attr, n=sourceNode, maxExists=True)
                        minValue = mc.attributeQuery(attr, n=sourceNode, min=True)[0] if minExists else 0
                        maxValue = mc.attributeQuery(attr, n=sourceNode, max=True)[0] if maxExists else 1
                        isKeyable = mc.attributeQuery(attr, n=sourceNode, keyable=True)
                        niceName = mc.attributeQuery(attr, n=sourceNode, niceName=True)
                        if mc.attributeQuery(attr, n=sourceNode, enum=True):
                            enums = mc.attributeQuery(attr, n=sourceNode, listEnum=True)
                            if enums == None:
                                continue
                            else:
                                enums = enums[0]
                            mc.addAttr(targetNode, at='enum', ln=newAttr, nn=niceName, 
                                        k=isKeyable, 
                                        enumName=enums, 
                                        dv=attrValue)
                        elif minExists and maxExists:
                            mc.addAttr(targetNode, at=attrType, ln=newAttr, nn=niceName, dv=attrValue, 
                                    hasMinValue=minExists, 
                                    minValue=minValue, 
                                    hasMaxValue=maxExists, 
                                    maxValue=maxValue,
                                    k=isKeyable)
                        elif minExists:
                            mc.addAttr(targetNode, at=attrType, ln=newAttr, nn=niceName, dv=attrValue, 
                                    hasMinValue=minExists, 
                                    minValue=minValue,
                                    k=isKeyable)
                        elif maxExists:
                            mc.addAttr(targetNode, at=attrType, ln=newAttr, nn=niceName, dv=attrValue, 
                                    hasMaxValue=maxExists, 
                                    maxValue=maxValue,
                                    k=isKeyable)
                        else:
                            mc.addAttr(targetNode, at=attrType, ln=newAttr, nn=niceName, dv=attrValue,
                                    k=isKeyable)
                        if not isKeyable:
                            mc.setAttr(targetNode+'.'+newAttr, cb=True)
                    if connect and not Nodes.isConnected(sourceNode, customAttrName=attr):
                        mc.connectAttr('%s.%s'%(targetNode, newAttr), sourceAttr)
                    if hideSourceAttr:
                        mc.setAttr(sourceAttr, keyable=False)

    return '%s.%s'%(targetNode, newAttr)

def multiGroupConnect(sourceNodeList,
                      targetNode,
                      skipAttrNames=[],
                      skipAttrTerms=[],
                      uniqueAttr=None):
    # uniqueAttr is WIP

    for sourceNode in sourceNodeList:
        attrList = [x for x in mc.listAttr(sourceNode, userDefined=True) if not x in skipAttrNames]
        for attr in attrList:
            for skipAttrTerm in skipAttrTerms:
                if skipAttrTerm in attr:
                    attrList.remove(attr)

        if attrList != None:
            for attr in attrList:
                if attr == 'side':
                    continue
                attrNode = targetNode+'.'+attr
                srcAttrNode = '%s.%s'%(sourceNode, attr)
                if not mc.objExists(attrNode) or uniqueAttr:
                    if attr == Settings.spaceAttrName:
                        copyAttr(sourceNode, targetNode, attr, uniqueAttr=Nodes.replaceNodeType(targetNode).capitalize())
                    else:
                        copyAttr(sourceNode, targetNode, attr, uniqueAttr=uniqueAttr)
                else:
                    if not Nodes.isConnected(sourceNode, customAttrName=attr) and not mc.getAttr(srcAttrNode, lock=True):
                        mc.connectAttr(attrNode, srcAttrNode)
    
def performanceSwitch(groupNodeList, 
                        parentNode, 
                        rigGroup=None, 
                        name='face', 
                        parentStaticNodes=True, 
                        skipNode='body'):

    if rigGroup != None:
        Nodes.addAttrTitle(rigGroup, 'performance')

    staticGroupNodeList = list()
    groupNodeList = [groupNode for groupNode in groupNodeList if mc.objExists(groupNode)]
    for g, groupNode in enumerate(groupNodeList):
        if mc.objExists(groupNode):
            parentGroupNode = mc.listRelatives(groupNode, parent=True)[0]
            geoNodeList = mc.listRelatives(groupNode, children=True, type='transform')
            staticGeoNodeList = list()
            for geoNode in geoNodeList:
                staticGeoNode = '_'.join([Nodes.replaceNodeType(geoNode), 'static', Settings.templateSuffix])
                if not mc.objExists(staticGeoNode):
                    staticGeoNode = mc.rename(mc.duplicate(geoNode)[0], staticGeoNode)
                    staticGeoNodeList.append(staticGeoNode)
            if staticGeoNodeList != []:
                staticGroupNode = mc.group(staticGeoNodeList, name='_'.join([groupNode, 'static']))
                mc.parent(staticGroupNode, parentGroupNode)
                Tools.parentScaleConstraint(parentNode, staticGroupNode)

    if rigGroup != None:

        switchAttrName = 'activate'+name.capitalize()
        switchAttr = '%s.%s'%(rigGroup, switchAttrName)
        if not mc.objExists(switchAttr):
            mc.addAttr(rigGroup, ln=switchAttrName, at='bool', k=False, dv=True)
            mc.setAttr(switchAttr, channelBox=True)
        if staticGroupNodeList != []:
            for g, groupNode in enumerate(groupNodeList):
                if mc.objExists(groupNode):
                    for n, node in enumerate([staticGroupNodeList[g], groupNode]):
                        for v in [n, 1-n]:
                            mc.setDrivenKeyframe('%s.visibility'%node, cd=switchAttr, dv=v, v=1 if v == n else 0, itt='linear', ott='linear')
        try:
            mc.connectAttr(switchAttr, '%s.visibility'%rigGroup)
        except:
            'Connection already exists: %s, %s' % (switchAttr, '%s.visibility'%rigGroup)

        # frozen state
        allFrozenNodes = list()
        for node in groupNodeList + [rigGroup]:
            allFrozenNodes.append(node)
            allFrozenNodes.extend(Tools.getAllRelatedChildNodes(node))
        for frozenNode in allFrozenNodes:
            if mc.objExists(frozenNode):
                if not 'static' in frozenNode and not 'faceDisplaySwitch' in frozenNode and not skipNode in frozenNode:
                    for attr in ['frozen']: # nodeState is outdated and produces cycle errors
                        frozenAttr = '%s.%s'%(frozenNode, attr)
                        if mc.listConnections(frozenAttr) == None:
                            for n in range(2):
                                mc.setDrivenKeyframe(frozenAttr, cd=switchAttr, dv=n, v=0 if n == 1 else 1, itt='linear', ott='linear')

    if parentStaticNodes and staticGroupNodeList != []:
        mc.parent(staticGroupNodeList, rigGroup)

    return staticGroupNodeList

def connectPerformanceSwitch(rigGroupList, switchNode, name='extra'):

    Nodes.addAttrTitle(switchNode, 'performance')
    switchAttrName = 'activate'+name[0].capitalize()+name[1:]
    switchAttr = '%s.%s'%(switchNode, switchAttrName)
    if not mc.objExists(switchAttr):
        mc.addAttr(switchNode, ln=switchAttrName, at='bool', k=False, dv=True)
        mc.setAttr(switchAttr, channelBox=True)
    for rigGroup in rigGroupList:
        targetAttr = None
        for attr in mc.listAttr(rigGroup, userDefined=True):
            if 'activate' in attr:
                targetAttr = attr
        if targetAttr != None:
            if not Nodes.isConnected(switchAttr, '%s.%s'%(rigGroup, targetAttr)):
                mc.connectAttr(switchAttr, '%s.%s'%(rigGroup, targetAttr))