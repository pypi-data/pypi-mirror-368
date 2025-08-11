#!/usr/bin/env python3

import json
import logging
import traceback
from typing import List

import uvicorn
from fastapi import (APIRouter, Body, Depends, FastAPI, Header, HTTPException,
                     Path, Query, Request, Response, Security, status)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security.api_key import APIKeyHeader

import dtiot_d2c.cli.prfmanapi.api_impl.healthz_get as healthz_get
import dtiot_d2c.cli.prfmanapi.api_impl.profile_get as profile_get
import dtiot_d2c.cli.prfmanapi.config as CFG
from dtiot_d2c.cli.prfmanapi.api_impl.datamodel import HealthzResponse

log = logging.getLogger(__name__)


if __name__ == '__main__':

    logging.basicConfig(force=True, level=CFG.LogLevel.upper(),
                        format="%(asctime)s | %(levelname)s | %(threadName)s | %(name)s | %(message)s")                                

    try:
        # Create the API server     

        api_app = FastAPI(tite=CFG.ServiceName, 
                          include_in_schema=True, 
                          redirect_slashes=False,
                          openapi_url="/openapi.json",
                          docs_url=CFG.DocsUrl,
                          redoc_url=None,
                          title="Device to Cloud CLI profile management API",
                          description="API manage Device to Cloud CLI profiles under ~/.d2c/ directory.",
                          version=CFG.AppVersion,
                          servers=[
                            {"url": CFG.ExternalUrl, "description": f"{CFG.NAME}"},
                          ],
                          openapi_tags=[
                              {
                                  "name":"General",
                                  "description":"General endpoints"
                              },
                              {
                                  "name":"Profiles",
                                  "description":"Profile related endpoints"
                              }
                          ])
        log.info(f"You can access swagger doc at {CFG.ExternalUrl}{CFG.DocsUrl}")

        api_app.add_middleware(CORSMiddleware,
                               allow_origins=["*"],
                               allow_credentials=False,
                               allow_methods=["*"],
                               allow_headers=["*"])

        #########################################
        # General
        #########################################
        
        ### GET {{baseUrl}}/healthz
        @api_app.get(
            "/healthz",
            tags=["General"],
            summary="Health test of the endpoint.",
            description="Performs a health test of the endpoint."
        )
        async def _healthz_get(request:Request)->HealthzResponse:
            #print("dadsfasdfasdfasdfasdfasdfasdfasd")
            return healthz_get.handleRequest(request)

        #########################################
        # Profile
        #########################################

        ### GET {{baseUrl}}/profile
        @api_app.get(
            "/profile",
            tags=["Profiles"],
            summary="Gets all profiles",
            description="Gets all profiles.",
            response_description="List of profile JSONs."
        )
        async def _profile_get(request:Request)->List[dict]:
            return profile_get.handleRequest(request)

        ### GET {{baseUrl}}/profile/{{profileId}}         
        @api_app.get(
            "/profile/{id}",
            tags=["Profiles"],
            summary="Get details of a profile",
            description="Gets the detail json of a profile.",
            response_description="Profile JSON"
        )
        async def _profile_get_by_id(request:Request, id:str = Path(description="Id of the profile."),
                    )->dict:
            return profile_get.handleRequest(request, id=id)


        #########################################
        # Reports
        #########################################
        
        ### POST {{baseUrl}}/device-report/{{tenantId}}?when=last-month
        # when_desc = f"this-hour | last-hour | this-day | last-day | this-month | last-month | month-of-year | from-to"
        # month_of_year_desc = f"if when==month-of-year: MM.YYYY"
        # from_date_desc = f"if when==from-to: DD.MM.YYYY hh:mm:ss"
        # to_date_desc = f"if when==from-to: DD.MM.YYYY hh:mm:ss"
        
        # @api_app.post(
        #     "/device-report/{tenant_id}",
        #     tags=["Reports"],
        #     summary="Starts a device report",
        #     description="Creates a starts a ReportJob to create a device report for a specific reporting intervall.",
        #     response_description="Created job from which the processing status can be queried and the report file be downloaded"
        # )
        # async def _device_report_post(request:Request, 
        #                         tenant_id:int = Path(description="Id of the IMPACT tenant for which branch a report shall be created."),
        #                         when: str = Query(None, description=when_desc),
        #                         month_of_year:str = Query(None, description=month_of_year_desc),
        #                         from_date:str= Query(None, description=from_date_desc),
        #                         to_date:str= Query(None, description=to_date_desc),
        #                         token_info:TokenInfo=Depends(verify_token))->ReportJob:
        #     return device_report_post.handleRequest(token_info, request, tenant_id, when, 
        #                                             month_of_year, from_date,to_date)

        ####
        # Put the url path prefix in fron all endpoints
        
        main_app = FastAPI(openapi_url=None, #"/openapi.json",
                           docs_url=f'/docs',
                           redoc_url=None,
                          )
        main_app.mount(f"{CFG.ServiceUrlPrefix}", api_app)
        
        #########################################
        # RUN
        #########################################

        uvicorn.run(main_app,
                    host="0.0.0.0", 
                    port=int(CFG.ServicePort),
                    log_level="info",
                    access_log=False,
                    reload=False,
                    workers=1)

    except Exception as ex:
        log.error("ERROR: %s" % (str(ex)))
        traceback.print_exc()

