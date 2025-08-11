import importlib
import imp
import logging
import os
import os.path
import json
from pathlib import Path
from datetime import datetime

log = logging.getLogger(__name__)

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def importModule(moduleName, moduleFile):
    """
    Imports a module from source code and returns the exected module
    @param moduleName Name of the module
    @param moduleFile File of the source code
    @return Excecuted module is returned 
    @throws Exception in case of an error
    """
    #log.debug("=> importModule(moduleName=%s, moduleFile=%s)" % (moduleName, moduleFile))

    # Python 2.7
    module = imp.load_source(moduleName, moduleFile)

    # Python 3.5
    #spec = importlib.util.spec_from_file_location(moduleName, moduleFile)
    #module = importlib.util.module_from_spec(spec)
    #spec = spec.loader.exec_module(module)

    return module

def newInstanceFromClass(moduleName, className):
    '''
    Creates an instance of a class from a module and class name string.
    @param moduleName Name of the module
    @param className Name of the class in the module.
    @return Instance of class
    @throws Exception in case of an error.
    '''
    log.debug("=> createClassInstance(moduleName=%s, className=%s)" % (moduleName, className))

    mod = importlib.import_module(moduleName)
    cl = getattr(mod, className, None)

    if cl == None:
        raise Exception("Could not get class object %s from module %s." % (className, moduleName))

    obj = cl()

    if obj == None :
        raise Exception("Could not create instance of class %s from module %s." % (className, moduleName))
    
    log.debug("<= createClassInstance()");
    return obj

def splitString(str, sepChar):
    a = []
    for s in str.split(sepChar):
        a.append(s.strip())
    return a

def isDict(obj):
    if not obj:
        return False
    else:
        return True if obj.__class__ == {}.__class__ else False

def isArray(obj):
    if not obj:
        return False
    else:
        return True if obj.__class__ == [].__class__ else False

# Return the local IP
import socket
def getLocalIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    
    IP=None
    
    try:
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    
    return IP    

# Class to executues a function every x seconds 
import threading
import time
import traceback

class FunctionExecutor(threading.Thread):
    def __init__(self, cronSecs, function, *args, **kwargs):
        super().__init__()
        self._cronSecs = cronSecs
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def run(self):
        while True:
            try:
                time.sleep(self._cronSecs)
                self._function(*self._args, **self._kwargs)
            except Exception as ex:
                log.error(str(ex))
                traceback.print_exc()
                
#MARK: execCmd
from enum import Enum
class ReturnType(Enum):
    TEXT = 1
    JSON_AS_DICT = 2
    LINES_AS_LIST = 3

def execCmd(cmd, returnType : ReturnType = ReturnType.TEXT):
    log.debug("Exec %s" % (cmd))
        
    cmdIn = os.popen(cmd)

    line = cmdIn.readline()
    s = ""
    while line:
        if line.startswith("b\'"):
            line = line.strip()
            line = line[2:-1] + "\n"
        s = s + line
        line = cmdIn.readline()    

    log.debug("\n%s" % (s.strip()))                                  

    if returnType == ReturnType.JSON_AS_DICT:
        return json.loads(s)
    elif returnType == ReturnType.LINES_AS_LIST:
        return splitString(s, "\n")
    else:
        return s                
    
########################################################################
#MARK: date function
########################################################################
from datetime import datetime

def fnow(format:str="%Y-%m-%d %H:%M:%S")->str:
    return datetime.now().strftime(format)    