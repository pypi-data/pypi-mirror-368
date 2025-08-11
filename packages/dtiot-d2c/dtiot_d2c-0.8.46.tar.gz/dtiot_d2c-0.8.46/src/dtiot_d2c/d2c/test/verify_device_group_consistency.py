import json
import logging
from argparse import ArgumentParser

import dtiot_d2c.d2c as d2c
import dtiot_d2c.d2c.test.utils as tutils
import dtiot_d2c.dmo as dmo
from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface
from dtiot_d2c.d2c import CMDARGS, Application, Device, DeviceGroup, OneM2MBase
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.get_response import GetResponse
from dtiot_d2c.dmo import dmoCLI as dmocli

log = logging.getLogger(__name__)
            
#####################################################################################                
class VerifyDeviceGroupConsistencyCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Verifies the consistency of a device group."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n",required=True)

    def main(self, cmdargs=None):
        
        device_group_name = cmdargs.name
        api = self.apiConn
        
        device_group:DeviceGroup = DeviceGroup.get(api, name=device_group_name)

        if not device_group:
            raise Exception(f"Could not load device group {device_group_name}.")

        GetResponse(response=device_group).print()      
        
        ###
        # Load referenced applications
        applications = []
        for id in device_group.applicationIds:
            print(f"Loading application {id} ... ", end="", flush=True)
            application:Application = Application.get(api, id=id)

            if not application:
                tutils.print_ERROR(f"ERROR: could not load application.", flush=True)
            else:
                tutils.print_OK(flush=True)
            applications.append(application)            

        ###
        # Load referenced devices
        devices = []
        for id in device_group.deviceIds:
            print(f"Loading device {id} ... ", end="", flush=True)
            device:Device = Device.get(api, id=id)

            if not device:
                tutils.print_ERROR(f"ERROR: could not load device.", flush=True)
            else:
                tutils.print_OK(flush=True)

            devices.append(device)            
        
        ###
        # Check the device communication containers
        for device in devices:
            for application in applications:
                device_name = device.name
                application_name = application.name

                n = f"device-communication/{device_name}/received-msg/{device_group_name}-{application_name}-{device_name}"
                print(f"Checking {n} ... ", end="", flush=True)
                
                onem2m_dict = dmo.get_resources(api, resourceType="subscription", resourceName=n)
                if not onem2m_dict:
                    tutils.print_ERROR(f"ERROR: subscription does not exist.", flush=True)
                else:
                    tutils.print_OK(flush=True)                        

                
        
        