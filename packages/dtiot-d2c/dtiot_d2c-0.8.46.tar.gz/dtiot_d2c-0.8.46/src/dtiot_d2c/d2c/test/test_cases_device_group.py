import json
import logging
import sys
import time
from typing import List

import dtiot_d2c.d2c.test.application as application_test
import dtiot_d2c.d2c.test.device as device_test
import dtiot_d2c.d2c.test.device_group as device_group_test
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
    "test-dg01":"test-dg01 - Create device group without anything",
    "test-dg02":"test-dg02 - Create device group with description",
    "test-dg03":"test-dg03 - Modify description of device group",
    "test-dg04":"test-dg04 - Add 1 application to device group",
    "test-dg05-long":"test-dg05-long - Add 1 device to a device group with 1 application - with long names",
    "test-dg05-short":"test-dg05-short - Add 1 device to a device group with 1 application - with short names",
    "test-dg06-short":"test-dg06-short - Add 2 devices to a device group with 1 application - with short names",
    "test-dg07-short":"test-dg07-short - Add 1 devices to a device group with 2 application - with short names",
    "test-dg08-short":"test-dg08-short - Add 2 devices to a device group with 2 application - with short names",
    "test-dg09-short":"test-dg09-short - Add 1 devices to a device group with 0 application - with short names",
    "test-dg10-short":"test-dg10-short - Add 1 application to a device group with 1 device - with short names",
    "test-dg11-short":"test-dg11-short - Add 2 application to a device group with 2 device - with short names",
    "test-dg15-short":"test-dg15-short - Remove 2 devices from device group with 2 applications - with short names",
    "test-dg16-short":"test-dg16-short - Remove 2 applications from device group with 2 devices - with short names",
    "test-dg17-short":"test-dg17-short - Inject an uplink message to a device which is in a device group with 1 applications",
    "test-dg18-short":"test-dg18-short - Inject an uplink message to a device which is in a device group with 2 applications",
    "test-dg20":"test-dg20 - Delete device group",
    "test-dg21":"test-dg21 - Re-create a device group with the same name",
}    

class Test_Base(TestSet):
    def __init__(self, api: ApiClient, test_name:str, test_cfg_name:str):
        super().__init__(api, test_name)
        self._test_cfg_name = test_cfg_name
    def get_sample_configuration_varname(self)->str:
        return self._test_cfg_name

    def test_cleanup(self, cfg:dict):
        device_group_test.delete_device_group(self.api, cfg.get("name"))
        
    def test_pre_cleanup(self, cfg:dict):
        self.test_cleanup(cfg)
        
    def test_post_cleanup(self, cfg:dict):
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
# MARK: Test Case DG01
###    
class DeviceGroupTest_DG01(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG01", "DeviceGroupCfg_DG01")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
        ]
class DeviceGroupTest_DG01_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG01, DESC.get("test-dg01"))
        
###
# MARK: Test Case DG20
###    
class DeviceGroupTest_DG20(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG20", "DeviceGroupCfg_DG20")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            device_group_test.TestCase_DeleteDeviceGroup(api=self.api, cfg=cfg),
        ]
class DeviceGroupTest_DG20_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG20, DESC.get("test-dg20"))

###
# MARK: Test Case DG21
###    
class DeviceGroupTest_DG21(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG21", "DeviceGroupCfg_DG21")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            device_group_test.TestCase_DeleteDeviceGroup(api=self.api, cfg=cfg),
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),

        ]
class DeviceGroupTest_DG21_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG21, DESC.get("test-dg21"))
                        
###
# MARK: Test Case DG02
###    
class DeviceGroupTest_DG02(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG02", "DeviceGroupCfg_DG02")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
        ]
class DeviceGroupTest_DG02_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG02, DESC.get("test-dg02"))        
###
# MARK: Test Case DG03
###    
class DeviceGroupTest_DG03(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG03", "DeviceGroupCfg_DG03")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            device_group_test.TestCase_ModifyDeviceGroup(api=self.api, cfg=cfg),
        ]
class DeviceGroupTest_DG03_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG03, DESC.get("test-dg03"))   
###
# MARK: Test Case DG04
###    
class DeviceGroupTest_DG04(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG04", "DeviceGroupCfg_DG04")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                  device_group_cfg=cfg, 
                                                  application_cfgs=[cfg.get("application_1")]),            
        ]
    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        application_test.delete_application(self.api, cfg.get("application_1").get("name"))

class DeviceGroupTest_DG04_CLI(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG04, DESC.get("test-dg04"))                    
###
# MARK: Test Case DG05 long names
###    
class DeviceGroupTest_DG05_long(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG05 long", "DeviceGroupCfg_DG05_long")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_1")]),  
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_1")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_1")],
                                            verify_application_cfgs=[cfg.get("application_1")]),                   
        ]
    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        application_test.delete_application(self.api, cfg.get("application_1").get("name"))
        device_test.delete_device(self.api, cfg.get("device_1").get("name"))
class DeviceGroupTest_DG05_CLI_long(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG05_long, DESC.get("test-dg05-long"))  
###
# MARK: Test Case DG05 short names
###    
class DeviceGroupTest_DG05_short(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG05 short", "DeviceGroupCfg_DG05_short")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_1")]),  
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_1")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_1")],
                                            verify_application_cfgs=[cfg.get("application_1")]),                   
        ]
    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        application_test.delete_application(self.api, cfg.get("application_1").get("name"))
        device_test.delete_device(self.api, cfg.get("device_1").get("name"))
class DeviceGroupTest_DG05_CLI_short(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG05_short, DESC.get("test-dg05-short"))          
###
# MARK: Test Case DG06 short names
###    
class DeviceGroupTest_DG06_short(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG06 short", "DeviceGroupCfg_DG06_short")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_1")]),  
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_1")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_1")],
                                            verify_application_cfgs=[cfg.get("application_1")]),    
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_2")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_2")],
                                            verify_application_cfgs=[cfg.get("application_1")]),                   
        ]
    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        application_test.delete_application(self.api, cfg.get("application_1").get("name"))
        device_test.delete_device(self.api, cfg.get("device_1").get("name"))
        device_test.delete_device(self.api, cfg.get("device_2").get("name"))
class DeviceGroupTest_DG06_CLI_short(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG06_short, DESC.get("test-dg06-short"))          
###
# MARK: Test Case DG07 short names
###    
class DeviceGroupTest_DG07_short(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG07 short", "DeviceGroupCfg_DG07_short")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_1")]),  
            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_2")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_2")]),  
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_1")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_1")],
                                            verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]),    
        ]
    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        application_test.delete_application(self.api, cfg.get("application_1").get("name"))
        application_test.delete_application(self.api, cfg.get("application_2").get("name"))
        device_test.delete_device(self.api, cfg.get("device_1").get("name"))
class DeviceGroupTest_DG07_CLI_short(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG07_short, DESC.get("test-dg07-short"))          
###
# MARK: Test Case DG08 short names
###    
class DeviceGroupTest_DG08_short(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG08 short", "DeviceGroupCfg_DG08_short")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_1")]),  
            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_2")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_2")]),  
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_1")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_1")],
                                            verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]),    
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_2")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_2")],
                                            verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]),    
        ]
    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        application_test.delete_application(self.api, cfg.get("application_1").get("name"))
        application_test.delete_application(self.api, cfg.get("application_2").get("name"))
        device_test.delete_device(self.api, cfg.get("device_1").get("name"))
        device_test.delete_device(self.api, cfg.get("device_2").get("name"))
class DeviceGroupTest_DG08_CLI_short(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG08_short, DESC.get("test-dg08-short"))          
        
###
# MARK: Test Case DG09 short names
###    
class DeviceGroupTest_DG09_short(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG09 short", "DeviceGroupCfg_DG09_short")
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            # device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            # device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
            #                                                         device_group_cfg=cfg, 
            #                                                         application_cfgs=[cfg.get("application_1")]),  
            # device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_2")),
            # device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
            #                                                         device_group_cfg=cfg, 
            #                                                         application_cfgs=[cfg.get("application_2")]),  
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_1")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_1")],
                                            #verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]
                                            ),    
            # device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_2")),      
            # device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
            #                                 device_group_cfg=cfg, 
            #                                 device_cfgs=[cfg.get("device_2")],
            #                                 verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]
            #                                 ),    
        ]
    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        # application_test.delete_application(self.api, cfg.get("application_1").get("name"))
        # application_test.delete_application(self.api, cfg.get("application_2").get("name"))
        device_test.delete_device(self.api, cfg.get("device_1").get("name"))
        # device_test.delete_device(self.api, cfg.get("device_2").get("name"))
class DeviceGroupTest_DG09_CLI_short(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG09_short, DESC.get("test-dg09-short"))        
###
# MARK: Test Case DG10 short names
###    
class DeviceGroupTest_DG10_short(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG10 short", "DeviceGroupCfg_DG10_short") 
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_1")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_1")],
                                            #verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]
                                            ),    
            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_1")],
                                                                    verify_device_cfgs=[cfg.get("device_1")]),  

            # device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_2")),
            # device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
            #                                                         device_group_cfg=cfg, 
            #                                                         application_cfgs=[cfg.get("application_2")]),  
            #                                ),    
            # device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_2")),      
            # device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
            #                                 device_group_cfg=cfg, 
            #                                 device_cfgs=[cfg.get("device_2")],
            #                                 verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]
            #                                 ),    
        ]
    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        device_test.delete_device(self.api, cfg.get("device_1").get("name"))
        # device_test.delete_device(self.api, cfg.get("device_2").get("name"))
        application_test.delete_application(self.api, cfg.get("application_1").get("name"))
        # application_test.delete_application(self.api, cfg.get("application_2").get("name"))
class DeviceGroupTest_DG10_CLI_short(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG10_short, DESC.get("test-dg10-short"))        

###
# MARK: Test Case DG11 short names
###    
class DeviceGroupTest_DG11_short(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG11 short", "DeviceGroupCfg_DG11_short") 
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_1")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_1")],
                                            #verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]
                                            ),    

            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_2")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_2")],
                                            #verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]
                                            ),    


            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_1")],
                                                                    verify_device_cfgs=[cfg.get("device_1"), cfg.get("device_2")]),  

            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_2")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_2")],
                                                                    verify_device_cfgs=[cfg.get("device_1"), cfg.get("device_2")]),              
        ]
    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        device_test.delete_device(self.api, cfg.get("device_1").get("name"))
        device_test.delete_device(self.api, cfg.get("device_2").get("name"))
        application_test.delete_application(self.api, cfg.get("application_1").get("name"))
        application_test.delete_application(self.api, cfg.get("application_2").get("name"))
class DeviceGroupTest_DG11_CLI_short(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG11_short, DESC.get("test-dg11-short"))        

###
# MARK: Test Case DG15 short names
###    
class DeviceGroupTest_DG15_short(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG15 short", "DeviceGroupCfg_DG15_short") 
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_1")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_1")],
                                            #verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]
                                            ),    

            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_2")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_2")],
                                            #verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]
                                            ),    


            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_1")],
                                                                    verify_device_cfgs=[cfg.get("device_1"), cfg.get("device_2")]),  

            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_2")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_2")],
                                                                    verify_device_cfgs=[cfg.get("device_1"), cfg.get("device_2")]), 
            
            device_group_test.TestCase_RemoveDevicesFromDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    device_cfgs=[cfg.get("device_1")],
                                                                    verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]),                         
            device_group_test.TestCase_RemoveDevicesFromDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    device_cfgs=[cfg.get("device_2")],
                                                                    verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]),                         

        ]
    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        device_test.delete_device(self.api, cfg.get("device_1").get("name"))
        device_test.delete_device(self.api, cfg.get("device_2").get("name"))
        application_test.delete_application(self.api, cfg.get("application_1").get("name"))
        application_test.delete_application(self.api, cfg.get("application_2").get("name"))
class DeviceGroupTest_DG15_CLI_short(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG15_short, DESC.get("test-dg15-short"))        
###
# MARK: Test Case DG16 short names
###    
class DeviceGroupTest_DG16_short(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG16 short", "DeviceGroupCfg_DG16_short") 
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_1")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_1")],
                                            #verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]
                                            ),    

            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_2")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_2")],
                                            #verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]
                                            ),    


            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_1")],
                                                                    verify_device_cfgs=[cfg.get("device_1"), cfg.get("device_2")]),  

            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_2")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_2")],
                                                                    verify_device_cfgs=[cfg.get("device_1"), cfg.get("device_2")]), 
            
            # device_group_test.TestCase_RemoveDevicesFromDeviceGroup(api=self.api, 
            #                                                         device_group_cfg=cfg, 
            #                                                         device_cfgs=[cfg.get("device_1")],
            #                                                         verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]),                         
            # device_group_test.TestCase_RemoveDevicesFromDeviceGroup(api=self.api, 
            #                                                         device_group_cfg=cfg, 
            #                                                         device_cfgs=[cfg.get("device_2")],
            #                                                         verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]),       
            
            device_group_test.TestCase_RemoveApplicationsFromDeviceGroup(api=self.api, 
                                                                         device_group_cfg=cfg, 
                                                                         application_cfgs=[cfg.get("application_1")],
                                                                         verify_device_cfgs=[cfg.get("device_1"), cfg.get("device_2")]),                              
            device_group_test.TestCase_RemoveApplicationsFromDeviceGroup(api=self.api, 
                                                                         device_group_cfg=cfg, 
                                                                         application_cfgs=[cfg.get("application_2")],
                                                                         verify_device_cfgs=[cfg.get("device_1"), cfg.get("device_2")]),                              

        ]
    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        device_test.delete_device(self.api, cfg.get("device_1").get("name"))
        device_test.delete_device(self.api, cfg.get("device_2").get("name"))
        application_test.delete_application(self.api, cfg.get("application_1").get("name"))
        application_test.delete_application(self.api, cfg.get("application_2").get("name"))
class DeviceGroupTest_DG16_CLI_short(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG16_short, DESC.get("test-dg16-short"))        
                                
###
# MARK: Test Case DG17 short names
###    
class DeviceGroupTest_DG17_short(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG17 short", "DeviceGroupCfg_DG17_short") 
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            
            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_1")]), 
             
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_1")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_1")],
                                            verify_application_cfgs=[cfg.get("application_1")]),    

            tutils.TestCase_Sleep(api=self.api, cfg=cfg, run_info="Sleep to let d2c service bring uplink message forwarding in placed"),
            
            device_group_test.TestCase_InjectUplinkMessage(api=self.api,
                                                           device_group_cfg=cfg,
                                                           device_cfg=cfg.get("device_1"),
                                                           verify_application_cfgs=[cfg.get("application_1")],
                                                           ),
        ]

    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        device_test.delete_device(self.api, cfg.get("device_1").get("name"))
        application_test.delete_application(self.api, cfg.get("application_1").get("name"))
class DeviceGroupTest_DG17_CLI_short(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG17_short, DESC.get("test-dg17-short"))        

###
# MARK: Test Case DG18 short names
###    
class DeviceGroupTest_DG18_short(Test_Base):
    def __init__(self, api: ApiClient):
        super().__init__(api, "Test DG18 short", "DeviceGroupCfg_DG18_short") 
    def get_test_cases(self, cfg:dict)->List[TestCase]:
        return [
            device_group_test.TestCase_CreateDeviceGroup(api=self.api, cfg=cfg),
            
            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_1")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_1")]), 

            device_group_test.TestCase_CreateApplication(api=self.api, cfg=cfg.get("application_2")),
            device_group_test.TestCase_AddApplicationsToDeviceGroup(api=self.api, 
                                                                    device_group_cfg=cfg, 
                                                                    application_cfgs=[cfg.get("application_2")]), 
             
            device_test.TestCase_CreateDevice(api=self.api, cfg=cfg.get("device_1")),      
            device_group_test.TestCase_AddDevicesToDeviceGroup(api=self.api, 
                                            device_group_cfg=cfg, 
                                            device_cfgs=[cfg.get("device_1")],
                                            verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")]),    

            tutils.TestCase_Sleep(api=self.api, cfg=cfg, run_info="Sleep to let d2c service bring uplink message forwarding in placed"),
            
            device_group_test.TestCase_InjectUplinkMessage(api=self.api,
                                                           device_group_cfg=cfg,
                                                           device_cfg=cfg.get("device_1"),
                                                           verify_application_cfgs=[cfg.get("application_1"), cfg.get("application_2")],
                                                           ),
        ]

    def test_cleanup(self, cfg:dict)->str:
        device_group_test.delete_device_group(self.api, cfg.get("name"))   
        device_test.delete_device(self.api, cfg.get("device_1").get("name"))
        application_test.delete_application(self.api, cfg.get("application_1").get("name"))
        application_test.delete_application(self.api, cfg.get("application_2").get("name"))
class DeviceGroupTest_DG18_CLI_short(Test_Base_CLI):
    def __init__(self):
        super().__init__(DeviceGroupTest_DG18_short, DESC.get("test-dg18-short"))        
                                                                