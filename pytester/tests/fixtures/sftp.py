# !/usr/bin/env python
# -*-coding: utf-8 -*-

import pytest
import paramiko

RES_MGNT_PATH = 'tests/resource_management_testcases/files/'


@pytest.fixture
def sftp_access_host(ip_address):
    nev_infos = {}
    nev_infos.update({'host': ip_address})
    nev_infos.update({'port': 22})
    nev_infos.update({'username': 'user'})
    nev_infos.update({'password': '123456'})
    yield nev_infos


@pytest.fixture
def sftp_connect(sftp_access_host):
    infos = sftp_access_host
    hostname = infos.get('host')
    username = infos.get('username')
    password = infos.get('password')
    port = infos.get('port')
    t = paramiko.Transport((hostname, port))
    t.connect(username=username, password=password)
    transport = paramiko.SFTPClient.from_transport(t)
    yield transport


@pytest.fixture
def sftp_connect_put_res(sftp_connect):

    def _exec(local_file, remote_file):
        file_path = RES_MGNT_PATH + local_file
        t = sftp_connect
        t.put(file_path, remote_file)
        return t
    yield _exec

@pytest.fixture
def sftp_connect_del(sftp_connect):

    def _exec(remote_file):
        t = sftp_connect
        t.remove(remote_file)
        return t
    yield _exec
