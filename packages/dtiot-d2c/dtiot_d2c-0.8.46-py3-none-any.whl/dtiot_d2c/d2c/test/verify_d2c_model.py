import json
import logging
import sys
from argparse import ArgumentParser

import dtiot_d2c.d2c as d2c
import dtiot_d2c.dmo as dmo
from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface
from dtiot_d2c.d2c import CMDARGS, Device, DeviceGroup, OneM2MBase
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.get_response import GetResponse
from dtiot_d2c.d2c.utils import color
from dtiot_d2c.dmo import dmoCLI as dmocli

log = logging.getLogger(__name__)
            
def print_flushed(s:str, end=None):
    print(s, end=end)
    sys.stdout.flush()    

def print_red(s:str, end=None):
    print_flushed(f"{color.RED}{s}{color.END}", end=end)

def print_green(s:str, end=None):
    print_flushed(f"{color.GREEN}{s}{color.END}", end=end)

def check_if_ae_exists(api_conn, origin, rn:str)->bool:
    print_flushed(f"Checking ae  '{rn}' ... ", end="")
    
    response = dmo.get_resources(api_conn, origin, resourceName=rn)
    if not response:
        print_red(f"NOT OK. Ae {rn} not found!")  
        return False      
    else:
        print_green("OK")
        return True

def check_if_cnt_exists(api_conn, origin, rn:str)->bool:
    print_flushed(f"Checking cnt '{rn}' ... ", end="")
    response = dmo.get_resources(api_conn, origin, resourceName=rn)
    if not response:
        print_red(f"NOT OK. Cnt {rn} not found!")  
        return False      
    else:
        print_green("OK")
        return True
    
def check_if_sub_exists(api_conn, origin, parent_rn:str, sub_rn:str, url:str=None)->bool:
    if parent_rn:
        print_flushed(f"Checking sub '{sub_rn}' in '{parent_rn}' ... ", end="")
        response = dmo.get_resources(api_conn, origin, resourceName=parent_rn)
    else:
        print_flushed(f"Checking sub '{sub_rn}' ... ", end="")
        response = dmo.get_resources(api_conn, origin, resourceType="sub")

    if not response:
        print_red(f"NOT OK. Resource {parent_rn} not found!")  
        return False      

    subs = []    
    if parent_rn:
        subs = response.get("m2m:sub", [])
        if not subs:
            print_red(f"NOT OK. No subscriptions in {parent_rn} found!")  
            return False    
    else:
        subs = response
        
    #print(json.dumps(subs))

    found_sub = None
    for sub in subs:
        rn = sub.get("rn", None)
        if rn and rn == sub_rn:
            found_sub = sub
            break

    if not found_sub:
        print_red(f"NOT OK. No subscription {sub_rn} not found in {parent_rn}!")  
        return False      

    if url:
        if not (urls := found_sub.get("nu", [])):
            print_red(f"NOT OK. No url defined in subscription {sub_rn}!")
            return False

        if url != urls[0]:
            print_red(f"WARNING. Urls of subscription {sub_rn} are different!")
            print_red(f"   Check url: {url}")
            print_red(f"   Found url: {urls[0]}")
            return False      
        else:     
            print_green("OK")
            print_flushed(f"   Check url: {url}")
            print_flushed(f"   Found url: {urls[0]}")
            return True
    else:
        print_green("OK")
        return True
    
def check_if_cnt_in_ae_exists(api_conn, origin, ae_rn:str, cnt_rn:str)->bool:
    print_flushed(f"Checking cnt '{cnt_rn}' exists in ae '{ae_rn}' ... ", end="")

    if not (response := dmo.get_resources(api_conn, origin, resourceName=ae_rn)):
        print_red(f"NOT OK. Ae {ae_rn} not found!")  
        return False      

    if not (cnts := response.get("m2m:cnt", None)):
        print_red(f"NOT OK. No containers in AE {ae_rn}!")  
        return False      

    found = False
    for cnt in cnts:
        rn = cnt.get("rn", None)
        if rn and rn == cnt_rn:
            found = True
            break

    if not found:
        print_red(f"NOT OK. No container {cnt_rn} not found in AE {ae_rn}!")  
        return False      
    else:
        print_green("OK")
        return True
            
#####################################################################################                
class VerifyD2CModelCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Creates a new device group."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")

    def main(self, cmdargs=None):

        ### NI-IPE
        # Check if AE NI-IPE 
        niipe_exists = check_if_ae_exists(self.apiConn, cmdargs.origin, "NI-IPE")
                    
        ### device-provisioning
        devprov_exists = check_if_ae_exists(self.apiConn, cmdargs.origin, "device-provisioning")        
        devprov_sub_exists = check_if_sub_exists(self.apiConn, cmdargs.origin, None, "subscription",
                                                 url="http://d2c-device-provisioning.d2c.svc.cluster.local/provisioning/application-entity")
        request_exists = check_if_cnt_in_ae_exists(self.apiConn, cmdargs.origin, "device-provisioning", "request")
        response_exists = check_if_cnt_in_ae_exists(self.apiConn, cmdargs.origin, "device-provisioning", "response")
        request_sub_exists = check_if_sub_exists(self.apiConn, cmdargs.origin, "device-provisioning/request", "subscription",
                                                 url="http://d2c-device-provisioning.d2c.svc.cluster.local/provisioning/node-list-provisioning")

            
        ### device-group
        # Check if AE device-group
        devgrp_exists = check_if_ae_exists(self.apiConn, cmdargs.origin, "device-group")     
        devgrp_sub_exists = check_if_sub_exists(self.apiConn, cmdargs.origin, "device-group", "subscription",
                                                url="http://d2c-device-provisioning.d2c.svc.cluster.local/provisioning/device-group")
        
        ### device-communication
        devcomm_exists = check_if_cnt_exists(self.apiConn, cmdargs.origin, "device-communication")

            
