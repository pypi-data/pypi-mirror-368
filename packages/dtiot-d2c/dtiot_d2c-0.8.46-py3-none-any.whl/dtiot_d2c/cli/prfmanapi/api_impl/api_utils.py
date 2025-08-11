#!/usr/bin/env python3

import json
from fastapi import Request

import logging
log = logging.getLogger(__name__)

def copyHeaders(headers, namesToLower=False):
    ret = {}
    for k in headers.keys():
        if namesToLower:
            ret[k.lower()] = headers[k]
        else:
            ret[k] = headers[k]
    return ret

def logRequest(request:Request, body=None):
    log.debug(">>> HEADER")
    for h in request.headers.keys():
        log.debug("%s : %s" % (h, request.headers[h]))
    log.debug("")
    for qp in request.query_params.keys():
        log.debug("%s : %s" % (qp, request.query_params[qp]))

    if body:
        log.debug("")
        log.debug(">>> BODY")
        if type(body) == dict:
            log.debug(json.dumps(body, indent=4))
        elif type(body) == str:
            log.debug(body)
        else:
            log.debug(str(body))
    log.debug(">>>")

