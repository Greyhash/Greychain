#!/usr/bin/python3 -u 
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import threading
import urllib.request
import time
import http.server
import socketserver
import ssl
import copy

import BlockChain
import Block
import Transaction
import Key
import Mine
import Node
import Network
from Common import *

# Class to handle the server part of the program
# Should be easy for you to use another server if you dont like this basic http.server example
# Written by Victor Näslund <victor.naslund@greyhash.se>

# Multithreaded http.server
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass

# The request handler, requests run do_GET or do_POST depending on the request
class RequestHandler(http.server.BaseHTTPRequestHandler):
    server_version = "Greychain/0.9"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    # Mine a new proof so we can create a block
    def mine(self):
        next_proof = Mine.mine(self.blockchain.chain[-1].proof)

        # We finished mining, create block and send it into the network
        self.lock.acquire()
        
        while len(self.pending_transactions) > 0:
            pt = copy.deepcopy(self.pending_transactions)
            block = Block.create(self.public_key, str(time.time()), self.blockchain.chain[-1].hash(), next_proof)
            for t in range(0, len(pt)):
                if t >= 45:
                    break
                block.add_transaction(pt.pop(0))
        
            invalid_block = self.blockchain.add_block(block, self.blockchain.chain[-1].proof)
            
            # The block was invalid
            if invalid_block == -2 or invalid_block == 0:
                self.is_mining.clear()
                self.lock.release()
                return

            # One of the transactions was invalid, remove it and try again
            elif invalid_block > 0:
                del self.pending_transactions[invalid_block-1]
                
            else:
                print ("Mined a new block, added transactions and commited block to blockchain")
                Network.send_block_to_network(self.node_list, self.our_node, block.json().encode('utf-8'))
                del self.pending_transactions[0:45]

                if len(self.pending_transactions) > 0:
                    self.lock.release()
                    return self.mine()

        self.mining_lock.acquire()
        self.is_mining.clear()
        self.mining_lock.release()
        self.lock.release()

    # Send a response to the client
    def send_json_response(self, code, data):
        self.send_response(code)
        self.send_header("Content-type", 'text/json')
        self.send_header("Content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # Was the data in the POST reqest valid
    def is_valid_data(self):
        try:
            content_length = int(self.headers['Content-Length'])
            if content_length < 1:
                return None
            data = self.rfile.read(content_length)

            # Ensure data is utf-8
            data.decode('utf-8')

            # Get json object
            data = data_to_json(data)
            return data
        except:
            return None

    # GET requests begins here
    def do_GET(self):
        msg = None
        
        # Handle download chain requests
        if self.path == "/download":
            msg = self.download_chain()
        
        # Handle download nodes list
        elif self.path == "/node_list":
            msg = self.send_node_list()

        if msg is None:
            self.send_json_response(404, json.dumps("Not Found").encode('utf-8'))
        else:
            self.send_json_response(200, msg)

    # POST requests begin here
    def do_POST(self):
        data = self.is_valid_data()
        if data is None:
            self.send_json_response(401, json.dumps("Invalid post data"))
            return
        
        msg = None
        
        # Handle new transaction
        if self.path == "/post_transaction":
            msg = self.post_transaction(data)

        # Handle new block
        elif self.path == "/post_block":
            msg = self.post_block(data)

        # Handle new blockchain
        elif self.path == "/post_blockchain":
            msg = self.post_blockchain(data)

        # Handle new node
        elif self.path == "/post_node_list":
            msg = self.post_node_list(data)

        if msg is None:
            self.send_json_response(404, json.dumps("Not Found"))
        else:
            self.send_json_response(200, msg)

    # Send the our node list as json to the client
    def send_node_list(self):
        self.lock.acquire()
        data = json.dumps(self.node_list, default=convert_to_dict, indent=4, sort_keys=True).encode('utf-8')
        self.lock.release()
        return data

    # Send our entire blockchain as json to the client
    def download_chain(self):
        self.lock.acquire()
        data = self.blockchain.json().encode('utf-8')
        self.lock.release()
        return data

    # Add the received block to our blockchain
    def post_block(self, data):
        block = Block.json_to_block(data)
        if block is None:
            return b'{"Block accepted": false}'

        self.lock.acquire()
        
        if self.blockchain.add_block(block, self.blockchain.chain[-1].proof) == -1:
            self.blockchain.save_chain("greychain.txt")
            self.lock.release()
            print ("Received new block! blockchain length is " + str(len(self.blockchain)))
            return b'{"Block accepted": true}'
        else:
            self.lock.release()
            return b'{"Block accepted": false}'

    # Add new transaction to pending_transactions
    # Also start to mine if we are not already mining
    # Since we have new transactions we need to mine a proof to create a new block for the transactions
    def post_transaction(self, data):
        transaction = Transaction.json_to_transaction(data)
        if transaction is None:
            return b'{"Transaction accepted": false}'

        self.lock.acquire()
        self.pending_transactions.append(transaction)
        self.lock.release()

        self.mining_lock.acquire()
        if len(self.is_mining) == 0:
            mining_thread = threading.Thread(target=self.mine, args=())
            mining_thread.start()
            self.is_mining.append(True)
        self.mining_lock.release()
        
        print ("Received new transaction")
        return b'{"Transaction accepted": true}'

    # Request to replace our chain
    def post_blockchain(self, data):
        self.lock.acquire()
        chain = BlockChain.json_to_blockchain(data)
    
        if chain is None or self.blockchain.replace_chain(chain):
            self.blockchain.save_chain("greychain.txt")
            self.lock.release()
            return b'{"Blockchain accepted": false}'

        self.lock.release()
        return b'{"Blockchain accepted": true}'

    # Request to add a node to the network
    def post_node_list(self, data):
        self.lock.acquire()
        for n in range(0, len(data)):
            
            node = Node.json_to_node(data[n])
            if node is None:
                continue

            found = False
            for curr_node in range(0, len(self.node_list)):
                # If we already has this node in our list
                if self.node_list[curr_node].id == node.id:
                    found = True
                    break

            if not found:
                self.node_list.append(node)
                print ("Added new node to the network")

        Node.save_node_list(self.node_list, "node_list.txt")
        self.lock.release()
    
        return b'{"Node_list accepted": true}'

# Create/load our public/private key based on the seed and user password
def setup_seed(config):
    if os.path.isfile("./seed.txt"):
        seed = Key.load_seed("./seed.txt")
    else:
        seed = Key.create_seed()
    priv, pub = Key.create(config["password"], seed)
    return priv, pub

# Setup variables if this node is greyhash.se
def setup_greyhash_se(our_node):
    node_list = []
    node_list.append(our_node)
    
    if os.path.isfile("greychain.txt"):
        with open("greychain.txt") as json_file:
            data = json.load(json_file)

            blockchain = BlockChain.json_to_blockchain(data)
    else:
        blockchain = BlockChain.create()
        genesis_block = Block.create_genesis_block()
        blockchain.add_genesis_block(genesis_block)
        blockchain.save_chain("greychain.txt")
    return node_list, blockchain

# Setup variables if this node is not greyhash.se
def setup(our_node):
    # Download the node list
    node_list = Network.download_node_list()
    if node_list is None:
        print ("ERROR could not download network node list")
        sys.exit(1)

    # Save the node list to file
    Node.save_node_list(node_list, "node_list.txt")

    # Add our node to the network node list
    our_node_exist = False
    for node in range(0, len(node_list)):
        if our_node.id == node_list[node].id:
            our_node_exist = True
            break
    if not our_node_exist:
        node_list.append(our_node)
        
    # Download the blockchain from the network node list
    blockchain = Network.download_blockchain(node_list, our_node)
    if blockchain is None or len(blockchain) < 1:
        print ("ERROR Could not download blockchain from the network")
        sys.exit(1)
    else:
        print ("Downloaded blockchain from the network, blockchain length is now " + str(len(blockchain)))

    # Save the downloaded chain to file
    blockchain.save_chain("greychain.txt")
    
    # Send our node list to the network
    Network.send_node_list(node_list, our_node)
    return node_list, blockchain

# Main function
def main(argv):
    # Get configs from config file
    with open('config.json') as json_file:
        config = json.load(json_file)

    # Setup our private/public key
    priv, public_key = setup_seed(config)

    # Create our own node
    our_node = Node.create(protocol=config["protocol"], port=config["port"])

    # If this node is not greyhash.se
    if str(our_node.ip) != "54.77.253.75":
        node_list, blockchain = setup(our_node)
    else:
        node_list, blockchain = setup_greyhash_se(our_node)

    server_address = (config["hostname"], config["port"])

    # Define variables shared with the concurrent threads
    RequestHandler.lock = threading.Lock() # The lock we use to synchronize our threads access to these variables below
    RequestHandler.mining_lock = threading.Lock() # The lock we use to synchronize our threads for mining
    RequestHandler.blockchain = blockchain # The blockchain variable
    RequestHandler.pending_transactions = [] # Pending transaction waiting to be written into a new block and the block the added to the blockchain
    RequestHandler.our_node = our_node # Our node (information such as our ip address
    RequestHandler.node_list = node_list # List of the nodes in the network including our own
    RequestHandler.public_key = public_key # Our public key
    RequestHandler.is_mining = [] # if our node is currently mining a new block

    # Update the list of network nodes every 60 minutes
    Network.update_node_list(RequestHandler)
    
    # Create the http server object
    httpd = http.server.ThreadingHTTPServer(server_address, RequestHandler)
    
    # If we are using https
    if config["protocol"] == "https" and os.path.isfile(config["tls_cert"]) and os.path.isfile(config["tls_key"]):
        server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_context.options |= ssl.OP_NO_TLSv1
        server_context.load_cert_chain(config["tls_cert"], config["tls_key"])
        httpd.socket = server_context.wrap_socket(httpd.socket, server_side=True)
        print ("Listening for https on port " + str(config["port"]) + ", we are now a part of the network")
    else:
        print ("Listening for http on port " + str(config["port"]) + ", we are now a part of the network")
        print ("")
        print ("You can use https (change in config.json) instead if you create a https (tls) cert and key using this command")
        print ("openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365")
        print ("The network ignore all information on the cert, its only used to create an encrypted connection, Check so it works by using curl -vk https://localhost:" + str(config["port"]) + " The -k flag to ignore cert hostname/request hostname mismatch")

    # Start the http.server
    httpd.serve_forever()
        
if __name__== "__main__":
    main(sys.argv)
