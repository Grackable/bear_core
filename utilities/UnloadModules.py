import inspect
from os.path import dirname 
import sys

def execute(customPath=None):

    if not customPath:
      customPath = dirname(__file__)

    customPath = customPath.lower()
    toDeletedNodes = list()
    
    for key, module in sys.modules.items():
      try:
          moduleFilePath = inspect.getfile(module).lower()
          
          if moduleFilePath == __file__.lower():
              continue
          
          if moduleFilePath.startswith(customPath):
              toDeletedNodes.append(key)
      except:
          pass

    for module in toDeletedNodes:
        del (sys.modules[module])