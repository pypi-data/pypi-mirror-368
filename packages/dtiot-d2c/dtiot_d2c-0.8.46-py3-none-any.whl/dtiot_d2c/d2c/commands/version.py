import json
import logging
import sys
from argparse import ArgumentParser

from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface, CmdLineInterface

log = logging.getLogger(__name__)
            
import dtiot_d2c.d2c as d2c


#####################################################################################                
class VersionCLI(CmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Prints the version infos."
    
    def addCmdLineArgs(self, argsParser):
        pass

    def main(self, cmdargs=None):
        print(json.dumps(d2c.get_version_info(), indent=4))

        

            
            
            
