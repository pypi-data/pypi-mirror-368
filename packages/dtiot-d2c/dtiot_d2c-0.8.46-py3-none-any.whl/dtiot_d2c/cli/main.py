#!/usr/bin/env python3

import argparse
import logging
import os
import os.path
import sys
import traceback

import dtiot_d2c.cli.CFG as CFG
import dtiot_d2c.cli.utils as utils
from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface
from dtiot_d2c.cli.cli_command import CLICommands as clicmds
from dtiot_d2c.cli.cli_command import (ConfigCmdLineInterface,
                                       ProfileCmdLineInterface)
from dtiot_d2c.cli.config import Configuration
from dtiot_d2c.cli.profile import Profile
from dtiot_d2c.cli.utils import color

log = logging.getLogger(__name__)

WAIT_FOR_DBG_CLIENT=True

def printUsage():
    print("Usage: d2c MAJOR-COMMAND [MINOR-COMMAND] [OPTIONS] [PARAMETERS]")

def printSupportedCommands():
    print("Supported commands are:")
    print("  --help")
    for n in clicmds.getCommandNames():
        print("  %s" % (n))

# Build commands help
class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        return argparse.HelpFormatter._split_lines(self, text, width)

def _main():

    '''
    ni COMMAND [options] [parameters]
    Options are:
    -h, --help: 
    -l, --loglevel:
    --debug
    ''' 
    argsNum = len(sys.argv)
    arg1 = sys.argv[1] if argsNum > 1 else None

    # Create the command line parse with the basic command line options ...
    argsParser = argparse.ArgumentParser(prog="d2c", 
                                         description="D2C command line interface", 
                                         formatter_class=SmartFormatter)

    # Build the command's help
    cmdsHelp = "R|"
    for grpname in clicmds.getCommandGroupNames():
        cmdgrp = clicmds.getCommandGroup(grpname)

        cmdsHelp = "%s%s%s%s%s\n" % (cmdsHelp, color.UNDERLINE, color.BOLD, cmdgrp["name"], color.END)

        for cmd in cmdgrp["commands"]:
            cmdNames = cmd.getName()
            for a in cmd.getAliasNames():
                cmdNames = "%s, %s" % (cmdNames, a)

            cmdsHelp = "%s%s: %s\n" % (cmdsHelp, cmdNames, cmd.callGet1LineHelp())

        cmdsHelp = "%s\n" % (cmdsHelp)

    argsParser.add_argument("command", nargs='?', help=cmdsHelp)

    argsParser.add_argument("command-options", nargs="*", 
                            help="Command options.")

    # If no command line arguments are passed, display help messages and exit
    if len(sys.argv) == 1:
        argsParser.print_help()
        return 1
    
    # Remove all command line args behind the command name to  let parse the basic args
    # If we don't do this the argument parser creates an error because we can not 
    # declare the command specific arguments here. We don't know them.

    # Copy original command line args
    argvBackup = []
    for arg in sys.argv:
        argvBackup.append(arg)    

    # Search for the command name in the arguments ...
    cmdNames = []

    for cmd in clicmds.getCommands():
        cmdNames.append(cmd.getName())
        #print("A>%s<" % (str(cmd.getName())))
        for a in cmd.getAliasNames():
            #print("B>%s<" % (str(a)))
            cmdNames.append(a)

    cmdIdx = None
    for idx in range(1, len(sys.argv)):
        if sys.argv[idx] in cmdNames:
            cmdIdx = idx
            break

    # Remove all command line args behind the command name
    if cmdIdx:
        while len(sys.argv) > (cmdIdx + 1):
            sys.argv.pop(-1)

    #  Parse the command lines arguments
    cmdargs = argsParser.parse_args()

    ###
    # Initialize the command and execute it
    cmd = clicmds.getCommand(cmdargs.command)

    if not cmd:
        print("Error: unknown command %s.\n" % (cmdargs.command), file=sys.stderr)
        argsParser.print_help()
        return 1

    log.debug("Selected command %s of type %s." % (cmdargs.command, str(type(cmd))))

    # Re-create the command line parser for command from the stored command line args
    sys.argv = argvBackup[cmdIdx:]
    
    argsParser = argparse.ArgumentParser(prog="d2c %s" % (cmdargs.command), 
                                         description=cmd.get1LineHelp())

    argsParser.add_argument("-l", 
                            choices = ["INFO", "info", "WARN", "warn", "DEBUG", "debug"],
                            dest="log_level", default="WARN",
                            help="Log level. Possible values  are INFO, info, WARN, warn, DEBUG, debug.") 

    argsParser.add_argument("--debug", dest="debug", action="store_const", const=True, default=False,
                            help="If set, than debug output is printed. Same like -l debug")

    argsParser.add_argument("--info", dest="info", action="store_const", const=True, default=False,
                            help="If set, than info output is printed. Same like -l info")

    argsParser.add_argument("--outfile", metavar="<filepath>", dest="outfile", default="-",
                            help="File into which the log outputs shall be written additionaly.")

    # add configuration arguments if required by command
    if isinstance(cmd, ConfigCmdLineInterface):
        argsParser.add_argument("--config-directory", metavar="<directory>", dest="configDir", 
                                help="Directory which contains the configuration file %s." % (CFG.DEFAULT_CFGFILE_NAME))

        argsParser.add_argument("--config-file", metavar="<file>", dest="configFile", 
                                help="Path to the configuration file. If set than --config-directory is ignored.")

    # add profile argument if required by command
    if isinstance(cmd, ProfileCmdLineInterface):
        argsParser.add_argument("-p", "--profile-file", metavar="<file>", dest="profileFile",
                                help="Path to the profile file. If not set the configured active profile is ued.")

    cmd.addCmdLineArgs(argsParser)

    cmdargs = argsParser.parse_args()

    if cmdargs.debug:
        cmdargs.log_level = "DEBUG"
        logging.basicConfig(force=True, level=cmdargs.log_level.upper(), format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")                                
    else:
        if cmdargs.info:
            cmdargs.log_level = "INFO"

        logging.basicConfig(force=True, level=cmdargs.log_level.upper(), format="%(asctime)s | %(levelname)s | %(message)s")                                

   # Debug the parsed command line options
    for e in dir(cmdargs):
        if not e.startswith("_"):
            log.debug("%-20s = %s" % (e, str(getattr(cmdargs, e))))

    # Add an addtional logging output file if requested by command line option
    if cmdargs.outfile and len(cmdargs.outfile) > 0 and cmdargs.outfile != "-":
        file_handler = logging.FileHandler(cmdargs.outfile)
        file_handler.setLevel(level=cmdargs.log_level.upper())
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")                                
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

    # If the current command requires a configuration check if the 
    # configuration file is available.
    if isinstance(cmd, ConfigCmdLineInterface):
        cfgFile = Configuration.getPathToConfigFile(configFile=cmdargs.configFile, 
                                                    configDir=cmdargs.configDir)
        if not os.path.exists(cfgFile):
            raise Exception("Config file %s does not exist." % (cfgFile))

        cmd.config = Configuration(configFile=cfgFile)

    # If the current command requires a profile load the profile
    if isinstance(cmd, ProfileCmdLineInterface):

        if not cmd.config:
            raise Exception("Configuration hasn't been loaded.")

        if not cmdargs.profileFile:
            profileFile = os.path.join(cmd._config.getProfilesDirectory(), cmd._config.getActiveProfileFile())
        else:
            profileFile = cmdargs.profileFile

        cmd.profile = Profile(file=profileFile)

    # If the current command requires a Nokia Impact API connection

    if isinstance(cmd, ApiConnCmdLineInterface):
        if not cmd.profile:
            raise Exception("No profile has been loaded.")

        cmd.apiConn = CFG.createApiConnection(cmd.profile)
    
    ###
    # Execut the command ...
    cmd.callMain(cmdargs)

    return 0

def main():
    exitCode = 0

    try:
        
        exitCode = _main()
        
    except Exception as ex:
        if log.root.level == logging.DEBUG:
            traceback.print_exc()
        else:
            utils.print_stderr(f"Error: {ex}")
            utils.print_stderr("Use \"--debug\" command line option to see more info.")
            #traceback.print_exc()
        exitCode = 1
    
    finally:
        sys.exit(exitCode)
            
if __name__ == '__main__':
    main()    
