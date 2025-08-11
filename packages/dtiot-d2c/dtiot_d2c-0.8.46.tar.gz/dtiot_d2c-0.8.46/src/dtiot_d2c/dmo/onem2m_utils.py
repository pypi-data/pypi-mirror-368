import fnmatch
import logging
from datetime import datetime
from typing import List, Literal

import dtiot_d2c.dmo.utils as utils
from dtiot_d2c.dmo.consts import *

log = logging.getLogger(__name__)

def convert_dict_to_onem2m_labels(d:dict)->List[str]:
    """Converts a dcitionary to onem2m labels

    Args:
        d (dict): Dictionary which shall be converted.

    Returns:
        List[str]: Array of strings of the form ["<key>:<value>", "<key>:<value>", ...]
    """
    if not d:
        return []
    
    labels = []
    for (k, v) in d.items():
        if v == None:
            v = ""
        
        if v and type(v) == str:
            v = v.replace(":", " ")
        labels.append(f"{k}:{v}")            
    return labels

def convert_onem2m_labels_to_dict(labels:List[str])->dict:
    if not labels:
        return {}
    
    d={}
    for label in labels:
        idx = label.find(":")
        if idx == -1:
            continue
        d[label[0:idx]] = utils.convert_str_to_python_type(label[idx+1:])
    return d

def convert_onem2m_timestamp_to_datetime(onem2m_ts:str= "20250101T000000,000000")->datetime:
    # "ct": "20250321T095914,759000",
    if onem2m_ts and (idx:=onem2m_ts.find(",")) > -1:
        onem2m_ts = onem2m_ts[0:idx]        

    t_date:datetime = None
    
    try:
        t_date = datetime.strptime(onem2m_ts, ONEM2M_DATE_FORMAT)
    except Exception as ex:
        log.error(f"Cannot convert creation date '{onem2m_ts}' into date objekt: {ex}")
        t_date = datetime.now()

    return t_date

def select_from_response_body(body, 
                              select:List[str] | str = None, 
                              format:Literal["JSON", "CSV"] = "CSV"
                             ):
    """_summary_

    Args:
        body (_type_): _description_
        select (List[str] | str, optional): _description_. Defaults to None.

    Raises:
        Exception: _description_
        Exception: _description_

    Returns:
        _type_: _description_
    """

    if not select:
        return body

    # dicts    
    dicts = []
    is_object = False
    
    if type(body) == dict:
        dicts.append(body)
    elif type(body) == list:
        for obj in body:
            if type(obj) == dict:
                dicts.append(obj)
            else:
                dicts.append(obj.dict())
    else:
        dicts.append(body.dict())
        is_object = True
    
    # select
    if type(select) == str:
        selectKeys = utils.splitString(select, ",")
    elif type(select) == list:
        selectKeys = select
    else:
        raise Exception(f"Unsupported type {type(select)} for select parameter {select}.")

    # format   
    if not format:
        format = "CSV"
    if format not in ["CSV", "JSON"]:
        raise Exception(f"Unsupported format {format}.")

    # Filter elements from body data
    filtered_elems = []
    for d in dicts:
        filtered_elem = {}        

        for key in selectKeys:

            if key.startswith("labels."):
                
                pattern = key[key.find(".")+1:] 
                labels = {}
                
                for label_name, label_value in d.get("labels", {}).items():
                    if fnmatch.fnmatchcase(label_name, pattern):
                        labels[label_name] = label_value
                filtered_elem["labels"] = labels
                
            else:
                filtered_elem[key] = utils.getValueFromDict(d, key, "", sepChar=".")

        filtered_elems.append(filtered_elem)

    if format.upper() == "CSV":
        lines = []
        for elem in filtered_elems:
            line = []
            for (key, value) in elem.items():
                line.append(str(value))
            lines.append(line)
        return lines if not is_object else lines[0]

    elif format.upper() == "JSON":
        return filtered_elems if not is_object else filtered_elems[0]

    else:
        raise Exception(f"Unsupported format {format}. JSON or CSV required.") 
            