# ==========================================================
# Usage : repsonse parser, to determine the correctness of =
#         the status code, the content, etc.               =
# Author: Jian-Han Wu                                      =
# ==========================================================

import pytest
import json
import time
import sys

from .gatekeeper import *
from .http import * 

ACTION = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

# =============================================
# = Usage: check a str is in json format      =
# = Parameters:                               =
# = * body: <str> the str you want to check   =
# = Return: new body or raise exception       =
# =============================================
def jsonFormat_check (body):
    if type (body) == dict:
        return body
    elif type (body) != str:
        raise TypeError (f"Incorrect type {type (body)}")
    try:
        body = json.loads (body)
    except:
        raise ValueError (f"Incorrect json format {body}")
    return body

# =============================================
# = Usage: response parser for each action    =
# = Note : not including get_token            =
# = Parameters:                               =
# = * route : <str> url where action          =
# =          executes,a sample:               =
# =  f"{gatekeeper_module}/openness/apps/"    =
# = * action: <str> get | post | put | patch  =
# =           | delete                        =
# = * body  : <str> in json format if needed  =
# =           or json <dict>                  =
# = Example:                                  =
# = a. api_parser (".../nodes", "get")        =
# = b. api_parser (".../nodes", "post", {...})=
# =============================================
@pytest.fixture
def api_parser (get_token, http_get, http_post, http_put, http_patch, http_delete):
    def inner (route, action, body="", expect_errCode=0):
        if not route or type (route) != str:
            raise ValueError ("Expected non-empty route <str>!")
        elif not action or type (action) != str:
            raise ValueError ("Expected non-empty action <str>!")
        elif action.upper() not in ACTION:
            raise ValueError (f"Action ({action}) not exists!")
        elif action.upper() in ['GET', 'DELETE'] and body != "":
            raise ValueError ("Expected null body <str> when 'get' or 'delete' specified!")
        elif action.upper() in ['POST', 'PUT', 'PATCH']:
            try:
                body = jsonFormat_check (body)
            except Exception as e:
                raise Exception (f"Expected json-formated body <dict> | <str> when 'post', 'put' or 'patch' specified! {e}")
        
        header = get_token ['token']
        if action.upper()   == 'GET':
            token = http_get (route, headers=header)
        elif action.upper() == 'POST':
            token = http_post (route, headers=header, json=body)
        elif action.upper() == 'PUT':
            token = http_put (route, headers=header, json=body)
        elif action.upper() == 'PATCH':
            token = http_patch (route, headers=header, json=body)
        elif action.upper() == 'DELETE':
            token = http_delete (route, headers=header)

        # status_code
        if token.status_code != 200:
            raise SystemError (f"{action} failed! Unexpected status code ({token.status_code}).")
        elif token.content == b'null\n':
            raise SystemError (f"{action} failed! Null content response.")

        content = json.loads ((token.content).decode ())
        if content ['err_code'] != expect_errCode:
            raise SystemError (f"{action} with error code {content ['err_code']}: {content ['message']}.")
        
        # if err code != 0, no content data!
        return_data = content ['data'] if expect_errCode == 0 else None  

        return {
            'message' : content ['message'],
            'data'    : return_data
        }
    yield inner
