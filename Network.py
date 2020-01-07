import os
import sys
import urllib.request
import json
import Node
import BlockChain
import ssl
import multiprocessing.pool
import threading
import time
import copy
from Common import *

# Class to handle the outgoing network functions the program need
# Written by Victor Näslund <victor.naslund@greyhash.se>

# Update the list of nodes in the network every hour
def update_node_list(RequestHandler):
    threading.Timer(60*60, update_node_list, args=[RequestHandler]).start() # called every minute
    RequestHandler.lock.acquire()
    node_list = copy.deepcopy(RequestHandler.node_list)
    pool = multiprocessing.pool.ThreadPool(5)

    try:
        for node in range(0, len(node_list)):
            if node_list[node].id == RequestHandler.our_node.id:
                our_index = node
            node_list[node].path = "/node_list"
            node_list[node].method = "GET"

        pool_output = pool.imap(send_request, node_list)

        lst = []
        counter = 0
        for x in pool_output:
            if x is not None and our_index != counter:
                lst.append(RequestHandler.node_list[counter])
            counter += 1
    
        lst.append(RequestHandler.node_list[our_index])
        RequestHandler.node_list = lst
    except:
        pass
        #raise

    pool.close()
    pool.join()
    RequestHandler.lock.release()

# Send a http request to the node
def send_request(node):
    try:
        if node.method == "POST":
            req = urllib.request.Request(node.protocol + "://" + node.ip + ":" + node.port + node.path, data=node.data, method='POST')
        else:
            req = urllib.request.Request(node.protocol + "://" + node.ip + ":" + node.port + node.path, method='GET')
        
        if "https" == node.protocol:
                with urllib.request.urlopen(req, timeout=3, context=ssl._create_unverified_context()) as f:
                    pass
        else:
            with urllib.request.urlopen(req, timeout=3) as f:
                pass
        return True
    except:
        return None

# Send to node list to all nodes in the network
def send_node_list(node_list, our_node):
    node_list = copy.deepcopy(node_list)
    pool = multiprocessing.pool.ThreadPool(5)
    
    try:
        data = json.dumps(node_list, default=convert_to_dict).encode('utf-8')
        for node in range(0, len(node_list)):
            if node_list[node].id != our_node.id:
                node_list[node].path = "/post_node_list"
                node_list[node].method = "POST"
                node_list[node].data = data
        pool_output = pool.map(send_request, node_list)
    except:
        #raise
        pass

    pool.close()
    pool.join()

# Download the node list from greyhash.se
def download_node_list():
    node_list = []
    try:
        data = urllib.request.urlopen("https://greyhash.se:8008/node_list", timeout=3, context=ssl._create_unverified_context()).read().decode('utf8')
        data = json.loads(data)
            
        for node in range(0, len(data)):
            n = Node.json_to_node(data[node])
                
            if n is None:
                continue
            
            node_list.append(n)
        return node_list
    except:
        raise
        return None

# Send the block to all nodes in the network
def send_block_to_network(node_list, our_node, block):
    node_list = copy.deepcopy(node_list)
    pool = multiprocessing.pool.ThreadPool(5)
    
    try:
        for node in range(0, len(node_list)):
            if node_list[node].id != our_node.id:
                node_list[node].path = "/post_block"
                node_list[node].method = "POST"
                node_list[node].data = block
        pool_output = pool.map(send_request, node_list)
    except:
        raise
        #print ("Timeout during send block to " + str(node_list[node].ip))

    pool.close()
    pool.join()

# Download the blockchain from all nodes
def download_blockchain(node_list, our_node):
    chain = BlockChain.create()
    
    for node in range(0, len(node_list)):
        try:
            if node_list[node].id == our_node.id:
                continue

            if node_list[node].protocol == "https":
                data = urllib.request.urlopen(node_list[node].protocol + "://" + node_list[node].ip + ":" + node_list[node].port + "/download", timeout=3, context=ssl._create_unverified_context()).read().decode('utf8')
            else:
                data = urllib.request.urlopen(node_list[node].protocol + "://" + node_list[node].ip + ":" + node_list[node].port + "/download", timeout=3).read().decode('utf8')
            data = json.loads(data)
            data = BlockChain.json_to_blockchain(data)
            if data is None:
                continue
            
            chain.replace_chain(data)
            return chain
        except:
            pass
    return None
