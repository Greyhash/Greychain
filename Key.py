import os
import sys
import nacl.encoding
import nacl.signing
import hmac
import hashlib
import secrets

# Class to handle the blockchain
# Written by Victor Näslund <victor.naslund@greyhash.se>

def hex(key):
    return key.encode(encoder=nacl.encoding.HexEncoder).decode('utf-8')

def pub_from_hex(key):
    return nacl.signing.VerifyKey(key.encode('utf-8'), encoder=nacl.encoding.HexEncoder)

# Get a random seed 512 bites long
def create_seed():
    # Generate a seed of 512 random bits in hex form
    s = secrets.token_bytes(int(512/8))
    return s

# Save seed into file
def save_seed(seed, file_path):
    with open(file_path, "x") as f:
        f.write(seed.hex())

# Load seed from file
def load_seed(file_path):
    with open(file_path, "r") as f:
        seed = bytes.fromhex(f.read())
    return seed
        
def create(password, seed):
    # Generate the private key seed from the user's password and seed
    h = hmac.new(password.encode('utf-8'), seed, hashlib.sha256).hexdigest(),

    priv = nacl.signing.SigningKey(h[0], encoder=nacl.encoding.HexEncoder)
    pub = priv.verify_key

    return priv, pub

def verify_sign(pub, message, signature):
    if isinstance(pub, str):
        pub = key_from_hex(pub)

    if isinstance(message, str):
        message = bytes.fromhex(message)

    if isinstance(signature, str):
        signature = bytes.fromhex(signature)
        
    return pub.verify(message, signature)

def sign(priv, message):
    signed = priv.sign(message.encode('utf-8'))
    return signed.message, signed.signature

def store_key(path, key):
    f = open(path,'x')
    f.write(key)
    f.close()
    
