#Module 2 - Create Cryptocurrency


#importing libraries
import datetime
import hashlib
from flask import Flask, json, request, jsonify
import requests
from uuid import uuid4 
from urllib.parse import urlparse

###############################################################################
#Part 1 - Building a blockchain

#initialize the blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        #transactions must be created before the block
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        #initialize nodes as an empty set. Not list because they shouldn't have
        #a certain order. Also better for computational purposes
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):
        #build a block
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        #empty transactions list so there won't be same transaction in 2 different blocks
        self.transactions = []
        #append block to the chain
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            #attempt to solve for check_proof
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            #check if there are 4 leading zeros
            if hash_operation [:4] == '0000':
                check_proof = True
            else: 
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block).encode()
        #hash the block
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            #iterate through chain
            block = chain[block_index]
            #check hash of previous block matches a hashing of that block
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            #check if first 4 digits are zeros
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index +=1
        return True
    
    def add_transaction(self, sender, receiver, amount):\
        #define format of a transaction
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_previous_block()
        #+1 is because transactions will go in the next block
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        #parses out the url and port to add to nodes. ie 127.0.0.1:5000
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        #get set of nodes
        network = self.nodes
        #initialize variables
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            #each node uses a different port. Why this way? I don't know...
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
            #if longest chain is not None
            if longest_chain:
                self.chain = longest_chain
                return True
            return False
            
    
###############################################################################
#Part 2 - Mining the blockchain

#Create web app with flask
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

#create address for the node on port 5000
node_address = str(uuid4()).replace('-','')

#creating a blockchain
blockchain = Blockchain()

#mining a new block
#calling url to mine a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    #get previous block
    previous_block = blockchain.get_previous_block()
    #get proof of previous block
    previous_proof = previous_block['proof']
    #get new proof
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    #add transactions
    blockchain.add_transaction(sender = node_address, receiver = 'c', amount = 1)
    #create block 
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return json.dumps(response), 200
    
#Getting the full blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return json.dumps(response), 200

#Check if blockchain is valid
@app.route('/is_chain_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:   
        response = {'message': 'The blockchain is valid.'}
    else:
        response = {'message': 'The blockchain is NOT valid.'}
    return json.dumps(response), 200

#adding a new transaction to the blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transactin are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return json(response), 201
    
###############################################################################
#Part 3 - Decentralize Blockchain

#Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connecte_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'messsage': 'All the nodes are now connected. The CCoin Blockchain now contains the following nodes: ',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

#Replacing the chain by the longest chain if needed.
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:   
        response = {'message': 'The node had different chains. The chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'The chain was not replaced. The chain is the longest one',
                    'actual_chain': blockchain.chain}
    return json.dumps(response), 200


###############################################################################
#Running the app
app.run(host = '0.0.0.0', port = 5003)