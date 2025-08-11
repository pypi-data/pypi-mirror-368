import sys
import os
import importlib.util
    
def _importModule(moduleName, moduleFile):
    spec = importlib.util.spec_from_file_location(moduleName, moduleFile)
    module = importlib.util.module_from_spec(spec)
    spec = spec.loader.exec_module(module)
    return module

def _loadConfigFile(cfgsDir, cfgName):
    cfgFile = "%s/%s.py" % (cfgsDir, cfgName)    

    # Import all attributes from the configuration file into the scope
    # of this module.
    if os.path.exists(cfgFile):
        cfgModule = _importModule(f"__cfg{cfgName}", cfgFile)
        thisModule = sys.modules[__name__]
        for k in dir(cfgModule):
            if not k.startswith("__"):
                setattr(thisModule, k, getattr(cfgModule, k))
    else:
        print("Cannot load configuration. Configuration variable ", cfgFile, " does not exist.", file=sys.stderr)
        
_tmp_ENVVARNAME_CFG="CFG"
_tmp_ENVVARNAME_CFGSDIR="CFGSDIR"
_tmp_CONST_CFGSDIRNAME="configs"

_tmp_cfgsDir = os.environ.get(_tmp_ENVVARNAME_CFGSDIR)
if not _tmp_cfgsDir:
    _tmp_m = sys.modules["__main__"]
    _tmp_file = _tmp_m.__file__
    if os.path.islink(_tmp_file):
        _tmp_file = os.path.realpath(_tmp_file)
    _tmp_cfgsDir = "%s/%s" % (os.path.dirname(_tmp_file), _tmp_CONST_CFGSDIRNAME)

# Load default configuration
_loadConfigFile(_tmp_cfgsDir, "DEFAULT")

# Overwrite the DEFAULTs with the environ specifics
_tmp_cfgName = os.environ.get(_tmp_ENVVARNAME_CFG)

if _tmp_cfgName:
    _loadConfigFile(_tmp_cfgsDir, _tmp_cfgName)
else:
    print("Cannot load configuration. Environment variable ", _tmp_ENVVARNAME_CFG, " not defined.", file=sys.stderr)

# if _tmp_cfgName:
#     _tmp_cfgFile = "%s/%s.py" % (_tmp_cfgsDir, _tmp_cfgName)    

#     # Import all attributes from the configuration file into the scope
#     # of this module.
#     if os.path.exists(_tmp_cfgFile):
#         _tmp_cfgModule = _importModule("__cfg", _tmp_cfgFile)
#         _tmp_thisModule = sys.modules[__name__]
#         for _k in dir(_tmp_cfgModule):
#             if not _k.startswith("__"):
#                 setattr(_tmp_thisModule, _k, getattr(_tmp_cfgModule, _k))
#     else:
#         print("Cannot load configuration. Configuration variable ", _tmp_cfgFile, " does not exist.", file=sys.stderr)
# else:
#     print("Cannot load configuration. Environment variable ", _tmp_ENVVARNAME_CFG, " not defined.", file=sys.stderr)

# Remove all temporary variables from this moduel.
for _k in dir(sys.modules[__name__]):
    if _k.startswith("_tmp_"):
        delattr(sys.modules[__name__], _k)

def log(logFunc):
    thisModule = sys.modules[__name__]    
    logFunc("")
    
    # If the environment variable is set to print the environment.
    pe=os.environ.get("PRINTENV")
    if pe and (pe.lower() in ("1", "true", "yes")):
        logFunc("*** ENV ******************************************")
        for k in os.environ.keys():
            logFunc(f"ENV.{k}: {os.environ.get(k)}")
        logFunc("*** ENV ******************************************")
        logFunc("")    
    
    # Print the configuration    
    logFunc("*** CFG ******************************************")
    for e in dir(thisModule):
        if e[0] == "_":
            continue
        a = getattr(thisModule, e, None)
        if not a:
            continue        
        if type(a) == str:
            logFunc(f"CFG.{e}: {a}")
        elif type(a) == dict:
            logFunc(f"CFG.{e}:")
            for k in a.keys():
                logFunc(f"  {k}: {a[k]}")
        elif type(a) == list:
            logFunc(f"CFG.{e}:")
            cnt=i
            for v in a:
                logFunc(f" {i}: {v}")
                i+=1
    logFunc("*** CFG ******************************************")
    logFunc("")    