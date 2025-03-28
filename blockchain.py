#Module 1 - Create a Blockchain


#importing libraries
import datetime
import hashlib
from flask import Flask, json

#Part 1 - Building a blockchain

#initialize the blockchain
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        #build a block
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
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
    
#Part 2 - Mining the blockchain

#Create web app with flask
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

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
    #create block 
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
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


#Running the app
app.run(host = '0.0.0.0', port = 5000)