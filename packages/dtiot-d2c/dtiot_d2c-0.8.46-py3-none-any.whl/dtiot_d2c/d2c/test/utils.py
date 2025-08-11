import json
import logging
import subprocess
import sys
import time
import traceback

import requests

from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.test.testcli_base import TestCase, TestCLI_Base, TestSet
from dtiot_d2c.d2c.utils import color as color
from dtiot_d2c.dmo import ApiClient

log = logging.getLogger(__name__)

# Log levels
DEBUG = 10
INFO = 20
WARNING=30
ERROR = 40
CRITICAL = 50

def print_ERROR(s:str, **kwargs):
    print(f"{color.RED}{s}{color.END}", **kwargs)
    
def print_OK(s:str = "OK", **kwargs):
    print(f"{color.GREEN}{s}{color.END}", **kwargs)

def print_BOLD(s:str, **kwargs):
    print(f"{color.BOLD}{s}{color.END}", **kwargs)       
    
def load_test_configuration(run_id:str, config_file:str, config_var:str)->dict:
    ### Load configuration
    cfg_mod = utils.importModule("test_configuration", config_file)
    cfg = getattr(cfg_mod, config_var)

    # Replace some config variables
    now_secs = str(int(time.time()))
    
    s = json.dumps(cfg)
    for (var_name, var_value) in [["%RUNID%", run_id],
                                  ["%NOWSECS%", now_secs]
                                 ]:
        s = s.replace(var_name, var_value)
    cfg = json.loads(s)
    
    #for (k, v) in cfg.items():
    #    if cfg[k] and type(cfg[k]) == str:
    #        cfg[k] = cfg[k].replace("%RUNID%", run_id)    
            
    return cfg            

def call_has_element_value(d:dict, elem_path:str, test_value):
    b = utils.has_element_value(d, elem_path, test_value)
    #ok = "OK" if b else "NOT OK"
    #print(f"{ok}: has_element_value(node_response, {elem_path}, {test_value})")  
    return b  

def exec_test(label:str, test_func, *args, **kwargs):
    try:
        print(f"{label} ... ", end="", flush=True)
        rv = test_func(*args, **kwargs)
        print_OK(flush=True)
        return rv
    except Exception as ex:
        print_ERROR(f"ERROR: {ex}", flush=True)
        traceback.print_exc()
        raise ex
        #return str(ex)

class TestCase_Sleep(TestCase):
    def __init__(self, api: ApiClient, cfg:dict, run_info:str=""):    
        super().__init__(api=api, cfg=cfg)
        self._run_info = run_info
            
    def get_name(self):
        return self._run_info if self._run_info else "Sleep"
        
    def run(self):
        time.sleep(self.cfg.get("sleep_secs", 5))

    def verify(self):
        pass
        pass

def exec_test_case(test_case_name:str, *args, **kwargs):
    command = ["d2c", test_case_name]

    for arg in args:
        command.append(str(arg))
    for key, val in kwargs.items():
        command.append(key)
        command.append(str(val))
        
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    for line in process.stdout:
        print(line, end='')

    process.wait()
    return process.returncode

def get_message_from_message_monitor(key:str):
    
    url = f"htts://api.scs.iot.telekom.com/message-monitor/body/{key}"
    log.debug(f"GET {url}")
    
    headers = {
        "Content-Type":"application/json",
        "Accept": "application/json"
    }
    log.debug(f"HEADERS: {headers}")
    
    response = requests.get(url, headers=headers)
    
    if not response.ok:
        response.raise_for_status()    

    return response.content    