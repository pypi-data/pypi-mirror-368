import json
import logging
from argparse import ArgumentParser

import dtiot_d2c.d2c as d2c
import dtiot_d2c.dmo as dmo
from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface
from dtiot_d2c.d2c import CMDARGS, Device, DeviceGroup, OneM2MBase
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.get_response import GetResponse
from dtiot_d2c.dmo import dmoCLI as dmocli

log = logging.getLogger(__name__)
            
#####################################################################################                
class AddDeviceGroupCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Creates a new device group."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n",required=True)
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-de")  # --description
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ds")  #--devices
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-as")  #--applications

    def main(self, cmdargs=None):
            
        response = DeviceGroup.create(self.apiConn, 
                                      origin=cmdargs.origin,
                                      name=cmdargs.name,
                                      devices=cmdargs.devices,
                                      applications=cmdargs.applications,
                                      description=cmdargs.description
                                     )
        GetResponse(response=response).print()        
            
#####################################################################################
class GetDeviceGroupsCLI(ApiConnCmdLineInterface):
    
    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Returns the details of a device group."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-i")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-li")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-os")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-rci")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-s")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-f")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-sc")
                
    def main(self, cmdargs=None):

        format = cmdargs.format # if cmdargs.format else "CSV" if cmdargs.select else None

        response = DeviceGroup.get(self.apiConn, 
                                   origin=cmdargs.origin,
                                   id=cmdargs.id,
                                   name=cmdargs.name,
                                   limit=cmdargs.limit,
                                   offset=cmdargs.offset,
                                   resultContentIndocator=cmdargs.rci, 
                                   select=cmdargs.select,
                                   format=format)
        
        if not response and (cmdargs.name or cmdargs.id):
            raise Exception(f"Device {cmdargs.name or cmdargs.id} does not exist")   
        elif response:
            GetResponse(response=response).print(cmdargs.sepchar)
            
#####################################################################################
class UpdateDeviceGroupCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Updates a device group."

    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o") 
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n")  # --name
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-i")  # --id
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-de") # --description
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ds") # --devices
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-as") # --applications
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-lbl")  # labels
        
    def main(self, cmdargs=None):
            
        response = DeviceGroup.update(self.apiConn, 
                                      origin=cmdargs.origin,
                                      id=cmdargs.id,
                                      name=cmdargs.name,
                                      devices=cmdargs.devices,
                                      applications=cmdargs.applications,
                                      description=cmdargs.description,
                                      labels=cmdargs.labels
                                     )
        
        if not response:
            raise Exception(f"Device group {cmdargs.name or cmdargs.id} does not exist")
                
        GetResponse(response=response).print()    

#####################################################################################            
class DeleteDeviceGroupCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Deletes a device group."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n")  # --name
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-i")  # --id
        
                
    def main(self, cmdargs=None):
        obj = DeviceGroup.delete(self.apiConn, 
                                 origin=cmdargs.origin, 
                                 id=cmdargs.id,
                                 name=cmdargs.name)

        if obj:
            print(str(obj))                                    

class ModifyDevicesCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Adds devices or removes devices to or from the device group."

    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o") 
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n", required=True)
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-addns")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-rmns")

    def main(self, cmdargs=None):
        add_names = utils.splitString(cmdargs.add_names, ",") if cmdargs.add_names else None
        remove_names = utils.splitString(cmdargs.remove_names, ",") if cmdargs.remove_names else None
            
        response = DeviceGroup.update_devices(self.apiConn, 
                                              origin=cmdargs.origin,
                                              name=cmdargs.name,
                                              add_names=add_names,
                                              remove_names=remove_names,
                                             )
            
        GetResponse(response=response).print()   
          
class ModifyApplicationsCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Returns the devices of the device group."

    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o") 
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n", required=True)
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-addns")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-rmns")

    def main(self, cmdargs=None):
        add_names = utils.splitString(cmdargs.add_names, ",") if cmdargs.add_names else None
        remove_names = utils.splitString(cmdargs.remove_names, ",") if cmdargs.remove_names else None
            
        response = DeviceGroup.update_applications(self.apiConn, 
                                                   origin=cmdargs.origin,
                                                   name=cmdargs.name,
                                                   add_names=add_names,
                                                   remove_names=remove_names,
                                                  )
        if not response:
            raise Exception(f"Device group {cmdargs.name or cmdargs.id} does not exist")
                    
        GetResponse(response=response).print()         
                    
        
class GetDeviceGroupDevicesCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Adds applications or removes applications to or from the device group."

    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o") 
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n", required=True)
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-s")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-f")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-sc")

    def main(self, cmdargs=None):
            
        device_group:DeviceGroup = DeviceGroup.get(self.apiConn, cmdargs.origin, cmdargs.name)

        #dics=[]
        #for device_id in device_group.deviceIds:
        #    device:Device = Device.get(self.apiConn, cmdargs.origin, )
        #GetResponse(response=response).print()                                   