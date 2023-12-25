'''
Author: Suizhi HUANG && sunrisen.huang@gmail.com
Date: 2023-11-29 15:41:10
LastEditors: Suizhi HUANG && sunrisen.huang@gmail.com
LastEditTime: 2023-12-25 09:46:00
FilePath: /DistributedLock/server.py
Description: 
Copyright (c) 2023 by $Suizhi HUANG, All Rights Reserved. 
'''
import socket
import threading
import json

HOST = '127.0.0.1'
LEADER_PORT = 65432
FOLLOWER_PORTS = [65433, 65434]  # Add more ports for additional followers

def send_message(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(json.dumps(message).encode('utf-8'))
        response = s.recv(1024)
    return json.loads(response.decode('utf-8'))

class LockServer:
    def __init__(self, host, port, is_leader=False):
        self.locks = {}
        self.host = host
        self.port = port
        self.is_leader = is_leader
        self.followers = [] if is_leader else None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.lock = threading.Lock()

    def start(self):
        print(f"{'Leader' if self.is_leader else 'Follower'} server started on {self.host}:{self.port}")
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        with client_socket:
            while True:
                message = client_socket.recv(1024)
                if not message:
                    break
                data = json.loads(message.decode('utf-8'))
                if self.is_leader:
                    result = self.handle_leader_request(data)
                else:
                    result = self.handle_follower_request(data)
                client_socket.sendall(json.dumps(result).encode('utf-8'))

    def is_valid_operation(self, data):
        if data['action'] not in ['preempt', 'release', 'check','update']:
            return False
        if data['action'] != 'check' and data['lock_name'] not in self.locks and data['action'] != 'preempt':
            return False
        if data['action'] == 'release' and self.locks.get(data['lock_name']) != data['client_id']:
            return False
        return True

    def handle_leader_request(self, data):
        if not self.is_valid_operation(data):
            return {'result': False, 'reason': 'Invalid operation'}
        if data['action'] == 'preempt':
            success = self.preempt_lock(data['lock_name'], data['client_id'])
        elif data['action'] == 'release':
            success = self.release_lock(data['lock_name'], data['client_id'])
        elif data['action'] == 'check':
            owner = self.check_lock(data['lock_name'])
            return {'owner': owner}
        return {'result': success}

    
    def handle_follower_request(self, data):
        if data['action'] == 'update':
            self.update_lock(data['lock_name'], data['client_id'])
            return {'result': True}
        else:
            # For other actions, forward the request to the leader and wait for the response.
            result = send_message(HOST, LEADER_PORT, data)
            return result

    def preempt_lock(self, lock_name, client_id):
        with self.lock:
            if lock_name not in self.locks:
                self.locks[lock_name] = client_id
                self.propagate_to_followers({'action': 'update', 'lock_name': lock_name, 'client_id': client_id})
                return True
            return False

    def release_lock(self, lock_name, client_id):
        with self.lock:
            if self.locks.get(lock_name) == client_id:
                del self.locks[lock_name]
                self.propagate_to_followers({'action': 'update', 'lock_name': lock_name, 'client_id': None})
                return True
            return False

    def check_lock(self, lock_name):
        return self.locks.get(lock_name, None)

    def update_lock(self, lock_name, client_id):
        if client_id is None:
            self.locks.pop(lock_name, None)
        else:
            self.locks[lock_name] = client_id

    def propagate_to_followers(self, message):
        # Ensure the message has the 'update' action before propagating to followers.
        message['action'] = 'update'
        for follower in self.followers:
            threading.Thread(target=send_message, args=(follower[0], follower[1], message), daemon=True).start()

    def add_follower(self, host,port): 
        self.followers.append((host, port))