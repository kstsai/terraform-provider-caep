# !/usr/bin/env python
# -*-coding: utf-8 -*-

import pytest
import paramiko
import time

cert_copy_flag = False

@pytest.fixture
def ssh_connect():
    host = paramiko.SSHClient()
    host.set_missing_host_key_policy(paramiko.WarningPolicy())
    yield host
    host.close()


@pytest.fixture
def ssh_exec_jumper(ssh_connect):
    # host, username, password given
    def exec_jumper(host, username, password):
        jhost = ssh_connect
        jhost.connect(host, username=username, password=password)
        jtransport = jhost.get_transport()
        return jtransport
    yield exec_jumper


@pytest.fixture
def ssh_access_edge():
    def _exec(edge_ip):
        edge_infos = {}
        edge_infos.update({'host': edge_ip})
        edge_infos.update({'port': 22})
        edge_infos.update({'username': 'user'})
        edge_infos.update({'password': '123456'})
        return edge_infos
    yield _exec


@pytest.fixture
def ssh_access_host(ip_address):
    nev_infos = {}
    nev_infos.update({'host': ip_address})
    nev_infos.update({'port': 22})
    nev_infos.update({'username': 'user'})
    nev_infos.update({'password': '123456'})
    yield nev_infos


@pytest.fixture
def ssh_exec_target(ssh_connect):
    def exec_target(j_channel, t_infos):
        target_host = t_infos.get('host')
        target_username = t_infos.get('username')
        target_password = t_infos.get('password')
        target_cmd = t_infos.get('cmd')
        thost = ssh_connect
        thost.connect(target_host, username=target_username, password=target_password, sock=j_channel)
        stdin, stdout, stderr = thost.exec_command(target_cmd)  # edited#
        res = stdout.read()  # edited#
        print(res)
        return res
    yield exec_target



@pytest.fixture
def ssh_exec_target_root(ssh_connect):
    def exec_target(j_channel, t_infos):
        target_host = t_infos.get('host')
        target_username = t_infos.get('username')
        target_password = t_infos.get('password')
        target_cmd = t_infos.get('cmd')
        thost = ssh_connect
        thost.load_system_host_keys()
        thost.set_missing_host_key_policy(paramiko.WarningPolicy)
        thost.connect(target_host, username=target_username, password=target_password, sock=j_channel)
        stdin, stdout, stderr = thost.exec_command(f'sudo {target_cmd}', get_pty=True)
        stdin.write(f'{target_password}\n')
        stdin.flush()
        output = stdout.read().decode('utf-8').rstrip()
        for out in output.split("\r\n"):
            if out == f"[sudo] password for {target_username}:":
                filter_q = f"[sudo] password for {target_username}:"
                break
            elif out == f"[sudo] password for {target_username}: ":
                filter_q = f"[sudo] password for {target_username}: "
                break
        # print(f'filter: {filter_q}')
        key = output.split("\r\n").index(f"{filter_q}")+1
        return output.split("\r\n")[key:] if output else []  # will return string array
    yield exec_target


@pytest.fixture
def open_channel_from_host_to_target(ssh_access_host, ssh_exec_jumper, ssh_exec_target):
    def _exec(target_infos):
        nev_infos = ssh_access_host
        nev_host = nev_infos.get('host')
        nev_port = nev_infos.get('port')
        nev_username = nev_infos.get('username')
        nev_password = nev_infos.get('password')
        h_transport = ssh_exec_jumper(nev_host, nev_username, nev_password)

        target_host = target_infos.get('host')
        target_port = target_infos.get('port')
        target_addr = (target_host, target_port)  # edited#
        host_addr = (nev_host, nev_port)  # edited#
        h_channel = h_transport.open_channel("direct-tcpip", target_addr, host_addr)
        return ssh_exec_target(h_channel, target_infos)
    yield _exec

@pytest.fixture
def open_channel_from_edge_to_target(ssh_access_edge, ssh_exec_jumper, ssh_exec_target_root):
    def _exec(target_infos, edgeIp, appIp, cmd):
        target_infos['host'] = appIp
        target_infos['cmd'] = cmd
        edge_infos = ssh_access_edge(edgeIp)
        edge_host = edge_infos.get('host')
        edge_port = edge_infos.get('port')
        edge_username = edge_infos.get('username')
        edge_password = edge_infos.get('password')
        h_transport = ssh_exec_jumper(edge_host, edge_username, edge_password)

        target_host = target_infos.get('host')
        target_port = target_infos.get('port')
        target_addr = (target_host, target_port)  # edited#
        edge_addr = (edge_host, edge_port)  # edited#
        h_channel = h_transport.open_channel("direct-tcpip", target_addr, edge_addr)
        return ssh_exec_target_root(h_channel, target_infos)
    yield _exec

@pytest.fixture
def execute_cmd_through_ssh():
    def execute(host, port, username, password, cmd):
        client = paramiko.SSHClient()
        try:
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy)
            client.connect(host, port=port, username=username, password=password)
            stdin, stdout, stderr = client.exec_command(cmd)
            output = stdout.read().decode('utf-8').rstrip()
            return output.split("\n") if output else []  # will return string array
        except Exception as e:
            print(e)
            client.close()
    yield execute

@pytest.fixture
def execute_cmd_through_ssh_root():
    def execute(host, port, username, password, cmd):
        client = paramiko.SSHClient()
        try:
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy)
            client.connect(host, port=port, username=username, password=password)
            stdin, stdout, stderr = client.exec_command(f'sudo {cmd}', get_pty=True)
            stdin.write(f'{password}\n')
            stdin.flush()
            output = stdout.read().decode('utf-8').rstrip()
            for out in output.split("\r\n"):
                if out == f"[sudo] password for {username}:":
                    filter_q = f"[sudo] password for {username}:"
                    break
                elif out == f"[sudo] password for {username}: ":
                    filter_q = f"[sudo] password for {username}: "
                    break
            # print(f'filter: {filter_q}')
            key = output.split("\r\n").index(f"{filter_q}")+1
            return output.split("\r\n")[key:] if output else []  # will return string array
        except Exception as e:
            print(e)
            client.close()
    yield execute


@pytest.fixture
def copy_cert(ip_address, protocol):
    global cert_copy_flag
    try:
        if cert_copy_flag is False and protocol == "https":
            ssh_conn = paramiko.SSHClient()
            ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_conn.connect(hostname=ip_address, port=22, username='root', password='123456')
            sftp = ssh_conn.open_sftp()
            sftp.get("/usr/local/lib/mec/certs/root/ca.crt", "./tests/certs/ca.crt")
            print("success to copy certificate")
            cert_copy_flag = True
    except Exception as e:
        print(f"Failed to fetch controller certificate, error: {e}")
        return False
    return True
