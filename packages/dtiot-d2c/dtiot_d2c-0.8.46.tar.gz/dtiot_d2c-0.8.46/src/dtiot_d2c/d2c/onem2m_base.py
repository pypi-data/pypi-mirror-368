import json
import logging
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

import dtiot_d2c.d2c.consts as d2c_consts
import dtiot_d2c.dmo as dmo
from dtiot_d2c.d2c import utils as utils

log = logging.getLogger(__name__)

class OneM2MBase(BaseModel):
    onem2m:dict = Field(default_factory=dict)

    def _get_child_array_attribute(self, child_name, attr_name, default_value=None):
        child = self.onem2m.get(child_name, [])
        return child[0].get(attr_name, default_value) if child else default_value

    def _set_child_array_attribute(self, child_name, attr_name, value):
        child = self.onem2m.get(child_name, None)
        if not child:
            child = self.onem2m[child_name] = []
            child.append({})
        child[0][attr_name] = value
    
    @property
    def id(self):
        return self.onem2m.get("ri", None) if self.onem2m else None

    @property
    def name(self):
        return self.onem2m.get("rn", None) if self.onem2m else None

    @property
    def labels(self)->dict:
        return dmo.convert_onem2m_labels_to_dict(self.onem2m.get("lbl", [])) if self.onem2m else {}

    def _set_labels(self, value:dict):
        self.onem2m["lbl"] = dmo.convert_dict_to_onem2m_labels(value)

    @labels.setter
    def labels(self, value:dict):
        self._set_labels(value)

    def _get_label(self, label_name, default_value=None):
        return self.labels.get(label_name, default_value)
    
    def _set_label(self, label_name, label_value):
        d = self.labels
        if label_value != None:
            d[label_name] = label_value
        elif label_name in d.keys():
            del d[label_name]
        self.labels = d
        
    def _del_label(self, label_name):
        self._set_label(label_name, None)        

    def integrate_labels(self, labels, del_label_func=None, set_label_func=None, set_labels_func=None,
                         force_integration:bool=False):
        if not del_label_func:
            del_label_func = self._del_label
        if not set_label_func:
            set_label_func = self._set_label
        if not set_labels_func:
            set_labels_func = self._set_labels

        if labels == None:
            return 

        if not force_integration:
            operation = "replace"            
            if labels:        
                for key in labels.keys():
                    if key[0] in (d2c_consts.UPDT_LABS_OPERATION_INDICATOR_ADD, d2c_consts.UPDT_LABS_OPERATION_INDICATOR_DEL):
                        operation = "integrate"
                        break
        else:
            operation = "integrate"
            
        if operation == "integrate":
            for key, value in labels.items():
                if key[0] == d2c_consts.UPDT_LABS_OPERATION_INDICATOR_DEL or value == None:
                    del_label_func(key[1:])
                elif key[0] == d2c_consts.UPDT_LABS_OPERATION_INDICATOR_ADD:
                    set_label_func(key[1:], value)
                else:
                    set_label_func(key, value)
        else:
            if type(labels) == str:
                labels = json.loads(labels)

            if type(labels) == dict:
                set_labels_func(labels)

            elif labels != None:
                raise Exception(f"Type {type(labels)} for onem2m labels not supported.")        
            
    @property
    def creationTime(self)->datetime:
        return dmo.convert_onem2m_timestamp_to_datetime(self.onem2m.get("ct", "20250101T000000,000000"))

    @property
    def lastModificationTime(self)->datetime:
        return dmo.convert_onem2m_timestamp_to_datetime(self.onem2m.get("lt", "20250101T000000,000000"))

    def model_dump(self,  *args, **kwargs):
        md = super().model_dump(*args, **kwargs)
        del md["onem2m"]
        for key in ["id", 
                    "name", 
                    "creationTime", 
                    "lastModificationTime",
                    "labels"
                   ]:
            md[key] = getattr(self, key)

        return md
        
    def set_from_kwargs(self, **kwargs):
        self.integrate_labels(kwargs.get("labels", None), force_integration=True)

    def to_onem2m(self)->dict:
        raise Exception("Function to_onem2m() not implemented.")

    def __str__(self):
        return str(self.model_dump())

    def to_json(self)->str:
        """Returns the object as a json string.
        Returns:
            str: JSON string
        """
        return json.dumps(self.dict(), sort_keys=False, indent=4, cls=utils.DatetimeJsonEncoder)
    
    ### 
    # Manage prefixed labels
    def _get_prefixed_labels(self, prefix:str)->dict:
        d = {}
        for (k, v) in self.labels.items():
            if k.startswith(prefix):
                d[k[len(prefix):]] = v
        return d

    def _get_unprefixed_labels(self, ignore_prefixes:List[str], system_labels:List[str],
                               prefix_separator_char="_"
                               )->dict:
        d = {}
        for (k, v) in self.labels.items():
            if k in system_labels:
                continue

            idx = k.find(prefix_separator_char)
            if idx >= 0 and k[0:idx] in ignore_prefixes:
                continue
    
            d[k] = v

        return d

    def _delete_prefixed_labels(self, prefix:str):
        old_labels = self.labels
        new_labels = {}
        for (k, v) in old_labels.items():
            if not k.startswith(prefix):
                new_labels[k] = old_labels[k]
        self.labels = new_labels

    def _set_prefixed_labels(self, prefix:str, props:dict):
        if props == None:
            return
        
        self._delete_prefixed_labels(prefix)
        
        for (key, value) in props.items():
            self._set_label(f"{prefix}{key}", value)   

    def _set_prefixed_label(self, prefix:str, key:str, value):
        self._set_label(f"{prefix}{key}", value)

    def _del_perfixed_property(self, prefix:str, key:str):
        self._del_label(f"{prefix}{key}")

    
    
    
