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
    #print(json_transaction)
    #sys.exit(0)
    with urllib.request.urlopen(req, timeout=5, context=ssl._create_unverified_context()) as f:
    
        return f.read()
     


def send_single_transaction():
    message, signature = Key.sign(priv_robin_1, "Pay,0.01," +             Key.hex(pub_robin_1) + "," + Key.hex(pub_robin_3) + "," + str(time.time()) + "," + "for the banana")
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

def test_false_transaction():
    message, signature = Key.sign(priv_robin_2, "Pay,-14," + Key.hex(pub_robin_2) + "," + Key.hex(pub_robin_1) + "," + str(time.time()) + "," + "for the banana")
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

# robin
if os.path.isfile("./seed_robin_1.txt"):
    seed_robin_1 = Key.load_seed("./seed_robin_1.txt")
else:
    seed_robin_1 = Key.create_seed()
    Key.save_seed(seed_robin_1, "./seed_robin_1.txt")

# 2
if os.path.isfile("./seed_robin_2.txt"):
    seed_robin_2 = Key.load_seed("./seed_robin_2.txt")
else:
    seed_robin_2 = Key.create_seed()
    Key.save_seed(seed_robin_2, "./seed_robin_2.txt")
    

# 3
if os.path.isfile("./seed_robin_3.txt"):
    seed_robin_3 = Key.load_seed("./seed_robin_3.txt")
else:
    seed_robin_3 = Key.create_seed()
    Key.save_seed(seed_robin_3, "./seed_robin_3.txt")

    
    

priv, pub = Key.create("change_me", seed)
priv2, pub2 = Key.create("change_me2", seed2)

#eobin
priv_robin_1, pub_robin_1 = Key.create("change_me", seed_robin_1)
priv_robin_2, pub_robin_2 = Key.create("change_me_robin_2", seed_robin_2)
priv_robin_3, pub_robin_3 = Key.create("change_me_robin_3", seed_robin_3)

data = send_single_transaction()
if debug:
    print ("Data from post_transaction:")
    print (data)


sys.exit(0)

tt = str(time.time())

for x in range(0, 5):
    data = download_chain()
    if debug:
        print ("Data from download:")
        print (data)
    blockchain = BlockChain.json_to_blockchain(data)

    if x == 1 or x == 3:
        data = test_false_transaction()
        if debug:
            print ("Data from post_transaction:")
            print (data)
    else:
        data = send_transaction()
        if debug:
            print ("Data from post_transaction:")
            print (data)
    time.sleep(0.5)
