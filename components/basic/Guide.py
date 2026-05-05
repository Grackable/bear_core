# Guide

import maya.cmds as mc

from bear.system import Settings
from bear.utilities import Nodes
from bear.components.basic import Control
from bear.components.basic import Shapes

def createGuide(node=None,
                component=None,
                size=10,
                side=None,
                element=None,
                specific=None,
                indices=None,
                alignAxis=None,
                hasGuideShape=True,
                hasAttrs=True,
                hasPivotAttr=True,
                hasParentAttr=True,
                hasSpaceAttr=True,
                hasShapeAttrs=True,
                hasGuidePivot=True,
                hasPivotShapeSizeAttr=True,
                hasLockAndHideAttrs=True,
                hasTransformLimits=True,
                hasRotateOrder=True,
                pivotColor='Green',
                indexFill=2,
                showLocalAxis=False,
                parentNode=None,
                lockPivotNodeScale=True):

    pivotNode = None
    
    if hasGuidePivot:
        
        pivot = Control.createControl(node=node,
                                component=component, 
                                shape='Square', 
                                color=pivotColor,
                                side=side, 
                                element=element,
                                specific=specific,
                                indices=indices,
                                indexFill=indexFill,
                                size=size*0.1, 
                                isGuide=True)

        if hasPivotShapeSizeAttr:
            pivotShapeSizeAttr = pivot['control']+'.pivotShapeSize'
            Nodes.addAttr(pivotShapeSizeAttr, dv=size*0.1, minVal=0, d=True, k=True)
            Nodes.addAttr(pivot['control']+'.pivotInitialShapeSize', dv=size*0.1, minVal=0, d=False, k=False)
        
        if lockPivotNodeScale:
            Nodes.lockAndHideAttributes(pivot['control'], s=[True, True, True])

        pivotNode = pivot['control']
        if parentNode:
            Nodes.setParent(pivotNode, parentNode)
        else:
            Nodes.setParent(pivotNode, 'world')
        if pivot['offset']:
            mc.delete(pivot['offset'])

        if Nodes.getShapeType(pivotNode) == 'locator':
            for axis in 'XYZ':
                mc.setAttr('%s.localScale%s' % (Nodes.getShapes(pivotNode)[0], axis), size*0.1)      
    
    if showLocalAxis:
        mc.setAttr('%s.displayLocalAxis'%node, True)

    if hasGuideShape:
        guide = Control.createControl(node=node,
                                component=component,
                                size=1,
                                side=side,
                                element=element,
                                specific=specific,
                                indices=indices,
                                indexFill=indexFill,
                                color='Default',
                                parentDirection='ControlToNode',
                                alignAxis=alignAxis,
                                shape='Circle',
                                offset=[0, 0, 0],
                                mirrorScale=[-1, -1, -1],
                                isGuide=True,
                                createShapes=False,
                                controlNodeType=Settings.guideShapeSuffix,
                                offNodeType=Settings.guideOffSuffix)

        guideOffNode = guide['offset']
        Nodes.lockAndHideAttributes(guideOffNode, t=[True, True, True], r=[True, True, True], s=[True, True, True], v=True)

        Nodes.setParent(guide['offset'], pivotNode)

        mc.setAttr('%s.sx' % (guide['control']), size)
        mc.setAttr('%s.sy' % (guide['control']), size)
        mc.setAttr('%s.sz' % (guide['control']), size)
        
        Nodes.addAttrTitle(guide['control'], 'guide')
        
        if hasAttrs:
            if hasShapeAttrs:
                mc.addAttr(guide['control'], at='enum', ln='shape', k=True, enumName=':'+':'.join(Settings.shapes))
                mc.addAttr(guide['control'], at='enum', ln='color', k=True, enumName=':'+':'.join(['Default']+Settings.colors))
            mc.addAttr(guide['control'], at='bool', ln='secondaryDefaultColor', k=True, dv=False)
            mc.addAttr(guide['control'], at='bool', ln='isVisible', k=True, dv=True)
        
        if hasPivotAttr:
            mc.addAttr(guide['control'], at='bool', ln='hasPivotControl', k=True, dv=False)

        if hasParentAttr:
            mc.addAttr(guide['control'], dt='string', ln='parentNode')
            mc.addAttr(guide['control'], dt='string', ln='orientNode')
            mc.addAttr(guide['control'], dt='string', ln='parentType')
            mc.addAttr(guide['control'], at='bool', ln='inheritScale', k=True, dv=True)
            mc.setAttr('%s.parentNode'%guide['control'], '', type='string')
            mc.setAttr('%s.orientNode'%guide['control'], '', type='string')
            mc.setAttr('%s.parentType'%guide['control'], '', type='string')

        if hasLockAndHideAttrs:
            for trs in 'trs':
                for axis in 'xyz':
                    mc.addAttr(guide['control'], at='bool', ln='lockAndHide%s%s'%(trs.upper(), axis), k=True, dv=False)

        if hasTransformLimits:
            mc.addAttr(guide['control'], at='bool', ln='hasTransformLimits', k=True, dv=False)

        if hasRotateOrder:
            mc.addAttr(guide['control'], at='bool', ln='hasRotateOrder', k=True, dv=False)

        if hasSpaceAttr:
            mc.addAttr(guide['control'], dt='string', ln='spaceNodes')
            mc.setAttr('%s.spaceNodes'%guide['control'], ',', type='string')
            mc.addAttr(guide['control'], dt='string', ln='spaceNames')
            mc.setAttr('%s.spaceNames'%guide['control'], ',', type='string')
        
        mc.setAttr('%s.overrideEnabled'%guide['control'], True)
        mc.setAttr('%s.overrideRGBColors'%guide['control'], True)
        greyVal = 0.6
        mc.setAttr('%s.overrideColorR'%guide['control'], greyVal)
        mc.setAttr('%s.overrideColorG'%guide['control'], greyVal)
        mc.setAttr('%s.overrideColorB'%guide['control'], greyVal)
    else:
        guide = None
    
    return {'pivot': pivotNode,
            'control': guide['control'] if guide != None else None,
            'offset': guideOffNode if guide != None else None}