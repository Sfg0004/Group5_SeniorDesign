#To run server: python3 posTnet.py
#To run client: nc <ip addr> <port#>


import hashlib
import json
import socket
import time
import random
import threading
import os
import requests
from random import randint
from datetime import datetime
from queue import Queue
import netifaces as ni
import traceback # for printing error exceptions

# Block represents each 'item' in the blockchain
class Block:
    def __init__(self, index, timestamp, bpm, prev_hash, validator, transaction_type, payload, file_name):
        self.index = index                          # block's position in the blockchain
        self.timestamp = timestamp                  # when block was created (<year>-<mh>-<dy> <hr>:<mi>:<se>.<millis>)
        self.bpm = bpm                              # default set to 10 for user-added blocks (0 for genesis)
        self.prev_hash = prev_hash                  # 64-character hash of previous block (blank for genesis)
        self.validator = validator                  # address of the author (blank for genesis)
        self.hash = self.calculate_block_hash()     # hash for the block
        self.transaction_type = transaction_type    # either "Upload", "Download", or "Genesis"
        self.payload = payload                      # the IPFS hash ("N/A" for genesis)
        self.file_name = file_name                  # name of uploaded/downloaded file ("no_file" for genesis)

        # update this depending on how sign-in/authorization works:
        self.approved_IDs = []

    # calculateHash is a simple SHA256 hashing function
    def calculate_hash(self, s):
        h = hashlib.sha256()
        h.update(s.encode('utf-8'))
        return h.hexdigest()


    # calculateBlockHash returns the hash of all block information
    def calculate_block_hash(self):
        record = str(self.index) + self.timestamp + str(self.bpm) + self.prev_hash
        return self.calculate_hash(record)

# Blockchain is a series of validated Blocks
blockchain = []
temp_blocks = []

#client tcp address array
nodes = []

# candidate_blocks handles incoming blocks for validation
candidate_blocks = []
candidate_blocks_lock = threading.Lock()

# keep up with all uploaded IPFS hashes and file names
ipfs_hashes = []
file_names = []

# announcements broadcasts winning validator to all nodes
# hi this is caleb. this list isn't called anywhere but idk the plan for it so
# i'm leaving it in
announcements = []

validator_lock = threading.Lock()

# validators keeps track of open validators and balances
validators = {}

# generate_genesis_block creates the genesis block
def generate_genesis_block():
    t = str(datetime.now())
    genesis_block = Block(0, t, 0, "", "", "Genesis", "N/A", "no_file")
    return genesis_block

# generate_block creates a new block using the previous block's hash
def generate_block(old_block, bpm, address, transaction_type, payload, file_name):
    t = str(datetime.now())
    new_block = Block(old_block.index + 1, t, bpm, old_block.hash, address, transaction_type, payload, file_name)
    return new_block

def generate_sample_blocks():
    t = str(datetime.now())
    address = ""
    address = calculate_hash(t)
    blockchain.append(generate_block(blockchain[-1], 0, address, "Upload", "QmRB39JYBwEqfpDJ5czsBpxrBtwXswTB4HUiiyvhS1b7ii", "chest_xray.png"))
    blockchain.append(generate_block(blockchain[-1], 0, address, "Upload", "QmeUp1ciEQnKo9uXLi1SH3V6Z6YQHtMHRgMbzNLaHt6gJH", "Patient Info.txt"))
    blockchain.append(generate_block(blockchain[-1], 0, address, "Upload", "QmeuNtvAJT8HMPgzEyuHCnWiMQkpwHBtAEHmzH854TqJXW", "RADRPT 08-13-2023.pdf"))
    blockchain.append(generate_block(blockchain[-1], 0, address, "Upload", "QmYRJY3Uq8skTrREx7aFkE7Ym7hXA6bk5pqJE9gWrhFB6n", "Project Timeline.pdf"))

# user input handling for menus (main menu and download)
# pass the connection and the maximum number listed for choices
def handle_input(conn, max_num):
    notValid = True     # validity flag to break loop
    while notValid:
        try:
            choice = conn.recv(1024).decode('utf-8').strip()    # take user's input
            choice = int(choice) - 1                            # try to convert to int; if not int, go to exception
            if choice >= 0 and choice < max_num:                # make sure choice is in range
                notValid = False
            else:                                               # if input is out of range:
                io_write(conn, "Invalid input. Try again: ")    #   give error message
        except ValueError:                                      # if input is not an int:
            if (choice.lower() == "q") and (max_num < 3):       #   check to see if it's "q" (specifically for main menu)
                notValid = False
                choice = 2                                      #   convert choice to 2
            else:                                               # if not q:
                io_write(conn, "Invalid input. Try again: ")    #   give error message
    return choice

# 
def user_input(conn):
    printMenu(conn)
    io_write(conn, "Input 1, 2, or q to quit: ")
    
    choice = handle_input(conn, 2)

    payload = "not_determined"
    transaction_type = "not_determined"
    file_name = "not_determined"
    if choice == 0:
        io_write(conn, "Uploading File...\n")
        payload, file_name = uploadIpfs(conn)
        transaction_type = "Upload"
    elif choice == 1:
        io_write(conn, "Downloading File...")
        payload, file_name = retrieveIpfs(conn)
        transaction_type = "Download"
    elif choice == 2:
        io_write(conn, "Closing connection...")
        # print("Closing connection...")

    return payload, transaction_type, file_name

def createValidator():
    #Randomly stakes coins to prevent a favored node
    balance = randint(0,100)

    t = str(datetime.now())
    address = ""
    address = calculate_hash(t)

    with validator_lock:
        validators[address] = balance
        print(validators)               

    return address

    # NEEDS TO BE PARSED (based on role)

def uploadIpfs(conn):
    io_write(conn, "Input the path of your file: ") #requests file path
    fileName = conn.recv(1024).decode('utf-8')
    command = f"node index.js {fileName[1:-3]} > temp_path.txt"	#runs the command to begin IPFS code and stores into file
    os.system(command)	#used to run command is if done in command prompt
    with open ('temp_path.txt') as file:
        lines = file.readlines()	#reads the file
    path = lines[2]
    parsedPath = path.split('/')	#splits up the file text
    fileName = fileName.split('/')[-1]
    
    hash = parsedPath[4]            # cleans up the hash and the file name
    fileName = fileName[:-3]
    ipfs_hashes.append(hash)        # update the hash and file lists
    file_names.append(fileName)

    return hash, fileName

def retrieveIpfs(conn):
    i = 1
    io_write(conn, "\n\nAvailable files:\n")
    for name in file_names:
        io_write(conn, "[" + str(i) + "] " + name + "\n")
        i += 1
    
    io_write(conn, "\n\nInput the number of your desired file: ")
    choice = handle_input(conn, len(ipfs_hashes))

    hash = ipfs_hashes[choice]
    url = "https://ipfs.moralis.io:2053/ipfs/" + hash + "/uploaded_file"	#does the url to retrieve the file from IPFS
    r = requests.get(url, allow_redirects=True)
    file_type = r.headers.get("content-type").split("/")[1]
    file_name = file_names[choice]
    open(file_name, "wb").write(r.content)	#opens the file and adds content
    io_write(conn, "Finished! Your file: " + file_name + "\n")	#Lets user know retrieval was successful
    return hash, file_name

def getFileList():
    for block in blockchain:
        if block.index == 0:
            continue
        if block.transaction_type == "Upload":
            ipfs_hashes.append(block.payload)
            file_names.append(block.file_name)
    return ipfs_hashes, file_names

def printMenu(conn):
    io_write(conn, "\n[1] Upload File\n")
    io_write(conn, "[2] Download File\n")
    io_write(conn, "[q] Quit\n")

def printBlockchain():
    for block in blockchain:
        print("\nIndex: " + str(block.index))
        print("Timestamp: " + block.timestamp)
        print("BPM: " + str(block.bpm))
        print("Previous Hash: " + block.prev_hash)
        print("Validator: " + block.validator)
        print("Hash: " + block.hash)
        print("Type: " + block.transaction_type)
        print("IPFS Hash: " + block.payload)
        print("File Name: " + block.file_name)
        print("-----------------------------------------")

# is_block_valid makes sure the block is valid by checking the index
# and comparing the hash of the previous block
def is_block_valid(new_block, old_block):
    if old_block.index + 1 != new_block.index:
        return False

    if old_block.hash != new_block.prev_hash:
        return False

    if new_block.calculate_block_hash() != new_block.hash:
        return False

    return True

def main_client_loop(conn):
    try:
        address = createValidator()
        # io_write(conn, f"\nAddress: {address}\nBalance: {validators[address]}")
        payload, transaction_type, file_name = user_input(conn)

        while True:
            # if user quit:
            if payload == "not_determined":
                # delete validator from dictionary of validators and close connection
                del validators[address]
                conn.close()
                return

            # Take in BPM from the client and add it to the blockchain after conducting necessary validation
            bpm = 10
            with validator_lock:
                old_last_index = blockchain[-1]
            new_block = generate_block(old_last_index, bpm, address, transaction_type, payload, file_name)

            if is_block_valid(new_block, old_last_index):
                candidate_blocks.append(new_block)
                
            else:
                 io_write(conn, "\nNot a valid input.\n")

            payload, transaction_type, file_name = user_input(conn)

    except Exception as q:
        #print(f"Connection closed: {q}")
        print(f"Connection closed: {traceback.format_exc()}") # for more detailed error message
        conn.close()

# calculate weighted probability for each validator
def getLotteryWinner():
    weighted_validators = validators.copy()
    balance_total = 0
    prev_balance = 0
    chosen_validator = "not_chosen"

    # get the total of all balances and amount of all validators
    for balance in validators.values():
        balance_total += balance

    # get a random number to choose lottery winner
    rand_int = randint(0, balance_total)

    # calculate the new balances and choose winner
    for validator in weighted_validators.keys():
        balance = weighted_validators[validator]
        new_balance = balance + prev_balance
        weighted_validators.update({validator : new_balance})
        prev_balance = new_balance
        if new_balance >= rand_int:
            chosen_validator = validator
            break

    return chosen_validator

# pick_winner creates a lottery pool of validators and chooses the validator who gets to forge a block to the blockchain
def pick_winner():
    print("\nPicking winner...")
    # i = 0 # for debugging
    while True:
        time.sleep(0.05) # .05 second refresh
        with validator_lock:    
            if len(validators) > 0:
                lottery_winner = getLotteryWinner()

                # the following block is for checking the accuracy of getLotteryWinner():
                # if i == 75:
                #     print(f"\nCurrent validator: {lottery_winner}")
                #     i = 0
                # else:
                #     i += 1

                for block in candidate_blocks:
                    if block.validator == lottery_winner:
                        # make sure candidate index isn't duplicated in existing blockchain (avoid forking):
                        indexes = []
                        for approved_block in blockchain:
                            indexes.append(approved_block.index)
                        if block.index in indexes:
                            new_block = generate_block(blockchain[-1], block.bpm, block.validator, block.transaction_type, block.payload, block.file_name)
                            blockchain.append(new_block)
                        else:
                            blockchain.append(block)
                        candidate_blocks.remove(block)
                        printBlockchain()
                        break

def io_write(conn, message):
    conn.sendall(message.encode('utf-8'))

def calculate_hash(s):  # Added this function
    h = hashlib.sha256()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

def main():
    # Create genesis block
    genesis_block = generate_genesis_block()
    blockchain.append(genesis_block)
    
    # hi this is caleb. I added this function to test the downloading option.
    # comment this line out to start with a fresh blockchain
    # generate_sample_blocks()

    # get lists of hashes and file names on start-up
    ipfs_hashes, file_names = getFileList()

    # Start TCP server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #this now allows for connections across computers
        ip = ni.ifaddresses('enp0s31f6')[ni.AF_INET][0]['addr']
        print("my ip: " + ip + "\n")
        port = 5555
        server.bind((ip, port))
        server.listen()
        print("Server is running.")
        run_server(server)
        
    except OSError:
        #If binding fails, assume it's a client
        print("Failed to bind, assuming client role.")
        run_client()
        
def run_server(server):
    # Handle candidate blocks in a separate thread
    candidate_thread = threading.Thread(target=lambda: candidate_blocks.append(None) if candidate_blocks else None)
    candidate_thread.start()

    # Pick winner thread
    winner_thread = threading.Thread(target=pick_winner)
    winner_thread.start()
    
    while True:
        conn, addr = server.accept()
        threading.Thread(target=main_client_loop, args=(conn,)).start()
        nodes.append(conn)
        print("conns:\n",nodes)

if __name__ == "__main__":
    main()
