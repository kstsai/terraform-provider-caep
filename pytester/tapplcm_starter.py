import allure
import json
import pytest
import random
import re
import requests
import time
import unittest
import warnings


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


class Cfg(object):

    def __init__(self,targetHostIp):
        self.PH={"content-type":"application/json;charset=UTF-8"}
        self._hostIP = targetHostIp
        self.test_api_prefix = f"http://{targetHostIp}:5666/gatekeeper/v1"
        self.image_id = self.__get_valid_image_id()
        self.node_id = self.__get_valid_node_id()
        self.__getGatekeeperToken()

    def __get_valid_image_id(self):
        resp = requests.get(f'http://{self._hostIP}:9292/image_mgmt/v1/images?type=vm')
        lstRet = resp.json()
        self.lstImagesCache = lstRet[:]
        if len(lstRet) > 0:
            return lstRet[0]["id"]
        return "ci-cirros"

    def __get_valid_node_id(self):
        # case GET /health
        resp = requests.get(f'http://{self._hostIP}:10286/health')
        print(resp.content)
        dicRet = resp.json()
        for l in dicRet["message"].split(","):
            print(l)
            if l.startswith("node_id"):
                return l.split("=")[1]

    def __getGatekeeperToken(self):
        targetUri = self.test_api_prefix+"/auth"
        r = requests.post(targetUri,headers=self.PH,data=json.dumps({"name":"user","password":"123456"}))
        print("POST "+targetUri)
        dicRet =  r.json()
        self.GKH={"content-type":"application/json;charset=UTF-8","Authorization":"Bearer " + dicRet["data"]["token"]} 
        print(self.GKH)

    def getAppTemplConfig(self):

        for ii in self.lstImagesCache:
            if ii["file"].find("vnfs_director") > 0:
                image_id = ii["id"]
 
                break

        return self.getAppTemplConfigForCirros()


    def getAppTemplConfigForCirros(self):

        for ii in self.lstImagesCache:
            if ii["file"].find("cirros") > 0:
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
        image_id = cfg.image_id
        rnd_appName = "okdel-{}".format(random.random())
        dicPostTempl= {
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
          "metadata": "ovs_network: \n  - int\n  - xhaul\n  - oam\n",
          #"userdata": "write_file:\n  xyz: %s\n"%(rnd_appName),
          "userdata": udata,
          "version": "1.0",
          "vendor": "faca",
          "description": "curror-testvm"
        }
        return dicPostTempl


    def getAppTemplConfigForTmLogProcessor(self):

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
        dicPostTempl= {
          "template_name": "tm-logp", 
          "app_type": "vm",
          "images": [
            {
              "image_id": "4d198446-a072-4ea3-8610-aa0d5a0ffd80"
            }
          ],
          "flavor_setting": {
            "vcpu_cores": 4,
            "memory": 8,
            "disk": 80
          },
          "metadata": "ovs_network: \n  - int\n  - xhaul\n  - oam\n",
          #"userdata": "write_file:\n  xyz: %s\n"%(rnd_appName),
          "userdata": udata,
          "version": "1.0",
          "vendor": "faca",
          "description": "Logprocessor"
        }
        return dicPostTempl

    def getAppTemplConfigForTmDirector(self):

        udata = r"""
write_files:
- content: |
    web:
      server:
        scheme: https
        port: 443
        timeout : 60000

    vnfc:
      server:
        port: 5570
    logprocessor_endpts:
      - logprocessor
    es_cluster:
      - logprocessor
    activation_code: VN-XNFF-MQ6HD-W4LBA-TWGH3-5UALH-S2UGQ
  path: /home/zeta/init.yaml

- content: |
    system:
      ddns: 192.168.122.1
      internet_dns: 192.168.122.1
  path: /home/init.yaml
"""

        dicPostTempl= {
          "template_name": "tm-director", 
          "app_type": "vm",
          "images": [
            {
              "image_id": image_id
            }
          ],
          "flavor_setting": {
            "vcpu_cores": 2,
            "memory": 4,
            "disk": 80
          },
          "metadata": "ovs_network: \n  - int\n  - xhaul\n  - oam\n",
          #"userdata": "write_file:\n  xyz: %s\n"%(rnd_appName),
          "userdata": udata,
          "version": "1.0",
          "vendor": "faca",
          "description": "Director"
        }
        return dicPostTempl

    def getAppTemplConfigForTmInspector(self):

        udata = r"""
hostname: BVT_generic

manage_resolv_conf: true
resolv_conf:
  nameservers: ['192.168.122.1', '8.8.8.8', '168.95.1.1']
  searchdomains:
    - trend.com
  domain: trend.com.tw

write_files:
  - path: /var/lib/vnf/udata/init.yaml
    content: |
      logprocessor_endpts:
        - vlps:9093
      director_ip: vnfs-director
      uuid: deadbeef-dead-beef-dead-beefdead7573
      port_cfgs:
        role:
          - 0: sfc
  - path: /var/lib/vnf/udata/vendor.json
    content: |
      {"serial_number":"VM010011703111111",
        "model":"vc1000",
        "vendor":{
          "vendor_info":{
            "vendor_short":"Generic",
            "vendor_long":"Generic Vendor"
          },
          "vendor_cfg":{
          }
        },
        "signature":"43b286219b2ba5ee033f0a01bef64627"
      }
"""
        dicPostTempl= {
          "template_name": "tm-inspector", 
          "app_type": "vm",
          "images": [
            {
              "image_id": "e343b7dd-8539-421b-a80b-83f7ccb74ff2"
            }
          ],
          "flavor_setting": {
            "vcpu_cores": 8,
            "memory": 12,
            "disk": 80
          },
          "metadata": "ovs_network: \n  - int\n  - xhaul\n  - oam\n",
          #"userdata": "write_file:\n  xyz: %s\n"%(rnd_appName),
          "userdata": udata,
          "version": "1.0",
          "vendor": "faca",
          "description": "Inspector"
        }
        return dicPostTempl


def test60_full_api_flow(cfg):

    # dicPostTempl = cfg.getAppTemplConfigForTmInspector()
    # dicPostTempl = cfg.getAppTemplConfigForTmDirector()
    dicPostTempl = cfg.getAppTemplConfigForCirros()

    targetUri=f'{cfg.test_api_prefix}/edgeapps/templates'
    print("POST "+targetUri)
    resp = requests.post(targetUri, \
            data=json.dumps(dicPostTempl),   \
            headers=cfg.GKH)
    print(resp.content)
    dicRet = resp.json()
    template_id = dicRet["data"]["template_id"]

    node_id = cfg.node_id 
    targetUri = f'{cfg.test_api_prefix}/edgeapps/nodes/{node_id}/apps'
    dicPostData={"template_id": template_id }
    print("POST "+targetUri +f" /w {dicPostData}")
    resp = requests.post(targetUri, \
            data=json.dumps(dicPostData),   \
            headers=cfg.GKH)
    print(resp.content)
    
    app_id = template_id
    retry = 0
    targetUri = f'{cfg.test_api_prefix}/edgeapps/nodes/{node_id}/apps'
    while retry < 999:
        time.sleep(1)
        resp = requests.get(targetUri, headers=cfg.GKH)
        dicRet = resp.json()
        if dicRet == None: continue
        for aa in dicRet["data"]:
            if aa["app_id"] == app_id:
                print(f'{retry} GET '+aa["state"])
                if aa["state"] in [ "ready","error" ]: 
                    retry = 1000 # to break outer loop
                    break
        retry = retry + 1

    targetUri = f'{cfg.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
    print('PATCH '+targetUri)
    resp = requests.patch(targetUri,    \
            data=json.dumps({"action":"start"}),   \
            headers=cfg.GKH)
    print(resp.content)
    appStartedOK = False
    retry = 0
    targetUri = f'{cfg.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
    print("GET " +targetUri)
    dicRet = {}
    while retry < 999:
        time.sleep(1)
        resp = requests.get(targetUri, headers=cfg.GKH)
        dicRet = resp.json()["data"]
        print(f'{retry} GET '+dicRet["state"])
        if dicRet["state"] in [ "running","error" ]: break
        retry = retry + 1

    if dicRet["state"] == "running":
        targetUri = f'{cfg.test_api_prefix}/networks/nodes/{node_id}/apps/{app_id}'
        resp2 = requests.get(targetUri, headers=cfg.GKH)
        print(resp2.content)

if __name__ == "__main__":
    import sys

    targetHostIp = sys.argv[1]
    print(targetHostIp)

    cfg = Cfg(targetHostIp)
    test60_full_api_flow(cfg)
