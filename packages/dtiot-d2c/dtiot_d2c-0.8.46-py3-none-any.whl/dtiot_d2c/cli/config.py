
from io import DEFAULT_BUFFER_SIZE
import sys
import os
import os.path
import logging
import json
from pathlib import Path

import dtiot_d2c.cli.utils as utils
import dtiot_d2c.cli.CFG as CFG
from dtiot_d2c.cli.profile import Profiles

log = logging.getLogger(__name__)

class Configuration():

    def __init__(self, configFile=None, configDir=None, autoRead=True):
        self._file = None
        self._activeProfileFile = None
        self._profilesDirectory = None
        self._profiles = None

        if autoRead:
            self.read(configFile=configFile, configDir=configDir)
    
    def __str__(self):
        return json.dumps(self.getAsDict())
    
    def getAsDict(self):
        return {
            CFG.CEN_ACTIVE_PROFILE_FILE : self._activeProfileFile,
            CFG.CEN_PROFILE_DIR : self._profilesDirectory
        }

    def set(self, activeProfileFile=None, profilesDirectory=None):
        self._activeProfileFile = activeProfileFile
        self._profilesDirectory = profilesDirectory

    def getFile(self):
        return self._file

    def getActiveProfileFile(self):
        return os.path.basename(self._activeProfileFile)
        #return os.path.expandvars(s.replace("~", str(Path.home()))) if s else None
    def setActiveProfileFile(self, file):
        self._activeProfileFile = os.path.basename(file) if file else None
        #self._activeProfileFile = os.path.expandvars(file.replace("~", str(Path.home())))

    def getProfilesDirectory(self):
        s = self._profilesDirectory
        return os.path.expandvars(s.replace("~", str(Path.home()))) if s else None
    def setProfilesDirectory(self, directory):
        self._profilesDirectory = os.path.expandvars(directory.replace("~", str(Path.home())))

    def getProfiles(self):
        if not self._profiles:
            self._profiles = Profiles(config=self)

        return self._profiles
        
    def read(self, configFile=None, configDir=None):
        # get path of the configuration file
        cfgFile = Configuration.getPathToConfigFile(configFile=configFile, configDir=configDir)

        if not os.path.exists(cfgFile):
            raise Exception("Config file %s does not exist." % (cfgFile))

        log.debug("Reading config file %s" % (str(cfgFile)))

        # Read the configuration from the config file
        d = utils.readJsonFile(cfgFile)

        self.set(activeProfileFile=d[CFG.CEN_ACTIVE_PROFILE_FILE],
                 profilesDirectory=d[CFG.CEN_PROFILE_DIR])

        self._file = cfgFile

    def write(self, file=None, backup=False):
        if not file:
            file = self._file

        if backup:
            utils.backupFile(file)

        utils.writeJsonFile(self.getAsDict(), file)

        self._file = file

    ####################
    # Static methods
    ####################

    def getPathToConfigFile(configFile=None, configDir=None):
        '''
        if   config-file parameter is defined: use it
        elif config-dir  parameter is defined: use <config-dir>/config.json
        elif config-file envvar is defined:    use it
        elif config-dir  parameter is defined: use <config-dir>/config.json
        else                                   use ~/.ni/config.json
        '''
        if configFile:
            log.debug("Using config file from input parameters: %s" % (configFile))
            configFile = os.path.expandvars(configFile.replace("~", str(Path.home())))
        elif configDir:
            log.debug("Using config directory from input parameters: %s" % (configDir))
            configDir = os.path.expandvars(configDir.replace("~", str(Path.home())))
            configFile = "%s/%s" % (configDir, CFG.DEFAULT_CFGFILE_NAME)

        elif CFG.ENVVARNAME_CFGFILE in os.environ.keys():
            s = os.environ[CFG.ENVVARNAME_CFGFILE]
            log.debug("Using config file from environment: %s" % (s))
            configFile = os.path.expandvars(s.replace("~", str(Path.home())))

        elif CFG.ENVVARNAME_CFGDIR in os.environ.keys():
            s = os.environ[CFG.ENVVARNAME_CFGDIR]
            log.debug("Using config directory from environment: %s" % (s))
            configDir = os.path.expandvars(s.replace("~", str(Path.home())))
            configFile = "%s/%s" % (configDir, CFG.DEFAULT_CFGFILE_NAME)
        else:
            s = "~/%s/%s" % (CFG.DEFAULT_CFGDIR_NAME, CFG.DEFAULT_CFGFILE_NAME)
            log.debug("Using defaults for both config directory and config file name: %s" % (s))
            configFile = os.path.expandvars(s.replace("~", str(Path.home())))

        log.debug("configFile: %s" % (configFile))
        return configFile

    def create(configDir=None, overwrite=False):
        log.debug("=> Configuration.createConfiguration()")

        cfgFile = Configuration.getPathToConfigFile(configDir=configDir)

        log.debug("Creating confg file %s ..." % (cfgFile))

        if os.path.exists(cfgFile) and not overwrite:
            raise Exception("Configuration file %s already exists. User overwrite flag to overwrite the file." % (
                               cfgFile))
        
        # Create config directory if it does not exist
        cfgDirPath = os.path.dirname(cfgFile)
        if not os.path.exists(cfgDirPath):
            os.makedirs(cfgDirPath)


        config = Configuration(autoRead=False)
        config.setActiveProfileFile(None)
        config.setProfilesDirectory(os.path.join(cfgDirPath, CFG.DEFAULT_PROFILES_DIRNAME))
        config.write(cfgFile)

        # Create the profiles directory within the config directory and copy
        # the default files into it.

        profilesDirPath = "%s/%s" % (cfgDirPath, CFG.DEFAULT_PROFILES_DIRNAME)
        if not os.path.exists(profilesDirPath):
            os.makedirs(profilesDirPath)

        # fromDir = os.path.join(os.path.dirname(__file__), CFG.DEFAULT_PROFILES_DIRNAME)
        # for fromFile in utils.getFilesInDir(fromDir):
        #     fromFile = os.path.join(fromDir, fromFile)
        #     toFile = "%s/%s" % (profilesDirPath, os.path.basename(fromFile))
        #     log.debug("Copy file from %s to %s" % (fromFile,toFile))
        #     utils.copyFile(fromFile, toFile)

        return Configuration(configFile=cfgFile, autoRead=True)
