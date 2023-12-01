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

#Used for Proof-of-Stake
import time

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

	#function for hashing
	def hash(self, block):
		encoded_block = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(encoded_block).hexdigest()

	#function to check the blockchain's validity
	def chain_valid(self, chain):
		previous_block = chain[0]
		block_index = 1
-		
		while block_index < len(chain):
			block = chain[block_index]
			if block['previous_hash'] != self.hash(previous_block):
				return False	#the hashes do not line up so the blockchain is invalid

			previous_proof = previous_block['proof']
			proof = block['proof']
			hash_operation = hashlib.sha256(
				str(proof**2 - previous_proof**2).encode()).hexdigest()

			if hash_operation[:5] != '00000':
				return False	#if the block wasn't created correctly with consensus mechanism blockchain is invalid
			previous_block = block
			block_index += 1

		return True

# Create the object
# of the class blockchain
blockchain = Blockchain()

# Mining a new block
def mine_block():
	previous_block = blockchain.print_previous_block()
	previous_proof = previous_block['proof']	#gets previous block's proof
	proof = blockchain.proof_of_work(previous_proof)	#mines with new proof of work
	previous_hash = blockchain.hash(previous_block)		#gets previous block's hash to store
	block = blockchain.create_block(proof, previous_hash)	#creates block with all the data required

	#output for user to see that the block is mined and info about block
	response = {'message': 'A block is MINED',
				'index': block['index'],
				'timestamp': block['timestamp'],
				'proof': block['proof'],
				'previous_hash': block['previous_hash']}

	i = 1
	for key, value in response.items():	#output layout for printing the message to terminal
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
#calls to chain_valid to check
def valid():
	valid = blockchain.chain_valid(blockchain.chain)	#var holds results of chain_valid function

	if valid:
		response = {'message': 'The Blockchain is valid.'}	#outputs to user in terminal
	else:
		response = {'message': 'The Blockchain is not valid.'}	#outputs to suer in terminal
	
	i = 1
	for key, value in response.items():	#output display format
		print(f"> {key} : {value}\n")
		i += 1

	#print(f"{response}\n")
	
	# return jsonify(response), 200


#Runs IPFS program
def ipfs():
	os.system("node index.js > file.txt")	#runs the command to begin IPFS code and puts output into file for parsing later
	with open('file.txt') as file:	#reads the file
		lines = file.readlines()
	path = lines[2]
	parsedPath = path.split('/')	#splits up the file text to get only the needed section (hash)
	print(f"File successfully added to IPFS: {path}")	#lets user know the file has be successfully uploaded
	return parsedPath[4]			#retrieves hash

#function for printing the menu for the user each time
def printMenu():
	print("What would you like to do concerning your blockchain?:")
	print("[1] Mine a Block")
	print("[2] Checkout Blockchain")
	print("[3] Check Blockchain Validity")
	print("[4] Upload File to Blockchain")

# Run program
def main():
	printMenu()	#prints menu for user to select
	choice = input("Choose 1-4 or q to quit: ")	#takes user input
	print()
	while choice != 'q':
		if choice == 'q':	#quits program
			break
		elif choice == "1":
			mine_block()	#mines block
		elif choice == "2":
			display_chain()	#shows the current blockchain
		elif choice == "3":
			valid()		#checks blockchain validity
		elif choice == "4":
			hash = ipfs()	#gets file hash for later use

		print()
		printMenu()	#prints menu again
		choice = input("Choose 1-4 or q to quit: ") #takes user input
		print()

#function to run main
if __name__ == "__main__":
	main()
