import os
import sys
import time
import json

import Key
import BlockChain
from Common import *

# Class to handle the transactions
# Written by Victor Näslund <victor.naslund@greyhash.se>

class Transaction:

    # Constructor
    def __init__(self, amount, sender, receiver, time, message, signature):
        self.amount = amount
        self.sender = sender
        self.signature = signature
        self.time = time
        self.message = message
        self.receiver = receiver

    # String representation
    def __str__(self):
        return self.json()
        
    # Json representation
    def json(self):
        return json.dumps(self, default=convert_to_dict, indent=4, sort_keys=True)

# Ensure all transactions in transactions are unique and does not already exist in the blockchain
def unique_transaction(transactions, chain):
    sigs = []
    for t in range(0, len(transactions)):
        if transactions[t].signature in sigs:
            print ("Signature was not unique in the transactions list")
            return t
        sigs.append(transactions[t].signature)

    for block_index in range(1, len(chain)):
        for transaction_index in range (1, len(chain.chain[block_index].transactions)):
            if chain.chain[block_index].transactions[transaction_index].signature in sigs:
                print ("Signature was not unique in the blockchain")
                return t
    return -1

# Ensure the transactions senders had the amount they want to send
def senders_has_funds(transactions, chain):
    block_amount = {}
        
    for t in range(0, len(transactions)):
        if t > 0:
            if transactions[t-1].receiver not in block_amount:
                block_amount[transactions[t-1].receiver] = 0.0
            if transactions[t-1].sender not in block_amount:
                block_amount[transactions[t-1].sender] = 0.0
                
            block_amount[transactions[t-1].receiver] += transactions[t-1].amount
            block_amount[transactions[t-1].sender] -= transactions[t-1].amount
        else:
            continue

        acc_sum = chain.account_balance(transactions[t].sender)
        if transactions[t].sender in block_amount:
            acc_sum += block_amount[transactions[t].sender]
        if acc_sum  < transactions[t].amount:
            print ("Sender " + transactions[t].sender + " has " + str(acc_sum) + " wanted to send " + str(transactions[t].amount))
            return t
    return -1

# Verify the mining pay transaction
def verify_mining_pay(transaction):
    try:
        if transaction.message != b"Mining_pay".hex():
            return False
        if transaction.sender != "0":
            return False
        if transaction.signature != "0":
            return False
        if float(transaction.amount) != 13:
            return False
        if str(transaction.time) > str(time.time()):
            return False
    except:
        return False
    
    return True

# Verify the transactions in a block
def verify(transactions, chain):
    # Do not allow blocks without transactions or to many
    if len(transactions) < 2 or len(transactions) > 50:
        print ("Ignored transactions: To few or to many transactions")
        return -2

    if not verify_mining_pay(transactions[0]):
        print ("Ignored transactions: Invalid mining pay")
        return 0
    
    for t in range(1, len(transactions)):
        # Create public keys from the sender and receiver
        try:
            sender_pub = Key.pub_from_hex(transactions[t].sender)
            receiver_pub = Key.pub_from_hex(transactions[t].receiver)
        except:
            print ("Ignored transactions: Could not hex decode public key")
            return t

        # Validate the message signature
        try:
            Key.verify_sign(sender_pub, transactions[t].message, transactions[t].signature)
        except:
            print ("Ignored transactions: Invalid signature")
            return t

        # Get the message string
        try:
            message = bytes.fromhex(transactions[t].message).decode('utf-8')
        except:
            print ("Ignored transactions: Could not hex decode message")
            return t

        message_part = message.split(",")
        if len(message_part) != 6:
            print ("Ignored transactions: Invalid message")
            return t
        
        m_type = message_part[0]
        m_amount = message_part[1]
        m_sender = message_part[2]
        m_receiver = message_part[3]
        m_time = message_part[4]
        m_comment = message_part[5]

        try:
            if float(m_time) > time.time():
                print ("Time was newer than current time")
                return t
        except:
            print ("Time was not a timestamp")
            return t
                
        # Require the type to be only Pay for now
        if "Pay" != m_type:
            print ("Ignored transactions: Transactions message did not start with 'Pay'")
            return t

        try:
            if float(m_amount) <= 0.0:
                print ("Ignored transactions: Can only transfer amount greater than 0")
                return t
        except:
            print ("Ignored transactions: Amount was not a number")
            return t

        # Check sender and receiver keys to be the same as in the signed message
        if sender_pub != Key.pub_from_hex(m_sender):
            print ("Sender was not sender in message")
            return t
        if receiver_pub != Key.pub_from_hex(m_receiver):
            print ("Receiver was not sender in message")
            return t

    # Ensure the sender has the funds it is trying to send
    shf = senders_has_funds(transactions, chain)
    if not shf == -1:
        return shf
        
    ut = unique_transaction(transactions, chain)
    if not ut  == -1:
        print ("Transaction was not unique")
        return ut
        
    return -1

# Create a transaction object
def create(message, signature):
    if not isinstance(message, str):
        m = message.decode('utf-8')
    else:
        m = message
        
    amount = float(m.split(",")[1])
    sender_hex = m.split(",")[2]
    receiver_hex = m.split(",")[3]
    time = m.split(",")[4]
    
    return Transaction(amount, sender_hex, receiver_hex, time, m.encode('utf-8').hex(), signature.hex())

# Create the mining pay "transaction"
def create_mining_pay(receiver, time=None):
    if time is None:
        return Transaction(13, "0", receiver, str(time.time()), b"Mining_pay".hex(), "0")
    else:
        return Transaction(13, "0", receiver, time, b"Mining_pay".hex(), "0")

# Create a transaction object from json data
def json_to_transaction(data):
    try:
        m = bytes.fromhex(data["message"])
        s = bytes.fromhex(data["signature"])
        transaction = create(m, s)
        return transaction
    except:
        return None
