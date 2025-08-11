
import logging

import dtiot_d2c.cli.CFG as CFG
import dtiot_d2c.cli.utils as utils
from dtiot_d2c.cli.cli_command import CLICommands as clicmds
from dtiot_d2c.cli.cli_command import CmdLineInterface
from dtiot_d2c.cli.config import Configuration
from dtiot_d2c.cli.profileCLI import *

log = logging.getLogger(__name__)

#################################################################
# Create Configuration
#################################################################
class CreateConfigurationCLI(CmdLineInterface):
    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return f"Creates a new configuration in a directory or in ~/{CFG.DEFAULT_CFGDIR_NAME}."
    
    def addCmdLineArgs(self, argsParser):

        argsParser.add_argument("--config-directory", metavar='<directory>', dest="directory", 
                                help="Directory in which the new configuration shall be created.")

        argsParser.add_argument("--overwrite", dest="overwrite", action="store_const", const=True,
                                default=False, 
                                help="If set an existing configuration file is overwritten.")

    def main(self, cmdargs=None):
        log.debug("=> CreateConfigurationCLI()")

        # Create the configuration
        config  = Configuration.create(configDir=cmdargs.directory, overwrite=cmdargs.overwrite)

        #  Let the user add a new profile
        profile = NewProfileCLI().main(config=config)

        # Activate profile
        ActivateProfileCLI().main(config=config, profile=profile)

        return config

