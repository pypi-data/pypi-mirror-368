import sys
import json
import time
import logging

from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface
import dtiot_d2c.dmo as dmo
from dtiot_d2c.dmo import dmoCLI as dmocli

log = logging.getLogger(__name__)
            
def print_flushed(s:str, end=None):
    print(s, end=end)
    sys.stdout.flush() 
    
#####################################################################################                
class PerformanceTest_GetResourceCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Runs a test to verify the performance of getting a resource."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-rn")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-ri")

        argsParser.add_argument("-n", "--number-of-gets", metavar="<integer>", 
                                dest="n", type=int, default=1,
                                help="Number of gets requests. Default is 1.")

                
    def main(self, cmdargs=None):
        
        if cmdargs.n <= 0:
            raise Exception(f"Parameters -n or --number-of-gets shall be greater than 0.")

        print(f"*** START ***")
        start_time = time.time()
        for i in range(cmdargs.n):
            print_flushed(f"{i + 1} ... ", end="")

            dmo.get_resources(self.apiConn, 
                              origin=cmdargs.origin, 
                              resourceId=cmdargs.ri, 
                              resourceName=cmdargs.rn)

        end_time = time.time()

        duration_total = end_time - start_time
        duration_per_get = duration_total / cmdargs.n 
        print("")
        print(f"*** END ***")
        print(f"  Resource:               {cmdargs.rn or cmdargs.ri}")
        print(f"  Number of get requests: {cmdargs.n}")
        print(f"  Total time:             {duration_total:.4f} seconds ")
        print(f"  Time per get request:   {duration_per_get:.4f} seconds")
        print("")
