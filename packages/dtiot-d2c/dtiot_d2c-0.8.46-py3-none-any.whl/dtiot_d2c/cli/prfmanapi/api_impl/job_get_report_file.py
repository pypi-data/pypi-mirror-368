from fastapi import Request, HTTPException

from . import api_utils
import config as CFG
from iam import TokenInfo
from report_job import ReportJob

import logging
log = logging.getLogger(__name__)


def init():
    pass

def handleRequest(token_info:TokenInfo, req:Request, 
                  id:int
                ) -> str:
    api_utils.logRequest(req)

    try:

        report_filepath = ReportJob.download_report_file(id, CFG.JobCfg["downloadDir"])
        return report_filepath

    except Exception as ex:
        log.error(f"Could not download report file from db for job {id}: {ex}.")
        raise HTTPException(status_code=500, detail=f"Internal error.")




