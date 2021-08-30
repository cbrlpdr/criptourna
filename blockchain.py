import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from block import Block
from urllib.parse import urlparse


def calculate_proof(new_proof, previous_proof):
    return hashlib.sha256(str((new_proof**2 - previous_proof**2)*29).encode()).hexdigest()


def hash(block):
    encoded_block = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(encoded_block).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.pool = []
        self.hardness = 4

    def create_block(self, proof, previous_hash):
        b = Block(proof=proof,
                  previous_hash=previous_hash,
                  chain=self.chain,
                  pool=self.pool
                  )
        block = b.get_block_dict()
        self.pool = []
        self.chain.append(block)

    def hash_condition(self, test_hash):
        return test_hash[:self.hardness] == "0000"

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        testing_proof = 1
        check_proof = False

        while not check_proof:
            hash_operation = calculate_proof(testing_proof, previous_proof)
            if self.hash_condition(hash_operation):
                check_proof = True
            else:
                testing_proof += 1

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = calculate_proof(proof, previous_proof)
            if not self.hash_condition(hash_operation):
                return False

            previous_block = block
            block_index += 1

        return True

    def add_vote(self, elector, vote):
        self.pool.append({
            'elector': elector,
            'vote': vote
        })
        previous_block = self.get_previous_block()

        return previous_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)

        for node in network:
            response = request.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False


