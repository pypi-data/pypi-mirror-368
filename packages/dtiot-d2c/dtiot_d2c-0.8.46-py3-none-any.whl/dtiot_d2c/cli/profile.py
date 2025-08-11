
import os
import os.path
import logging
import json
import dtiot_d2c.cli.utils as utils
import dtiot_d2c.cli.CFG as CFG

log = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
class Profile:
    def __init__(self, 
                 file=None, 
                 account=None, project=None, 
                 apiHost="api.scs.iot.telekom.com", apiPort=443, 
                 apiUsername=None, apiPassword=None, apiTenant=None, 
                 applicationUrl=None,
                 copyFromProfile=None,
                 profileCfg=None):

        self._file = file
        self._profileDict:dict = {}

        if self._file:
            self.read()
        elif copyFromProfile:
            self.copyFrom(copyFromProfile)
        elif profileCfg:
            for c in profileCfg["elements"]:
                self._profileDict[c["name"]] = c["default"]

    def copyFrom(self, other):
        self._profileDict = other._profileDict

    def __str__(self):
        return json.dumps(self._profileDict)

    def getAsDict(self):
        return self._profileDict

    def set(self, profileDict):
        self._profileDict = profileDict

    def getFile(self):
        return self._file
    def setFile(self, file):
        self._file = file

    def getElement(self, name, default=None):
        return self._profileDict.get(name, default)
    def setElement(self, name, value, type="string"):
        if type == "int":
            self._profileDict[name] = int(value)
        elif type == "float":
            self._profileDict[name] = float(value)
        else:            
            self._profileDict[name] = value

    def getBaseFilename(self):
        if self._file:
            return os.path.basename(self._file)
        else:
            return "%s_%s.%s" % (self._account, self._project, CFG.PROFILE_FILE_EXT)

    def buildFilename(self, profileCfg:dict)->str:
        '''
        Builds the filename according to the passed profile configuration.
        '''
        fname = ""
        for e in profileCfg["filenameElements"]:
            fname += self._profileDict.get(e, e)
        return fname
    
    def read(self, file=None):
        if not file and self._file:
            file = self._file

        if not os.path.exists(file):
            raise Exception("Profile file %s does not exist." % (file))

        log.debug("Reading profile file %s" % (file))

        # Read the profile from file
        d = utils.readJsonFile(file)

        for (k, v) in d.items():
            self._profileDict[k] = v

        self._file = file

    def write(self, directory=None, file=None):
        if not file:
            file = self._file
        else:
            if directory:
                file = os.path.join(directory, file)
            else:
                raise Exception("Cannot write profile %s. Directory required." % (file))

        utils.writeJsonFile(self._profileDict, file)

        self._file = file
        
#-------------------------------------------------------------------------------
class Profiles:
    def __init__(self, directory=None, config=None, autoLoad=True):

        if config and not directory:
            directory = config.getProfilesDirectory()

        self._directory = directory
        self._profiles = []

        if autoLoad:
            self.loadProfiles(directory)

    def loadProfiles(self, directory=None):
        if not directory:
            directory = self._directory

        if not directory:
            log.warn("Profiles directory is None")
            return None
        elif not os.path.exists(directory):
            raise Exception("Profiles directory %s does not exist." % (directory))            

        profiles = {}
        for file in utils.getFilesInDir(directory):
            if file.endswith(CFG.PROFILE_FILE_EXT):
                try:
                    profile = Profile(file=os.path.join(directory, file))
                    profiles[file] = profile
                except Exception as ex:
                    log.error("Could not load profile %s: %s" % (file, str(ex)))

        self._directory = directory
        self._profiles = profiles

    def getProfileKeys(self):
        return self._profiles.keys()

    def getProfiles(self, sorted=False):
        a = []
        for k in self._profiles.keys():
            a.append(self._profiles[k])

        if sorted:
            def getProfiles_getBaseFilename(profile):
                return profile.getBaseFilename()
            a.sort(key=getProfiles_getBaseFilename)

        return a

    def addProfile(self, profile):
        file = profile.getFile()

        if not file:
            raise Exception("Profile cannot be added. It has no file.")
        
        self._profiles[file] = profile

    def getProfile(self, file):
        return self._profiles.get(file)

