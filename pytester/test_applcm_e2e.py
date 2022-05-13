import allure
import json
import pytest
import random
import re
import requests
import subprocess
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

    @allure.severity('critical')
    @allure.story('applcm-user-cases')
    def test0000_init_data_for_applcm_apis(self):
        """
        user scenario 1: create app template, deploy an app based on created app template
        """
        print(TestAppLCM.GKH)
        dicPostTempl = self.getAppTemplConfigForCirros()
        self.__app_onboard_deploy_start_with_template(dicPostTempl)

    @allure.severity('critical')
    @allure.story('applcm-user-cases')
    def test0001_app_onboard_deploy_start_with_templates_metadata_userdata_null(self):
        """
        user scenario 2: create app template, deploy an app based on created app template with metadata/userdata None
        """
        dicPostTempl = self.getAppTemplConfigForCirros()
        dicPostTempl["metadata"] = None
        dicPostTempl["userdata"] = None
        self.__app_onboard_deploy_start_with_template(dicPostTempl)


    @allure.severity('critical')
    @allure.story('applcm-user-cases')
    def test0002_app_onboard_deploy_with_templates_big_image(self):
        """
        user scenario 3: create app template, deploy an app based on created app template with big image file
        """
        dicPostTempl = self.getAppTemplConfigForFepcCpf()
        self.__app_onboard_deploy_with_template(dicPostTempl)


    @allure.story('applcm_template')
    def test10_post_applcm_v1_edgeapps_templates(self):
        """
        # case POST /applcm/v1/edgeapps/templates
        """

        dicPostTempl = self.getAppTemplConfigForCirros()
        image_id = dicPostTempl["images"][0]["image_id"]
        resp0 = requests.get(f'http://{self._hostIP}:9292/image_mgmt/v1/images/{image_id}/refcount')
        print(f"before adding new app template, image {image_id} refcount",resp0.content)
        refcount0 = resp0.json()["refcount"]

        resp = requests.post(f'{self.test_api_prefix}/edgeapps/templates',    \
                data=json.dumps(dicPostTempl),   \
                headers=self.GKH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        dicRespBody = dicRet["data"]
        self.assertNotEqual(dicRespBody["template_id"],0)

        resp1 = requests.get(f'http://{self._hostIP}:9292/image_mgmt/v1/images/{image_id}/refcount')
        print(f"after adding new app template, image {image_id} refcount",resp1.content)
        refcount1 = resp1.json()["refcount"]
        self.assertEqual(refcount0+1, refcount1)

    @allure.story('applcm_template')
    def test10_post_applcm_v1_edgeapps_templates_fail1(self):
        """
        # negative case POST /applcm/v1/edgeapps/templates with duplicated template_name
        """

        dicPostTempl = self.getAppTemplConfigForCirros()
        resp = requests.post(f'{self.test_api_prefix}/edgeapps/templates',    \
                data=json.dumps(dicPostTempl),   \
                headers=self.GKH)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()

        if dicRet["err_code"] == 2109:
            pass
        elif dicRet["err_code"] == 0:
            # create same template again
            resp = requests.post(f'{self.test_api_prefix}/edgeapps/templates',    \
                    data=json.dumps(dicPostTempl),   \
                    headers=self.GKH)
            print(resp.content)
            self.assertEqual(resp.status_code, 200)
            dicRet = resp.json()
            self.assertEqual(dicRet["err_code"],2109)
            print(dicRet["message"])


    @allure.story('applcm_template')
    def test11_get_applcm_v1_edgeapps_templates(self):
        """
        # case GET /applcm/v1/edgeapps/templates for retrieving all app templates
        """    
        targetUri = f'{self.test_api_prefix}/edgeapps/templates'
        resp = requests.get(targetUri, headers=self.GKH)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        print("GET "+targetUri + " Resp:%d templates"%len(dicRet["data"]))
        self.assertEqual(dicRet["err_code"],0)
        for t in dicRet["data"]:
            self.assertNotEqual(t["template_id"],"")
            self.assertNotEqual(t["template_name"],"")
            self.assertTrue(t["app_type"] in ["vm","container","compose"])
            self.assertNotEqual(t["flavor"],"")
            self.assertGreater(int(t["cores"]),0)
            self.assertGreater(int(t["memory"]),0)
            self.assertGreaterEqual(int(t["disk"]),0)
            self.assertTrue("metadata" in t)
            self.assertTrue("userdata" in t)
            self.assertNotEqual(t["last_modified_isodate"],"")
            self.assertGreater(t["last_modified_timestamp"],0)

    def __get_valid_node_id(self):
        # case GET /health
        resp = requests.get(f'http://{self._hostIP}:10286/health')
        print(resp.content)
        dicRet = resp.json()
        for l in dicRet["message"].split(","):
            print(l)
            if l.startswith("node_id"):
                return l.split("=")[1]

    def __get_valid_template_id(self):
        resp = requests.get(f'{self.test_api_prefix}/edgeapps/templates', headers=self.GKH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        self.assertGreater(len(dicRet["data"]),0)
        for t in dicRet["data"]:
            if t["template_name"].startswith("okdel-"):
                return t["template_id"]
        return dicRet["data"][0]["template_id"]

    def __get_valid_image_id(self):
        resp = requests.get(f'http://{self._hostIP}:9292/image_mgmt/v1/images?type=vm')
        self.assertEqual(resp.status_code, 200)
        lstRet = resp.json()
        self.lstImagesCache = lstRet[:]
        if len(lstRet) > 0:
            return lstRet[0]["id"]
        return "ci-cirros"


    def __get_running_app_id(self,node_id):
        targeturi = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps'
        resp = requests.get(targeturi, headers=self.GKH)
        self.assertEqual(resp.status_code, 200)
        dicret = resp.json()
        self.assertEqual(dicret["err_code"],0)
        self.assertGreater(len(dicret["data"]),0)
        for inst in dicret["data"]:
            if inst["state"] == "running":
                return inst["app_id"]

    @allure.story('applcm_instance')
    def test200_get_applcm_v1_edgeapps_nodes(self):
        # case GET /applcm/v1/edgeapps/nodes
        resp = requests.get(f'{self.test_api_prefix}/edgeapps/nodes',headers=self.GKH)
        # resp = requests.get(self.api_prefix + '/edgeapps/nodes')
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        for inst in dicRet["data"]:
            print(inst)
            self.assertNotEqual(inst["node_id"],"")
            self.assertNotEqual(inst["hostname"],"")
            self.assertNotEqual(inst["app_id"],"")
            self.assertNotEqual(inst["app_name"],"")
            self.assertNotEqual(inst["flavor"],"")
            self.assertTrue(inst["app_type"] in ["vm","container"])
            self.assertTrue(inst["state"] in ["unknown", "deploying", "ready", "starting", "running", "stopping", "stopped", "error"])

    @allure.story('applcm_instance')
    def test201_post_applcm_v1_edgeapps_nodes__node_id__apps(self):
        # case POST /applcm/v1/edgeapps/nodes/{node_id}/apps

        nid = self.__get_valid_node_id()
        tid = self.__get_valid_template_id()
        node_id = nid
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps'
        resp = requests.post(targetUri, \
                data=json.dumps({"template_id": tid}),   \
                headers=self.GKH)
        print(targetUri)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

    @allure.story('applcm_instance')
    def test202_post_applcm_v1_edgeapps_nodes__node_id__apps_fail_1(self):
        # case POST /applcm/v1/edgeapps/nodes/{node_id}/apps with invalid node_id

        dicPostNodeApp = {"template_id":"temp0001" }
        node_id = 'v0'
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps'
        print(targetUri)
        resp = requests.post(targetUri, \
                data=json.dumps(dicPostNodeApp),   \
                headers=self.GKH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["err_code"], 2102)

    @allure.story('applcm_instance')
    def test203_post_applcm_v1_edgeapps_nodes__node_id__apps_fail_2(self):
        """
        # case POST /applcm/v1/edgeapps/nodes/{node_id}/apps with invalid template_id
        """
        dicPostNodeApp = {"template_id":"temp0001-wxyz-invalid" }
        node_id = self.__get_valid_node_id()
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps'
        resp = requests.post(targetUri, \
                data=json.dumps(dicPostNodeApp),   \
                headers=self.GKH)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        print(dicRet)
        self.assertEqual(dicRet["err_code"],2101)

    @allure.story('applcm_instance')
    def test21_get_applcm_v1_edgeapps_nodes__node_id__apps(self):
        # case GET /applcm/v1/edgeapps/nodes/{node_id}/apps

        node_id = self.__get_valid_node_id()
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps'
        print("GET "+targetUri)
        resp = requests.get(targetUri,headers=self.GKH)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        for inst in dicRet["data"]:
            self.assertNotEqual(inst["node_id"],"")
            self.assertNotEqual(inst["hostname"],"")
            self.assertNotEqual(inst["app_id"],"")
            self.assertNotEqual(inst["app_name"],"")

    @allure.story('applcm_instance')
    def test22_get_applcm_v1_edgeapps_nodes__node_id__apps_brief_summary(self):
        # case GET /applcm/v1/edgeapps/nodes/{node_id}/apps

        node_id = self.__get_valid_node_id()
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps?briefSummary=true'
        print(targetUri)
        resp = requests.get(targetUri,headers=self.GKH)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        print(dicRet)
        self.assertEqual(dicRet["err_code"],0)
        edgeSummary = dicRet["data"]
        self.assertNotEqual(edgeSummary["node_id"],"")
        self.assertNotEqual(edgeSummary["hostname"],"")
        self.assertGreaterEqual (int(edgeSummary["num_deployed_apps"]),0)
        self.assertGreaterEqual (int(edgeSummary["num_running_apps"]),0)
        self.assertGreaterEqual (int(edgeSummary["usable_vcpu_cores"]),0)
        self.assertGreaterEqual (int(edgeSummary["usable_memory_gb"]),0)
        self.assertGreaterEqual (int(edgeSummary["usable_disk_gb"]),0)
        if int(edgeSummary["num_running_apps"]) > 0:
            self.assertGreater(int(edgeSummary["occupied_vcpu_cores"]),0)
            self.assertGreater(int(edgeSummary["occupied_memory_gb"]),0)
            #self.assertGreater(int(edgeSummary["occupied_disk_gb"]),0)

    @allure.story('applcm_template')
    def test30_put_applcm_v1_edgeapps_templates__template_id_(self):
        """
        # case PUT /applcm/v1/edgeapps/templates/{template_id} to modify an existing app template
        """
        resp = requests.get(f'{self.test_api_prefix}/edgeapps/templates',headers=self.GKH)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        self.assertGreater(len(dicRet["data"]),0)

        for t0 in dicRet["data"]:
            print(t0)
            if t0["images"][0]["image_name"].startswith("cirros"):
                template_id = t0["template_id"]
                break

        dicPutTempl= {
          "template_name": t0["template_name"][:12] + "-modified",
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

        targetUri = f'{self.test_api_prefix}/edgeapps/templates/{template_id}'
        
        print("PUT " +targetUri + f" /w {dicPutTempl}") 
        resp = requests.put(targetUri,headers=self.GKH,data=json.dumps(dicPutTempl))
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)


    @allure.story('applcm_template')
    def test31_delete_applcm_v1_edgeapps_templates__template_id_(self):
        # case DELETE /applcm/v1/edgeapps/templates/{template_id}

        resp = requests.get(f'{self.test_api_prefix}/edgeapps/templates',headers=self.GKH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

        template_id = None
        for t0 in dicRet["data"]:
            if t0["template_name"].startswith("okdel-"):
                template_id = t0["template_id"]
                image_id = t0["images"][0]["image_id"]
                resp0 = requests.get(f'http://{self._hostIP}:9292/image_mgmt/v1/images/{image_id}/refcount')
                print(f"before deleting app template, image {image_id} refcount",resp0.content)
                targetUri = f'{self.test_api_prefix}/edgeapps/templates/{template_id}'
                resp = requests.delete(targetUri,headers=self.GKH)
                print(f"{targetUri},{resp.status_code}")
                self.assertEqual(resp.status_code, 200)
                dicRet = resp.json()
                self.assertEqual(dicRet["err_code"],0)

                resp1 = requests.get(f'http://{self._hostIP}:9292/image_mgmt/v1/images/{image_id}/refcount')
                print(f"after deleting app template, image {image_id} refcount",resp1.content)

    @allure.story('applcm_template')
    def test32_get_applcm_v1_edgeapps_templates__template_id_(self):
        # case GET /applcm/v1/edgeapps/templates/{template_id}

        resp = requests.get(f'{self.test_api_prefix}/edgeapps/templates',headers=self.GKH)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

        for t0 in dicRet["data"]:
            template_id = t0["template_id"]
            targetUri = f'{self.test_api_prefix}/edgeapps/templates/{template_id}'
            resp = requests.get(targetUri, headers=self.GKH)
            print(resp.content)
            self.assertEqual(resp.status_code, 200)
            dicRet = resp.json()
            self.assertEqual(dicRet["err_code"],0)
            t = dicRet["data"]
            self.assertNotEqual(t["template_id"],"")
            self.assertNotEqual(t["template_name"],"")
            self.assertTrue(t["app_type"] in ["vm","container","compose"])
            self.assertNotEqual(t["flavor"],"")
            self.assertGreater(int(t["cores"]),0)
            self.assertGreater(int(t["memory"]),0)
            self.assertGreaterEqual(int(t["disk"]),0)
            self.assertTrue("metadata" in t)
            self.assertTrue("userdata" in t)
            self.assertNotEqual(t["last_modified_isodate"],"")
            self.assertGreater(t["last_modified_timestamp"],0)

    @allure.story('applcm_template')
    def test32_get_applcm_v1_edgeapps_templates__template_id_fail1(self):
        """
        # case GET /applcm/v1/edgeapps/templates/{template_id} with invlid temlate_id
        """
        tid = "{}".format(random.random())
        resp = requests.get(f'{self.test_api_prefix}/edgeapps/templates/{tid}',headers=self.GKH)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],2101)
        print(dicRet)


    @allure.story('applcm_instance')
    def test9999_delete_applcm_v1_edgeapps_nodes__node_id__apps__app_id_(self):
        """
        # case DELETE /applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id} to undeploy app instance one-by-one
        """
        node_id = self.__get_valid_node_id()
        targeturi = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps'
        resp = requests.get(targeturi, headers=self.GKH)
        self.assertEqual(resp.status_code, 200)
        dicret = resp.json()
        self.assertEqual(dicret["err_code"],0)
        self.assertGreater(len(dicret["data"]),0)
        for inst in dicret["data"]:
            if inst["app_name"].startswith("okdel-") and inst["state"] not in ["deploying","starting","stopping"]:
                app_id = inst["app_id"]
                targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
                print("DELETE "+targetUri)
                resp = requests.delete(targetUri,headers=self.GKH)
                print(resp.content)
                self.assertEqual(resp.status_code, 200)
                dicRet = resp.json()
                self.assertEqual(dicRet["err_code"],0)

    @allure.story('applcm_instance')
    def test41_delete_applcm_v1_edgeapps_nodes__node_id__apps__app_id_fail_1(self):
        """
        # neg case DELETE /applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id} invalid node_id
        """
        node_id = 'v0'
        app_id = 'v1'
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
        print(targetUri)
        resp = requests.delete(targetUri,headers=self.GKH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],2102)

    @allure.story('applcm_instance')
    def test41_delete_applcm_v1_edgeapps_nodes__node_id__apps__app_id_fail_2(self):
        """
        # neg case DELETE /applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id} valid node_id but invlid app_id
        """
        node_id = self.__get_valid_node_id()
        app_id = 'v1'
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
        print(targetUri)
        resp = requests.delete(targetUri,headers=self.GKH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],2103)

    @allure.story('applcm_instance')
    def test42_patch_applcm_v1_edgeapps_nodes__node_id__apps__app_id_1_restart(self):
        """
        # case PATCH /applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id} do RESTART action 
        """
        node_id = self.__get_valid_node_id()
        app_id = self.__get_running_app_id(node_id)
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
        print(targetUri)
        resp = requests.patch(targetUri,    \
                data=json.dumps({"action":"restart"}),   \
                headers=self.GKH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

    @allure.story('applcm_instance')
    def test42_patch_applcm_v1_edgeapps_nodes__node_id__apps__app_id_fail_1(self):
        """
        # case PATCH /applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id} invalid node_id
        """
        node_id = 'v0'
        app_id = 'v1'
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
        print(targetUri)
        resp = requests.patch(targetUri,headers=self.GKH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],2102)

    @allure.story('applcm_instance')
    def test42_patch_applcm_v1_edgeapps_nodes__node_id__apps__app_id_fail_2(self):
        """
        case PATCH /applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id} valid node_id but invlid app_id
        """
        node_id = self.__get_valid_node_id()
        app_id = 'v1'
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
        print(targetUri)
        resp = requests.patch(targetUri,headers=self.GKH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],2103)

    @allure.story('applcm_instance')
    def test43_get_applcm_v1_edgeapps_nodes__node_id__apps__app_id_(self):
        # case GET /applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id}

        resp = requests.get(f'{self.test_api_prefix}/edgeapps/nodes',headers=self.GKH)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

        for inst in dicRet["data"]:
            v0 = inst["node_id"]
            v1 = inst["app_id"]
            node_id=v0
            app_id=v1
            targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
            resp = requests.get(targetUri,headers=self.GKH)
            self.assertEqual(resp.status_code, 200)
            dicRet = resp.json()
            self.assertEqual(dicRet["err_code"],0)
            inst2 = dicRet["data"]
            self.assertNotEqual(inst2["node_id"],"")
            self.assertNotEqual(inst2["hostname"],"")
            self.assertNotEqual(inst2["app_id"],"")
            self.assertNotEqual(inst2["app_name"],"")

    @allure.story('applcm_instance')
    def test43_get_applcm_v1_edgeapps_nodes__node_id__apps__app_id_fail_1(self):
        """
        # neg case GET /applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id} with invalid node_id value
        """
        node_id="v0"
        app_id="v1"
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
        print(targetUri)
        resp = requests.get(targetUri,headers=self.GKH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],2102)

    @allure.story('applcm_instance')
    def test43_get_applcm_v1_edgeapps_nodes__node_id__apps__app_id_fail_2(self):
        """
        # neg case GET /applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id} with valid node_id but invalid app_id value
        """
        node_id = self.__get_valid_node_id()
        app_id="v1"
        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
        print(targetUri)
        resp = requests.get(targetUri,headers=self.GKH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],2103)

    @allure.story('applcm_instance')
    def test50_get_health(self):
        # case GET /health
        resp = requests.get(f'http://{self._hostIP}:10286/health')
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        self.assertNotEqual(re.search("applcmctrl",dicRet["message"]),None)

    def getAppTemplConfigForCirros(self):

        self.__get_valid_image_id()
        image_id = "gi-cirros"
        for ii in self.lstImagesCache:
            if ii["file"].find("cirros") >= 0:
                image_id = ii["id"]
                print("GOT!!!!!!!!"+image_id)
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

    def getAppTemplConfigForFepcCpf(self):

        self.__get_valid_image_id()
        image_id = "gi-cirros"
        for ii in self.lstImagesCache:
            if ii["file"].find("cpf") >= 0:
                image_id = ii["id"]
                print("GOT FEPC CPF image!!!!!!!!"+image_id)
                break

        udata = r"""
write_files:
  xxx: 1234
"""
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
            "vcpu_cores": 4,
            "memory": 4,
            "disk": 80
          },
          "metadata": "ovs_network: \n  - int\n  - xhaul\n  - oam\n",
          #"userdata": "write_file:\n  xyz: %s\n"%(rnd_appName),
          "userdata": udata,
          "version": "1.0",
          "vendor": "faca",
          "description": "cpf-vm"
        }
        return dicPostTempl

    def __app_onboard_deploy_with_template(self, dicPostTempl):


        targetUri=f'{self.test_api_prefix}/edgeapps/templates'
        print("POST "+targetUri + f" /w\n{dicPostTempl}")
        resp = requests.post(targetUri, \
                data=json.dumps(dicPostTempl),   \
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

    def __app_onboard_deploy_start_with_template(self, dicPostTempl):

        self.__app_onboard_deploy_with_template(dicPostTempl)

        node_id = self.__get_valid_node_id()
        app_id = dicPostTempl["template_id"]

        targetUri = f'{self.test_api_prefix}/edgeapps/nodes/{node_id}/apps/{app_id}'
        dicPatchNodeApps = {"action":"start"}
        print('PATCH '+targetUri + f' /w\n{dicPatchNodeApps}')
        resp = requests.patch(targetUri,    \
                data=json.dumps(dicPatchNodeApps),  \
                headers=self.GKH)
        print(resp.content)
        print("="*32)
