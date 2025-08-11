import json
import logging
from datetime import datetime
from typing import List

import dtiot_d2c.dmo as dmo
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.onem2m_base import OneM2MBase
from dtiot_d2c.dmo import ApiClient
from pydantic import BaseModel, Field

from .consts import *

log = logging.getLogger(__name__)

'''
 {
            "rn": "23fe29a2-0302-4791-ba79-ac7330048a5f",
            "con": "Hallo von Roland",
            "cnf": "text/plain:0",
            "ty": 4,
            "cs": 16,
            "st": 0,
            "cr": "Cd2ccli4",
            "ri": "67ebf327c8a381a4e97e2668",
            "pi": "67ebb9d5c8a381a4e97e2614",
            "ct": "20250401T140735,303000",
            "lt": "20250401T140735,303000"
}
'''
class Message(OneM2MBase):
    
    @property
    def content(self):
        return self.onem2m.get("con", None) 

    @content.setter
    def content(self, value):
        self.onem2m["con"] = value
        
    @property
    def contentInfo(self):
        return self.onem2m.get("cnf", "text/plain:0") 

    @contentInfo.setter
    def contentInfo(self, value):
        self.onem2m["cnf"] = value

    @property
    def contentType(self):
        if not (ci := self.contentInfo):
            return None
        elif (idx := ci.find(":")) < 0:
            return 
        else:
            return ci[:idx]

    @property
    def contentEncoding(self):
        if not (ci := self.contentInfo):
            return None
        elif (idx := ci.find(":")) < 0:
            return 
        else:
            try:
                return utils.get_enum_name_by_value(dmo.CE, int(ci[idx+1:]), default="")                
            except Exception as ex:
                log.error(f"Could not convert content encoding {ci[idx+1:]}: {ex}")
                return ""

    @property
    def contentSize(self):
        return self.onem2m.get("cs", "text/plain:0") 

    @contentSize.setter
    def contentSize(self, value):
        self.onem2m["cs"] = value

    def model_dump(self,  *args, **kwargs):
        md = super().model_dump(*args, **kwargs)
        for key in ["content", 
                    "contentInfo",
                    "contentSize",
                    "contentType",
                    "contentEncoding"
                   ]:
            md[key] = getattr(self, key)
        del md["labels"]
        return md
        
  
        