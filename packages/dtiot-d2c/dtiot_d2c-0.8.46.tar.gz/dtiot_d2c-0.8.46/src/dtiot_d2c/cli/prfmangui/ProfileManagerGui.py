import glob
import importlib
import json
import logging
import os
import os.path
from tkinter import *
from tkinter import messagebox

import dtiot_d2c.cli.CFG as CFG
from dtiot_d2c.cli.profile import Profile

log = logging.getLogger(__name__)


from .ProfileEditor import ProfileEditor
from .ProfileSelector import ProfileSelector


class ProfileManagerGui():
    def __init__(self,  config):
        self._config = config
        self._profiles = config.getProfiles()
        self._selectedProfile = None
        self._activatedProfile = None
        self._newProfile = None

        rootWnd = Tk()
        rootWnd.title("NICLI Profile Manager")
        self._rootWnd = rootWnd

        # Build the left side of the window with the profile selector
        leftFrame = Frame(rootWnd)
        
        
        self._prfSelector = ProfileSelector(parent=leftFrame,
                                            profiles=self._profiles,
                                            controller=self,
                                            selectionChangedCallback=self.profileHasBeenSelectedCallBack)

        frame = self._buildCommandsFrame(leftFrame)
        self._prfSelector.pack(side=TOP, expand=TRUE, fill=BOTH, padx=0, pady=0)
        frame.pack(side=BOTTOM, expand=False, fill=X, padx=0, pady=0)  
    
        # Create right side of window with the profile editor
        self._prfEditor = ProfileEditor(parent=rootWnd, profileManager=self)

        # Pack the left and the right side of the window
        leftFrame.pack(side=LEFT, expand=False, fill=BOTH, padx=10, pady=10)
        self._prfEditor.pack(side=LEFT, expand=True, fill=BOTH, padx=10, pady=10)

    def getProfileCfg(self)->dict:
        return CFG.PROFILE_CONFIG
        
    def _buildCommandsFrame(self, parent):
        frame = Frame(parent)

        button = Button(frame, text="ACTIVATE", command=self.activateProfile, state="disabled", width=12)
        button.pack(side=RIGHT, expand=True, padx = 10, pady = 10)
        self._activateButton = button

        button = Button(frame, text="NEW", command=self.newProfile, state="normal", width=12)
        button.pack(side=RIGHT, expand=True, padx = 10, pady = 10)
        self._newButton = button

        button = Button(frame, text="COPY", command=self.copyProfile, state="disabled", width=12)
        button.pack(side=RIGHT, expand=True, padx = 10, pady = 10)
        self._copyButton = button

        button = Button(frame, text="DELETE", command=self.deleteProfile, state="disabled", width=12)
        button.pack(side=RIGHT, expand=True, padx = 10, pady = 10)
        self._deleteButton = button

        return frame

    def activateProfile(self, profile=None):
        if not profile:
            profile = self._selectedProfile

        file = profile.getFile()

        self._config.setActiveProfileFile(file)
        self._config.write()
        
        self._prfSelector.showActivatedProfile(profile)
        self._activateProfile = profile

    def copyProfile(self):
        if self._selectedProfile:
            self.newProfile(copyProfile=self._selectedProfile)
        else:
            self.newProfile()

    def newProfile(self, copyProfile=None):
        profile = Profile(profileCfg=self.getProfileCfg())
        self._prfEditor.setProfile(profile)
        self._newProfile = profile

    def deleteProfile(self):
        if not self._selectedProfile:
            return
        
        name = self._selectedProfile.getBaseFilename()

        rv = messagebox.askokcancel(
                title="Delete Profile", 
                message="Do you really want to delete profile %s?" % (name),
                icon=messagebox.QUESTION)
        
        if not rv:
            return

        file = self._selectedProfile.getFile()
        if not os.path.exists(file):
            raise Exception("Cannot delete profile. File %s does not exist." % (file))
        else:
            os.remove(file)

        self._selectedProfile = None
        self._profiles.loadProfiles()
        self._prfEditor.setProfile(None)
        self._prfSelector.updateProfilesList()

    def _updateButtonsState(self):
        if self._selectedProfile:
            state = NORMAL
        else:
            state = DISABLED

        for b in [self._activateButton, self._copyButton, self._deleteButton]:
            b.configure(state=state)

    def profileHasBeenSelectedCallBack(self, profile):
        log.info("=> profileHasBeenSelectedCallBack(profile=%s)" % (str(profile)))
        self._prfEditor.setProfile(profile)
        self._selectedProfile = profile

        self._updateButtonsState()

    def saveProfile(self, profile):
        log.info("=> saveProfile() ...")
        log.info(json.dumps(json.loads(str(profile)),indent=4))

        file = profile.getFile()

        if file and len(file.strip()) > 0:
            profile.write()

        else:
            # Build the filename of the profile
            fname = ""
            for e in self.getProfileCfg()["filenameElements"]:
               fname += profile._profileDict.get(e, e)
            dir = self._config.getProfilesDirectory()

            if os.path.exists(os.path.join(dir, fname)):
                raise Exception("A profile with the same account and project already exist. Choose a different ones!")

            profile.write(directory=dir, file=fname)
            self._profiles.addProfile(profile)
            self._prfEditor.setProfile(profile)
            self._prfSelector.updateProfilesList(select=profile)

    def run(self):
        self._rootWnd.mainloop()
