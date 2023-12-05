## Configuration

By default, the leader server listens on `localhost` (`127.0.0.1`) at port `65432`, and follower servers listen on ports `65433` and `65434`. You can modify these settings in the `main.py` script if needed.

## Running the System

To start the Distributed Lock System, run the `main.py` script:

```
python main.py
```

This will start one leader server and two follower servers. It will also create multiple clients that will attempt to acquire, release, and check locks.

## Client Usage

To interact with the system programmatically, you can create instances of `LockClient` from the `client.py` module:

```
from client import LockClient

# Initialize a client with the server's host and port
client = LockClient(server_host='127.0.0.1', server_port=65432)

# Preempt (acquire) a lock
response = client.preempt_lock('my_lock')
print(response)

# Release a lock
response = client.release_lock('my_lock')
print(response)

# Check the status of a lock
response = client.check_lock('my_lock')
print(response)
```

## Server Usage

While the `main.py` script will start the servers automatically, you can also run server instances manually using the `server.py` module:

```
from server import LockServer

# Start a leader server
leader_server = LockServer(host='127.0.0.1', port=65432, is_leader=True)
leader_server.start()

# Start a follower server
follower_server = LockServer(host='127.0.0.1', port=65433, is_leader=False)
follower_server.start()
```

Make sure to run each server in a separate process or thread.

## Stopping the System

To stop the servers and clients, use a keyboard interrupt (`Ctrl+C`) in the terminal where `main.py` is running.