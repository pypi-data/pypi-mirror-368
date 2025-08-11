import json
import logging
import time
import uuid
from datetime import datetime
from typing import List

import requests

from dtiot_d2c.dmo import ApiClient
from dtiot_d2c.dmo import html_utils as hutils
from dtiot_d2c.dmo import onem2m_utils as onem2m_utils
from dtiot_d2c.dmo import utils as utils
from dtiot_d2c.dmo.consts import *

log = logging.getLogger(__name__)

DMO_BASEPATH="api-gw/device-management-orchestrator"

################################################################################
# General Resource related Functions
################################################################################
def _add_labels_to_request_body(dest:dict, **kwargs)->list([str]):
    '''
    If the "labels" parameter is in the kwargs than it is translated from a dictionary
    into an array of strings "<key>:<value>" and added to the element "lbl" of the 
    destonation dictionary.
    '''
    labels = kwargs.get("labels", None)
    if labels:
        if type(labels) == str:
            labels = json.loads(labels)                
            
        a = []
        for (k, v) in labels.items():
            a.append(f"{k}:{v}")            
        if len(a) > 0:
            dest["lbl"] = a
    return labels

@utils.profile(log_func=log.info, log_prefix="dmo-profile")
def _get_resources(api_client:ApiClient,                # Client connection definition.
                   origin:str=None,                     # Value for X-M2M-Origin header 
                   resourceType:str=None,               # Resource type of the objects to get. Supported types are: TYs (see above).
                   resourceId:str=None,                 # Id of the resource                   
                   resourceName:str=None,               # Name of a resource which details shall be get. 
                                                        # If not defined the root CSEBase is used.
                   resultContentIndocator:str=None,     # Result content indicator. Supported types are RCIs (see above).
                   limit:int=1000000000,                # Max number of objects to return.
                   offset:int=0,
                   url_suffix:str=None,                 # Path suffix which is appended to the url path.
                   attribute_filters:list=None,
                   json_response_filter:str=None,    
                   use_unstructured_path:bool=False     # If set to True the unstructured path is used
                  ) -> dict:
    '''
    Gets objects of a specific resource type.
    '''
    log.debug("=> _get_resources()")
    log.debug(f"   origin:               {origin}")    
    log.debug(f"   rt:                   {resourceType}")    
    log.debug(f"   ri:                   {resourceId}")    
    log.debug(f"   rn:                   {resourceName}")    
    log.debug(f"   rci:                  {resultContentIndocator}")    
    log.debug(f"   limit:                {limit}")    
    log.debug(f"   offset:               {offset}")    
    log.debug(f"   url_suffix:           {url_suffix}")    
    log.debug(f"   attribute_filters:    {attribute_filters}")    
    log.debug(f"   json_response_filter: {limit}")    
    log.debug(f"   use_unstructured_path: {use_unstructured_path}")    
    log.debug("")    

    if resourceId or use_unstructured_path:
        url = f"{api_client.api_url_unstructured}"
    else:
        url = f"{api_client.api_url}"
        
    if url_suffix:
        url += f"/{url_suffix}"
        
    if resourceId:
        url += f"/{resourceId}"
    elif resourceName:
        url += f"/{resourceName}"

    rcn = RCIs.get(resultContentIndocator, 4)
    url += f"?rcn={rcn}"

    #if not resourceName and not resourceId:
    #    url += f"&limit={limit}&offset={offset}"
    if limit > 0:
        url += f"&limit={limit}&offset={offset}"
        
    if attribute_filters:
        url += f"&{'&'.join(attribute_filters)}"

    #url += f'&fwr={{"cra":"20250610T085823"}}'
    #/{resourcePath}?fwr={"cra":"20230101T000000"}

    ty = None
    # We only deal with the resource type if the no resource name is defined.
    # If a resource name is defined we force the resource type to be None
    if resourceType:
        # ty = TYs.get(resourceType, None)
        # if not ty:
        #     raise Exception(f"Unknown resource type {resourceType}")
        # url += f"&ty={ty}"

        if not resourceName:
            ty = TYs.get(resourceType, None)
            if not ty:
                raise Exception(f"Unknown resource type {resourceType}")
            url += f"&ty={ty}"
        else:
            #log.warning(f"Resource type {resourceType} ignored because resource name defined.")
            resourceType = None


    #/nodes?fc={"createdAfter":"2023-10-01T00:00:00Z"} HTTP
    #url += f'&"creationTime":"2025-06-06T17:11:28"'
    hutils.log_url(log.debug, "GET", url)

    headers = {
        "Content-Type"  : "application/json",
        "Accept"        : "application/json",
        "Authorization" : f"Bearer {api_client.bearer_token}",
        "X-M2M-Origin"  : f"C{origin or api_client.origin}",        
        "X-M2M-RI"      : f"{str(uuid.uuid1())}"
    }
    hutils.log_headers(log.debug, headers)

    body = None
    hutils.log_body(log.debug, body)
    
    response = requests.get(url=url, headers=headers, json=body)
    hutils.log_response(log.debug, response)    

    if not response.ok:
        if response.status_code == 404:
            #log.error(response.content)
            return None
        else:
            try:
                log.error(response.content)
            except:
                pass
            response.raise_for_status()
    
    d = json.loads(response.content)
    #log.debug(json.dumps(d, indent=4))

    if json_response_filter:
        if not resourceName:
            d = utils.getValueFromDict(d, json_response_filter, {})
        else:
            d = utils.getValueFromDict(d, json_response_filter, {})
    
    # If a named resource shall be get
    if resourceName or resourceId:
        if len(d.keys()) == 1:
            for (k, o) in d.items():
                return o
        else:
            return d    

    jsonFilter = TYs_JSON_FILTERS.get(resourceType, None)
    if jsonFilter:
        return utils.getValueFromDict(d, jsonFilter, {})
    
    return d
            
    # if resourceType == 'cb':
    #     return d.get("m2m:cb", {})
    # elif resourceType:
    #     return d.get("m2m:cb", {}).get(f"m2m:{resourceType}",[])
    # else:
    #     if len(d.keys()) == 1:
    #         for (k, o) in d.items():
    #             return o
    #     else:
    #         return d    
        
def get_resources(api_client:ApiClient,                # Client connection definition.
                  origin:str=None,                     # Value for X-M2M-Origin header 
                  resourceType:str=None,               # Resource type of the objects to get. Supported types are: TYs (see above).
                  resourceId:str=None,                 # Id of the resource
                  resourceName:str=None,               # Name of a resource which details shall be get. 
                                                       # If not defined the root CSEBase is used.
                  resultContentIndocator:str=None,     # Result content indicator. Supported types are RCIs (see above).
                  limit:int=1000000000,                # Max number of objects to return.
                  offset:int=0,
                  select:str=None,                     # Comma separated list of element names which shall be selected.
                  format:str="CSV",                    # Output format. Possible values are CSV and JSON
                  url_suffix:str=None,                 # Path suffix which is appended to the url path.        
                  json_response_filter:str=None,     
                  attribute_filters:list=None,   
                  use_unstructured_path:bool=False     # If set to True the unstructured path is used
                 ) -> dict:        

    log.debug("=> get_resources()")
    log.debug(f"   origin:                {origin}")    
    log.debug(f"   rt:                    {resourceType}")    
    log.debug(f"   ri:                    {resourceId}")    
    log.debug(f"   rn:                    {resourceName}")    
    log.debug(f"   rci:                   {resultContentIndocator}")    
    log.debug(f"   limit:                 {limit}")    
    log.debug(f"   offset:                {offset}")    
    log.debug(f"   url_suffix:            {url_suffix}")    
    log.debug(f"   attribute_filters:     {attribute_filters}")    
    log.debug(f"   json_response_filter:  {limit}")    
    log.debug(f"   use_unstructured_path: {use_unstructured_path}")    
    
    log.debug("")    

    o = _get_resources(api_client=api_client, 
                       origin=origin,
                       resourceType=resourceType, 
                       resourceId=resourceId,
                       resourceName=resourceName,
                       resultContentIndocator=resultContentIndocator, 
                       limit=limit, 
                       offset=offset,
                       url_suffix=url_suffix,
                       json_response_filter=json_response_filter,
                       attribute_filters=attribute_filters,
                       use_unstructured_path=use_unstructured_path)
    if not select:
        return o

    selectFields = utils.splitString(select, ",")

    ret = []
    if type(o) != list:
        o = [o]

    if not format:
        format = "CSV"
        
    if format.upper() == "CSV":
        # for i in o:
        #     a = []
        #     for select_field in selectFields:
        #         v = utils.get_value_from_dict_3(i, select_field, default="", sepChar=".")
        #         a.append(str(v))
        #     ret.append(a)
        # return ret
        for i in o:
            a = []
            for s in selectFields:
                if s in i.keys():
                    v=i[s]
                    if type(v) in [dict, list, tuple]:
                        v = json.dumps(v)
                    else:
                        v = str(v)
                    a.append(v)
            ret.append(a)
        return ret
        # for i in o:
        #     a = []
        #     for s in selectFields:
        #         if s in i.keys():
        #             a.append(str(i[s]))
        #     ret.append(a)
        # return ret

    elif format.upper() == "JSON":
        for i in o:
            if type(i) != dict:
                continue
            d = {}
            for s in selectFields:
                if s in i.keys():
                    d[s] = i[s]
            ret.append(d)
            
        if resourceName and ret:
            return ret[0]
        else:
            return ret            
    else:
        raise Exception(f"Unsupported format {format}. JSON or CSV required.") 

@utils.profile(log_func=log.info, log_prefix="dmo-profile")
def add_resource(api_client:ApiClient, 
                 origin:str=None,             # Value for X-M2M-Origin header                  
                 r_type:str=None,             # resource type
                 r_name:str=None,             # resource name
                 onem2m_body:dict=None,       # Body of the http request
                 **kwargs             
                ) -> dict:
    '''
    Adds a resource object to the tenant or another resource.
    '''
    url = f"{api_client.api_url}"
    if r_name:
        url += f"/{r_name}"

    hutils.log_url(log.debug, "POST", url)        

    headers = {
        "Content-Type"  : f"application/json;ty={TYs[r_type]}",
        "Accept"        : "application/json",
        "Authorization" : f"Bearer {api_client.bearer_token}",
        "X-M2M-Origin"  : f"C{origin or api_client.origin}",        
        "X-M2M-RI"      : f"{str(uuid.uuid1())}"
    }
    hutils.log_headers(log.debug, headers)            

    log.debug(f"BODY: {onem2m_body}")

    # if len(resourceNames) == 1:
    #     headers["X-M2M-Origin"] = f"C{apiClient.client_rn}"
    # else:
    #     headers["X-M2M-Origin"] = "/".join(resourceNames[0:-1])
    #headers["X-M2M-Origin"] = f"C{apiClient.client_rn}"
    
    response = requests.post(url=url, headers=headers, json=onem2m_body)   
    hutils.log_response(log.debug, response)    
    
    if not response.ok:
        try:
            log.error(response.content)
        except:
            pass
        response.raise_for_status()
    
    d = json.loads(response.content)

    return d

@utils.profile(log_func=log.info, log_prefix="dmo-profile")
def delete_resource(api_client:ApiClient,  
                    origin:str=None,       # Value for X-M2M-Origin header 
                    name:str=None,          # Name of the resource object to delete.
                    id:str=None
                   ):
    if id:
        url = f"{api_client.api_url_unstructured}/{id}"
    else:
        url = f"{api_client.api_url}/{name}"

    hutils.log_url(log.debug, "DELETE", url)        

    headers = {
        "Content-Type"  : f"application/json",
        "Accept"        : "application/json",
        "Authorization" : f"Bearer {api_client.bearer_token}",
        "X-M2M-Origin"  : f"C{origin or api_client.origin}",        
        "X-M2M-RI"      : f"{str(uuid.uuid1())}"
    }
    hutils.log_headers(log.debug, headers)            

    response = requests.delete(url=url, headers=headers)
    hutils.log_response(log.debug, response)    
    
    if not response.ok:
        try:
            log.error(response.content)
        except:
            pass
        response.raise_for_status()

    return None

@utils.profile(log_func=log.info, log_prefix="dmo-profile")
def update_labels(api_client:ApiClient,   # Client connection definition.
                 origin:str,             # Value for X-M2M-Origin header                     
                 name:str=None,          # Name of the resource object to update.
                 id:str=None,
                 labels:dict=None, 
                ) -> dict:

    if not id and not name:
        raise Exception("Cannot update labels. No object name or id defined.")
    
    if not labels:
        labels = {}

    loaded_onem2m = get_resources(api_client, origin=origin, resourceId=id, resourceName=name)
    if not loaded_onem2m:
        raise Exception(f"Could not load object {id or name} to integrate labels")

    type_id = loaded_onem2m.get("ty")
    ns_prefix = NSPREFIXs_BY_RESOURCE_TYPE_ID.get(type_id, None)
    if not ns_prefix:
        raise Exception(f"Resource type {type_id} not support by update_labels() function.")
    

    loaded_lbl = loaded_onem2m.get("lbl", [])
    input_lbl = onem2m_utils.convert_dict_to_onem2m_labels(labels)

    if loaded_lbl:
        integrated_lbl = utils.integrate_lists(loaded_lbl, input_lbl)

    body = {
        ns_prefix: {
            "lbl" : integrated_lbl
        }
    }        

    if id:
        url = f"{api_client.api_url_unstructured}/{id}"
    else:
        url = f"{api_client.api_url}/{name}"

    hutils.log_url(log.debug, "PUT", url)        

    headers = {
        "Content-Type"  : f"application/json",
        "Accept"        : "application/json",
        "Authorization" : f"Bearer {api_client.bearer_token}",
        "X-M2M-Origin"  : f"C{origin or api_client.origin}",        
        "X-M2M-RI"      : f"{str(uuid.uuid1())}"
    }
    hutils.log_headers(log.debug, headers)            

    hutils.log_body(log.debug, body)
    
    response = requests.put(url=url, headers=headers, json=body)
    hutils.log_response(log.debug, response)    
    
    if not response.ok:
        try:
            log.error(response.content)
        except:
            pass
        response.raise_for_status()
    
    d = json.loads(response.content)

    return d

@utils.profile(log_func=log.info, log_prefix="dmo-profile")
def update_resource(api_client:ApiClient,   # Client connection definition.
                    origin:str,             # Value for X-M2M-Origin header                     
                    name:str=None,          # Name of the resource object to update.
                    id:str=None,
                    #labels:dict=None, 
                    onem2m_body:dict=None,
                  ) -> dict:

    # If labels and onem2m_body is defined create an error only one of both can be updated
    # if labels and onem2m_body:
    #     raise Exception("Cannot update resource object with both onem2m body and labels. Use only one of both.")
    # elif not labels and not onem2m_body:
    #     raise Exception("Cannot update resource object. Wether onem2m body or labels required.")
    if not id and not name:
        raise Exception("Cannot update resource object. Wether name or id required.")
                    
    # If labels have been defined, update labels by integrating current labels with new ones.
    # if labels:
    #     return update_labels(api_client, origin=origin, name=name, id=id, labels=labels)

    # Run a norm update by onem2m body        
    if id:
        url = f"{api_client.api_url_unstructured}/{id}"
    else:
        url = f"{api_client.api_url}/{name}"

    hutils.log_url(log.debug, "PUT", url)        

    headers = {
        "Content-Type"  : f"application/json",
        "Accept"        : "application/json",
        "Authorization" : f"Bearer {api_client.bearer_token}",
        "X-M2M-Origin"  : f"C{origin or api_client.origin}",        
        "X-M2M-RI"      : f"{str(uuid.uuid1())}"
    }
    hutils.log_headers(log.debug, headers)            

    hutils.log_body(log.debug, onem2m_body)
    
    response = requests.put(url=url, headers=headers, json=onem2m_body)
    hutils.log_response(log.debug, response)    
    
    if not response.ok:
        try:
            log.error(response.content)
        except:
            pass
        response.raise_for_status()
    
    d = json.loads(response.content)

    return d

@utils.profile(log_func=log.info, log_prefix="dmo-profile")
def update_resource_labels(api_client:ApiClient,   # Client connection definition.
                           origin:str,             # Value for X-M2M-Origin header   
                           r_type:str,             # Type of the resource object
                           r_name:str,             # Name of the resource object
                           labels:dict,            # Labels dictionary
                          ) -> dict:
    '''
    Updates the labels of a resource object.
    '''
    url = f"{api_client.api_url}/{r_name}?rcn={RCIs['return-all']}"
    hutils.log_url(log.debug, "PUT", url)        

    headers = {
        "Content-Type"  : f"application/json",
        "Accept"        : "application/json",
        "Authorization" : f"Bearer {api_client.bearer_token}",
        "X-M2M-Origin"  : f"C{origin or api_client.origin}",        
        "X-M2M-RI"      : f"{str(uuid.uuid1())}"
    }
    hutils.log_headers(log.debug, headers)            

    body = {
        f"m2m:{r_type}": {
            "lbl":onem2m_utils.convert_dict_to_onem2m_labels(labels)
        }
    }
    hutils.log_body(log.debug, body)

    response = requests.put(url=url, headers=headers, json=body)
    hutils.log_response(log.debug, response)    
    
    if not response.ok:
        try:
            log.error(response.content)
        except:
            pass
        response.raise_for_status()
    
    d = json.loads(response.content)

    return d

################################################################################
################################################################################
################################################################################
################################################################################

def old__getResources(apiClient:ApiClient,                 # Client connection definition.
                  resourceType:str=None,               # Resource type of the objects to get. Supported types are: TYs (see above).
                  resourceName:str=None,               # Name of a resource which details shall be get. 
                                                       # If not defined the root CSEBase is used.
                  resultContentIndocator:str=None,     # Result content indicator. Supported types are RCIs (see above).
                  limit:int=1000000000,                # Max number of objects to return.
                  origin:str=None                      # Originitor object of this request. If not defined the default from 
                                                       # API client object is used.
                  ) -> dict:
    '''
    Gets objects of a specific resource type.
    '''

    ###
    # Build the URL
    url = f"https://{apiClient.host}/{DMO_BASEPATH}/{apiClient.api_version}/{apiClient.tenant_name}"
    
    if resourceName:
        url += f"/{resourceName}"

    rcn = RCIs.get(resultContentIndocator, 4)
    url += f"?rcn={rcn}&limit={limit}"

    ty = None
    # We only deal with the resource type if the no resource name is defined.
    # If a resource name is defined we force the resource type to be None
    if resourceType:
        if not resourceName:
            ty = TYs.get(resourceType, None)
            if not ty:
                raise Exception(f"Unknown resource type {resourceType}")
            url += f"?&ty={ty}"
        else:
            log.warn(f"Resource type {resourceType} ignored because resource name defined.")
            resourceType = None

    log.debug(f"POST {url}")

    headers = {
        "Content-Type"  : "application/json",
        "Accept"        : "application/json",
        "Authorization" : f"Bearer {apiClient.bearer_token}",
        "X-M2M-Origin"  : f"C{apiClient.client_rn}" if not origin else origin,
        "X-M2M-RI"      : f"dmo_{str(time.time())}"
    }
    log.debug(f"HEADER: {headers}")        

    body = None
    hutils.log_body(log.debug, body)
    
    response = requests.get(url=url, headers=headers, json=body)
    
    if not response.ok:
        try:
            log.error(response.content)
        except:
            pass
        
        response.raise_for_status()
    
    d = json.loads(response.content)
    log.debug(json.dumps(d, indent=4))
    
    # If a named resource shall be get
    if resourceName:
        if len(d.keys()) == 1:
            for (k, o) in d.items():
                return o
        else:
            return d    
        
    if resourceType == 'cb':
        return d.get("m2m:cb", {})
    elif resourceType:
        return d.get("m2m:cb", {}).get(f"m2m:{resourceType}",[])
    else:
        if len(d.keys()) == 1:
            for (k, o) in d.items():
                return o
        else:
            return d    
        
def old_getResources(apiClient:ApiClient,                  # Client connection definition.
                 resourceType:str,                     # Resource type of the objects to get. Supported types are: TYs (see above).
                 resourceName:str=None,                # Name of a resource which details shall be get. 
                                                       # If not defined the root CSEBase is used.
                 resultContentIndocator:str=None,      # Result content indicator. Supported types are RCIs (see above).
                 limit:int=1000000000,                 # Max number of objects to return.
                 origin:str=None,                      # Originitor object of this request. If not defined the default from
                                                       # API client object is used.
                 select:str=None,                      # Comma separated list of element names which shall be selected.
                 format:str="CSV"                      # Output format. Possible values are CSV and JSON
                 ) -> dict:        

    o = old__getResources(apiClient=apiClient, 
                      resourceType=resourceType, 
                      resourceName=resourceName,
                      resultContentIndocator=resultContentIndocator, 
                      limit=limit, origin=origin)

    if not select:
        return o

    selectFields = utils.splitString(select, ",")

    ret = []
    if type(o) != list:
        o = [o]

    if not format:
        format = "CSV"
        
    if format.upper() == "CSV":

        for i in o:
            a = []
            for s in selectFields:
                if s in i.keys():
                    a.append(str(i[s]))
            ret.append(a)

    elif format.upper() == "JSON":
        for i in o:
            if type(i) != dict:
                continue
            d = {}
            for s in selectFields:
                if s in i.keys():
                    d[s] = i[s]
            ret.append(d)
    else:
        raise Exception(f"Unsupported format {format}. JSON or CSV required.") 
    
    return ret







def addMessageContainer(apiClient:ApiClient,     # Client connection definition.
                        resourceName:str,        # Name of the object to which the container shall be added.
                        containerName:str,       # Name of the container.
                        maxByteSize:int=10000,   # Max. number of bytes in a message.
                        maxNrOfInstaces:int=10,  # Max. number of stored messages.
                        **kwargs                 # "labels":dict - Dictionary of labels. Labels are translated into an 
                                                 #                 array of strings of the form "<key>:<value>"
                       )->dict:
    '''
    Adds a container of uplink messages to a resource object.
    '''
    url = f"https://{apiClient.host}/{DMO_BASEPATH}/{apiClient.api_version}/{apiClient.tenant_name}/{resourceName}"
    log.debug(f"PUT {url}")

    headers = {
        "Content-Type"  : f"application/json;ty=3",
        "Accept"        : "application/json",
        "Authorization" : f"Bearer {apiClient.bearer_token}",
        "X-M2M-Origin"  : f"C{resourceName}", #"X-M2M-Origin"  : f"C{apiClient.client_rn}",
        "X-M2M-RI"      : f"dmo_{str(time.time())}"
    }
    log.debug(f"HEADER: {headers}")        

    # Build the body
    body = {
        "container": {
            "maxByteSize": maxByteSize,
            "maxNrOfInstances": maxNrOfInstaces,
            "resourceName": containerName
        }
    }
    
    # labels
    _add_labels_to_request_body(body["container"], **kwargs)    

    hutils.log_body(log.debug, body)

    response = requests.post(url=url, headers=headers, json=body)
    
    if not response.ok:
        try:
            log.error(response.content)
        except:
            pass
        response.raise_for_status()
    
    d = json.loads(response.content)

    return d

def addSubscription(apiClient:ApiClient,     # Client connection definition.
                    resourceName:str,        # Name of the object to which the subscription shall be added.
                    subscriptionName:str,    # Name of the subscription
                    notificationUrl:str,     # URL to which the events shall be forwarded.
                    notificationContentType:str="all", # Content type of the notification. Siehe NCTs oben
                    eventNotificationCriterias:list([str])=["u","d","cc", "dc"], # Event notififcation criterias
                    **kwargs                 # "labels":dict - Dictionary of labels. Labels are translated into an 
                                             #                 array of strings of the form "<key>:<value>"
                                             # "pendingNotification":str - Defines how to handle pending notifiations.
                                             #                             possible valures are defined in PNs.
                   ) -> dict:
    '''
    Adds a subscription to a resource object.
    '''
    url = f"https://{apiClient.host}/{DMO_BASEPATH}/{apiClient.api_version}/{apiClient.tenant_name}/{resourceName}"
    log.debug(f"PUT {url}")

    headers = {
        "Content-Type"  : f"application/json;ty=23",
        "Accept"        : "application/json",
        "Authorization" : f"Bearer {apiClient.bearer_token}",
        "X-M2M-Origin"  : f"C{apiClient.client_rn}", #f"C{resourceName}", #"X-M2M-Origin"  : 
        "X-M2M-RI"      : f"dmo_{str(time.time())}"
    }
    log.debug(f"HEADER: {headers}")        

    # Build the list of event notification criterias
    encs = []
    if eventNotificationCriterias:
        for s in eventNotificationCriterias:
            encs.append(ENCs.get(s))            

    ###
    # Build the body
    body = {
        "subscription": {
            "rn":  subscriptionName,
            "nu":  [notificationUrl],
            "nct": NCTs.get(notificationContentType),
            "enc": {
                "net": encs
            }
        }
    }

    # pendingNotification    
    pn = kwargs.get("pendingNotification", None)
    if pn:
        body["subscription"]["pn"] = PNs.get(pn)

    # labels
    _add_labels_to_request_body(body["subscription"], **kwargs)

    hutils.log_body(log.debug, body)

    ###
    # Post the request 
    response = requests.post(url=url, headers=headers, json=body)
    
    if not response.ok:
        try:
            log.error(response.content)
        except:
            pass
        response.raise_for_status()
    
    d = json.loads(response.content)

    return d



