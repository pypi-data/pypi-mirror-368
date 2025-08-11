from fastapi import Request, HTTPException

from . import api_utils
import config as CFG
from iam import TokenInfo
from report_job import ReportJob
from reports.device_report import DeviceReportJob, DeviceReport

import logging
log = logging.getLogger(__name__)


def init():
    pass

def handleRequest(token_info:TokenInfo, req:Request, 
                  tenant_id:int, 
                  when:str=None, 
                  month_of_year:str=None, 
                  from_date:str=None, 
                  to_date:str=None
                ) -> ReportJob:
    api_utils.logRequest(req)

    try:
        drj =DeviceReportJob(tenant_id = tenant_id,
                            when=when, 
                            month_of_year=month_of_year,
                            from_date=from_date, 
                            to_date=to_date)

        drj_thread = DeviceReport(report_job=drj)
        drj_thread.start()
        return drj

    except Exception as ex:
        log.error(f"Could not create device report job: {ex}.")
        raise HTTPException(status_code=500, detail=f"Internal error.")




