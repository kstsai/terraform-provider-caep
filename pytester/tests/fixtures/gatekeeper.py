# !/usr/bin/env python
# -*-coding: utf-8 -*-

import pytest
import json
import time
import subprocess
from .http import *

from .http import *

@pytest.fixture
def gatekeeper_module(protocol, ip_address):
    default_port = "5666"
    if protocol == "https":
        default_port = "4666"
    module_name = "gatekeeper"
    module_api_version = "v1"
    service_url = f"{protocol}://{ip_address}:{default_port}/{module_name}/{module_api_version}"
    return service_url


@pytest.fixture
def gatekeeper_auth_api(gatekeeper_module):
    return f"{gatekeeper_module}/auth"


@pytest.fixture
def sentinel_container_api(gatekeeper_module):
    return f"{gatekeeper_module}/containers"


@pytest.fixture
def get_token(gatekeeper_auth_api, http_post, control_name, gatekeeper_default_user, gatekeeper_default_pwd):
    content = {
        "name": gatekeeper_default_user,
        "password": gatekeeper_default_pwd,
    }
    retry = 0
    result = http_post(gatekeeper_auth_api, json=content)
    body = json.loads(result.content)
    while retry < 3 and body["err_code"] != 0:
        time.sleep(5)
        print("Get token failed! retry left: %d" % (3-retry))
        result = http_post(gatekeeper_auth_api, json=content)
        body = json.loads(result.content)
        retry += 1
    if body["err_code"] == 0:
        print("Get token success! retry times: %d" % retry)
        token = body["data"]["token"]
    else:
        token = ""
    return {
        'err_code': body["err_code"],
        'data': body["data"],
        'token': {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + token,
            "Host": control_name
        }
    }


@pytest.fixture
def get_container_list(sentinel_container_api, http_get):
    def inner(header):
        result = http_get(sentinel_container_api, headers=header)
        return {
            'status_code': result.status_code,
            'content': result.content
        }
    yield inner


@pytest.fixture
def resolve_container_name():
    def inner(input_list):
        result = []
        res = json.loads(input_list)
        for item in res:
            result.append(item['name'])
        return result
    yield inner


@pytest.fixture
def get_container_cpu(sentinel_container_api, http_get):
    def inner(name, header):
        url = f"{sentinel_container_api}/{name}/cpu"
        result = http_get(url, headers=header)
        return {
            'status_code': result.status_code,
            'content': result.content
        }
    yield inner


@pytest.fixture
def get_container_disks(sentinel_container_api, http_get):
    def inner(name, header):
        url = f"{sentinel_container_api}/{name}/disks"
        result = http_get(url, headers=header)
        return {
            'status_code': result.status_code,
            'content': result.content
        }
    yield inner


@pytest.fixture
def get_container_memory(sentinel_container_api, http_get):
    def inner(name, header):
        url = f"{sentinel_container_api}/{name}/memory"
        result = http_get(url, headers=header)
        return {
            'status_code': result.status_code,
            'content': result.content
        }
    yield inner


@pytest.fixture
def get_container_networks(sentinel_container_api, http_get):
    def inner(name, header):
        url = f"{sentinel_container_api}/{name}/networks"
        result = http_get(url, headers=header)
        return {
            'status_code': result.status_code,
            'content': result.content
        }
    yield inner


@pytest.fixture
def get_host_path(gatekeeper_module):
    return f"{gatekeeper_module}/hosts"


@pytest.fixture
def get_host_list_path(get_host_path):
    return f"{get_host_path}/information"


@pytest.fixture
def get_host_list(get_host_list_path, http_get, api_parser):
    def inner():
        '''result = http_get(get_host_list_path, headers=header)'''
        res = api_parser(get_host_list_path, 'get', "")
        return res
    yield inner


@pytest.fixture
def resolve_resource_name():
    def inner(input_list):
        result = []
        res = json.loads(input_list)
        for item in res:
            result.append({'id': item['ID'], 'name': item['name']})
        return result
    yield inner


@pytest.fixture
def get_request_time():
    start_time = int(time.time()) - (1*60*60)  # get one hour ago data
    return f"starttime={start_time}"


@pytest.fixture
def get_host_metrics(get_host_path, get_request_time, api_parser):
    def inner(name, metric, err_code):
        result = api_parser(get_host_path+f"/{name}/{metric}?{get_request_time}", 'get', "", err_code)
        print(get_host_path+f"/{name}/{metric}?{get_request_time}")
        if err_code == 0:
            return json.dumps(result['data'])
        else:
            return json.dumps(result['message'])
    yield inner


@pytest.fixture
def get_new_container_list(get_host_path, api_parser):
    def inner(host_name, err_code):
        result = api_parser(get_host_path+f"/{host_name}/containers", 'get', "", err_code)
        if err_code == 0:
            return json.dumps(result['data'])
        else:
            return json.dumps(result['message'])
    yield inner


@pytest.fixture
def get_new_container_metrics(get_host_path, http_get, get_request_time, api_parser):
    def inner(host_name, cn_name, metric, err_code):
        result = api_parser(get_host_path+f"/{host_name}/containers/{cn_name}/{metric}?{get_request_time}", 'get',
                            "", err_code)
        if err_code == 0:
            return json.dumps(result['data'])
        else:
            return json.dumps(result['message'])
    yield inner


@pytest.fixture
def get_vm_list(get_host_path, http_get, api_parser):
    def inner(host_name, err_code):
        result = api_parser(get_host_path+f"/{host_name}/vms", 'get', "", err_code)
        if err_code == 0:
            return json.dumps(result['data'])
        else:
            return json.dumps(result['message'])
    yield inner


@pytest.fixture
def get_new_vm_metrics(get_host_path, http_get, get_request_time, api_parser):
    def inner(host_name, vm_name, metric, err_code):
        result = api_parser(get_host_path+f"/{host_name}/vms/{vm_name}/{metric}?{get_request_time}", 'get',
                            "", err_code)
        if err_code == 0:
            return json.dumps(result['data'])
        else:
            return json.dumps(result['message'])
    yield inner


@pytest.fixture
def bring_app(ip_address, edge_name):
    def inner():
        cmd = f"bash tests/script/01_launch_app.sh {ip_address} tests/script/json/app_vm1.json {edge_name}"
        print(cmd)
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            if e.output.rstrip():
                return f"Bring up app failed: {e.output}"
        return "success"
    yield inner


@pytest.fixture
def delete_app(ip_address, edge_name):
    def inner():
        cmd = f"bash tests/script/02_remove_app.sh {ip_address} tests/script/json/app_vm1.json {edge_name}"
        print(cmd)
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            if e.output.rstrip():
                return f"Delete app failed: {e.output}"
        return "success"
    yield inner


@pytest.fixture
def get_configs(get_host_path, http_get, api_parser):
    def inner(host_name, err_code):
        result = api_parser(get_host_path+f"/{host_name}/configs", 'get', "", err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner


@pytest.fixture
def post_configs(get_host_path, http_post, api_parser):
    def inner(host_name, err_code, data):
        result = api_parser(get_host_path+f"/{host_name}/configs", 'post', data, err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner


@pytest.fixture
def sshapi_path(gatekeeper_module):
    return f"{gatekeeper_module}/edgenodes/sshproxy"


@pytest.fixture
def exec_ssh(sshapi_path, http_post, get_token):
    def inner(hostname, cmd, user, pwd, timeout):
        content = {
            "hostname": hostname,
            "cmd": cmd,
            "sshAccount": user,
            "sshPassword": pwd
        }
        if timeout != 0:
            content["sshTimeout"] = timeout
        # To get token
        token_res = get_token
        assert 0 == token_res['err_code']
        assert b'[]\n' != token_res['data']
        result = http_post(sshapi_path, json=content, headers=token_res['token'])
        return result
    return inner

@pytest.fixture
def user_path(gatekeeper_module):
    return f"{gatekeeper_module}/system/users"

@pytest.fixture
def get_gatekeeper_userlist(api_parser, user_path):
    def inner():
        res = api_parser(user_path, 'get')
        return res['data']
    return inner

@pytest.fixture
def add_gatekeeper_user(user_path, api_parser):
    def inner(name, password, role):
        content = {
            "name": name,
            "password": password,
            "role": role
        }
        result = api_parser(user_path, 'post', content)
        return result['message']
    return inner

@pytest.fixture
def delete_gatekeeper_user(user_path, http_delete, get_token):
    def inner(name):
        content = {
            "name": name
        }
        # To get token
        token_res = get_token
        assert 0 == token_res['err_code']
        assert b'[]\n' != token_res['data']
        result = http_delete(user_path, json=content, headers=token_res['token'])
        if result.status_code != 200:
            raise SystemError (f"Unexpected status code ({result.status_code}).")
        elif result.content == b'null\n':
            raise SystemError (f"Null content response.")
        content = json.loads((result.content).decode())
        if content['err_code'] != 0:
            raise SystemError (f"Error code {content['err_code']}: {content['message']}.")
        return content['message']
    return inner

@pytest.fixture
def delete_all_userlist(api_parser, user_path, delete_gatekeeper_user):
    def inner():
        res = api_parser(user_path, 'get')
        for item in res['data']:
            delete_gatekeeper_user(item['name'])
    return inner