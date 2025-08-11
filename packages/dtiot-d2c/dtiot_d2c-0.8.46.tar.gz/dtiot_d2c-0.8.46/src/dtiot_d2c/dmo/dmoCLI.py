import argparse
import json
import logging
from argparse import ArgumentParser

from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface
from dtiot_d2c.dmo import device_provisioning as device_provisioning
from dtiot_d2c.dmo import dmo as dmo
from dtiot_d2c.dmo import utils as utils

log = logging.getLogger(__name__)

class _CFG:
    default_d2c_origin:str = "NI-IPE"
                                      
cmdArgTemplates:dict = {
    "-lbl" : ["--labels", 
        {
            "type": utils.argparse_type_json,
            "metavar":"{key:value, key:value, ...}", 
            "dest":"labels", 
            "required":False,
            "default":None,
            "help":"Labels defined by a JSON dictionary of key/value pairs."
        }
    ],
    "-rn": ["--resource-name",
            {"metavar":"<string>", 
            "dest":"rn", 
            "required": False,
            "default":None,
            "help":"Name of the resource object."}
    ],
    "-ri": ["--resource-id", 
            {"metavar":"<string>", 
            "dest":"ri", 
            "required": False,
            "default":None,
            "help":"Id of the object."}
    ],        
    "-rt": ["--resource-type", 
            {"metavar":"<string>",
            "dest": "ty",
            "choices": dmo.TYs.keys(),
            "help":f"Type of resource. Following values are possible: {dmo.TYs.keys()}"}
    ],
    "--outfile": {"metavar":"<filepath>", 
            "dest":"outfile", 
            "required": False,
            "default":None,
            "help":"File into which the log outputs shall be written additionaly."
    },
    "-o": ["--origin", 
           {"metavar":"<string>", 
            "dest":"origin", 
            "required": False,
            "default":None,
            "help":"X-M2M-ORIGIN heder."}
    ],
    "-af": ["--attribute-filter", 
            {"metavar":"<string>", 
            "dest":"attr_filters", 
            "required": False,
            "default":None,
            "help":"Comma separated list of attribute filters such as: reqRD=67dc2219c9a47b53f222658b,st=0"}
    ],            
    "-rci": ["--result-content-indicator", 
            {"dest":"rci", 
            "choices": dmo.RCIs.keys(),
            "required": False,
            "default":"ac",
            "help":"Result content indicator. Default is attributes-and-children."}
    ],          
    "-li": ["--limit",
            {"metavar":"<int>", 
            "type":int,
            "dest":"limit", 
            "required": False,
            "default":100000000,
            "help":"Max. number objects to return."}
    ],             
    "-os": ["--offset",
            {"metavar":"<int>", 
            "type":int,
            "dest":"offset", 
            "required": False,
            "default":0,
            "help":"Offset for pagination retrievel."}
    ],             
    "-s": ["--select",
            {"metavar":"<select>", 
            "dest":"select", 
            "required": False,
            "help":"Comma separated list of elements to be selected."}
    ],             
    "-f": ["--format",
            {"dest":"format", 
            "choices": ["CSV", "JSON"], 
            "required": False,
            "help":"Output format for selected fields."}
    ],             
    "-sc": ["--separator-char",
            {"metavar":"<char>", 
            "dest":"sepchar", 
            "default":";",
            "required": False,
            "help":"Character to separate the fields in the select response. Default value is ;"}
    ],             
}        

# Definiere die Funktion für den benutzerdefinierten Typ
def dict_arg(s):
    try:
        return json.loads(s)
    except Exception as ex:
        raise argparse.ArgumentTypeError(f"{s} is not a valid JSON: {ex}")

def dict_file_arg(filepath):
    s:str = None
    try:
            f = open(filepath, "r")
            s =f.read()
            f.close()        
    except Exception as ex:
        raise argparse.ArgumentTypeError(f"Could not read file {filepath}: {ex}")

    try:
        return json.loads(s)
    except Exception as ex:
        raise argparse.ArgumentTypeError(f"{s} is not a valid JSON: {ex}")
#####################################################################################
class GetResourcesCLI(ApiConnCmdLineInterface):
    
    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Returns resources."
    
    def addCmdLineArgs(self, argsParser):
        
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-rn")
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-ri")        
        
        if not self.hasHideCmdArg("-rt"):        
            self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-rt", required=False)

        if not self.hasHideCmdArg("-rci"):    
            argsParser.add_argument("-rci", "--result-content-indicator", dest="rci",
                                    choices = dmo.RCIs.keys(),
                                    default="ac",
                                    help="Result content indicator. Default is attributes-and-children.")

        if not self.hasHideCmdArg("-li"):    
            argsParser.add_argument("-li", "--limit", metavar='<int>', type=int, dest="limit", default=1000000000,
                                help="Max. number objects to return.")

        if not self.hasHideCmdArg("-os"):    
            argsParser.add_argument("-os", "--offset", metavar='<int>', type=int, dest="offset", default=0,
                                help="Index of the first object to return.")


        argsParser.add_argument("-s", "--select", metavar='<select>', dest="select",
                               help="Comma separated list of elements to be selected.")

        argsParser.add_argument("-f", "--format",
                                dest="format",
                                choices = ["CSV", "JSON"], 
                                help="Output format for selected fields.")

        argsParser.add_argument("-sc", "--separator-char", metavar='<char>', dest="sepchar", 
                                default=";",
                                help="Character to separate the fields in the select response. Default value is ;")
                
    def main(self, cmdargs=None):

        obj = dmo.get_resources(self.apiConn, 
                                origin=cmdargs.origin or self.apiConn.origin,
                                resourceType=cmdargs.ty,
                                resourceName=cmdargs.rn,
                                resourceId=cmdargs.ri,
                                resultContentIndocator=cmdargs.rci, 
                                limit=cmdargs.limit, 
                                offset=cmdargs.offset,
                                select=cmdargs.select,
                                format=cmdargs.format)

        if not cmdargs.select or cmdargs.format == "JSON":
            print(json.dumps(obj, sort_keys=False, indent=4))
        else:
            for a in obj:
                line = cmdargs.sepchar.join(a)
                print("%s" % (line))

#####################################################################################
class AddResourceCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Adds an object of a specific resource type."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-rt", required=True)
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-rn", required=False)
        
        argsParser.add_argument("-b", "--body", metavar="<JSON>", type=dict_arg, dest="body", 
                                default=None, required=False, 
                                help="OneM2M JSON body of the resource object to create.")

        argsParser.add_argument("-bf", "--body-file", metavar="<file>", type=dict_file_arg, dest="file_body",
                                default=False, required=False, 
                                help="File with the OneM2M JSON body.")
        
    def main(self, cmdargs=None):
        body = {}

        if cmdargs.body:
            body = cmdargs.body
        elif cmdargs.file_body:
            body = cmdargs.file_body

        # If an application entity shall be created and no origin has been defined
        # Use the name of the application entity as the origin. 
        # If the default origin "d2ccli" it is not possible to create application  
        # entities
        if cmdargs.ty in ("ae", "application-entity") and not cmdargs.origin:
            cmdargs.origin = body.get("m2m:ae", {}).get("rn", None)
    
        obj = dmo.add_resource(self.apiConn,
                               origin=cmdargs.origin,
                               r_type=cmdargs.ty, 
                               r_name=cmdargs.rn,
                               onem2m_body=body,
                              )

        print(json.dumps(obj, sort_keys=False, indent=4))
                  
#####################################################################################
class UpdateResourceCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Updates a resource object."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-ri")  # --resource-id
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-rn")  # --resource-name
        #self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-lbl") # --labels

        argsParser.add_argument("-b", "--body", metavar="<JSON>", type=dict_arg, dest="body", 
                                default=None, required=False, 
                                help="OneM2M JSON body of the resource object to create.")

        argsParser.add_argument("-bf", "--body-file", metavar="<file>", type=dict_file_arg, dest="file_body",
                                default=False, required=False, 
                                help="File with the OneM2M JSON body.")
        
    def main(self, cmdargs=None):
        body = {}

        if cmdargs.body:
            body = cmdargs.body
        elif cmdargs.file_body:
            body = cmdargs.file_body
    
        obj = dmo.update_resource(self.apiConn,
                                  origin=cmdargs.origin,
                                  name=cmdargs.rn, 
                                  id=cmdargs.ri, 
                                  #labels=cmdargs.labels,
                                  onem2m_body=body,
                                 )

        print(json.dumps(obj, sort_keys=False, indent=4))
                                                   
#####################################################################################
class GetDeviceProvisioningRequestsCLI(ApiConnCmdLineInterface):
    
    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Returns the device provisioning requests."
    
    def addCmdLineArgs(self, argsParser):
        
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-rn")
        #self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-ri")
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-af")
        
        argsParser.add_argument("-s", "--select", metavar='<select>', dest="select",
                               help="Comma separated list of elements to be selected.")

        argsParser.add_argument("-f", "--format",
                                dest="format",
                                choices = ["CSV", "JSON"], 
                                help="Output format for selected fields.")

        argsParser.add_argument("-sc", "--separator-char", metavar='<char>', dest="sepchar", 
                                default=";",
                                help="Character to separate the fields in the select response. Default value is ;")
                
    def main(self, cmdargs=None):

        if cmdargs.attr_filters:
            af = utils.splitString(cmdargs.attr_filters, ",")
        else:
            af = None
            
        obj = device_provisioning.get_requests(self.apiConn, 
                                               origin=cmdargs.origin or self.apiConn.origin,
                                               name=cmdargs.rn,
                                               #id=cmdargs.ri,
                                               select=cmdargs.select,
                                               format=cmdargs.format,
                                               attribute_filters=af)

        if not cmdargs.select or cmdargs.format == "JSON":
            print(json.dumps(obj, sort_keys=False, indent=4))
        else:
            for a in obj:
                line = cmdargs.sepchar.join(a)
                print("%s" % (line))        
                
#####################################################################################
class GetDeviceProvisioningResponsesCLI(ApiConnCmdLineInterface):
    
    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Returns the device provisioning requests."
    
    def addCmdLineArgs(self, argsParser):
        
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-rn")
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-af")
        
        argsParser.add_argument("-s", "--select", metavar='<select>', dest="select",
                               help="Comma separated list of elements to be selected.")

        argsParser.add_argument("-f", "--format",
                                dest="format",
                                choices = ["CSV", "JSON"], 
                                help="Output format for selected fields.")

        argsParser.add_argument("-sc", "--separator-char", metavar='<char>', dest="sepchar", 
                                default=";",
                                help="Character to separate the fields in the select response. Default value is ;")
                
    def main(self, cmdargs=None):

        if cmdargs.attr_filters:
            af = utils.splitString(cmdargs.attr_filters, ",")
        else:
            af = None
            
        obj = device_provisioning.get_responses(self.apiConn, 
                                    origin=cmdargs.origin or self.apiConn.origin,
                                    name=cmdargs.rn,
                                    select=cmdargs.select,
                                    format=cmdargs.format,
                                    attribute_filters=af)

        if not cmdargs.select or cmdargs.format == "JSON":
            print(json.dumps(obj, sort_keys=False, indent=4))
        else:
            for a in obj:
                line = cmdargs.sepchar.join(a)
                print("%s" % (line))                     

class DeleteResourceCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Deletes a resource object."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-rn", required=False)
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-ri", required=False)
                
    def main(self, cmdargs=None):
        apiConn = self.apiConn
                
        if not cmdargs.rn and not cmdargs.ri:
            raise Exception(f"--resource-name or --resource-id option required to identify the object.")
        
        obj = dmo.delete_resource(apiConn, origin=cmdargs.origin, name=cmdargs.rn, id=cmdargs.ri)

        if obj:
            print(str(obj))

                                    
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
#####################################################################################
class oldUpdateResourceCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Updates an resource object."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-rt", required=False)
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-rn", "--resource-name")
                
    def main(self, cmdargs=None):
        '''
        Main entry point.
        '''
        apiConn = self.apiConn

        obj = dmo.updateResource(apiConn, 
                                 resourceType=cmdargs.ty, 
                                 resourceName=cmdargs.rn,
                                 labels=cmdargs.labels)

        print(json.dumps(obj, sort_keys=False, indent=4))                                

#####################################################################################
class oldAddMessageContainerCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Adds a message container to an resource object."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-rn", "--resource-name")

        argsParser.add_argument("-cn", "--container-name", metavar="<string>", dest="containerName",
                                required=True,
                                help="Name of the container within the resource object. E.g. uplinkMsg or downlinkMsg")
        
        argsParser.add_argument("-mms", "--max-message-size", metavar="<bytes>", dest="maxByteSize",
                                required=False, type=int, default=10000, 
                                help="Max. size of a message. The default is 10.000 bytes.")

        argsParser.add_argument("-mmn", "--max-message-num", metavar="<num>", dest="maxNrOfInstaces",
                                required=False, type=int, default=100, 
                                help="Max. number of stored messages. The default is 100.")

        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-lbl", "--labels")
                
    def main(self, cmdargs=None):
        '''
        Main entry point.
        '''
        apiConn = self.apiConn
            
        obj = dmo.addMessageContainer(apiConn, 
                                     resourceName=cmdargs.rn,
                                     containerName=cmdargs.containerName,
                                     maxByteSize=cmdargs.maxByteSize,
                                     maxNrOfInstaces=cmdargs.maxNrOfInstaces,
                                     labels=cmdargs.labels)

        print(json.dumps(obj, sort_keys=False, indent=4))                 
        
#####################################################################################
class oldAddSubscriptionCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Adds a subscription to an resource object."
    
    def addCmdLineArgs(self, argsParser):
        
        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-rn", "--resource-name")

        argsParser.add_argument("-sn", "--subscription-name", metavar="<string>", dest="subscriptionName",
                                required=True,
                                help="Name of the subscription  within the resource object.")
        
        argsParser.add_argument("-nu", "--notification-url", metavar="<url>", dest="notificationUrl",
                                required=True,
                                help="URL to which the notification shall be forwarded.")

        argsParser.add_argument("-nct", "--notification-content-type", dest="notificationContentType",
                                choices = dmo.NCTs.keys(), default="all",
                                help="Content type of the notification event. Defaule is all")

        argsParser.add_argument("-enc", "--event-notification-criteria", dest="eventNotificationCriteria",
                                choices=dmo.ENCs.keys(), default="update,delete,create-child,delete-child", 
                                metavar="[<string>,<string>,...]",
                                help=f"Comma separated list of event notification criterias. Default is u,d,cc,dc. Possible values are {dmo.ENCs.keys()}")

        self.addCmdLineArgsFromTemplate(cmdArgTemplates, argsParser, "-lbl", "--labels")
                
    def main(self, cmdargs=None):
        '''
        Main entry point.
        '''
        apiConn = self.apiConn

        encs = []
        if cmdargs.eventNotificationCriteria:
            for s in utils.splitString(cmdargs.eventNotificationCriteria,","):
                encs.append(s)

                            
        obj = dmo.addSubscription(apiConn, 
                                  resourceName=cmdargs.rn,
                                  subscriptionName=cmdargs.subscriptionName,
                                  notificationUrl=cmdargs.notificationUrl,
                                  notificationContentType=cmdargs.notificationContentType,
                                  eventNotificationCriterias=encs,
                                  pendingNotification="sendAllPending",
                                  labels=cmdargs.labels
                                  )
                    
        print(json.dumps(obj, sort_keys=False, indent=4))                 
        
