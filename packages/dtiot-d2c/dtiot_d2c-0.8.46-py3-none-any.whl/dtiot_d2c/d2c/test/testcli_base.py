import json
import logging
import os
import sys
import time
from typing import Callable, ClassVar, List

from pydantic import BaseModel, Field

import dtiot_d2c.d2c.test.utils as tutils
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

class TestCase:
    def __init__(self, api: ApiClient, cfg:dict):
        self.api = api
        self.cfg = cfg

    def get_name(self):
        return "TestCase"
    
    def run(self):
        raise Exception("run() function requires implementation.")
    
    def verify(self):
        return None
    
class TestSet:
    def __init__(self, api: ApiClient, name:str):
        self.api = api
        self.name = name
        self.error_count = 0
    
    def get_sample_configuration_varname(self)->str:
        raise Exception("get_sample_configuration_varname() function requires implementation by child class.")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return []    
    
    def test_pre_cleanup(self, cfg:dict)->str:
        return None

    def test_post_cleanup(self, cfg:dict)->str:
        return None
        
    def run_all_tests(self, cfg:dict, **kwargs):
        number_of_test_loops:int = kwargs.get("number_of_test_loops", 1)
        skip_pre_cleanup:bool = kwargs.get("skip_pre_cleanup", False)
        skip_post_cleanup:bool = kwargs.get("skip_post_cleanup", False)
                
        if not skip_pre_cleanup:
            tutils.print_BOLD(f"*** PRE CLEANING UP ...")
            errmsg = None
            try:
                errmsg=self.test_pre_cleanup(cfg)
                #if not errmsg:
                #    tutils.print_OK()                

            except Exception as ex:
                errmsg = str(ex)

            if errmsg:
                tutils.print_ERROR(f"An error occured during pre cleaning up.")
                tutils.print_ERROR(errmsg)                
                return
                
            print("")
        else:
            tutils.print_BOLD(f"*** SKIPPING PRE CLEANING UP ...")
            
        ok_count = 0
        finished_with_errmsg = None
        start_time = time.time()

        for i in range(number_of_test_loops):

            if number_of_test_loops > 1:
                tutils.print_BOLD(f"*** TESTRUN {i + 1} of {number_of_test_loops} **********************************", flush=True)

            errmsg = None
            try:
                for tc in self.get_test_cases(cfg):
                    tc_name = tc.get_name()
                    tutils.print_BOLD(f"RUNNING {tc_name} ...")
                    tc.run()
                    print("")
                    tutils.print_BOLD(f"VERIFYING {tc_name} ...")                    
                    tc.verify()
                    print("")

            except Exception as ex:
                errmsg = str(ex)

            if errmsg:
                tutils.print_ERROR(f"An error occured. Stopping test during the {i+1}. run.")
                tutils.print_ERROR(errmsg)
                finished_with_errmsg = errmsg
                self.error_count += 1
                break
            else:
                ok_count += 1
                
        end_time = time.time()

        duration_total = end_time - start_time
        duration_per_run = (duration_total / ok_count) if ok_count > 0 else duration_total

        if not skip_post_cleanup:
            tutils.print_BOLD(f"*** POST CLEANING UP ...")
            errmsg = None
            try:
                errmsg=self.test_post_cleanup(cfg)
                #if not errmsg:
                #    tutils.print_OK()
                    
            except Exception as ex:
                errmsg = str(ex)

            if errmsg:
                tutils.print_ERROR(f"An error occured during post cleaning up.")
                tutils.print_ERROR(errmsg)             

            print("")
        else:
            tutils.print_BOLD(f"*** SKIPPING POST CLEANING UP ...")
            
        if not finished_with_errmsg:
            print_func = tutils.print_OK
            print_func(f"*** END OK ***")
        else:
            print_func = tutils.print_ERROR
            print_func(f"*** END ERROR ***")
            print_func(f"Error message:       {finished_with_errmsg}")
    
        print_func(f"Number of test runs: {ok_count}")
        print_func(f"Total time:          {duration_total:.4f} seconds ")
        print_func(f"Time per test run:   {duration_per_run:.4f} seconds")
class TestCLI_Base(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()
    
    def addCmdLineArgs(self, argsParser):
        argsParser.add_argument("-i", "--test-run-id", metavar="<string>", 
                                dest="run_id", required=True,
                                help="Id of the test run.")

        argsParser.add_argument("-cf", "--test-configuration-file", metavar="<file>", 
                                dest="config_file", required=False,
                                help="Python file which contains the configuration of the test.")

        argsParser.add_argument("-cd", "--test-configuration-dict", metavar="<variable-name>", 
                                dest="config_varname", required=False,
                                help="Name of the dictionary variable within the configuration file with the configuration.")

        argsParser.add_argument("-spr", "--skip-pre-cleanup", dest="skip_pre_cleanup", action="store_const", 
                                const=True, default=False,
                                help="If set, the pre cleanup function is skipped.")

        argsParser.add_argument("-spo", "--skip-post-cleanup", dest="skip_post_cleanup", action="store_const", 
                                const=True, default=False,
                                help="If set, the post cleanup function is skipped.")

        argsParser.add_argument("-n", "--number-of-test-runs", metavar="<integer>", 
                                dest="n", type=int, default=1,
                                help="Number of test runs. Default is 1.")

    def get_test_set(self, api: ApiClient)->TestSet:
        raise Exception("get_test_set() requires implementation in child class.")
        
    def main(self, cmdargs=None):
        print(f"################################################################################")
        print(f"#{self.get1LineHelp().center(78)}#")
        print(f"################################################################################")

        test_set:TestSet = self.get_test_set(self.apiConn)
        run_id = cmdargs.run_id

        # If no configuration file is defined use the sample configuration as default.
        config_file = cmdargs.config_file
        config_varname = cmdargs.config_varname

        if not config_file:
            config_file = f"{os.path.dirname(__file__)}/sample_test_configuration.py"
            config_varname = test_set.get_sample_configuration_varname()

        # Configuration file has been defined but no name of the configuration variable
        # within the configuration file is defined. 
        elif not config_varname:
            raise Exception(f"Command line option --test-configuration-dict required.")
        
        if cmdargs.n <= 0:
            raise Exception(f"Parameters -n or --number-of-test-runs shall be greater than 0.")
        else:
            n = cmdargs.n

        # Load the test configuration            
        cfg = tutils.load_test_configuration(run_id, config_file, config_varname)

        # Run all tests
        test_set.run_all_tests(cfg,
                               number_of_test_loops=cmdargs.n,
                               skip_pre_cleanup=cmdargs.skip_pre_cleanup,
                               skip_post_cleanup=cmdargs.skip_post_cleanup
                              )

        if test_set.error_count > 0:
            raise Exception(f"{test_set.error_count} errors occured during test run")
