'''
Author: Suizhi HUANG && sunrisen.huang@gmail.com
Date: 2023-11-29 15:41:10
LastEditors: Suizhi HUANG && sunrisen.huang@gmail.com
LastEditTime: 2023-12-25 09:40:32
FilePath: /undefined/Users/suizhi/Desktop/研究生/研二/DistributedLock/main.py
Description: 
Copyright (c) 2023 by $Suizhi HUANG, All Rights Reserved. 
'''

import time
from client import LockClient
from server import LockServer

# Global constants
HOST = '127.0.0.1'
LEADER_PORT = 65432
FOLLOWER_PORTS = [65433, 65434]  # Add more ports for additional followers

# Main function to start the servers and demonstrate the lock system
def main():
    # Start the leader server
    leader_server = LockServer(HOST, LEADER_PORT, is_leader=True)
    leader_server.start()
    
    # Start follower servers
    follower_servers = []
    all_ports = FOLLOWER_PORTS + [LEADER_PORT]
    for port in FOLLOWER_PORTS:
        follower_server = LockServer(HOST, port, is_leader=False)
        follower_server.start()
        follower_servers.append(follower_server)
        leader_server.add_follower(HOST, port)

    # Wait for servers to start up (not ideal for production code)
    time.sleep(1)

    # Create multiple clients, some connecting to the leader, others to followers
    clients = [LockClient(HOST, port) for port in all_ports]

    # each client could preempt a lock, release a lock, or check a lock
    print('each client could preempt a lock, release a lock, or check a lock wether it is bind to the leader server or the follower server')
    for i, client in enumerate(clients):
        lock_name = f'resource{i+1}'
        print(f"Client {client.client_id[:6]} attempting to preempt lock '{lock_name}':", client.preempt_lock(lock_name))
        print(f"Client {client.client_id[:6]} checking lock '{lock_name}':", client.check_lock(lock_name))
        print(f"Client {client.client_id[:6]} attempting to release lock '{lock_name}':", client.release_lock(lock_name))
        print(f"Client {client.client_id[:6]} checking lock '{lock_name}':", client.check_lock(lock_name))

    # when a client of the follower server tries to preempt a lock, other clients could not preempt the same lock
    print('-----------------------------------------------')
    print('when a client of the follower server tries to preempt a lock, other clients could not preempt the same lock')
    print(f"Client {clients[1].client_id[:6]} attempting to preempt lock 'resource':", clients[1].preempt_lock('resource'))
    print(f"Client {clients[2].client_id[:6]} attempting to preempt lock 'resource':", clients[2].preempt_lock('resource'))
    print(f"Client {clients[0].client_id[:6]} attempting to release lock 'resource':", clients[0].release_lock('resource'))
    print(f"Client {clients[2].client_id[:6]} checking lock 'resource':", clients[2].check_lock('resource'))
    print(f"Client {clients[1].client_id[:6]} releasing lock 'resource':", clients[1].release_lock('resource'))
    print(f"Client {clients[2].client_id[:6]} checking lock 'resource':", clients[2].check_lock('resource'))
    
    # when a client of the leader server tries to preempt a lock, other clients could not preempt the same lock
    print('-----------------------------------------------')
    print('when a client of the leader server tries to preempt a lock, other clients could not preempt the same lock')
    print(f"Client {clients[2].client_id[:6]} attempting to preempt lock 'resource':", clients[2].preempt_lock('resource'))
    print(f"Client {clients[1].client_id[:6]} attempting to preempt lock 'resource':", clients[1].preempt_lock('resource'))
    print(f"Client {clients[0].client_id[:6]} attempting to release lock 'resource':", clients[0].release_lock('resource'))
    print(f"Client {clients[1].client_id[:6]} checking lock 'resource':", clients[1].check_lock('resource'))
    print(f"Client {clients[2].client_id[:6]} releasing lock 'resource':", clients[2].release_lock('resource'))
    print(f"Client {clients[1].client_id[:6]} checking lock 'resource':", clients[1].check_lock('resource'))

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()