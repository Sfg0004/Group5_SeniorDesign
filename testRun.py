# Python program to create Blockchain and upload files to IPFS

# For timestamp
import datetime

# Calculating the hash
# in order to add digital
# fingerprints to the blocks
import hashlib

# To store data
# in our blockchain w/ IPFS
import json

# Used to run IPFS
import os

# For retrieving from IPFS
import requests

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

# Display blockchain in json format
def display_chain():
	response = {'chain': blockchain.chain,
				'length': len(blockchain.chain)}

	i = 1
	for key, value in response.items():
		print(f"> {key} : {value}")
		i += 1			

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

# Uploads to IPFS
def uploadIpfs():
	fileName = input("Input the path of your file: ")
	command = f"node index.js {fileName[3:-1]} > temp_path.txt"
	print(f"{command}")
	os.system(command)
	getDatabase()
	with open ('temp_path.txt') as file:
		lines = file.readlines()
	path = lines[2]
	parsedPath = path.split('/')
	print(f"File successfully added to IPFS: {path}")
	return parsedPath[4]

# Retrieves file from IPFS
def retrieveIpfs():
	getDatabase()
	choice = '?'
	with open("database.txt", 'r') as file:
		ipfs_files = file.readlines()
	file.close()

	# index = 1
	# print("\nAvailable files: ")
	# for file in ipfs_files:
	# 	temp_file_name = file.split('$')[0]
	# 	print(f"\t{index}. {temp_file_name}")
	# 	index += 1
	# choice = input("Input your number or 'q' to quit: ")
	# if choice == 'q':
	# 	return
	# choice = int(choice)
	# while choice > len(ipfs_files) or choice < 1:
	# 	choice = input("That choice is not available. Try again: ")
	# 	if choice == 'q':
	# 		return
	# 	choice = int(choice)
	# selected_file = ipfs_files[choice - 1]
	# file_name = selected_file.split('$')[0].strip()
	# hash = selected_file.split('$')[1]

	hash = input("Input your requested hash: ")
	url = "https://ipfs.moralis.io:2053/ipfs/" + hash + "/uploaded_file"
	r = requests.get(url, allow_redirects=True)
	file_type = r.headers.get("content-type").split("/")[1]
	print(file_type)
	file_extension = ".txt"
	if file_type == "png":
		file_extension = ".png"
	elif file_type == "pdf":
		file_extension = ".pdf"
	file_name = "requested_file" + file_extension
	open(file_name, "wb").write(r.content)
	print("Finished! Your file: " + file_name + "\n")

# Get list of uploaded hashes
def getDatabase():
	hash = "QmTDb4cS6TPYxDfWwDqJHkVR1u9dAK5g9HQ1YPXwFfVNrr"
	url = "https://ipfs.moralis.io:2053/ipfs/" + hash + "/uploaded_file"
	r = requests.get(url, allow_redirects=True)
	file_extension = ".txt"
	open("database" + file_extension, "wb").write(r.content)

# Run program
def main():
	print("What would you like to do concerning your blockchain?:")
	print("[1] Mine a Block")
	print("[2] Checkout Blockchain")
	print("[3] Check Blockchain Validity")
	print("[4] Upload File to IPFS")
	print("[5] Retrieve File From IPFS")
	choice = input("Choose 1-5 or q to quit: ")

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
			uploadIpfs()
		elif choice == "5":
			retrieveIpfs()

		print("\nWhat would you like to do concerning your blockchain?:")
		print("[1] Mine a Block")
		print("[2] Checkout Blockchain")
		print("[3] Check Blockchain Validity")
		print("[4] Upload File to IPFS")
		print("[5] Retrieve File From IPFS")
		choice = input("Choose 1-5 or q to quit: ")
		print("")

if __name__ == "__main__":
	main()
