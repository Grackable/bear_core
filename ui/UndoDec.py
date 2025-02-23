from functools import wraps
import maya.cmds as mc

def undo(func):
    """ Puts the wrapped `func` into a single Maya Undo action, then 
        undoes it when the function enters the finally: block """
    @wraps(func)
    def _undofunc(*args, **kwargs):
        try:
            # start an undo chunk
            mc.undoInfo(ock=True)
            return func(*args, **kwargs)
        finally:
            # after calling the func, end the undo chunk
            mc.undoInfo(cck=True)

    return _undofunc