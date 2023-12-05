'''
Author: Suizhi HUANG && sunrisen.huang@gmail.com
Date: 2023-11-29 15:40:50
LastEditors: Suizhi HUANG && sunrisen.huang@gmail.com
LastEditTime: 2023-12-01 16:52:11
FilePath: /DistributedLock/client.py
Description: 
Copyright (c) 2023 by $Suizhi HUANG, All Rights Reserved. 
'''
import socket
import uuid
import json

def send_message(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(json.dumps(message).encode('utf-8'))
        response = s.recv(1024)
    return json.loads(response.decode('utf-8'))

class LockClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.client_id = str(uuid.uuid4())

    def preempt_lock(self, lock_name):
        return send_message(self.server_host, self.server_port, {
            'action': 'preempt',
            'lock_name': lock_name,
            'client_id': self.client_id
        })

    def release_lock(self, lock_name):
        return send_message(self.server_host, self.server_port, {
            'action': 'release',
            'lock_name': lock_name,
            'client_id': self.client_id
        })

    def check_lock(self, lock_name):
        return send_message(self.server_host, self.server_port, {
            'action': 'check',
            'lock_name': lock_name
        })