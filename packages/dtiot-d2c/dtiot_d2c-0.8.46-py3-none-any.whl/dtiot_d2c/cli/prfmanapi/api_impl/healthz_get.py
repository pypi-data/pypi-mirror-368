from fastapi import Request
from . import api_utils

from  .datamodel import HealthzResponse

import logging
log = logging.getLogger(__name__)

def init():
    '''
    Initializes the module
    '''
    pass

def handleRequest(request:Request):
    api_utils.logRequest(request)
    return HealthzResponse(message = "OK")

