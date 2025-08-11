import json
import logging

import dtiot_d2c.cli.CFG as CFG
import dtiot_d2c.cli.profile_webapp as profile_webapp
import dtiot_d2c.cli.utils as utils
from dtiot_d2c.cli.cli_command import (CmdLineInterface,
                                       ConfigCmdLineInterface,
                                       ProfileCmdLineInterface)
from dtiot_d2c.cli.config import Configuration
from dtiot_d2c.cli.profile import Profile, Profiles

log = logging.getLogger(__name__)
#----------------------------------------------------------------
def _editProfile(config, profiles, profile:Profile, isNew=True):

    if isNew:
        prompt = "add profile - "
    else:
        prompt = "modify profile - "

    for e in CFG.PROFILE_CONFIG["elements"]:
        #log.debug(f"e: {e}")
        if (n := e.get("name", None)):
            dv = profile.getElement(n)
        else:
            dv = str(e["default"])
            
        v = utils.getUserInput(prompt=prompt, title=e["label"], defaultValue=dv, requiresInput=True)
        profile.setElement(e["name"], v, e["type"])

    # Build the filename for the profile and verify if it exists
    if isNew:
        fname = profile.buildFilename(CFG.PROFILE_CONFIG)        

        if profiles.getProfile(fname):
            print("error: Profile file %s NOT unique. Choose a different combination of account and project." % (file))
            return          

        profile.setFile(fname)

    profile.write(directory=config.getProfilesDirectory(), file=profile.getFile())

#################################################################
# ListProfiles
#################################################################

class ListProfilesCLI(ConfigCmdLineInterface):
    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Lists the profiles in the configuration."
    
    def addCmdLineArgs(self, argsParser):

        argsParser.add_argument("-s", "--select", metavar='<select>', 
                                help="Comma separated list of elements to be selected.")

        argsParser.add_argument("-f", "--filter", metavar='<filter>', dest="filter",
                                help="Filters the  profiles by its filename with the pattern \"*<filter>*\".")

        argsParser.add_argument("--separator-char", metavar='<char>', dest="sepchar", default=";",
                                help="Character to separate the fields in the select response. Default value is ;")        

    def main(self, cmdargs=None):
        log.debug("=> ListProfilesCLI()")

        profiles = Profiles(config=self.getConfig())

        d = {}

        #  If a filter is defined.
        if cmdargs.filter and len(cmdargs.filter) > 0:
            for key in profiles.getProfileKeys():
                profile = profiles.getProfile(key)
                if profile.getFile().lower().find(cmdargs.filter) > -1:
                    d[key] =  profile.getAsDict()
                    d[key]["file"] = key # The file is used as a key in the profiles dictionary
        else:
            for key in profiles.getProfileKeys(): 
                d[key] = profiles.getProfile(key).getAsDict() 
                d[key]["file"] = key # The file is used as a key in the profiles dictionary

        if not cmdargs.select:            
            print(json.dumps(d, indent=4))
        else:
            select_fields = utils.splitString(cmdargs.select, ",")
            for (k, prf) in d.items():
                a = []
                for sf in select_fields:
                    v = prf.get(sf, None)
                    a.append(str(v))
                line = cmdargs.sepchar.join(a)
                print("%s" % (line))

#################################################################
# PrintProfile
#################################################################

class PrintProfileCLI(ConfigCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Prints a profile of the configuration."
    
    def addCmdLineArgs(self, argsParser):

        argsParser.add_argument("-f", "--file", metavar='<file>', required=True,
                                help="Filename of the profile to be printed.")

        argsParser.add_argument("-s", "--select", metavar='<select>', 
                                help="Comma separated list of elements to be selected.")

        argsParser.add_argument("--separator-char", metavar='<char>', dest="sepchar", default=";",
                                help="Character to separate the fields in the select response. Default value is ;")        

    #def main(self, cmdargs=None, file=None, select=None, sepChar=None, config=None):
    def main(self, cmdargs=None, profile=None, select=None, sepChar=None):
        log.debug("=> PrintProfileCLI()")

        if not profile:
            profiles = Profiles(config=self.getConfig())
            file = cmdargs.file
            profile = profiles.getProfile(file)
    
            if not profile:
                raise Exception("Profile %s not available." % (file))

        if not select and cmdargs:
            select = cmdargs.select

        if not sepChar and cmdargs:
            sepChar = cmdargs.sepchar
        if not sepChar:
            sepChar = ";"

        d = profile.getAsDict()
        d["file"] = profile.getFile()

        if not select:        
            print(json.dumps(d, sort_keys=False, indent=4))

        else:
            a = []
            for s in utils.splitString(select, ","):
                if s in d.keys():
                    a.append(str(d[s]))
            line = sepChar.join(a)
            print("%s" % (line))

#################################################################
# NewProfile
#################################################################

class NewProfileCLI(ConfigCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Creates a new profile by collecting required infos from user input."
    
    def addCmdLineArgs(self, argsParser):

        argsParser.add_argument("--copy-from-profile", metavar='<profile name>', 
                                dest="copy_from_profile",
                                help="filiename of the profile which values shall be used to initialize the new profile.")

    def main(self, cmdargs=None, config=None):
        log.debug("=> NewProfileCLI()")
    
        if not config:
            config = self.getConfig()


        profiles = Profiles(config=config)

        # Create an empty profile
        profile = Profile(profileCfg=CFG.PROFILE_CONFIG)
        
        if cmdargs and cmdargs.copy_from_profile:
            #log.debug(f"cmdargs.copy_from_profile: {cmdargs.copy_from_profile}")
            cpFromPrf = profiles.getProfile(cmdargs.copy_from_profile)
            if not cpFromPrf:
               raise Exception("Copy from profile %s does not exist!" % (cmdargs.copy_from_profile))
            profile.copyFrom(cpFromPrf)
            #log.debug(f"profile: {profile}")

        _editProfile(config, profiles, profile, isNew=True)

        return profile

#################################################################
# EditProfile
#################################################################
class EditProfileCLI(ConfigCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Modifies profile by collecting user input from console."
    
    def addCmdLineArgs(self, argsParser):
        argsParser.add_argument("-f", "--file", metavar='<file>', required=True,
                                help="Filename of the profile which shall be modified.")

    #def main(self, cmdargs=None, configFilePath=None, file=None):
    def main(self, cmdargs=None):
        log.debug("=> EditProfileCLI()")

        config = self.getConfig()
        profiles = Profiles(config=config)
        profile = profiles.getProfile(cmdargs.file)

        if not profile:
            raise Exception("Profile %s does not exist!" % (cmdargs.file))

        _editProfile(config, profiles, profile, isNew=False)

#################################################################
# Activate Profile
#################################################################
class ActivateProfileCLI(ConfigCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Acticates a profile to be used as default."
    
    def addCmdLineArgs(self, argsParser):

        argsParser.add_argument("-f", "--file", metavar='<file>', required=True,
                                help="Filename of the profile to activate.")

    def main(self, cmdargs=None, config=None, profile=None):
        log.debug("=> ActivateProfileCLI()")

        if not config:
            config = self.getConfig()

        if not profile:            
            profiles = Profiles(config=config)
            profile = profiles.getProfile(cmdargs.file)

            if not profile:
                raise Exception("Profile %s does not exist!" % (cmdargs.file))

        config.setActiveProfileFile(profile.getFile())
        config.write()

#################################################################
# Print Activated Profile
#################################################################
class PrintActivatedProfileCLI(ProfileCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Prints the current activated profile."
    
    def addCmdLineArgs(self, argsParser):
        argsParser.add_argument("-s", "--select", metavar='<select>', 
                                help="Comma separated list of elements to be selected.")

        argsParser.add_argument("--separator-char", metavar='<char>', dest="sepchar", default=";",
                                help="Character to separate the fields in the select response. Default value is ;")        

    def main(self, cmdargs=None):
        log.debug("=> PrintActivatedProfileCLI()")

        profile = self.getProfile()

        if not profile:
            raise Exception("No profile activated")

        # Get the activate profile name and print it.
        PrintProfileCLI().main(profile=profile,
                               select=cmdargs.select, 
                               sepChar=cmdargs.sepchar)

#################################################################
# Start Profile Manager Gui
#################################################################
class StartProfileManagerGuiCLI(ConfigCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Starts the profile manager gui."
    
    def addCmdLineArgs(self, argsParser):
        pass
                
    def main(self, cmdargs=None):
        from dtiot_d2c.cli.prfmangui.ProfileManagerGui import ProfileManagerGui
        prfManGui = ProfileManagerGui(self.getConfig())
        prfManGui.run()

#################################################################
# Start Profile Manager application in a WebBrowser
#################################################################
class StartProfileManagerWebBrowserCLI(ConfigCmdLineInterface):

    def __init__(self):
        super().__init__()

    def get1LineHelp(self):
        return "Starts the profile manager application in a web browser."
    
    def addCmdLineArgs(self, argsParser):
        argsParser.add_argument("-u", "--url", metavar='<url>', default="http://127.0.01:3000/login",
                                help="URL on which the profile manager web application can be accessed.")

    def main(self, cmdargs=None):

        profile_webapp.open_in_browser(webapp_url=cmdargs.url)

        #from dtiot_d2c.cli.prfmangui.ProfileManagerGui import ProfileManagerGui
        #prfManGui = ProfileManagerGui(self.getConfig())
        #prfManGui.run()
