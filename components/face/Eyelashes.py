# Eyelashes

import maya.cmds as mc

from bear.system import Generic
from bear.system import Guiding
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.system import MessageHandling
from bear.utilities import VisSwitch
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import NodeOnVertex
from bear.utilities import Nodes
from bear.components.basic import Curve

class Build(Generic.Build):

    def __init__(self,
                name='eyelash',
                eyeName='eye',
                pointCountUpper=9,
                pointCountLower=9,
                geoNode=Nodes.createName('skin', nodeType=Settings.geoNodeSuffix)[0],
                eyeballGuide=Nodes.createName('eye', Settings.leftSide, element='ball', nodeType=Settings.guidePivotSuffix)[0],
                skeletonParent=None,
                displaySwitch='faceDisplaySwitch',
                *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.eyeName = eyeName
        self.pointCountUpper = pointCountUpper
        self.pointCountLower = pointCountLower
        self.geoNode = geoNode
        self.eyeballGuide = eyeballGuide if eyeballGuide != '' else None
        self.skeletonParent = skeletonParent
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, 'auto', definition)
        if definition:
            return {'guideGroup': guideGroup}

        self.eyeballGuide = ConnectionHandling.inputExists(self.eyeballGuide)
        
        for n, elementName in enumerate(['upper', 'lower']):
            pointCount = [self.pointCountUpper, self.pointCountLower][n]
            if not pointCount:
                continue
            curveGuide = Curve.Build(component=self.name,
                                        element=elementName, 
                                        side=Settings.leftSide,
                                        curveType='nurbsCurve', 
                                        controlCount=pointCount,
                                        jointCount=pointCount,
                                        hasJointGuides=True, 
                                        squashing=False,
                                        scaling=False,
                                        upnode=self.eyeballGuide,
                                        upAxis='y',
                                        lengthAxis='x',
                                        size=1).createGuide(definition)
            mc.parent(curveGuide['guideGroup'], guideGroup)
            for c, curvePivot in enumerate(curveGuide['guidePivots']):
                mc.move(-4+c, [2, -2][n], 0, curvePivot)
            mc.delete(curveGuide['guideOffsets'])

            for side in [Settings.leftSide, Settings.rightSide]:
                [ConnectionHandling.addOutput(guideGroup, Nodes.createName(self.name, side, Settings.skinJointSuffix, element=elementName, indices=n)[0]) \
                    for n in range(pointCount)]

        return {'guideGroup': guideGroup}

    def createRig(self):

        eyelashesUpperGuide = Nodes.createName(self.name, Settings.leftSide, Settings.guideCurveSuffix, element='upper')[0]
        if not mc.objExists(eyelashesUpperGuide):
            eyelashesUpperGuide = None
        eyelashesLowerGuide = Nodes.createName(self.name, Settings.leftSide, Settings.guideCurveSuffix, element='lower')[0]
        if not mc.objExists(eyelashesLowerGuide):
            eyelashesLowerGuide = None

        rigGroup = super(Build, self).createRig(self.name, 'auto')
        mc.setAttr('%s.inheritsTransform'%rigGroup, False)

        pinNodes = list()
        jointNodes = list()

        if mc.objExists(self.geoNode):
            bshNodes = Nodes.getInputNodes(self.geoNode, inputType='blendShape')[0]
            if bshNodes != []:
                mc.setAttr('%s.envelope'%bshNodes[0], 0)

        eyelashesGuides = [x for x in [eyelashesUpperGuide, eyelashesLowerGuide] if x != None]

        for side in [Settings.leftSide, Settings.rightSide]:

            for eyelashesGuide in eyelashesGuides:
                
                cvCount = Tools.getCvCount(eyelashesGuide)
                
                upperlidName = 'upperlid' if Nodes.getElement(eyelashesGuide) == 'upper' else 'lowerlid'
                
                upperlidControl = Nodes.createName(self.eyeName, side, Settings.controlSuffix, element=upperlidName)[0]
                if mc.objExists(upperlidControl):
                    Nodes.addAttrTitle(upperlidControl, 'eyelash')
                    Nodes.addAttr(upperlidControl+'.tilt')
                    
                    if not mc.objExists(self.geoNode):
                        MessageHandling.warning('geo node does not exist, eyelash proximity pin creation skipped')
                        continue
                        
                    offNodes = list()
                    for c in range(cvCount):
                        offNode = AddNode.emptyNode(component=self.name, side=side, indices=c, element=Nodes.getElement(eyelashesGuide), nodeType=Settings.offNodeSuffix)
                        guidePivot = Nodes.createName(self.name, 
                                                    Settings.leftSide, 
                                                    Settings.guidePivotSuffix, 
                                                    indices=c, 
                                                    element=Nodes.getElement(eyelashesGuide))[0]
                        jointGuide = Nodes.createName(self.name, 
                                                    Settings.leftSide, 
                                                    Settings.guidePivotSuffix, 
                                                    indices=c, 
                                                    element=Nodes.getElement(eyelashesGuide), 
                                                    specific='joint')[0]
                        Nodes.alignObject(guidePivot, jointGuide)
                        if side == Settings.rightSide:
                            guidePivot = Guiding.convertGuide(guidePivot, mirror=True)[0]
                        Nodes.alignObject(offNode, guidePivot)
                        offNodes.append(offNode)
                    
                    NodeOnVertex.proximityPin(self.geoNode, offNodes)

                    for c in range(cvCount):
                        pinLoc = offNodes[c]
                        
                        jointNode = AddNode.jointNode(pinLoc, 
                                                        side=side, 
                                                        component=self.name, 
                                                        indices=c, 
                                                        element=Nodes.getElement(eyelashesGuide),
                                                        skeletonParent=self.skeletonParent)
                        jointNodes.append(jointNode)
                        mc.parent(pinLoc, rigGroup)
                        pinNodes.append(pinLoc)

                        tiltNode = AddNode.inbetweenNode(pinLoc, 'tilt')
                        mc.connectAttr('%s.tilt'%upperlidControl, '%s.rx'%tiltNode)
        
        VisSwitch.connectVisSwitchGroup(jointNodes, rigGroup, displayAttr='jointDisplay')

        if mc.objExists(self.geoNode) and bshNodes != []:
            mc.setAttr('%s.envelope'%bshNodes[0], 1)
        
        self.cleanup(Nodes.replaceNodeType(rigGroup, 'guide'), trashGuides=True, removeRightGuides=True, hierarchy=False, display=False, selectionSets=False)

        return {'rigGroup': rigGroup, 
                'joints': jointNodes}