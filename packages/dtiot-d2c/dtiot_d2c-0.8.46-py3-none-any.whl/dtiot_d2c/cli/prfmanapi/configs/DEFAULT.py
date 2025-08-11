import json
import os

NAME="DEFAULT"

LogLevel = os.getenv("LOGLEVEL") or "INFO" 
ServiceName = os.getenv("SERVICE_NAME") or "d2c-profile-management-api"
ServiceUrlPrefix = f"/{ServiceName}"
ServicePort = os.getenv("SERVICE_PORT") or 38081
AppVersion = os.getenv("APP_VERSION") or "X.X.X"      
ServiceHostname = os.getenv("SERVICEHOSTNAME") or "127.0.0.1"

if ServiceHostname == "127.0.0.1":
    ExternalUrl = f"http://{ServiceHostname}:{ServicePort}/{ServiceName}"
else:
    ExternalUrl = f"https://{ServiceHostname}/{ServiceName}"
    
WelcomeMessage = f"GET {ExternalUrl}/healthz to test"

DocsCfg = {
    "url_token" : os.getenv("DOCS_URL_TOKEN") or ""
}
DocsUrl = f'/docs'   

