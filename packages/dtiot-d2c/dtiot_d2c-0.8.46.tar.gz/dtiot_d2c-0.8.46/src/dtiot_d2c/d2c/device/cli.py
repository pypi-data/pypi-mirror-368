import json
import logging
from argparse import ArgumentParser

import dtiot_d2c.d2c as d2c
import dtiot_d2c.dmo as dmo
from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface
from dtiot_d2c.d2c import CMDARGS
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.device import Device
from dtiot_d2c.d2c.device.consts import *
from dtiot_d2c.d2c.get_response import GetResponse
from dtiot_d2c.dmo import dmoCLI as dmocli

log = logging.getLogger(__name__)
            
#####################################################################################
class AddDeviceCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Adds a device."

    def addCmdLineArgs(self, argsParser):

        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n", required=True)

        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-de")  # descripton
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-la")  # label
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-dty") # device type
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-dna") # device name
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-fv")  # firmware version
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-sv")  # software version
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ov")  # os version
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-lo")  # location

        if not self.hasPreDefinedCmdArg("--protocol"):
            self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-pr")  # protocols

        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ma")  # manufacturer
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-mo")  # model
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-smo") # sub model
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ic")  # iccid
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-hv")  # hardware version
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-cy")  # country code
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-up")  # uplink properties
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-dp")  # device properties

        # LWM2M
        #if not self.hasHideCmdArg("--lwm2m"):

        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-cid")  # credentials id
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-csec") # credentials secret
        
    def main(self, cmdargs=None):
        
        if cmdargs.protocol in ["LoRaWAN", "UDP", "MQTT", "DTLS CoAP", "CoAP", "HTTP"]:
            raise Exception(f"Protocol {cmdargs.protocol} not supported yet.")

        if not cmdargs.credentials_id:
            cmdargs.credentials_id = cmdargs.name

        uplink_properties = json.loads(cmdargs.uplink_properties) if cmdargs.uplink_properties else None
        device_properties = json.loads(cmdargs.device_properties) if cmdargs.device_properties else None
        
        response = Device.create(self.apiConn, 
                                 origin=cmdargs.origin or self.apiConn.origin,
                                 name=cmdargs.name,
                                 iccid=getattr(cmdargs, "iccid", ""),
                                 description=cmdargs.description, 
                                 label=getattr(cmdargs, "label", None),
                                 device_type=getattr(cmdargs, "device_type", None),
                                 device_name=getattr(cmdargs, "device_name", None),
                                 firmware_version=getattr(cmdargs, "firmware_version", None),
                                 software_version=getattr(cmdargs, "software_version", None),
                                 os_version=getattr(cmdargs, "os_version", None),
                                 location=getattr(cmdargs, "location", None),
                                 protocols=[cmdargs.protocol],                                
                                 manufacturer=getattr(cmdargs, "manufacturer", None),
                                 model=getattr(cmdargs, "model", None),
                                 sub_model=getattr(cmdargs, "sub_model", None),
                                 country=getattr(cmdargs, "country", None),
                                 hardware_version=getattr(cmdargs, "hardware_version", None),
                                 uplink_properties=uplink_properties,
                                 device_properties=device_properties,
                                 credentials_id=getattr(cmdargs, "credentials_id", None),                                
                                 credentials_secret=getattr(cmdargs, "credentials_secret", None),
                                )
        
        GetResponse(response=response).print()

class AddLwm2mDeviceCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Adds a lwm2m device."

    def addCmdLineArgs(self, argsParser):

        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n", required=True)
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-cid", required=True)  # credentials id
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-csec", required=True) # credentials secret

        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-de")  # descripton
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-la")  # label
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-dty") # device type
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-dna") # device name
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-fv")  # firmware version
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-sv")  # software version
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ov")  # os version
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-lo")  # location

        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ma")  # manufacturer
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-mo")  # model
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-smo") # sub model
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ic")  # iccid
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-hv")  # hardware version
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-cy")  # country code
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-up")  # uplink properties
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-dp")  # device properties


    def main(self, cmdargs=None):
        uplink_properties = json.loads(cmdargs.uplink_properties) if cmdargs.uplink_properties else None
        device_properties = json.loads(cmdargs.device_properties) if cmdargs.device_properties else None
        
        response = Device.create(self.apiConn, 
                                 origin=cmdargs.origin or self.apiConn.origin,
                                 name=cmdargs.name,
                                 iccid=getattr(cmdargs, "iccid", ""),
                                 description=cmdargs.description, 
                                 label=getattr(cmdargs, "label", None),
                                 device_type=getattr(cmdargs, "device_type", None),
                                 device_name=getattr(cmdargs, "device_name", None),
                                 firmware_version=getattr(cmdargs, "firmware_version", None),
                                 software_version=getattr(cmdargs, "software_version", None),
                                 os_version=getattr(cmdargs, "os_version", None),
                                 location=getattr(cmdargs, "location", None),
                                 protocols=["LWM2M"],                                
                                 manufacturer=getattr(cmdargs, "manufacturer", None),
                                 model=getattr(cmdargs, "model", None),
                                 sub_model=getattr(cmdargs, "sub_model", None),
                                 country=getattr(cmdargs, "country", None),
                                 hardware_version=getattr(cmdargs, "hardware_version", None),
                                 uplink_properties=uplink_properties,
                                 device_properties=device_properties,
                                 credentials_id=getattr(cmdargs, "credentials_id", None),                                
                                 credentials_secret=getattr(cmdargs, "credentials_secret", None),
                                )
        
        GetResponse(response=response).print()
        
#####################################################################################
class UpdateDeviceCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Updates the attributes of a device."

    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-i")

        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-de")  # descripton
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-la")  # label
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-dty") # device type
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-dna") # device name
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-fv")  # firmware version
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-sv")  # software version
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ov")  # os version
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-hv")  # hardware version
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-lo")  # location
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-pr")  # protocols
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ma")  # manufacturer
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-mo")  # model
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-smo") # sub model
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ic")  # iccid
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-cy")  # country
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-up")  # uplink properties
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-dp")  # device properties

        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-cid")  # credentials id
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-csec") # credentials secret

        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-lbl")  # labels

    def main(self, cmdargs=None):
        
        if cmdargs.protocol in ["LoRaWAN", "UDP", "MQTT", "DTLS CoAP", "CoAP", "HTTP"]:
            raise Exception(f"Protocol {cmdargs.protocol} not supported yet.")

        if not cmdargs.name and not cmdargs.id:
            raise Exception(f"--name or --id option required to identify device.")            

        uplink_properties = json.loads(cmdargs.uplink_properties) if cmdargs.uplink_properties else None
        device_properties = json.loads(cmdargs.device_properties) if cmdargs.device_properties else None
        
        response = Device.update(self.apiConn, 
                                 origin=cmdargs.origin or self.apiConn.origin,
                                 name=cmdargs.name,
                                 id=cmdargs.id,                                 
                                 iccid=getattr(cmdargs, "iccid", ""),
                                 description=cmdargs.description, 
                                 label=getattr(cmdargs, "label", None),
                                 device_type=getattr(cmdargs, "device_type", None),
                                 device_name=getattr(cmdargs, "device_name", None),
                                 firmware_version=getattr(cmdargs, "firmware_version", None),
                                 software_version=getattr(cmdargs, "software_version", None),
                                 os_version=getattr(cmdargs, "os_version", None),
                                 location=getattr(cmdargs, "location", None),
                                 protocols=[cmdargs.protocol],                                
                                 manufacturer=getattr(cmdargs, "manufacturer", None),
                                 model=getattr(cmdargs, "model", None),
                                 sub_model=getattr(cmdargs, "sub_model", None),
                                 country=getattr(cmdargs, "country", None),
                                 hardware_version=getattr(cmdargs, "hardware_version", None),
                                 uplink_properties=uplink_properties,
                                 device_properties=device_properties,
                                 credentials_id=getattr(cmdargs, "credentials_id", None),                                
                                 credentials_secret=getattr(cmdargs, "credentials_secret", None),
                                 labels=getattr(cmdargs, "labels", None),
                                )
        if not response:
            raise Exception(f"Device {cmdargs.name or cmdargs.id} does not exist")
                
        GetResponse(response=response).print()

#####################################################################################
class GetDevicesCLI(ApiConnCmdLineInterface):
    
    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Returns the details of a single device or a list of devices."
    
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
        response = Device.get(self.apiConn,
                              origin=cmdargs.origin,
                              name=cmdargs.name,
                              id=cmdargs.id,
                              limit=cmdargs.limit,
                              offset=cmdargs.offset,
                              resultContentIndocator=cmdargs.rci, 
                              select=cmdargs.select,
                              format=cmdargs.format)

        if not response and (cmdargs.name or cmdargs.id):
            raise Exception(f"Device {cmdargs.name or cmdargs.id} does not exist")   
        elif response:
            GetResponse(response=response).print(cmdargs.sepchar)

#####################################################################################            
class DeleteDeviceCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Deletes a device object."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-i")
                
    def main(self, cmdargs=None):
        obj = Device.delete(self.apiConn, 
                            origin=cmdargs.origin, 
                            id=cmdargs.id,
                            name=cmdargs.name)

        if obj:
            print(str(obj))            
            
#####################################################################################            
class InjectUplinkMessageCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Injects an uplink message for a device to d2c."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-i")
        
        argsParser.add_argument("-con", "--content", metavar="<string>", dest="content",
                                required=False, 
                                help="Content to inject as message.")

        argsParser.add_argument("-conf", "--content-file", metavar="<file>", dest="content_file",
                                required=False, 
                                help="File which contains the content to inject as message.")

        argsParser.add_argument("-cont", "--content-type", metavar="<mime-type>", dest="content_type",
                                choices=["text/plain", "application/json"], default="text/plain",
                                required=False, 
                                help="Type of the content. Default is text/plain.")

    def main(self, cmdargs=None):
        content = None                
        
        if cmdargs.content:
            content = cmdargs.content 
        elif cmdargs.content_file:
            f = open(cmdargs.content_file, "r")
            content = f.read()
            f.close()
        else:
            raise Exception("Parameter --content or --content-file required.")                            
        
        #content = json.loads(content)
        response = Device.inject_uplink_message(self.apiConn,
                                                origin=cmdargs.origin,
                                                id=cmdargs.id,
                                                name=cmdargs.name,
                                                content=content,
                                                content_type=cmdargs.content_type
                                               )
        if response:
            GetResponse(response=response).print()

#####################################################################################            
class InjectDownlinkMessageCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Injects a downlink message for a device to d2c."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-i")
        
        argsParser.add_argument("-con", "--content", metavar="<string>", dest="content",
                                required=False, 
                                help="Content to inject as message.")

        argsParser.add_argument("-conf", "--content-file", metavar="<file>", dest="content_file",
                                required=False, 
                                help="File which contains the content to inject as message.")

        argsParser.add_argument("-cont", "--content-type", metavar="<mime-type>", dest="content_type",
                                choices=["text/plain", "application/json"], default="text/plain",
                                required=False, 
                                help="Type of the content. Default is text/plain.")

    def main(self, cmdargs=None):
        content = None                
        
        if cmdargs.content:
            content = cmdargs.content 
        elif cmdargs.content_file:
            f = open(cmdargs.content_file, "r")
            content = f.read()
            f.close()
        else:
            raise Exception("Parameter --content or --content-file required.")                            
        
        #content = json.loads(content)
        response = Device.inject_downlink_message(self.apiConn,
                                                  origin=cmdargs.origin,
                                                  id=cmdargs.id,
                                                  name=cmdargs.name,
                                                  content=content,
                                                  content_type=cmdargs.content_type
                                                 )
        if response:
            GetResponse(response=response).print()
            
#####################################################################################
class GetDeviceMessagesCLI(ApiConnCmdLineInterface):
    
    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Returns the messages related to a device."
    
    def addCmdLineArgs(self, argsParser):
        
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n") # Device name
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-i") # Device id
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ms", required=True) # Message store
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-mn")  # Message name

        argsParser.add_argument("-la", "--last", dest="last", action="store_const", const=True, default=False,
                                help="If set only the last message is returned from the store.")
                
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-li")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-os")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-s")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-f")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-sc")
                
    def main(self, cmdargs=None):
        
        msg_store:MessageStore = None
        if cmdargs.msg_store in ["uplink-inbound", "uli"]:
            msg_store = INBOUND_UPLINK_MESSAGE_STORE
        elif cmdargs.msg_store in ["uplink-outbound", "ulo"]:
            msg_store = OUTBOUND_UPLINK_MESSAGE_STORE
            raise Exception("Outbound uplink messages are not supported yet.")
        if cmdargs.msg_store in ["downlink-inbound", "dli"]:
            msg_store = INBOUND_DOWNLINK_MESSAGE_STORE
        elif cmdargs.msg_store in ["downlink-outbound", "dlo"]:
            msg_store = OUTBOUND_DOWNLINK_MESSAGE_STORE
        
        response = Device.get_messages(self.apiConn,
                                       origin=cmdargs.origin,
                                       name=cmdargs.name,
                                       id=cmdargs.id,
                                       msg_store=msg_store,
                                       msg_name=cmdargs.message_name,
                                       last=cmdargs.last,
                                       limit=cmdargs.limit,
                                       offset=cmdargs.offset,
                                       select=cmdargs.select,
                                       format=cmdargs.format)
        
        GetResponse(response=response).print(cmdargs.sepchar)
        
#####################################################################################
class DeleteDeviceMessageCLI(ApiConnCmdLineInterface):
    
    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Deletes a device message from a mesage store."
    
    def addCmdLineArgs(self, argsParser):
        
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n")  # Device name
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-i")  # Device id
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-ms") # Message store
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-mn") # Message name
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-mi") # Message id
                
    def main(self, cmdargs=None):
        
        msg_store:MessageStore = None
        if cmdargs.msg_store in ["uplink-inbound", "uli"]:
            msg_store = INBOUND_UPLINK_MESSAGE_STORE
        elif cmdargs.msg_store in ["uplink-outbound", "ulo"]:
            msg_store = OUTBOUND_UPLINK_MESSAGE_STORE
            raise Exception("Outbound uplink messages are not supported yet.")
        if cmdargs.msg_store in ["downlink-inbound", "dli"]:
            msg_store = INBOUND_DOWNLINK_MESSAGE_STORE
        elif cmdargs.msg_store in ["downlink-outbound", "dlo"]:
            msg_store = OUTBOUND_DOWNLINK_MESSAGE_STORE
        
        Device.delete_message(self.apiConn,
                              origin=cmdargs.origin,
                              name=cmdargs.name,
                              id=cmdargs.id,
                              msg_store=msg_store,
                              msg_name=cmdargs.message_name,
                              msg_id=cmdargs.message_id)
