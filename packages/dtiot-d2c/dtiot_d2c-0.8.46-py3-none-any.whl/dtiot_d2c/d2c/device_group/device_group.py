import json
import logging
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

import dtiot_d2c.d2c.consts as d2c_consts
import dtiot_d2c.dmo as dmo
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.application import Application
from dtiot_d2c.d2c.device import Device
from dtiot_d2c.d2c.onem2m_base import OneM2MBase
from dtiot_d2c.dmo import ApiClient

from .consts import *

log = logging.getLogger(__name__)

'''
{
    "dtiot:devGr": {
        "cnd": "com.telekom.iot.orchestrator.deviceGroup",
        "rn": "myDeviceGroup",
        "nds": [ "6724ca4407f20523ba2c6f1f","<applicatdevice_ri_2>", "...", "..." ],
        "aes": [ "66fe6b02baa471e374bd0041" ]
    }
} 
'''
class DeviceGroup(OneM2MBase):
    
    @property
    def devices(self)->List[str]:
        return self.onem2m.get("nds", []) 

    @devices.setter
    def devices(self, value:List[str]):
        current_list = self.devices
        self.onem2m["nds"] = utils.integrate_lists(current_list, value)

    @property
    def devicesCount(self)->int:
        return len(self.devices) if self.devices else 0
    
    @property
    def applications(self)->List[str]:
        return self.onem2m.get("aes", [])

    @applications.setter
    def applications(self, value:List[str]):
        current_list = self.applications
        self.onem2m["aes"] = utils.integrate_lists(current_list, value)

    @property
    def applicationsCount(self)->int:
        return len(self.applications) if self.applications else 0        

    @property
    def description(self):
        return self._get_label(f"{DESCRIPTION_LABEL_NAME}")

    @description.setter
    def description(self, value): 
        labels = {f"+{DESCRIPTION_LABEL_NAME}":value}
        self.integrate_labels(labels)
        
    def model_dump(self,  *args, **kwargs):
        md = super().model_dump(*args, **kwargs)
        for key in ["description",
                    "devices", 
                    "devicesCount",
                    "applications", 
                    "applicationsCount",
                   ]:
            md[key] = getattr(self, key)

        return md
        
    def set_from_kwargs(self, **kwargs):
        super().set_from_kwargs(**kwargs)
        
        #### Copy simple string argumentsw
        for (paramName, attrName) in (("description", "description"),
                                     ):
            if not (value := kwargs.get(paramName, None)):
                continue
            setattr(self, attrName, value)
                    
        # Copy list args into the object
        for (paramName, attrName) in [["devices", "devices"],
                                      ["applications", "applications"],
                                     ]:
            if not (value := kwargs.get(paramName, None)):
                continue

            if type(value) == list:
                setattr(self, attrName, value)
            elif type(value) == str:
                setattr(self, attrName, utils.splitString(value, ","))
                #setattr(self, key, json.loads(value))
            else:
                log.error(f"Unsupported type {type(value)} for argument {paramName}={value}")

                  
    def to_onem2m(self, **kwargs)->dict:
        d = {}
        for (attr_name, onem2m_path) in [["devices",      "nds"],
                                         ["applications", "aes"],
                                        ]:
            d[onem2m_path] = getattr(self, attr_name)

        d["lbl"] = dmo.convert_dict_to_onem2m_labels(self.labels)
        
        # Add the d2c version
        d2c_version_lbl = f"{d2c_consts.D2C_SYSTEM_VERSION_LABEL}:{d2c_consts.D2C_SYSTEM_VERSION}"
        if d2c_version_lbl not in d["lbl"]:
            d["lbl"].append(d2c_version_lbl)        

        # add the additional keyword arguments
        for (key, value) in kwargs.items():
            d[key] = value
            
        return {"dtiot:devGr":d}

    def add_devices(self, add_names:List[str])->List[str]:
        if not add_names:
            return 
        
        current_names = self.devices
        for name in add_names:
            if name not in current_names:
                current_names.append(name)

    def remove_devices(self, rm_names:List[str])->List[str]:
        if not rm_names:
            return
        current_names = self.devices
        for name in rm_names:
            try:
                current_names.remove(name)
            except Exception:
                log.warning(f"Device name {name} not in current list of devices.")
        
    def add_applications(self, add_names:List[str])->List[str]:
        if not add_names:
            return 
        
        current_names = self.applications
        for name in add_names:
            if name not in current_names:
                current_names.append(name)

    def remove_applications(self, rm_names:List[str])->List[str]:
        if not rm_names:
            return 
        
        current_names = self.applications
        for name in rm_names:
            try:
                current_names.remove(name)
            except Exception:
                log.warning(f"Application name {name} not in current list of applications.")
        
    ######################################################################
    # Static public functions
    ######################################################################
    def get_create_onem2m_dict(name:str, **kwargs)->dict:
        
        labels = kwargs.get("labels", {})
        labels[d2c_consts.D2C_SYSTEM_VERSION_LABEL] = d2c_consts.D2C_SYSTEM_VERSION
        labels[DESCRIPTION_LABEL_NAME] = kwargs.get("description", None)
        
        return {
            "dtiot:devGr": {
                "cnd": DEVICE_GROUP_CND,
                "rn": name,
                "lbl": dmo.convert_dict_to_onem2m_labels(labels),
                "nds": kwargs.get("devices", []),
                "aes": kwargs.get("applications", [])
            }
        }        
            
    def get(api_client:ApiClient,  
            origin:str=None,    
            id:str=None,   
            name:str=None,
            resultContentIndocator:str=None, # Result content indicator. Supported types are RCIs (see above).
            limit:int=1000000000,            # Max number of objects to return.
            offset:int=0,
            select:str=None,                 # Comma separated list of element names which shall be selected.
            format:str="CSV"                 # Output format. Possible values are CSV and JSON
           ):
        return get(api_client, 
                   origin=origin, 
                   id=id, name=name, 
                   limit=limit, offset=offset,
                   resultContentIndocator=resultContentIndocator,
                   select=select, format=format)
        
    def create(api_client:ApiClient,
               origin:str=None,     
               name:str=None,
               **kwargs):    
        return create(api_client, origin, name, **kwargs)
    
    def delete(api_client:ApiClient, 
               origin:str=None, 
               id:str=None,
               name:str=None, 
              ):
        return delete(api_client, origin=origin, id=id, name=name)
    
    def update(api_client:ApiClient, origin:str=None, 
               device_group=None,  # DeviceGroup
               id:str=None,
               name:str=None,
               **kwargs
              ):  
        return update(api_client, origin, 
                           device_group=device_group, 
                           id=id,
                           name=name,
                           **kwargs)  
        
    def update_devices(api_client:ApiClient, 
                       origin:str=None, 
                       device_group=None,  # DeviceGroup
                       name:str=None,
                       add_names:List[str]=None,
                       remove_names:List[str]=None,
                     ):  
        return update_devices(api_client, origin, device_group=device_group, name=name,
                              add_names=add_names, remove_names=remove_names,
                             )
        
    def update_applications(api_client:ApiClient, 
                            origin:str=None, 
                            device_group=None,  # DeviceGroup
                            name:str=None,
                            add_names:List[str]=None,
                            remove_names:List[str]=None,
                          ):  
        return update_applications(api_client, origin=origin, device_group=device_group, name=name,
                                   add_names=add_names, remove_names=remove_names,
                                  )        

################################################################
################################################################
################################################################
#MARK: IMPLEMENTATIONS
def _get(api_client:ApiClient,  # Client connection definition.
         origin:str=None,       # Value for X-M2M-Origin header 
         id:str=None,
         name:str=None,
         resultContentIndocator:str=None, # Result content indicator. Supported types are RCIs (see above).
         limit:int=1000000000,            # Max number of objects to return.
         offset:int=0,
         select:str=None,                 # Comma separated list of element names which shall be selected.
         format:str="CSV"                 # Output format. Possible values are CSV and JSON
        ): 
    
    if not name and not id:
        response = dmo.get_resources(api_client, 
                                     origin=origin,
                                     limit=limit,
                                     offset=offset,
                                     resourceType="fcn", 
                                     resourceName="device-group",
                                     resultContentIndocator=resultContentIndocator)
    else:
        response = dmo.get_resources(api_client, 
                                     origin=origin,
                                     resourceType="fcn", 
                                     resourceId=id,
                                     resourceName=f"device-group/{name}", 
                                     resultContentIndocator=resultContentIndocator)      
    if not response:
        return None

    if not name and not id:
        object = [DeviceGroup(onem2m=onem2m) for onem2m in response.get("dtiot:devGr", [])]
    else:
        object = DeviceGroup(onem2m=response)  

    # Return the plain objects
    if not object:
        return None
    elif not select:
        return object
    else:
        return dmo.select_from_response_body(object, select=select, format=format)

def get(api_client:ApiClient,  # Client connection definition.
        origin:str=None,       # Value for X-M2M-Origin header 
        id:str=None,
        name:str=None,
        resultContentIndocator:str=None, # Result content indicator. Supported types are RCIs (see above).
        limit:int=1000000000,            # Max number of objects to return.
        offset:int=0,
        select:str=None,                 # Comma separated list of element names which shall be selected.
        format:str="CSV"                 # Output format. Possible values are CSV and JSON
       ):        

    if name or id:
        log.info(f"Getting device group {name or id} from DMO ...")
    else:
        log.info(f"Getting device groups from DMO ...")

    return _get(api_client, origin=origin, id=id, name=name, 
                limit=limit, offset=offset, 
                select=select, format=format, 
                resultContentIndocator=resultContentIndocator)
        
def create(api_client:ApiClient, 
           origin:str=None,      
           name:str=None,
           **kwargs):

    log.info(f"Creating device group {name} in DMO ...")
    onem2m = DeviceGroup.get_create_onem2m_dict(name, **kwargs)
    dmo.add_resource(api_client, origin=origin, r_type="fcn", r_name="device-group", 
                     onem2m_body=onem2m)

    return get(api_client, origin=origin, name=name)

def delete(api_client:ApiClient, 
           origin:str=None, 
           id:str=None,
           name:str=None, 
          ):
    if not name and not id:
        raise Exception(f"delete_device_group() requires parameter name or id as input.")
    
    log.info(f"Deleting device group {name or id} from DMO ...")
    
    if id:
        resource_name = None
    else:
        resource_name = f"device-group/{name}"
    return dmo.delete_resource(api_client, origin=origin, name=resource_name, id=id)

def _update(api_client:ApiClient,  # Client connection definition.
            origin:str,            # Value for X-M2M-Origin header 
            device_group:DeviceGroup,
           )->DeviceGroup:
    if not device_group:
        raise Exception(f"update_device_group() requires parameter device_group as input.")

    # Create the oneM2M dvi dictionary from the device
    onem2m:dict = device_group.to_onem2m()

    log.info(f"Updating device group {device_group.name} in DMO ...")        
    dmo.update_resource(api_client, origin, name=f"device-group/{device_group.name}", onem2m_body=onem2m)

    # Reload the device group and return it
    return get(api_client, origin=origin, id=None, name=device_group.name)  

def update(api_client:ApiClient,  
           origin:str=None,       
           device_group:DeviceGroup=None,
           id:str=None,
           name:str=None,
           **kwargs
          ):
    if device_group:
        return _update(api_client, origin=origin, device_group=device_group)
    elif not name and not id:
        raise Exception(f"update_device_group() requires parameter device_group, name or id as input.")

    device_group = get(api_client, origin=origin, id=id, name=name)  

    # Copy the keyword arguments into the device object
    device_group.set_from_kwargs(**kwargs)
            
    return _update(api_client,origin=origin, device_group=device_group)

def update_devices(api_client:ApiClient,  
                   origin:str=None,       
                   device_group:DeviceGroup=None,
                   name:str=None,
                   add_names:List[str]=None,
                   remove_names:List[str]=None,
                  ):
    if not device_group and not name:
        raise Exception(f"update_devices() requires parameter device_group or name as input.")

    if not device_group:
        device_group = get(api_client, origin=origin, name=name)
        
    device_group.add_devices(add_names)
    device_group.remove_devices(remove_names)

    return _update(api_client, origin, device_group)


def update_applications(api_client:ApiClient,  
                        origin:str=None,       
                        device_group:DeviceGroup=None,
                        name:str=None,
                        add_names:List[str]=None,
                        remove_names:List[str]=None,
                       ):
    if not device_group and not name:
        raise Exception(f"update_applications() requires parameter device_group or name as input.")

    if not device_group:
        device_group = get(api_client, origin=origin, name=name)
        
    device_group.add_applications(add_names)
    device_group.remove_applications(remove_names)

    return _update(api_client, origin, device_group)
