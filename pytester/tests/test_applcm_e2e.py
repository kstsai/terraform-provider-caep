import allure
import json
import os
import pytest
import random
import re
import requests
import subprocess
import time
import unittest
import warnings

from .fixtures.applcm import ApplcmHelper


@pytest.fixture(autouse=True)
def hostIP(request):
    hostIp = request.config.getoption("--ip_address")
    return hostIp

@pytest.fixture(autouse=True)
def applcm_api_pre(request):
    hostIp = request.config.getoption("--ip_address")
    return f"http://{hostIp}:10286/applcm/v1"

@pytest.fixture(autouse=True)
def applcm_api_via_gatekeeper(request):
    hostIp = request.config.getoption("--ip_address")
    return f"http://{hostIp}:5666/gatekeeper/v1"

@pytest.fixture(scope="class")
def db_class(request):
    class DummyDb:
        pass

    request.cls.db = DummyDb()

warnings.simplefilter('ignore',pytest.PytestUnknownMarkWarning)


from .fixtures.http import *
from .fixtures.applcm import *
from .fixtures.api_parser import *

"""
@pytest.fixture(autouse=True)
def getValidNodeId(get_applcm_health):

    dicRet = get_applcm_health(0)
    print (dicRet)
    for l in dicRet["message"].split(","):
            print(l)
            if l.startswith("node_id"):
                node_id = l.split("=")[1]
                return node_id
"""

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0000_get_applcm_health(get_applcm_health):
    print (f"get_applcm_health")
    res = get_applcm_health(0)
    print (res)

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0100_post_applcm_edgaapps_templates(get_applcm_hostIp, post_applcm_edgaapps_templates):
    """
    # case POST /applcm/v1/edgeapps/templates for creating a new app template
    """    
    targetHostIp = get_applcm_hostIp()
    print(targetHostIp)
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    print(dicAppTempl) 
    image_id = dicAppTempl["images"][0]["image_id"]

    resp0 = requests.get(f'http://{targetHostIp}:9292/image_mgmt/v1/images/{image_id}/refcount')
    print(f"before adding new app template, image {image_id} refcount",resp0.content)
    refcount0 = resp0.json()["refcount"]
    res = post_applcm_edgaapps_templates(0,dicAppTempl)
    print(res)
    resp1 = requests.get(f'http://{targetHostIp}:9292/image_mgmt/v1/images/{image_id}/refcount')
    print(f"after adding new app template, image {image_id} refcount",resp1.content)
    refcount1 = resp1.json()["refcount"]
    assert refcount0 == refcount1 -1

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0101_get_applcm_edgaapps_templates(get_applcm_edgaapps_templates):
    """
    # case GET /applcm/v1/edgeapps/templates for retrieving all app templates
    """    
    res = get_applcm_edgaapps_templates(0)
    print("get_applcm_edgaapps_templates Resp:%d templates"%len(res))
    for t in res: 
        assert t["template_id"] != ""
        assert t["template_name"] !=""
        assert(t["app_type"] in ["vm","container","compose"])
        assert(t["flavor"]!="")
        assert(int(t["cores"]) > 0)
        assert(int(t["memory"])> 0)
        assert(int(t["disk"])>=0)
        assert("metadata" in t)
        assert("userdata" in t)
        assert("networkdata" in t)
        assert(t["last_modified_isodate"]!="")
        assert(t["last_modified_timestamp"]!=0)

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0102_get_applcm_edgaapps_templates_tid(get_applcm_edgaapps_templates, get_applcm_edgaapps_templates_tid):
    """
    # case GET /applcm/v1/edgeapps/templates/{tmplate_id} for retrieving ONE app template
    """    
    res = get_applcm_edgaapps_templates(0)
    print("get_applcm_edgaapps_templates Resp:%d templates"%len(res))
    for tt in res: 
        t = get_applcm_edgaapps_templates_tid(0,tt["template_id"])
        assert t["template_id"] != ""
        assert t["template_name"] !=""
        assert(t["app_type"] in ["vm","container","compose"])
        assert(t["flavor"]!="")
        assert(int(t["cores"]) > 0)
        assert(int(t["memory"])> 0)
        assert(int(t["disk"])>=0)
        assert("metadata" in t)
        assert("userdata" in t)
        assert("networkdata" in t)
        assert(t["last_modified_isodate"]!="")
        assert(t["last_modified_timestamp"]!=0)



@allure.feature('negative_test')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0103_post_applcm_edgaapps_templates_duplicated_name(get_applcm_hostIp, post_applcm_edgaapps_templates):
    """
    # negative case POST /edgeapps/templates with duplicated template_name
    """
    targetHostIp = get_applcm_hostIp()
    print(targetHostIp)
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    print(dicAppTempl) 
    res = post_applcm_edgaapps_templates(0,dicAppTempl)
    print(res)
    res = post_applcm_edgaapps_templates(2109,dicAppTempl)
    print(res)

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0104_put_applcm_edgaapps_templates_tid_modify(get_applcm_hostIp, post_applcm_edgaapps_templates, get_applcm_edgaapps_templates_tid, put_applcm_edgaapps_templates):
    """
    # case PUT /edgeapps/templates with to modify template_name
    """
    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    print(dicAppTempl) 
    res = post_applcm_edgaapps_templates(0,dicAppTempl)
    print(res)
    t0 =get_applcm_edgaapps_templates_tid(0,res["template_id"])

    dicPutTempl= {
      "template_name": "modified-"+ t0["template_name"][:12],
      "app_type":  t0["app_type"],
      "images": [
        {
          "image_id": t0["images"][0]["image_id"]
        }
      ],
      "flavor_setting": {
        "vcpu_cores": t0["cores"],
        "memory": t0["memory"],
        "disk": t0["images"][0]["vdisk_size"]
      },
      "metadata": t0["metadata"], 
      "userdata": t0["userdata"],
      "version": t0["version"] if t0["version"] else "1.0",
      "vendor": t0["vendor"] if t0["vendor"] else "faca",
      "description": t0["description"] if t0["description"] else "1"
    }
    res = put_applcm_edgaapps_templates(0,t0["template_id"], dicPutTempl)
    print(res)

    t1 =get_applcm_edgaapps_templates_tid(0, t0["template_id"])
    assert t1["template_name"] == dicPutTempl["template_name"]




@allure.feature('negative_test')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0105_post_applcm_edgaapps_templates_max_33(get_applcm_hostIp, post_applcm_edgaapps_templates):
    """
    # case POST /edgeapps/templates with with vcpu_cores=33
    """
    targetHostIp = get_applcm_hostIp()
    print(targetHostIp)
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    dicAppTempl["flavor_setting"]["vcpu_cores"]= 33
    print(dicAppTempl) 
    res = post_applcm_edgaapps_templates(2112,dicAppTempl)
    print(res)

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0106_put_applcm_edgaapps_templates_tid_modify_max_33(get_applcm_hostIp, post_applcm_edgaapps_templates, get_applcm_edgaapps_templates_tid, put_applcm_edgaapps_templates):
    """
    # case PUT /edgeapps/templates with vcpu_cores=33 
    """
    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    print(dicAppTempl) 
    res = post_applcm_edgaapps_templates(0,dicAppTempl)
    print(res)
    t0 =get_applcm_edgaapps_templates_tid(0,res["template_id"])

    dicPutTempl= {
      "template_name": t0["template_name"],
      "app_type":  t0["app_type"],
      "images": [
        {
          "image_id": t0["images"][0]["image_id"]
        }
      ],
      "flavor_setting": {
        "vcpu_cores": 33,
        "memory": t0["memory"],
        "disk": t0["images"][0]["vdisk_size"]
      },
      "metadata": t0["metadata"], 
      "userdata": t0["userdata"],
      "version": t0["version"] if t0["version"] else "1.0",
      "vendor": t0["vendor"] if t0["vendor"] else "faca",
      "description": t0["description"] if t0["description"] else "1"
    }
    res = put_applcm_edgaapps_templates(2114,t0["template_id"], dicPutTempl)
    print(res)

    t1 =get_applcm_edgaapps_templates_tid(0, t0["template_id"])
    assert t1["template_name"] == dicPutTempl["template_name"]


@allure.feature('negative_test')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0107_post_applcm_edgaapps_templates_max_65(get_applcm_hostIp, post_applcm_edgaapps_templates):
    """
    # negative case POST /edgeapps/templates with memory=65
    """
    targetHostIp = get_applcm_hostIp()
    print(targetHostIp)
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    dicAppTempl["flavor_setting"]["memory"]= 65
    print(dicAppTempl) 
    res = post_applcm_edgaapps_templates(2112,dicAppTempl)
    print(res)

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0108_put_applcm_edgaapps_templates_tid_modify_max_65(get_applcm_hostIp, post_applcm_edgaapps_templates, get_applcm_edgaapps_templates_tid, put_applcm_edgaapps_templates):
    """
    # case PUT /edgeapps/templates with memory = 65
    """
    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    print(dicAppTempl) 
    res = post_applcm_edgaapps_templates(0,dicAppTempl)
    print(res)
    t0 =get_applcm_edgaapps_templates_tid(0,res["template_id"])

    dicPutTempl= {
      "template_name": t0["template_name"],
      "app_type":  t0["app_type"],
      "images": [
        {
          "image_id": t0["images"][0]["image_id"]
        }
      ],
      "flavor_setting": {
        "vcpu_cores": t0["cores"],
        "memory": 65,
        "disk": t0["images"][0]["vdisk_size"]
      },
      "metadata": t0["metadata"], 
      "userdata": t0["userdata"],
      "version": t0["version"] if t0["version"] else "1.0",
      "vendor": t0["vendor"] if t0["vendor"] else "faca",
      "description": t0["description"] if t0["description"] else "1"
    }
    res = put_applcm_edgaapps_templates(2114,t0["template_id"], dicPutTempl)
    print(res)

    t1 =get_applcm_edgaapps_templates_tid(0, t0["template_id"])
    assert t1["template_name"] == dicPutTempl["template_name"]


@allure.feature('applcm')
@allure.severity('critical')
@pytest.mark.applcm
@pytest.mark.latest
def test0200_post_applcm_nodes_apps(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid):
    """
    # case POST /edgeapps/nodes/{nid}/apps /w {template_id: tid }
    """

    targetHostIp = get_applcm_hostIp()
    print(targetHostIp)
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    print(dicAppTempl) 
    res = post_applcm_edgaapps_templates(0,dicAppTempl)
    print(res)

    node_id = getValidNodeId
    res = get_applcm_edgaapps_templates(0)

    deployedApps = get_applcm_edgaapps_nodes_nid_apps(0,node_id)
    deployedAppIdList = [ app["app_id"] for app in deployedApps ]
    print("get_applcm_edgaapps_templates Resp:%d templates"%len(res))
    for tt in res: 
        if tt["template_name"].find("okdel") >= 0:
            if tt["template_id"] in deployedAppIdList: continue 
            print(f"deploy app to {node_id} /w {tt}")
            dicDeployApp = {"template_id":tt["template_id"]}
            res = post_applcm_edgaapps_nodes_nid_apps(0,node_id,dicDeployApp)
            print(res)
            break
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

@allure.feature('applcm')
@allure.severity('critical')
@pytest.mark.applcm
@pytest.mark.latest
def test0201_post_applcm_nodes_apps_big_image(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid):
    """
    # case POST /edgeapps/nodes/{nid}/apps /w {template_id: tid }
    """

    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForBigImageFile()
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


@allure.feature('applcm')
@allure.severity('critical')
@pytest.mark.applcm
@pytest.mark.latest
def test0202_post_applcm_nodes_apps_err1(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid):
    """
    # case POST /edgeapps/nodes/{nid}/apps /w {template_id: tid } which has malformed metadata
    """


    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()

    dicAppTempl["metadata"] = r"""
cloud_init: 
  -int  
  -oam
"""
    dicAppTempl["userdata"] = None
    
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
    assert inst["state"] == "error"

@allure.feature('applcm')
@allure.severity('critical')
@pytest.mark.applcm
@pytest.mark.latest
def test0210_post_applcm_nodes_apps_networkdata(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid,
        delete_applcm_edgaapps_nodes_nid_apps_aid,
        get_edgaapps_nodes_nid_apps_aid_traffic_rules,
        remove_edgaapps_nodes_nid_ovs_oid_mirror_rule):
    """
    # case POST /edgeapps/nodes/{nid}/apps /w {template_id: tid } with networkdata in app template 
    """

    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    dicAppTempl["networkdata"] = r"""
interfaces:
  - "int"
  - "oam"
traffic_policy:
  type: mirror 
  interfaces:
    - int
    - oam
"""

    dicAppTempl["metadata"] = r"hostname: a%s"%(dicAppTempl["template_name"][-5:])
    dicAppTempl["userdata"] = None 
    # dicAppTempl["networkdata"] = None 
    dicAppTempl["template_name"] = dicAppTempl["template_name"].upper()

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
    assert inst["state"] == "ready"
    time.sleep(5) 
    inst = get_applcm_edgaapps_nodes_nid_apps_aid(0, node_id, dicDeployApp["template_id"])
    print("{}".format(inst))
    assert len(inst["ip_config"]) > 0
    assert len(inst["ip_config"]) == len(inst["networks"])
    time.sleep(5) 
    res = delete_applcm_edgaapps_nodes_nid_apps_aid(2115,node_id,inst["app_id"])
    print(res)
    assert res.find("mirror_rule") > -1
    res = get_edgaapps_nodes_nid_apps_aid_traffic_rules(0,node_id,inst["app_id"])
    print(res)
    for tr in res:
        if "mirror_rule" in tr.keys():
            print(tr)
            print(tr["netconfig"])
            print(tr["netconfig"]["uuid"])
            res = remove_edgaapps_nodes_nid_ovs_oid_mirror_rule(0, node_id, tr["netconfig"]["uuid"])
            print(res)

    time.sleep(1) # this time should be ok 
    res = delete_applcm_edgaapps_nodes_nid_apps_aid(0,node_id,inst["app_id"])
    print(res)

@allure.feature('applcm')
@allure.severity('critical')
@pytest.mark.applcm
@pytest.mark.latest
def test0211_post_applcm_nodes_apps_networkdata_u16docker(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid):
    """
    # case POST /edgeapps/nodes/{nid}/apps /w {template_id: tid } with networkdata in app template 
    """

    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfig("ubuntu.tar")
    dicAppTempl["networkdata"] = r"""
interfaces:
  - "int"
  - "oam"
"""
    dicAppTempl["metadata"] = r"hostname: a%s"%(dicAppTempl["template_name"][-5:])
    dicAppTempl["userdata"] = None 
    # dicAppTempl["networkdata"] = None 

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
    assert inst["state"] == "ready"
    time.sleep(5) 
    inst = get_applcm_edgaapps_nodes_nid_apps_aid(0, node_id, dicDeployApp["template_id"])
    print("{}".format(inst))
    assert len(inst["ip_config"]) > 0

@allure.feature('applcm')
@allure.severity('critical')
@pytest.mark.applcm
@pytest.mark.latest
def test0212_post_applcm_nodes_apps_networkdata_xyz(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid):
    """
    # case POST /edgeapps/nodes/{nid}/apps /w {template_id: tid } with networkdata in app template 
    """

    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    dicAppTempl["networkdata"] = r"""
interfaces:
  - "int"
  - "oam"
  - "xxxyyyzzz_invalide_network_name"
"""
    dicAppTempl["metadata"] = r"hostname: a%s"%(dicAppTempl["template_name"][-5:])
    dicAppTempl["userdata"] = None 
    # dicAppTempl["networkdata"] = None 

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
    time.sleep(3) 
    inst = get_applcm_edgaapps_nodes_nid_apps_aid(0, node_id, dicDeployApp["template_id"])
    print("{}".format(inst))
    assert len(inst["ip_config"]) == 0
    assert inst["state"] == "error"



@allure.feature('applcm')
@allure.severity('critical')
@pytest.mark.applcm
@pytest.mark.latest
def test0221_put_applcm_nodes_apps_networkdata(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        get_applcm_edgaapps_templates_tid,
        put_applcm_edgaapps_templates,
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid):
    """
    # case PUT /edgeapps/nodes/{nid}/apps /w {template_id: tid } with networkdata in app template 
    """

    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    dicAppTempl["metadata"] = r"hostname: a%s"%(dicAppTempl["template_name"][-5:])
    dicAppTempl["userdata"] = r""
    dicAppTempl["networkdata"] = None

    res = post_applcm_edgaapps_templates(0,dicAppTempl)
    print(res)

    t0 = get_applcm_edgaapps_templates_tid(0,res["template_id"])

    updNnetworkdata = r"""interfaces:
  - oam
  - int
"""

    dicPutTempl= {
      "template_name": "modified-"+ t0["template_name"][:12],
      "app_type":  t0["app_type"],
      "images": [
        {
          "image_id": t0["images"][0]["image_id"]
        }
      ],
      "flavor_setting": {
        "vcpu_cores": t0["cores"],
        "memory": t0["memory"],
        "disk": t0["images"][0]["vdisk_size"]
      },
      "metadata": t0["metadata"], 
      "userdata": t0["userdata"],
      "version": t0["version"] if t0["version"] else "1.0",
      "vendor": t0["vendor"] if t0["vendor"] else "faca",
      "description": t0["description"] if t0["description"] else "1",
      "networkdata": updNnetworkdata 
    }
    res = put_applcm_edgaapps_templates(0,t0["template_id"], dicPutTempl)
    print(res)

    node_id = getValidNodeId
    print(f"deploy app to {node_id} /w {dicAppTempl}")
    dicDeployApp = {"template_id": t0["template_id"]}
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
    assert inst["state"] == "ready"
    time.sleep(7) 
    inst = get_applcm_edgaapps_nodes_nid_apps_aid(0, node_id, dicDeployApp["template_id"])
    print("{}".format(inst))
    assert len(inst["ip_config"]) > 0


@allure.feature('applcm')
@allure.severity('critical')
@pytest.mark.applcm
@pytest.mark.latest
def test0203_patch_applcm_nodes__nid__apps_aid_start(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid,
        patch_applcm_edgaapps_nodes_nid_apps_aid,
        applcm_onboard_deploy_start_with_template):

    """
    # case PATCH /edgeapps/nodes/{nid}/apps/{aid} /w { "action" : "start" }
    """

    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()

    res = applcm_onboard_deploy_start_with_template(dicAppTempl)
    print (res)

@allure.feature('applcm')
@allure.severity('critical')
@pytest.mark.applcm
@pytest.mark.latest
def test0204_post_applcm_nodes_apps_secure_vm(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid,
        applcm_onboard_deploy_start_with_template):
    """
    # case POST /edgeapps/nodes/{nid}/apps /w {template_id: tid }
    """

    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForSecureVm()
    if dicAppTempl == None:
        return

    s,node_id,app_id,appMgmIp,appName = applcm_onboard_deploy_start_with_template(dicAppTempl)
    print(f"{s},{node_id},{app_id}, {appMgmIp} {appName}")
    assert appMgmIp != None
    app_id4 = app_id[:4]
    app_id8 = app_id[:8]

    shCmdWget = f"wget -q http://{targetHostIp}:10288/apps/{app_id}/sshkeys -O {app_id4}-sshkeys.tgz"
    r = os.popen(shCmdWget).read()
    print(r)
    shCmdUntar = f"tar xzvf {app_id4}-sshkeys.tgz"
    r = os.popen(shCmdUntar).read()
    print(r)
    wrkDir = r.split("/")[0]
    time.sleep(5)

    rshCmdTest = f"""cd {wrkDir}  && ssh -o ProxyCommand="ssh -o StrictHostKeyChecking=no -i caep-jumper.pem -W %h:%p faca@{targetHostIp}" -o StrictHostKeyChecking=no -i app-{app_id8}.pem faca{app_id4}@{appMgmIp} sudo ip addr && cd ..
    """
    print(rshCmdTest)
    r = os.popen(rshCmdTest).read()
    print(r)

@allure.feature('applcm')
@allure.severity('critical')
@pytest.mark.applcm
@pytest.mark.latest
def test0205_post_applcm_nodes_apps_egsvc_reg_by_others(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid,
        applcm_onboard_deploy_start_with_template):
    """
    # case POST /edgeapps/nodes/{nid}/apps /w {template_id: tid }
    """

    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForSecureVm()
    if dicAppTempl == None:
        return

    s,node_id,app_id,appMgmIp,appName = applcm_onboard_deploy_start_with_template(dicAppTempl)
    print(f"{s},{node_id},{app_id}, {appMgmIp} {appName}")
    assert appMgmIp != None

    app_id4 = app_id[:4]
    app_id8 = app_id[:8]

    shCmdWget = f"wget -q http://{targetHostIp}:10288/apps/{app_id}/sshkeys -O {app_id4}-sshkeys.tgz"
    r = os.popen(shCmdWget).read()
    print(r)
    shCmdUntar = f"tar xzvf {app_id4}-sshkeys.tgz"
    r = os.popen(shCmdUntar).read()
    print(r)
    wrkDir = r.split("/")[0]
    time.sleep(5)

    eaaServices = requests.get(f'http://{targetHostIp}:10282/eaa/services?ItsUrBoss=true').json()
    print(f"{eaaServices}")
    assert appMgmIp not in f"{eaaServices}"

    r = requests.post(f'http://{targetHostIp}:10282/eaa/services/{app_id}/enable')
    print(r)

    eaaServices = requests.get(f'http://{targetHostIp}:10282/eaa/services?ItsUrBoss=true').json()
    assert appMgmIp in f"{eaaServices}"
    assert appName in f"{eaaServices}"

    rndMsg = "{}".format(random.random())
    cmdRunInsideApp = r"""curl -X POST eaaproxy:10282/my/notify -d '{"hello":"%s sent via curl POST inside app"}'"""%(rndMsg)
    rshCmdTest = f"""cd {wrkDir}  && ssh -o ProxyCommand="ssh -o StrictHostKeyChecking=no -i caep-jumper.pem -W %h:%p faca@{targetHostIp}" -o StrictHostKeyChecking=no -i app-{app_id8}.pem faca{app_id4}@{appMgmIp} {cmdRunInsideApp} && cd ..
    """
    print(cmdRunInsideApp)
    r = os.popen(rshCmdTest).read()
    print(r)

    appRtLog = requests.get(f'http://{targetHostIp}:10288/apps/{app_id}/logs').json()
    assert rndMsg in f"{appRtLog}"

    r = requests.delete(f'http://{targetHostIp}:10282/eaa/services/{app_id}/enable?ItsUrBoss=true')
    print(f"DELETE :10282/eaa/services/{app_id}/enable {r} {appName}")

    eaaServices = requests.get(f'http://{targetHostIp}:10282/eaa/services?ItsUrBoss=true').json()
    assert appMgmIp not in f"{eaaServices}"
    assert appName not in f"{eaaServices}"

    print("inside app POST /my/notify again, should be failed because unregistered")
    rshCmdTest = f"""cd {wrkDir}  && ssh -o ProxyCommand="ssh -o StrictHostKeyChecking=no -i caep-jumper.pem -W %h:%p faca@{targetHostIp}" -o StrictHostKeyChecking=no -i app-{app_id8}.pem faca{app_id4}@{appMgmIp} {cmdRunInsideApp} && cd ..
    """
    print(cmdRunInsideApp)
    r = os.popen(rshCmdTest).read()
    print(r)
    assert "Not regisered edge service, so that cannot send notify" in r


@allure.feature('applcm')
@allure.severity('critical')
@pytest.mark.applcm
@pytest.mark.latest
def test0206_post_applcm_nodes_apps_egsvc_reg_byself(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid,
        applcm_onboard_deploy_start_with_template):
    """
    # case POST /edgeapps/nodes/{nid}/apps /w {template_id: tid }
    """

    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForSecureVm()
    if dicAppTempl == None:
        return

    s,node_id,app_id,appMgmIp,appName = applcm_onboard_deploy_start_with_template(dicAppTempl)
    print(f"{s},{node_id},{app_id}, {appMgmIp} {appName}")
    assert appMgmIp != None
    app_id4 = app_id[:4]
    app_id8 = app_id[:8]

    shCmdWget = f"wget -q http://{targetHostIp}:10288/apps/{app_id}/sshkeys -O {app_id4}-sshkeys.tgz"
    r = os.popen(shCmdWget).read()
    print(r)
    shCmdUntar = f"tar xzvf {app_id4}-sshkeys.tgz"
    r = os.popen(shCmdUntar).read()
    print(r)
    wrkDir = r.split("/")[0]
    time.sleep(5)

    cmdRunInsideApp = r"""curl -X POST eaaproxy:10282/eaa/services/me"""
    rshCmdTest = f"""cd {wrkDir}  && ssh -o ProxyCommand="ssh -o StrictHostKeyChecking=no -i caep-jumper.pem -W %h:%p faca@{targetHostIp}" -o StrictHostKeyChecking=no -i app-{app_id8}.pem faca{app_id4}@{appMgmIp} {cmdRunInsideApp} && cd ..
    """
    print(cmdRunInsideApp)

    r = os.popen(rshCmdTest).read()
    print(r)

    eaaServices = requests.get(f'http://{targetHostIp}:10282/eaa/services?ItsUrBoss=true').json()
    print(f"{eaaServices}")
    assert appMgmIp in f"{eaaServices}"
    assert appName in f"{eaaServices}"

    rndMsg = "{}".format(random.random())
    cmdRunInsideApp = r"""curl -X POST eaaproxy:10282/my/notify -d '{"hello":"%s sent via curl POST inside app"}'"""%(rndMsg)
    rshCmdTest = f"""cd {wrkDir}  && ssh -o ProxyCommand="ssh -o StrictHostKeyChecking=no -i caep-jumper.pem -W %h:%p faca@{targetHostIp}" -o StrictHostKeyChecking=no -i app-{app_id8}.pem faca{app_id4}@{appMgmIp} {cmdRunInsideApp} && cd ..
    """
    print(cmdRunInsideApp)
    r = os.popen(rshCmdTest).read()
    print(r)

    appRtLog = requests.get(f'http://{targetHostIp}:10288/apps/{app_id}/logs').json()
    assert rndMsg in f"{appRtLog}"

    cmdRunInsideApp = r"""curl -v -X DELETE eaaproxy:10282/eaa/services/me"""
    rshCmdTest = f"""cd {wrkDir}  && ssh -o ProxyCommand="ssh -o StrictHostKeyChecking=no -i caep-jumper.pem -W %h:%p faca@{targetHostIp}" -o StrictHostKeyChecking=no -i app-{app_id8}.pem faca{app_id4}@{appMgmIp} {cmdRunInsideApp} && cd ..
    """
    print(cmdRunInsideApp)
    r = os.popen(rshCmdTest).read()
    print(r)

    cmdRunInsideApp = r"""curl -X POST eaaproxy:10282/my/notify -d '{"hello":"%s sent via curl POST inside app"}'"""%(rndMsg)
    print("inside app POST /my/notify again, should be failed because unregistered")
    rshCmdTest = f"""cd {wrkDir}  && ssh -o ProxyCommand="ssh -o StrictHostKeyChecking=no -i caep-jumper.pem -W %h:%p faca@{targetHostIp}" -o StrictHostKeyChecking=no -i app-{app_id8}.pem faca{app_id4}@{appMgmIp} {cmdRunInsideApp} && cd ..
    """
    print(cmdRunInsideApp)
    r = os.popen(rshCmdTest).read()
    print(r)
    assert "Not regisered edge service, so that cannot send notify" in r

@allure.feature('applcm')
@allure.severity('critical')
@pytest.mark.applcm
@pytest.mark.latest
def test0207_post_applcm_nodes_apps_egsvc_addVbr1028(get_applcm_hostIp,
        post_applcm_edgaapps_templates,
        getValidNodeId, 
        get_applcm_edgaapps_templates, 
        post_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid,
        applcm_onboard_deploy_start_with_template):
    """
    # case POST /edgeapps/nodes/{nid}/apps /w {template_id: tid }
    """

    targetHostIp = get_applcm_hostIp()
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForSecureVm()
    if dicAppTempl == None:
        return

    s,node_id,app_id,appMgmIp,appName = applcm_onboard_deploy_start_with_template(dicAppTempl)
    print(f"{s},{node_id},{app_id}, {appMgmIp} {appName}")
    assert appMgmIp != None
    app_id4 = app_id[:4]
    app_id8 = app_id[:8]

    shCmdWget = f"wget -q http://{targetHostIp}:10288/apps/{app_id}/sshkeys -O {app_id4}-sshkeys.tgz"
    r = os.popen(shCmdWget).read()
    print(r)
    shCmdUntar = f"tar xzvf {app_id4}-sshkeys.tgz"
    r = os.popen(shCmdUntar).read()
    print(r)
    wrkDir = r.split("/")[0]
    time.sleep(5)

    clientIp = os.environ.get("clientIp","192.168.82.229")

    cmdRunInsideApp = r"""ping -c 10 %s"""%(clientIp)
    rshCmdTest = f"""cd {wrkDir}  && ssh -o ProxyCommand="ssh -o StrictHostKeyChecking=no -i caep-jumper.pem -W %h:%p faca@{targetHostIp}" -o StrictHostKeyChecking=no -i app-{app_id8}.pem faca{app_id4}@{appMgmIp} {cmdRunInsideApp} && cd ..
    """
    print(cmdRunInsideApp)

    r = os.popen(rshCmdTest).read()
    print(r)
    assert "ttl=" in r

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0300_get_applcm_nodes_apps(get_applcm_edgaapps_nodes):
    """
    # case GET /edgeapps/nodes
    """
    res = get_applcm_edgaapps_nodes(0)
    dicNodeApps = {}
    dicDupApps = {}
    for inst in res:
        eaId = inst["hostname"] + "/"+ inst["app_id"]
        if eaId not in dicDupApps.keys():
            dicDupApps[eaId] = 1
        else:
            dicDupApps[eaId] += 1

        if inst["node_id"]+"/"+inst["hostname"] in dicNodeApps.keys():
            dicNodeApps[inst["node_id"]+"/"+inst["hostname"]] += 1
        else:
            dicNodeApps[inst["node_id"]+"/"+inst["hostname"]] = 1
        assert inst["node_id"] != ""
        assert inst["hostname"] != ""
        assert inst["app_id"] != ""
        assert inst["app_name"] != ""
        assert inst["flavor"] != ""
        assert inst["app_type"] in ["vm","container"]
        assert inst["ip_config"] != None
    totalApps = 0
    for nid,napps in dicNodeApps.items():
        print(f"# of deployed apps in {nid} is {napps}")
        totalApps += napps
    assert len(res) == totalApps
    for k,v in dicDupApps.items():
        print(f"{k} {v}")


@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0301_get_applcm_v1_edgeapps_nodes__node_id__apps__ok(getValidNodeId, get_applcm_edgaapps_nodes_nid_apps):
    """
    # case GET /edgeapps/nodes/{node_id}/apps
    """
    node_id = getValidNodeId
    res = get_applcm_edgaapps_nodes_nid_apps(0,node_id)
    for inst in res:
        assert inst["node_id"] != ""
        assert inst["hostname"] != ""
        assert inst["app_id"] != ""
        assert inst["app_name"] != ""
        assert inst["flavor"] != ""
        assert inst["app_type"] in ["vm","container"]
        assert inst["ip_config"] != None


@allure.feature('applcm')
@allure.feature('negative_test')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0302_get_applcm_v1_edgeapps_nodes__node_id__apps__fail_1(get_applcm_edgaapps_nodes_nid_apps):
    """
    # case GET /edgeapps/nodes/{node_id}/apps with invlid node_id
    """
    res = get_applcm_edgaapps_nodes_nid_apps(err_code=2102,node_id="invalid-node_id")
    print (res)

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0303_get_applcm_v1_edgeapps_nodes__node_id__apps__aid_ok(getValidNodeId, 
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid):

    """
    # case GET /edgeapps/nodes/{node_id}/apps/{app_id}
    """
    node_id = getValidNodeId
    res = get_applcm_edgaapps_nodes_nid_apps(0,node_id)
    for aa in res:
        
        if aa["state"] != "deploying":
            inst = get_applcm_edgaapps_nodes_nid_apps_aid(0, node_id, aa["app_id"])
            assert inst["node_id"] != ""
            assert inst["hostname"] != ""
            assert inst["app_id"] != ""
            assert inst["app_name"] != ""
            assert inst["flavor"] != ""
            assert inst["app_type"] in ["vm","container"]
            assert inst["state"] in ["unknown", "deploying", "ready", "starting", "running", "stopping", "stopped", "error"]
            assert inst["ip_config"] != None

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0304_get_applcm_v1_edgeapps_nodes__node_id__apps__aid_fail_1(getValidNodeId, 
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid):

    """
    # case GET /edgeapps/nodes/{node_id}/apps/{app_id} with invalid app_id
    """
    node_id = getValidNodeId
    res = get_applcm_edgaapps_nodes_nid_apps_aid(2103, node_id, "invalid-app-id-xxxyyyzzz")
    print (res)

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0305_get_applcm_v1_edgeapps_nodes__node_id__apps__aid_logs(getValidNodeId, 
        get_applcm_edgaapps_nodes_nid_apps,
        get_applcm_edgaapps_nodes_nid_apps_aid_logs):

    """
    # case GET /edgeapps/nodes/{node_id}/apps/{app_id}.logs for retrieving edge app's life log started from deploy
    """

    node_id = getValidNodeId
    res = get_applcm_edgaapps_nodes_nid_apps(0,node_id)
    for aa in res:
        res2 = get_applcm_edgaapps_nodes_nid_apps_aid_logs(0, node_id, aa["app_id"])
        print (res2)

@allure.feature('applcm')
@allure.feature('negative_test')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0306_get_applcm_v1_edgeapps_nodes__node_id__apps__brief(getValidNodeId,get_applcm_edgaapps_nodes_nid_apps_brief):
    """
    # case GET /edgeapps/nodes/{node_id}/apps?briefSummar=true
    """
    node_id = getValidNodeId
    res = get_applcm_edgaapps_nodes_nid_apps_brief(0,node_id)
    print (res)
    assert res["hostname"] != ""
    assert res["node_id"] == node_id
    assert res["num_deployed_apps"] >= 0
    assert res["num_running_apps"] >= 0
    assert res["vcpu_total"] > 0
    assert res["vcpu_used"] > 0
    assert res["mem_total_mb"] >= 0
    assert res["mem_used_mb"] >= 0
    assert res["hugepage_total_gb"] >= 0
    assert res["hugepage_used_gb"] >= 0
    assert res["swap_total_mb"] >= 0
    assert res["swap_used_mb"] >= 0
    assert res["homedisk_total_gb"] > 0.0
    assert res["homedisk_used_gb"] > 0.0
    assert res["rootdisk_total_gb"] > 0.0
    assert res["rootdisk_used_gb"] > 0.0
    assert res["vmapp_quota_total_gb"] >= 0

    """
{'homedisk_total_gb': 3481.6, 'homedisk_used_gb': 25, 'hostname': 'dell730', 'hugepage_total_gb': 48, 'hugepage_used_gb': 18, 'mem_total_mb': 64206, 'mem_used_mb': 56840, 'node_id': '03aeacbd-546c-49e5-b780-0ea503a0a43d', 'num_deployed_apps': 14, 'num_running_apps': 4, 'rootdisk_total_gb': 50, 'rootdisk_used_gb': 8.9, 'swap_total_mb': 0, 'swap_used_mb': 0, '': 20, '': 20, 'vmapp_quota_total_gb': 64}
    """

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0400_del_applcm_v1_edgeapps_nodes__node_id__apps__aid(getValidNodeId, get_applcm_edgaapps_nodes_nid_apps, delete_applcm_edgaapps_nodes_nid_apps_aid):
    """
    # case DELETE /edgeapps/nodes/{node_id}/apps/{app_id}
    """
    node_id = getValidNodeId
    res = get_applcm_edgaapps_nodes_nid_apps(0,node_id)
    for inst in res:
        if re.search("okdel", inst["app_name"],re.IGNORECASE) and inst["state"] not in ["deploying","starting","stopping"]:
            res = delete_applcm_edgaapps_nodes_nid_apps_aid(0,node_id,inst["app_id"])
            print(f"{res} " + inst["app_name"] + " " + inst["app_id"])

    time.sleep(3)
    res = get_applcm_edgaapps_nodes_nid_apps(0,node_id)
    deleteFailCount = 0
    for inst in res:
        if inst["app_name"].find("okdel") >= 0 and inst["state"] not in ["deploying","starting","stopping"]:
            print(inst)
            deleteFailCount += 1 
    assert deleteFailCount == 0


@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0401_del_applcm_edgaapps_templates(get_applcm_hostIp, get_applcm_edgaapps_templates, delete_applcm_edgaapps_templates_tid):
    """
    # case DELETE /applcm/v1/edgeapps/templates/{tmplate_id} for those name starts with 'okdel" 
    """    

    targetHostIp = get_applcm_hostIp()
    respAllTemplates = requests.get(f'http://{targetHostIp}:10286/applcm/v1/edgeapps/templates')
    if respAllTemplates.status_code == 200:
        lstTemplates = respAllTemplates.json()
        print("all templates in applcmdb.app_templates: %d"%(len(lstTemplates))) 
        nDeleted = 0
        for tt in lstTemplates[500:]: 
            if re.search("okdel", tt["template_name"],re.IGNORECASE):
                res = delete_applcm_edgaapps_templates_tid(0,tt["template_id"])
                assert res["err_code"] == 0
                nDeleted += 1 

        respAllTemplates2 = requests.get(f'http://{targetHostIp}:10286/applcm/v1/edgeapps/templates')
        lstTemplates2 = respAllTemplates2.json()
        assert len(lstTemplates) ==  len(lstTemplates2) + nDeleted

    res = get_applcm_edgaapps_templates(0)
    print("get_applcm_edgaapps_templates Resp:%d templates"%len(res))
    for tt in res: 
        if re.search("okdel", tt["template_name"],re.IGNORECASE):
            print (tt)
            image_id = tt["images"][0]["image_id"]
            resp0 = requests.get(f'http://{targetHostIp}:9292/image_mgmt/v1/images/{image_id}/refcount')
            print(f"before adding new app template, image {image_id} refcount",resp0.content)
            refcount0 = resp0.json()["refcount"]

            res = delete_applcm_edgaapps_templates_tid(0,tt["template_id"])
            print(res)
            resp1 = requests.get(f'http://{targetHostIp}:9292/image_mgmt/v1/images/{image_id}/refcount')
            print(f"before adding new app template, image {image_id} refcount",resp1.content)
            refcount1 = resp1.json()["refcount"]
            assert refcount0 == refcount1+1

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0501_get_applcm_edgaapps_nodes_vdisks(get_applcm_hostIp, getValidNodeId, get_applcm_edgaapps_nodes_nid_vdisks):
    """
    # case GET /applcm/v1/edgeapps/nodes/{nid}/vdisks 
    """    
    targetHostIp = get_applcm_hostIp()
    node_id = getValidNodeId

    dicRet = get_applcm_edgaapps_nodes_nid_vdisks(0,node_id)
    #resp0 = requests.get(f'http://{targetHostIp}:10286/applcm/v1/edgeapps/nodes/{node_id}/vdisks')
    #dicRet = resp0.json()
    assert "pdisks" in dicRet.keys()
    print(dicRet["pdisks"])
    assert "vdisks" in dicRet.keys()
    for vd in dicRet["vdisks"]:
        assert vd["vdisk_name"].startswith("pd")
        assert vd["vdisk_size_gb"] in [128,256,512,1024,2048]
        if vd["vdisk_attached_to"] == "":
            assert vd["vdisk_used_by"] == ""
        else:
            assert vd["vdisk_used_by"] != ""
        print(vd)

    assert "pdisks_sum" in dicRet.keys()
    print(dicRet["pdisks_sum"])

@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0502_post_applcm_edgaapps_nodes_vdisks(get_applcm_hostIp, getValidNodeId,get_applcm_edgaapps_nodes_nid_vdisks, post_applcm_edgaapps_nodes_nid_vdisks):
    """
    # case POST /applcm/v1/edgeapps/nodes/{nid}/vdisks
    """    
    targetHostIp = get_applcm_hostIp()
    node_id = getValidNodeId

    dic0 = get_applcm_edgaapps_nodes_nid_vdisks(0,node_id)
    print(dic0["pdisks_sum"])
    remaining = dic0["pdisks_sum"]["total_gb"] - dic0["pdisks_sum"]["used_gb"]

    sizeReq = 128
    dic1 = {"at_phydisk":"pd1","size_gb_req":sizeReq ,"vdisk_desc":f"okdel-vdisk-{sizeReq}"}

    if sizeReq < remaining:
        dic2 = post_applcm_edgaapps_nodes_nid_vdisks(0,node_id,dic1)
        print(f"POST {dic1} got {dic2}")
        assert dic2["vdisk_name"] != ""
        assert dic2["vdisk_size_gb"] == sizeReq 
        assert dic2["vdisk_attached_to"] == ""
        assert dic2["vdisk_used_by"] == ""
        dic3 = get_applcm_edgaapps_nodes_nid_vdisks(0,node_id)
        assert dic3["pdisks_sum"]["used_gb"] == sizeReq + dic0["pdisks_sum"]["used_gb"]
    else:
        dic2 = post_applcm_edgaapps_nodes_nid_vdisks(2135,node_id,dic1)
        print(f"POST {dic1} got {dic2}")
        assert dic2.find("not enough") > 0


@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0503_patch_applcm_edgaapps_nodes_vdisks_vdname(get_applcm_hostIp, getValidNodeId,get_applcm_edgaapps_nodes_nid_vdisks, applcm_onboard_deploy_start_with_template, applcm_onboard_deploy_app_with_template, post_applcm_edgaapps_nodes_nid_vdisks,patch_applcm_edgaapps_nodes_nid_apps_aid_vdisks,delete_applcm_edgaapps_nodes_nid_apps_aid,delete_applcm_edgaapps_templates_tid):
    """
    # case PATCH /applcm/v1/edgeapps/nodes/{nid}/apps/{aid}/vdisks attach case
    """    
    targetHostIp = get_applcm_hostIp()
    node_id = getValidNodeId

    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    t1,t2,app_id = applcm_onboard_deploy_app_with_template(dicAppTempl)
    time.sleep(1)
    dicAppTempl = ApplcmHelper(targetHostIp).getAppTemplConfigForCirros()
    t1,t2,app_id2_running,_,_ = applcm_onboard_deploy_start_with_template(dicAppTempl)
    assert t1 == "ok"

    dic0 = get_applcm_edgaapps_nodes_nid_vdisks(0,node_id)
    remaining = dic0["pdisks_sum"]["total_gb"] - dic0["pdisks_sum"]["used_gb"]
    print(dic0["pdisks_sum"])
    vdAvail = None
    for vd in dic0["vdisks"]:
        if vd["vdisk_desc"].find("okdel") == -1: 
            continue
        if vd["vdisk_used_by"] == "":
            vdAvail = vd
            break

    if vdAvail == None:
        sizeReq = 128
        dic1 = {"at_phydisk":"pd1","size_gb_req":sizeReq ,"vdisk_desc":f"okdel-vdisk-{sizeReq}"}
        dic2 = post_applcm_edgaapps_nodes_nid_vdisks(0,node_id,dic1)
        print(f"POST {dic1} got {dic2}")
        assert dic2["vdisk_name"] != ""
        assert dic2["vdisk_size_gb"] == sizeReq 
        assert dic2["vdisk_attached_to"] == ""
        assert dic2["vdisk_used_by"] == ""
        dic3 = get_applcm_edgaapps_nodes_nid_vdisks(0,node_id)
        assert dic3["pdisks_sum"]["used_gb"] == sizeReq + dic0["pdisks_sum"]["used_gb"]

    # iterate again
    dic0 = get_applcm_edgaapps_nodes_nid_vdisks(0,node_id)
    for vd in dic0["vdisks"]:
        if vd["vdisk_desc"].find("okdel") == -1: 
            continue
        if vd["vdisk_used_by"] == "":
            dic2 = vd
            dic4 = {"vdisk_op":"attach", "vdisk_name": dic2["vdisk_name"] }
            res5 = patch_applcm_edgaapps_nodes_nid_apps_aid_vdisks(2134,node_id,app_id2_running,dic4)
            print(f"{res5}")
            assert res5.find("failed, please stop the App") > 0 or res5.find("INACTIVE")
            res5 = patch_applcm_edgaapps_nodes_nid_apps_aid_vdisks(0,node_id,app_id,dic4)
            print(f"{res5}")

            res5 = patch_applcm_edgaapps_nodes_nid_apps_aid_vdisks(2134,node_id,app_id,dic4)
            print(f"{res5}")
            print( res5.find("already attached") > 0)
            assert res5.find("already attached") > 0
            break

    res = delete_applcm_edgaapps_nodes_nid_apps_aid(0,node_id,app_id)
    res = delete_applcm_edgaapps_nodes_nid_apps_aid(0,node_id,app_id2_running)

    delete_applcm_edgaapps_templates_tid(0,app_id)
    delete_applcm_edgaapps_templates_tid(0,app_id2_running)


@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0504_patch_applcm_edgaapps_nodes_vdisks_vdname(get_applcm_hostIp, getValidNodeId,get_applcm_edgaapps_nodes_nid_vdisks, applcm_onboard_deploy_start_with_template, applcm_onboard_deploy_app_with_template, post_applcm_edgaapps_nodes_nid_vdisks,patch_applcm_edgaapps_nodes_nid_apps_aid_vdisks,get_applcm_edgaapps_nodes_nid_apps_aid):
    """
    # case PATCH /applcm/v1/edgeapps/nodes/{nid}/apps/{aid}/vdisks detach case
    """    
    targetHostIp = get_applcm_hostIp()
    node_id = getValidNodeId

    dicRet = get_applcm_edgaapps_nodes_nid_vdisks(0,node_id)
    for vd in dicRet["vdisks"]:
        if vd["vdisk_name"].find("okdel") > 0: 
            continue
        print(f"{vd}")
        if vd["vdisk_used_by"] != "": 
            app_id = vd["vdisk_used_by"]
            dic4 = {"vdisk_op":"detach", "vdisk_name": vd["vdisk_name"] }
            inst = get_applcm_edgaapps_nodes_nid_apps_aid(0, node_id, app_id)

            if inst["state"] in [ "starting", "running", "stopping"]:
                res5 = patch_applcm_edgaapps_nodes_nid_apps_aid_vdisks(2134,node_id,app_id,dic4)
            else:
                res5 = patch_applcm_edgaapps_nodes_nid_apps_aid_vdisks(0,node_id,app_id,dic4)
            print(f"{res5}")


@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
def test0509_delete_applcm_edgaapps_nodes_vdisks_vdiskname(get_applcm_hostIp, getValidNodeId,get_applcm_edgaapps_nodes_nid_vdisks, delete_applcm_edgaapps_nodes_nid_vdisks_vdname):
    # case DELETE /applcm/v1/edgeapps/nodes/{nid}/vdisks/{vdname}
    targetHostIp = get_applcm_hostIp()
    node_id = getValidNodeId
    #resp0 = requests.get(f'http://{targetHostIp}:10286/applcm/v1/edgeapps/nodes/{node_id}/vdisks')
    dicRet = get_applcm_edgaapps_nodes_nid_vdisks(0,node_id)
    print(dicRet["pdisks"])
    okdelExist = False
    isAttached = False
    for vd in dicRet["vdisks"]:
        if vd["vdisk_desc"].find("okdel") == -1:
            continue
        vdname = vd["vdisk_name"]
        if vd["vdisk_attached_to"] != "":
            dicRet1 = delete_applcm_edgaapps_nodes_nid_vdisks_vdname(2136,node_id,vdname)
            dicRet2 = get_applcm_edgaapps_nodes_nid_vdisks(0,node_id)
            assert  dicRet2["pdisks_sum"]["used_gb"] == dicRet["pdisks_sum"]["used_gb"]
        else:
            dicRet1 = delete_applcm_edgaapps_nodes_nid_vdisks_vdname(0,node_id,vdname)
            dicRet2 = get_applcm_edgaapps_nodes_nid_vdisks(0,node_id)
            assert  dicRet2["pdisks_sum"]["used_gb"] == dicRet["pdisks_sum"]["used_gb"] - vd["vdisk_size_gb"]
        print(f"{dicRet1} {vdname} deletion")
        break


@pytest.mark.usefixtures("db_class")
@allure.feature('applcm')
@allure.severity('normal')
@pytest.mark.applcm
@pytest.mark.latest
class TestAppLCM(unittest.TestCase):

    GKH = None

    @pytest.fixture(autouse=True)
    def _pass_fixture_value(self, hostIP):
        self._hostIP = hostIP

    @pytest.fixture(autouse=True)
    def _get_cmdoption_ip_address(self, applcm_api_pre,applcm_api_via_gatekeeper):
        self.test_api_prefix = applcm_api_pre
        self.test_api_prefix_gk = applcm_api_via_gatekeeper
        TestAppLCM.test_api_prefix_gk = applcm_api_via_gatekeeper

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.PH={"content-type":"application/json;charset=UTF-8"}
        print(self._hostIP)

        self.test_api_prefix = self.test_api_prefix_gk 

        if TestAppLCM.GKH is None:
            r = requests.post(self.test_api_prefix_gk+"/auth",headers=self.PH,data=json.dumps({"name":"user","password":"123456"}))
            print("POST "+self.test_api_prefix_gk+"/auth")
            dicRet =  r.json()
            print(dicRet)
            GKH={"content-type":"application/json","Authorization":"Bearer " + dicRet["data"]["token"]} 
            TestAppLCM.GKH = GKH
            self.GKH = GKH.copy() 

        self.__get_valid_image_id()
        imgName = "cirros-pre-upload"
        needUploadImage = True
        for ii in self.lstImagesCache:
            if ii["name"].find(imgName) >= 0:
                needUploadImage = False
                break
            if ii["file"].find("cirros") >= 0:
                needUploadImage = False
                break

        if needUploadImage:
            cirrosFilenamePreUload = "cirros-test.img"
            upImg = r"""#!/bin/bash
curl -v -i -X POST -H "Content-Type: multipart/form-data" \
     -F "metadata={\"name\": \"%s\", \"type\": \"vm\", \"file\": \"%s\"};type=application/json" \
     -F "media=@%s; filename=%s" http://%s:9292/image_mgmt/v1/images
"""%(imgName ,cirrosFilenamePreUload, cirrosFilenamePreUload, cirrosFilenamePreUload, self._hostIP)
            print(upImg)
            mybashscript = "upload-cirros-img.sh"
            open(mybashscript ,"w").write(upImg)
            p = subprocess.Popen(["/bin/bash",mybashscript], stdout=subprocess.PIPE)
            cout,cerr = p.communicate()
            print(cout)

    def tearDown(self):
        pass


    def getAppTemplConfigForCirros(self):

        self.__get_valid_image_id()
        image_id = "gi-cirros"
        for ii in self.lstImagesCache:
            if ii["file"].find("cirros") >= 0:
                image_id = ii["id"]
                print("GOT FEPC CPF image!!!!!!!!"+image_id)
                break

        udata = r"""
write_files:
  xxx: 1234
"""
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
            "vcpu_cores": 4,
            "memory": 4,
            "disk": 80
          },
          "metadata": "ovs_network: \n  - int\n  - xhaul\n  - oam\n",
          "userdata": udata,
          "version": "1.0",
          "vendor": "faca",
          "description": "cpf-vm"
        }
        return dicAppTempl

    def app_onboard_with_template(self, dicAppTempl):

        targetUri=f'{self.test_api_prefix}/edgeapps/templates'
        print("POST "+targetUri + f" /w\n{dicAppTempl}")
        resp = requests.post(targetUri, \
                data=json.dumps(dicAppTempl),   \
                headers=self.GKH)
        print(resp.content)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

    def __app_onboard_deploy_with_template(self, dicAppTempl):


        targetUri=f'{self.test_api_prefix}/edgeapps/templates'
        print("POST "+targetUri + f" /w\n{dicAppTempl}")
        resp = requests.post(targetUri, \
                data=json.dumps(dicAppTempl),   \
                headers=self.GKH)
        print(resp.content)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        template_id = dicRet["data"]["template_id"]

        nid = self.__get_valid_node_id()
        node_id = nid
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps'
        dicPostData={"template_id": template_id }
        print("POST "+targetUri +f" /w {dicPostData}")
        resp = requests.post(targetUri, \
                data=json.dumps(dicPostData),   \
                headers=self.GKH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        print("="*32)
        
        app_id = template_id
        retry = 0
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps'
        while retry < 999:
            time.sleep(1)
            resp = requests.get(targetUri, headers=self.GKH)
            dicRet = resp.json()
            try:
                for aa in dicRet["data"]:
                    if aa["app_id"] == app_id:
                        if True: # retry % 10 == 0:
                            print(f'{retry} GET '+aa["state"] + ' '+ aa["app_name"] + ' '+ aa["app_id"])
                        if aa["state"] in [ "ready","error" ]: 
                            retry = 1000 # to break outer loop
                            break
            except:
                import sys, traceback
                if retry % 3 == 0:
                    print(f'{retry} GET '+ targetUri) 
                    print("{} {}".format(sys.exc_info(), traceback.format_exc()))
                pass
            retry = retry + 1

        print("="*32)

    def app_onboard_deploy_start_with_template(self, dicAppTempl):

        self.__app_onboard_deploy_with_template(dicAppTempl)

        node_id = self.__get_valid_node_id()
        app_id = dicAppTempl["template_id"]

        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
        dicPatchNodeApps = {"action":"start"}
        print('PATCH '+targetUri + f' /w\n{dicPatchNodeApps}')
        resp = requests.patch(targetUri,    \
                data=json.dumps(dicPatchNodeApps),  \
                headers=self.GKH)
        print(resp.content)
        print("="*32)
