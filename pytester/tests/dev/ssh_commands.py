# !/usr/bin/env python
# -*-coding: utf-8 -*-


def wrapper(host, username, password, cmd):
    cmd_infos = {}
    cmd_infos.update({'host': host})
    cmd_infos.update({'port': 22})
    cmd_infos.update({'username': username})
    cmd_infos.update({'password': password})
    cmd_infos.update({'cmd': cmd})
    return cmd_infos



#default setting
class SSHCommands(object):
    def __init__(self):
        super(SSHCommands, self).__init__()

    @property
    def golden_status(self):
        host = '127.0.0.1'
        username = 'user'
        password = '1234'
        cmd = 'ls -l'
        cmd_infos = wrapper(host, username, password, cmd)
        return cmd_infos

    @property
    def golden_status_1804(self):
        host = '127.0.0.1'
        username = 'user'
        password = '123456'
        cmd = 'ls -l'
        cmd_infos = wrapper(host, username, password, cmd)
        return cmd_infos

SSH_Commands = SSHCommands()
