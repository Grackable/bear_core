# Ears

import maya.cmds as mc

from bear.system import Generic
from bear.system import Settings
from bear.system import ConnectionHandling
from bear.utilities import Nodes
from bear.utilities import AttrConnect
from bear.components.basic import Single

class Build(Generic.Build):

    def __init__(self,
                name='ear',
                controlCount=1,
                extraControlCount=0,
                parentNode=Nodes.createName('head', nodeType=Settings.controlSuffix)[0],
                displaySwitch='faceDisplaySwitch',
                *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.controlCount = controlCount
        self.extraControlCount = extraControlCount
        self.parentNode = Nodes.getPivotCompensate(parentNode)
        self.displaySwitch = displaySwitch

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, 'auto', definition)
        if definition:
            return {'guideGroup': guideGroup}

        guide = Single.Build(name=self.name,
                                side=Settings.leftSide,
                                count=self.controlCount,
                                parentNode=guideGroup,
                                size=1).createGuide()

        for guidePivot in  guide['guides']:
            mc.rotate(0, 90, 0, guidePivot)
        Nodes.setParent(guide['guideGroup'], guideGroup)

        guide = Single.Build(name=self.name,
                                side=Settings.leftSide,
                                element='extra',
                                count=self.extraControlCount,
                                parentNode=guideGroup,
                                size=1).createGuide()
        Nodes.setParent(guide['guideGroup'], guideGroup)

        return {'guideGroup': guideGroup}

    def createRig(self):

        rigGroup = super(Build, self).createRig(self.name, 'auto')

        self.parentNode = ConnectionHandling.inputExists(self.parentNode)

        earRigs = list()
        for side in [Settings.leftSide, Settings.rightSide]:
            earRig = Single.Build(name=self.name,
                                    side=side,
                                    chainParented=True,
                                    parentNode=self.parentNode,
                                    count=self.controlCount).createRig()
            earRigs.append(earRig)
            Nodes.setParent(earRig['rigGroup'], rigGroup)

            earRig = Single.Build(name=self.name,
                                    side=side,
                                    element='extra',
                                    parentNode=self.parentNode,
                                    count=self.extraControlCount).createRig()
            earRigs.append(earRig)
            Nodes.setParent(earRig['rigGroup'], rigGroup)

        AttrConnect.multiGroupConnect([earRig['rigGroup'] for earRig in earRigs], rigGroup)

        return {'rigGroup': rigGroup, 
                'earRigs': earRigs}