import json
import logging
import sys
import time
from typing import List

import dtiot_d2c.d2c.test.utils as tutils
import dtiot_d2c.dmo as dmo
from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface
from dtiot_d2c.d2c import CMDARGS
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.device import Device
from dtiot_d2c.d2c.device.consts import *
from dtiot_d2c.d2c.get_response import GetResponse
from dtiot_d2c.d2c.test.testcli_base import TestCase, TestCLI_Base, TestSet
from dtiot_d2c.dmo import ApiClient
from dtiot_d2c.dmo import dmoCLI as dmocli

log = logging.getLogger(__name__)
log_level = log.getEffectiveLevel() 

def verify_device_communication(api:ApiClient, name:str):
    '''
    device-communication/<name> = 
    {
        "mbs": 1000000,
        "mni": 100,
        "rn": "device01-112",
        "ty": 3,
        "st": 0,
        "cbs": 0,
        "cni": 0,
        "cr": "CDevice-Provisioning",
        "ri": "67ffeee60aced48199fa7087",
        "pi": "67f641e2bbad596bd91446e3",
        "ct": "20250416T175446,849000",
        "lt": "20250416T175446,849000",
        "m2m:cnt": [
            {
                "mbs": 1000000,
                "mni": 100,
                "rn": "outgoing-msg",
                "ty": 3,
                "st": 0,
                "cbs": 0,
                "cni": 0,
                "cr": "CDevice-Provisioning",
                "ri": "67ffeee60aced48199fa7089",
                "pi": "67ffeee60aced48199fa7087",
                "ct": "20250416T175446,902000",
                "lt": "20250416T175446,902000",
                "m2m:sub": [
                    {
                        "rn": "protocol-adapter-subscription",
                        "nct": 1,
                        "enc": {
                            "net": [
                                1,
                                2,
                                3,
                                4
                            ]
                        },
                        "nu": [
                            "http://d2c-protocol-adapter-scs-lwm2m.d2c.svc.cluster.local/node/TMNL.D2CDEV.DEV_D2C_ROOT_002.d2c-dev-3/device01-112/downlink-message"
                        ],
                        "su": "http://d2c-protocol-adapter-scs-lwm2m.d2c.svc.cluster.local:80/node/TMNL.D2CDEV.DEV_D2C_ROOT_002.d2c-dev-3/device01-112/downlink-message",
                        "ty": 23,
                        "ri": "67ffeee70aced48199fa7091",
                        "pi": "67ffeee60aced48199fa7089",
                        "ct": "20250416T175447,341000",
                        "lt": "20250416T175447,341000"
                    }
                ]
            },
            {
                "mbs": 1000000,
                "mni": 100,
                "rn": "received-msg",
                "ty": 3,
                "st": 0,
                "cbs": 0,
                "cni": 0,
                "cr": "CDevice-Provisioning",
                "ri": "67ffeee70aced48199fa708d",
                "pi": "67ffeee60aced48199fa7087",
                "ct": "20250416T175447,015000",
                "lt": "20250416T175447,015000"
            },
            {
                "mbs": 1000000,
                "mni": 100,
                "rn": "sent-msg",
                "ty": 3,
                "st": 0,
                "cbs": 0,
                "cni": 0,
                "cr": "CDevice-Provisioning",
                "ri": "67ffeee60aced48199fa708b",
                "pi": "67ffeee60aced48199fa7087",
                "ct": "20250416T175446,958000",
                "lt": "20250416T175446,958000"
            }
        ]
    }        
    '''
    ###
    # Check the toplevel device-communication container of the device
    n = f"device-communication/{name}"
    def operation():
        onem2m_dict = dmo.get_resources(api_client=api, resourceName=n)
        if not onem2m_dict:
            raise Exception(f"Couldn't get resource {n}.")
        else:
            return onem2m_dict
    onem2m_dict:dict = tutils.exec_test(f"Getting device communication container {n}", operation)        

    ###
    # Check the device-communication/<name>/outgoing-msg container (downlink inbound)
    n = f"device-communication/{name}/outgoing-msg"
    def operation():
        onem2m_dict = dmo.get_resources(api_client=api, resourceName=n)
        if not onem2m_dict:
            raise Exception(f"Couldn't get resource {n}.")
        else:
            return onem2m_dict
    onem2m_dict:dict = tutils.exec_test(f"Getting device communication container {n}", operation)        

    ###
    # Is there an outgoing subscription to forward messages to the southbound adapter ?
    n = f"device-communication/{name}/outgoing-msg/protocol-adapter-subscription"
    def operation():
        onem2m_dict = dmo.get_resources(api_client=api, resourceType="subscription", resourceName=n)
        if not onem2m_dict:
            raise Exception(f"Couldn't get subscription {n}.")
        else:
            return onem2m_dict
    onem2m_dict:dict = tutils.exec_test(f"Getting protocol adapter subscription {n}", operation)      
    
    ###        
    # Check the device-communication/<name>/received-msg container (uplink inbound)
    n = f"device-communication/{name}/received-msg"
    def operation():
        onem2m_dict = dmo.get_resources(api_client=api, resourceName=n)
        if not onem2m_dict:
            raise Exception(f"Couldn't get resource {n}.")
        else:
            return onem2m_dict
    onem2m_dict:dict = tutils.exec_test(f"Getting device communication container {n}", operation)               

    ###        
    # Check the device-communication/<name>/sent-msg container (downlink outbound)
    n = f"device-communication/{name}/sent-msg"
    def operation():
        onem2m_dict = dmo.get_resources(api_client=api, resourceName=n)
        if not onem2m_dict:
            raise Exception(f"Couldn't get resource {n}.")
        else:
            return onem2m_dict
    onem2m_dict:dict = tutils.exec_test(f"Getting device communication container {n}", operation)               
    
def verify_device(api: ApiClient, name:str, device_props:dict):
    '''
    {
        "ni": "urn:gsma:imei:device01-103",
        "lbl": [
            "profile:SCS-lwM2M",
            "ICCID:89374121317959919924",
            "UplinkProperty_address:Kuckhoffstr 114A, 13156 Berlin",
            "lastMaintenance:25.3.2025 13 00"
        ],
        "rn": "device01-103",
        "ty": 14,
        "ri": "67ffe2e3eab987515f7c3484",
        "pi": "d2c-dev-3",
        "ct": "20250416T170331,008000",
        "lt": "20250416T170335,841000",
        "m2m:crds": [
            {
                "dc": "cred",
                "mgd": 1029,
                "rn": "credentials",
                "ty": 13,
                "ri": "67ffe2e3eab987515f7c348a",
                "pi": "67ffe2e3eab987515f7c3484",
                "ct": "20250416T170331,436000",
                "lt": "20250416T170331,436000",
                "crid": "device01-103",
                "crse": "Q3hhc21FTUw3NFNiUlIzUw=="
            }
        ],
        "m2m:sub": [
            {
                "rn": "device-update-subscription",
                "nct": 1,
                "enc": {
                    "net": [
                        1,
                        2,
                        3,
                        4
                    ]
                },
                "nu": [
                    "http://d2c-device-provisioning.d2c.svc.cluster.local/provisioning/node"
                ],
                "su": "http://d2c-device-provisioning.d2c.svc.cluster.local:80/provisioning/node",
                "ty": 23,
                "ri": "67ffe2e3eab987515f7c3488",
                "pi": "67ffe2e3eab987515f7c3484",
                "ct": "20250416T170331,325000",
                "lt": "20250416T170331,325000"
            }
        ],
        "m2m:dvi": [
            {
                "rn": "device01-103",
                "mgd": 1007,
                "loc": "geo:25.245470,51.454009",
                "dty": "Pretty Device",
                "dlb": "this is a label",
                "dvnm": "device01-103",
                "fwv": "fw 1.0.1",
                "swv": "sw 2.0.1",
                "osv": "os 3.0.1",
                "hwv": "2024.1 PC r1",
                "ptl": [
                    "LWM2M"
                ],
                "man": "PSsystec",
                "mod": "Smartbox Mini",
                "smod": "NB-IoT",
                "cnty": "DE",
                "ty": 13,
                "ri": "67ffe2e7eab987515f7c3490",
                "pi": "67ffe2e3eab987515f7c3484",
                "ct": "20250416T170335,053000",
                "lt": "20250416T170335,053000"
            }
        ]
    }        
    '''
    def operation():
        onem2m_dict = dmo.get_resources(api_client=api, resourceName=name)
        if not onem2m_dict:
            raise Exception(f"Node resource {name} couldn't be get after creation.")
        else:
            return onem2m_dict
    onem2m_dict:dict = tutils.exec_test(f"Getting ae {name}", operation)

    ###
    # Check node labels
    if (dev_props := device_props.get("device_properties_verify", None)) == None:
        dev_props = device_props.get("device_properties", {})
    if (upl_props := device_props.get("uplink_properties_verify", None)) == None:
        upl_props = device_props.get("uplink_properties", {})
        
    for (key, val) in [["profile", DEVICE_PROFILES.SCS_LWM2M],
                        ["ICCID", device_props.get("iccid", None)],
                        #*[(k, v) for (k, v) in dev_props.items()],
                        *[(f"UplinkProperty_{k}", v) for (k, v) in upl_props.items()],
                        *[(f"DeviceProperty_{k}", v) for (k, v) in dev_props.items()]                        
    ]:
        if val == None:
            continue
        elem_path = "lbl"
        elem_value = f"{key}:{val}"
        def operation():
            if not tutils.call_has_element_value(onem2m_dict, elem_path, elem_value):
                raise Exception(f"Value of element {elem_path} does not meet required value {elem_value}.")
        tutils.exec_test(f"Verifing {elem_path} for {elem_value}", operation)
                
    ###
    # Check dvi elements
    for (dvi_elem, cfg_elem) in [["man" ,"manufacturer"], 
                                    ["mod" ,"model"],
                                    ["smod" ,"sub_model"],
                                    ["hwv" ,"hardware_version"],
                                    ["cnty" ,"country"],
                                    #["dc" ,"description"],
                                    ["dlb" ,"label"],
                                    ["dty" ,"device_type"],
                                    ["dvnm" ,"device_name"],
                                    ["fwv" ,"firmware_version"],
                                    ["swv" ,"software_version"],
                                    ["osv" ,"os_version"],
                                    ["loc" ,"location"],
                                    #["ptl" ,"protocols"]
    ]:
        elem_path = f"m2m:dvi[0].{dvi_elem}"
        elem_value = device_props.get(cfg_elem, "__UNDEFINED__")

        if elem_value == "__UNDEFINED__":
            continue

        def operation():
            if not tutils.call_has_element_value(onem2m_dict, elem_path, elem_value):
                raise Exception(f"Value of element {elem_path} does not meet required value {elem_value}.")
        tutils.exec_test(f"Verifing {elem_path} for {elem_value}", operation)

    # elem_path = f"m2m:dvi[0].dvnm"
    # elem_value = name
    # def operation():
    #     if not tutils.call_has_element_value(onem2m_dict, elem_path, elem_value):
    #         raise Exception(f"Value of element {elem_path} does not meet required value {elem_value}.")
    # tutils.exec_test(f"Verifing {elem_path} for {elem_value}", operation)

    # Check credentials
    for (crds_elem, cfg_elem) in [["crid" ,"credentials_id"], 
                                  ["crse" ,"credentials_secret"],
    ]:
        elem_path = f"m2m:crds[0].{crds_elem}"
        elem_value = device_props.get(cfg_elem, "__UNDEFINED__")

        if elem_value == "__UNDEFINED__":
            continue

        def operation():
            if not tutils.call_has_element_value(onem2m_dict, elem_path, elem_value):
                raise Exception(f"Value of element {elem_path} does not meet required value {elem_value}.")
        tutils.exec_test(f"Verifing {elem_path} for {elem_value}", operation)

    return None

def delete_device(api:ApiClient, name:str):
    def operation():  
        if (application := Device.get(api, name=name)):
            Device.delete(api, name=name)
    tutils.exec_test(f"Deleting device {name}", operation)
    return None
class TestCase_CreateDevice(TestCase):
    def get_name(self):
        return "Create Device"
        
    def run(self):
        name = self.cfg.get("name")

        if (create_props := self.cfg.get("create_props", None)) == None:
            raise Exception(f"Cannot find element create_props in configuration.")

        def operation():    
            response = Device.create(self.api, name=name, **create_props)

            if not response:
                raise Exception(f"Device {name} hasn't been created")
        
            #if log_level <= tutils.INFO:
            #    GetResponse(response=response).print()      

        tutils.exec_test(f"Creating device {name}", operation)

        return None
        
    def verify(self):
        name = self.cfg.get("name")

        if (create_props := self.cfg.get("create_props", None)) == None:
            raise Exception(f"Cannot find element create_props in configuration.")

        verify_device(self.api, name, create_props)
        verify_device_communication(self.api, name)

        return None    
    
class TestCase_ModifyDevice(TestCase):
    def get_name(self):
        return "Modify Device"
        
    def run(self):
        name = self.cfg.get("name")

        if not (modify_props := self.cfg.get("modify_props", None)):
            raise Exception(f"Cannot find element modify_props in configuration.")

        def operation():        
            response = Device.update(self.api, name=name, **modify_props)

            if not response:
                raise Exception(f"Device {name} hasn't been created")
        
            #if log_level <= tutils.INFO:
            #    GetResponse(response=response).print()      

        tutils.exec_test(f"Modifying device {name}", operation)

        return None        

    def verify(self):
        name = self.cfg.get("name")

        if not (modify_props := self.cfg.get("modify_props", None)):
            raise Exception(f"Cannot find element modify_props in configuration.")
                
        verify_device(self.api, name, modify_props)
          
        return None    
    
class TestCase_DeleteDevice(TestCase):
    def get_name(self):
        return "Delete Device"
        
    def run(self):
        delete_device(self.api, self.cfg.get("name"))

    def verify(self):
        name = self.cfg.get("name")

        def operation():
            if dmo.get_resources(api_client=self.api, resourceName=name):
                raise Exception(f"Delete request didn't delete device {name}.")
        tutils.exec_test(f"Checking if device {name} has been deleted", operation)

        return None      

class TestCase_CreateDevice(TestCase):
    def get_name(self):
        return "Create Device"
        
    def run(self):
        name = self.cfg.get("name")

        if (create_props := self.cfg.get("create_props", None)) == None:
            raise Exception(f"Cannot find element create_props in configuration.")

        def operation():    
            response = Device.create(self.api, name=name, **create_props)

            if not response:
                raise Exception(f"Device {name} hasn't been created")
        
            #if log_level <= tutils.INFO:
            #    GetResponse(response=response).print()      

        tutils.exec_test(f"Creating device {name}", operation)

        return None
        
    def verify(self):
        name = self.cfg.get("name")

        if (create_props := self.cfg.get("create_props", None)) == None:
            raise Exception(f"Cannot find element create_props in configuration.")

        verify_device(self.api, name, create_props)
        verify_device_communication(self.api, name)

        return None    
    
class TestCase_InjectUplinkMessage(TestCase):

    def get_name(self):
        return "Inject Uplink Message"
        
    def run(self):
        self._message_ids = []

        name = self.cfg.get("name")

        if (content := self.cfg.get("inject_data")) == None:
            raise Exception("No content configured to inject.")
        
        content_type = "application/json" if type(content) == dict else "text/plain"
        
        def operation():        
            response = Device.inject_uplink_message(self.api, name=name, 
                                                    content=content, content_type=content_type)

            if not response:
                raise Exception(f"Uplink messages couldn't been injected for device {name}")

            self._message_ids.append(response.name)

        tutils.exec_test(f"Injecting uplinkg message {content} to device {name}", operation)

        return None        

    def verify(self):
    
        name = self.cfg.get("name")
        
        for message_id in self._message_ids:
            
            # Build the name path of the injected uplink message
            message_name = f"device-communication/{name}/received-msg/{message_id}"
    
            def operation():
                onem2m_dict = dmo.get_resources(api_client=self.api, resourceName=message_name)
                if not onem2m_dict:
                    raise Exception(f"Message resource {message_name} couldn't be get after injection.")
                else:
                    return onem2m_dict
            
            tutils.exec_test(f"Getting injected message {message_name}", operation)    
            
