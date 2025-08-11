import json
import logging
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, PrivateAttr

import dtiot_d2c.d2c.consts as d2c_consts
import dtiot_d2c.dmo as dmo
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.onem2m_base import OneM2MBase
from dtiot_d2c.dmo import ApiClient

from .consts import *

log = logging.getLogger(__name__)

class Application(OneM2MBase):
    _application_type: str = PrivateAttr(default=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize the application type
        self._application_type = self._get_label(APPL_TYPE_LABEL_NAME, default_value=APPL_TYPE_DEFAULT)

    @property
    def urls(self)->List[str]:
        return self.onem2m.get("poa", []) 

    @urls.setter
    def urls(self, value:List[str]):
        urls_1 = self.urls
        self.onem2m["poa"] = utils.integrate_lists(urls_1, value)

    @property
    def type(self):
        return self._get_label(f"{APPL_TYPE_LABEL_NAME}")

    @property
    def description(self):
        return self._get_label(f"{DESCRIPTION_LABEL_NAME}")

    @description.setter
    def description(self, value): 
        labels = {f"+{DESCRIPTION_LABEL_NAME}":value}
        self.integrate_labels(labels)
        
    ### 
    # connection properties

    def set_connection_properties(self, props:dict):
        prefix = CONN_PROPS_LABEL_PREFIXS.get(self._application_type, APPL_TYPE_DEFAULT)
        self._set_prefixed_labels(prefix, props)

    def delete_connection_properties(self):
        prefix = CONN_PROPS_LABEL_PREFIXS.get(self._application_type, APPL_TYPE_DEFAULT)
        self._delete_prefixed_labels(prefix)

    def set_connection_property(self, key, value):
        prefix = CONN_PROPS_LABEL_PREFIXS.get(self._application_type, APPL_TYPE_DEFAULT)
        self._set_prefixed_label(prefix, key, value)
        
    def del_connection_property(self, key):
        prefix = CONN_PROPS_LABEL_PREFIXS.get(self._application_type, APPL_TYPE_DEFAULT)
        self._del_perfixed_property(prefix, key)

    @property    
    def connectionProperties(self)->dict:   
        prefix = CONN_PROPS_LABEL_PREFIXS.get(self._application_type, APPL_TYPE_DEFAULT)
        return self._get_prefixed_labels(prefix)
    
    @connectionProperties.setter
    def connectionProperties(self, props:dict):
        self.set_connection_properties(props)
            
    ### regular functions
    #
    def model_dump(self,  *args, **kwargs):
        md = super().model_dump(*args, **kwargs)
        for key in ["type",
                    "urls", 
                    "connectionProperties",
                    "description",
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
        for key in ["urls",
                   ]:
            if not (value := kwargs.get(key, None)):
                continue

            if type(value) == list:
                setattr(self, key, value)
            elif type(value) == str:
                setattr(self, key, utils.splitString(value, ","))
            else:
                log.error(f"Unsupported type {type(value)} for argument {key}={value}")

        ### 
        # Copy the connection properties into the labels of the application
        self.integrate_labels(kwargs.get("connection_properties", None), 
                              self.del_connection_property,
                              self.set_connection_property,
                              self.set_connection_properties)
                  
    def to_onem2m(self, **kwargs)->dict:
        d = {}
        for (attr_name, onem2m_path) in [["urls", "poa"],
                                        ]:
            d[onem2m_path] = getattr(self, attr_name)

        d["lbl"] = self.onem2m.get("lbl", [])

        # Add the d2c version
        d2c_version_lbl = f"{d2c_consts.D2C_SYSTEM_VERSION_LABEL}:{d2c_consts.D2C_SYSTEM_VERSION}"
        if d2c_version_lbl not in d["lbl"]:
            d["lbl"].append(d2c_version_lbl)

        # Add the application type
        appl_type = kwargs.get("application_type", APPL_TYPE_WEBHOOK)
        appl_type_lbl = f"{APPL_TYPE_LABEL_NAME}:{appl_type}"
        if appl_type_lbl not in d["lbl"]:
            d["lbl"].append(appl_type_lbl)
            
        # add the additional keyword arguments
        for (key, value) in kwargs.items():
            d[key] = value

        return {"m2m:ae":d}

    ######################################################################
    # Static public functions
    ######################################################################
    def get_create_onem2m_dict(name:str, **kwargs)->dict:
        application_type = kwargs.get("application_type", APPL_TYPE_DEFAULT)

        if (description := kwargs.get("description", "")) == None:
            description = ""

        if (labels := kwargs.get("labels", {})) == None:
            labels = {}

        labels[APPL_TYPE_LABEL_NAME] = application_type
        labels[d2c_consts.D2C_SYSTEM_VERSION_LABEL] = d2c_consts.D2C_SYSTEM_VERSION
        labels[DESCRIPTION_LABEL_NAME] = description
        labels["type"] = "d2c"
        
        # Add the connection properties to the labels
        props = kwargs.get("connection_properties", None) or {}
        for k, v in props.items():
            n = CONN_PROPS_LABEL_PREFIXS.get(application_type)
            labels[f"{n}{k}"] = v

        return  {
            "m2m:ae": {
                "api": f"N{name}",
                "rn": f"{name}",
                "lbl": dmo.convert_dict_to_onem2m_labels(labels),
                "poa": kwargs.get("urls", []),
            }
        }
        
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

        return get(api_client, origin, id, name, resultContentIndocator=resultContentIndocator,
                   limit=limit, offset=offset, select=select, format=format)
        
    def create(api_client:ApiClient,
               origin:str=None,     
               name:str=None,
               **kwargs):    
        return create(api_client, origin=origin, name=name, **kwargs)
    
    def delete(api_client:ApiClient, 
               origin:str=None, 
               name:str=None, 
               id:str=None
              ):
        return delete(api_client, origin=origin, name=name, id=id)
    
    def update(api_client:ApiClient, 
               origin:str=None, 
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
                                     resourceType="ae", 
                                     limit=limit,
                                     offset=offset,
                                     resultContentIndocator=resultContentIndocator)
    else:
        response = dmo.get_resources(api_client, 
                                     origin=origin,
                                     #resourceType="ae", 
                                     resourceId=id,
                                     resourceName=name,
                                     limit=limit,
                                     offset=offset,
                                     resultContentIndocator=resultContentIndocator)      
    if not response:
        return None
        
    if not name and not id:
        object = [Application(onem2m=onem2m) for onem2m in response]
    else:
        object = Application(onem2m=response)  
                
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
        log.info(f"Getting application {name or id} from DMO ...")
    else:
        log.info(f"Getting applications from DMO ...")        

    return _get(api_client, origin=origin, id=id, name=name, select=select, format=format, 
                resultContentIndocator=resultContentIndocator, limit=limit, offset=offset)

def create(api_client:ApiClient, 
           origin:str=None,      
           name:str=None,
           **kwargs):

    # Only create the application if id doesn't exist
    
    log.info(f"Testing if the application {name} already exists ...")
    if (app := get(api_client, origin, name=name)):
        log.warning(f"  Application {name} already exists.")
        return app

    log.info(f"Creating application {name} in DMO ...")
    onem2m = Application.get_create_onem2m_dict(name, **kwargs)
    dmo.add_resource(api_client, origin=origin if origin else name, r_type="ae", onem2m_body=onem2m)

    return get(api_client, origin, name=name)

def delete(api_client:ApiClient, 
           origin:str=None, 
           name:str=None, 
           id:str=None
          ):
    if not name and not id:
        raise Exception(f"delete() requires parameter name or id as input.")
    
    log.info(f"Deleting application {name or id} from DMO ...")
    return dmo.delete_resource(api_client, origin=origin, name=name, id=id)

def _update(api_client:ApiClient, 
            origin:str,           
            object:Application,
           )->OneM2MBase:

    if not object:
        raise Exception(f"_update() requires parameter object as input.")

    # Create the oneM2M from the object
    onem2m:dict = object.to_onem2m()

    log.info(f"Updating application {object.name} in DMO ...")        
    dmo.update_resource(api_client, origin, name=object.name, onem2m_body=onem2m)

    # Reload the device group and return it
    return get(api_client, origin=origin, name=object.name)

def update(api_client:ApiClient,  
           origin:str=None,       
           object:OneM2MBase=None,
           id:str=None,
           name:str=None,
           **kwargs
          ):
    
    if object:
        return _update(api_client, origin, object)
    elif not name and not id:
        raise Exception(f"update() requires parameter object or name or id as input.")

    object = get(api_client, origin, id, name)  

    # Copy the keyword arguments into the object
    object.set_from_kwargs(**kwargs)
            
    return _update(api_client, origin, object)


