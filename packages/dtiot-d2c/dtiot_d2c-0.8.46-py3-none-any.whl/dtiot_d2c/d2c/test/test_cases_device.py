import json
import logging
import sys
import time
from typing import List

import dtiot_d2c.d2c.test.device as device_test
import dtiot_d2c.d2c.test.utils as tutils
import dtiot_d2c.dmo as dmo
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.device import Device
from dtiot_d2c.d2c.device.consts import *
from dtiot_d2c.d2c.test.testcli_base import TestCase, TestCLI_Base, TestSet
from dtiot_d2c.d2c.utils import color as color
from dtiot_d2c.dmo import ApiClient

log = logging.getLogger(__name__)
log_level = log.getEffectiveLevel() 

DESC = {
    "test-d01":"test-d01: create device without anything",
    "test-d02":"test-d02: create device with psk credentials",
    "test-d03":"test-d03: create device with various dvi attributes",
    "test-d04":"test-d04: create device with uplink properties",
    "test-d05":"test-d05: create device with device properties",
    "test-d06":"test-d06: Update device dvi attributes",
    "test-d07":"test-d07: Update device device by adding device properties",
    "test-d08":"test-d08: Update device device by updating device properties",
    "test-d09":"test-d09: Update device by deleting device properties",
    "test-d10":"test-d10: Update device by adding uplink properties",
    "test-d11":"test-d11: Update device by updating uplink properties",
    "test-d13":"test-d13: Delete device",
    "test-d14":"test-d14: Re-create device with same name",
    "test-d15":"test-d15: Inject JSON uplink message",
}    

class Test_Base(TestSet):
    def __init__(self, api: ApiClient, test_name:str, test_cfg_name:str):
        super().__init__(api, test_name)
        self._test_cfg_name = test_cfg_name
    def get_sample_configuration_varname(self)->str:
        return self._test_cfg_name

    def test_cleanup(self, cfg:dict)->str:
        name = cfg.get("name")
        def operation():
            if (device := Device.get(self.api, name=name)):
                Device.delete(self.api, name=name)
            return None
        return tutils.exec_test(f"Deleting device {name}", operation)

    def test_pre_cleanup(self, cfg:dict):
        self.test_cleanup(cfg)

    def test_post_cleanup(self, cfg:dict)->str:
        self.test_cleanup(cfg)
class Test_Base_CLI(TestCLI_Base):
    def __init__(self, test_class, description:str):
        self._description = description
        self._test_class = test_class 
    def get1LineHelp(self):
        return self._description
    def get_test_set(self, api: ApiClient):
        return self._test_class(api)
        
###
# MARK: Test Case D01
###    
class DeviceTest_D01(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D01", "DeviceCfg_D01")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
        ]
class DeviceTest_D01_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D01, DESC.get("test-d01"))
###
# MARK: Test Case D02
###    
class DeviceTest_D02(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D02", "DeviceCfg_D02")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
        ]
class DeviceTest_D02_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D02, DESC.get("test-d02"))
###
# MARK: Test Case D03
###    
class DeviceTest_D03(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D03", "DeviceCfg_D03")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
        ]
class DeviceTest_D03_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D03, DESC.get("test-d03"))
###
# MARK: Test Case D04
###    
class DeviceTest_D04(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D04", "DeviceCfg_D04")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
        ]
class DeviceTest_D04_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D04, DESC.get("test-d04"))
###
# MARK: Test Case D05
###    
class DeviceTest_D05(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D05", "DeviceCfg_D05")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
        ]
class DeviceTest_D05_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D05, DESC.get("test-d05"))
###
# MARK: Test Case D06
###    
class DeviceTest_D06(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D06", "DeviceCfg_D06")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
            device_test.TestCase_ModifyDevice(api=self.api, cfg=cfg),            
        ]
class DeviceTest_D06_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D06, DESC.get("test-d06"))
###
# MARK: Test Case D07
###    
class DeviceTest_D07(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D07", "DeviceCfg_D07")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
            device_test.TestCase_ModifyDevice(api=self.api, cfg=cfg),                  
        ]
class DeviceTest_D07_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D07, DESC.get("test-d07"))
###
# MARK: Test Case D08
###    
class DeviceTest_D08(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D08", "DeviceCfg_D08")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
            device_test.TestCase_ModifyDevice(api=self.api, cfg=cfg),                  
        ]
class DeviceTest_D08_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D08, DESC.get("test-d08"))
###
# MARK: Test Case D09
###    
class DeviceTest_D09(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D09", "DeviceCfg_D09")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
            device_test.TestCase_ModifyDevice(api=self.api, cfg=cfg),                  
        ]
class DeviceTest_D09_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D09, DESC.get("test-d09"))
###
# MARK: Test Case D10
###    
class DeviceTest_D10(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D10", "DeviceCfg_D10")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
            device_test.TestCase_ModifyDevice(api=self.api, cfg=cfg),                  
        ]
class DeviceTest_D10_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D10, DESC.get("test-d10"))
###
# MARK: Test Case D11
###    
class DeviceTest_D11(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D11", "DeviceCfg_D11")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
            device_test.TestCase_ModifyDevice(api=self.api, cfg=cfg),                  
        ]
class DeviceTest_D11_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D11, DESC.get("test-d11"))
###
# MARK: Test Case D13
###    
class DeviceTest_D13(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D13", "DeviceCfg_D13")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
            tutils.TestCase_Sleep(api=self.api, cfg=cfg, run_info="Sleep to let d2c service create device in IMPACT"),
            device_test.TestCase_DeleteDevice(api=self.api, cfg=cfg)
        ]
class DeviceTest_D13_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D13, DESC.get("test-d13"))
###
# MARK: Test Case D14
###    
class DeviceTest_D14(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D14", "DeviceCfg_D14")

    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
            tutils.TestCase_Sleep(api=self.api, cfg=cfg, run_info="Sleep to let d2c service create device in IMPACT"),
            device_test.TestCase_DeleteDevice(api=self.api, cfg=cfg),
            tutils.TestCase_Sleep(api=self.api, cfg=cfg, run_info="Sleep to let d2c service delete the device in IMPACT"),
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
            tutils.TestCase_Sleep(api=self.api, cfg=cfg, run_info="Sleep to let d2c service create device in IMPACT"),
            device_test.TestCase_DeleteDevice(api=self.api, cfg=cfg)
        ]
class DeviceTest_D14_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D14, DESC.get("test-d14"))
       
       
###
# MARK: Test Case D15
###    
class DeviceTest_D15(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test D15", "DeviceCfg_D15")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg),
            device_test.TestCase_InjectUplinkMessage(api=self.api, cfg=cfg),
        ]
class DeviceTest_D15_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceTest_D15, DESC.get("test-d15"))       