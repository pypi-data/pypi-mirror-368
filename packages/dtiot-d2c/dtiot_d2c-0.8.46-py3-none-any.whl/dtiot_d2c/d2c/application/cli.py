import json
import logging
from argparse import ArgumentParser

import dtiot_d2c.d2c as d2c
import dtiot_d2c.dmo as dmo
from dtiot_d2c.cli.cli_command import ApiConnCmdLineInterface
from dtiot_d2c.d2c import CMDARGS
from dtiot_d2c.d2c import utils as utils
from dtiot_d2c.d2c.application import Application
from dtiot_d2c.d2c.get_response import GetResponse
from dtiot_d2c.dmo import dmoCLI as dmocli

log = logging.getLogger(__name__)
          
#####################################################################################                
class AddC2cCliApplicationCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Creates the application for the d2c command line interface it-self."
    
    def addCmdLineArgs(self, argsParser):
        pass
                
    def main(self, cmdargs=None):
        response = Application.create(self.apiConn, 
                                      origin=self.apiConn.origin,
                                      name=self.apiConn.origin,
                                     )

        GetResponse(response=response).print()      
                    
#####################################################################################                
class AddApplicationCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Creates a new application."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n", required=True)
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-at")  # --application-type
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-de")  # --description
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-us")  # --urls
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-cp")  # --connection-properties
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-lbl")  # labels
                
    def main(self, cmdargs=None):
        response = Application.create(self.apiConn, 
                                      origin=cmdargs.origin if cmdargs.origin else cmdargs.name,
                                      name=cmdargs.name,
                                      urls=cmdargs.urls,
                                      application_type=cmdargs.application_type,
                                      description=cmdargs.description,
                                      connection_properties=cmdargs.connection_properties,
                                      labels=cmdargs.labels
                                      
                                     )
        GetResponse(response=response).print()        
        
#####################################################################################
class GetApplicationsCLI(ApiConnCmdLineInterface):
    
    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Returns the applications."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o") #, default=dmo.CLICFG.default_d2c_origin)
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n") # --name
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-i") # --id
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-li")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-os")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-rci")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-s")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-f")
        self.addCmdLineArgsFromTemplate(dmocli.cmdArgTemplates, argsParser, "-sc")
                
    def main(self, cmdargs=None):
        response = Application.get(self.apiConn,
                                   origin=cmdargs.origin,
                                   id=cmdargs.id,
                                   name=cmdargs.name,
                                   limit=cmdargs.limit,
                                   offset=cmdargs.offset,
                                   resultContentIndocator=cmdargs.rci, 
                                   select=cmdargs.select,
                                   format=cmdargs.format)

        GetResponse(response=response).print(cmdargs.sepchar)
            
#####################################################################################
class UpdateApplicationCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Updates an application."

    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o") 
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-i")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-de")  # --description
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-us")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-cp")  # --connection-properties
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-lbl")  # labels

                
    def main(self, cmdargs=None):
        response = Application.update(self.apiConn, 
                                      origin=cmdargs.origin or self.apiConn.origin,
                                      id=cmdargs.id,
                                      name=cmdargs.name,
                                      urls=cmdargs.urls,
                                      connection_properties=cmdargs.connection_properties,
                                      description=cmdargs.description,
                                      labels=cmdargs.labels
                                     )
        if not response:
            raise Exception(f"Application {cmdargs.name or cmdargs.id} does not exist")
                        
        GetResponse(response=response).print()   

#####################################################################################            
class DeleteApplicationCLI(ApiConnCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Deletes an application."
    
    def addCmdLineArgs(self, argsParser):
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-o")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-n")
        self.addCmdLineArgsFromTemplate(CMDARGS, argsParser, "-i")
                
    def main(self, cmdargs=None):
        obj = Application.delete(self.apiConn, 
                                 origin=cmdargs.origin, 
                                 name=cmdargs.name, 
                                 id=cmdargs.id
                                )

        if obj:
            print(str(obj))                                    
            
