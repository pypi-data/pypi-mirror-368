import os

###
# Feature flags of the various CLI command interfaces. Those flags are set by 
# the command implementation to tell the controlling modules what the implemenation
# requires.
###
REQUIRES_CONFIG = 1
REQUIRES_PROFILE = 2
REQUIRES_DMOAPICONNECT = 4

# Names of environment variables, directories and files
###

# Environment variable of the directory which contains the configuration files
ENVVARNAME_CFGDIR = "D2CCLI_CONFIGDIR"

# File which contains the API access configuration
ENVVARNAME_CFGFILE = "D2CCLI_CONFIGFILE"

# Default name of the directory which contains the configuration files
DEFAULT_CFGDIR_NAME = ".d2c"

# Default name of the configuration file
DEFAULT_CFGFILE_NAME = "config.json"

# Name of the profiles sub directory within the configuration directory
DEFAULT_PROFILES_DIRNAME = "profiles"
DEFAULT_PROFILES_DIRPATH = "$HOME/%s/%s" % (DEFAULT_CFGDIR_NAME, DEFAULT_PROFILES_DIRNAME)

# Profile file extension
PROFILE_FILE_EXT = "profile"

# Configuration element names
CEN_ACTIVE_PROFILE_FILE = "activeProfileFile"
CEN_PROFILE_DIR = "profilesDir"

# Init configuration 
DEFAULT_CONFIGURATION = {
    "activeProfileFile": "",
    "profilesDir": DEFAULT_PROFILES_DIRPATH
}

# Profile configuration
PROFILE_CONFIG = {
    "elements": [
        {"name":"profileName",  "label":"Profile Name",       "type":"string", "state":"normal", "default":"My Profile"},
        {"name":"apiUrl",       "label":"API URL",             "type":"string", "state":"normal", "default":"https://qa.spacegate.telekom.de/bond/t-iot-hub/device-management-orchestrator/v3/TENANT-REQUIRED"},
        {"name":"getTokenUrl",  "label":"Get Token URL",       "type":"string", "state":"normal", "default":"https://qa.spacegate.telekom.de/auth/realms/bond/protocol/openid-connect/token"},
        {"name":"clientId",     "label":"Client Id",          "type":"string", "state":"normal", "default":"t-iot-hub--##########--########-####-####-####-################"},
        {"name":"clientSecret", "label":"Client Secret",      "type":"string", "state":"normal", "default":"########-####-####-####-########"},
    ],
    "filenameElements":["profileName", ".profile"] 
}

D2CCLI_DEFAULT_ORIGIN="d2ccli"

###
# Factory function to create an APIConnection object from profile
from dtiot_d2c.cli.profile import Profile


def createApiConnection(profile:Profile)->any:
    from dtiot_d2c.dmo import ApiClient
    apiClient:ApiClient = ApiClient(api_url=profile.getElement("apiUrl"),
                                    origin=D2CCLI_DEFAULT_ORIGIN,
                                    get_token_url=profile.getElement("getTokenUrl"),
                                    client_id=profile.getElement("clientId"),
                                    client_secret=profile.getElement("clientSecret"))

    apiClient.auth()
    
    return apiClient

###
# Configuration of the profile manager web application and api
# Profile management web application
#PMWEBAPP_PORT=3000
# PMWEBAPP_PATH="/profile-manager"

# Profile management API 
#from .prfmanapi.configs import DEFAULT as PMAPI_CFG
#PMAPI_PROTOCOL="http"
#PMAPI_HOST="127.0.0.1"
#PMAPI_PORT=PMAPI_CFG.ServicePort
#PMAPI_PATH=PMAPI_CFG.ServiceName

###
# Registration of cli commands ...
CLICommands = [
    {
        "name": "CONFIGURATION",
        "help": "Confguration commands",
        "commands": [
            {
                "name": ["create-configuration", "cc"],
                "cmdFile": "%s/configCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "CreateConfigurationCLI"
            }
        ]
    },
    {
        "name": "PROFILE",
        "help": "Profile commands",
        "commands": [
            {
                "name": ["list-profiles", "lp"],
                "cmdFile": "%s/profileCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "ListProfilesCLI"
            },
            {
                "name": ["print-profile", "pp"],
                "cmdFile": "%s/profileCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "PrintProfileCLI"
            },
            {
                "name": ["add-profile", "ap"],
                "cmdFile": "%s/profileCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "NewProfileCLI"
            },
            {
                "name": ["modify-profile", "mp"],
                "cmdFile": "%s/profileCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "EditProfileCLI"
            },
            {
                "name": ["activate-profile", "acp"],
                "cmdFile": "%s/profileCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "ActivateProfileCLI"
            },
            {
                "name": ["print-active-profile", "pap"],
                "cmdFile": "%s/profileCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "PrintActivatedProfileCLI"
            },
            {
                "name": ["profile-manager", "pm"],
                "cmdFile": "%s/profileCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "StartProfileManagerGuiCLI"
            },
            # {
            #     "name": ["profile-manager-webapp", "pm2"],
            #     "cmdFile": "%s/profileCLI.py" % (os.path.dirname(__file__)),
            #     "cmdClass": "StartProfileManagerWebBrowserCLI"
            # }
            
        ]
    },
    {
        "name": "DMO",
        "help": "DMO functions",
        "commands": [
            {
                "name": ["get-resources", "gr"],
                "cmdFile": "%s/../dmo/dmoCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "GetResourcesCLI"
            },
            {
                "name": ["add-resource", "ar"],
                "cmdFile": "%s/../dmo/dmoCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "AddResourceCLI"
            },
            {
                "name": ["update-resource", "ur"],
                "cmdFile": "%s/../dmo/dmoCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "UpdateResourceCLI"
            },
            {
                "name": ["delete-resource", "dr"],
                "cmdFile": "%s/../dmo/dmoCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeleteResourceCLI"
            },
            {
                "name": ["get-device-provisioning-requests", "gdpreq"],
                "cmdFile": "%s/../dmo/dmoCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "GetDeviceProvisioningRequestsCLI"
            },                      
            {
                "name": ["get-device-provisioning-responses", "gdpres"],
                "cmdFile": "%s/../dmo/dmoCLI.py" % (os.path.dirname(__file__)),
                "cmdClass": "GetDeviceProvisioningResponsesCLI"
            },      
            # {
            # {
            #     "name": ["update-resource", "ur"],
            #     "cmdFile": "%s/../iothubcli/dmoCLI.py" % (os.path.dirname(__file__)),
            #     "cmdClass": "UpdateResourceCLI"
            # },
            # {
            #     "name": ["add-message-container", "amsgc"],
            #     "cmdFile": "%s/../iothubcli/dmoCLI.py" % (os.path.dirname(__file__)),
            #     "cmdClass": "AddMessageContainerCLI"
            # },                 
            # {
            #     "name": ["add-subscription", "asub"],
            #     "cmdFile": "%s/../iothubcli/dmoCLI.py" % (os.path.dirname(__file__)),
            #     "cmdClass": "AddSubscriptionCLI"
            # },
            # {
            #     "name": ["post-message", "pmsg"],
            #     "cmdFile": "%s/../iothubcli/dmoCLI.py" % (os.path.dirname(__file__)),
            #     "cmdClass": "PostMessageToContainerCLI"
            # },
        ]
    },
    # Devices
    {
        "name": "D2C Device Management",
        "help": "D2C functions to manage devices",
        "commands": [

            {
                "name": ["add-device", "ad"],
                "cmdFile": "%s/../d2c/device/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "AddDeviceCLI"
            },    
            {
                "name": ["add-lwm2m-device", "alwm2md"],
                "cmdFile": "%s/../d2c/device/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "AddLwm2mDeviceCLI"
            },                
            {
                "name": ["get-devices", "gd"],
                "cmdFile": "%s/../d2c/device/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "GetDevicesCLI"
            },      
            {
                "name": ["update-device", "ud"],
                "cmdFile": "%s/../d2c/device/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "UpdateDeviceCLI"
            },
            {
                "name": ["delete-device", "dd"],
                "cmdFile": "%s/../d2c/device/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeleteDeviceCLI"
            },
            {
                "name": ["inject-uplink-message", "ium"],
                "cmdFile": "%s/../d2c/device/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "InjectUplinkMessageCLI"
            },                      
            {
                "name": ["inject-downlink-message", "idm"],
                "cmdFile": "%s/../d2c/device/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "InjectDownlinkMessageCLI"
            },                      
            {
                "name": ["get-device-messages", "gdms"],
                "cmdFile": "%s/../d2c/device/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "GetDeviceMessagesCLI"
            },            
            {
                "name": ["delete-device-message", "ddm"],
                "cmdFile": "%s/../d2c/device/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeleteDeviceMessageCLI"
            },            
            
        ]
    },
    # Applications
    {
        "name": "D2C Application Management",
        "help": "D2C functions to manage applications",
        "commands": [    
            {
                "name": ["add-application", "aa"],
                "cmdFile": "%s/../d2c/application/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "AddApplicationCLI"
            },    
            {
                "name": ["get-applications", "ga"],
                "cmdFile": "%s/../d2c/application/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "GetApplicationsCLI"
            },                              
            {
                "name": ["update-application", "ua"],
                "cmdFile": "%s/../d2c/application/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "UpdateApplicationCLI"
            },                        
            {
                "name": ["delete-application", "da"],
                "cmdFile": "%s/../d2c/application/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeleteApplicationCLI"
            },   
        ]
    },
    ### Device Groups
    {
        "name": "D2C Device Group Management",
        "help": "D2C functions to manage device groups",
        "commands": [
            {
                "name": ["add-device-group", "adg"],
                "cmdFile": "%s/../d2c/device_group/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "AddDeviceGroupCLI"
            },                       
            {
                "name": ["get-device-groups", "gdg"],
                "cmdFile": "%s/../d2c/device_group/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "GetDeviceGroupsCLI"
            },                              
            {
                "name": ["update-device-group", "udg"],
                "cmdFile": "%s/../d2c/device_group/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "UpdateDeviceGroupCLI"
            },                        
            {
                "name": ["delete-device-group", "ddg"],
                "cmdFile": "%s/../d2c/device_group/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeleteDeviceGroupCLI"
            },     
        ]
    },
    # Admin
    {
        "name": "D2C Admin",
        "help": "D2C admin functions",
        "commands": [
            {
                "name": ["add-d2ccli-application"],
                "cmdFile": "%s/../d2c/application/cli.py" % (os.path.dirname(__file__)),
                "cmdClass": "AddC2cCliApplicationCLI"
            },                
            {
                "name": ["version"],
                "cmdFile": "%s/../d2c/commands/version.py" % (os.path.dirname(__file__)),
                "cmdClass": "VersionCLI"
            },                 
        ]
    },
    # Test
    {
        "name": "Tests",
        "help": "Test functions",
        "envVars":["D2CCLI_TEST"],        
        "commands": [
            {
                "name": ["verify-d2c-model"],
                "cmdFile": "%s/../d2c/test/verify_d2c_model.py" % (os.path.dirname(__file__)),
                "cmdClass": "VerifyD2CModelCLI"
            },                
            {
                "name": ["get-sample-configuration-file"],
                "cmdFile": "%s/../d2c/test/print_sample_test_configuration.py" % (os.path.dirname(__file__)),
                "cmdClass": "PrintSampleTestConfigurationCLI"
            },      
            {
                "name": ["verify-device-group-consistency"],
                "cmdFile": "%s/../d2c/test/verify_device_group_consistency.py" % (os.path.dirname(__file__)),
                "cmdClass": "VerifyDeviceGroupConsistencyCLI"
            },                   
            {
                "name": ["get-resource-performance-test"],
                "cmdFile": "%s/../d2c/test/perftest_get_resource.py" % (os.path.dirname(__file__)),
                "cmdClass": "PerformanceTest_GetResourceCLI"
            },          
            {
                "name": ["run-test-cases"],
                "cmdFile": "%s/../d2c/test/all_test_cases_runner.py" % (os.path.dirname(__file__)),
                "cmdClass": "AllTestCasesRunner_CLI"
            },    
            
            #########################
            # Application test cases              
            {
                "name": ["test-a01"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A01_CLI"
            },    
            {
                "name": ["test-a02"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A02_CLI"
            },    
            {
                "name": ["test-a03"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A03_CLI"
            },    
            {
                "name": ["test-a04"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A04_CLI"
            },    
            {
                "name": ["test-a04-short-header"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A04_CLI_short_header"
            },                
            {
                "name": ["test-a05"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A05_CLI"
            },                
            {
                "name": ["test-a06"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A06_CLI"
            },                            
            {
                "name": ["test-a07"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A07_CLI"
            },               
            {
                "name": ["test-a08"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A08_CLI"
            },               
            {
                "name": ["test-a08-short-header"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A08_CLI_short_header"
            },         
            {
                "name": ["test-a09"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A09_CLI"
            },          
            {
                "name": ["test-a09-short-header"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A09_CLI_short_header"
            },               
            {
                "name": ["test-a10"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A10_CLI"
            },                    
            {
                "name": ["test-a11"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A11_CLI"
            },    
            {
                "name": ["test-a12"],
                "cmdFile": "%s/../d2c/test/test_cases_application.py" % (os.path.dirname(__file__)),
                "cmdClass": "ApplicationTest_A12_CLI"
            },  
            
            #########################
            # Device test cases              
            {
                "name": ["test-d01"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D01_CLI"
            },         
            {
                "name": ["test-d02"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D02_CLI"
            },      
            {
                "name": ["test-d03"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D03_CLI"
            },                  
            {
                "name": ["test-d04"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D04_CLI"
            },                  
            {
                "name": ["test-d05"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D05_CLI"
            },         
            {
                "name": ["test-d06"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D06_CLI"
            },                           
            {
                "name": ["test-d07"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D07_CLI"
            },           
            {
                "name": ["test-d08"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D08_CLI"
            },           
            {
                "name": ["test-d09"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D09_CLI"
            },              
            {
                "name": ["test-d10"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D10_CLI"
            },  
            {
                "name": ["test-d11"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D11_CLI"
            },              
            {
                "name": ["test-d13"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D13_CLI"
            },                                               
            {
                "name": ["test-d14"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D14_CLI"
            },     
            {
                "name": ["test-d15"],
                "cmdFile": "%s/../d2c/test/test_cases_device.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceTest_D15_CLI"
            },     
            
            #########################
            # Device group test cases              
            {
                "name": ["test-dg01"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG01_CLI"
            },      
            {
                "name": ["test-dg02"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG02_CLI"
            },                  
            {
                "name": ["test-dg03"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG03_CLI"
            },                  
            {
                "name": ["test-dg04"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG04_CLI"
            },                  
            {
                "name": ["test-dg05-long"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG05_CLI_long"
            },                  
            {
                "name": ["test-dg05-short"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG05_CLI_short"
            },
            {
                "name": ["test-dg06-short"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG06_CLI_short"
            },                  
            {
                "name": ["test-dg07-short"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG07_CLI_short"
            },                  
            {
                "name": ["test-dg08-short"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG08_CLI_short"
            },                  
            {
                "name": ["test-dg09-short"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG09_CLI_short"
            },                  
            {
                "name": ["test-dg10-short"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG10_CLI_short"
            },                  
            {
                "name": ["test-dg11-short"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG11_CLI_short"
            },          
            {
                "name": ["test-dg15-short"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG15_CLI_short"
            },         
            {
                "name": ["test-dg16-short"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG16_CLI_short"
            },         
            {
                "name": ["test-dg17-short"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG17_CLI_short"
            },         
            {
                "name": ["test-dg18-short"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG18_CLI_short"
            },         
            {
                "name": ["test-dg20"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG20_CLI"
            },      
            {
                "name": ["test-dg21"],
                "cmdFile": "%s/../d2c/test/test_cases_device_group.py" % (os.path.dirname(__file__)),
                "cmdClass": "DeviceGroupTest_DG21_CLI"
            },                  
        ]
    },    
]
