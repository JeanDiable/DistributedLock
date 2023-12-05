# Distributed Lock Design

## Introduction

In the realm of distributed systems, managing access to shared resources is a critical challenge. Distributed Lock aims to tackle this challenge by creating a simple yet robust consensus system that coordinates distributed locking mechanisms across multiple servers. The core objective of the project is to design a system that ensures consistency and fairness in acquiring and releasing locks for distributed resources.

The proposed system architecture comprises a single leader server and multiple follower servers. Each follower server maintains a replicated map that mirrors the leader server's map. This map holds the crucial information for the distributed locking mechanism, with keys representing the names of the distributed locks and values containing the IDs of the clients who currently own those locks.

The system is designed to handle multiple clients attempting to perform three key operations: preempting a lock, releasing a lock, and checking the ownership of a lock. Preemption rules dictate that a lock can be successfully acquired if it does not already exist; otherwise, the attempt will fail. Release operations are contingent on the requesting client being the current lock owner. Any client is permitted to query the owner of a lock without restrictions.

To maintain data consistency, the leader server plays a pivotal role in processing requests to preempt or release locks. It is responsible for proposing changes to the replicated maps on follower servers whenever modifications are necessary. Follower servers, upon receiving such proposals, update their local maps accordingly and resolve any pending client requests.

Clients interfacing with this system are equipped with functionalities to preempt, release, and check locks. Each client is initialized with a unique identifier, derived from user information via UUID, and is configured with the IP address of the target server they will interact with.

## Implementation

### System Architecture

The system comprises three main components: 

1. The `client.py` module represents the client-side logic, allowing clients to communicate with the server to manage locks. 
2. The `server.py` module embodies the server-side functionality, with the ability to act as either a leader or a follower in the distributed system. 
3. The `main.py` script initializes the system, starting servers and simulating client interactions. 

- The `client.py` module represents the client-side component of the Distributed Lock System. It includes the `LockClient` class, which provides methods for clients to interact with the server. Each client can preempt a lock, release a lock, or check the status of a lock. Additionally, the module contains a helper function, `send_message`, for sending messages to the server and receiving responses.

  - Key Functions and Attributes:

    - `send_message(host, port, message)`: A function that establishes a TCP connection to the server at the specified host and port, sends a JSON-encoded message, and waits for a response. It returns the decoded JSON response from the server.

    - `client_id`: A unique identifier for the client, generated using `uuid.uuid4()` to ensure that each client has a distinct identity in the system.

  - Client Initialization: When a `LockClient` instance is created, it is initialized with the server's host and port information and generates a unique `client_id` for itself.

  - Client Methods:

    - `preempt_lock(lock_name)`: Sends a request to the server to preempt (acquire) a lock with the specified `lock_name`. The request includes the client's `client_id` to identify who is attempting to acquire the lock.

    - `release_lock(lock_name)`: Sends a request to release a lock that the client currently owns. The `lock_name` and `client_id` are included to validate ownership and authorize the release.

    - `check_lock(lock_name)`: Sends a request to check the current owner of the specified lock. This operation does not require the client's `client_id` since it is a read-only action.

  - Communication Protocol: The communication between the client and the server relies on a simple JSON-based protocol. Each message is a JSON object containing at least an `action` field (such as `preempt`, `release`, or `check`) and a `lock_name`. For `preempt` and `release` actions, the `client_id` is also included.

- The `server.py` module encapsulates the server-side logic of the Distributed Lock System. It defines the `LockServer` class, which is responsible for handling lock-related requests from clients, managing the lock state, and ensuring consistency across the distributed system. The `LockServer` class can function as either a leader or a follower within the system's architecture, depending on the `is_leader` flag passed during initialization.

  - Key Attributes:

    - `locks`: A dictionary that serves as the primary data store for the server, mapping lock names to client IDs that currently hold the lock.

    - `host` and `port`: Network address information where the server listens for incoming connections.

    - `is_leader`: A boolean flag indicating whether the server instance is the leader.

    - `followers`: A list of follower servers (used by the leader server) to propagate updates.

    - `server_socket`: A socket object for accepting network connections.

    - `lock`: A threading lock to ensure thread-safe operations on the shared `locks` dictionary.

  - Server Initialization: Upon instantiation, the `LockServer` initializes its attributes, sets up the server socket, and starts listening for incoming connections.

  - Connection Handling: The `start` method launches a new thread that runs the `accept_connections` method. This method continuously waits for new client connections. When a client connects, a new thread is spawned to handle the client's requests via the `handle_client` method.

  - Client Request Handling: The `handle_client` method is the core of the server's request processing logic. It reads messages from the client, decodes them from JSON, and determines the appropriate action based on whether the server is a leader or a follower.

  - Leader Server Logic:

    - The `handle_leader_request` method processes client requests and performs the necessary operations based on the action specified (`preempt`, `release`, `check`).

    - The `preempt_lock` method attempts to acquire a lock for the client. If the lock is not currently held, it assigns the lock to the client and propagates the update to followers.

    - The `release_lock` method releases a lock if the requesting client is the current owner, removing the client ID from the `locks` map and notifying followers of the change.

    - The `check_lock` method provides the client ID of the lock's current owner or `None` if the lock is not held.

    - The `propagate_to_followers` method sends updates to all follower servers to synchronize the state of the locks.

  - Follower Server Logic:

    - The `handle_follower_request` method forwards requests to the leader server if the action is not an `update` or applies the update to its local `locks` map if it is.

    - The `update_lock` method updates the local `locks` map based on the information received from the leader server.

  - Validation:
    - The `is_valid_operation` method checks if a request is valid based on the current state of the `locks` map and the requested action.

  - Concurrency: The `LockServer` employs a threading lock (`self.lock`) to ensure that operations on the `locks` map are atomic and thread-safe. This prevents race conditions and ensures consistent behavior when multiple clients interact with the system concurrently.

  

- Main Script (`main.py`): The `main.py` script sets up the distributed lock system by starting the leader and follower servers. It then creates multiple client instances, each attempting to preempt, release, and check locks on various resources. The script simulates a sequence of client operations to demonstrate the system's functionality and handles graceful shutdown upon user interruption. 

### Operational Workflow

1. The leader server starts and awaits connection requests. Follower servers are also started and connected to the leader. 
2. Clients send lock management requests to their configured servers. 
3. If a client sends a request to a follower server, the follower forwards the request to the leader.
4. The leader server processes the request:  
   - For `preempt` requests, the leader checks if the lock exists. If not, it grants the lock to the client and informs the followers. 
   - For `release` requests, the leader verifies the client's ownership before releasing the lock and updates the followers.  
   - For `check` requests, the leader returns the current owner of the lock. 
5. The followers update their replicated maps upon receiving updates from the leader. 
6. Clients receive responses to their requests, indicating success or failure and providing lock ownership information when applicable. 

## Experiments

In the main.py, we implement 3 different scenarios for testing the effectiveness of our system. We first 

1. Each client could preempt a lock, release a lock, or check a lock wether it is bind to the leader server or the follower server

![image-20231201192123742](https://raw.githubusercontent.com/JeanDiable/MyGallery/main/img/image-20231201192123742.png)

2. When a client of the follower server tries to preempt a lock, other clients could not preempt the same lock

![image-20231201192236724](https://raw.githubusercontent.com/JeanDiable/MyGallery/main/img/image-20231201192236724.png)

3. When a client of the leader server tries to preempt a lock, other clients could not preempt the same lock

![image-20231201192156371](https://raw.githubusercontent.com/JeanDiable/MyGallery/main/img/image-20231201192156371.png)