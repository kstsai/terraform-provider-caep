# !/usr/bin/env python
# -*-coding: utf-8 -*-

from .dev.constants import *
from .fixtures.sftp import *
from .fixtures.ssh import *
from .fixtures.openness import *
import urllib3


def pytest_addoption(parser):
    parser.addoption(f"--{CONST_IP_ADDRESS}", action="store", dest=CONST_IP_ADDRESS, type="string", default="localhost")
    parser.addoption(f"--{CONST_CONTROL_NAME}", action="store", dest=CONST_CONTROL_NAME, type="string", default="opennessCI")
    parser.addoption(f"--{CONST_PROTOCOL}", action="store", dest=CONST_PROTOCOL, type="string", default="http")
    parser.addoption(f"--{CONST_ROOT_CA_PATH}", action="store", dest=CONST_ROOT_CA_PATH, type="string", default="./tests/certs/ca.crt")
    parser.addoption(f"--{CONST_EDGE_NAME}", action="store", dest=CONST_EDGE_NAME, type="string", default="ciedgenode01")

    # operator
    parser.addoption(f"--{CONST_OPERATOR_WS}", action="store", dest=CONST_OPERATOR_WS, type="string", default="")
    
    parser.addoption(f"--{CONST_EDGE_IP}", action="store", dest=CONST_EDGE_IP, type="string", default="")
    parser.addoption(f"--{CONST_ECS_VERSION}", action="store", dest=CONST_ECS_VERSION, type="string", default="latest")
    parser.addoption(f"--{CONST_DEPLOY_VM_NAME}", action="store", dest=CONST_DEPLOY_VM_NAME, type="string", default="ecsdev")
    parser.addoption(f"--{CONST_DEPLOY_VM_IP}", action="store", dest=CONST_DEPLOY_VM_IP, type="string", default="10.60.6.180")
    parser.addoption(f"--{CONST_GATEKEEPER_DEFAULT_USER}", action="store", dest=CONST_GATEKEEPER_DEFAULT_USER, type="string", default="user")
    parser.addoption(f"--{CONST_GATEKEEPER_DEFAULT_PWD}", action="store", dest=CONST_GATEKEEPER_DEFAULT_PWD, type="string", default="123456")

def pytest_generate_tests(metafunc):
    ip_address = metafunc.config.getoption(CONST_IP_ADDRESS, default='localhost')
    protocol = metafunc.config.getoption(CONST_PROTOCOL, default="http")
    root_ca_path = metafunc.config.getoption(CONST_ROOT_CA_PATH, default="")
    edge_name = metafunc.config.getoption(CONST_EDGE_NAME, default='ciedgenode01')
    operator_ws = metafunc.config.getoption(CONST_OPERATOR_WS, default="")
    edge_ip = metafunc.config.getoption(CONST_EDGE_IP, default="")
    control_name = metafunc.config.getoption(CONST_CONTROL_NAME, default="opennessCI")    
    ecs_version = metafunc.config.getoption(CONST_ECS_VERSION, default="latest")    
    deploy_vm_name = metafunc.config.getoption(CONST_DEPLOY_VM_NAME, default="ecsdev")
    deploy_vm_ip = metafunc.config.getoption(CONST_DEPLOY_VM_IP, default="10.60.6.180") 
    gatekeeper_default_user = metafunc.config.getoption(CONST_GATEKEEPER_DEFAULT_USER, default="user")
    gatekeeper_default_pwd = metafunc.config.getoption(CONST_GATEKEEPER_DEFAULT_PWD, default="123456") 
       
    if CONST_IP_ADDRESS in metafunc.fixturenames:
        metafunc.parametrize(CONST_IP_ADDRESS, [ip_address])
    if CONST_PROTOCOL in metafunc.fixturenames:
        metafunc.parametrize(CONST_PROTOCOL, [protocol])
    if CONST_ROOT_CA_PATH in metafunc.fixturenames:
        metafunc.parametrize(CONST_ROOT_CA_PATH, [root_ca_path])
    if CONST_EDGE_NAME in metafunc.fixturenames:
        metafunc.parametrize(CONST_EDGE_NAME, [edge_name])
    if CONST_OPERATOR_WS in metafunc.fixturenames:
        metafunc.parametrize(CONST_OPERATOR_WS, [operator_ws])
    if CONST_EDGE_IP in metafunc.fixturenames:
        metafunc.parametrize(CONST_EDGE_IP, [edge_ip])        
    if CONST_CONTROL_NAME in metafunc.fixturenames:
        metafunc.parametrize(CONST_CONTROL_NAME, [control_name])     
    if CONST_ECS_VERSION in metafunc.fixturenames:
        metafunc.parametrize(CONST_ECS_VERSION, [ecs_version])
    if CONST_DEPLOY_VM_NAME in metafunc.fixturenames:
        metafunc.parametrize(CONST_DEPLOY_VM_NAME, [deploy_vm_name])   
    if CONST_DEPLOY_VM_IP in metafunc.fixturenames:
        metafunc.parametrize(CONST_DEPLOY_VM_IP, [deploy_vm_ip])
    if CONST_GATEKEEPER_DEFAULT_USER in metafunc.fixturenames:
        metafunc.parametrize(CONST_GATEKEEPER_DEFAULT_USER, [gatekeeper_default_user])
    if CONST_GATEKEEPER_DEFAULT_PWD in metafunc.fixturenames:
        metafunc.parametrize(CONST_GATEKEEPER_DEFAULT_PWD, [gatekeeper_default_pwd])


@pytest.fixture(autouse=True)
def copy_certificate_from_controller(copy_cert):
    urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
    assert copy_cert
