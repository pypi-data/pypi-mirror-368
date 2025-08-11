import json
import logging
import uuid
from datetime import datetime

import requests

import dtiot_d2c.dmo as dmo
from dtiot_d2c.dmo import ApiClient

from . import html_utils as hutils

log = logging.getLogger(__name__)

def _build_timestamp_name(prefix:str):
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    return f"{prefix}{ts}"
   
def create_request(api_client:ApiClient, # Client connection definition.
                   origin:str=None,      # Value for X-M2M-Origin header 
                   **kwargs              # Elements of the provisioning data which are placed
                                         # into the dictionary "requestList" of the provisoning 
                                         # request
                  ):     
    '''
    POST {{API_URL}}/device-management-orchestrator/v3/{{TENANT}}/device-provisioning/request HTTP/2
    Accept: application/json
    Content-Type: application/json;ty=28
    X-M2M-Origin: CTestApp
    fullName: true
    X-M2M-RI: 123
    Authorization: Bearer {{ACCESS_TOKEN}}

    {
        "dtiot:noPRt": {
            "cnd": "com.telekom.iot.orchestrator.nodeProvisioningRequest",
            "rn": "myProvisioningRequest01",
            "operation": 1,
            "requestList": [
                {
                    "nodeID" : "urn:gsma:imei:3519...88011",
                    "nodeResourceName" : "sensor001",
                    "ICCID" : "898...20111",
                    "profile" : "SCS-lwM2M",
                    "nodeCredentials": ["psk-id:test@test.com","psk:test123"],
                    "ndvi": {
                        "rn": "deviceInfo2055",
                        "mgd": 1007,
                        "man": "evel-corp",
                        "dty": "world-destructor",
                        "mod": "WD-15",
                        "dlb": "some:label",
                        "dc": "it destroys everything"
                    },
                }
            ]
        }
    }
    '''    
    url = f"{api_client.api_url}/device-provisioning/request"
    hutils.log_url(log.debug, "POST", url)

    headers = {
        "Content-Type"  : f"application/json;ty={dmo.TYs['fcn']}",
        "Accept"        : "application/json",
        "Authorization" : f"Bearer {api_client.bearer_token}",
        "X-M2M-Origin"  : f"C{origin or api_client.origin}",        
        "X-M2M-RI"      : f"{str(uuid.uuid1())}",
        "fullName"      : "true",
    }
    hutils.log_headers(log.debug, headers)

    body = {
        "dtiot:noPRt": {
            "cnd": "com.telekom.iot.orchestrator.nodeProvisioningRequest",
            "rn": _build_timestamp_name("device_provisioning_request_"),
            "operation": dmo.DEVPROV_OPs["create"],
            "requestList": []
        }
    }

    # Build and add the request data to the provisioning request
    requestList = {}
    for (key, value) in kwargs.items():
        requestList[key] = value
    body["dtiot:noPRt"]["requestList"].append(requestList)
        
    hutils.log_body(log.debug, body)
    
    response = requests.post(url=url, headers=headers, json=body)
    hutils.log_response(log.debug, response)    
    
    if not response.ok:
        try:
            log.error(response.content)
        except:
            pass
        response.raise_for_status()
    
    d = json.loads(response.content)

    return d

def get_requests(api_client:ApiClient, # Client connection definition.
                origin:str=None,      # Value for X-M2M-Origin header 
                name:str=None,
                id:str=None,
                select:str=None,
                format:str=None,
                attribute_filters:list=None,
               )->dict:
    return dmo.get_resources(api_client, 
                             origin=origin,
                             resourceId=id,
                             resourceName=name, 
                             resultContentIndocator=dmo.RCIs["attributes-and-children"],
                             select=select,
                             format=format,
                             url_suffix="device-provisioning/request",
                             json_response_filter="m2m:cnt.dtiot:noPRt",
                             attribute_filters=attribute_filters)    
    
def get_responses(api_client:ApiClient, # Client connection definition.
                  origin:str=None,      # Value for X-M2M-Origin header 
                  name:str=None,
                  id:str=None,
                  select:str=None,
                  format:str=None,
                  attribute_filters:list=None,
                 )->dict:
    
    return dmo.get_resources(api_client, 
                             origin=origin,
                             resourceId=id,
                             resourceName=name, 
                             resultContentIndocator=dmo.RCIs["attributes-and-children"],
                             select=select,
                             format=format,
                             url_suffix="device-provisioning/response",
                             json_response_filter="flexContainer", #"m2m:cnt.dtiot:prRRe",
                             attribute_filters=attribute_filters)
