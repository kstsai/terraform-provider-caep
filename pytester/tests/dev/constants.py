# !/usr/bin/env python
# -*-coding: utf-8 -*-


CONST_EDGE_IP = "edge_ip"
CONST_IP_ADDRESS = "ip_address"
CONST_PROTOCOL = "protocol"
CONST_ROOT_CA_PATH = "root_ca_path"
CONST_EDGE_NAME = "edge_name"
CONST_CONTROL_NAME = "control_name"
CONST_ECS_VERSION = "ecs_version"
CONST_DEPLOY_VM_NAME = "deploy_vm_name"
CONST_DEPLOY_VM_IP = "deploy_vm_ip"

# GATEKEEPER
CONST_GATEKEEPER_DEFAULT_USER = "gatekeeper_default_user"
CONST_GATEKEEPER_DEFAULT_PWD = "gatekeeper_default_pwd"

CONST_VCPU_URL = "vcpu_url"
CONST_USB_URL = "usb_url"
CONST_ACCELERATOR_URL = "accelerator_url"
CONST_NIC_URL = "nic_url"
CONST_APP_NAME = "app_name"
CONST_OPERATOR_WS = "operator_ws"

# iperf
CONST_CLIENT = "client"
CONST_SERVER = "server"
CONST_CLIENT_USERPWD = "client_userpwd"
CONST_SERVER_USERPWD = "server_userpwd"
CONST_EXTRA_PARA = "extra_parameter"
CONST_IPERF_PROTOCOL = "iperf_protocol"


CONST_METADATA_URL = "metadata_url"

class PrtColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# api Lifecycle
class apiStatus:
    DEPLOYING  = "deploying"
    DEPLOYED   = "ready"
    STARTING   = "starting"
    RUN        = "running"
    STOPPING   = "stopping"
    STOP       = "stopped"
    ERROR      = "error"
    SNAPSHOT   = "snapshot"


class TemplateKey:
    ID   = 'template_id'
    NAME = 'template_name'
    TYPE = 'app_type'
    IMG  = 'images'
    VERSION  = 'version'
    VENDOR   = 'vendor'
    DESCRIBE = 'description'
    FLAVOR = 'flavor'
    CORE = 'cores'
    MEM  = 'memory'
    DISK = 'disk'
    MODIFYDATE = 'last_modified_isodate'
    MODIFYTIME = 'last_modified_timestamp'
    METADATA = 'metadata'
    USERDATA = 'userdata'

class NodeKey:
    NAME = 'hostname'
    ID   = 'node_id'
    IP   = 'mgmt_ip'
    MAC  = 'mgmt_MAC'
    STATE    = 'node_state'
    HARDWARE = 'capability' # containing cpu, memory, pci_info etc

class NodeHardwareKey: # from 'capability' in class NodeKey
    CPU  = 'cpu'
    CUPMODEL = 'cpu_model'
    MEMORY   = 'memory'
    PCI  = 'pci_info'

class NodeAppKey:
    ID   = 'app_id'
    NAME = 'app_name'
    TYPE = 'app_type'
    STATE  = 'state'
    FLAVOR = 'flavor'
    HOSTNAME = 'hostname'
    NETWORK  = 'networks'
    HOSTID   = 'node_id'
    METADATA = 'metadata'


