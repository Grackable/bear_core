# Script

from bear.system import Generic

class Build(Generic.Build):
    
    def __init__(self,
                    name='script',
                    fileName='script.py',
                    runOnBuildStep='rig',
                    useAssetFolder=True,
                    customFolder='',
                    createRigGroup=False,
                    *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.name = name
        self.fileName = fileName
        self.runOnBuildStep = runOnBuildStep
        self.useAssetFolder = useAssetFolder
        self.customFolder = customFolder
        self.createRigGroup = createRigGroup

    def createGuide(self, definition=False):
        
        guideGroup = super(Build, self).createGuide(self.name, None, definition=False)

        return {'guideGroup': guideGroup}

    def createRig(self):

        if self.createRigGroup:
            rigGroup = super(Build, self).createRig(self.name)
        else:
            rigGroup = None

        return {'rigGroup': rigGroup}