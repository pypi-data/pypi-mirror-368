import dtiot_d2c.d2c.utils as utils
import dtiot_d2c.dmo as dmo

D2C_SYSTEM_VERSION_LABEL = "d2c"
D2C_SYSTEM_VERSION = "1.0"

# Operation indicator characters to update labels
UPDT_LABS_OPERATION_INDICATOR_ADD = "+"
UPDT_LABS_OPERATION_INDICATOR_DEL = "-"
UPDT_LABS_OPERATION_INDICATOR_ADD = "+"
UPDT_LABS_OPERATION_INDICATOR_DEL = "-"

CMDARGS:dict = {
    "-o": ["--origin", 
           {"metavar":"<string>", 
            "dest":"origin", 
            "required": False,
            "default":None,
            "help":"X-M2M-ORIGIN heder."}
    ],
    "-n" : ["--name", 
        {
            "dest":"name", 
            "metavar":"<string>", 
            "help":f"Unique object name."
        }
    ],      
    "-i" : ["--id", 
        {
            "dest":"id", 
            "metavar":"<string>", 
            "help":f"Id of the object."
        }
    ],          
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
    # Device Group parameters 
    "-ds": ["--devices", 
            {
                "type": utils.argparse_type_list,
                "metavar":"<list-of-strings>", 
                "dest":"devices",
                "required": False,
                "default":[],
                "help":"Comma separated list of onem2m device names."
            }
    ],            
    "-as": ["--applications", 
            {
                "type": utils.argparse_type_list,
             "metavar":"<list-of-strings>", 
            "dest":"applications",
            "required": False,
            "default":[],
            "help":"Comma separated list of onem2m application names."
        }
    ],     
    "-addns": ["--add-names", 
            {"metavar":"<string>", 
            "dest":"add_names",
            "required": False,
            "default":[],
            "help":"Comma separated list of device or application names which shall be added."}
    ],         
    "-rmns": ["--remove-names", 
            {"metavar":"<string>", 
            "dest":"remove_names",
            "required": False,
            "default":[],
            "help":"Comma separated list of device or application names which shall be remvoved."}
    ],         

    # Application parameters
    "-us" : ["--urls", 
        {
            "type": utils.argparse_type_list,
            "dest":"urls", 
            "metavar":"<urls>",
            "help":f"Comma sepaerated list of application urls. "
        }
    ],         
    "-at" : ["--application-type", 
        {
            "metavar":"<string>", 
            "dest":"application_type", 
            "choices": ["WebHook"], 
            "default":"WebHook", 
            "help":f"Type of the application. Possible values are WebHook. If not defined webHook is used."
        }
    ],         
    "-cp" : ["--connection-properties", 
        {
            "type":utils.argparse_type_json,
            "dest":"connection_properties", 
            "metavar":"'<{\"key\":\"value\", \"key\":\"value\"}>'", 
            "help":f"Properties to configure the application connection. For WebHooks it would be header fields."
        }
    ],      

    # Device parameters
    "-rt": ["--type", 
            {"metavar":"<string>",
            "dest": "ty",
            "choices": dmo.TYs.keys(),
            "help":"Type of resource."}
    ],      
    "-ma" : ["--manufacturer", 
        {
            "metavar":"<string>", 
            "dest":"manufacturer", 
            "required":False,
            "default":None,
            "help":f"Manufacturer of the device. If not defined Generic is used."
        }
    ],    
    "-mo" : ["--model", 
        {
            "metavar":"<string>", 
            "dest":"model", 
            "required":False,
            "default":None,
            "help":f"Model of the device. If not defined Generic is used."
        }
    ],    
    "-smo" : ["--sub-model", 
        {
            "metavar":"<string>", 
            "dest":"sub_model", 
            "required":False,
            "help":f"Sub model of the device."
        }
    ],        
    "-ic" : ["--iccid", 
        {
            "metavar":"<string>", 
            "dest":"iccid", 
            "required":False,
            "default":"282828282828", 
            "help":f"ICCID of the SIM card in the device. If not defined 282828282828 is used."
        }
    ],    
    "-pr" : ["--protocol", 
        {
            "metavar":"<string>", 
            "dest":"protocol", 
            "choices": ["LWM2M", "LoRaWAN", "UDP", "MQTT", "DTLS CoAP", "CoAP", "HTTP"], 
            "default":"LWM2M", 
            "help":f"Protocol of the device. Possible values are HTTP, MQTT, LWM2M. If not defined LWM2M is used."
        }
    ],        
    "-lo" : ["--location", 
        {
            "dest":"location", 
            "metavar":"<string>", 
            "help":f"Device location."
        }
    ],        
    "-la" : ["--label", 
        {
            "dest":"label", 
            "metavar":"<string>", 
            "help":f"Device label."
        }
    ],        
    "-fv" : ["--firmware-version", 
        {
            "dest":"firmware_version", 
            "metavar":"<string>", 
            "help":f"Device firmware version."
        }
    ],    
    "-sv" : ["--software-version", 
        {
            "dest":"software_version", 
            "metavar":"<string>", 
            "help":f"Device firmware version."
        }
    ],        
    "-ov" : ["--os-version", 
        {
            "dest":"os_version", 
            "metavar":"<string>", 
            "help":f"Device operating system version."
        }
    ],    
    "-hv" : ["--hardware-version", 
        {
            "dest":"hardware_version", 
            "metavar":"<string>", 
            "help":f"Device hardware version."
        }
    ],        
    "-cy" : ["--country", 
        {
            "dest":"country", 
            "metavar":"<string>", 
            "default":None,
            "help":f"Device country code. If not defined DE is used."
        }
    ],        
    "-dty" : ["--device-type", 
        {
            "dest":"device_type", 
            "metavar":"<string>", 
            "help":f"Type of the device."
        }
    ],      
    "-dna" : ["--device-name", 
        {
            "dest":"device_name", 
            "metavar":"<string>", 
            "help":f"Type of the device."
        }
    ],      
    "-de" : ["--description", 
        {
            "dest":"description", 
            "metavar":"<string>", 
            "help":f"Description of the device."
        }
    ],   
    "-up" : ["--uplink-properties", 
        {
            "dest":"uplink_properties", 
            "metavar":"'<{\"key\":\"value\", \"key\":\"value\"}>'", 
            "help":f"Additional uplink properties."
        }
    ],   
    "-dp" : ["--device-properties", 
        {
            "dest":"device_properties", 
            "metavar":"'<{\"key\":\"value\", \"key\":\"value\"}>'", 
            "help":f"Additional device properties."
        }
    ],   
    "-cid" : ["--credentials-id", 
        {
            "dest":"credentials_id", 
            "metavar":"'<string>'", 
            "help":f"Id of the device credentials such as PSK identity. If this is not defined the device serial number is used instead."
        }
    ],   
    "-csec" : ["--credentials-secret", 
        {
            "dest":"credentials_secret", 
            "metavar":"'<string>'", 
            "help":f"Secret of the device credentials such as the PSK key for UDP encryption. This key shall be base64 encoded."
        }
    ],
    "-mn" : ["--message-name", 
        {
            "dest":"message_name", 
            "metavar":"<string>", 
            "help":f"Identifying name of the message."
        }
    ],
    "-mi" : ["--message-id", 
        {
            "dest":"message_id", 
            "metavar":"<string>", 
            "help":f"Identifying id of the message."
        }
    ],     
    "-ms" : ["--message-store", 
        {
            "metavar":"<message-store>", 
            "dest":"msg_store", 
            "choices": ["uplink-inbound", "uli", "uplink-outbound", "ulo",
                        "downlink-inbound", "dli", "downlink-outbound", "dlo"], 
            "help": "Type of message store which shall be queried. Possible values are: uplink-inbound, uli, uplink-outbound, ulo, downlink-inbound, dli, downlink-outbound, dlo."
        }
    ],            
}     