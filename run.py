import datetime
from flask import Flask, jsonify, request
# import requests
from uuid import uuid4
from criptourna.models.blockchain import Blockchain, hash

app = Flask(__name__)

node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    start_time = datetime.datetime.now()
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = hash(previous_block)
    blockchain.add_vote(node_address, 'candidate')
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Created block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'elapsed_mining_time': str(
                    datetime.datetime.strptime(block['timestamp'],
                                               '%Y-%m-%d %H:%M:%S') - start_time),
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transaction': block['transactions']}
    return jsonify(response), 201


@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'size': len(blockchain.chain)}
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def is_valid():
    response = {'valid': blockchain.is_chain_valid(blockchain.chain)}
    return jsonify(response), 200


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    tx_keys = ['elector', 'candidate']
    if not all(key in json for key in tx_keys):
        return 'Some elements are missing', 400
    index = blockchain.add_vote(json['elector'],
                                json['candidate']
                                )
    response = {'message': f'This vote will be added to block {index}!'}
    return jsonify(response), 201


@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'Empty', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All nodes are successfully added: ',
                'all_nodes': list(blockchain.nodes)
                }
    return jsonify(response), 201


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'Chain has been replaced',
                    'new_chain': blockchain.chain
                    }
    else:
        response = {'message': 'Chain are okay. No replacement.',
                    'actual_chain': blockchain.chain
                    }
    return jsonify(response), 201


app.run(host='0.0.0.0', port=5000)
