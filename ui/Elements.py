from bear.system import Settings
import json, os

def loadScreenPosition(self, window='mainUI'):

    maya_user_folder = Settings.getMayaUserFolder()
    userConfigFilePath = maya_user_folder+'/b'+window+'_position.json'
    if os.path.exists(userConfigFilePath):
        with open(userConfigFilePath, "r") as file:
            data = json.load(file)
            x = data["x"]
            y = data["y"]
            position = (x, y)
            self.move(position[0], position[1])

def saveScreenPosition(self, window='mainUI'):

    maya_user_folder = Settings.getMayaUserFolder()
    userConfigFilePath = maya_user_folder+'/b'+window+'_position.json'
    position = self.pos()
    with open(userConfigFilePath, "w") as file:
        json.dump({"x": position.x(), "y": position.y()}, file)

def resetScreenPosition(windows=['mainUI', 'toolsUI']):

    maya_user_folder = Settings.getMayaUserFolder()
    for window in windows:
        userConfigFilePath = maya_user_folder+'/b'+window+'_position.json'
        if os.path.exists(userConfigFilePath):
            os.remove(userConfigFilePath)