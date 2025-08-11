import logging
from typing import List

from fastapi import HTTPException, Request

import dtiot_d2c.cli.prfmanapi.config as CFG

from . import api_utils

log = logging.getLogger(__name__)


def init():
    pass

def handleRequest(req:Request, id:str=None,
                 ) -> None | dict | List[str]:
    
    api_utils.logRequest(req)

    try:

        return ReportJob.get(id, when=when, month_of_year=month_of_year, 
                           from_date=from_date, to_date=to_date)
        
    except Exception as ex:
        log.error(f"Could not query job objectg from db: {ex}.")
        raise HTTPException(status_code=500, detail=f"Internal error.")




