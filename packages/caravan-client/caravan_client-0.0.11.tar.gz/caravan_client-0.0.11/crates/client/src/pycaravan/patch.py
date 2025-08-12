from dataclasses import dataclass
import pickle
import socket
import torch
import random

HOST = '127.0.0.1'
PORT = 65432        
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
# This code builds off the benchmarking code in patch_benchmarking.py

def dumps(obj, protocol=None):
    return pickle.dumps(obj, protocol=protocol)

def loads(serialized_obj):
    return pickle.loads(serialized_obj)

@dataclass
class RId:
    rid: int
    def __init__(self):
        self.rid = random.getrandbits(64)
    def __hash__(self):
        return self.rid

def create_patched_func(func):
    def patched_func(*args, **kwargs):
        name = func.__name__
        module = func.__module__
        
        print(f"Calling patched function: {module}.{name} with args={args}, kwargs={kwargs}")   
        bytes = dumps((module, name, args, kwargs))
        try:
              client_socket.getpeername()  # This will raise an exception if not connected
              print("Client socket is already connected with peername:", client_socket.getpeername())
        except (OSError, socket.error):
              client_socket.connect((HOST, PORT))
              print(f"Connected to server at {HOST}:{PORT}")
        

        client_socket.sendall(bytes)
        print(f"Sent serialized function call to server: {module}.{name} with args={args}, kwargs={kwargs}")
        recvd_bytes = client_socket.recv(4096)  # Adjust buffer size as needed
        print(f"Received bytes from server, length: {len(recvd_bytes)}")
        
        result = loads(recvd_bytes)  # Adjust buffer size as needed
        print(f"Received result from server: {result}")

        # original_result = func(*args, **kwargs)
        # assert result == original_result
        
        return result

    return patched_func


def patched_func(func_obj, *args, **kwargs):
    func_name = func_obj.__name__
    func_module = func_obj.__module__

    # replace tensors with rids
    for arg in args:
        if isinstance(arg, torch.tensor) or isinstance(arg, torch.Tensor):
            new_id = id(arg)
            arg = rid(rid=new_id)  # replace tensor with rid

    for key, value in kwargs.items():
        if isinstance(value, torch.tensor) or isinstance(value, torch.Tensor):
            new_id = id(value)
            kwargs[key] = rid(rid=new_id)

    # Serialize the function call
    serialized_obj = dumps((func_module, func_name, args, kwargs))
    res = send_bytes(serialized_obj)
    deserialized_result = loads(res)
    return deserialized_result

def serialize_func_call(func_obj, *args, **kwargs):
    return dumps((func_obj.__module__, func_obj.__name__, args, kwargs))



# 1) Parse original function call into namespace, function, args, kwargs
# 2) Replacement of tensors with RIDs where applicable
# 3) Bundle and serialize object
# 4) Deserialize object
# 5) Unpack object into namespace, function, args, kwargs
# 6) Replacement of RIDs with tensors where applicable
# 7) Call the function with the unpacked args and kwargs
# 8) Send the result back to the client

'''
import torch
import torch.nn as nn

func_type = type(torch.add)
func_name = torch.add.__name__
print(f'Function type: {func_type}')
print(f'Function name: {func_name}')
func_module = torch.add.__module__
print(f'Function module: {func_module}')

func_type = type(torch.nn.functional.relu)
func_name = torch.nn.functional.relu.__name__
print(f'Function type: {func_type}')
print(f'Function name: {func_name}')
func_module = torch.nn.functional.relu.__module__
print(f'Function module: {func_module}')

func_type = type(nn.functional.relu)
func_name = nn.functional.relu.__name__
print(f'Function type: {func_type}')
print(f'Function name: {func_name}')
func_module = nn.functional.relu.__module__
print(f'Function module: {func_module}')
'''





