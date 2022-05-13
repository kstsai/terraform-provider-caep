# Prerequisite

* Python3.6

* pytest

* requests

# Guideline

* Use virtualenv for your development

```
   python3.6 -m virtualenv venv --no-site-packages
   source venv/bin/activate
   pip install -r requirements.txt
```


# Options

* ip_address: string, the target test server

* protocol: string, http/https

* root_ca_path: string, logserver ssl certificate path

* edge_name: string, edge node name

* deploy_vm_name: string, vm name for testing edgedeployer deploy api
 
* deploy_vm_ip: string, vm ip address for testing edgedeployer deploy api

* ecs_version: string, ecs release version 

* operator_ws: string, the workspace folder path for operator

* client: for iperf

* server: for iperf

* client_userpwd: for iperf

* server_userpwd: for iperf

* extra_parameter: for iperf

* iperf_protocol: for iperf