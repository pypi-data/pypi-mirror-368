import importlib
import json
import logging
import os
import os.path
import sys
import time
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
        return importlib.machinery.SourceFileLoader(moduleName, moduleFile).load_module()

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

def isString(obj):
    return obj.__class__ == "str".__class__ if obj else False

def convert_str_to_python_type(s:str):
    if not s:
        return s

    try:
        return int(s)
    except Exception:
        pass
    
    try:
        return float(s)
    except Exception:
        pass
    
    if s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False

    try:
        result = json.loads(s)
        if isinstance(result, (list, dict, tuple)):
            return result
    except json.JSONDecodeError:
        pass            
    
    return s

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

#MARK: readlines
def readlines(filepath:str="-", 
              stripLines:bool=False, 
              skipEmptyLines:bool=False, 
              skipLinesStartWith:list[str]=[],
              encoding="utf-8"):
    '''
    Generator function to read a file linewise.
    You can use this function to read the file line by line with the following code:
        
    lines = readlines(filename)
    while (line := next(lines)):
        print(line) 
        
    Advanage of this function is that file is not read into the memory completely. By this unlimited file sizes
    can be processed.
    '''
    if not filepath or filepath == "-":
        file = sys.stdin
        iamOwner = False
    else:        
        file = open(filepath, "r", encoding=encoding)
        iamOwner = True

    while True:
        line = file.readline()
        
        # If we reached end of file
        if line == '':
            if iamOwner:
                file.close()
            yield None

        if stripLines:
            line=line.strip()
        else:
            line=line.rstrip()
            
        if skipEmptyLines and len(line)==0:
            continue

        if len(line)>0 and line[0] in skipLinesStartWith:
            continue

        yield line    
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

import socket


def getIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
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
                
def getValueFromDict(rootD:dict, elemPath:str, default:any=None, sepChar=".") -> any:
    '''
    Gets a value from a dictionary element.
    '''
    d = rootD
    names = elemPath.split(sepChar)
    name = names[0]    

    if name not in d.keys() or len(names) == 0:
        return default
    elif len(names) == 1:
        return d.get(name)            
    else:
        return getValueFromDict(d.get(names[0]), sepChar.join(names[1:]), default=default, sepChar=sepChar)

def get_value_from_dict_2(rootD:dict, elemPath:str, default:any=None, sepChar=".") -> any:
    '''
    New version of getValueFromDict which supports arrays.
    '''
    d = rootD
    names = elemPath.split(sepChar)
    name = names[0]    

    # If name represents an elemement in an array such as dvi[0]
    list_idx = -1
    
    if (idx1 := name.find("[")) > -1:
        if (idx2 := name.find("]", idx1)) == -1:
            return default
        list_idx = int(name[idx1+1:idx2])
        name = name[0:idx1]
        
    if name not in d.keys() or len(names) == 0:
        return default
    elif len(names) == 1:
        if list_idx == -1:
            return d.get(name)            
        else:
            l = d.get(name)
            return l[list_idx] if list_idx < len(l) else default
    else:
        if list_idx == -1:
            return get_value_from_dict_2(d.get(names[0]), sepChar.join(names[1:]), default=default, sepChar=sepChar)
        else:
            l = d.get(name)
            if list_idx >= len(l):
                return default
            return get_value_from_dict_2(l[list_idx], sepChar.join(names[1:]), default=default, sepChar=sepChar)
            

def has_element_value(d:dict, elem_name_path:str, test_value)->bool:
    """Verifies if an element in a dictionary has a specific value. 
       By using the function get_value_from_dict_2 it can support arrays in the elem_name_path.
    Returns:
        bool: True if the element with the value exists. 
    """
    _DOES_NOT_EXIST = "__DOES_NOT_EXIST__"
    
    v = get_value_from_dict_2(d, elem_name_path, default=_DOES_NOT_EXIST, sepChar=".")
    
    if v != None and v == _DOES_NOT_EXIST:
        return False        
    elif v == None and test_value == None:
        return True
    elif test_value != None and v == None:
        return False
    elif test_value == None and v != None:
        return False
    # Check if the searched value is in the array
    elif type(v) in [list, tuple] and type(test_value) not in [list, tuple]:
        return test_value in v
    # If the found value and test value have not the same type, they are not equal.
    elif type(v) != type(test_value):
        return False
    else:        
        return v == test_value
    
def hasElementInDict(rootD:dict,     # Dictionary which shall be checked for the element
                     elemPath:str,   # Element path string
                     sepChar="."     # Dictionary level separator charactor in element path string.
) -> bool:                           # True if the element exists. False if the element doesn't exist.
    '''
    Verifies if a specific element in the dictionary exists by parsing an element path string.
    '''
    d = rootD
    names = elemPath.split(sepChar)
    firstName = names[0]    

    if firstName not in d.keys() or len(names) == 0:
        return False
    elif firstName not in d.keys():
        return False
    elif len(names) == 1:
        return True if firstName in d.keys() else False          
    else:
        return hasElementInDict(d.get(names[0]), sepChar.join(names[1:]), sepChar=sepChar)

def setValueInDict(rootD:dict,              # Dictionary in which the value of an element shall be set.
                   elemPath:str,            # Path string to indicate the element in dictionary
                   value,                   # Value to set.
                   sepChar=".",             # Character which seperates the dictionary levels in path string
                   createIfNotExist=False   # If true, the element is created if it doesn't exist.
) -> bool:                                  # True if the value has been set. False if the value
                                            # hasn't been set because the element hasn't been found.
    '''
    Sets a value to an element in a dictionary by parsing an element path.
    '''
    d = rootD
    names = elemPath.split(sepChar)
    firstName = names[0]    

    if firstName not in d.keys():
        if createIfNotExist:
            if len(names) > 1:
                for i in range(0, len(names) - 1):
                    d[names[i]] = {}
                    d = d[names[i]]
            d[names[-1]] = value
            return True
        else:
            return False

    # At this point the element with firstName always exist.
    # If we reached the leaf of the path
    if len(names) == 1:
        d[firstName] = value
        return True
    else:
        return setValueInDict(d.get(names[0]), sepChar.join(names[1:]), value, sepChar=sepChar, createIfNotExist=createIfNotExist)

def flattenDict(inD:dict,       # Multilevel dictionary which elements shall be flatten to 
                                # to a single level dictionary.
                prefix:str="",  # Prefix which shall be added to each element
                sepChar:str="_" # Character which shall be used to seperate the level from each other
)->dict:                        # Single level dirctionary
    '''
    Walks top/down through a multi-level dictionary and creates out of it a dictionary
    with only a single level. The names of the sub-dictionary in the input dictionary
    are separated in the name of the return dictionary by a separator character.
    '''
    retD = {}
    for k in inD.keys():
        e = inD[k]
        if type(e) == dict:
            d = flattenDict(e, prefix=f"{prefix}{k}{sepChar}", sepChar=sepChar)
            retD.update(d)
        else:
            retD[f"{prefix}{k}"] = inD[k]

    return retD

def suppressEx(func, *args, **kwargs) -> any:
    '''
    Runs a function and suppresses an exception. 
    
    :param *args: Optional arguments to pass into the function.
    :param **kwargs: Option keyword arguments to pass into the function.
    
    :return: Return of the function or None in case an exception is caught.
    '''
    try:
        return func(*args, **kwargs)
    except Exception as ex:
        log.error(f"Error while exec {func.__name__}: {ex}")        
        return None           
    
def int2StrWithDots(
    v:int,      # integer
    default:str=""    # default value 
)->str:
    '''
    Converts an integer to a string with "." as decimal seperator.
    '''
    if not v:
        return default
    else:
        return f"{v:,}".replace(",", ".")    

###
# Some usefull decorators
#MARK: profile decorator
from functools import wraps

PROFILE_SWITCHED_ON=False
def profile(log_func=None,       # Logger function to use for output. 
                                 # If not defined "print" is used to output to stdout.
            log_prefix="profile" # Prefix string for the log output
):                               # Any value of decorated function
    '''
    Function decorator to print function call arguments and execution time to stdout or a logger.
    
    By default the profile decoration is switchd off. To switch it on set the variable 
    utils.PROFILE_SWTICHED_ON=True.
    
    How to use the profile decorator:

    import utils
    
    utils.PROFILE_SWITCHED_ON=true
    
    @utils.profile(logger=log.info)
    def myFunc(name):
        print(f"Hallo from {name}")
    '''
    
    if not log_func:
        log_func = print
        
    def decorator(fu):
        if not PROFILE_SWITCHED_ON:
            return fu
        @wraps(fu)
        def wrapper(*args, **kwargs):
            s = ""
            for a in args:
                if s:
                    s += ", "
                s += f"{a}" 
            for (k, v) in kwargs.items():
                if s:
                    s += ", "
                s += f"{k}={v}" 
            log_func(f"{log_prefix}: calling {fu.__name__}({s})")
                
            before = time.time()
            rv = fu(*args, **kwargs)
            after = time.time()
            
            log_func(f"{log_prefix}: called {fu.__name__}: {after - before:.6f} secs")

            return rv
        return wrapper
    return decorator        


UTF8_to_UNICODE_ESCAPE = lambda s: s.encode('unicode_escape').decode('ascii')
UNICODE_ESCAPE_to_UTF8 = lambda s: s.encode('ascii').decode('unicode_escape')

def xxcode_str_values_in_dict(d:dict,   # Dictionary in which the string values shall be en- or de-coded. 
                              xxcoder   # Lambda function to en- or de-code.
                             ) -> None:
    '''
    En- or de-codes the string values within a dictionary recursivly.
    '''
    if not d:
        return None

    for k, v in d.items():
        if type(v) == str:
            d[k] = xxcoder(v)
        elif type(v) == dict:
            xxcode_str_values_in_dict(v, xxcoder)

    return None

########################################################################
#MARK: date function
########################################################################
from datetime import datetime


def fnow(format:str="%Y-%m-%d %H:%M:%S")->str:
    return datetime.now().strftime(format)

class DatetimeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return super().default(obj)   

########################################################################
#MARK: base64
########################################################################
import base64


def str_to_b64str(s:str)->str:
    if not s:
        return s
    b = s.encode('utf-8')
    b64 = base64.b64encode(b)
    return b64.decode('utf-8')    

def to_basic_auth(username:str, password:str)->str:
    return str_to_b64str(f"{username}:{password}")

########################################################################
#MARK: retry_function
########################################################################
def retry_function(retry_function, args:list=None, kwargs:dict=None, 
                   max_try_count:int=-1, max_secs:int=-1,
                   sleep_before_first_try_secs:int=-1, sleep_after_error_secs:int=-1,
                   error_return_value=None, 
                   info_message=None,
                   info_logger=None, 
                   error_logger=None):
    
    il = info_logger or log.info
    el = error_logger or log.error
        
    start_secs = time.time()

    last_ex = None    
    try_count = 0
    
    if info_message:
        il(info_message)
        
    if sleep_before_first_try_secs > 0:
        time.sleep(sleep_before_first_try_secs)
        
    while True:
        try_count += 1
        
        # Test if the max duration of the max number of trys have been reached
        now_secs = time.time()
        if (now_secs - start_secs > max_secs) or try_count > max_try_count:
            if last_ex:
                raise last_ex
            else:
                return error_return_value

        # Execute the function
        try:
            if try_count > 1 and info_message:
                il(f"... {try_count-1}. retry ...")
            
            rv = retry_function(*args, **kwargs)

            return rv
        
        except Exception as ex:
            el(ex)
            last_ex = ex
            if sleep_after_error_secs > 0 and try_count < max_try_count:
                log.info(f"... sleeping {sleep_after_error_secs} seconds before retrying ...")
                time.sleep(sleep_after_error_secs)

    
########################################################################
#MARK: enumerations
########################################################################
    
def get_enum_name_by_value(enum_class, value, default=None)->str | None:
    for member in enum_class:
        if member.value == value:
            return member.name
    return default

def get_enum_value_by_name(enum_class, name:str, default=None)->str | None:
    for member in enum_class:
        if member.name == name:
            return member.value
    return default


def get_enum_by_name(enum_class, name)->Enum | None:
    for member in enum_class:
        if member.name == name:
            return member
    return None

########################################################################
#MARK: UniqueList
########################################################################
class UniqueList:
    """List class to deal with unique elements.
    """
    def __init__(self, iterable=None):
        self._list = list()
        self._dict = dict() # Dictionary to manage items as keys to speadup 
                            # check if the item already exists in list
        
        if iterable:
            for item in iterable:
                self.append(item)

    @property 
    def list(self)->list:
        return self._list
        
    def append(self, item):
        if not item:
            raise ValueError(f"Empty items not allowed in list with unique values.")()
        if item not in self._dict.keys():
            self._list.append(item)
            self._dict[item] = True

    def extend(self, iterable):
        for item in iterable:
            self.append(item)

    def remove(self, item):
        if item in self._dict.keys():
            self._list.remove(item)
            del self._dict[item]

    def __contains__(self, item):
        return item in self._dict.keys()

    def __len__(self):
        return len(self._list)

    def __getitem__(self, index):
        return self._list[index]

    def __setitem__(self, index, value):
        if value in self._list and self._list[index] != value:
            raise ValueError(f"{value} already exists in UniqueList")
        self._list[index] = value
        del self._dict[value]
        self._dict[value] = True
        
    def __delitem__(self, index):
        del self._dict[self._list[index]]
        del self._list[index]

    def __iter__(self):
        return iter(self._list)

    def __repr__(self):
        return f"UniqueList({self._list})"

    def clear(self):
        self._list = list()
        self._dict = dict()

def integrate_lists(list_1:list, list_2:list)->list:
    """Integrates a list-2 with a list-1 or replaces a list-1 by a list-2. 

    Args:
        list_1 (list): List-1 which elements shall be updated, deleted or replaced completely by the the elements of list-2
        list_2 (list): List-2 which elements shall integrated with list-1.

    Returns:
        list: New list
    """

    # Determine if we need to perform a replace or an integration operation
    operation = "r"  # r := replace
    del_elems = {}
    add_elems = {}
        
    for e in list_2:
        if e[0] == "+":
            operation = "i"
            add_elems[e[1:]] = True
        elif e[0] == "-":
            operation = "i"
            del_elems[e[1:]] = True

    if operation == "r":
        return list_2
    
    ul = UniqueList(list_1)
    
    for e in list_2:
        #print(f"e: {e}")
        if e[0] == "-":
            # If the complete list shall be completely removed
            if e == "-*":
                return ()
            else:
                ul.remove(e[1:])
        elif e[0] == "+":
            ul.append(e[1:])
        else:
            ul.append(e)

    return ul.list        

########################################################################
#MARK: Argument type converter
########################################################################

import argparse

def argparse_type_list(arg_value):
    try:
        if arg_value[0] == "\\":
            arg_value = arg_value[1:]

        if arg_value[0] != "[":
            return splitString(arg_value, ",")
        else:
            o = json.loads(arg_value)
    
        if type(o) != list:
            raise argparse.ArgumentTypeError(f"Not a list format: {arg_value}")
        
        return o
    
    except json.JSONDecodeError:
        raise argparse.ArgumentTypeError(f"Not a valid JSON list format: {arg_value}")

def argparse_type_json(arg_value):
    try:
        return json.loads(arg_value)
    except json.JSONDecodeError:
        raise argparse.ArgumentTypeError(f"Not a valid JSON format: {arg_value}")





