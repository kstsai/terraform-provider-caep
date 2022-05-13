
import json
import re
import requests
import unittest
class TestFoo(unittest.TestCase):
    def setUp(self):
        self.PH={"content-type":"application/json"}

    def tearDown(self):
        pass

    def test00_get_applcm_v1_edgeapps_nodes(self):
        # case GET /applcm/v1/edgeapps/nodes
        resp = requests.get('http://applcmctrl:10286/applcm/v1/edgeapps/nodes')
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        for inst in dicRet["data"]:
            self.assertNotEqual(inst["node_id"],"")
            self.assertNotEqual(inst["hostname"],"")
            self.assertNotEqual(inst["app_id"],"")
            self.assertNotEqual(inst["app_name"],"")
            self.assertNotEqual(inst["flavor"],"")
            self.assertTrue(inst["app_type"] in ["vm","container"])
            self.assertTrue(inst["state"] in ["unknown", "deploying", "ready", "starting", "running", "stopping", "stopped", "error"])

    def test10_post_applcm_v1_edgeapps_templates(self):
        # case POST /applcm/v1/edgeapps/templates
        dicPostTempl= {
          "template_name": "template_for_creating_app_instance",
          "app_type": "vm",
          "images": [
            {
              "image_id": "img-123456-abcdxzy"
            }
          ],
          "flavor_setting": {
            "vcpu_cores": 4,
            "memory": 8,
            "disk": 80
          },
          "metadata": "expect yaml format!!! bala bala... foobarbar... multiple lines allowed",
          "userdata": "bala bala...\nfoobarbar...\nmultiple lines allowed",
          "version": "1.0",
          "vendor": "faca",
          "description": "bala bala...\nfoobarbar...\nmultiple lines allowed"
        }
        resp = requests.post('http://applcmctrl:10286/applcm/v1/edgeapps/templates',    \
                data=json.dumps(dicPostTempl),   \
                headers=self.PH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        dicRespBody = dicRet["data"]
        self.assertNotEqual(dicRespBody["template_id"],0)

    def test11_get_applcm_v1_edgeapps_templates(self):
        # case GET /applcm/v1/edgeapps/templates
        resp = requests.get('http://applcmctrl:10286/applcm/v1/edgeapps/templates')
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
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

    def __get_valid_node_id(self):

        # TODO: not work if NO node app at any nodes
        resp = requests.get('http://applcmctrl:10286/applcm/v1/edgeapps/nodes')
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        self.assertGreater(len(dicRet["data"]),0)
        nodeIds = { inst["node_id"]:1 for inst in dicRet["data"] }
        return list(nodeIds.keys())[0]

    def __get_valid_template_id(self):
        resp = requests.get('http://applcmctrl:10286/applcm/v1/edgeapps/templates')
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        self.assertGreater(len(dicRet["data"]),0)
        return dicRet["data"][0]["template_id"]

    def test20_post_applcm_v1_edgeapps_nodes__node_id__apps(self):
        # case POST /applcm/v1/edgeapps/nodes/{node_id}/apps

        nid = self.__get_valid_node_id()
        self.test10_post_applcm_v1_edgeapps_templates()
        tid = self.__get_valid_template_id()
        targetUri = 'http://applcmctrl:10286/applcm/v1/edgeapps/nodes/{node_id}/apps'.format(node_id=nid) 
        resp = requests.post(targetUri, \
                data=json.dumps({"template_id": tid}),   \
                headers=self.PH)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

    def test20_post_applcm_v1_edgeapps_nodes__node_id__apps_fail_1(self):
        # case POST /applcm/v1/edgeapps/nodes/{node_id}/apps with invalid node_id

        dicPostNodeApp = {"template_id":"temp0001" }
        targetUri = 'http://applcmctrl:10286/applcm/v1/edgeapps/nodes/{node_id}/apps'.format(node_id='v0') 
        resp = requests.post(targetUri, \
                data=json.dumps(dicPostNodeApp),   \
                headers=self.PH)
        print(resp.content)
        self.assertEqual(resp.status_code, 404)

    def test20_post_applcm_v1_edgeapps_nodes__node_id__apps_fail_2(self):
        # case POST /applcm/v1/edgeapps/nodes/{node_id}/apps with invalid template_id

        resp = requests.get('http://applcmctrl:10286/applcm/v1/edgeapps/nodes')
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        self.assertGreater(len(dicRet["data"]),0)

        nodes = { inst["node_id"]:1 for inst in dicRet["data"] }
        for nid in nodes.keys():
            dicPostNodeApp = {"template_id":"temp0001-wxyz-invalid" }
            targetUri = 'http://applcmctrl:10286/applcm/v1/edgeapps/nodes/{node_id}/apps'.format(node_id=nid) 
            resp = requests.post(targetUri, \
                    data=json.dumps(dicPostNodeApp),   \
                    headers=self.PH)
            print(resp.content)
            self.assertEqual(resp.status_code, 404)
            break

    def test21_get_applcm_v1_edgeapps_nodes__node_id__apps(self):
        # case GET /applcm/v1/edgeapps/nodes/{node_id}/apps

        resp = requests.get('http://applcmctrl:10286/applcm/v1/edgeapps/nodes')
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

        nodes = { inst["node_id"]:1 for inst in dicRet["data"] }
        for nid in nodes.keys():
            targetUri = 'http://applcmctrl:10286/applcm/v1/edgeapps/nodes/{node_id}/apps'.format(node_id=nid) 
            print(targetUri)
            resp = requests.get(targetUri)
            self.assertEqual(resp.status_code, 200)
            dicRet = resp.json()
            self.assertEqual(dicRet["err_code"],0)
            for inst in dicRet["data"]:
                self.assertNotEqual(inst["node_id"],"")
                self.assertNotEqual(inst["hostname"],"")
                self.assertNotEqual(inst["app_id"],"")
                self.assertNotEqual(inst["app_name"],"")

    def test22_get_applcm_v1_edgeapps_nodes__node_id__apps_brief_summary(self):
        # case GET /applcm/v1/edgeapps/nodes/{node_id}/apps
        
        resp = requests.get('http://applcmctrl:10286/applcm/v1/edgeapps/nodes')
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

        nodes = { inst["node_id"]:1 for inst in dicRet["data"] }
        for nid in nodes.keys():
            targetUri = 'http://applcmctrl:10286/applcm/v1/edgeapps/nodes/{node_id}/apps?briefSummary=true'.format(node_id=nid) 
            print(targetUri)
            resp = requests.get(targetUri)
            self.assertEqual(resp.status_code, 200)
            dicRet = resp.json()
            print(dicRet)
            self.assertEqual(dicRet["err_code"],0)
            edgeSummary = dicRet["data"]
            self.assertGreaterEqual (int(edgeSummary["num_deployed_apps"]),0)
            self.assertGreaterEqual (int(edgeSummary["num_running_apps"]),0)
            self.assertGreaterEqual (int(edgeSummary["usable_vcpu_cores"]),0)
            self.assertGreaterEqual (int(edgeSummary["usable_memory_gb"]),0)
            self.assertGreaterEqual (int(edgeSummary["usable_disk_gb"]),0)
            if int(edgeSummary["num_running_apps"]) > 0:
                self.assertGreater(int(edgeSummary["occupied_vcpu_cores"]),0)
                self.assertGreater(int(edgeSummary["occupied_memory_gb"]),0)
                #self.assertGreater(int(edgeSummary["occupied_disk_gb"]),0)

    def test30_put_applcm_v1_edgeapps_templates__template_id_(self):
        # case PUT /applcm/v1/edgeapps/templates/{template_id}
        targetUri = 'http://applcmctrl:10286/applcm/v1/edgeapps/templates/{template_id}'.format(template_id='v0') 
        resp = requests.put(targetUri)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

    def test31_delete_applcm_v1_edgeapps_templates__template_id_(self):
        # case DELETE /applcm/v1/edgeapps/templates/{template_id}

        resp = requests.get('http://applcmctrl:10286/applcm/v1/edgeapps/templates')
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        
        template_id = None 
        for t0 in dicRet["data"]:
            if t0["template_name"] == "template_for_creating_app_instance":
                template_id = t0["template_id"]
                break
        if template_id is not None:
            targetUri = 'http://applcmctrl:10286/applcm/v1/edgeapps/templates/{template_id}'.format(template_id=template_id) 
            resp = requests.delete(targetUri)
            print(resp.content)
            self.assertEqual(resp.status_code, 200)
            dicRet = resp.json()
            self.assertEqual(dicRet["err_code"],0)

    def test32_get_applcm_v1_edgeapps_templates__template_id_(self):
        # case GET /applcm/v1/edgeapps/templates/{template_id}

        resp = requests.get('http://applcmctrl:10286/applcm/v1/edgeapps/templates')
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        
        for t0 in dicRet["data"]:
            template_id = t0["template_id"]

            targetUri = 'http://applcmctrl:10286/applcm/v1/edgeapps/templates/{template_id}'.format(template_id=template_id) 
            resp = requests.get(targetUri)
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

    def test41_delete_applcm_v1_edgeapps_nodes__node_id__apps__app_id_(self):
        # case DELETE /applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id}
        targetUri = 'http://applcmctrl:10286/applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id}'.format(node_id='v0',app_id='v1') 
        resp = requests.delete(targetUri)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

    def test42_patch_applcm_v1_edgeapps_nodes__node_id__apps__app_id_(self):
        # case PATCH /applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id}
        targetUri = 'http://applcmctrl:10286/applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id}'.format(node_id='v0',app_id='v1') 
        resp = requests.patch(targetUri)
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

    def test43_get_applcm_v1_edgeapps_nodes__node_id__apps__app_id_(self):
        # case GET /applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id}

        resp = requests.get('http://applcmctrl:10286/applcm/v1/edgeapps/nodes')
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)

        for inst in dicRet["data"]:
            v0 = inst["node_id"]
            v1 = inst["app_id"]

            targetUri = 'http://applcmctrl:10286/applcm/v1/edgeapps/nodes/{node_id}/apps/{app_id}'.format(node_id=v0,app_id=v1)
            resp = requests.get(targetUri)
            self.assertEqual(resp.status_code, 200)
            dicRet = resp.json()
            self.assertEqual(dicRet["err_code"],0)
            inst = dicRet["data"]
            self.assertNotEqual(inst["node_id"],"")
            self.assertNotEqual(inst["hostname"],"")
            self.assertNotEqual(inst["app_id"],"")
            self.assertNotEqual(inst["app_name"],"")

    def test50_get_health(self):
        # case GET /health
        resp = requests.get('http://applcmctrl:10286/health')
        print(resp.content)
        self.assertEqual(resp.status_code, 200)
        dicRet = resp.json()
        self.assertEqual(dicRet["err_code"],0)
        self.assertNotEqual(re.search("applcmctrl",dicRet["message"]),None)
