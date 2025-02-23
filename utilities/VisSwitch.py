# VisSwitch

import maya.cmds as mc
import maya.mel as mel

from bear.utilities import Nodes
from bear.components.basic import Control

def parentVisSwitch(node=None,
                    name='displaySwitch',
                    side=None,
                    targetRigGroups=None,
                    geoDisplay=False,
                    parentNode=None,
                    parentType='Constraint',
                    alignAxis='-Z',
                    hasGuide=True):

    displaySwitchRig = Control.createControl(node=node,
                                                component=name,
                                                side=side,
                                                alignAxis=alignAxis,
                                                shape='Pyramid Needle',
                                                useGuideAttr=hasGuide,
                                                parentNode=parentNode,
                                                parentType=parentType)

    Nodes.lockAndHideAttributes(displaySwitchRig['control'], 
                                t=[True, True, True], 
                                r=[True, True, True],
                                s=[True, True, True], 
                                v=True)

    Nodes.addAttrTitle(displaySwitchRig['control'], 'display')

    attrList = (['allGeoDisplay'] if geoDisplay else []) + ['allControlDisplay', 'allSetupDisplay', 'allJointDisplay']

    for attr in attrList:
        if not mc.attributeQuery(attr, node=displaySwitchRig['control'], ex=True):
            mc.addAttr(displaySwitchRig['control'], at='bool', ln=attr, keyable=False, dv=True)
            if 'SetupDisplay' in attr:
                mc.setAttr(displaySwitchRig['control']+'.'+attr, False)
            elif 'JointDisplay' in attr:
                mc.setAttr(displaySwitchRig['control']+'.'+attr, False)
                mc.setAttr(displaySwitchRig['control']+'.'+attr, channelBox=True)
            else:
                mc.setAttr(displaySwitchRig['control']+'.'+attr, channelBox=True)

    for targetRigGroup in targetRigGroups:
            
        attrList = mc.listAttr(targetRigGroup, userDefined=True)
        
        if attrList != None: 
            
            visNameList = [x for x in attrList if 'ControlDisplay' in x or 'controlDisplay' in x or 'setupDisplay' in x or 'jointDisplay' in x]
        
            for visName in visNameList:
                
                visType = 'Control'
                visType = 'Setup' if ('setup' in visName or 'Setup' in visName) else visType
                visType = 'Joint' if ('joint' in visName or 'Joint' in visName) else visType
                visPfx = targetRigGroup.split('_rig')[0]
                visAttr = visPfx+'_'+visName

                if mc.attributeQuery('visGroup', node=targetRigGroup, ex=True):
                    visAttr = mc.getAttr('%s.visGroup'%targetRigGroup)+(visName[0].upper()+visName[1:])
    
                displayAttr = '%s.%s'%(displaySwitchRig['control'], visAttr)
                if not mc.objExists(displayAttr):
                    mc.addAttr(displaySwitchRig['control'], at='bool', ln=visAttr, keyable=False, dv=not 'IkLine' in visAttr)
                if visType == 'Setup':
                    mc.setAttr(displaySwitchRig['control'] + '.' + visAttr, True)
                elif visType == 'Joint':
                    mc.setAttr(displaySwitchRig['control'] + '.' + visAttr, True)
                else:
                    mc.setAttr(displaySwitchRig['control'] + '.' + visAttr, channelBox=True)
    
                targetVisAttr = displaySwitchRig['control']+'.'+visAttr
                sourceVisAttr = '%s.%s'%(targetRigGroup, visName)
    
                mel.eval("source channelBoxCommand; CBdeleteConnection \"%s\"" % sourceVisAttr)
    
                if mc.attributeQuery(visName, node=targetRigGroup, ex=True):
                    if not mc.getAttr(sourceVisAttr, lock=True):
                        Nodes.mulNode(targetVisAttr, 
                                    '%s.all%sDisplay'%(displaySwitchRig['control'], visType),
                                    sourceVisAttr)

    return displaySwitchRig

def connectVisSwitchGroup(sourceNodeList,
                          groupNode,
                          displayAttr=None,
                          visGroup=None,
                          simpleConnect=False,
                          forceConnection=False):

    Nodes.addAttrTitle(groupNode, 'display')

    if not simpleConnect:
        if not mc.attributeQuery(displayAttr, node=groupNode, ex=True):
            mc.addAttr(groupNode, at='bool', ln=displayAttr, dv=True, k=False)
            if 'setup' in displayAttr or 'joint' in displayAttr:
                mc.setAttr('%s.%s'%(groupNode, displayAttr), False)
            mc.setAttr('%s.%s'%(groupNode, displayAttr), channelBox=True)

    for sourceNode in sourceNodeList:

        if sourceNode != None:
            
            if simpleConnect:
                displayAttr = '%s%sDisplay' % (sourceNode.split('_')[0].capitalize(), 'Control')
                if not mc.attributeQuery(displayAttr, node=groupNode, ex=True):
                    mc.addAttr(groupNode, at='bool', ln=displayAttr, dv=True, keyable=True)

            nodeList = [sourceNode]
            if not simpleConnect:
                if not 'setup' in displayAttr and not 'joint' in displayAttr:
                    nodeList = mc.listRelatives(sourceNode, shapes=True)
                    if nodeList == None:
                        return

            for node in nodeList:
                if node != None:
                    visAttr = '%s.visibility' % node
                    if not mc.getAttr(visAttr, lock=True):
                        if forceConnection:
                            mc.connectAttr(groupNode + '.' + displayAttr, visAttr, f=True)
                        else:
                            if not Nodes.isConnected(node, customAttrName='visibility'):
                                mc.connectAttr(groupNode + '.' + displayAttr, visAttr)

    if visGroup != None:
        visGroupAttrName = 'visGroup'
        if not mc.attributeQuery(visGroupAttrName, node=groupNode, ex=True): 
            mc.addAttr(groupNode, dt='string', ln=visGroupAttrName)
            mc.setAttr('%s.%s'%(groupNode, visGroupAttrName), visGroup, type='string')