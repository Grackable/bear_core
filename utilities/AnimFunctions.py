# AnimFunctions

import maya.cmds as mc

from bear.system import Settings
from bear.utilities import Tools
from bear.utilities import AddNode
from bear.utilities import Nodes

def createAnimWave(attrNode, 
                    tipControlList,
                    chainControlList,
                    stringIndexPosition=None,
                    rangeValue=10,
                    name='animWave'):

    if rangeValue == None:
        rangeNodeList = tipControlList
        distList = [1.0]
    else:
        rangeNodeList, distList = Tools.getNodesWithinRange(attrNode, 
                                                            tipControlList, 
                                                            rangeValue)
                                                                        
    Nodes.addAttrTitle(attrNode, name)

    attrList = [['strength', 1.0],
                ['rootWeight', 0.0],
                ['tipWeight', 1.0],
                ['rootOffset', 0.0],
                ['useKeyOffsetValues', False],
                ['keyStrandDistanceOffset', 0.5],
                ['keyChainOffset', 2.0],
                ['keyOverallOffset', -5.0]]

    for attr in attrList:
        
        niceName = Tools.createNiceName(attr[0])
        attrName = Tools.createUniqueName(attr[0], name)

        if attr[0] == 'keyOverallOffset' or attr[0] == 'weightFalloff' or attr[0] == 'keyChainOffset':
            mc.addAttr(attrNode, at='float', ln=attrName, nn=niceName, k=False, dv=attr[1])
        elif attr[0] == 'useKeyOffsetValues':
            mc.addAttr(attrNode, at='bool', ln=attrName, nn=niceName, k=False, dv=attr[1])
        else:
            mc.addAttr(attrNode, at='float', ln=attrName, nn=niceName, k=False, dv=attr[1], hasMinValue=True, minValue=0)
        mc.setAttr(attrNode+'.'+attrName, cb=True)

    strength, \
    rootWeight, \
    tipWeight, \
    rootOffset, \
    useKeyOffsetValues, \
    keyStrandDistanceOffset, \
    keyChainOffset, \
    keyOverallOffset = ['%s.%s' % (attrNode, Tools.createUniqueName(attr[0], name)) for attr in attrList]

    if len(rangeNodeList) == 0:
        mc.error('There is no tip control in the given range of the attribute node.')

    for r, rangeNode in enumerate(rangeNodeList):
        
        # we expect that the input is only one chain if the range nodes / tip control count is 1,
        # otherwise is expected to be a list nested in a list, for example if we have multiple chains
        if len(rangeNodeList) == 1:
            chainControls = chainControlList
        else:
            if stringIndexPosition == None:
                strandIndex = r
            else:
                strandIndex = int(rangeNode.split('_')[stringIndexPosition])-1
            chainControls = chainControlList[strandIndex]

        distMult = 1.0/(distList[r]-distList[0]+1)

        Nodes.addAttrTitle(chainControls[-1], 'weight')
        distAttrName = 'weight_'+Nodes.replaceNodeType(attrNode)
        distAttr = chainControls[-1]+'.'+distAttrName
        if not mc.objExists(distAttr):
            mc.addAttr(chainControls[-1], ln=distAttrName, dv=distMult, k=False)
            mc.setAttr(distAttr, cb=True)

        for c, chainControl in enumerate(chainControls):
            
            chainCount = len(chainControls)
            
            funcNode = AddNode.parentNode(chainControl, nodeType='waveFunc_'+Nodes.replaceNodeType(attrNode))

            for a in 'XYZ':

                rotAttr = '%s.rotate%s'% (funcNode, a)

                rotateExpr = '$attrRot = %s.rotate%s;\n' % (attrNode, a) \
                            + '$chainCount = %s-%s;\n' % (float(chainCount), rootOffset) \
                            + '$c = (%s-%s)*(%s/$chainCount);\n' % (float(c), rootOffset, float(chainCount)) \
                            + 'if ($c < 0) {$c = 0;}\n' \
                            + '$instRot = $attrRot * (%s*%s*2);\n' % \
                                (strength, distAttr) \
                            + '$frameOffset = (($c*%s)+(%s*%s))-%s;\n' % \
                                (keyChainOffset, float(r), keyStrandDistanceOffset, keyOverallOffset) \
                            + '$funcRot = `getAttr -t (frame-$frameOffset) %s.rotate%s` * (%s*%s*2);\n' % \
                                (attrNode, a, strength, distAttr) \
                            + '$rot = $instRot;\n' \
                            + 'if (%s == 1) {$rot = $funcRot;}\n' % (useKeyOffsetValues) \
                            + '$p0 = %s;\n' % (rootWeight) \
                            + '$p1 = %s;\n' % (tipWeight) \
                            + '$t0 = %s;\n' % (0) \
                            + '$t1 = %s;\n' % (1) \
                            + '$rotBlend = $rot * `hermite $p0 $p1 $t0 $t1 (1.0/($chainCount-1)*$c)`;\n' \
                            + 'if ($c < 0) {$rotBlend = 0;}\n' \
                            + '%s = $rotBlend' % rotAttr

                rotExprName = rotAttr + '_' + Settings.expressionSuffix
                mc.expression(rotAttr, string=rotateExpr, name=rotExprName, alwaysEvaluate=1)

    return

def createAim(attrNode,
                tipControlList,
                chainControlList,
                chainOffList,
                indexPosition,
                rangeValue=10,
                lengthAxis='X',
                upAxis='Y',
                name='translate'):

    rangeNodeList, distList = Tools.getNodesWithinRange(attrNode, 
                                                        tipControlList, 
                                                        rangeValue)

    Nodes.addAttrTitle(attrNode, name)

    attrList = [['aimStrength', 1.0],
                ['distanceWeight', 0.0],
                ['distanceFalloff', 0.0]]

    for attr in attrList:
        if attr[0] == 'distanceWeight' or attr[0] == 'distanceFalloff':
            mc.addAttr(attrNode, at='float', ln=attr[0], k=False, dv=attr[1])
        else:
            mc.addAttr(attrNode, at='float', ln=attr[0], k=False, dv=attr[1], hasMinValue=True, minValue=0)
        mc.setAttr(attrNode+'.'+attr[0], cb=True)

    aimStrength, \
    distanceWeight, \
    distanceFalloff = ['%s.%s' % (attrNode, attr[0]) for attr in attrList]

    for r, rangeNode in enumerate(rangeNodeList):
        
        strandIndex = int(rangeNode.split('_')[indexPosition])-1
        chainControls = chainControlList[strandIndex]

        distMult = 1.0/(distList[r]-distList[0]+1)

        Nodes.addAttrTitle(chainControls[-1], 'weight')
        distAttrName = 'weight_'+Nodes.replaceNodeType(attrNode)
        distAttr = chainControls[-1]+'.'+distAttrName
        if not mc.objExists(distAttr):
            mc.addAttr(chainControls[-1], ln=distAttrName, dv=distMult, k=False)
            mc.setAttr(distAttr, cb=True)

        aimNode = AddNode.childNode(chainOffList[strandIndex][1], 'aim_'+Nodes.replaceNodeType(attrNode))

        aimVector, upVector = Nodes.convertAimAxis(lengthAxis, upAxis)

        mc.aimConstraint(attrNode, aimNode, aimVector=aimVector,
                    wuo=attrNode, wut='object', u=upVector, mo=True)

        aimReceiver = AddNode.parentNode(chainControls[1], 'aimReceiver_'+Nodes.replaceNodeType(attrNode))

        distValue = (1.0/(len(rangeNodeList)-1))*r

        for axis in 'XYZ':
            rotAttr = '%s.rotate%s' % (aimReceiver, axis)
            rotateExpr = '$rot = %s.rotate%s;\n' % \
                            (aimNode, axis) \
                        + '$p0 = %s;\n' % (aimStrength) \
                        + '$p1 = %s;\n' % (distanceWeight) \
                        + '$t0 = %s;\n' % (1) \
                        + '$t1 = %s;\n' % (distanceFalloff) \
                        + '$rotBlend = $rot*`hermite $p0 $p1 $t0 $t1 (%s)`;\n' % (str(distValue)+'*'+distAttr) \
                        + '%s = $rotBlend' % rotAttr
            
            rotExprName = rotAttr + '_' + Settings.expressionSuffix
            mc.expression(rotAttr, string=rotateExpr, name=rotExprName, alwaysEvaluate=1)

        for c, strandControl in enumerate(chainControls[1:-1]):
            if c > 0:
                chainReceiver = AddNode.parentNode(strandControl, 'aimReceiver_'+Nodes.replaceNodeType(attrNode))
                for axis in 'XYZ':
                    mc.connectAttr('%s.rotate%s'%(aimReceiver, axis), '%s.rotate%s'%(chainReceiver, axis))

    return
    
def createSinusWave(nodes, 
                    attrNode,
                    name='wave',
                    attribute='rotate',
                    waveAxis='X',
                    directionAxis='Y',
                    nodeSuffix='trsFunc',
                    createWeightAttr=False,
                    hasInterpolationAttributes=False):

    Nodes.addAttrTitle(attrNode, name)
    
    waveAxis = waveAxis.upper()
    directionAxis = directionAxis.upper()

    attrList = [['strength', 0.0],
                ['travel', 0.0],
                ['direction', 0.0], 
                ['frequency', 1.0]]

    for attr in attrList:

        niceName = Tools.createNiceName(attr[0])
        attrName = Tools.createUniqueName(attr[0], name)
        if attr[0] == 'frequency':
            mc.addAttr(attrNode, at='float', ln=attrName, nn=niceName, dv=attr[1], k=False,
                        hasMinValue=True,
                        minValue=0.01)
            mc.setAttr(attrNode+'.'+attrName, cb=True)
        else:
            mc.addAttr(attrNode, at='float', ln=attrName, nn=niceName, dv=attr[1], k=True)

    attrList = [['rootWeight', 0.0], 
                ['midWeight', 0.5], 
                ['midPosition', 0.5], 
                ['tipWeight', 1.0]]
    if hasInterpolationAttributes:
        attrList.extend([['rootInterpolation', 0], 
                            ['midInterpolation', 0], 
                            ['tipInterpolation', 0]])

    for attr in attrList:
        niceName = Tools.createNiceName(attr[0])
        attrName = Tools.createUniqueName(attr[0], name)
        mc.addAttr(attrNode, at='float', ln=attrName, nn=niceName, dv=attr[1], 
                    k=True,
                    hasMinValue=True,
                    minValue=0.01 if attr[0] == 'midPosition' else 0,
                    hasMaxValue=True if attr[0] == 'midPosition' else False,
                    maxValue=0.99 if attr[0] == 'midPosition' else 1)

    if createWeightAttr:
        Nodes.addAttrTitle(nodes[-1], 'weight')
        weightAttrName = 'weight_'+Nodes.replaceNodeType(attrNode)
        weightAttr = nodes[-1]+'.'+weightAttrName
        if not mc.objExists(weightAttr):
            mc.addAttr(nodes[-1], ln=weightAttrName, dv=1.0, k=False)
            mc.setAttr(weightAttr, cb=True)
    else:
        weightAttr = 1

    chainCount = len(nodes)
    trsFuncNodes = list()
    dirNegNodes = list()
    dirNodes = list()

    for n, node in enumerate(nodes):

        dirNode = AddNode.parentNode(node, nodeType=nodeSuffix+'Dir')
        trsFuncNode = AddNode.parentNode(dirNode, nodeType=nodeSuffix)
        dirNegNode = AddNode.parentNode(trsFuncNode, nodeType=nodeSuffix+'DirNeg')

        dirNodes.append(dirNode)
        trsFuncNodes.append(trsFuncNode)
        dirNegNodes.append(dirNegNode)

        rootWeight = '%s.%sRootWeight' % (attrNode, name)
        midWeight = '%s.%sMidWeight' % (attrNode, name)
        midPosition = '%s.%sMidPosition' % (attrNode, name)
        tipWeight = '%s.%sTipWeight' % (attrNode, name)
        if hasInterpolationAttributes:
            rootBlending = '%s.%sRootInterpolation' % (attrNode, name)
            midBlending = '%s.%sMidInterpolation' % (attrNode, name)
            tipBlending = '%s.%sTipInterpolation' % (attrNode, name)
        else:
            rootBlending = 0
            midBlending = 0
            tipBlending = 0

        trsWaveAttr = '%s.%s%s' % (trsFuncNode, attribute, waveAxis)
        trsDirAttr = '%s.%s%s' % (dirNode, 'rotate', directionAxis)
        trsDirNegAttr = '%s.%s%s' % (dirNegNode, 'rotate', directionAxis)

        manualScale = '%s.%sStrength' % (attrNode, name)
        direction = '%s.%sDirection' % (attrNode, name)
        frequency = '%s.%sFrequency' % (attrNode, name)
        offset = '%s.%sTravel' % (attrNode, name)

        mc.connectAttr(direction, trsDirAttr)
        mulNegNode = mc.shadingNode('multDoubleLinear', asUtility=True, name=dirNegNode+'_mul')
        mc.connectAttr(direction, '%s.input1'%mulNegNode)
        mc.setAttr('%s.input2'%mulNegNode, -1)
        mc.connectAttr('%s.output'%mulNegNode, trsDirNegAttr)

        trsExpr = '$chainCount = %s;\n' % (float(chainCount)) \
                + '$midPosition = %s;\n' % (midPosition) \
                + '$hAchainCount = ($chainCount-1)*$midPosition+1;\n' \
                + '$hBchainCount = ($chainCount-1)*(1.0-$midPosition)+1;\n' \
                + '$c = (1.0/($chainCount-1))*%s;\n' % (float(n)) \
                + '$hAc = $c/$midPosition;\n' \
                + '$hBc = ($c-$midPosition)*(1.0/(1-$midPosition));\n' \
                + '$trsVal = %s*sin((%s-%s)/%s);\n' % (manualScale, n, offset, frequency) \
                + '$pA0 = %s;\n' % (rootWeight) \
                + '$pA1 = %s;\n' % (midWeight) \
                + '$tA0 = %s;\n' % (rootBlending) \
                + '$tA1 = %s;\n' % (midBlending) \
                + '$pB0 = %s;\n' % (midWeight) \
                + '$pB1 = %s;\n' % (tipWeight) \
                + '$tB0 = %s;\n' % (midBlending) \
                + '$tB1 = %s;\n' % (tipBlending) \
                + '$hA = `hermite $pA0 $pA1 $tA0 $tA1 $hAc`*%s;\n' % (weightAttr) \
                + '$hB = `hermite $pB0 $pB1 $tB0 $tB1 $hBc`*%s;\n' % (weightAttr) \
                + '$h = 0.0;\n' \
                + 'if ($c <= $midPosition) {$h = $hA;}\n' \
                + 'if ($c > $midPosition) {$h = $hB;}\n' \
                + '$trsBlend = $trsVal*$h*%s;\n' % (weightAttr) \
                + '%s = $trsBlend+%s' % (trsWaveAttr, 1 if attribute == 'scale' else 0)
        
        trsName = trsWaveAttr.replace('.', '_')
        trsExprName = trsName + '_' + Settings.expressionSuffix
        mc.expression(trsWaveAttr, string=trsExpr, name=trsExprName, alwaysEvaluate=0)

    return {'weightAttr': weightAttr,
            'frequencyAttr': frequency,
            'travelAttr': offset,
            'directionAttr': direction,
            'dirNodes': dirNodes,
            'trsFuncNodes': trsFuncNodes,
            'dirNegNodes': dirNegNodes}