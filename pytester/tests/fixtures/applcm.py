# !/usr/bin/env python
# -*-coding: utf-8 -*-

import pytest
import random
import re
import requests
import json

from .gatekeeper import *

@pytest.fixture
def applcm_api_direct(gatekeeper_module):
    uri = f"{gatekeeper_module}/edgeapps"
    return uri.replace("gatekeeper","applcm").replace("5666","10286").replace("4666","10286")


@pytest.fixture
def applcm_api_via_gk(gatekeeper_module):
    return f"{gatekeeper_module}/edgeapps"

@pytest.fixture
def networks_ovs_api_via_gk(gatekeeper_module):
    return f"{gatekeeper_module}/networks"


@pytest.fixture
def get_applcm_edgaapps_templates(api_parser, applcm_api_via_gk):
    def inner(err_code=0):
        print(applcm_api_via_gk+f"/templates")
        result = api_parser(applcm_api_via_gk+"/templates", 'get', "", err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def post_applcm_edgaapps_templates(api_parser, applcm_api_via_gk):
    def inner(err_code=0,dicAppTempl={}):
        print(f"POST {applcm_api_via_gk}/templates")
        result = api_parser(applcm_api_via_gk+"/templates", 'post',json.dumps(dicAppTempl), err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def put_applcm_edgaapps_templates(api_parser, applcm_api_via_gk):
    def inner(err_code=0,tid=None,dicAppTempl={},):
        print(applcm_api_via_gk+f"/templates")
        result = api_parser(applcm_api_via_gk+"/templates/"+tid, 'put',json.dumps(dicAppTempl), err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def delete_applcm_edgaapps_templates_tid(api_parser, applcm_api_via_gk):
    def inner(err_code=0,tid=None,dicAppTempl={},):
        print(f"DEL {applcm_api_via_gk}/templates/{tid}")
        result = api_parser(applcm_api_via_gk+"/templates/"+tid, 'delete','', err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def get_applcm_edgaapps_templates_tid(api_parser, applcm_api_via_gk):
    def inner(err_code=0,tid=None):
        result = api_parser(applcm_api_via_gk+"/templates/"+tid, 'get', "", err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner


@pytest.fixture
def get_applcm_hostIp(applcm_api_via_gk):
    def inner(err_code=0):
        print(applcm_api_via_gk+f"/nodes")
        sr = re.search("(http|https):\/\/(.+):([0-9]+)\/gatekeeper", applcm_api_via_gk)
        if sr:
            targetHostIp = sr.group(2) 
            return targetHostIp
    yield inner

@pytest.fixture
def get_applcm_health(api_parser, applcm_api_via_gk):
    def inner(err_code=0):
        print(applcm_api_via_gk+f"/nodes")
        sr = re.search("(http|https):\/\/(.+):([0-9]+)\/gatekeeper", applcm_api_via_gk)
        if sr:
            targetHostIp = sr.group(2) 
        resp = requests.get(f"http://{targetHostIp}:10286/health")
        return resp.json()
    yield inner

@pytest.fixture
def get_applcm_edgaapps_nodes(api_parser, applcm_api_via_gk):
    def inner(err_code=0):
        print(applcm_api_via_gk+f"/nodes")
        result = api_parser(applcm_api_via_gk+"/nodes", 'get', "", err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def get_applcm_edgaapps_nodes_nid_apps(api_parser, applcm_api_via_gk):
    def inner(err_code=0,node_id=None):
        print(applcm_api_via_gk+f"/nodes/{node_id}/apps")
        result = api_parser(applcm_api_via_gk+f"/nodes/{node_id}/apps", 'get', "", err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def get_applcm_edgaapps_nodes_nid_apps_brief(api_parser, applcm_api_via_gk):
    def inner(err_code=0,node_id=None):
        print(applcm_api_via_gk+f"/nodes/{node_id}/apps")
        result = api_parser(applcm_api_via_gk+f"/nodes/{node_id}/apps?briefSummary=true", 'get', "", err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def post_applcm_edgaapps_nodes_nid_apps(api_parser, applcm_api_via_gk):
    def inner(err_code=0,node_id=None,dic1=None):
        print(f"POST {applcm_api_via_gk}/nodes/{node_id}/apps")
        result = api_parser(applcm_api_via_gk+f"/nodes/{node_id}/apps", 'post', json.dumps(dic1), err_code)
        return result
    yield inner

@pytest.fixture
def get_applcm_edgaapps_nodes_nid_apps_aid(api_parser, applcm_api_via_gk):
    def inner(err_code=0,node_id=None,app_id=None):
        result = api_parser(applcm_api_via_gk+f"/nodes/{node_id}/apps/{app_id}", 'get', "", err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def get_applcm_edgaapps_nodes_nid_apps_aid_logs(api_parser, applcm_api_via_gk):
    def inner(err_code=0,node_id=None,app_id=None):
        result = api_parser(applcm_api_via_gk+f"/nodes/{node_id}/apps/{app_id}/logs", 'get', "", err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def patch_applcm_edgaapps_nodes_nid_apps_aid(api_parser, applcm_api_via_gk):
    def inner(err_code=0,node_id=None,app_id=None,dic1=None):
        result = api_parser(applcm_api_via_gk+f"/nodes/{node_id}/apps/{app_id}", 'patch', json.dumps(dic1), err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def delete_applcm_edgaapps_nodes_nid_apps_aid(api_parser, applcm_api_via_gk):
    def inner(err_code=0,node_id=None,app_id=None):
        result = api_parser(applcm_api_via_gk+f"/nodes/{node_id}/apps/{app_id}", 'delete', "", err_code)
        print(f"DELETE {applcm_api_via_gk}/nodes/{node_id}/apps/{app_id} {err_code}")
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def get_applcm_edgaapps_nodes_nid_vdisks(api_parser, applcm_api_via_gk):
    def inner(err_code=0,node_id=None):
        result = api_parser(applcm_api_via_gk+f"/nodes/{node_id}/vdisks", 'get', "", err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def post_applcm_edgaapps_nodes_nid_vdisks(api_parser, applcm_api_via_gk):
    def inner(err_code=0,node_id=None,dic1=None):
        print(f"POST {applcm_api_via_gk}/nodes/{node_id}/vdisks")
        result = api_parser(applcm_api_via_gk+f"/nodes/{node_id}/vdisks", 'post', json.dumps(dic1), err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def patch_applcm_edgaapps_nodes_nid_apps_aid_vdisks(api_parser, applcm_api_via_gk):
    def inner(err_code=0,node_id=None,app_id=None,dic1={}):
        result = api_parser(f"{applcm_api_via_gk}/nodes/{node_id}/apps/{app_id}/vdisks", 'patch',json.dumps(dic1), err_code)
        print(f"PATCH {applcm_api_via_gk}/nodes/{node_id}/apps/{app_id}/vdisks /w {dic1} {err_code}")
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture
def delete_applcm_edgaapps_nodes_nid_vdisks_vdname(api_parser, applcm_api_via_gk):
    def inner(err_code=0,node_id=None,vdname=None):
        print(f"DELETE {applcm_api_via_gk}/nodes/{node_id}/vdisks/{vdname}")
        result = api_parser(f"{applcm_api_via_gk}/nodes/{node_id}/vdisks/{vdname}", 'delete','', err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner
    
@pytest.fixture
def get_edgaapps_nodes_nid_apps_aid_traffic_rules(api_parser, networks_ovs_api_via_gk):
    def inner(err_code=0,node_id=None,app_id=None):
        result = api_parser(networks_ovs_api_via_gk+f"/nodes/{node_id}/ovs", 'get', "", err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner


@pytest.fixture
def remove_edgaapps_nodes_nid_ovs_oid_mirror_rule(api_parser, networks_ovs_api_via_gk):
    def inner(err_code=0,node_id=None,ovs_id=None):
        result = api_parser(networks_ovs_api_via_gk+f"/nodes/{node_id}/ovs/{ovs_id}/mirror", 'delete', "", err_code)
        if err_code == 0:
            return result['data']
        else:
            return result['message']
    yield inner

@pytest.fixture(autouse=True)
def getValidNodeId(get_applcm_health):

    dicRet = get_applcm_health(0)
    print (dicRet)
    for l in dicRet["message"].split("\n"):
        if l.find("online") ==  -1:
            continue
        for kvp in l.split(","):
            if kvp.startswith("node_id"):
                node_id = kvp.split("=")[1]
                return node_id

@pytest.fixture
def applcm_onboard_deploy_app_with_template(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid):


    def inner(dicAppTempl):
        targetHostIp = get_applcm_hostIp()
        print(dicAppTempl) 
        res = post_applcm_edgaapps_templates(0,dicAppTempl)
        print(res)

        node_id = getValidNodeId
        print(f"deploy app to {node_id} /w {dicAppTempl}")
        dicDeployApp = {"template_id":res["template_id"]}
        res = post_applcm_edgaapps_nodes_nid_apps(0,node_id,dicDeployApp)
        print(res)

        time.sleep(1) 
        retry = 0
        while retry < 1000:
            inst = get_applcm_edgaapps_nodes_nid_apps_aid(0, node_id, dicDeployApp["template_id"])
            if inst["state"] in ["ready","error"]:
                break
            if retry % 10 == 0:
                print("%d %s %s %s"%(retry, inst["state"],inst["app_name"],inst["app_id"]))
            time.sleep(1) 
            retry += 1
        print("%d %s %s %s"%(retry, inst["state"],inst["app_name"],inst["app_id"]))

        if inst["state"] in ["ready"]:
            return "ok",node_id, inst["app_id"]
        else:
            return "fail",node_id, inst["app_id"]
    yield inner

@pytest.fixture
def applcm_onboard_deploy_start_with_template(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid,
        patch_applcm_edgaapps_nodes_nid_apps_aid):

    def inner(dicAppTempl):
        targetHostIp = get_applcm_hostIp()
        print(dicAppTempl) 
        res = post_applcm_edgaapps_templates(0,dicAppTempl)
        print(res)

        node_id = getValidNodeId
        print(f"deploy app to {node_id} /w {dicAppTempl}")
        dicDeployApp = {"template_id":res["template_id"]}
        res = post_applcm_edgaapps_nodes_nid_apps(0,node_id,dicDeployApp)
        print(res)

        time.sleep(1) 
        retry = 0
        while retry < 1000:
            inst = get_applcm_edgaapps_nodes_nid_apps_aid(0, node_id, dicDeployApp["template_id"])
            if inst["state"] in ["ready","error"]:
                break
            if retry % 10 == 0:
                print("%d %s %s %s"%(retry, inst["state"],inst["app_name"],inst["app_id"]))
            time.sleep(1) 
            retry += 1
        print("%d %s %s %s"%(retry, inst["state"],inst["app_name"],inst["app_id"]))

        if inst["state"] in ["ready"]:
            patch_applcm_edgaapps_nodes_nid_apps_aid(0, node_id, inst["app_id"], {"action":"start"})

            retry = 0
            while retry < 300:
                inst = get_applcm_edgaapps_nodes_nid_apps_aid(0, node_id, inst["app_id"])
                if len(inst["ip_config"]) > 0:
                    print("{} {} {} {} {}".format(retry, inst["state"],inst["app_name"],inst["app_id"],inst["ip_config"]))
                    appMgmIp = inst["ip_config"][0]["port_vnic"].split(":")[1]
                    return "ok",node_id, inst["app_id"],appMgmIp,inst["app_name"] 
                if inst["state"] in ["error"]:
                    return "error",node_id, inst["app_id"],None, None
                if retry % 10 == 0:
                    print("%d %s %s %s"%(retry, inst["state"],inst["app_name"],inst["app_id"]))
                time.sleep(1) 
                retry += 1
            print("%d %s %s %s"%(retry, inst["state"],inst["app_name"],inst["app_id"]))


        return "ok",node_id, inst["app_id"],None, None
    yield inner


###################################################################################

class ApplcmHelper(object):


    @pytest.fixture(autouse=True)
    def _get_cmdoption_ip_address(self, get_applcm_hostIp):
        self._hostIP = get_applcm_hostIp

    def __init__(self,targetHostIp):
        self.PH={"content-type":"application/json;charset=UTF-8"}
        self._hostIP = targetHostIp
        self.image_id = self.__get_valid_image_id()
        self.node_id = self.__get_valid_node_id()

    def __get_valid_image_id(self):
        resp = requests.get(f'http://{self._hostIP}:9292/image_mgmt/v1/images')
        lstRet = resp.json()
        self.lstImagesCache = lstRet[:]
        if len(lstRet) > 0:
            return lstRet[0]["id"]
        return "ci-cirros"

    def __get_valid_node_id(self):
        # case GET /health
        resp = requests.get(f'http://{self._hostIP}:10286/health')
        dicRet = resp.json()
        for l in dicRet["message"].split(","):
            if l.startswith("node_id"):
                return l.split("=")[1]


    def getAppTemplConfig(self,filenamePattern):

        image_id = None 
        for img in self.lstImagesCache:
            if re.search(filenamePattern, img["file"]):
                image_id = img["id"]
                break

        dicAppTempl = self.getAppTemplConfigForCirros()
        if image_id != None: 
            dicAppTempl["app_type"] = img["type"] 
            dicAppTempl["images"][0]["image_id"] = image_id 
            dicAppTempl["template_name"] = "okdel-"+filenamePattern + ("{}".format(random.random())[:5])

        return dicAppTempl 

    def getAppTemplConfigForSecureVm(self):

        image_id = None
        for ii in self.lstImagesCache:
            if ii["file"].find("cos7-cloud-init.qcow2") >= 0:
                image_id = ii["id"]
                break
        if image_id == None:
            return

        dicAppTempl = self.getAppTemplConfigForCirros()
        dicAppTempl["images"][0]["image_id"] = image_id 
        dicAppTempl["metadata"] = None 
        dicAppTempl["userdata"] = None 
        dicAppTempl["vendor"] = "faca-secure-vm"
        dicAppTempl["template_name"] = dicAppTempl["template_name"][:12]+"sec"

        return dicAppTempl 

    def getAppTemplConfigForBigImageFile(self):

        for img in self.lstImagesCache:
            if int(img["size"]) > 1000000000: # 1G
                image_id = img["id"]
                break

        dicAppTempl = self.getAppTemplConfigForCirros()
        dicAppTempl["images"][0]["image_id"] = image_id 
        dicAppTempl["template_name"] = dicAppTempl["template_name"][:16]+"big"

        return dicAppTempl 


    def getAppTemplConfigForCirros(self):

        for ii in self.lstImagesCache:
            if ii["file"].find("cirros") >= 0:
                image_id = ii["id"]
                break

        udata = r"""
write_files:
-   content: |
      system:
        is_standalone: 1
        detailed_data: 1
        ddns: 8.8.8.8
        internet_dns: 8.8.8.8
        mgmt_interface: eth0
    path: /home/init.yaml
"""
        image_id = image_id
        rnd_appName = "okdel-{}".format(random.random())
        dicAppTempl= {
          "template_name": rnd_appName, 
          "app_type": "vm",
          "images": [
            {
              "image_id": image_id 
            }
          ],
          "flavor_setting": {
            "vcpu_cores": 1,
            "memory": 1,
            "disk": 80
          },
          "metadata": "cloud_init: \n  - int\n  - xhaul\n  - oam\n",
          #"userdata": "write_file:\n  xyz: %s\n"%(rnd_appName),
          "userdata": udata,
          "version": "1.0",
          "vendor": "faca",
          "description": "curror-testvm"
        }
        return dicAppTempl

