import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


class Block:
    def __init__(self, proof, previous_hash, chain, pool):
        self.index = len(chain) + 1,
        self.timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.proof = proof
        self.previous_hash = previous_hash
        self.data = pool

    def get_block_dict(self) -> dict:
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'proof': self.proof,
            'previous_hash': self.previous_hash,
            'data': self.data
        }

    def get_block_data(self):
        return self.data
