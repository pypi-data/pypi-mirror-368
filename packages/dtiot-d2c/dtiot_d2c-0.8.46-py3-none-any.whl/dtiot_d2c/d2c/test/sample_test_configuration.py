Device01Cfg = {
    "name":"device01-%RUNID%",
    "create_props" : {
        "manufacturer":"PSsystec",
        "model":"Smartbox Mini",
        "sub_model":"NB-IoT",
        "iccid": "89374121317959919924",
        "hardware_version":"2024.1 PC r1",
        "country":"DE",
        "description":"Das ist eine Beschreibung.",
        "label":"this is a label" ,
        "device_type":"Pretty Device" ,
        "device_name":"This is the name of the device",
        "firmware_version":"fw 1.0.1",
        "software_version":"sw 2.0.1",
        "os_version":"os 3.0.1",
        "location":"geo:25.245470,51.454009" ,
        "protocols":["LWM2M"] ,
        "uplink_properties": {"address":"Kuckhoffstr 114A, 13156 Berlin"},
        "device_properties": {"lastMaintenance":"25.3.2025 1300", "prop2":"value2"},
        "credentials_id": "device01-%RUNID%",
        "credentials_secret": "Q3hhc21FTUw3NFNiUlIzUw=="
    },
    "modify_props" : {
        "manufacturer":"x PSsystec",
        "model":"x Smartbox Mini",
        "sub_model":"x NB-IoT",
        "iccid": "99999999317959919924",
        "hardware_version":"x 2024.1 PC r1",
        "country":"XX",
        "description":"x Das ist eine Beschreibung.",
        "label":"x this is a label" ,
        "device_type":"x Pretty Device" ,
        "device_name":"Hallo die Waldfee device_name",
        "firmware_version":"x fw 1.0.1",
        "software_version":"x sw 2.0.1",
        "os_version":"x os 3.0.1",
        "location":"geo:88.999999,88.999999" ,
        "protocols":["LWM2M"] ,
        "uplink_properties": {"address":"xx Kuckhoffstr 114A, 13156 Berlin", "location":"Berlin"},
        "device_properties": {"lastMaintenance":"25.3.2025 1300","Status": "Out of order"},

        #Update lwm2m cridentials is not supported yet via d2ccli
        #"credentials_id": "x device01-%RUNID%",
        #"credentials_secret": "x Q3hhc21FTUw3NFNiUlIzUw=="
    }    
} 
Device02Cfg = {
    "name":"device02-%RUNID%",
    "create_props" : {
        "manufacturer":"PSsystec",
        "model":"Smartbox Mini",
        "sub_model":"NB-IoT",
        "iccid": "89374121317959919924",
        "hardware_version":"2024.1 PC r1",
        "country":"DE",
        "description":"Das ist eine Beschreibung.",
        "label":"this is a label" ,
        "device_type":"Pretty Device" ,
        "firmware_version":"fw 1.0.1",
        "software_version":"sw 2.0.1",
        "os_version":"os 3.0.1",
        "location":"geo:25.245470,51.454009" ,
        "protocols":["LWM2M"] ,
        "uplink_properties": {"address":"Kuckhoffstr 114A, 13156 Berlin"},
        "device_properties": {"lastMaintenance":"25.3.2025 1300"},
        "credentials_id": "device01-%RUNID%",
        "credentials_secret": "Q3hhc21FTUw3NFNiUlIzUw=="
    }
} 

Application01Cfg = {
    "name":"application01-%RUNID%",
    "create_props" : {
        "application_type":"webHook",
        "urls": ["https://api.scs.iot.telekom.com/message-monitor"],
        "connection_properties": {"Auth":"dfadfdsafasdf", "another-token":"88888888"}
    }, 
    "modify_props" : {    
        "urls": ["https://dev.scs.iot.telekom.com/scs-callback-dummy"],
        "connection_properties": {"Auth":"88888888", "another-token":"dfadfdsafasdf"}
    }
}

DeviceGroup01Cfg = {
    "name":"devicegroup01-%RUNID%", 
    "create_props" : {
        "labels":{"deviceType":"SDI People Counter"},
        "device_ids": [],
        "application_ids": [],
        "description": "This is a description"
    },
    "modify_props":{
        "labels":{"deviceType":"SDI People Counter, ELSYS", "street":"Kuckhoffstr."},
        "device_ids": [],
        "application_ids": [],
        "description": "This is an updated description"
    }
}

DeviceGroup02Cfg = {
    "name":"devicegroup02-%RUNID%", 
    "create_props" : {
        "labels":{"deviceType":"SDI People Counter"},
        "device_ids": [],
        "application_ids": [],
        "description": "This is a description"        
    },
    "application_1": {
        "name":"devicegroup02-app1-%RUNID%",
        "create_props":{
            "urls": ["https://api.scs.iot.telekom.com/message-monitor"],
            "labels": {"customerKey":"CUST-001"},        
        }
    },
    "application_2":{
        "name":"devicegroup02-app2-%RUNID%",
        "create_props":{
            "urls": ["https://dev.scs.iot.telekom.com/scs-callback-dummy"],
            "labels": {"customerKey":"CUST-099", "costCenter":"999888"},        
        }
    },
    "device_1": Device01Cfg,
    "device_2": Device02Cfg
}
###################################################################
###################################################################
# MARK: Application test configurations
###################################################################
###################################################################
ApplicationCfg_A01 = {
    "name":"application-a01-%RUNID%",
    "create_props" : {},
    "modify_props" : {}
}
ApplicationCfg_A02 = {
    "name":"application-a02-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor"
        ],
    }, 
    "modify_props" : {}
}
ApplicationCfg_A03 = {
    "name":"application-a03-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],
    }, 
    "modify_props" : {}
}
ApplicationCfg_A04 = {
    "name":"application-a04-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],
        "connection_properties": {
            "Authorization":"cm9sYW5kLmJhbGRpbkB0ZWxla29tLmRlOm42NVIkRXh6bkVwTVltTWY=", 
            "log-level":"debug"
        }        
    }, 
    "modify_props" : {}
}
ApplicationCfg_A04_short_header = {
    "name":"application-a04-short-header-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],
        "connection_properties": {
            "Authorization":"cm9sYW5kLVltTWY=", 
            "log-level":"debug"
        }        
    }, 
    "modify_props" : {}
}
ApplicationCfg_A05 = {
    "name":"application-a05-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor"
        ],
    }, 
    "modify_props" : {
        "urls": [
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],        
    }
}
ApplicationCfg_A06 = {
    "name":"application-a06-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor"
        ],
    }, 
    "modify_props" : {
        "urls": [
            "+https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],   
        "urls_verify": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ]
    }
}
ApplicationCfg_A07 = {
    "name":"application-a07-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],
    }, 
    "modify_props" : {
        "urls": [
            "-https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ], 
        "urls_verify": [
            "https://api.scs.iot.telekom.com/message-monitor",
        ]               
    }
}
ApplicationCfg_A08 = {
    "name":"application-a08-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],
        "connection_properties": {
            "Authorization":"cm9sYW5kLmJhbGRpbkB0ZWxla29tLmRlOm42NVIkRXh6bkVwTVltTWY=", 
            "log-level":"debug"
        }        
    }, 
    "modify_props" : {
        "connection_properties": {
            "+another-prop":"Hallo"
        },
        "connection_properties_verify":{
            "Authorization":"cm9sYW5kLmJhbGRpbkB0ZWxla29tLmRlOm42NVIkRXh6bkVwTVltTWY=", 
            "log-level":"debug",
            "another-prop":"Hallo"                        
        },
        "urls_verify": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],        
    }
}
ApplicationCfg_A08_short_header = {
    "name":"application-a08-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],
        "connection_properties": {
            "Authorization":"cm9sYTWY=", 
            "log-level":"debug"
        }        
    }, 
    "modify_props" : {
        "connection_properties": {
            "+another-prop":"Hallo"
        },
        "connection_properties_verify":{
            "Authorization":"cm9sYTWY=", 
            "log-level":"debug",
            "another-prop":"Hallo"                        
        },
        "urls_verify": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],        
    }
}
ApplicationCfg_A09 = {
    "name":"application-a09-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],
        "connection_properties": {
            "Authorization":"cm9sYW5kLmJhbGRpbkB0ZWxla29tLmRlOm42NVIkRXh6bkVwTVltTWY=",             
            "log-level":"debug",
            "another-prop":"Hallo"
        }        
    }, 
    "modify_props" : {
        "connection_properties": {
            "+another-prop":"Hihihihih"
        },
        "connection_properties_verify":{
            "Authorization":"cm9sYW5kLmJhbGRpbkB0ZWxla29tLmRlOm42NVIkRXh6bkVwTVltTWY=",             
            "log-level":"debug",
            "another-prop":"Hihihihih"                        
        },
        "urls_verify": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],                       
    }
}
ApplicationCfg_A09_short_header = {
    "name":"application-a09-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],
        "connection_properties": {
            "Authorization":"cm9sYTWY=", 
            "log-level":"debug",
            "another-prop":"Hallo"
        }        
    }, 
    "modify_props" : {
        "connection_properties": {
            "+another-prop":"Hihihihih"
        },
        "connection_properties_verify":{
            "Authorization":"cm9sYTWY=", 
            "log-level":"debug",
            "another-prop":"Hihihihih"                        
        },
        "urls_verify": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],                       
    }
}
ApplicationCfg_A10 = {
    "name":"application-a10-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],
        "connection_properties": {
            "Authorization":"cm9sYTWY=", 
            #"Authorization":"cm9sYW5kLmJhbGRpbkB0ZWxla29tLmRlOm42NVIkRXh6bkVwTVltTWY=",                    
            "log-level":"debug",
            "another-prop":"Hallo"
        }        
    }, 
    "modify_props" : {
        "connection_properties": {
            "-another-prop":None
        },
        "connection_properties_verify":{
            "Authorization":"cm9sYTWY=", 
            "log-level":"debug",
        },
        "urls_verify": [
            "https://api.scs.iot.telekom.com/message-monitor",
            "https://dev.scs.iot.telekom.com/scs-callback-dummy"
        ],                                  
    }
}
ApplicationCfg_A11 = {
    "name":"application-a11-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor",
        ],
        "connection_properties": {}
    }, 
    "modify_props" : {}
}
ApplicationCfg_A12 = {
    "name":"application-a12-%RUNID%",
    "create_props" : {
        "urls": [
            "https://api.scs.iot.telekom.com/message-monitor",
        ],
        "connection_properties": {}
    }, 
    "modify_props" : {}
}

###################################################################
###################################################################
# MARK: Device test configurations
###################################################################
###################################################################
DeviceCfg_D01 = {
    "name":"device-d01-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M"
    },
    "modify_props" : {}
}
DeviceCfg_D02 = {
    "name":"device-d02-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "credentials_id": "device-d02-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA=="        
    },
    "modify_props" : {}
}
DeviceCfg_D03 = {
    "name":"devic-d03-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "manufacturer":"PSsystec",
        "model":"Smartbox Mini",
        "sub_model":"NB-IoT",
        "iccid": "89374121317959919924",
        "hardware_version":"2024.1 PC r1",
        "country":"DE",
        "description":"Das ist eine Beschreibung.",
        "label":"this is a label" ,
        "device_type":"Pretty Device" ,
        "device_name":"This is the name of the device",
        "firmware_version":"fw 1.0.1",
        "software_version":"sw 2.0.1",
        "os_version":"os 3.0.1",
        "location":"geo:25.245470,51.454009" ,
        "protocols":["LWM2M"] ,
        "uplink_properties": {},
        "device_properties": {},
        "credentials_id": "device-d03-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA==",    
    },
    "modify_props" : {}
} 
DeviceCfg_D04 = {
    "name":"devic-d04-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "manufacturer":"PSsystec",
        "model":"Smartbox Mini",
        "sub_model":"NB-IoT",
        "iccid": "89374121317959919924",
        "hardware_version":"2024.1 PC r1",
        "country":"DE",
        "description":"Das ist eine Beschreibung.",
        "label":"this is a label" ,
        "device_type":"Pretty Device" ,
        "device_name":"This is the name of the device",
        "firmware_version":"fw 1.0.1",
        "software_version":"sw 2.0.1",
        "os_version":"os 3.0.1",
        "location":"geo:25.245470,51.454009" ,
        "protocols":["LWM2M"] ,
        "uplink_properties": {"address":"Kuckhoffstr 114A, 13156 Berlin"},
        "device_properties": {},
        "credentials_id": "device-d04-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA==",    
    },
    "modify_props" : {}
} 
DeviceCfg_D05 = {
    "name":"devic-d05-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "manufacturer":"PSsystec",
        "model":"Smartbox Mini",
        "sub_model":"NB-IoT",
        "iccid": "89374121317959919924",
        "hardware_version":"2024.1 PC r1",
        "country":"DE",
        "description":"Das ist eine Beschreibung.",
        "label":"this is a label" ,
        "device_type":"Pretty Device" ,
        "device_name":"This is the name of the device",
        "firmware_version":"fw 1.0.1",
        "software_version":"sw 2.0.1",
        "os_version":"os 3.0.1",
        "location":"geo:25.245470,51.454009" ,
        "protocols":["LWM2M"] ,
        "uplink_properties": {},
        "device_properties": {"lastMaintenance":"25.3.2025 1300", "prop2":"value2"},        
        "credentials_id": "device-d05-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA==",    
    },
    "modify_props" : {}
} 
DeviceCfg_D06 = {
    "name":"device-d06-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "manufacturer":"PSsystec",
        "model":"Smartbox Mini",
        "sub_model":"NB-IoT",
        "iccid": "89374121317959919924",
        "hardware_version":"2024.1 PC r1",
        "country":"DE",
        "description":"Das ist eine Beschreibung.",
        "label":"this is a label" ,
        "device_type":"Pretty Device" ,
        "device_name":"This is the name of the device",
        "firmware_version":"fw 1.0.1",
        "software_version":"sw 2.0.1",
        "os_version":"os 3.0.1",
        "location":"geo:25.245470,51.454009" ,
        "protocols":["LWM2M"] ,
        "uplink_properties": {},
        "device_properties": {},
        "credentials_id": "device-d06-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA==",    
    },
    "modify_props" : {
        "manufacturer":"x PSsystec",
        "model":"x Smartbox Mini",
        "sub_model":"x NB-IoT",
        "iccid": "99999999317959919924",
        "hardware_version":"x 2024.1 PC r1",
        "country":"XX",
        "description":"x Das ist eine Beschreibung.",
        "label":"x this is a label" ,
        "device_type":"x Pretty Device" ,
        "device_name":"Hallo die Waldfee device_name",
        "firmware_version":"x fw 1.0.1",
        "software_version":"x sw 2.0.1",
        "os_version":"x os 3.0.1",
        "location":"geo:88.999999,88.999999" ,
        #Update lwm2m cridentials is not supported yet via d2ccli
        #"credentials_id": "x device01-%RUNID%",
        #"credentials_secret": "x Q3hhc21FTUw3NFNiUlIzUw=="
    }    
} 
DeviceCfg_D07 = {
    "name":"device-d07-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "manufacturer":"PSsystec",
        "model":"Smartbox Mini",
        "sub_model":"NB-IoT",
        "iccid": "89374121317959919924",
        "hardware_version":"2024.1 PC r1",
        "country":"DE",
        "description":"Das ist eine Beschreibung.",
        "label":"this is a label" ,
        "device_type":"Pretty Device" ,
        "device_name":"This is the name of the device",
        "firmware_version":"fw 1.0.1",
        "software_version":"sw 2.0.1",
        "os_version":"os 3.0.1",
        "location":"geo:25.245470,51.454009" ,
        "protocols":["LWM2M"] ,
        "uplink_properties": {},
        "device_properties": {
            "lastMaintenance":"25.3.2025 1300", 
            "prop2":"value2"
        },        
        "credentials_id": "device-d07-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA==",    
    },
    "modify_props" : {
        "device_properties": {
            "+prop77":"value77", 
            "+prop88":"value88"
        },  
        "device_properties_verify": {
            "lastMaintenance":"25.3.2025 1300", 
            "prop2":"value2",
            "prop77":"value77", 
            "prop88":"value88"
        },  
                  
    }
} 
DeviceCfg_D08 = {
    "name":"device-d08-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "manufacturer":"PSsystec",
        "model":"Smartbox Mini",
        "sub_model":"NB-IoT",
        "iccid": "89374121317959919924",
        "hardware_version":"2024.1 PC r1",
        "country":"DE",
        "description":"Das ist eine Beschreibung.",
        "label":"this is a label" ,
        "device_type":"Pretty Device" ,
        "device_name":"This is the name of the device",
        "firmware_version":"fw 1.0.1",
        "software_version":"sw 2.0.1",
        "os_version":"os 3.0.1",
        "location":"geo:25.245470,51.454009" ,
        "protocols":["LWM2M"] ,
        "uplink_properties": {},
        "device_properties": {
            "lastMaintenance":"25.3.2025 1300", 
            "prop2":"value2"
        },        
        "credentials_id": "device-d08-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA==",    
    },
    "modify_props" : {
        "device_properties": {
            "+prop77":"value77 and 77 and 77", 
            "+prop88":"value88 and 88 and 88"
        },  
        "device_properties_verify": {
            "lastMaintenance":"25.3.2025 1300", 
            "prop2":"value2",
            "prop77":"value77 and 77 and 77", 
            "prop88":"value88 and 88 and 88"
        },  
                  
    }
} 
DeviceCfg_D09 = {
    "name":"device-d09-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "manufacturer":"PSsystec",
        "model":"Smartbox Mini",
        "sub_model":"NB-IoT",
        "iccid": "89374121317959919924",
        "hardware_version":"2024.1 PC r1",
        "country":"DE",
        "description":"Das ist eine Beschreibung.",
        "label":"this is a label" ,
        "device_type":"Pretty Device" ,
        "device_name":"This is the name of the device",
        "firmware_version":"fw 1.0.1",
        "software_version":"sw 2.0.1",
        "os_version":"os 3.0.1",
        "location":"geo:25.245470,51.454009" ,
        "protocols":["LWM2M"] ,
        "uplink_properties": {},
        "device_properties": {
            "lastMaintenance":"25.3.2025 1300", 
            "prop2":"value2"
        },        
        "credentials_id": "device-d09-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA==",    
    },
    "modify_props" : {
        "device_properties": {
            "-prop77":None,
            "-prop88":None
        },  
        "device_properties_verify": {
            "lastMaintenance":"25.3.2025 1300", 
            "prop2":"value2",
        },  
                  
    }
} 
DeviceCfg_D10 = {
    "name":"device-d10-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "manufacturer":"PSsystec",
        "model":"Smartbox Mini",
        "sub_model":"NB-IoT",
        "iccid": "89374121317959919924",
        "hardware_version":"2024.1 PC r1",
        "country":"DE",
        "description":"Das ist eine Beschreibung.",
        "label":"this is a label" ,
        "device_type":"Pretty Device" ,
        "device_name":"This is the name of the device",
        "firmware_version":"fw 1.0.1",
        "software_version":"sw 2.0.1",
        "os_version":"os 3.0.1",
        "location":"geo:25.245470,51.454009" ,
        "protocols":["LWM2M"] ,
        "uplink_properties": {},
        "device_properties": {},
        "credentials_id": "device-d10-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA==",    
    },
    "modify_props" : {
        "uplink_properties": {
            "+decoding-selector":"adeunis", 
            "+prop88":"value88"
        },  
        "uplink_properties_verify": {
            "decoding-selector":"adeunis", 
            "prop88":"value88"
        },  
    }
} 
DeviceCfg_D11 = {
    "name":"device-d11-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "manufacturer":"PSsystec",
        "model":"Smartbox Mini",
        "sub_model":"NB-IoT",
        "iccid": "89374121317959919924",
        "hardware_version":"2024.1 PC r1",
        "country":"DE",
        "description":"Das ist eine Beschreibung.",
        "label":"this is a label" ,
        "device_type":"Pretty Device" ,
        "device_name":"This is the name of the device",
        "firmware_version":"fw 1.0.1",
        "software_version":"sw 2.0.1",
        "os_version":"os 3.0.1",
        "location":"geo:25.245470,51.454009" ,
        "protocols":["LWM2M"] ,
        "uplink_properties": {},
        "device_properties": {},
        "credentials_id": "device-d11-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA==",    
    },
    "modify_props" : {
        "uplink_properties": {
            "+decoding-selector":"adeunis",             
            "+prop88":"value88"
        },  
        "uplink_properties_verify": {
            "decoding-selector":"adeunis", 
            "prop88":"value88"
        },  
    }
} 
DeviceCfg_D13 = {
    "name":"device-d13-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "credentials_id": "device-d13-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA=="        
    },
    "modify_props" : {},
    "sleep_secs": 20
}
DeviceCfg_D14 = {
    "name":"device-d14-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "credentials_id": "device-d14-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA=="        
    },
    "modify_props" : {},
    "sleep_secs": 20
}
DeviceCfg_D15 = {
    "name":"device-d15-%RUNID%",
    "create_props" : {
        "protocol":"LWM2M",
        "credentials_id": "device-d15-%RUNID%",
        "credentials_secret": "OSRBYUJrckhYbVlCNEJvQA=="        
    },
    "modify_props" : {},
    "sleep_secs": 20,
    "inject_data": {"firstName":"Roland", "lastName":"Baldin"},
}
###################################################################
###################################################################
# MARK: Device group test configurations
###################################################################
###################################################################
DeviceGroupCfg_DG01 = {
    "name":"devicegroup-01-%RUNID%", 
    "create_props" : {},
    "modify_props":{}
}
DeviceGroupCfg_DG02 = {
    "name":"devicegroup-02-%RUNID%", 
    "create_props" : {
        "description":"Das ist eine DeviceGroup"
    },
    "modify_props":{}
}
DeviceGroupCfg_DG03 = {
    "name":"devicegroup-03-%RUNID%", 
    "create_props" : {
        "description":"Das ist eine DeviceGroup"
    },
    "modify_props":{
         "description":"Das ist eine geänderte DeviceGroup"
    }
}
DeviceGroupCfg_DG04 = {
    "name":"devicegroup-04-%RUNID%", 
    "create_props" : {},
    "modify_props":{},
    "application_1": {
        "name":"devicegroup-04-app1-%RUNID%",
        "create_props":{
            "urls": ["https://api.scs.iot.telekom.com/message-monitor"],
        }
    },    
}
DeviceGroupCfg_DG05_long = {
    "name":"devicegroup-05-%RUNID%", 
    "create_props" : {},
    "modify_props":{},
    "application_1": {
        "name":"devicegroup-05-app1-%RUNID%-123456789012345678901234567890",
        "create_props":{
            "urls": ["https://api.scs.iot.telekom.com/message-monitor"],
        }
    },  
    "device_1": DeviceCfg_D02,      
}
DeviceGroupCfg_DG05_short = {
    "name":"dg05%RUNID%", 
    "create_props" : {},
    "modify_props":{},
    "application_1": {
        "name":"dg5ap%RUNID%",
        "create_props":{
            "urls": ["https://api.scs.iot.telekom.com/message-monitor"],
        }
    },  
    "device_1": DeviceCfg_D02,      
}
DeviceGroupCfg_DG06_short = {
    "name":"dg06%RUNID%", 
    "create_props" : {},
    "modify_props":{},
    "application_1": {
        "name":"dg6ap%RUNID%",
        "create_props":{
            "urls": ["https://api.scs.iot.telekom.com/message-monitor"],
        }
    },  
    "device_1": {
        "name":"d106-%RUNID%",
        "create_props" : {
            "protocol":"LWM2M"
        },
        "modify_props" : {}
    },
    "device_2": {
        "name":"d206-%RUNID%",
        "create_props" : {
            "protocol":"LWM2M"
        },
        "modify_props" : {}
    },
}
DeviceGroupCfg_DG07_short = {
    "name":"dg07%RUNID%", 
    "create_props" : {},
    "modify_props":{},
    "application_1": {
        "name":"dg7ap1%RUNID%",
        "create_props":{
            "urls": ["https://api.scs.iot.telekom.com/message-monitor"],
        }
    },  
    "application_2": {
        "name":"dg7ap2%RUNID%",
        "create_props":{
            "urls": ["https://dev.scs.iot.telekom.com/scs-callback-dummy"],
        }
    },  
    "device_1": {
        "name":"dg7d1-%RUNID%",
        "create_props" : {
            "protocol":"LWM2M"
        },
        "modify_props" : {}
    },
}
DeviceGroupCfg_DG08_short = {
    "name":"dg8%RUNID%", 
    "create_props" : {},
    "modify_props":{},
    "application_1": {
        "name":"dg8ap1%RUNID%",
        "create_props":{
            "urls": ["https://api.scs.iot.telekom.com/message-monitor"],
        }
    },  
    "application_2": {
        "name":"dg8ap2%RUNID%",
        "create_props":{
            "urls": ["https://dev.scs.iot.telekom.com/scs-callback-dummy"],
        }
    },  
    "device_1": {
        "name":"dg8d1-%RUNID%",
        "create_props" : {
            "protocol":"LWM2M"
        },
        "modify_props" : {}
    },
    "device_2": {
        "name":"dg8d2-%RUNID%",
        "create_props" : {
            "protocol":"LWM2M"
        },
        "modify_props" : {}
    },
}
DeviceGroupCfg_DG09_short = { 
    "name":"dg9%RUNID%", 
    "create_props" : {},
    "modify_props":{},
    "application_1": {
        "name":"dg9ap1%RUNID%",
        "create_props":{
            "urls": ["https://api.scs.iot.telekom.com/message-monitor"],
        }
    },  
    "application_2": {
        "name":"dg9ap2%RUNID%",
        "create_props":{
            "urls": ["https://dev.scs.iot.telekom.com/scs-callback-dummy"],
        }
    },  
    "device_1": {
        "name":"dg9d1-%RUNID%",
        "create_props" : {
            "protocol":"LWM2M"
        },
        "modify_props" : {}
    },
    "device_2": {
        "name":"dg9d2-%RUNID%",
        "create_props" : {
            "protocol":"LWM2M"
        },
        "modify_props" : {}
    },
}

DeviceGroupCfg_DG10_short = DeviceGroupCfg_DG09_short
DeviceGroupCfg_DG11_short = DeviceGroupCfg_DG09_short
DeviceGroupCfg_DG15_short = DeviceGroupCfg_DG09_short
DeviceGroupCfg_DG16_short = DeviceGroupCfg_DG09_short

DeviceGroupCfg_DG17_short = {
    "name":"dg17%RUNID%", 
    "create_props" : {},
    "modify_props":{},
    "sleep_secs": 5,  # Sleep seconds before the uplink message is injected
    "correlation_id":"d2ctest_%NOWSECS%",    
    "application_1": {
        "name":"dg17ap%RUNID%",
        "create_props":{
            "urls": ["https://api.scs.iot.telekom.com/message-monitor?store-body-key=d2ctest_%NOWSECS%"],
        },
        "get_message_urls":["https://api.scs.iot.telekom.com/message-monitor/body/d2ctest_%NOWSECS%"]
    },  
    "device_1": DeviceCfg_D02,      
}
DeviceGroupCfg_DG18_short = {
    "name":"dg18%RUNID%", 
    "create_props" : {},
    "modify_props":{},
    "sleep_secs": 5,  # Sleep seconds before the uplink message is injected
    "correlation_id":"d2ctest_%NOWSECS%",    
    "application_1": {
        "name":"dg18ap1_%RUNID%",
        "create_props":{
            "urls": ["https://api.scs.iot.telekom.com/message-monitor?store-body-key=d2ctest_%NOWSECS%_1"],
        },
        "get_message_urls":["https://api.scs.iot.telekom.com/message-monitor/body/d2ctest_%NOWSECS%_1"]
    },  
    "application_2": {
        "name":"dg18ap2_%RUNID%",
        "create_props":{
            "urls": ["https://api.scs.iot.telekom.com/message-monitor?store-body-key=d2ctest_%NOWSECS%_2"],
        },
        "get_message_urls":["https://api.scs.iot.telekom.com/message-monitor/body/d2ctest_%NOWSECS%_2"]
    },  
    "device_1": DeviceCfg_D02,      
}

DeviceGroupCfg_DG20 = DeviceGroupCfg_DG01
DeviceGroupCfg_DG21 = DeviceGroupCfg_DG01

# DeviceGroup02Cfg = {
#     "name":"devicegroup02-%RUNID%", 
#     "create_props" : {
#         "labels":{"deviceType":"SDI People Counter"},
#         "device_ids": [],
#         "application_ids": [],
#         "description": "This is a description"        
#     },
#     "application_1": {
#         "name":"devicegroup02-app1-%RUNID%",
#         "create_props":{
#             "urls": ["https://api.scs.iot.telekom.com/message-monitor"],
#             "labels": {"customerKey":"CUST-001"},        
#         }
#     },
#     "application_2":{
#         "name":"devicegroup02-app2-%RUNID%",
#         "create_props":{
#             "urls": ["https://dev.scs.iot.telekom.com/scs-callback-dummy"],
#             "labels": {"customerKey":"CUST-099", "costCenter":"999888"},        
#         }
#     },
#     "device_1": Device01Cfg,
#     "device_2": Device02Cfg
# }