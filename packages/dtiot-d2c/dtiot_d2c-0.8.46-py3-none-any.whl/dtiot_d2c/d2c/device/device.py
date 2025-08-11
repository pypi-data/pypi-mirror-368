import json
import logging
import os
import re
import time
import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, PrivateAttr

import dtiot_d2c.dmo as dmo
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.onem2m_base import OneM2MBase
from dtiot_d2c.dmo import ApiClient, device_provisioning

from .consts import *
from .message import Message

log = logging.getLogger(__name__)
class Device(OneM2MBase):
    _init_with_dvi: bool = PrivateAttr(default=False)
    _init_with_crds: bool = PrivateAttr(default=False)
    _dirty_dvi:bool = PrivateAttr(default=False)
    _dirty_credentials:bool = PrivateAttr(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.onem2m:
            if self.onem2m.get("m2m:dvi", []):
                self._init_with_dvi = True
            if self.onem2m.get("m2m:crds", []):
                self._init_with_crds = True
        
    @property        
    def dirty_dvi(self)->bool:
        return self._dirty_dvi    
    @dirty_dvi.setter
    def dirty_dvi(self, value:bool):
        self._dirty_dvi = value        

    @property        
    def dirty_credentials(self)->bool:
        return self._dirty_credentials        
    @dirty_credentials.setter
    def dirty_credentials(self, value:bool):
        self._dirty_credentials = value          
        
    @property
    def iccid(self)->List[str]:
        return self._get_label("ICCID")

    @iccid.setter
    def iccid(self, value:str):
        self._set_label("ICCID", value)
    
    ### 
    # Uplink properties
    def set_uplink_properties(self, props:dict):
        self._set_prefixed_labels(UPLINK_PROPERTY_PREFIX, props)

    def delete_uplink_properties(self):
        self._delete_prefixed_labels(UPLINK_PROPERTY_PREFIX)

    def set_uplink_property(self, key, value):
        self._set_prefixed_label(UPLINK_PROPERTY_PREFIX, key, value)
        
    def del_uplink_property(self, key):
        self._del_perfixed_property(UPLINK_PROPERTY_PREFIX, key)

    @property    
    def uplinkProperties(self)->dict:   
        return self._get_prefixed_labels(UPLINK_PROPERTY_PREFIX)
    
    @uplinkProperties.setter
    def uplinkProperties(self, props:dict):
        self.set_uplink_properties(props)    

    ### 
    # Device properties
    def set_device_properties(self, props:dict):
        self._set_prefixed_labels(DEVICE_PROPERTY_PREFIX, props)

    def delete_device_properties(self):
        self._delete_prefixed_labels(DEVICE_PROPERTY_PREFIX)

    def set_device_property(self, key, value):
        self._set_prefixed_label(DEVICE_PROPERTY_PREFIX, key, value)
        
    def del_device_property(self, key):
        self._del_perfixed_property(DEVICE_PROPERTY_PREFIX, key)

    @property    
    def deviceProperties(self)->dict:   
        return self._get_prefixed_labels(DEVICE_PROPERTY_PREFIX)
    
    @deviceProperties.setter
    def deviceProperties(self, props:dict):
        self.set_device_properties(props)   

    ### 
    # Device properties
    # def delete_device_properties(self):
    #     old_labels = self.labels
    #     new_labels = {}
    #     for (k, v) in old_labels.items():
    #         if k.startswith(UPLINK_PROPERTY_PREFIX) or k in DEVICE_SYSTEM_LABELS:
    #             new_labels[k] = old_labels[k]
    #     self.labels = new_labels

    # def set_device_properties(self, props:dict):
    #     if props == None:
    #         return

    #     self.delete_device_properties()
        
    #     for (key, value) in props.items():
    #         self._set_label(key, value)        
            
    # def set_device_property(self, key, value):
    #     self._set_label(key, value)

    # def del_device_property(self, key):
    #     self._del_label(key)

    #@property    
    # def deviceProperties(self)->dict:
    #     d = {}
    #     for (k, v) in self.labels.items():
    #         if k.startswith(UPLINK_PROPERTY_PREFIX) or k in DEVICE_SYSTEM_LABELS:
    #             continue
    #         d[k] = v
    #     return d
    
    # @deviceProperties.setter
    # def deviceProperties(self, props:dict):
    #     self.set_device_properties(props)
    
    ### DVI attributes
        
    @property
    def deviceType(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "dty")

    @deviceType.setter
    def deviceType(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "dty", value)
        
    @property
    def deviceName(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "dvnm")

    @deviceName.setter
    def deviceName(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "dvnm", value)

    @property
    def location(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "loc")

    @location.setter
    def location(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "loc", value)

    @property
    def label(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "dlb")

    @label.setter
    def label(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "dlb", value)

    @property
    def description(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "dc")

    @description.setter
    def description(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "dc", value)
                
    @property
    def firmwareVersion(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "fwv")

    @firmwareVersion.setter
    def firmwareVersion(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "fwv", value)
        
    @property
    def softwareVersion(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "swv")

    @softwareVersion.setter
    def softwareVersion(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "swv", value)
                          
    @property
    def osVersion(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "osv")

    @osVersion.setter
    def osVersion(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "osv", value)

    @property
    def hardwareVersion(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "hwv")

    @hardwareVersion.setter
    def hardwareVersion(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "hwv", value)
                     
    @property
    def protocols(self)->List[str]:#
        return self._get_child_array_attribute("m2m:dvi", "ptl")

    @protocols.setter
    def protocols(self, value:List[str]):
        self._set_child_array_attribute("m2m:dvi", "ptl", value)
        
    @property
    def manufacturer(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "man")

    @manufacturer.setter
    def manufacturer(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "man", value)
                
    @property
    def model(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "mod")

    @model.setter
    def model(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "mod", value)
                        
    @property
    def subModel(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "smod")

    @subModel.setter
    def subModel(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "smod", value)

    @property
    def country(self)->List[str]:
        return self._get_child_array_attribute("m2m:dvi", "cnty")

    @country.setter
    def country(self, value:str):
        self._set_child_array_attribute("m2m:dvi", "cnty", value)

    ### CRDS attributes (Credentials)
    '''
    "m2m:crds": [
        {
            "dc": "cred",
            "mgd": 1029,
            "rn": "credentials",
            "ty": 13,
            "ri": "67fff2fceab987515f7c361c",
            "pi": "67fff2fceab987515f7c3616",
            "ct": "20250416T181212,718000",
            "lt": "20250416T181212,718000",
            "crid": "device01-115",
            "crse": "Q3hhc21FTUw3NFNiUlIzUw=="
        }
    ],    
    '''    
    @property
    def credentialsId(self)->List[str]:
        return self._get_child_array_attribute("m2m:crds", "crid")

    @credentialsId.setter
    def credentialsId(self, value:str):
        self._set_child_array_attribute("m2m:crds", "crid", value)
        
    @property
    def credentialsSecret(self)->List[str]:#
        if os.getenv("SHOW_SECRETS", "false").lower() in ["true", "1", "yes"]:
            return self._get_child_array_attribute("m2m:crds", "crse")
        else:
            return "***"

    @credentialsSecret.setter
    def credentialsSecret(self, value:str):
        self._set_child_array_attribute("m2m:crds", "crse", value)

    def validate_name(name:str)->bool:
        return re.match(VALID_NAME_CHARS, name)

    def model_dump(self,  *args, **kwargs):
        md = super().model_dump(*args, **kwargs)
        for key in ["iccid",
                    "deviceType",
                    "deviceName",
                    "location", 
                    "label",
                    "description",
                    "deviceName",
                    "firmwareVersion", "softwareVersion", "osVersion", "hardwareVersion",
                    "protocols", 
                    "manufacturer", "model", "subModel",
                    "country",
                    "uplinkProperties",
                    "deviceProperties",
                    "credentialsId",
                    "credentialsSecret"
                   ]:
            md[key] = getattr(self, key)

        return md

    def set_from_kwargs(self, **kwargs):
        super().set_from_kwargs(**kwargs)

        #### Copy simple string argumentsw
        for (paramName, attrName) in (("iccid", "iccid"),
                                      ("description", "description"),
                                      ("label", "label"),
                                      ("device_type", "deviceType"),
                                      ("device_name", "deviceName"),
                                      ("firmware_version", "firmwareVersion"),
                                      ("software_version", "softwareVersion"),
                                      ("os_version", "osVersion"),
                                      ("hardware_version", "hardwareVersion"),
                                      ("location", "location"),
                                      ("manufacturer", "manufacturer"),
                                      ("model", "model"),
                                      ("sub_model", "subModel"),
                                      ("country", "country"),
                                      ("credentials_id", "credentialsId"),
                                      ("credentials_secret", "credentialsSecret")
                                     ):
            if not (value := kwargs.get(paramName, None)):
                continue

            setattr(self, attrName, value)
                  
            if paramName in ("credentials_id", "credentials_secret"):
                self.dirty_credentials = True

            elif paramName in ("description", "label", "device_type", "device_name", 
                               "firmware_version", "software_version", "os_version", 
                               "hardware_version", "location", "manufacturer", "model", 
                               "sub_model", "country"):
                self.dirty_dvi = True
            
        ### Copy list args into the object
        for (paramName, attrName) in [["protocols", "protocols"],
                                     ]:
            if not (value := kwargs.get(paramName, None)):
                continue
            if type(value) == list:
                setattr(self, attrName, value)
            elif type(value) == str:
                setattr(self, attrName, utils.splitString(value, ","))
            else:
                log.error(f"Unsupported type {type(value)} for argument {paramName}={value}")                  

        ### 
        # Copy the uplink properties into the labels of the device
        self.integrate_labels(kwargs.get("uplink_properties", None), 
                              self.del_uplink_property,
                              self.set_uplink_property,
                              self.set_uplink_properties)

        ###
        # Copy the ddevice properties into the labels of the device
        self.integrate_labels(kwargs.get("device_properties", None), 
                              self.del_device_property,
                              self.set_device_property,
                              self.set_device_properties)
                
    def to_onem2m(self, **kwargs)->dict:
        return {}

    def to_onem2m_dvi(self)->dict:
        '''
        {
            "m2m:dvi": {
                "loc": "geo:48.861069,2.335798",
                "rn": "device001",
                "mod": "Heart of Gold",
                "man": "a Manufacturer",
                "dlb": "|label:value anotherLabel:value",
                "mgd": 1007,
                "dty": "SIM"
            }
        }
        '''
        dvi = {
            "rn": DEVICE_INFO_RN,
            "mgd": DEVICE_INFO_MGD
        }
        
        for (dev_attr_name, onem2m_path) in [["location",       "loc"],
                                            ["deviceType",      "dty"],
                                            ["deviceName",      "dvnm"],
                                            ["label",           "dlb"],
                                            ["description",     "dc"],
                                            ["firmwareVersion", "fwv"],
                                            ["softwareVersion", "swv"],
                                            ["osVersion",       "osv"],
                                            ["hardwareVersion", "hwv"],
                                            ["protocols",       "ptl"],
                                            ["manufacturer",    "man"],
                                            ["model",           "mod"],
                                            ["subModel",        "smod"],
                                            ["country",         "cnty"],
                                            ]:
            utils.setValueInDict(dvi, onem2m_path, getattr(self, dev_attr_name), createIfNotExist=True)
            
        return dvi

    def to_onem2m_crds(self)->dict:
        '''
        {
            "dc": "cred",
            "mgd": 1029,
            "rn": "credentials",
            "ty": 13,
            "ri": "680be5a783dba99abdafb9ab",
            "pi": "680be5a783dba99abdafb9a5",
            "ct": "20250425T194231,895000",
            "lt": "20250425T194231,895000",
            "crid": "UNDEFINED",
            "crse": "UNDEFINED"
        }
        '''
        crds = {
            "dc":"cred",
            "mgd": 1029,
            "rn": "credentials",
            "crid": self.credentialsId,
            "crse": self.credentialsSecret
        }
            
        return crds

    ######################################################################
    # Static public functions
    ######################################################################
    def get_create_onem2m_dict(name:str, **kwargs)->dict:
        return {}
            
    def get(api_client:ApiClient,  
            origin:str=None,       
            id:str=None,
            name:str=None,
            select:str=None,                 # Comma separated list of element names which shall be selected.
            format:str="CSV",                # Output format. Possible values are CSV and JSON
            resultContentIndocator:str=None, # Result content indicator. Supported types are RCIs (see above).
            limit:int=1000000000,            # Max number of objects to return.
            offset:int=0
           ) -> dict:  

        return get(api_client, origin=origin, id=id, name=name, resultContentIndocator=resultContentIndocator,
                   limit=limit, offset=offset, select=select, format=format)
        
    def create(api_client:ApiClient,
               origin:str=None,     
               name:str=None,
               **kwargs):    
        return create(api_client, origin, name, **kwargs)
    
    def delete(api_client:ApiClient, 
               origin:str=None, 
               id:str=None,
               name:str=None 
              ):
        return delete(api_client, origin=origin, id=id, name=name)
    
    def update(api_client:ApiClient, 
               origin:str=None, 
               device=None, 
               name:str=None,
               id:str=None,
               **kwargs
              ):  
        return update(api_client, 
                      origin, 
                      device=device, 
                      name=name,
                      id=id,
                      **kwargs)  

    def inject_uplink_message(api_client:ApiClient, 
                              origin:str=None,      
                              id:str=None,
                              name:str=None,
                              device=None,
                              content=None,
                              content_type:str="text/plain",
                              contentEncoding:str="none",
                             ):
        return _inject_message(api_client,
                               origin=origin,
                               msg_store=INBOUND_UPLINK_MESSAGE_STORE,
                               id=id,
                               name=name,
                               device=device,
                               content=content,
                               content_type=content_type,
                               contentEncoding=contentEncoding,
                              )
        
    def inject_downlink_message(api_client:ApiClient, 
                                origin:str=None,      
                                id:str=None,
                                name:str=None,
                                device=None,
                                content=None,
                                content_type:str="text/plain",
                                contentEncoding:str="none",
                               ):
        return _inject_message(api_client,
                               origin=origin,
                               msg_store=INBOUND_DOWNLINK_MESSAGE_STORE,
                               id=id,
                               name=name,
                               device=device,
                               content=content,
                               content_type=content_type,
                               contentEncoding=contentEncoding,
                              )        
        
    def get_messages(api_client:ApiClient,  
                     origin:str=None,       
                     name:str=None,
                     id:str=None,
                     msg_store:MessageStore=None,
                     msg_name:str=None,
                     last:bool=False,
                     select:str=None,              
                     format:str="CSV",                # Output format. Possible values are CSV and JSON
                     limit:int=1000000000,  
                     offset:int=0,         
                    ) -> dict:  

        return get_messages(api_client, origin=origin, name=name, id=id, 
                            msg_store=msg_store, msg_name=msg_name, 
                            last=last, limit=limit, offset=offset, 
                            select=select, format=format)
        
    def delete_message(api_client:ApiClient,
                       origin:str=None,   
                       name:str=None,    
                       id:str=None,
                       msg_store:MessageStore=None,
                       msg_name:str=None,
                       msg_id:str=None
                       ):
        delete_message(api_client,
                       origin=origin,
                       name=name,
                       id=id,
                       msg_store=msg_store,
                       msg_name=msg_name,
                       msg_id=msg_id)
                          
################################################################
################################################################
################################################################
#MARK: IMPLEMENTATIONS

def _get(api_client:ApiClient,  
         origin:str=None,   
         id:str=None,    
         name:str=None,
         resultContentIndocator:str=None, # Result content indicator. Supported types are RCIs (see above).
         limit:int=1000000000,            # Max number of objects to return.
         offset:int=0,
         select:str=None,                 # Comma separated list of element names which shall be selected.
         format:str="CSV"                 # Output format. Possible values are CSV and JSON
        ) -> dict:        
    if not name and not id:
        response = dmo.get_resources(api_client, 
                                     origin=origin,
                                     resourceType="nod", 
                                     limit=limit,
                                     offset=offset,
                                     resultContentIndocator=resultContentIndocator)
    else:
        response = dmo.get_resources(api_client, 
                                     origin=origin,
                                     resourceId=id,
                                     resourceName=name,
                                     limit=limit,
                                     offset=offset,
                                     resultContentIndocator=resultContentIndocator)      
    if not response:
        return None

    if not name and not id:
        object = [OneM2MBase(onem2m=onem2m) for onem2m in response]
    else:
        object = Device(onem2m=response)  
                
    # Return the plain objects
    if not select:
        return object
    else:
        return dmo.select_from_response_body(object, select=select, format=format)

def get(api_client:ApiClient,
        origin:str=None,   
        id:str=None,
        name:str=None,    
        select:str=None,                 
        format:str="CSV",             
        limit:int=1000000000,      
        offset:int=0,   
        resultContentIndocator:str=None, 
       ):        
    if name or id:
        log.info(f"Getting device {name or id} from DMO ...")
    else:
        log.info(f"Getting device from DMO ...")        

    return _get(api_client, origin=origin, id=id, name=name, select=select, format=format, 
                resultContentIndocator=resultContentIndocator, limit=limit, offset=offset)

def delete(api_client:ApiClient, 
           origin:str=None, 
           id:str=None,
           name:str=None, 
          ):
    if not name and not id:
        raise Exception(f"delete() requires parameter name or id as input.")
    
    log.info(f"Deleting device {name} from DMO ...")
    return dmo.delete_resource(api_client, origin=origin, name=name, id=id)

def _update(api_client:ApiClient,  # Client connection definition.
            origin:str,            # Value for X-M2M-Origin header 
            device:Device,
           )->Device:

    if not device:
        raise Exception(f"update() requires parameter device as input.")

    #####
    # If the device info object is "dirty"
    if device.dirty_dvi:
        # Create the oneM2M dvi dictionary from the device
        dvi:dict = device.to_onem2m_dvi()

        # Re-create the dvi object of the device node.
        onem2m_dvis = device.onem2m.get('m2m:dvi', []) 
        #if device._init_with_dvi and onem2m_dvis:
        if onem2m_dvis:
            #to_delete_dvi_rn = f"{device.name}/{device.onem2m.get('m2m:dvi')[0].get('rn')}"
            to_delete_dvi_rn = f"{device.name}/{onem2m_dvis[0].get('rn')}"

            log.info(f"Deleting old managed dvi object {to_delete_dvi_rn} from DMO ...")
            dmo.delete_resource(api_client, origin, to_delete_dvi_rn)
        #else:
        #    log.warning(f"Onem2m node of device {device.name} does NOT have a device information object !!")    
            
        log.info(f"Adding new manged dvi object for device {device.name} in DMO ...")
        dmo.add_resource(api_client, origin=origin, r_type="managed-object", r_name=device.name, 
                            onem2m_body={"m2m:dvi": dvi})
        
    ####
    # Update credentials if they are "dirty"
    if device.dirty_credentials:
        deleted_flag = False

        # Delete existing credentials
        onem2m_crds = device.onem2m.get('m2m:crds', []) 

        # if device._init_with_crds and onem2m_crds:
        if onem2m_crds and onem2m_crds[0].get("ri", None): 
            to_delete_crds_rn = f"{device.name}/{onem2m_crds[0].get('rn')}"
            log.info(f"Deleting old device credentials {to_delete_crds_rn} from DMO ...")
            dmo.delete_resource(api_client, origin, to_delete_crds_rn)

            deleted_flag = True

        # Create the credentials 
        crds:dict = device.to_onem2m_crds()
        
        #log.info(f"Adding new credentials object for device {device.name} in DMO ...")
        #dmo.add_resource(api_client, origin=origin, r_type="managed-object", r_name=device.name, 
        #                 onem2m_body={"m2m:crds": crds})
        utils.retry_function(dmo.add_resource, 
                             args=[api_client], 
                             kwargs={
                                 "origin":origin, 
                                 "r_type":"managed-object", 
                                 "r_name":device.name, 
                                 "onem2m_body":{"m2m:crds": crds}
                             },
                             max_try_count=4, 
                             max_secs=15, 
                             sleep_before_first_try_secs=DELETE_CREDENTIALS_SLEEP_SECS if deleted_flag else -1,
                             sleep_after_error_secs=DELETE_CREDENTIALS_SLEEP_SECS,
                             error_return_value=log.error,
                             info_message="Adding new credentials object for device {device.name} in DMO ...",
                             info_logger=log.info, 
                             error_logger=log.error)
    ###
    # Update the labels in the node resource
    log.info(f"Updating labels of device {device.name} in DMO ...")
    dmo.update_resource_labels(api_client, origin, "nod", device.name, device.labels)

    # Reload the device and return it
    log.info(f"Reloading {device.name} from DMO ...")
    return get(api_client, origin, name=device.name)

def update(api_client:ApiClient,  # Client connection definition.
           origin:str=None,       # Value for X-M2M-Origin header 
           device:Device=None,
           name:str=None,
           id:str=None,
           **kwargs
          ):

    if device:
        return _update(api_client, origin, device=device)
    elif not name and not id:
        raise Exception(f"update() requires parameter device, name or id as input.")

    device = get(api_client, origin=origin, id=id, name=name)

    # Copy the keyword arguments into the device object
    device.set_from_kwargs(**kwargs)

    return _update(api_client, origin, device=device)

def create(api_client:ApiClient, # Client connection definition.
           origin:str=None,      # Value for X-M2M-Origin header 
           name:str=None,
           timeout_secs:int=10,
           **kwargs):

    # Verify if the name contains forbidden characters
    # MARK: WORK
    if not Device.validate_name(name):
        raise Exception(f"Invalid characters in name {name}. The name should look like {VALID_NAME_CHARS}")

    ## Build the credentials 
    credentials_id = kwargs.get("credentials_id", None)
    credentials_secret = kwargs.get("credentials_secret", None)

    if credentials_id and credentials_secret:
        node_creds = [f"psk-id:{credentials_id}",f"psk:{credentials_secret}"]
        node_creds_arg = {"nodeCredentials":node_creds}
    else:
        node_creds_arg = {}

    # Build the device information for the node
    '''
    "nodeDvi": {
        "rn": "device-info",
        "mgd": 1007,
        "man": "evel-corp",
        "dty": "world-destructor",
        "mod": "WD-15",
        "dlb": "some:label",
        "dc": "it destroys everything"
    },
    '''    
    dvi:dict = {
        "rn": DEVICE_INFO_RN,
        "mgd": DEVICE_INFO_MGD
    }
    
    for (arg_name, dvi_name, default) in (
                                          ("device_type",       "dty", ""), 
                                          ("location",          "loc",  None), #"geo:25.245470,51.454009"),
                                          ("label",             "dlb",  ""), 
                                          ("description",       "dc",   ""), 
                                          ("device_name",       "dvnm", ""), 
                                          ("firmware_version",  "fwv",  ""), 
                                          ("software_version",  "swv",  ""), 
                                          ("os_version",        "osv",  ""), 
                                          ("hardware_version",  "hwv",  ""), 
                                          ("protocols",         "ptl",  []),
                                          ("manufacturer",      "man",  ""), 
                                          ("model",             "mod",  ""), 
                                          ("sub_model",         "smod", ""), 
                                          ("country",           "cnty", "") 
                                         ):
        if (v := kwargs.get(arg_name, None)) == None:
            v = default
        if v != None:
            dvi[dvi_name] = v
        
    ###
    # Build labels 
    labels=[]
    if (props := kwargs.get("uplink_properties", None)):
        for (k, v) in props.items():
            labels.append(f"{UPLINK_PROPERTY_PREFIX}{k}:{v}")

    if (props := kwargs.get("device_properties", None)):
        for (k, v) in props.items():
            labels.append(f"{DEVICE_PROPERTY_PREFIX}{k}:{v}")

    if labels:
        labels.append(f"{d2c_consts.D2C_SYSTEM_VERSION_LABEL}:{d2c_consts.D2C_SYSTEM_VERSION}")
        labels_arg = {"labels":labels}
    else:
        labels_arg = {"labels":[f"{d2c_consts.D2C_SYSTEM_VERSION_LABEL}:{d2c_consts.D2C_SYSTEM_VERSION}"]}

    # Step 1: Create device provisioning request which is execute asynchronously to 
    #         create the device in d2c. a
    log.info(f"Creating device provisioning request in DMO for {name} ...")
    d = device_provisioning.create_request(api_client,
                                           origin=origin,
                                           # Add the additional request data 
                                           nodeID=f"urn:gsma:imei:{name}",
                                           nodeResourceName=name,
                                           ICCID=kwargs.get("iccid", "89374121224379144333"),
                                           profile=DEVICE_PROFILES.SCS_LWM2M,
                                           **node_creds_arg, 
                                           ndvi=dvi,
                                           **labels_arg 
                                          )

    # Step 2: Wait for the device provisioning response until the job is executed
    #         succesfully or with errors. 
    '''
    POST of device provisioning request returns: 
        "dtiot:noPRt.resourceID": "67dc0c88c9a47b53f222656c"
        "dtiot:noPRt.resourceName": "device_provisioning_request_20250320-133933",

    GET of device provisioning reqeust contains: 
        "rn": "device_provisioning_request_20250320-133933",
        "ri": "67dc0c88c9a47b53f222656c"                        = dtiot:noPRt.resourceID

    GET of device provisioning respoonse contains:
        "rn": "responseToRequest-67dc0c88c9a47b53f222656c",      = "responseToRequest-"<request.ri>
        "reqRD": "67dc0c88c9a47b53f222656c",    
    '''
    requestId:str = utils.getValueFromDict(d, "dtiot:noPRt.resourceID", None, ".")
    responseName:str = f"responseToRequest-{requestId}" if requestId else None

    start_time=time.time()
        
    log.info(f"Waiting for response ...")
    found_response = False        
    while True:
        
        try:
            log.info(f"  trying to get response {responseName} from DMO ...")
            response = device_provisioning.get_responses(api_client, origin=origin, name=responseName)
            
            # If no response can be found 
            if not response:
                if time.time() > start_time + timeout_secs:
                    log.info(f"  ... not  found. Waiting for device provisioning response '{responseName}' timed out.")
                    break
                else:
                    log.info(f"  ... not found. Sleeping 1.0 seconcds ...")                    
                    time.sleep(1.0)
                    continue

            found_time = time.time()
            
            # Get the processing status from the response and test if it is ok.
            status = response.get("resSs", None)
            # "geEMe":"Total to be provisioned: 1; Successfully processed: 1; Errors: 0"
            general_message = response.get("geEMe", "No general processing message available")   
            individual_message = response.get("inEMs", "No individual processing message available")
            
            if status != 1:
                raise Exception(f"Device provisioninig request ended with status {status}.\n{general_message}\n{individual_message}")

            # We exit the loop to wait for the response object
            log.info(f"... found response after {found_time - start_time} seconds.")
            found_response = True
            break

        except Exception as ex:
            log.error(f"Error while getting the device provisioning response '{responseName}': {ex}")
            raise ex

    # Step 3: Even if we didn't find the provisioning request we try to load the device node from dmo.  
    if not found_response:
        log.warning("Could not find device provisioning response. Trying to get the new device anyway ...")
        
    device:Device = get(api_client, origin=origin, name=name)
    
    if not device:
        raise Exception(f"Could not get device {name} from DMO. Was the device provisioning request processed successfully?")    

    return device

def _inject_message(api_client:ApiClient, 
                    origin:str=None, 
                    msg_store:MessageStore=None,
                    id:str=None, 
                    name:str=None,
                    device:Device=None,
                    content=None,
                    content_type:str="text/plain",
                    contentEncoding:str="none",
                    **kwargs):    
    if content == None:
        return None
    elif msg_store == None:
        raise Exception(f"_inject_message() requires msg_store parameter.")
    elif not device and not name and not id:
        raise Exception(f"_inject_message() requires parameter device, name or id as input.")        
    
    # Determine the onem2m id of the encoding type
    contentEncodingId = utils.get_enum_value_by_name(dmo.CE, contentEncoding, default=dmo.CE.none.value)

    if content_type == "text/plain":
        content = str(content)
    elif content_type == "application/json":
        if type(content) != dict:
            content = json.loads(content)
    else:
        raise Exception(f"Unsupported content type {content_type}.")
    
    body = {
        "m2m:cin": {
            "rn":    f"{uuid.uuid4()}",
            "con":   content,
            "cnf":   f"{content_type}:{contentEncodingId}"
        }
    }

    resource_name = f"device-communication/"
    if device:
        resource_name += device.name
    elif name:
        resource_name += name
    else:
        resource_name += id
    resource_name += f"/{msg_store.rn}"        
    
    response = dmo.add_resource(api_client, 
                                origin=origin, 
                                r_type="cin", 
                                r_name=resource_name,
                                onem2m_body=body)
    
    if not response:
        return None
    
    msg_id = response.get("m2m:cin", {}).get("ri", None)
    
    if not msg_id:
        log.error(f"Could not get id of message.")
        return None

    onem2m = dmo.get_resources(api_client, origin=origin, resourceId=msg_id)
    if not onem2m:
        log.error(f"Could not get message resource {msg_id}.")
        return None

    return Message(onem2m=onem2m)

def get_messages(api_client:ApiClient,
                 origin:str=None,   
                 name:str=None,    
                 id:str=None,
                 msg_store:MessageStore=None,
                 msg_name:str=None,
                 last:bool=False,
                 select:str=None,                 
                 format:str="CSV",             
                 limit:int=1000000000,    
                 offset:int=0     
                ):        
    if not msg_store:
        raise Exception("Function get_messages() requires msg_store as input parameter")
    elif not name and not id:
        raise Exception("Function get_messages() requires name or id as input parameter")

    log.info(f"Getting {msg_store.label} messages for device {name or id} from DMO ...")
    
    if id and not name:
        device = get(api_client, origin=origin, id=id)
        if not device:
            raise Exception(f"Could not load device with id {id}.")
        name = device.name

    # Build the resource name of the device message store
    resource_name = f"device-communication/{name}/{msg_store.rn}"

    # If a concrete message shall be get add its identfier to resource name
    if msg_name:
        resource_name += f"/{msg_name}"

    # If only the last message shall be get
    elif last:
        resource_name += "/la"
        limit=-1
    
    response = dmo.get_resources(api_client, 
                                origin=origin,
                                resourceName=resource_name,
                                limit=limit,
                                offset=offset)

    if not response:
        return None
    elif last:
        objects = Message(onem2m=response)
    elif response.get("con", None):
        objects = Message(onem2m=response)
    else:
        objects = [Message(onem2m=onem2m) for onem2m in response.get("m2m:cin", [])]

    if not select:
        return objects
    else:
        return dmo.select_from_response_body(objects, select=select, format=format)            

def delete_message(api_client:ApiClient,
                   origin:str=None,   
                   name:str=None,    
                   id:str=None,
                   msg_store:MessageStore=None,
                   msg_name:str=None,
                   msg_id:str=None
                  ):        
    # If the msg_id has been defined the message can be deleted without any other info
    if msg_id:
        log.info(f"Deleting message {msg_id} ...")
        dmo.delete_resource(api_client, origin=origin, id=msg_id)
        return        
    elif not msg_name:
        raise Exception("Function delete_message() requires parameter msg_name as input.")

    if not msg_store:
        raise Exception("Function delete_message() requires msg_store as input parameter")
    elif not name and not id:
        raise Exception("Function delete_message() requires name or id as input parameter")

    log.info(f"Deleting message {msg_name} from {msg_store.label} for device {name or id} from DMO ...")
    
    if id and not name:
        device = get(api_client, origin=origin, id=id)
        if not device:
            raise Exception(f"Could not load device with id {id}.")
        name = device.name

    # Build the resource name of the message to delete and delete it
    resource_name = f"device-communication/{name}/{msg_store.rn}/{msg_name}"
    dmo.delete_resource(api_client, origin=origin, name=resource_name)

    return None