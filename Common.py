import os
import sys
import json

# Module which holds common functionality for the rest of the program
# Written by Victor Näslund <victor.naslund@greyhash.se>

def convert_to_dict(obj):
    return obj.__dict__

def data_to_json(data):
    try:
        return json.loads(data)
    except:
        return None
