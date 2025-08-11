from enum import Enum

#OneM2m Dateformat
ONEM2M_DATE_FORMAT = "%Y%m%dT%H%M%S"

# DMO basepath
DMO_BASEPATH="api-gw/device-management-orchestrator"

# OneM2M resource type ids
TYs = {
    'acp':1,             
    'ae':2,                     # AE
    'application-entity':2,
    'cnt':3,                    # CONTAINER
    'container':3,
    'cin':4,                    # CONTENT INSTANCE
    'content-instance':4,
    'cb':5,                     # CSEBASE
    'pc':5,                     # POLLING CHANNEL        
    'sch':7,                    # SCHEDULE
    'grp':9,                    # GROUP 
    'group':9,
    'mob':13,                   # Managed Object
    'managed-object':13,
    'nod':14,                   # NODE
    'node':14,
    'csr':16,                   # REMOTECSE
    'sub':23,                   # SUBSCRIPTIONS
    'subscription':23,
    'smd':27,                   # SEMANTIC DESCRIPTOR
    'fcn':28,                   # FLEX CONTAINER 
    'flex-container':28         
}

TYs_JSON_FILTERS = {
    'acp':None,             
    'ae':"m2m:cb.m2m:ae",                      # AE
    'application-entity':"m2m:cb.m2m:ae",
    'cnt':"m2m:cb.m2m:cnt",                    # CONTAINER
    'container':"m2m:cb.m2m:cnt",
    'cin':None,                                # CONTENT INSTANCE
    'content-instance':None,                      
    'cb':"m2m:cb",                             # CSEBASE
    'pc':None,                                 # POLLING CHANNEL        
    'sch':None,                                # SCHEDULE
    'grp':None,                                # GROUP 
    'group':None,
    'mob':None,                                # Managed Object
    'managed-object':None,

    'nod':"m2m:cb.m2m:nod",                    # NODE
    'node':"m2m:cb.m2m:nod",

    'csr':None,                                # REMOTECSE
    'sub':"m2m:cb.m2m:sub",                    # SUBSCRIPTIONS
    'subscription':"m2m:cb.m2m:sub",                         
    'smd':None,                                # SEMANTIC DESCRIPTOR
    'fcn':"m2m:cb.m2m:flexContainer",          # FLEX CONTAINER 
    'flex-container':"m2m:cb.m2m:flexContainer",      
}
# Namespace prefix for different onem2m resource types
NSPREFIXs_BY_RESOURCE_TYPE_ID = {
     2: "m2m:ae",    # ae, application entity
     3: "m2m:cnt",   # cnt, Container
     4: "m2m:cin",   # cin, Container Instance
     5: "m2m:cb",    # cb, Common serivce entity base
     9:  "m2m:grp",  # grp, Group          
    13: "m2m:mgo",   # mgo, Managed object
    14: "m2m:nod",   # nod, Node           
    16: "m2m:csr",   # csr, Remote common service entity
    23: "m2m:sub",   # sub, Subscription
    28: "m2m:fc",    # fc, Flex container
}

# Result content indocators
RCIs = {
    
    'return-nothing':0,
    'rn':0,
    'return-all':1,
    'ra':1,
    'return-modified':9,
    'rm':9,
    
    'attributes':1,
    'a':1,
    'attributes-and-children':4,
    'ac':4,
    'children':8,
    'c':8
}

# Notification Content Types for subscriptions
NCTs = {
    "all":          1,
    "a":            1,
    "changed":      2,
    "c":            2,
    "all-and-meta": 3,
    "am":           3,
    "meta":         4,
    "m":            4

}

# Event Notification Criterias for subscriptions
ENCs = {
    "update":                1, #Resource updated
    "u":                     1,
    "delete":                2, #Resource deleted
    "d":                     2,
    "create-child":          3, # Create direct child resource
    "cc":                    3,
    "delete-child":          4, # Delete of direct child resource
    "dc":                    4,
    "retrieve-of-container": 5, # Retrieve of container resource
    "rc":                    5,               
    "command-completed":     6, # Command completed
    "coc":                   6,
    "interworking":          7, # Interworking in process
    "i":                     7
}

# Content encodings for messages posted into a container
CEs = {
  "none":   0,
  "base64": 1,
  "xml":    2,
  "json":   3,
  "opaque": 4, 
  "jpeg":   5,
  "gif":    6,
  "pdf":    1001
}
class CE(Enum):
  none   = 0
  base64 = 1
  xml    = 2
  json   = 3
  opaque = 4 
  jpeg   = 5
  gif    = 6
  pdf    = 1001
  
#pendingNotifications
PNs = {
    "sendLatest":     1,
    "sendAllPending": 2
}

# Operations types of device provisioning requests
DEVPROV_OPs = {
    "create": 1,
    "remove": 2
}