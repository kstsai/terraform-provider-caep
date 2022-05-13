# !/usr/bin/env python
# -*-coding: utf-8 -*-
# ================================================
# Features: comprehensive app lifecycle fixtures =
# Author: Jian Han Wu                            =
# ================================================

import pytest
import json
import time
import ipaddress
import glob
import sys

from .http import *
from .images import *
from .gatekeeper import *
from .api_parser import api_parser
from .comprehensive_feature_check import *
from ..dev.constants import apiStatus, TemplateKey, NodeKey, NodeHardwareKey, NodeAppKey, PrtColors

# ====================
# =    FUNCTIONS     =
# ====================
def animate(wait_dialogue="loading", times=10):
    count = 0
    if times < 10:
        times = 10
    while count <= times:
        count += 1
        sys.stdout.write(f"\r{wait_dialogue} |")
        time.sleep(0.1)
        sys.stdout.write(f"\r{wait_dialogue} /")
        time.sleep(0.1)
        sys.stdout.write(f"\r{wait_dialogue} -")
        time.sleep(0.1)
        sys.stdout.write(f"\r{wait_dialogue} \\")
        time.sleep(0.1)
    sys.stdout.write ("\r")

# =============================================
# = Function: readTemplate                    =
# = Usage: read template info from file       =
# =============================================
@pytest.fixture
def readTemplate():
    def inner(file_name):        
        with open(file_name) as json_file:
            try:
                data = json.load(json_file)
            except FileNotFoundError:
                print("Cannot open file " + file_name + "!!")
                exit()
            except ValueError:
                print("File " + file_name + " is not in JSON format!!")
                exit()
        return data
    yield inner

# ======================
# = PATH FIXTURES      =
# ======================
@pytest.fixture
def appPath(gatekeeper_module):
    def inner(app_id=''):
        return f"{gatekeeper_module}/edgeapps/templates/{app_id}" if app_id else f"{gatekeeper_module}/edgeapps/templates"
    yield inner

@pytest.fixture
def nodePath(gatekeeper_module):
    def inner(node_id=''):
        return f"{gatekeeper_module}/edgenodes/{node_id}" if node_id else f"{gatekeeper_module}/edgenodes"
    yield inner

@pytest.fixture
def nodeAppPath(gatekeeper_module):
    def inner(node_id='', app_id=''):
        if not node_id:
            return f"{gatekeeper_module}/edgeapps/nodes"
        elif not app_id:
            return f"{gatekeeper_module}/edgeapps/nodes/{node_id}/apps"
        else:
            return f"{gatekeeper_module}/edgeapps/nodes/{node_id}/apps/{app_id}"
    yield inner

# app clone status path
@pytest.fixture
def nodeAppCloneStatuPath(gatekeeper_module):
    def inner(node_id='', app_id=''):
        return f"{gatekeeper_module}/edgeapps/nodes/{node_id}/apps/{app_id}/clone"
    yield inner


@pytest.fixture
def imagePath(gatekeeper_module):
    return f"{gatekeeper_module}/images"

# ======================
# = IMG FICTURES       =
# ======================
@pytest.fixture
def getImage(imagePath, api_parser):
    image_arr = []
    images = api_parser(imagePath, 'get', '', 0)['data']
    for img in images:
        image_arr.append({'name': img['name'], 'type': img['type'], 'id': img['id']})
    return image_arr

@pytest.fixture
def getImageID(imagePath, api_parser):
    def inner(image_name, expected_errCode=0):
        images = api_parser(imagePath, 'get', '', expected_errCode)['data']
        image_id = ''
        for image in images:
            if image['name'] != image_name:
                continue
            image_id = image['id']
            break
        if not image_id:
            raise SystemError(f"Image name {image_name} not found!")
        return image_id
    yield inner

# ======================
# = APP FICTURES       =
# ======================
@pytest.fixture
def getTemplate(appPath, api_parser):
    def inner(app_id='', expected_errCode=0):
        result = api_parser(appPath(app_id), 'get', "", expected_errCode)['data']
        return result
    yield inner

@pytest.fixture
def postTemplate(appPath, api_parser, getImageID, readTemplate):
    def inner(file_name, expected_errCode=0, template_name = None):
        body = readTemplate(file_name)
        try:
            print(f"image name:{body['image_name']}")
            image_id = getImageID(body['image_name'])
            body['images'] = [{'image_id': image_id}]
            if template_name is not None:
                body['template_name'] = template_name
            result = api_parser(appPath(""), 'post', body, expected_errCode)['data']
        except Exception as e:
            raise e
        return result[TemplateKey.ID]
    yield inner

@pytest.fixture
def deleteTemplate(appPath, api_parser):
    def inner(app_id, expected_errCode=0):
        if not app_id or not isinstance(app_id, str):
            raise ValueError("Expected template ID <str>!")
        api_parser(appPath(app_id), 'delete', "", expected_errCode)
    yield inner

# ======================
# = EDGENODE FICTURES  =
# ======================
@pytest.fixture
def getNodeById(nodePath, api_parser):
    def inner(node_id="", expected_errCode=0):
        result = api_parser(nodePath(node_id), 'get', "", expected_errCode)['data']
        return result
    yield inner

@pytest.fixture
def getNodeIdByName (nodePath, api_parser):
    def inner (node_name, expected_errCode=0):
        if not node_name or not isinstance(node_name, str):
            raise ValueError ("Expected nodeName <str>!")

        nodes = api_parser(nodePath(""), 'get', '', expected_errCode)['data']
        for node in nodes:
            if node[NodeKey.NAME] != node_name:
                node_id = ''
                continue
            node_id = node[NodeKey.ID]
            break
        
        if not node_id:
            raise SystemError(f"Host name '{node_name}' not found!")
        return node_id
    yield inner

# ======================
# = NODE APP FICTURES  =
# ======================
@pytest.fixture
def getNodeApp(nodeAppPath, api_parser):
    def inner(node_id='', app_id='', expected_errCode=0):
        if not isinstance(node_id, str):
            raise TypeError("Expected node id <str>!")
        elif not isinstance(app_id, str):
            raise TypeError("Expected app id <str>!")
        result = api_parser(nodeAppPath(node_id, app_id), 'get', "", expected_errCode)['data']
        return result
    yield inner

@pytest.fixture
def postNodeApp(nodeAppPath, api_parser):
    def inner(node_id, app_id, expected_errCode=0):
        if not node_id or not isinstance(node_id, str):
            raise ValueError("Expected node id <str>!")
        elif not app_id or not isinstance(app_id, str):
            raise ValueError("Expected app id <str>!")
        api_parser(nodeAppPath(node_id), 'post', {"template_id": app_id}, expected_errCode)
    yield inner

@pytest.fixture
def deleteNodeApp(nodeAppPath, api_parser):
    def inner(node_id, app_id, expected_errCode=0):
        if not node_id or not isinstance(node_id, str):
            raise ValueError("Expected node id <str>!")
        elif not app_id or not isinstance(app_id, str):
            raise ValueError("Expected app id <str>!")
        api_parser(nodeAppPath(node_id, app_id), 'delete', "", expected_errCode)
    yield inner

@pytest.fixture
def patchNodeApp(nodeAppPath, api_parser):
    def inner(node_id, app_id, update_status, expected_errCode=0):
        if not node_id or not isinstance(node_id, str):
            raise ValueError("Expected node id <str>!")
        elif not app_id or not isinstance(app_id, str):
            raise ValueError("Expected app id <str>!")
        result = api_parser(nodeAppPath(node_id, app_id), 'patch', {"action": update_status}, expected_errCode)['data']
        return result
    yield inner


@pytest.fixture
def patchSnapshotNodeApp(nodeAppPath, api_parser):
    def inner(node_id, app_id, update_status, clone_name, expected_errCode=0):
        if not node_id or not isinstance(node_id, str):
            raise ValueError("Expected node id <str>!")
        elif not app_id or not isinstance(app_id, str):
            raise ValueError("Expected app id <str>!")
        result = api_parser(nodeAppPath(node_id, app_id), 'patch', {"action": update_status, "clone_name": clone_name}, expected_errCode)['data']
        return result
    yield inner


# ======================
# = LIFECYCLE PROCESS  =
# ======================
# =============================================
# = Function: app add resorces                =
# = Usage: add resources to instances         =
# =============================================
@pytest.fixture
def app_add_resource(set_global_variable, getTemplate, app_add_vcpu, app_add_usb, app_add_nic, clearApp):
    def inner(node_id, app_id, pin_vcpu=True, attach_usb=True, attach_nic=True):
        set_global_variable('node_id', node_id)
        usb_serial_num = ''
        nic_pci_address = ''
        try:
            app_type = getTemplate(app_id)[TemplateKey.TYPE]
            if pin_vcpu:
                app_add_vcpu(node_id, app_id)
            if attach_usb:
                if app_type.upper() == "CONTAINER":
                    print(f"{PrtColors.WARNING}USB resource management skipped! No support for 'container'...{PrtColors.ENDC}")
                else:
                    usb_serial_num = app_add_usb(node_id, app_id)
            if attach_nic:
                nic_pci_address = app_add_nic(node_id, app_id)
        except Exception as e:
            clearApp(node_id, app_id)
            raise e
        return {'usb_serial': usb_serial_num, 'pci_address': nic_pci_address}
    yield inner

# =============================================
# = Function: app check resorces              =
# = Usage: check resources on instances       =
# =============================================
@pytest.fixture
def app_check_resource(set_global_variable, getTemplate, app_vcpu_check, app_usb_check, app_nic_check, clearApp):
    def inner(node_id, app_id, pin_vcpu=True, attach_usb=True, attach_nic=True):
        set_global_variable('node_id', node_id)
        try:
            app_type = getTemplate(app_id)[TemplateKey.TYPE]
            if pin_vcpu:
                app_vcpu_check(node_id, app_id)
            if attach_usb:
                if app_type.upper() == "CONTAINER":
                    print(f"{PrtColors.WARNING}USB resource management skipped! No support for 'container'...{PrtColors.ENDC}")
                else:
                    app_usb_check(node_id, app_id)
            if attach_nic:
                app_nic_check(node_id, app_id)
        except Exception as e:
            clearApp(node_id, app_id)
            raise e
    yield inner

# =============================================
# = Function: app remove resorces             =
# = Usage: detach resources from instances    =
# =============================================
@pytest.fixture
def app_remove_resource(set_global_variable, getTemplate, app_remove_vcpu, app_remove_usb, app_remove_nic, clearApp):
    def inner(node_id, app_id, hardware_info, pin_vcpu=True, attach_usb=True, attach_nic=True):
        set_global_variable('node_id', node_id)
        try:
            app_type = getTemplate(app_id)[TemplateKey.TYPE]
            if pin_vcpu:
                app_remove_vcpu(node_id, app_id)
            if attach_usb:
                if app_type.upper() == "CONTAINER":
                    print(f"{PrtColors.WARNING}USB resource management skipped! No support for 'container'...{PrtColors.ENDC}")
                else:
                    app_remove_usb(node_id, app_id, hardware_info['usb_serial'])
            if attach_nic:
                app_remove_nic(node_id, app_id, hardware_info['pci_address'])
        except Exception as e:
            clearApp(node_id, app_id)
            raise e
    yield inner

# =============================================
# = Function: clearApp                        =
# = Usage: stop and remove app on edge node   =
# =============================================
@pytest.fixture
def clearApp(getNodeApp, patchNodeApp, deleteNodeApp, getTemplate, deleteTemplate):
    def inner(node_id, app_id):
        if not isinstance(node_id, str):
            raise TypeError("Expected node id <str>!")
        elif not app_id or not isinstance(app_id, str):
            raise ValueError("Expected app id <str>!")

        print(f"Clearing app ({app_id}) ...")
        while node_id:
            try:
                time.sleep(1)
                get_response = getNodeApp(node_id, app_id)
            except Exception as e:
                print(f"Cannot get node app: {e}. Please check the problem on CI.")
                break

            status = get_response[NodeAppKey.STATE]
            if status == apiStatus.DEPLOYING:
                animate("Waiting a deploying process")
                continue
            elif status == apiStatus.STARTING:
                animate("Waiting an activating process")
                continue
            elif status == apiStatus.RUN:
                patchNodeApp(node_id, app_id, "stop")
                continue
            elif status == apiStatus.STOPPING:
                animate("Waiting an stopping process")
                continue
            
            try:
                deleteNodeApp(node_id, app_id)
            except Exception as e:
                raise SystemError(f"Cannot delete node app: {e}. Please check the problem on CI.")
            print(f"{PrtColors.OKGREEN}App ({app_id}) deleted from the edgenode ({node_id})!{PrtColors.ENDC}")
            break
            
        try:
            deleteTemplate(app_id)
            getTemplate(app_id, expected_errCode=2101)
        except Exception as e:
            raise SystemError(f"Cannot delete node app: {e}. Please check the problem on CI.")   
        print(f"{PrtColors.OKGREEN}App ({app_id}) deleted from the app list!{PrtColors.ENDC}")    
    yield inner

# =============================================
# = Function: deployApp                       =
# = Usage: deploy template to the edge node   =
# = Note : resulting status is "deployed" if  =
# =        succeeded                          =
# =============================================
@pytest.fixture
def deployApp(getTemplate, postNodeApp, getNodeApp, clearApp):
    def inner(node_id, app_id):
        # deploy the api to the node
        if not node_id or not isinstance(node_id, str):
            raise ValueError("Expected node id <str>!")
        elif not app_id or not isinstance(app_id, str):
            raise ValueError("Expected app id <str>!")

        try:
            postNodeApp(node_id, app_id)
        except Exception as e:
            clearApp("", app_id)
            raise e

        # wait instance to be deployed
        initial_time = time.time()
        while True:
            animate("deploying")
            try:
                time.sleep(1)
                get_result = getNodeApp(node_id, app_id)
            except Exception as e:
                if time.time() - initial_time > 600: # timeout 10 min
                    clearApp(node_id, app_id)
                    raise SystemError(f"Cannot find app ({app_id}) on the edgenode! Please check the problem on CI.")
                print(f"{PrtColors.WARNING}App not found yet! Time: {time.time() - initial_time}.{PrtColors.ENDC}")
                continue

            status = get_result[NodeAppKey.STATE]
            if status == apiStatus.DEPLOYED:
                break
            elif status != apiStatus.DEPLOYING:
                clearApp(node_id, app_id)
                raise SystemError(f"App deployed failed! Unexpected status ({status})")
        print("Instance deployed!!")
    yield inner

# =============================================
# = Function: activateApp                     =
# = Usage: activate deployed app on the node  =
# = Note : resulting status is "running" if   =
# =        succeeded                          =
# =============================================
@pytest.fixture
def activateApp(getNodeApp, patchNodeApp, clearApp):
    def inner(node_id, app_id):
        # activate instance
        try:
            patch_result = patchNodeApp(node_id, app_id, "start")
        except Exception as e:
            clearApp(node_id, app_id)
            raise e
        
        # wait instance to run
        while True:
            animate("activating")
            try:
                time.sleep(1)
                get_result = getNodeApp(node_id, app_id)
            except Exception as e:
                clearApp(node_id, app_id)
                raise SystemError(f"Cannot get node app: {e}. Please check the problem on CI.")

            status = get_result[NodeAppKey.STATE]
            if status == apiStatus.RUN:
                break
            elif status != apiStatus.STARTING:
                clearApp(node_id, app_id)
                raise SystemError(f"App activated failed! Unexpected status ({status})")
        print("Instance activated!!")
    yield inner

# =============================================
# = Function: stopApp                         =
# = Usage: stop running app on the node       =
# = Note : resulting status is "stopped" if   =
# =        succeeded                          =
# =============================================
@pytest.fixture
def stopApp(getNodeApp, patchNodeApp, clearApp):
    def inner(node_id, app_id):
        # stop the instance
        try:
            patch_result = patchNodeApp(node_id, app_id, "stop")
        except Exception as e:
            clearApp(node_id, app_id)
            raise e

        # wait instance to stop
        while True:
            animate("stopping")
            try:
                time.sleep(1)
                get_result = getNodeApp(node_id, app_id)
            except Exception as e:
                clearApp (node_id, app_id)
                raise SystemError(f"Cannot get node app: {e}. Please check the problem on CI.")
            
            status = get_result[NodeAppKey.STATE]
            if status == apiStatus.STOP:
                break
            elif status != apiStatus.STOPPING:
                clearApp(node_id, app_id)
                raise SystemError(f"App terminated failed! Unexpected status ({status})")
        print("Instance stopped!!")
    yield inner


# =============================================
# = Function: snapshotApp                     =
# = Usage: snapshot stopped app on the node   =
# = Note : resulting status is "stopped" if   =
# =        succeeded                          =
# =============================================
@pytest.fixture
def snapshotApp(getNodeApp, patchSnapshotNodeApp, clearApp):
    def inner(node_id, app_id, clone_name, expected_errCode=0):
        # snapshotApp the instance
        try:
            patch_result = patchSnapshotNodeApp(node_id, app_id, "clone", clone_name, expected_errCode)
            print(f"@@@@@@@@@ snapshotApp patch_result = {patch_result}")
        except Exception as e:
            clearApp(node_id, app_id)
            print(e)
            raise e

        # wait instance snapshot finished
        while True:
            animate("snapshot")
            try:
                get_result = getNodeApp(node_id, app_id)
            except Exception as e:
                clearApp (node_id, app_id)
                raise SystemError(f"Cannot get node app: {e}. Please check the problem on CI.")

            status = get_result[NodeAppKey.STATE]
            if status == apiStatus.STOP or status == apiStatus.RUN :
                break
            elif status != apiStatus.SNAPSHOT:
                clearApp(node_id, app_id)
                raise SystemError(f"App terminated failed! Unexpected status ({status})")
        print("Instance snapshot done!!")
    yield inner


# =============================================
# = Function: stopCloneApp                    =
# = Usage: clone    stopped app on the node   =
# =============================================
@pytest.fixture
def cloneStopApp(getNodeApp, patchSnapshotNodeApp, clearApp):
    def inner(node_id, app_id, clone_name, expected_errCode=0):
        # cloneStopApp the instance
        try:
            patch_result = patchSnapshotNodeApp(node_id, app_id, "clone-stop", clone_name, expected_errCode)
            print(f"@@@@@@@@@ cloneStopApp patch_result = {patch_result}")
        except Exception as e:
            clearApp(node_id, app_id)
            print(e)
            raise e

        # wait instance clone finished
        while True:
            animate("clone")
            try:
                time.sleep(1)
                get_result = getNodeApp(node_id, app_id)
            except Exception as e:
                clearApp (node_id, app_id)
                raise SystemError(f"Cannot get node app: {e}. Please check the problem on CI.")
            
            status = get_result[NodeAppKey.STATE]
            if status == apiStatus.STOP or status == apiStatus.RUN :
                break
            elif status != apiStatus.SNAPSHOT:
                clearApp(node_id, app_id)
                raise SystemError(f"App terminated failed! Unexpected status ({status})")
        print("Instance clone-stop done!!")
    yield inner


# =============================================
# = Function: getAppCloneStatus               =
# = Usage: get app clone progress on the node =
# = Note : resulting progress status info     =
# =                                           =
# =============================================
@pytest.fixture
def getNodeAppCloneStatus(nodeAppCloneStatuPath, api_parser):
    def inner(node_id='', app_id='', expected_errCode=0):
        if not isinstance(node_id, str):
            raise TypeError("Expected node id <str>!")
        elif not isinstance(app_id, str):
            raise TypeError("Expected app id <str>!")
        result = api_parser(nodeAppCloneStatuPath(node_id, app_id), 'get', "", expected_errCode)['data']
        return result
    yield inner

# =============================================
# = Function: getAppCloneStatus               =
# = Usage: get app clone progress on the node =
# = Note : resulting progress status info     =
# =                                           =
# =============================================
@pytest.fixture
def findTemplateByName(getTemplate, readTemplate):
    def inner(template_path='', template_name = None):
        template_id = ''        
        try:
            template = readTemplate(template_path)
            if template_name is not None:
                template['template_name'] = template_name
            get_result = getTemplate('')
            for template_data in  get_result:
                if template['template_name'] == template_data['template_name']:
                    template_id = template_data['template_id']
                    break
        except Exception as e:
            print(e)
        finally:
            return template_id
    yield inner


# ======================
# = COMPREHENSIVES     =
# ======================

# =============================================
# = Function: deployRunApp                    =
# = Usage: Deploy an app to the edge node     =
# = Note : Including onboard,deploy.run       =
# =============================================
@pytest.fixture
def deployRunApp(postTemplate ,getTemplate, update_app_source, deployApp, activateApp, clearApp, findTemplateByName):
    def inner(node_id, app_template, template_name = None):
        if not node_id or not isinstance(node_id, str):
            raise ValueError("Expected node id <str>!")
        elif not app_template or not isinstance(app_template, str):
            raise ValueError("Expected template file name <str>!")

        template_path = f"./tests/comprehensive_cases/templates/{app_template}"

        template_id = findTemplateByName(template_path, template_name)
        if template_id != "":
            clearApp(node_id, template_id)

        try:
            app_id = postTemplate(template_path, template_name = template_name)
        except Exception as e:
            raise SystemError(f"Failed to post template {app_template}! {e}.")
        
        try:
            get_result = getTemplate(app_id)
            print(f"Successfully create an APP! ID: {get_result[TemplateKey.ID]}, name: {get_result[TemplateKey.NAME]}.")
        except Exception as e:
            clearApp("", app_id)
            raise e

        try:
            deployApp(node_id, app_id)
            activateApp(node_id, app_id)
        except Exception as e:
            # already cleared
            raise e
        return app_id
    yield inner

# =============================================
# = Function: removeApp                       =
# = Usage: remove an app from the edge node   =
# = Note : Including stop,remove the app      =
# =============================================
@pytest.fixture
def removeApp(stopApp, clearApp):
    def inner(node_id, app_id):
        if not node_id or not isinstance(node_id, str):
            raise ValueError("Expected node id <str>!")
        elif not app_id or not isinstance(app_id, str):
            raise ValueError("Expected app_id <str>!")
        try:
            stopApp(node_id, app_id)
            clearApp(node_id, app_id)
        except Exception as e:
            raise e 
    yield inner


@pytest.fixture
def run_app_with_del(api_parser, deployRunApp, removeApp):
    created_apps = []

    def _run_app(node_id, tmpl, template_name=None):
        app_id = deployRunApp(node_id, tmpl, template_name=template_name)
        created_apps.append((node_id, app_id))
        return app_id
    yield _run_app

    for node_id, app in created_apps:
        removeApp(node_id, app)
