# Python program to create Blockchain

# For timestamp
import datetime

# Calculating the hash
# in order to add digital
# fingerprints to the blocks
import hashlib

# To store data
# in our blockchain w/ IPFS
import json

#Used to run IPFS
import os

class Blockchain:

	# This function is created
	# to create the very first
	# block and set its hash to "0"
	def __init__(self):
		self.chain = []
		self.create_block(proof=1, previous_hash='0')

	# This function is created
	# to add further blocks
	# into the chain
	def create_block(self, proof, previous_hash):
		block = {'index': len(self.chain) + 1,
				'timestamp': str(datetime.datetime.now()),
				'proof': proof,
				'previous_hash': previous_hash}
		self.chain.append(block)
		return block

	# This function is created
	# to display the previous block
	def print_previous_block(self):
		return self.chain[-1]

	# This is the function for proof of work
	# and used to successfully mine the block
	def proof_of_work(self, previous_proof):
		new_proof = 1
		check_proof = False

		while check_proof is False:
			hash_operation = hashlib.sha256(
				str(new_proof**2 - previous_proof**2).encode()).hexdigest()
			if hash_operation[:5] == '00000':
				check_proof = True
			else:
				new_proof += 1

		return new_proof

	#This is the function for Proof of Authentication
	#and used to mine/secure the block
	#def proof_of_auth(self, previous_proof):
	#	new_proof = 1
	#	check_proof = False

	def hash(self, block):
		encoded_block = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(encoded_block).hexdigest()

	def chain_valid(self, chain):
		previous_block = chain[0]
		block_index = 1

		while block_index < len(chain):
			block = chain[block_index]
			if block['previous_hash'] != self.hash(previous_block):
				return False

			previous_proof = previous_block['proof']
			proof = block['proof']
			hash_operation = hashlib.sha256(
				str(proof**2 - previous_proof**2).encode()).hexdigest()

			if hash_operation[:5] != '00000':
				return False
			previous_block = block
			block_index += 1

		return True

# Create the object
# of the class blockchain
blockchain = Blockchain()

# Mining a new block


def mine_block():
	previous_block = blockchain.print_previous_block()
	previous_proof = previous_block['proof']
	proof = blockchain.proof_of_work(previous_proof)
	previous_hash = blockchain.hash(previous_block)
	block = blockchain.create_block(proof, previous_hash)

	response = {'message': 'A block is MINED',
				'index': block['index'],
				'timestamp': block['timestamp'],
				'proof': block['proof'],
				'previous_hash': block['previous_hash']}

	i = 1
	for key, value in response.items():
		print(f"> {key} : {value}")
		i += 1
	#print(f"{response}\n")

# Display blockchain in json format
def display_chain():
	response = {'chain': blockchain.chain,
				'length': len(blockchain.chain)}

	i = 1
	for key, value in response.items():
		print(f"> {key} : {value}")
		i += 1			
	#print(f"{response}\n")

# Check validity of blockchain
def valid():
	valid = blockchain.chain_valid(blockchain.chain)

	if valid:
		response = {'message': 'The Blockchain is valid.'}
	else:
		response = {'message': 'The Blockchain is not valid.'}
	
	i = 1
	for key, value in response.items():
		print(f"> {key} : {value}\n")
		i += 1

	#print(f"{response}\n")
	
	# return jsonify(response), 200


#Runs IPFS program
def ipfs():
	os.system("node index.js")

# Run program
def main():
	print("What would you like to do concerning your blockchain?:")
	print("[1] Mine a Block")
	print("[2] Checkout Blockchain")
	print("[3] Check Blockchain Validity")
	print("[4] Upload File to Blockchain")
	choice = input("Choose 1-4 or q to quit: ")

	while choice != 'q':
		if choice == 'q':
			break
		elif choice == "1":
			mine_block()
		elif choice == "2":
			display_chain()
		elif choice == "3":
			valid()
		elif choice == "4":
			ipfs()

		print("\nWhat would you like to do concerning your blockchain?:")
		print("[1] Mine a Block")
		print("[2] Checkout Blockchain")
		print("[3] Check Blockchain Validity")
		print("[4] Upload File to Blockchain")
		choice = input("Choose 1-4 or q to quit: ")
		"\n"

if __name__ == "__main__":
	main()
