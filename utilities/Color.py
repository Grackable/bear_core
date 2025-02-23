# Color

import maya.cmds as mc
import maya.mel as mel

from bear.system import Settings

def getColor(name):
    
    for c, colorName in enumerate(Settings.colors):
        if colorName == name:
            return c

def setColor(node, color='Yellow', side=None, secondaryDefaultColor=False):

    if color == 'Default':
        if side == Settings.rightSide:
            if secondaryDefaultColor:
                color = 'Bright Red'
            else:
                color = 'Red'
        elif side == Settings.leftSide:
            if secondaryDefaultColor:
                color = 'Bright Blue'
            else:
                color = 'Blue'
        else:
            if secondaryDefaultColor:
                color = 'Bright Yellow'
            else:
                color = 'Yellow'
    '''
    shapeList = mc.listRelatives(node, shapes=True, fullPath=True)
    if shapeList == None:
        return

    for shape in shapeList:

        colorIndex = getColor(color)
        hsv = Settings.colorsHSV[colorIndex]
        setHSVColor(shape, hsv)
    '''
    colorIndex = getColor(color)
    hsv = Settings.colorsHSV[colorIndex]
    setHSVColor(node, hsv)

def setHSVColor(node, hsv=(1, 1, 1)):
    
    rgbVals = mel.eval('hsv_to_rgb <<%s, %s, %s>>'%(hsv[0], hsv[1], hsv[2]))
    
    rgb = 'RGB'
    
    mc.setAttr(node + '.overrideEnabled', True)
    mc.setAttr(node + '.overrideRGBColors', True)
    
    for channel, rgbVal in zip(rgb, rgbVals):
        mc.setAttr(node + '.overrideColor%s' %channel, rgbVal)