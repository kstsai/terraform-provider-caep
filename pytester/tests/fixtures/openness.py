# !/usr/bin/env python
# -*-coding: utf-8 -*-
import pytest
import json
import os


@pytest.fixture
def auth_api(ip_address):
    return "http://%s:8080/auth" % ip_address


@pytest.fixture
def app_api(ip_address):
    return "http://%s:8080/apps" % ip_address


@pytest.fixture
def app_with_id_api(ip_address):
    def _exec(app_id):
        return "http://%s:8080/apps/%s" % (ip_address, app_id)
    yield _exec


@pytest.fixture
def nodes_api(ip_address):
    return "http://%s:8080/nodes" % ip_address


@pytest.fixture
def node_app_api(ip_address):
    def _exec(node_id):
        return "http://%s:8080/nodes/%s/apps" % (ip_address, node_id)
    yield _exec


@pytest.fixture
def node_app_with_id_api(ip_address):
    def _exec(node_id, app_id):
        return "http://%s:8080/nodes/%s/apps/%s" % (ip_address, node_id, app_id)
    yield _exec


@pytest.fixture
def node_if_api(ip_address):
    def _exec(node_id):
        return "http://%s:8080/nodes/%s/interfaces" % (ip_address, node_id)
    yield _exec


@pytest.fixture
def get_json_config():

    local_path = os.path.dirname(__file__)

    def _exec(config_dir, config_file):

        with open(os.path.join(local_path, "..", config_dir, config_file)) as f:
            req = f.read()
        return json.loads(req)

    yield _exec


@pytest.fixture
def openness_auth(get_json_config, http_post, auth_api):
    # send auth request and get token
    request_body = get_json_config("resource_management_testcases", "openness_auth.json")
    headers = {
        "content-type": "application/json"
    }

    res = http_post(auth_api,
                    headers=headers,
                    json=request_body)
    print("\n" + auth_api + "==>token: " + json.loads(res.content).get('token'))

    yield {
        'status_code': res.status_code,
        'token': json.loads(res.content).get('token')
    }


@pytest.fixture
def openness_patch_node_if2(get_json_config, node_if_api, http_patch):

    def _exec(header, node_id):
        request_body = get_json_config("resource_management_testcases", "bind_interface_63.json")

        res = http_patch(node_if_api(node_id), headers=header, json=request_body)
        print(res.content)
        return res
    yield _exec


@pytest.fixture
def openness_patch_node_if(get_json_config,
                           node_if_api,
                           http_patch):

    def _exec(header, node_id):
        request_body = get_json_config("resource_management_testcases", "bind_interface.json")
        res = http_patch(node_if_api(node_id), headers=header,
                         json=request_body)
        return res
    yield _exec


@pytest.fixture
def openness_create_app(http_post,
                        app_api):
    def _exec(json_data, header):
        res = http_post(app_api,
                        headers=header,
                        json=json_data)
        return {
            'status_code': res.status_code,
            'app_id': json.loads(res.content).get('id')
        }
    yield _exec


@pytest.fixture
def openness_get_node_nums(http_get, nodes_api):
    def _exec(header):

        res = http_get(nodes_api, headers=header)
        if res.status_code != 200 and res.status_code != 201:
            return {
                'status_code': res.status_code
            }

        nodes = json.loads(res.content).get('nodes')
        return {
            'status_code': res.status_code,
            'nums': len(nodes)
        }
    yield _exec


@pytest.fixture
def openness_get_node_id_by_name(http_get,
                                 nodes_api):
    def _exec(node_name, header):
        res = http_get(nodes_api, headers=header)

        if res.status_code != 200 and res.status_code != 201:
            return {
                'status_code': res.status_code
            }

        node_id = ""
        nodes = json.loads(res.content).get('nodes')
        for node in nodes:
            print("***************")
            print(node)
            if node['name'] == node_name:
                node_id = node['id']
        if node_id == "":
            return {
                'status_code': 404,
                'node_id': ""
            }
        return {
            'status_code': res.status_code,
            'node_id': node_id
        }
    yield _exec


@pytest.fixture
def openness_deploy_app(node_app_api,
                        http_post):
    def _exec(json_data, header, node_id):
        res = http_post(node_app_api(node_id),
                        headers=header,
                        json=json_data)
        return res
    yield _exec


@pytest.fixture
def openness_get_app_status(node_app_with_id_api,
                            http_get):
    def _exec(header, node_id, app_id):
        res = http_get(node_app_with_id_api(node_id, app_id), headers=header)
        return {
            'status_code': res.status_code,
            'status': json.loads(res.content).get("status")
        }
    yield _exec


@pytest.fixture
def openness_start_app(node_app_with_id_api,
                       http_patch):
    def _exec(header, node_id, app_id):
        request_body = {
            "command": "start"
        }
        return http_patch(node_app_with_id_api(node_id, app_id), headers=header, json=request_body)
    yield _exec


@pytest.fixture
def openness_stop_app(node_app_with_id_api, http_patch):
    def _exec(header, node_id, app_id):
        request_body = {
            "command": "stop"
        }
        return http_patch(node_app_with_id_api(node_id, app_id), headers=header, json=request_body)
    yield _exec


@pytest.fixture
def openness_get_node_app_list(node_app_api, http_get):
    def _exec(header, node_id):
        res = http_get(node_app_api(node_id), headers=header)
        return res
    yield _exec


@pytest.fixture
def openness_delete_node_app(node_app_with_id_api, http_delete):
    def _exec(header, node_id, app_id):
        res = http_delete(node_app_with_id_api(node_id, app_id), headers=header)
        return res
    yield _exec


@pytest.fixture
def openness_get_app_list(app_api, http_get):
    def _exec(header):
        res = http_get(app_api, headers=header)
        return res
    yield _exec


@pytest.fixture
def openness_delete_app(app_with_id_api, http_delete):
    def _exec(header, app_id):
        res = http_delete(app_with_id_api(app_id),
                          headers=header)
        return res
    yield _exec
