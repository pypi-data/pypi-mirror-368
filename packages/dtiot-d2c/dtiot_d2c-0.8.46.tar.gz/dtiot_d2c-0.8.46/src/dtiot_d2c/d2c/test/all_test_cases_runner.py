import json
import logging

import dtiot_d2c.d2c.test.utils as tutils
import dtiot_d2c.dmo as dmo
from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.application import Application
from dtiot_d2c.d2c.application.consts import *
from dtiot_d2c.d2c.device.consts import *
from dtiot_d2c.d2c.test.test_cases_application import DESC as APPL_DESC
from dtiot_d2c.d2c.test.test_cases_device import DESC as DEV_DESC
from dtiot_d2c.d2c.test.test_cases_device_group import DESC as DEVGRP_DESC
from dtiot_d2c.d2c.utils import color as color

log = logging.getLogger(__name__)
log_level = log.getEffectiveLevel() 

class AllTestCasesRunner_CLI(ApiConnCmdLineInterface):
    def get1LineHelp(self):
        return "Runs the test cases of a single or all test objects."

    def addCmdLineArgs(self, argsParser):

        argsParser.add_argument("-to", "--test-object", metavar="<test-object>", 
                                dest="test_object", required=True,
                                choices= ["application", "device", "devicegroup", "all"],
                                help="Test object which test cases shall be run. Possible values are application, device, devicegroup, all")

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

    def main(self, cmdargs=None):
        
        if cmdargs.test_object == "application":
            DESC = APPL_DESC
        elif cmdargs.test_object == "device":
            DESC = DEV_DESC
        elif cmdargs.test_object == "devicegroup":
            DESC = DEVGRP_DESC
        elif cmdargs.test_object == "all":
            DESC = {}
            DESC.update(APPL_DESC)
            DESC.update(DEV_DESC)
            DESC.update(DEVGRP_DESC)
        
        # Build args
        args = []
        if cmdargs.skip_pre_cleanup:
            args.append("--skip-pre-cleanup")            
        if cmdargs.skip_post_cleanup:
            args.append("--skip-post-cleanup")            

        # Build kwargs
        kwargs = {}
        if cmdargs.config_file:
            kwargs["--test-configuration-file"] = cmdargs.config_file            
        if cmdargs.config_varname:
            kwargs["--test-configuration-dict"] = cmdargs.config_varname            
        if cmdargs.n:
            kwargs["--number-of-test-runs"] = cmdargs.n            

        kwargs["--test-run-id"] = cmdargs.run_id

        ok_tests = []
        error_tests = []

        for test_name, test_desc in DESC.items():
            kwargs["--test-run-id"] = int(kwargs["--test-run-id"]) + 1
            exit_code = tutils.exec_test_case(test_name, *args, **kwargs)
            if exit_code == 0:
                ok_tests.append(test_name)
            else:
                error_tests.append(test_name)

        print("")        
        print(f"{'='*80}")
        print(f"Ok Tests: {len(ok_tests)} / {len(DESC)} ")
        for t in ok_tests:
            print(f"  {DESC[t]}")

        print("")

        print(f"Error Tests:  {len(error_tests)} / {len(DESC)} ")
        for t in error_tests:
            print(f"  {DESC[t]}")
        
                       


