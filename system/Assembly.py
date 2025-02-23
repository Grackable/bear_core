# Assembly

import maya.cmds as mc

from bear.system import DataStructure
from bear.system import Component
from bear.system import Files

class Build(DataStructure.Asset):
    
    def __init__(self, 
                    buildStep='deform', 
                    assetFolder=None,
                    projectFolder=None,
                    versionName=None,
                    removeRef=True,
                    skinNodes=None,
                    byUVs=False,
                    byVertexID=True,
                    loadSkin=True,
                    loadLattice=True,
                    loadSmooth=True,
                    loadProxWrap=True,
                    loadGeometryConstraints=True,
                    loadInputOrder=True,
                    *args, **kwargs):

        super(Build, self).__init__(*args, **kwargs)

        self.buildStep = buildStep
        self.assetFolder = assetFolder
        self.projectFolder = projectFolder
        self.versionName = versionName
        if not self.versionName:
            self.versionName = Files.Config(self.projectFolder,
                                            self.assetFolder).getVersion()
        self.removeRef = removeRef
        self.skinNodes = skinNodes if skinNodes else []
        self.byUVs = byUVs
        self.byVertexID = byVertexID
        self.loadSkin = loadSkin
        self.loadLattice = loadLattice
        self.loadSmooth = loadSmooth
        self.loadProxWrap = loadProxWrap
        self.loadGeometryConstraints = loadGeometryConstraints
        self.loadInputOrder = loadInputOrder
    
    def skinning(self):

        if self.buildStep == 'deform':

            setupFile = DataStructure.Asset(assetFolder=self.assetFolder,
                                            versionName=self.versionName).skin(nodeList=self.skinNodes,
                                                                                byUVs=self.byUVs,
                                                                                byVertexID=self.byVertexID,
                                                                                loadSkin=self.loadSkin,
                                                                                loadLattice=self.loadLattice,
                                                                                loadSmooth=self.loadSmooth,
                                                                                loadProxWrap=self.loadProxWrap,
                                                                                loadGeometryConstraints=self.loadGeometryConstraints,
                                                                                loadInputOrder=self.loadInputOrder)
            if self.removeRef and setupFile in mc.file(reference=True, q=True):
                mc.file(setupFile, removeReference=True)

        if self.buildStep == 'blendshapes':

            pass

        if self.buildStep == 'faceCorrections':

            pass

        if self.buildStep == 'poseCorrections':

            pass

        if self.buildStep == 'postDeform':

            DataStructure.Asset(assetFolder=self.assetFolder,
                                versionName=self.versionName).postDeform()

        if self.buildStep == 'delivery':
            
            if mc.objExists(self.geometryRoot+'.freezeSelection'):
                mc.setAttr(self.geometryRoot+'.freezeSelection', True)

            for refFile in mc.file(reference=True, q=True):
                mc.file(refFile, removeReference=True)

            for groupNode in ['template', 'interpenetrationShapes', 'guide', 'blendshapes']:
                if mc.objExists(groupNode):
                    mc.delete(groupNode)

        Component.customScript(self.buildStep)

        mc.select(clear=True)