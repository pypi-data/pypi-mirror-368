import json
import logging
import os
import subprocess
import sys
import time
from typing import List

import dtiot_d2c.d2c.test.application as application_test
import dtiot_d2c.d2c.test.utils as tutils
import dtiot_d2c.dmo as dmo
from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.application import Application
from dtiot_d2c.d2c.application.consts import *
from dtiot_d2c.d2c.device.consts import *
from dtiot_d2c.d2c.get_response import GetResponse
from dtiot_d2c.d2c.test.testcli_base import TestCase, TestCLI_Base, TestSet
from dtiot_d2c.d2c.utils import color as color
from dtiot_d2c.dmo import ApiClient

log = logging.getLogger(__name__)
log_level = log.getEffectiveLevel() 

DESC = {
    "test-a01":"test-a01 - Create application without anything",
    "test-a02":"test-a02 - Create application with single url",
    "test-a03":"test-a03 - Create application with multiple urls",
    "test-a04":"test-a04 - Create application with urls and connection properties",
    "test-a04-short-header": "test-a04-short-header - Create application with urls and short connection properties",
    "test-a05": "test-a05 - Update current url",
    "test-a06": "test-a06 - Add url",
    "test-a07": "test-a07 - Delete url",
    "test-a08": "test-a08 - Add connection property",
    "test-a08-short-header": "test-a08-short-header - Add connection property with short header",
    "test-a09": "test-a09 - Modify connection property",
    "test-a09-short-header": "test-a09-short-header - Modify connection property with short header",
    "test-a10": "test-a10 - Delete connection property",
    "test-a11": "test-a11 - Delete application",
    "test-a12": "test-a12 - Re-create application with the same name",
}
        
class Test_Base(TestSet):
    def __init__(self, api: ApiClient, test_name:str, test_cfg_name:str):
        super().__init__(api, test_name)
        self._test_cfg_name = test_cfg_name
    def get_sample_configuration_varname(self)->str:
        return self._test_cfg_name
    def test_pre_cleanup(self, cfg:dict)->str:
        application_test.delete_application(self.api, cfg.get("name"))
    def test_post_cleanup(self, cfg:dict)->str:
        application_test.delete_application(self.api, cfg.get("name"))

class Test_Base_CLI(TestCLI_Base):
    def __init__(self, test_class, description:str):
        self._description = description
        self._test_class = test_class 
    def get1LineHelp(self):
        return self._description
    def get_test_set(self, api: ApiClient):
        return self._test_class(api)
        
###
# MARK: Test Case A01
###    
class ApplicationTest_A01(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A01", "ApplicationCfg_A01")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A01_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A01, DESC.get("test-a01"))
###
# MARK: Test Case A02
###    
class ApplicationTest_A02(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A02", "ApplicationCfg_A02")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A02_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A02, DESC.get("test-a02"))
###
# MARK: Test Case A03
###    
class ApplicationTest_A03(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A03", "ApplicationCfg_A03")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A03_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A03, DESC.get("test-a03"))
###
# MARK: Test Case A04
###    
class ApplicationTest_A04(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A04", "ApplicationCfg_A04")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A04_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A04, DESC.get("test-a04"))
###
# MARK: Test Case A04 short header
###    
class ApplicationTest_A04_short_header(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A04 short header", "ApplicationCfg_A04_short_header")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A04_CLI_short_header(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A04_short_header, DESC.get("test-a04-short-header"))
###
# MARK: Test Case A05
###    
class ApplicationTest_A05(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A05", "ApplicationCfg_A05")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
            application_test.TestCase_ModifyApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A05_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A05, DESC.get("test-a05"))
###
# MARK: Test Case A06
###    
class ApplicationTest_A06(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A06", "ApplicationCfg_A06")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
            application_test.TestCase_ModifyApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A06_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A06, DESC.get("test-a06"))
###
# MARK: Test Case A07
###    
class ApplicationTest_A07(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A07", "ApplicationCfg_A07")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
            application_test.TestCase_ModifyApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A07_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A07, DESC.get("test-a07"))
###
# MARK: Test Case A08
###    
class ApplicationTest_A08(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A08", "ApplicationCfg_A08")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
            application_test.TestCase_ModifyApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A08_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A08, DESC.get("test-a08"))
###
# MARK: Test Case A08 short header
###    
class ApplicationTest_A08_short_header(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A08 short header", "ApplicationCfg_A08_short_header")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
            application_test.TestCase_ModifyApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A08_CLI_short_header(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A08_short_header, DESC.get("test-a04-short-header"))
###
# MARK: Test Case A09
###    
class ApplicationTest_A09(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A09", "ApplicationCfg_A09")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
            application_test.TestCase_ModifyApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A09_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A09, DESC.get("test-a09"))
###
# MARK: Test Case A09 short header
###    
class ApplicationTest_A09_short_header(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A09 short header", "ApplicationCfg_A09_short_header")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
            application_test.TestCase_ModifyApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A09_CLI_short_header(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A09_short_header, DESC.get("test-a09-short-header"))
###
# MARK: Test Case A10
###    
class ApplicationTest_A10(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A10", "ApplicationCfg_A10")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
            application_test.TestCase_ModifyApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A10_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A10, DESC.get("test-a10"))
###
# MARK: Test Case A11
###    
class ApplicationTest_A11(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A11", "ApplicationCfg_A11")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
            application_test.TestCase_DeleteApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A11_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A11, DESC.get("test-a11"))
###
# MARK: Test Case A12
###    
class ApplicationTest_A12(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test A12", "ApplicationCfg_A12")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
            application_test.TestCase_DeleteApplication(api=self.api, cfg=cfg),
            application_test.TestCase_CreateApplication(api=self.api, cfg=cfg),
        ]
class ApplicationTest_A12_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(ApplicationTest_A12, DESC.get("test-a12"))
        
