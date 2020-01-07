import os
import sys
import time
import pytz
import json
import Transaction
import hashlib

import Key
import BlockChain
import Mine
from Common import *

# Class to handle the blocks
# Written by Victor Näslund <victor.naslund@greyhash.se>

class Block:

    # Constructor
    def __init__(self, pub, time, prev_hash, proof):
        self.time = time
        self.transactions = list()

        if not isinstance(pub, str):
            pub = Key.hex(pub)

        if pub != "0":
            self.transactions.append(Transaction.create_mining_pay(pub, time))
            
        self.proof = proof
        self.prev_hash = prev_hash

    # The hash of the json representation
    def hash(self):
        j = json.dumps(self, default=convert_to_dict, indent=4, sort_keys=True)
        return hashlib.sha256(j.encode('utf-8')).hexdigest()

    # Allow len() to be used on BlockChain objects
    def __len__(self):
        return len(self.transactions)
    
    # String representation
    def __str__(self):
        return self.json()

    # Get the json representation
    def json(self):
        return json.dumps(self, default=convert_to_dict, indent=4, sort_keys=True)

    # Add a transaction to the block
    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    # Verify the block against the previous block's hash and the block's proof
    def verify(self, prev_proof, prev_hash, chain):
        # Ensure the mining proof is valid
        if not Mine.verify(chain.chain[-1].proof, self.proof):
            return -2

        if not self.prev_hash == prev_hash:
            print ("Previous block hash was invalid")
            return -2
        
        # Ensure the Transactions are valid
        v = Transaction.verify(self.transactions, chain)
        if not v == -1:
            return v

        return -1

# Create a Block object
def create(pub, time, prev_hash, proof):
    b = Block(pub, time, prev_hash, proof)
    return b

# Create the special genesis block
def create_genesis_block(t=None):
    if t is None:
        return Block("0", str(time.time()), "0", 0)
    else:
        return Block("0", t, "0", 0)

# Create a block object from json data
def json_to_block(data):
    try:
        block = create(data["transactions"][0]["receiver"], data["time"], data["prev_hash"], data["proof"])

        for transaction in range(1, len(data["transactions"])):
            message = bytes.fromhex(data["transactions"][transaction]["message"])
            signature = bytes.fromhex(data["transactions"][transaction]["signature"])
            t = Transaction.create(message, signature)
            block.add_transaction(t)
        
        return block
    except:
        return None

