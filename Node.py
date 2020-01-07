import os
import sys
import hashlib
import uuid
import json
import urllib.request
import ipaddress
from Common import *

# Class which has the info of a node in the network
# Written by Victor Näslund <victor.naslund@greyhash.se>

class Node:

    # Constructor
    def __init__(self, id, ip, protocol, port):
        self.id = id
        self.ip = ip
        self.protocol = protocol
        self.port = port

    # String representation
    def __str__(self):
        return self.json()

    # Json representation
    def json(self):
        return json.dumps(self, default=convert_to_dict, indent=4, sort_keys=True)

# Create a node object
def create(id=None, ip=None, protocol=None, port=None):
    try:
        if id is None:
            id = hashlib.sha256(str(uuid.uuid1()).encode('utf-8')).hexdigest()
        if ip is None:
            # Get the current public ip using https://v4.ident.me
            ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
        if protocol is None:
            protocol = "http"
        if port is None:
            port = 8008
        if len(id) < 10 or len(id) > 70:
            return None
    
        ip = ipaddress.ip_address(ip)
        return Node(id, str(ip), str(protocol), str(port))
    except:
        raise
        return None

# Create a node object from json data
def json_to_node(data):
    try:
        id = str(data["id"])
        ip = str(data["ip"])
        protocol = str(data["protocol"])
        port = str(data["port"])

        node = create(id, ip, protocol, port)
        return node
    except:
        return None

# Save the list of nodes to a file
def save_node_list(node_list, file_path):
    with open(file_path, 'w') as outfile:
        json.dump(node_list, outfile, default=convert_to_dict, indent=4, sort_keys=True)

