import logging
import os
from argparse import ArgumentParser

import dtiot_d2c.cli.CFG as CFG
import dtiot_d2c.cli.utils as utils
from dtiot_d2c.cli.config import Configuration
from dtiot_d2c.cli.profile import Profile, Profiles

log = logging.getLogger(__name__)


class CmdLineInterface:
    def __init__(self, flags=0):
        self._flags = flags
        self._name = "NoName"
        self._aliasNames = []
        self._preDefinedCmdArgs = {}
        self._hideCmdArgs = []
        self._1LineHelp = None

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    def getAliasNames(self):
        return self._aliasNames

    def setAliasNames(self, aliasNames):
        self._aliasNames = aliasNames

    def setPreDefinedCmdArgs(self, preDefinedCmdArgs):
        self._preDefinedCmdArgs = {}
        if preDefinedCmdArgs:
            for pdca in preDefinedCmdArgs:
                self._preDefinedCmdArgs[pdca["name"]] = pdca

    def addPreDefinedCmdArg(self, name, value):
        self._preDefinedCmdArgs[name] = value

    def hasPreDefinedCmdArg(self, name):
        return True if name in self._preDefinedCmdArgs.keys() else None

    def getPreDefinedCmdArg(self, name):
        return self._preDefinedCmdArgs[name] if name in self._preDefinedCmdArgs.keys() else None

    def getPreDefinedCmdArgs(self):
        return self._preDefinedCmdArgs

    def setHideCmdArgs(self, hideCmdArgs):
        self._hideCmdArgs = hideCmdArgs if hideCmdArgs else []

    def hasHideCmdArg(self, findPattern):
        for c in self._hideCmdArgs:
            if c.find(findPattern) > -1:
                return True

    def get1LineHelp(self):
        return "No 1-line-help available."

    def overwrite1LineHelp(self, txt):
        self._1LineHelp = txt

    def callGet1LineHelp(self):
        if self._1LineHelp:
            return self._1LineHelp
        else:
            return self.get1LineHelp()

    def addCmdLineArgs(self, argsParser):
        pass

    def isFlagSet(self, flag):
        return True if (self._flags & flag) > 0 else False

    def main(self, cmdargs=None):
        raise Exception("Method not implemented.")

    def callMain(self, cmdargs=None):
        # If command line args have been passed, check if any pre-defined args
        # have been configured. If yes, add the to cmdargs.
        if cmdargs:
            for key in self._preDefinedCmdArgs:
                pdca = self._preDefinedCmdArgs[key]
                name = pdca["name"]
                value = pdca["value"]
                dest = pdca["dest"] if "dest" in pdca.keys() else None

                if not dest:
                    dest = name.strip("-_").replace("-", "_")

                # Add the pre-defined command argument
                if not hasattr(cmdargs, dest):
                    setattr(cmdargs, dest, value)

        # Call the implementation's main function
        self.main(cmdargs=cmdargs)

    def addCmdLineArgsFromTemplate(self, args_templates:dict, args_parser:ArgumentParser, arg_name:str, *args, **overwrite_params)->bool:
        '''
        Adds a command line option from the configuration of command line options from a template dictionary.
        The template dictionary should have the following form:
        
        {
            "-lbl" : {"metavar":"{key:value, key:value, ...}", 
                    "dest":"labels", 
                    "required":False,
                    "default":None,
                    "help":"Labels defined by a JSON dictionary of key/value pairs."},
            "-o": ["--origin", 
                {"metavar":"<string>", 
                    "dest":"origin", 
                    "required": False,
                    "default":None,
                    "help":"X-M2M-ORIGIN heder."}
            ],
        }
        '''
        cfg = args_templates.get(arg_name, None)
        if not cfg:
            raise Exception(f"No command line argument configuration {arg_name} available.")
        elif type(cfg) not in [dict, list]:
            raise Exception(f"Invalid command line argument configuration for {arg_name}.")

        arg_name2:str = None
        if type(cfg) == list and len(cfg) >= 2:
            arg_name2 = cfg[0]            
            cfg = cfg[1]
        elif type(cfg) == list and len(cfg) == 1:
            cfg = cfg[0]

        _cfg = cfg.copy()
        
        for (k, v) in overwrite_params.items():
            _cfg[k] = v

        if arg_name2:
            args_parser.add_argument(arg_name, arg_name2, **_cfg)
        else:
            args_parser.add_argument(arg_name, **_cfg)

        return True  

class ConfigCmdLineInterface(CmdLineInterface):
    def __init__(self):
        super().__init__()
        self._config:Configuration = None

    def getConfig(self)->Configuration:
        return self._config

    @property  
    def config(self)->Configuration:
        return self._config
    
    @config.setter
    def config(self, config:Configuration):
        self._config = config

class ProfileCmdLineInterface(ConfigCmdLineInterface):
    def __init__(self):
        super().__init__()
        self._profile:Profile = None

    def getProfile(self)->Profile:
        return self._profile
    
    @property  
    def profile(self)->Profile:
        return self._profile
    
    @profile.setter
    def profile(self, profile:Profile):
        self._profile = profile
    
class ApiConnCmdLineInterface(ProfileCmdLineInterface):
    def __init__(self):
        super().__init__()
        self.apiConn = None

class _CLICommands():
    def __init__(self):
        self._cmdgrps = {}
        self._commands = {}

    def addCommandGroup(self, name, help):
        self._cmdgrps[name] = {
            "name": name,
            "help": help,
            "commands": []
        }

    def getCommandGroupNames(self):
        return self._cmdgrps.keys()

    def getCommandGroup(self, name):
        return self._cmdgrps[name]

    def addCommand(self, grp, cmd):
        self._cmdgrps[grp]["commands"].append(cmd)
        self._commands[cmd.getName()] = cmd

        # Add the alias names for  the command to the index
        for ca in cmd.getAliasNames():
            self._commands[ca] = cmd

    def getCommandNames(self):
        names = []
        for key in self._commands.keys():
            cmd = self._commands[key]
            names.append(cmd.getName())
        return names

    def getCommands(self):
        commands = []
        for key in self._commands.keys():
            commands.append(self._commands[key])
        return commands

    def getCommand(self, name):
        for key in self._commands.keys():
            cmd = self._commands[key]
            if name == cmd.getName() or name in cmd.getAliasNames():
                return cmd
        return None

# Create the singelton instance to manage registered cli commands
CLICommands = None

def init():
    log.debug("Loading CLI commands ...")
    for cg in CFG.CLICommands:
        grpname = cg["name"]
        grphelp = cg["help"]

        # If environment variable names are configured to activate
        # the command group check if the environment variable is set.
        # If not, skip this command group because it isn't activated.
        if (env_var_names := cg.get("envVars", [])):
            skip_cg = True
            for env_var_name in env_var_names:
                if (v := os.getenv(env_var_name, None)):
                    if str(v).lower() in ["1", "true", "yes"]:
                        skip_cg = False
                        break
            # The command group hasn't been switched on by environment varialbe
            if skip_cg:
                continue

        log.debug("  group name: %s" % (grpname))
        log.debug("  group help: %s" % (grphelp))

        CLICommands.addCommandGroup(grpname, grphelp)

        for c in cg["commands"]:
            cmdName = c["name"]
            log.debug("    name:  %s" % (str(cmdName)))
            log.debug("    file:  %s" % (c["cmdFile"]))
            log.debug("    class: %s" % (c["cmdClass"]))

            preDefinedCmdArgs = c["preDefinedCmdArgs"] if "preDefinedCmdArgs" in c.keys() else None
            log.debug("    preDefinedCmdArgs: %s" % (str(preDefinedCmdArgs)))

            hideCmdArgs = c["hideCmdArgs"] if "hideCmdArgs" in c.keys() else None
            log.debug("    hideCmdArgs: %s" % (str(hideCmdArgs)))

            help = c["1LineHelp"] if "1LineHelp" in c.keys() else None
            log.debug("    help: %s" % (str(help)))

            cmdAliasNames = []
            if utils.isArray(cmdName):
                cmdAliasNames = cmdName[1:]
                cmdName = cmdName[0]

            modName = "_Command_%s" % (cmdName)
            mod = utils.importModule(modName, c["cmdFile"])
            cmd = utils.newInstanceFromClass(modName, c["cmdClass"])
            cmd.setName(cmdName)
            cmd.setAliasNames(cmdAliasNames)
            cmd.setPreDefinedCmdArgs(preDefinedCmdArgs)
            cmd.setHideCmdArgs(hideCmdArgs)
            cmd.overwrite1LineHelp(help)

            CLICommands.addCommand(grpname, cmd)


# Initialize registered cli commands
if not CLICommands:
    CLICommands = _CLICommands()
    init()
