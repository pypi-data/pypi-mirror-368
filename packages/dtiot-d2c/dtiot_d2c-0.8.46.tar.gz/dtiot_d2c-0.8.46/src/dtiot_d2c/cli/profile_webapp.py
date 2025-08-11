import logging
import os
import subprocess
import sys
import tempfile
import time
import webbrowser

import requests

import dtiot_d2c.cli.CFG as CFG

log = logging.getLogger(__name__)

def build_api_server_url()->str:
    return f"{CFG.PMAPI_PROTOCOL}://{CFG.PMAPI_HOST}:{CFG.PMAPI_PORT}/{CFG.PMAPI_PATH}"
    
def test_api_server_health()->bool:

    url = f"{build_api_server_url()}/healthz"
    log.debug(f"GET: {url}")

    headers = {
        "Content-Type"  : "application/json",
        "Accept"        : "application/json",
    }
    log.debug(f"HEADERS: {headers}")

    try:
        response = requests.get(url=url, headers=headers)   

        if response.ok:
            return True
        else:
            return False
    except Exception as ex:
        #log.error(f"Error while testing pm api {url}: {ex}")
        return False

def start_api_server(startup_timeout_secs:int=3)->bool:
    python_exe = sys.executable
    server_py = f"{os.path.dirname(__file__)}/prfmanapi/main.py"

    # Setze die Umgebungsvariable LOGLEVEL auf "debug"
    env = os.environ.copy()
    
    env["CFG"] = "DEFAULT"
    env["PRINTENV"] = "true"
    current_log_level = log.getEffectiveLevel()
    env["LOGLEVEL"] = logging.getLevelName(current_log_level)    

    # Create temp file for stdout and stderr
    temp_file, temp_file_name = tempfile.mkstemp()

    log.info(f"Starting profile manager API and deligating stdout and stderr to {temp_file_name}.")
    process = subprocess.Popen(
        [python_exe, server_py],
        env=env,
        start_new_session=True,
        stderr=temp_file,
        stdout=temp_file
    )
    
    # Wait until the server has been started ...
    before_time=time.time()
    while True:
        if test_api_server_health():
            break
        elif (time.time() - before_time) > startup_timeout_secs:
            log.error(f"Profile manager API doesn't response health.")
            return False
        else:
            time.sleep(0.5)

    return True
    
def open_url_in_browser(url):
    browsers = ['google-chrome', 'firefox', 'msedge', 'chrome', 'mozilla', 'edge']  
    for browser_name in browsers:
        try:
            browser = webbrowser.get(browser_name)
            browser.open(url)
            #print(f"URL geöffnet in {browser_name}.")
            return
        except webbrowser.Error as e:
           print(f"Konnte nicht öffnen mit {browser_name}: {e}")

    # Fallback auf Standardbrowser
    webbrowser.open(url)
    
def open_in_browser(webapp_url:str=None):
    
    ###
    # Test if the profile management api server is running.
    # If not, start it.    
    api_running=False
    wait_for_api_timeout_secs = 3
    start_time = time.time()
    while True:
        if test_api_server_health():
            api_running=True
            break
        elif (time.time() - start_time) > wait_for_api_timeout_secs:
            break
        else:
            time.sleep(1)

    # The api is not running, start it ...  
    if not api_running:
        if not start_api_server():
            raise Exception(f"Could not start profile manager API server locally.")

    log.info(f"Profile manager API server is running.")

    ###
    # Start profile manager web app
    
    ###
    # Open profile manager in the api
    log.info(f"Opening profile manager in browser ..")
    url = f"http://127.0.0.1:{CFG.PMWEBAPP_PORT}/{CFG.PMWEBAPP_PATH}"
    open_url_in_browser(url)
    #webbrowser.open_new(url)

    
    