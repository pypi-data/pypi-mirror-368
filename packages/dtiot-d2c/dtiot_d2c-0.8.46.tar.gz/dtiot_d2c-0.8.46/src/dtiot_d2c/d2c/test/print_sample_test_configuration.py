import json
import logging
import os
import sys
import time

import dtiot_d2c.d2c.test.utils as tutils
import dtiot_d2c.dmo as dmo
from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface
from dtiot_d2c.d2c import CMDARGS
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.application import Application
from dtiot_d2c.d2c.device.consts import *
from dtiot_d2c.d2c.get_response import GetResponse
from dtiot_d2c.dmo import ApiClient
from dtiot_d2c.dmo import dmoCLI as dmocli

log = logging.getLogger(__name__)
            
def print_flushed(s:str, end=None):
    print(s, end=end)
    sys.stdout.flush() 

class PrintSampleTestConfigurationCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()
        
    def get1LineHelp(self):
        return "Prints a sample configuration for all test cases."
        
    def addCmdLineArgs(self, argsParser):
        argsParser.add_argument("-co", "--config-outfile", metavar="<file>", 
                                dest="out_filepath", required=False,
                                help="File into which the sample test configuration shall be written to. If not defined it is writtten to stdout.")

    def main(self, cmdargs=None):

        config_filepath = f"{os.path.dirname(__file__)}/sample_test_configuration.py"
        in_file = open(config_filepath, "r")
        
        if not cmdargs.out_filepath:
            print(in_file.read())
        else:
            out_file = open(cmdargs.out_filepath, "w")     
            out_file.write(in_file.read())
            out_file.close()
