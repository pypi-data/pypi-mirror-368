#####################################################################
# Copyright (c) 2020 Telekom Deutchland IoT GmbH                    #
# All rights reserved                                               #
#                                                                   #
# Licensed under the MIT license. See LICENSE file in the project   # 
# root for full license information.                                #
#####################################################################

import glob
import importlib
import logging
import os
import os.path
from tkinter import *

import dtiot_d2c.cli.CFG as CFG

log = logging.getLogger(__name__)

class ProfileSelector(Frame):

    def __init__(self, parent, profiles, controller, selectionChangedCallback):
        super().__init__(parent)

        self._profiles = profiles
        self._controller = controller
        
        self._config = None
        self._shownProfiles = None

        self._selectionChangedCallback = selectionChangedCallback
        
        self._selectedProfile = None
        self._selectedProfileVar = None
        self._profileList = None
        self._filterVar = None

        # Build the top area which displays current selected configuration and
        # contains the filter input
        frame = Frame(self)

        self._buildCurrentlySelectedLabel(frame, row=0)
        self._buildFilterInput(frame, row=1)
        
        frame.columnconfigure(1, weight=1)
        frame.pack(side=TOP, expand=False, fill=X)  

        # List of selectable access configurations
        frame = self._buildList(self)
        frame.pack(side=TOP, expand=True, fill=BOTH)

        self._filterVar.trace("w", self._filterProfiles)

        # Show the profiles in the list
        self.updateProfilesList()

    def _buildCurrentlySelectedLabel(self, parent, row):
        
        label = Label(parent, text = "Active:")
        label.grid(row=row, column=0, padx='5', pady='5', sticky='ew')
        
        self._selectedProfileVar = StringVar()
        label = Label(parent, text = "", justify=LEFT, textvariable=self._selectedProfileVar, bg="red", fg="white")
        label.grid(row=row, column=1, padx='5', pady='5', sticky='ew')

    def _buildFilterInput(self, parent, row):
        
        label = Label(parent, text = "Filter:")
        label.grid(row=row, column=0, padx='5', pady='5', sticky='ew')
        
        self._filterVar = StringVar()
        entry = Entry(parent, justify=LEFT, textvariable=self._filterVar)
        entry.grid(row=row, column=1, padx='5', pady='5', sticky='ew')

    def _buildList(self, parent):
        frame = Frame(parent)

        listbox = Listbox(frame, justify=LEFT, width=60, height=30)
        listbox.pack(side=LEFT, expand=True, fill=BOTH)
        self._profileList = listbox

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side = RIGHT, fill = BOTH)

        listbox.bind('<<ListboxSelect>>', self.onSelect)        
        listbox.bind('<Double-Button-1>', self.onDoubleClick)

        listbox.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = listbox.yview)

        return frame

    def updateProfilesList(self, filter=None, select=None):
        self._profileList.delete(0, END)
        self._shownProfiles = []

        if filter:
            filter = filter.lower()

        if select:
            selectFile = select.getFile()
        else:
            selectFile = None

        idx = 0

        for profile in self._profiles.getProfiles(sorted=os.truncate):
            file = profile.getFile()

            if not file:
                log.warn("File of profile not defined.")
                continue

            # Cut off leading directory
            label = os.path.basename(file)

            # Cut off the ".profile" file extension
            idx = label.find(".%s" % (CFG.PROFILE_FILE_EXT))
            if idx > -1:
                label = label[0:idx]

            if filter and len(filter) > 0:
                if label.lower().find(filter) == -1:
                    continue

            self._profileList.insert("end", label)
            self._shownProfiles.append(profile)
            
            if selectFile and file == selectFile:
                self._profileList.select_set(idx)

            idx = idx + 1

    def _filterProfiles(self, *args):
        filter = self._filterVar.get()
        filter = filter.strip() if filter else None

        self.updateProfilesList(filter)
       
    def onSelect(self, evt):
        log.info("=> onSelect()")
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
       
        self._selectionChangedCallback(self._shownProfiles[index])

    def showActivatedProfile(self, profile):
        if profile:
            file = os.path.basename(profile.getFile())
            idx = file.find(".%s" % (CFG.PROFILE_FILE_EXT))
            if idx > -1:
                file = file[:idx]
            self._selectedProfileVar.set(file)
        else:
            self._selectedProfileVar.set("")

    def onDoubleClick(self, evt):
        pass
        '''
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        cmd = "gnome-terminal"
        log.debug("Exec %s" % (cmd))
        os.system(cmd)
        '''

    '''
    def setConfig(self, config):
        self._config = config
        self.updateProfilesList()
    '''
