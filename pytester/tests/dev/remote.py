# !/usr/bin/env python
# -*-coding: utf-8 -*-


import paramiko
from scp import SCPClient


def create_ssh_client(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client


def fetch_remote_folder_with_scp(server, port, user, password, remote_folder, dest):
    client = create_ssh_client(server, port, user, password)
    scp = SCPClient(client.get_transport())
    scp.get(remote_path=remote_folder, local_path=dest, recursive=True)
    client.close()
