import json
import logging
from enum import Enum
from typing import Union

from pydantic import BaseModel

import dtiot_d2c.d2c.utils as utils
from dtiot_d2c.d2c.onem2m_base import OneM2MBase

log = logging.getLogger(__name__)

class GetResponseType(Enum):
    ANY = 0
    ONEM2M_BASE_OBJECT = 1
    LIST_OF_ONEM2M_BASE_OBJECTS = 2
    DICT = 3
    LIST_OF_DICTS = 4
    STR = 5
    LIST_OF_STRS = 6
    LIST_OF_LISTS = 7
    NONE = 99
    UNSUPPORTED_TYPE=100

class GetResponse(BaseModel):
    response:Union[None, dict, list, str, OneM2MBase] 
    type: GetResponseType = GetResponseType.ANY
    
    def __init__(self, **data):
        super().__init__(**data)    
        self._init_type_from_response(self.response)
        
    def _init_type_from_response(self, response):
        if response is None:
            self.type = GetResponseType.NONE
        elif isinstance(response, OneM2MBase): 
            self.type = GetResponseType.ONEM2M_BASE_OBJECT
        elif isinstance(response, dict):
            self.type = GetResponseType.DICT
        elif isinstance(response, str):
            self.type = GetResponseType.STR
        elif isinstance(response, list):
            if response and isinstance(response[0], OneM2MBase): 
                self.type = GetResponseType.LIST_OF_ONEM2M_BASE_OBJECTS
            elif response and isinstance(response[0], dict):
                self.type = GetResponseType.LIST_OF_DICTS
            elif response and isinstance(response[0], str):
                self.type = GetResponseType.LIST_OF_STRS
            elif response and isinstance(response[0], list):
                self.type = GetResponseType.LIST_OF_LISTS
        else:
            self.type = GetResponseType.UNSUPPORTED_TYPE
                
    def print(self, sepchar:str=";"):
        #print(f"type: {type(self.response)}")
        #print(f"type: {self.type}")

        if not self.response or self.type == GetResponseType.NONE:
            return 
        elif self.type == GetResponseType.UNSUPPORTED_TYPE:
            print(f"Type {self.type} not supported. Cannot print result {self.result}.")
            return

        if self.type == GetResponseType.ONEM2M_BASE_OBJECT:
            print(self.response.to_json())
        elif self.type == GetResponseType.DICT:
            print(json.dumps(self.response, indent=4, cls=utils.DatetimeJsonEncoder))
        elif self.type == GetResponseType.STR:
            print(self.response)
        elif self.type == GetResponseType.LIST_OF_ONEM2M_BASE_OBJECTS:
            cnt=0
            print("[")
            for obj in self.response:
                print(obj.to_json(), end="")
                cnt += 1
                if cnt < len(self.response):
                    print(",")
            print("")
            print("]")
        elif self.type == GetResponseType.LIST_OF_DICTS:
            cnt=0
            print("[")
            for obj in self.response:
                print(json.dumps(obj, indent=4, cls=utils.DatetimeJsonEncoder), end="")
                cnt += 1
                if cnt < len(self.response):
                  print(",")
            print("")
            print("]")
        elif self.type == GetResponseType.LIST_OF_STRS:
            print(sepchar.join(self.response))
        elif self.type == GetResponseType.LIST_OF_LISTS:
            for obj in self.response:
                line = sepchar.join(obj)
                print(line)





