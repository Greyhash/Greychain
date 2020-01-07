import os
import sys
import time
import urllib.request
import ssl
import json

sys.path.append(".")

import BlockChain
import Block
import Mine
import Transaction
import Key

def download_chain():
    req = urllib.request.Request(url=config["protocol"] + "://localhost:" + str(config["port"]) + "/download")
    with urllib.request.urlopen(req, timeout=5, context=ssl._create_unverified_context()) as f:
        return f.read()

def send_transaction():
    message, signature = Key.sign(priv, "Pay,0.14," + Key.hex(pub) + "," + Key.hex(pub2) + "," + str(time.time()) + "," + "for the banana")
    transaction = Transaction.create(message, signature)
    
    json_transaction = transaction.json().encode('utf-8')
    req = urllib.request.Request(url=config["protocol"] + "://localhost:" + str(config["port"]) + "/post_transaction", data=json_transaction, method='POST')
    with urllib.request.urlopen(req, timeout=5, context=ssl._create_unverified_context()) as f:
        return f.read()

def send_false_transaction():
    message, signature = Key.sign(priv, "Pay_false,0.14," + Key.hex(pub) + "," + Key.hex(pub2) + "," + str(time.time()) + "," + "for the banana")
    transaction = Transaction.create(message, signature)
    
    json_transaction = transaction.json().encode('utf-8')
    req = urllib.request.Request(url=config["protocol"] + "://localhost:" + str(config["port"]) + "/post_transaction", data=json_transaction, method='POST')
    with urllib.request.urlopen(req, timeout=5, context=ssl._create_unverified_context()) as f:
        return f.read()

if len(sys.argv) == 2 and sys.argv[1] == "--debug":
    debug = True
else:
    debug = False

# Get configs from config file
with open('config.json') as json_file:
    config = json.load(json_file)
    
if os.path.isfile("./seed.txt"):
    seed = Key.load_seed("./seed.txt")
else:
    seed = Key.create_seed()
    Key.save_seed(seed, "./seed.txt")
    
if os.path.isfile("./seed2.txt"):
    seed2 = Key.load_seed("./seed2.txt")
else:
    seed2 = Key.create_seed()
    Key.save_seed(seed2, "./seed2.txt")

priv, pub = Key.create("change_me", seed)
priv2, pub2 = Key.create("change_me2", seed2)

tt = str(time.time())

for x in range(0, 5):
    data = download_chain()
    if debug:
        print ("Data from download:")
        print (data)
    blockchain = BlockChain.json_to_blockchain(data)

    if x == 1 or x == 3:
        data = send_false_transaction()
        if debug:
            print ("Data from post_transaction:")
            print (data)
    else:
        data = send_transaction()
        if debug:
            print ("Data from post_transaction:")
            print (data)
    time.sleep(0.5)
