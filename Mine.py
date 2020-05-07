import os
import sys
import hashlib

# Module to handle mining
# Written by Victor Näslund <victor.naslund@greyhash.se>

# Verify a proof, yeah its that simple, the hashsum of the proof has to end with '21828'.
# We only care about the last 5 digits.
# Normally this is to little but this program was written in a educational purpose.
def verify_proof(h):
    if hashlib.sha256(h.encode("utf-8")).hexdigest()[-5:] == "21828":
        print(hashlib.sha256(h.encode("utf-8")).hexdigest())
    return hashlib.sha256(h.encode("utf-8")).hexdigest()[-5:] == "21828"
 
# Verify mining proof of work
def verify(prev_proof, proof):
    h = str(prev_proof) + "_" + str(proof)
    if verify_proof(h):
        return True
        
    print ("Invalid proof of work hash")
    return False

# "Mine", find a proof, integer here, combined with the last proof match
# Yes to "mine" is to hash stuff hoping the hashsum ends with something special
def mine(prev_proof):
    prev_proof = str(prev_proof)

    y = 0
    while True:                
        
        h = (prev_proof + "_" + str(y))
        if verify_proof(h): 
            print(y)          
            return y
        else:
            y += 1
