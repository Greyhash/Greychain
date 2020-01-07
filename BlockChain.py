import os
import sys
import json
import hashlib

import Block
import Mine
import Key
import Transaction
from Common import *

# Class to handle the blockchain
# Written by Victor Näslund <victor.naslund@greyhash.se>

class BlockChain:
    
    # Constructor
    def __init__(self):
        self.chain = list()
        
    # Enable iteration over the chain
    def __iter__(self):
        self.iter_index = -1
        return self

    # Enable iteration over the chain
    def __next__(self):
        if self.iter_index+2 > len(self.chain):
            raise StopIteration

        self.iter_index += 1
        return self.chain[self.iter_index]

    # Allow len() to be used on BlockChain objects
    def __len__(self):
        return len(self.chain)

    # String representation
    def __str__(self):
        return self.json()

    # Replace the chain if the newer one is longer
    def replace_chain(self, chain):
        if len(chain) > len(self):
            self.chain = chain.chain
            print ("Replaced our chain with a longer one, length is now " + str(len(self)))
            return True

        print ("Our chain was longer or equally long, this usually indicates problems with the new chain")
        return False
    
    # Add block to chain
    def add_block(self, block, proof):
        v = block.verify(self.chain[-1].proof, self.chain[-1].hash(), self)
        if not v == -1:
            return v
        
        self.chain.append(block)
        return -1
        
    # Add genesis block to chain
    def add_genesis_block(self, block):
        if len(self.chain) == 0:
            self.chain.append(block)

    # The current blockchain balance for an account 
    def account_balance(self, pub):
        b = 0.0
        key = Key.pub_from_hex(pub)
        
        for block in self.chain:
            for transaction in range(0, len(block.transactions)):
                if block.transactions[transaction].receiver == key:
                    b += block.transactions[transaction].amount
                elif block.transactions[transaction].sender == key:
                    b -= block.transactions[transaction].amount
        return b
                            
    # Save blockchain to a file
    def save_chain(self, file_path):
        with open(file_path, 'w') as outfile:
            json.dump(self.chain, outfile, default=convert_to_dict, indent=4, sort_keys=True)

    # Get the json representation
    def json(self):
        return json.dumps(self.chain, default=convert_to_dict, indent=4, sort_keys=True)

# Create an entire blockchain object from json data
def json_to_blockchain(data):
    try:
        chain = create()
        genesis_block = Block.create_genesis_block(data[0]["time"])
        chain.add_genesis_block(genesis_block)

        for block_index in range(1, len(data)):
            block = Block.create(data[block_index]["transactions"][0]["receiver"], data[block_index]["time"], data[block_index]["prev_hash"], data[block_index]["proof"])

            for transaction in range(1, len(data[block_index]["transactions"])):
                message = bytes.fromhex(data[block_index]["transactions"][transaction]["message"])
                signature = bytes.fromhex(data[block_index]["transactions"][transaction]["signature"])
                t = Transaction.create(message, signature)
                block.add_transaction(t)
            if not chain.add_block(block, chain.chain[-1].proof):
                return None
            
        return chain
    except:
        #raise
        return None

# Create a BlockChain object
def create():
    return BlockChain()
