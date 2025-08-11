import json


def log_url(log_func, operation:str, url:str):
    log_func("")    
    log_func(f"URL: {operation} {url}")

def _maskAuth(headers:dict, header_name:str)->bool:
    if not (auth := headers.get(header_name, None)):
        return False
    elif len(auth) < 30:
        return False
    elif auth.startswith("Bearer "):
        headers[header_name] = "Bearer ***" #f"{auth[0:30]} ..."        
        return True
    else:
        headers[header_name] = "***" #f"{auth[0:30]} ..."        
        return True
    
def log_headers(log_func, headers:dict):
    h = headers.copy()
    #_maskAuth(h, "Authorization")
    #_maskAuth(h, "authorization")
    log_func(f"HEADERS:\n{json.dumps(h, indent=4)}")
    
def log_body(log_func, body:dict):
    if not body:
        body = ""
    log_func(f"BODY:\n{json.dumps(body, indent=4)}")

def log_response(log_func, response):
    log_func(f"RESPONSE CODE: {response.status_code}")
    log_func(f"RESPONSE HEADERS:")
    for header, value in response.headers.items():
        log_func(f"  {header}: {value}")    
    log_func(f"RESPONSE CONTENT: {response.content}")

