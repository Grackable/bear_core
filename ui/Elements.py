from bear.system import Settings
import json, os

def loadScreenPosition(self, window='mainUI'):
    maya_user_folder = Settings.getMayaUserFolder()
    userConfigFilePath = os.path.join(maya_user_folder, f"b{window}_position.json")

    if not os.path.exists(userConfigFilePath):
        return

    try:
        with open(userConfigFilePath, "r") as file:
            data = json.load(file)

        # Restore position
        if "x" in data and "y" in data:
            self.move(int(data["x"]), int(data["y"]))

        # Restore size
        if "w" in data and "h" in data:
            self.resize(int(data["w"]), int(data["h"]))

    except Exception:
        # Corrupt or incompatible file → ignore silently
        pass

def saveScreenPosition(self, window='mainUI'):
    maya_user_folder = Settings.getMayaUserFolder()
    userConfigFilePath = os.path.join(maya_user_folder, f"b{window}_position.json")

    pos = self.pos()
    size = self.size()

    data = {
        "x": pos.x(),
        "y": pos.y(),
        "w": size.width(),
        "h": size.height(),
    }

    try:
        with open(userConfigFilePath, "w") as file:
            json.dump(data, file, indent=2)
    except Exception:
        pass

def resetScreenPosition(windows=['mainUI', 'toolsUI']):

    maya_user_folder = Settings.getMayaUserFolder()
    for window in windows:
        userConfigFilePath = maya_user_folder+'/b'+window+'_position.json'
        if os.path.exists(userConfigFilePath):
            os.remove(userConfigFilePath)