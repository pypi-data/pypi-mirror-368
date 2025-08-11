import importlib
import importlib.util
import json
import logging
import os
import os.path
import sys
from datetime import datetime
from pathlib import Path

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

import importlib
import sys

if sys.version_info.minor < 12:
    import imp
    def importModule(moduleName, moduleFile):
        """
        Imports a module from source code and returns the exected module
        @param moduleName Name of the module
        @param moduleFile File of the source code
        @return Excecuted module is returned 
        @throws Exception in case of an error
        """
        log.debug("=> importModule(moduleName=%s, moduleFile=%s)" % (moduleName, moduleFile))
        return imp.load_source(moduleName, moduleFile)
else:
    def importModule(moduleName, moduleFile):
        """
        Imports a module from source code and returns the exected module
        @param moduleName Name of the module
        @param moduleFile File of the source code
        @return Excecuted module is returned 
        @throws Exception in case of an error
        """
        log.debug("=> importModule(moduleName=%s, moduleFile=%s)" % (moduleName, moduleFile))
        #return importlib.machinery.SourceFileLoader(moduleName, moduleFile).load_module()
        
        #def import_module(module_name, module_file):
        spec = importlib.util.spec_from_file_location(moduleName, moduleFile)
        module = importlib.util.module_from_spec(spec)
        sys.modules[moduleName] = module
        spec.loader.exec_module(module)
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

def resolveVarsInPath(p):
    # Resolve home directory and environment variables
    return os.path.expandvars(p.replace("~", str(Path.home())))

def readJsonFile(filename):
    log.debug("=> read(%s)" % (filename))
    file = open(filename, "r")
    txt = file.read()
    return json.loads(txt)

def getUserInput(title = "", prompt = "", defaultValue=None, requiresInput=False):

    if defaultValue == None:
        prompt = "%s%s: " % (prompt, title)
    else:
        defVal = defaultValue if defaultValue else ""
        prompt = "%s%s [%s]: " % (prompt, title, defVal)

    while True:
        print("%s" % (prompt), end="")
        rv = input()
            
        if rv:
            rv = rv.strip()
        else:
            rv = ""
        
        if len(rv) == 0 and (defaultValue != None and len(str(defaultValue)) > 0):
            rv = defaultValue
        
        if len(str(rv)) > 0 or (len(str(rv)) == 0 and not requiresInput): 
            return rv
               

def backupFile(srcFilepath):

    # Build a unique filename 
    now = datetime.now() 
    date_time = now.strftime("%Y%m%d_%H%M%S")

    count = 0
    while True:
        destFilepath = "%s.%s.%d" % (srcFilepath, date_time, count)
        if not os.path.exists(destFilepath):
            break
        else:
            count = count + 1

    srcFile = open(srcFilepath, "r")
    destFile = open(destFilepath,"w")
    destFile.write(srcFile.read())
    srcFile.close()
    destFile.close()

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

def getFilesInDir(dir):
    return [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

def getDirInDir(dir):
    return [f for f in os.listdir(dir) if os.path.isdir(os.path.join(dir, f))]    

def copyFile(fromFile, toFile):
    with open(toFile, 'w') as outFd, open(fromFile, 'r') as inFd:
        outFd.write(inFd.read())

def readJsonFile(filename):
    log.debug("=> readJsonFilie(%s)" % (filename))
    file = open(filename, "r")
    txt = file.read()
    return json.loads(txt)

def writeJsonFile(pyDict, filename):
    log.debug("=> writeJsonFile(pyDict, %s)" % (filename))
    file = open(filename, "w")
    file.write(json.dumps(pyDict, indent=4))
    file.close()


def exec_cmd(cmd, returnAsDict=False, returnAsLinesArray=False):
    cmdIn = os.popen(cmd)

    line = cmdIn.readline()
    s = ""
    while line:
        if line.startswith("b\'"):
            line = line.strip()
            line = line[2:-1] + "\n"
        s = s + line
        line = cmdIn.readline()

    if returnAsDict:
        return json.loads(s)
    elif returnAsLinesArray:
        return splitString(s, "\n")
    else:
        return s

class FileLinesIterator:
    '''
    Iterator class to walk through lines of a text file in the context of for loop.

    Sample code:    

    from file_lines_iter import FileLines

    for line in FileLinesIterator("/Users/rolan/Desktop/WORK/1646599091.json"):
        print(line)
        
    '''
    
    def __init__(self, filepath, stripLines:bool=False, skipEmptyLines:bool=False, skipLinesStartWith:list[str]=[]):
        '''
        Constructor of FileLinesIterator class.
        :param filepath: Path of the file through which lines shall be iterated. If "-" than stdin is read
        :param skipLines: If set all lines are left and right stripped.
        :param skipEmptyLines: If set to true empty lines are not returned.
        :param skipLinesStartWith: Array of single characters. If a line starts with one of the chars it is not returned.
        '''
        self._filepath = filepath
        self._file = None
        self._skipEmptyLines=skipEmptyLines
        self._skipLinesStartWith=skipLinesStartWith
        self._stripLines=stripLines

    def __iter__(self):
        return self
    
    def __next__(self):
        if not self._file:
            if self._filepath=="-":
                self._file = sys.stdin
            else:
                self._file = open(self._filepath, "r")

        while True:
            line = self._file.readline()
            if not line:
                if self._filepath!="-":
                    self._file.close()
                raise StopIteration

            if self._stripLines:
                line=line.strip()
            else:
                line=line.rstrip()
                
            if self._skipEmptyLines and len(line)==0:
                continue

            if len(line)>0 and line[0] in self._skipLinesStartWith:
                continue

            return line

def readLinesFromFile(filepath:str, 
                      stripLines:bool=False, 
                      skipEmptyLines:bool=False, 
                      skipLinesStartWith:list[str]=[]) -> list([str]):
    if not filepath:
        return []
    
    lines = []
    for line in FileLinesIterator(filepath, 
                                  stripLines=stripLines,
                                  skipEmptyLines=skipEmptyLines,
                                  skipLinesStartWith=skipLinesStartWith):
        lines.append(line)
        
    return lines

########################################################################
#MARK: output functions
########################################################################
def print_stdout(s:str, end:str="\n", flush:bool=False):
    sys.stdout.write(f"{s}{end}")

    if flush:
        sys.stdout.flush()    
        
def print_stderr(s:str, end:str="\n", flush:bool=False):
    sys.stderr.write(f"{s}{end}")

    if flush:
        sys.stdout.flush()    