import json
import logging
import threading
import time

import requests

from . import html_utils as hutils
from . import utils

log = logging.getLogger(__name__)

class _CFG:
    dmoBasepath:str = "device-management-orchestrator" 
    minApiTokenValiditySecs:int = 10  # Min validity secs of an api token. If the left validity is 
                                      # is smaller the token is refreshed.

def cfg(**kwargs):
    global _CFG
    for (k, v) in kwargs.items():
        if hasattr(_CFG, k):
            setattr(_CFG, k, v)
        else:
            log.warning(f"Ignoring unknown configuration element {k}.")

class ApiToken:
    '''
    API token after successfull client authentication.
    '''
    def __init__(self, info:dict):
        '''
        info: 
            {
                "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJaS1U2QjVQNXQ2aTcwRzh0R2YwZEdsejBBVlN5cXhZYms5THRQN3N2cjBvIn0.eyJleHAiOjE3MDUzMTE5MjYsImlhdCI6MTcwNTMxMTYyNiwianRpIjoiOWRjODEyNmEtMGI2ZC00OTRkLWEwYzItY2YxMmY2ZTRhYTZlIiwiaXNzIjoiaHR0cHM6Ly9pYW0tYnItaW90Lm15aW90LWQuY29tL2F1dGgvcmVhbG1zL2lvdGh1YiIsInN1YiI6IjI2MjNiMmRjLTc2MmEtNGE4Mi1hMDZiLWEwZTgzNTNlMWRjOSIsInR5cCI6IkJlYXJlciIsImF6cCI6IjQ2M2VhOGEzLTQ0OGEtNDBhZC05MzRiLWYxMzYxNTgzOGQ2ZSIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsicm8lY29ubmVjdGlvbi1tYW5hZ2VtZW50LW9yY2hlc3RyYXRvciIsInJ3JWNvbm5lY3Rpb24tbWFuYWdlbWVudC1vcmNoZXN0cmF0b3IiLCJybyVkZXZpY2UtbWFuYWdlbWVudC1vcmNoZXN0cmF0b3IiLCJydyVkZXZpY2UtbWFuYWdlbWVudC1vcmNoZXN0cmF0b3IiXX0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsInRlbmFudHMiOlsiZW9zIl0sImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiY2xpZW50SG9zdCI6Ijc5LjIxMC4xODYuMTc5IiwiY2xpZW50SWQiOiI0NjNlYThhMy00NDhhLTQwYWQtOTM0Yi1mMTM2MTU4MzhkNmUiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzZXJ2aWNlLWFjY291bnQtNDYzZWE4YTMtNDQ4YS00MGFkLTkzNGItZjEzNjE1ODM4ZDZlIiwiY2xpZW50QWRkcmVzcyI6Ijc5LjIxMC4xODYuMTc5In0.GthxWKymbpRVN0UVVuYGHGykMMleIx1E512hpBLPyCM82sY1QJvTzqx-Zqd6XTlVlFTzueAAT5ybRVl63uQlNqQisdAqwkbwF4qMwEawCpoN3UnXlzVBnp0s9uF81UCDQOcGXbDilaySYviuxJicFTKMbpsKsCbAPJNKte2FJ-QqRTFgAx6_wDA5pVlm4aRUsm6KwYU6I9nl7rAfAEaFpQCw1tttxuh5jVqkE-uoUQbwfrhE8NegztILD6TAL3bmIs_c4sUP-1XkxiIdOy5Y7QrDb8E_ozo-inMoskkAsq5d62Du_1l1LIhxtbgPkF6ctSA8q0shyxR19Y_QCfUeOw",
                "expires_in": 300,
                "refresh_expires_in": 0,
                "token_type": "Bearer",
                "not-before-policy": 0,
                "scope": "profile email"
            }
        '''
        self._info = info
        self._tokenTime = time.time()

    @property
    def access_token(self):
        return self._info.get("access_token", None)

    @property
    def validity_secs(self):
        return self._info.get("expires_in", 0) - (time.time() - self._tokenTime)


class ApiClient:
    '''
    API client credentials.
    '''
    
    def __init__(self, api_url:str, origin:str, get_token_url:str, client_id:str, client_secret:str):
        self._api_url:str = api_url
        self._origin:str = origin 
        self._get_token_url:str = get_token_url
        self._client_id:str = client_id
        self._client_secret:str = client_secret
        self._apiToken:ApiToken = None
        self._refreshTokenLock = threading.Lock()

    @property
    def key(self):
        return f"{self._tenant_name}:{self._client_id}:{self._client_secret}"

    @property
    def origin(self):
        return self._origin
    
    @property
    def api_url(self):
        return self._api_url           

    @property
    def api_url_unstructured(self):
        '''
        This is a dirty hack to make out of the regular, structured, api url which contains as the last
        path element the CseId (tenant) an unstructured api url to access resources by its it and not
        by its name
        '''
        l = self.api_url.split("/")
        return "/".join(l[:-1]) + "/~/" + l[-1]
    
    @property
    def get_token_url(self):
        return self._get_token_url

    @property
    def client_id(self):
        return self._client_id
    
    @property
    def client_secret(self):
        return self._client_secret   

    @property
    def token(self) -> ApiToken:
        return self._apiToken

    @property
    def bearer_token(self) -> str:
        
        if not self._apiToken:
            self._apiToken = self.auth()

        # Refresh the token
        elif self._apiToken.validity_secs < _CFG.minApiTokenValiditySecs:
            self._refreshTokenLock.acquire()
            try:
                log.info(f"Refresh access token for {self._client_id} ...")
                self._apiToken = self.auth()
            except Exception as ex:
                log.error(f"{ex}")
            finally:
                self._refreshTokenLock.release()            

        return self._apiToken.access_token
    
    def auth(self) -> ApiToken:
        '''
        Performs API authentication and returns the ApiToke.
                
        curl --request POST "https://playground.spacegate.telekom.de/auth/realms/default/protocol/openid-connect/token" \
        --header 'Content-Type: application/x-www-form-urlencoded' \
        --header 'Accept: application/x-www-form-urlencoded, application/json' \
        --header 'uthorization: Basic t-iot-hub--aag7zrqole--056e86c6-8b22-4c7c-a4fa-be9451987feb 0ca42ee6-9c07-4081-a536-9c3ceec2ed80' \
        --header 'Authorization: Basic dC1pb3QtaHViLS1hYWc3enJxb2xlLS0wNTZlODZjNi04YjIyLTRjN2MtYTRmYS1iZTk0NTE5ODdmZWI6MGNhNDJlZTYtOWMwNy00MDgxLWE1MzYtOWMzY2VlYzJlZDgw' \
        --data 'grant_type=client_credentials' \

        '''
        url = self.get_token_url
        hutils.log_url(log.debug, "POST", url)

        headers = {
            "Content-Type" :"application/x-www-form-urlencoded",
            "Accept": "application/x-www-form-urlencoded, application/json",
            "Authorization": f"Basic {utils.to_basic_auth(self._client_id, self._client_secret)}"
        }
        hutils.log_headers(log.debug, headers)

        body = "grant_type=client_credentials"
        hutils.log_body(log.debug, body)
       
        response = requests.post(url=url, headers=headers, data=body)
        hutils.log_response(log.debug, response)          
        
        '''
        {
            "access_token":"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICItQ2oyakVyejN0b1d0Y1FZVWtzRFB3aGFXZHQyS3AteWpZMTduRjBXdjZvIn0.eyJleHAiOjE3NDIzODE2NzUsImlhdCI6MTc0MjM4MTM3NSwianRpIjoiZTM0MWJhZmMtM2Q1Yi00MmYyLWJmMmUtYzlkZDgwY2Y5ZjMyIiwiaXNzIjoiaHR0cHM6Ly9wbGF5Z3JvdW5kLnNwYWNlZ2F0ZS50ZWxla29tLmRlL2F1dGgvcmVhbG1zL2RlZmF1bHQiLCJzdWIiOiJmOGIyODgxZi00MTQ1LTQ3ZmYtYTBiZC05M2ExYTBkOWMxZmQiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ0LWlvdC1odWItLWFhZzd6cnFvbGUtLTA1NmU4NmM2LThiMjItNGM3Yy1hNGZhLWJlOTQ1MTk4N2ZlYiIsImFjciI6IjEiLCJzY29wZSI6ImNsaWVudC1vcmlnaW4gcHJvZmlsZSBlbWFpbCIsImNsaWVudEhvc3QiOiIxMDAuMTAyLjE0NC44NSIsImNsaWVudElkIjoidC1pb3QtaHViLS1hYWc3enJxb2xlLS0wNTZlODZjNi04YjIyLTRjN2MtYTRmYS1iZTk0NTE5ODdmZWIiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsIm9yaWdpblpvbmUiOiJzcGFjZSIsInByZWZlcnJlZF91c2VybmFtZSI6InNlcnZpY2UtYWNjb3VudC10LWlvdC1odWItLWFhZzd6cnFvbGUtLTA1NmU4NmM2LThiMjItNGM3Yy1hNGZhLWJlOTQ1MTk4N2ZlYiIsImNsaWVudEFkZHJlc3MiOiIxMDAuMTAyLjE0NC44NSIsIm9yaWdpblN0YXJnYXRlIjoiaHR0cHM6Ly9wbGF5Z3JvdW5kLnNwYWNlZ2F0ZS50ZWxla29tLmRlIn0.AZByWXAthRPPy0O-c07_gHdvzHILZYEw1AFJlejBKL2ZxeL2YIZyDaj15FNk29cQWT8gK5CizsODKUqA2MPV47s50PtbH0AOKnFe203zgxrsOxAwUiRa_y0TKga9cIVjFN8llqDyJUCmCAMOIKdLtvul1H_k8sHx3BTjBpbQBhaNkMOugn1yHVwNQVgyXkiThBypPImJImiDu2zGqui8WLZGGi2tAHIeDhjZq7g1ane0aUUkzWCcXh_fOk9ecch0B9GBmk5RoDnbL_Lo51cZWk2zRjr2P7TdQQzG4ZZ8kO-fsw_Wz6rePFKQcGhFF44FikIM-Knf8xJFENNWIPCRqQ",
            "expires_in":300,
            "refresh_expires_in":0,"token_type":
            "Bearer","not-before-policy":0,
            "scope":"client-origin profile email"
        }                
        '''       
       
        if not response.ok:
            response.raise_for_status()

        d = json.loads(response.content)

        self._apiToken = ApiToken(d)        

        return self._apiToken

class _ApiClients:
    '''
    Container to managbe APIClient instances.
    '''
    def __init__(self):
        self._clients = {}
        
    def addClient(self, client:ApiClient):
        '''
        Add a client to the container.
        '''
        self._clients[client.key] = client
        return client
        
    def getClient(self, key:str) -> ApiClient:
        '''
        Returns a client instance by its key.
        
        :key:str: The key of the client as returned by the clients'
                  key property.
        '''
        return self._clients.get(key, None)

# Create the singelton instance of the ApiClients container
ApiClients = _ApiClients()
    
    