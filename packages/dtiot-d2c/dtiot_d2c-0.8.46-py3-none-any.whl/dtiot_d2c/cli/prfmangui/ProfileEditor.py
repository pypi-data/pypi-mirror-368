
import json
import logging
from tkinter import *

log = logging.getLogger(__name__)

_LABEL_WIDTH = 12
_ENTRY_WIDTH = 60
_TEXT_WIDTH = 60
_FRAME_RELIEF = "flat"
_FRAME_BRDWIDTH = 1

def _createFrame(parent, relief=_FRAME_RELIEF, borderwidth=_FRAME_BRDWIDTH, padx=3, pady=3):
    return Frame(parent, relief=relief, padx=padx, pady=pady, borderwidth=borderwidth)

class InputEntry(Frame):
    def __init__(self, parent, 
                 labeltext, 
                 type="string", 
                 state=NORMAL, 
                 keyCallback=None):
        super().__init__(parent)

        self._type = type
        self._labeltext = labeltext

        if type == "string":
            self._var = StringVar()
        elif type == "int":
            self._var = IntVar()
        
        self._label = Label(self, text=labeltext, anchor="w", width=_LABEL_WIDTH)
        self._label.pack(side=LEFT)

        self._entry = Entry(self, textvariable=self._var, width=_ENTRY_WIDTH, state=state)
        self._entry.pack(side=LEFT, expand=True, fill=X)

        if keyCallback:
            self._entry.bind('<Key>', keyCallback)

        self.pack(side=TOP, expand=False, fill=X)

    @property
    def profileName(self):
        return self._profileName
    
    @property
    def type(self):
        return self._type
    
    @property
    def label(self):
        return self._labeltext
            
    def set(self, value):
        self._var.set(value)

    def get(self, inputRequired=False):
        return self._verify(inputRequired=inputRequired)
    
    def _verify(self, inputRequired=False):
        if self._type == "int":
            try:
                v = self._var.get()
                return v
            except Exception as ex:
                raise Exception("Invalid number for %s." % (self._labeltext))
        else:
            v = str(self._var.get()).strip()
            if inputRequired and not v or len(v) == 0:
                raise Exception("Input required for %s." % (self._labeltext))
            return v

class ProfileEditor(Frame):

    def __init__(self, parent, 
                 profileManager=None):
        super().__init__(parent)

        self._profileManager = profileManager
        self._cfg = None
        self._dirty = False
        self._new = True
        self._errorMsg = None
        self._profile = None

        inputFrame = _createFrame(self)
        
        self._statusVar = StringVar()
        self._statusLabel = self._buildStatusLabel(inputFrame, self._statusVar)
        self._updateStatusLabel()

        # Generate the input elements ...
        self._fileInput = InputEntry(inputFrame, "File", keyCallback=self.keyInputCallback, state=DISABLED)
        self._inputs = {}
        for c in self._profileManager.getProfileCfg()["elements"]:
            if c["type"] in ("string", "int"):
                i = InputEntry(inputFrame, c["label"], type=c["type"], state=c["state"], keyCallback=self.keyInputCallback)
            elif c["type"] == "text":
                i = self._buildInputText(inputFrame, "Application URL")                
            else:
                log.error(f'Unknown type {c["type"]} of profile element.')

            self._inputs[c["name"]] = i

        inputFrame.pack(side=TOP, expand=True, fill=BOTH)

        self._saveButton = None
        frame = self._buildCommandsFrame(self)
        frame.pack(side=BOTTOM, expand=False, fill=X)
    
    def _buildStatusLabel(self, parent, var):
        frame = _createFrame(parent, relief=GROOVE, borderwidth=2, padx=3, pady=1)
        label = Label(frame, textvariable=var, anchor="w")
        label.pack(side=TOP, expand=False, fill=X)
        frame.pack(side=TOP, expand=False, fill=X)
        return label

    def _buildInputText(self, parent, inputLabel):
        frame = _createFrame(parent)

        label = Label(frame, text=inputLabel, anchor="nw", width=_LABEL_WIDTH)
        label.pack(side=LEFT, expand=False, fill=Y)
        
        f = Frame(frame)
        f.pack(side=LEFT, expand=True, fill=BOTH)

        text = Text(f, height=10, width=_TEXT_WIDTH)
        text.pack(side=LEFT, expand=True, fill=BOTH)
        text.bind('<Key>', self.keyInputCallback)

        scrollV = Scrollbar(f)
        scrollV.pack(side = RIGHT, fill = Y)
        scrollV.config(command=text.yview)
        text.config(yscrollcommand=scrollV.set)

        frame.pack(side=TOP, expand=True, fill=BOTH)

        return text

    def _buildCommandsFrame(self, parent):
        frame = _createFrame(parent)
        self._saveButton = Button(frame, text="SAVE", command=self._saveProfile)
        self._saveButton.pack(side=RIGHT, padx = 10, pady = 10)
        return frame
            
    def _setErrorMsg(self, msg):
        self._errorMsg = msg

    def _updateStatusLabel(self):
        fg = "darkgrey"
        s = None
        color = None

        if self._errorMsg:
            s = "error: %s" % (self._errorMsg)
            fg = "red"
        else:
            if self._new:
                s = "new"
            else:
                s = "loaded"

            if self._dirty:
                s = "%s | changed" % (s)
            else:
                s = "%s | unchanged" % (s)

        self._statusVar.set(s)
        self._statusLabel.configure(fg=fg)

        # Clean error message
        self._setErrorMsg(None)

    def _setDirty(self, dirtyFlag):
        self._dirty = dirtyFlag
        self._updateStatusLabel()

    def keyInputCallback(self, event):
        self._setDirty(True)

    def _saveProfile(self):
        if not self._profile:
            return
        
        try: 
            for (k, i) in self._inputs.items():
                if type(i) == InputEntry:
                    self._profile.setElement(k, i.get(inputRequired=True), type=i.type)
                elif type(i) == Text:
                    d = json.loads(i.get(1.0, END).strip())
                    self._profile.setElement(k, d)
        except Exception as ex:    
            self._setErrorMsg(str(ex))
            self._updateStatusLabel()
            return

        try:
            self._profileManager.saveProfile(self._profile)
            self._new = False
            self._setDirty(False)

        except Exception as ex:
            self._setErrorMsg(str(ex))
            self._updateStatusLabel()
            return            

    def setProfile(self, profile):
        self._profile = profile
        self._fileInput.set("")

        # Cleanup
        for (k, i) in self._inputs.items():
            if type(i) == InputEntry:
                if i.type == "int":
                    i.set(0)
                elif i.type == "float":
                    i.set(0.0)
                else:
                    i.set("")
            elif type(i) == Text:
                i.delete(1.0, END)                
 
        self._new = True
        self._setDirty(False)

        if not profile:
            self._updateStatusLabel()
            return

        # Set the values from input profiile
        self._fileInput.set(profile.getFile())
         
        for (k, i) in self._inputs.items():
            if type(i) == InputEntry:
                if i.type == "int":
                    i.set(int(profile.getElement(k, 0)))
                elif i.type == "float":
                    i.set(float(profile.getElement(k, 0.0)))
                else:
                    i.set(profile.getElement(k, ""))
            elif type(i) == Text:
                d = profile.getElement(k, {})
                if d:
                    s = json.dumps(d, indent=4)
                else:
                    s = ""
                i.insert(1.0, s)

        self._new = False if profile.getFile() else True

        self._updateStatusLabel()


