import json
import logging
import sys
import time
from typing import List

import dtiot_d2c.d2c.test.utils as tutils
import dtiot_d2c.dmo as dmo
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.application import Application
from dtiot_d2c.d2c.application.consts import *
from dtiot_d2c.d2c.consts import *
from dtiot_d2c.d2c.device.consts import *
from dtiot_d2c.d2c.get_response import GetResponse
from dtiot_d2c.d2c.test.testcli_base import TestCase, TestCLI_Base, TestSet
from dtiot_d2c.d2c.utils import color as color
from dtiot_d2c.dmo import ApiClient

log = logging.getLogger(__name__)
log_level = log.getEffectiveLevel() 

def create_application(api: ApiClient, name:str, props:dict):
    def operation():   
        response = Application.create(api,
                                      name=name,
                                      urls=props.get("urls", []),
                                      type=props.get("type", None),
                                      connection_properties=props.get("connection_properties", None)
                                     )
        if not response:
            return f"Application {name} hasn't been created"
        
        if log_level <= tutils.INFO:
            GetResponse(response=response).print()      

    tutils.exec_test(f"Creating ae {name}", operation)
    return None        
        
def verify_application(api:ApiClient, name:str, props:dict):
    '''
    {
        "api": "Nrba-appl-20250404-t002-1",
        "rn": "rba-appl-20250404-t002-1",
        "lbl": [
            "applicationType:WebHook"
        ],
        "poa": [
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],
        "ty": 2,
        "ri": "67efbea49b1f20af72d58d78",
        "aei": "Crba-appl-20250404-t002-1",
        "pi": "d2c-dev-1",
        "ct": "20250404T111236,691000",
        "lt": "20250404T111236,691000"
    }        
    '''    
    def operation():
        onem2m_dict = dmo.get_resources(api_client=api, resourceName=name)
        if not onem2m_dict:
            raise Exception(f"Application resource {name} couldn't be get after creation.")
        else:
            return onem2m_dict
    onem2m_dict:dict = tutils.exec_test(f"Getting ae {name}", operation)

    elem_path = "rn"
    elem_value = name
    def operation():
        if not tutils.call_has_element_value(onem2m_dict, elem_path, elem_value):
            raise Exception(f"Value of element {elem_path} does not meet required value {elem_value}.")
    tutils.exec_test(f"Verifing {elem_path} for {elem_value}", operation)

    elem_path = "lbl"
    elem_value = f'{D2C_SYSTEM_VERSION_LABEL}:{D2C_SYSTEM_VERSION}'
    def operation():
        if not tutils.call_has_element_value(onem2m_dict, elem_path, elem_value):
            raise Exception(f"Value of element {elem_path} does not meet required value {elem_value}.")
    tutils.exec_test(f"Verifing {elem_path} for {elem_value}", operation)

    elem_path = "lbl"
    elem_value = f'{APPL_TYPE_LABEL_NAME}:{props.get("type", APPL_TYPE_DEFAULT)}'
    def operation():
        if not tutils.call_has_element_value(onem2m_dict, elem_path, elem_value):
            raise Exception(f"Value of element {elem_path} does not meet required value {elem_value}.")
    tutils.exec_test(f"Verifing {elem_path} for {elem_value}", operation)

    if (conn_props := props.get("connection_properties_verify", None)) == None:
        conn_props = props.get("connection_properties", {})

    for (key, val) in conn_props.items():
        elem_path = "lbl"
        appl_type = props.get("type", APPL_TYPE_DEFAULT)
        prefix = CONN_PROPS_LABEL_PREFIXS.get(appl_type, None)
        elem_value = f"{prefix}{key}:{val}"
        
        def operation():
            if not tutils.call_has_element_value(onem2m_dict, elem_path, elem_value):
                raise Exception(f"Value of element {elem_path} does not meet required value {elem_value}.")
        tutils.exec_test(f"Verifing {elem_path} for {elem_value}", operation)

    elem_path = "poa"
    if (elem_value := props.get("urls_verify", None)) == None:
        elem_value = props.get("urls", [])
    def operation():
        if not tutils.call_has_element_value(onem2m_dict, elem_path, elem_value):
            raise Exception(f"Value of element {elem_path} does not meet required value {elem_value}.")
    tutils.exec_test(f"Verifing {elem_path}: {elem_value}", operation)
    return None    

def delete_application(api:ApiClient, name:str):
    def operation():  
        if (application := Application.get(api, name=name)):
            Application.delete(api, name=name)
    tutils.exec_test(f"Deleting ae {name}", operation)
    return None
        
class TestCase_CreateApplication(TestCase):
    def get_name(self):
        return "Create Application"

    def run(self):
        if (props := self.cfg.get("create_props", None)) == None:
            raise Exception(f"Cannot find element create_props in configuration.")
        return create_application(self.api, self.cfg.get("name"), props)

    def verify(self):
        if (props := self.cfg.get("create_props", None)) == None:
            raise Exception(f"Cannot find element create_props in configuration.")          
        return verify_application(self.api, self.cfg.get("name"), props)

class TestCase_ModifyApplication(TestCase):
    def get_name(self):
        return "Modify Application"
    
    def run(self):
        name = self.cfg.get("name")

        if not (modify_props := self.cfg.get("modify_props", None)):
            raise Exception(f"Cannot find element modify_props in configuration.")  
        
        def operation():      
            response = Application.update(self.api, 
                                        name=name,
                                        urls=modify_props.get("urls", []),
                                        labels=modify_props.get("labels", None),
                                        connection_properties=modify_props.get("connection_properties", None),
                                        )        
            
            if not response:
                raise Exception(f"Application {name} hasn't been modified")
        
            if log_level <= tutils.INFO:
                GetResponse(response=response).print()      

        tutils.exec_test(f"Modifing ae {name}", operation)
        return None

    def verify(self):
        if not (props := self.cfg.get("modify_props", None)):
            raise Exception(f"Cannot find element modify_props in configuration.")          
        return verify_application(self.api, self.cfg.get("name"), props)

class TestCase_DeleteApplication(TestCase):
    def get_name(self):
        return "Delete Application"
    
    def run(self):
        delete_application(self.api, self.cfg.get("name"))

    def verify(self):    
        name = self.cfg.get("name")        
        def operation():
            if dmo.get_resources(api_client=self.api, resourceName=name):
                raise Exception(f"Delete request didn't delete application {name}.")
        tutils.exec_test(f"Checking if ae {name} has been deleted", operation)



