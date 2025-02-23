# Weights

import maya.cmds as mc
import maya.mel as mel    
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

from bear.utilities import Nodes
from bear.system import MessageHandling

class SkinTransfer(object):

    def __init__(self,
                    sourceGeoNode=None,
                    targetGeoNode=None,
                    transferMethod='vertexID'):

        self.sourceGeoNode = sourceGeoNode
        self.targetGeoNode = targetGeoNode
        self.transferMethod = transferMethod

    def transferWeights(self):

        skinData = self.getWeights(self.sourceGeoNode)
        if skinData:
            self.setWeights(self.targetGeoNode, skinData)

    def getMfnSkinCluster(self, skinClusterNode):

        mc.select(skinClusterNode)
        sel = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(sel)
        skinClusterObject = OpenMaya.MObject()
        sel.getDependNode(0, skinClusterObject)
        skinClusterFn = OpenMayaAnim.MFnSkinCluster(skinClusterObject)

        return skinClusterFn

    def getShapeDag(self, shape):

        mc.select(shape, r = True)
        sel = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(sel)
        shapeDag = OpenMaya.MDagPath()
        sel.getDagPath(0, shapeDag)

        return shapeDag

    def getWeights(self, geoNode):
        
        skinClusterNode = Nodes.getSkinCluster(geoNode)[0]
        
        # get the MFnSkinCluster
        skinClusterFn = self.getMfnSkinCluster(skinClusterNode)
        
        # get the influence objects
        joints = mc.skinCluster(skinClusterNode, q=True, inf=True)
        
        # get the connected shape node
        shape = mc.skinCluster(skinClusterNode, q=True, g=True)[0]
        
        # get the dag path of the shape node
        shapeDag = self.getShapeDag(shape)

        # create the geometry iterator
        geoIter = OpenMaya.MItGeometry(shapeDag)
        
        # get the skin cluster attributes
        normalizeWeights = mc.getAttr(skinClusterNode + ".normalizeWeights")
        maxInfluences = mc.getAttr(skinClusterNode + ".maxInfluences")
        dropOff = mc.getAttr(skinClusterNode + ".dropoff")[0][0]
        
        # create a pointer object for the influence count of the MFnSkinCluster
        infCount = OpenMaya.MScriptUtil()
        infCountPtr = infCount.asUintPtr()
        OpenMaya.MScriptUtil.setUint(infCountPtr, 0)

        # get the skinCluster weights
        weights = list()
        blendWeights = list()
        value = OpenMaya.MDoubleArray()
        try:
            while geoIter.isDone() == False:
                skinClusterFn.getWeights(shapeDag, geoIter.currentItem(), value, infCountPtr)
                for j in range(0, len(joints)):
                    if value[j] > 0:
                        weights.append([geoIter.index(), joints[j], j, value[j]])

                # dq blend weights
                skinClusterFn.getBlendWeights(shapeDag, geoIter.currentItem(), value)
                blendWeights.append(value[0])

                geoIter.next()
        except:
            MessageHandling.warning('There is an issue with the skin cluster: %s'%skinClusterNode)
            return None
        
        return {'skinClusterName': skinClusterNode,
                'joints': joints,
                'weights': weights,
                'blendWeights': blendWeights,
                'shape': shape,
                'normalizeWeights': normalizeWeights,
                'maxInfluences': maxInfluences,
                'dropOff': dropOff}
        
    def setWeights(self, geoNode, skinData, recreateSkinCluster=False):
        
        normalization = skinData['normalizeWeights']
        maxInfluences = skinData['maxInfluences']
        dropOff = skinData['dropOff']
        weights = skinData['weights']
        blendWeights = skinData['blendWeights']
        
        # variables for writing a range of influences
        weightString = ''
        inflStart = -1
        inflEnd = -1
        setCount = 0
        writeData = 0

        objects = skinData['joints']
        shapes = mc.listRelatives(geoNode, shapes=True, fullPath=True)
        # finding shape which has skin cluster applied
        for shape in shapes:
            if Nodes.getSkinCluster(shape)[0]:
                break

        shape = self.targetGeoNode
        
        # check for missing joint
        missingItems = []
        for item in objects:
            if not mc.objExists(item):
                missingItems.append(item)

        if missingItems:
            OpenMaya.MGlobal.displayError('Missing the following joints:\n')

        for item in missingItems:
            print(item)
        
        if missingItems:
            return(-1)

        # select the influences and the skin shape
        mc.select(objects+[shape], r=True)
        
        # create the new skinCluster
        skinClusterNode = Nodes.getSkinCluster(geoNode)[0]
        if skinClusterNode and recreateSkinCluster:
            mc.delete(skinClusterNode)
            skinClusterNode = None
        if skinClusterNode:
            newSkinCluster = skinClusterNode
        else:
            newSkinCluster = mel.eval('newSkinCluster \"-tsb -bm 0 -nw ' + str(normalization) + ' -mi ' + \
                                        str(maxInfluences) + ' -dr ' + str(dropOff) + ' -omi true -rui false\"')[0]
        
        # get the current normalization and store it
        # it will get re-applied after applying all the weights
        normalization = mc.getAttr(newSkinCluster + '.nw')
        # turn off the normalization to correctly apply the stored skin weights
        mc.setAttr((newSkinCluster + '.nw'), 0)
        # pruning the skin weights to zero is much faster
        # than iterating through all components and setting them to 0
        mc.skinPercent(newSkinCluster, shape, prw = 100, nrm = 0)
            
        # allocate memory for the number of components to set
        weightData = weights[len(weights) - 1]
        # get the index of the last component stored in the weight list
        maxIndex = weightData[0]
        mc.select(newSkinCluster, r=True)
        cmdString = 'setAttr -s ' + str(maxIndex + 1) + ' \".wl\"'
        cmdDQString = 'setAttr -s ' + str(maxIndex + 1) + ' \".bw\"'
        OpenMaya.MGlobal.executeCommand(cmdString)
        OpenMaya.MGlobal.executeCommand(cmdDQString)
        
        # apply the weight data
        for w in range(len(weights)):
            
            weightData = weights[w]
            weightsNext = ''
            # also get the next line for checking if the component changes
            # but only if it's not the end of the list
            if w < len(weights) - 1:
                weightsNext = weights[w + 1]
            else:
                weightsNext = weightData
                writeData = 1
            
            compIndex = weightData[0]

            # construct the setAttr string
            # i.e. setAttr -s 4 ".wl[9].w[0:3]"  0.0003 0.006 0.496 0.496
            
            # start a new range
            if inflStart == -1:
                inflEnd = inflStart = weightData[2]
            else:
                # if the current component is the next in line
                if inflEnd == weightData[2] - 1:
                    inflEnd = weightData[2]
                # if influences were dropped because of zero weight
                else:
                    # fill the weight string inbetween with zeros
                    for x in range(inflEnd + 1, weightData[2]):
                        weightString += '0 '
                        setCount += 1
                    inflEnd = weightData[2]
                
            # add the weight to the weight string
            weightString += str(weightData[3]) + ' '
            # increase the number of weights to be set
            setCount += 1
                
            # if the next line is for the next index set the weights
            if compIndex != weightsNext[0]:
                writeData = 1
                
            if writeData == 1:
                # decide if a range or a single influence index is written
                rangeString = ':' + str(inflEnd)
                if inflEnd == inflStart:
                    rangeString = ''
                cmdString = 'setAttr -s ' + str(setCount) + ' \".weightList[' + str(compIndex) + '].weights[' + str(inflStart) + rangeString + ']\" ' + weightString
                cmdDQString = 'setAttr .bw[' + str(compIndex) + '] ' + str(blendWeights[compIndex])
                OpenMaya.MGlobal.executeCommand(cmdString)
                OpenMaya.MGlobal.executeCommand(cmdDQString)

                # reset and start over
                inflStart = inflEnd = -1
                writeData = 0
                setCount = 0
                weightString = ''
            
        mc.setAttr((newSkinCluster + '.nw'), normalization)
'''
class DeformerTransfer(object):

    def __init__(self,
                    sourceDeformerNode=None,
                    targetDeformerNode=None,
                    sourceGeoNode=None,
                    targetGeoNode=None,
                    transferMethod='UVs',
                    sourceUVSet='map1',
                    targetUVSet='map1'):

        self.sourceDeformerNode = sourceDeformerNode
        self.targetDeformerNode = targetDeformerNode
        self.sourceGeoNode = sourceGeoNode
        self.targetGeoNode = targetGeoNode
        self.transferMethod = transferMethod
        self.sourceUVSet = sourceUVSet
        self.targetUVSet = targetUVSet

    def transferWeights(self):

        try: #catch due to missing deformer set error (guess it happens only when there are no weights to transfer)
            mc.copyDeformerWeights(sourceDeformer=self.sourceDeformerNode, 
                                    destinationDeformer=self.targetDeformerNode,
                                    sourceShape=self.sourceGeoNode, 
                                    destinationShape=self.targetGeoNode, 
                                    sa='closestPoint', 
                                    uv=(self.sourceUVSet, self.targetUVSet))
        except:
            pass
'''
class DeformerTransfer(object):

    def __init__(self,
                    sourceDeformerNode=None,
                    targetDeformerNode=None,
                    targetGeo=None,
                    deformerType=None,
                    transferMethod='vertexID'):

        self.sourceDeformerNode = sourceDeformerNode
        self.targetDeformerNode = targetDeformerNode
        self.targetGeo = targetGeo
        self.deformerType = deformerType
        self.transferMethod = transferMethod

    def transferWeights(self):

        dataDict = self.getWeights()
        self.setWeights(dataDict)

    def getDeformerGeos(self, deformerNode):

        geometryNodes = mc.deformer(deformerNode, query=True, geometry=True)
        geometryNodes = mc.ls(geometryNodes)
        geometryIndices = [int(index) for index in mc.deformer(deformerNode, query=True, gi=True)]

        geoByIndex = dict(zip(geometryIndices, geometryNodes))
        geoByNode = dict(zip(geometryNodes, geometryIndices))

        return geoByIndex, geoByNode

    def getWeights(self):
        
        geoByIndex, geoByNode = self.getDeformerGeos(self.sourceDeformerNode)

        sourceDeformerAttr = '%s.wl'%self.sourceDeformerNode

        dataDict = dict()
        for shapeIndex in geoByIndex.keys():
            shapeNode = geoByIndex[shapeIndex]
            dataDict[shapeNode] = dict()
            weightsAttr = "{0}[{1}].weights".format(sourceDeformerAttr, shapeIndex)
            items = mc.getAttr(weightsAttr, multiIndices=True)
            if items:
                weightIndices = [int(item) for item in mc.getAttr(weightsAttr, multiIndices=True)]
                weights = mc.getAttr(weightsAttr)
                weights = list(weights[0])
                for i in range(0, len(weightIndices)):
                    dataDict[shapeNode][weightIndices[i]] = weights[i]

        return dataDict

    def setWeights(self, dataDict):
        
        if self.deformerType == 'ffd':
            mc.lattice(self.targetDeformerNode, e=True, g=self.targetGeo)
        if not mc.objExists(self.targetDeformerNode):
            if self.deformerType == 'deltaMush':
                mc.deltaMush(self.targetGeo, name=self.targetDeformerNode)
            if self.deformerType == 'tension':
                mc.tension(self.targetGeo, name=self.targetDeformerNode)

        geoByIndex, geoByNode = self.getDeformerGeos(self.targetDeformerNode)

        targetDeformerAttr = '%s.wl'%self.targetDeformerNode

        # remove current weights
        shapeIndices = mc.getAttr(targetDeformerAttr, multiIndices=True)
        if shapeIndices:
            for shapeIndex in shapeIndices:
                mc.removeMultiInstance("{0}[{1}]".format(targetDeformerAttr, shapeIndex))

        # set weights
        for geometryNode in dataDict:
            targetGeometryNode = geometryNode.split(':')[1]
            if mc.objExists(targetGeometryNode):
                if not targetGeometryNode in geoByNode.keys():
                    continue
                shapeIndex = geoByNode[targetGeometryNode]
                for weightIndex in dataDict[geometryNode]:
                    weight = dataDict[geometryNode][weightIndex]
                    mc.setAttr("{0}[{1}].weights[{2}]".format(targetDeformerAttr, int(shapeIndex), weightIndex), weight)

'''
def Weights_Import(deformer, path):
    path = path.replace("/"+deformer, "")
    fileName = deformer+".xml"
    if cmds.objExists(deformer):
        if cmds.file(path+"/"+fileName, q=True, ex=True):
            try:
                path = cmds.deformerWeights(fileName,im = True, deformer = deformer, format = "XML", path = path)# deformer+".xml")
                print path
            except RuntimeError:
                print "File didn't actually contain custom painted weights for deformer:"+deformer
        else:
            cmds.warning("Cannot find file named: "+path+"/"+fileName)
    else:
        cmds.warning("Cannot find deformer named: "+deformer)

def Weights_Export(deformer, path):

    fileName = deformer+".xml"
    if cmds.objExists(deformer):
        if not cmds.file(path, q=True, ex=True):        
            cmds.sysFile( path, makeDir=True )# Unix #Make Directory if missing
        if cmds.file(path, q=True, ex=True):

            try:
                path = cmds.deformerWeights(fileName,ex = True, deformer = deformer, format = "XML", path = path)# deformer+".xml")
                print path
            except RuntimeError:
                print "Didn't actually find custom weights for deformer:"+deformer
        else:
            cmds.warning("Cannot find folder named: "+path)
    else:
        cmds.warning("Cannot find deformer named: "+deformer)

def ProximityWrap(driver, driven, fallOffScale = 10):
   
    shapes = cmds.listRelatives(driver,shapes=True, f = True)
    influenceShape = shapes[0]
    wrap = cmds.deformer(driven, type="proximityWrap")
    pwni = ifc.NodeInterface(wrap[0])
    pwni.addDriver(influenceShape)
    cmds.setAttr(wrap[0]+".falloffScale",fallOffScale)
    wrap[0] = cmds.rename(wrap[0],driven+"_pwrap")
    return wrap[0]
def importDeformerWeights(deform):

    path =cmds.workspace(q = 1, rd = 1)+ 'scripts/data/'

    deformType = cmds.nodeType(deform);

    validDeformers = ["cluster","softMod","wire","jiggle","deltaMush", "ffd"]
    if deformType in validDeformers:
        if deformType == "cluster":
            path += 'Cluster'
            path += "/"+deform
            Weights_Import(deform, path)        
        elif deformType == "deltaMush":
            path += 'DeltaMush'
            path += "/"+deform            
            Weights_Import(deform, path)
        elif deformType == "ffd":
            path += 'Lattice'
            lw.LatticeWeights(deform).load(path)
            print "Saved Lattice Weights["+deform+"] to folder: "+path+"\n"
        else:
            print "Current Supported Deformer types are : [Cluster, DeltaMush, Lattice].  Bother Stephen for more."

def exportDeformerWeights(deform):

    path =cmds.workspace(q = 1, rd = 1)+ 'scripts/data/'

    deformType = cmds.nodeType(deform);

    validDeformers = ["cluster","softMod","wire","jiggle","deltaMush", "ffd"]
    if deformType in validDeformers:
        if deformType == "cluster":
            path += 'Cluster'
            Weights_Export(deform, path)        
        elif deformType == "deltaMush":
            path += 'DeltaMush'
            Weights_Export(deform, path)
        elif deformType == "ffd":
            path += 'Lattice'
            lw.LatticeWeights(deform).save(path)
            print "Saved Lattice Weights["+deform+"] to folder: "+path+"\n"
        else:
            print "Current Supported Deformer types are : [Cluster, DeltaMush, Lattice].  Bother Stephen for more."
def mirrorDeformerWeights(deform, mesh,  mode):
    deformType = cmds.nodeType(deform);

    validDeformers = ["cluster","softMod","wire","jiggle","deltaMush"]
    if deformType in validDeformers:

        cmds.copyDeformerWeights( sd=deform, dd=deform, ss = mesh, ds= mesh, mirrorMode='YZ', mirrorInverse=mode)
    elif deformType == "ffd":
        mirrorLatticeWeights(deform, [mesh], mode)
        #print "test"
    else: 
        print deform +" is not a valid deformers\n"

def mirrorLatticeWeights(lattice, inputMeshes,mode):
    #I copy the weights manually to a deltamush deformer...then I mirror...then I copy weights back to lattice.
    meshes = cmds.lattice(lattice, q = 1, g = 1)

    for inputMesh in inputMeshes:

        inputShape = cmds.listRelatives(inputMesh, f =1, s = 1)[0]

        for i in range(0,len(meshes)):
            mesh = meshes[i]
            if cmds.ls(mesh, uuid=True)[0] == cmds.ls(inputShape, uuid=True)[0]:#UniqueID

                name = mesh.split('|') 
                deltaMushProxy = cmds.deltaMush(mesh, name = mesh[-2]+'_mirrorFlipProxy')[0]
                cmds.select(deltaMushProxy)

                VertexNb = cmds.polyEvaluate(mesh, v=1)-1
                                     
                weights = cmds.getAttr('{0}.weightList[{1}].weights[0:{2}]'.format(lattice,i, VertexNb))
                cmds.setAttr('{0}.weightList[0].weights[0:{1}]'.format(deltaMushProxy, VertexNb), *weights, size=len(weights))

                mirrorDeformerWeights(deltaMushProxy, mesh ,mode)


                weights = cmds.getAttr('{0}.weightList[0].weights[0:{1}]'.format(deltaMushProxy, VertexNb))
                cmds.setAttr('{0}.weightList[{1}].weights[0:{2}]'.format(lattice,i, VertexNb), *weights, size=len(weights))

                cmds.delete(deltaMushProxy)
                 
#mirrorLatticeWeights("M_Squash", ["hair_mesh"], 0)

'''