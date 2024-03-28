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

class Validator:
    def __init__(self, balance, account): # account is an Account object!
        self.address = account.username
        self.balance = balance
        self.role = account.role
        self.fullLegalName = account.fullLegalName

class FileData:
    def __init__(self, ipfsHash, fileName, authorName, accessList):
        self.ipfsHash = ipfsHash
        self.fileName = fileName
        self.authorName = authorName
        self.accessList = accessList

class Account:
    def __init__(self, username, password, role, fullLegalName):
        self.username = username
        self.password = password
        self.role = role
        self.fullLegalName = fullLegalName

# Block represents each 'item' in the blockchain
class Block:
    def __init__(self, index, timestamp, prevHash, validatorName, transactionType, payload):
        self.index = index                          # block's position in the blockchain
        self.timestamp = timestamp                  # when block was created (<year>-<mh>-<dy> <hr>:<mi>:<se>.<millis>)
        self.prevHash = prevHash                    # 64-character hash of previous block (blank for genesis)
        self.validatorName = validatorName          # address of the validator (blank for genesis)
        self.hash = self.calculate_block_hash()     # hash for the block
        self.transactionType = transactionType      # either "Upload", "Download", "Create_Account", or "Genesis"
        self.payload = payload                      # ** EITHER FILEDATA OR ACCOUNT OBJECT
        
        # update this depending on how sign-in/authorization works:
        self.approved_IDs = []

    # calculateHash is a simple SHA256 hashing function
    def calculate_hash(self, s):
        h = hashlib.sha256()
        h.update(s.encode('utf-8'))
        return h.hexdigest()


    # calculateBlockHash returns the hash of all block information
    def calculate_block_hash(self):
        record = str(self.index) + self.timestamp + self.prevHash
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
ipfsHashes = []
fileNames = []

# announcements broadcasts winning validator to all nodes
# hi this is caleb. this list isn't called anywhere but idk the plan for it so
# i'm leaving it in
announcements = []

validator_lock = threading.Lock()

# validators keeps track of open validators and balances
# validators = {}
validators = []

# generate_genesis_block creates the genesis block
def generate_genesis_block():
    t = str(datetime.now())
    genesis_block = Block(0, t, "", "", "Genesis", 0)
    return genesis_block

# generate_block creates a new block using the previous block's hash
def generate_block(oldBlock, address, transactionType, payload):
    t = str(datetime.now())
    new_block = Block(oldBlock.index + 1, t, oldBlock.hash, address, transactionType, payload)
    return new_block

def generate_sample_blocks():
    t = str(datetime.now())
    address = ""
    address = calculate_hash(t)
    accessList = []
    blockchain.append(generate_block(blockchain[-1], address, "Upload", FileData("QmRB39JYBwEqfpDJ5czsBpxrBtwXswTB4HUiiyvhS1b7ii", "chest_xray.png", "Genesis", accessList)))
    blockchain.append(generate_block(blockchain[-1], address, "Upload", FileData("QmeUp1ciEQnKo9uXLi1SH3V6Z6YQHtMHRgMbzNLaHt6gJH", "Patient Info.txt", "Genesis", accessList)))
    blockchain.append(generate_block(blockchain[-1], address, "Upload", FileData("QmeuNtvAJT8HMPgzEyuHCnWiMQkpwHBtAEHmzH854TqJXW", "RADRPT 08-13-2023.pdf", "Genesis", accessList)))
    blockchain.append(generate_block(blockchain[-1], address, "Upload", FileData("QmYRJY3Uq8skTrREx7aFkE7Ym7hXA6bk5pqJE9gWrhFB6n", "Project Timeline.pdf", "Genesis", accessList)))

# user input handling for admin menu
# pass the connection and the maximum number listed for choices
def handleAdminInput(conn):
    notValid = True     # validity flag to break loop
    while notValid:
        try:
            choice = conn.recv(1024).decode('utf-8').strip()    # take user's input
            choice = int(choice) - 1                            # try to convert to int; if not int, go to exception
            if choice >= 0 and choice < 4:                      # make sure choice is in range
                notValid = False
            else:                                               # if input is out of range:
                io_write(conn, "Invalid input. Try again: ")    #   give error message
        except ValueError:                                      # if input is not an int:
            if (choice.lower() == "q"):                             #   check to see if it's "q" (specifically for main menu)
                notValid = False
                choice = 4                                      #   convert choice to 4
            else:                                               # if not q:
                io_write(conn, "Invalid input. Try again: ")    #   give error message
    return choice

# user input handling for patient and doctor menus
# pass the connection and the maximum number listed for choices
def handleGenericInput(conn):
    notValid = True     # validity flag to break loop
    while notValid:
        try:
            choice = conn.recv(1024).decode('utf-8').strip()    # take user's input
            choice = int(choice) - 1                            # try to convert to int; if not int, go to exception
            if choice >= 0 and choice < 2:                # make sure choice is in range
                notValid = False
            else:                                               # if input is out of range:
                io_write(conn, "Invalid input. Try again: ")    #   give error message
        except ValueError:                                      # if input is not an int:
            if (choice.lower() == "q"):                         #   check to see if it's "q" (specifically for main menu)
                notValid = False
                choice = 2                                      #   convert choice to 4
            else:                                               # if not q:
                io_write(conn, "Invalid input. Try again: ")    #   give error message
    return choice

# user input handling for download menu
# pass the connection and the maximum number listed for choices
def handleDownloadInput(conn, max_num):
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
            if (choice.lower() == "q") and (max_num < 5):       #   check to see if it's "q" (specifically for main menu)
                notValid = False
                choice = 4                                      #   convert choice to 4
            else:                                               # if not q:
                io_write(conn, "Invalid input. Try again: ")    #   give error message
    return choice

def handleLoginInput(conn):
    notValid = True     # validity flag to break loop
    while notValid:
        try:
            choice = conn.recv(1024).decode('utf-8').strip()    # take user's input
            choice = int(choice) - 1                            # try to convert to int; if not int, go to exception
            if choice >= 0 and choice < 1:                # make sure choice is in range
                notValid = False
            else:                                               # if input is out of range:
                io_write(conn, "Invalid input. Try again: ")    #   give error message
        except ValueError:                                      # if input is not an int:
            if (choice.lower() == "q"):                         #   check to see if it's "q" (specifically for main menu)
                notValid = False
                choice = 1                                      #   convert choice to 4
            else:                                               # if not q:
                io_write(conn, "Invalid input. Try again: ")    #   give error message
    return choice


# 
def userInput(conn, validator):
    payload = "not_determined"
    transactionType = "not_determined"

    if (validator.role == "a"):   # If validator is an admin: 
        printAdminMenu(conn)
        io_write(conn, "Input 1, 2, 3, 4, or q to log out: ")
        
        choice = handleAdminInput(conn)

        if choice == 0:
            io_write(conn, "Uploading File...\n")
            payload = uploadIpfs(conn, validator.address)
            transactionType = "Upload"
        elif choice == 1:
            io_write(conn, "Downloading File...")
            payload = retrieveIpfs(conn, validator.address)
            transactionType = "Download"
        elif choice == 2:
            io_write(conn, "Creating Account...")
            payload = createAccount(conn)
            transactionType = "Create_Account"
        elif choice == 3:
            io_write(conn, "Listing Users...")
            payload = "User list"
            getUserList(conn)
            transactionType = "List_Users"
        elif choice == 4:
            io_write(conn, "Logging Out...")
            payload = validator # might need to be validator for log out block??
            transactionType = "Log_Out"
    
    elif (validator.address == '') and (validator.balance == '') and (validator.role =='') and (validator.fullLegalName == ''):
        printLoginMenu(conn)
        io_write(conn, "Input 1 to Login or q to quit: ")
        
        choice = handleLoginInput(conn)

        payload = "not_determined" 
        if choice == 0:
            io_write(conn, "Log In: ")
            payload = ""
            transactionType = "Log_In"
        elif choice == 1:
            transaction_type = "not_determined"
            io_write(conn, "Closing connection...") 
    else:
        printGenericMenu(conn)
        io_write(conn, "Input 1, 2, or q to log out: ")
        
        choice = handleGenericInput(conn)

        payload = "not_determined"
        if choice == 0:
            io_write(conn, "Uploading File...\n")
            payload = uploadIpfs(conn, validator.address)
            transactionType = "Upload"
        elif choice == 1:
            io_write(conn, "Downloading File...")
            payload = retrieveIpfs(conn, validator.address)
            transactionType = "Download"
        elif choice == 2:
            io_write(conn, "Logging Out...")
            payload = validator
            transactionType = "Log_Out"

    return payload, transactionType


def login(conn):
    validLogin = False
    loggingIn = False
    nullAccount = Account("","","","")
	
    while validLogin != True:
        payload, loggingIn = userInput(conn, Validator("", nullAccount)) #should return transaction type as loggingIn (ie "Log_In" or "not_determined")
        if loggingIn == "not_determined":
            return nullAccount, loggingIn
            break
        elif loggingIn == "Log_In":
            io_write(conn, "\n\nEnter username: ")
            username = conn.recv(1024).decode('utf-8').strip()
            io_write(conn, "Enter password: ")
            password = conn.recv(1024).decode('utf-8').strip()
            for block in blockchain:
                if block.transactionType == "Create_Account":
                    if block.payload.username == username:
                        if block.payload.password == password:
                            validLogin = True
                            account = block.payload
                            io_write(conn, "Successful login.\n\n")
                            return account, loggingIn
            if validLogin == False:
                io_write(conn, "Bad login! Try Again.")
    


def createValidator(conn, accountObj):
    #Randomly stakes coins to prevent a favored node
    balance = randint(1,100)

	# do we need these 3 lines?
    t = str(datetime.now())
    address = ""
    address = calculate_hash(t)

    #currentAccount, transactionType = login(conn)
    newValidator = Validator(balance, accountObj)

    with validator_lock:
        validators.append(newValidator)
        for validator in validators:
            print(f"{validator.address} : {validator.balance}")             

    return newValidator

    # NEEDS TO BE PARSED (based on role)

def uploadIpfs(conn, author):
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
    ipfsHashes.append(hash)        # update the hash and file lists
    fileNames.append(fileName)

    accessList = []
    newFileData = FileData(hash, fileName, author, accessList)

    return newFileData

def retrieveIpfs(conn, author):
    i = 1
    io_write(conn, "\n\nAvailable files:\n")
    for name in fileNames:
        io_write(conn, "[" + str(i) + "] " + name + "\n")
        i += 1
    
    io_write(conn, "\n\nInput the number of your desired file: ")
    choice = handleDownloadInput(conn, len(ipfsHashes))

    hash = ipfsHashes[choice]
    url = "https://ipfs.moralis.io:2053/ipfs/" + hash + "/uploaded_file"	#does the url to retrieve the file from IPFS
    r = requests.get(url, allow_redirects=True)
    fileType = r.headers.get("content-type").split("/")[1]
    fileName = fileNames[choice]
    with open(fileName, "wb") as f:
        f.write(r.content)	#opens the file and adds content

    io_write(conn, "Finished! Your file: " + fileName + "\n")	#Lets user know retrieval was successful
    
    accessList = []
    newFileData = FileData(hash, fileName, author, accessList)

    return newFileData

def getFileList():
    for block in blockchain:
        if block.index == 0:
            continue
        if block.transactionType == "Upload":
            ipfsHashes.append(block.payload.ipfsHash)
            fileNames.append(block.payload.fileName)
    return ipfsHashes, fileNames
    
def getUserList(conn):
    userList = []
    for block in blockchain:
        if block.index == 0:
            continue
        if block.transactionType == "Create_Account":
            userList.append(block.payload.username)
            
    i = 1
    io_write(conn, "\n\nCurrent Users:\n")
    for name in userList:
        io_write(conn, "[" + str(i) + "] " + name + "\n")
        i += 1
    return

def createAccount(conn):
    io_write(conn, "\n\nEnter username: ")
    username = conn.recv(1024).decode('utf-8').strip()
    io_write(conn, "Enter password: ")
    password = conn.recv(1024).decode('utf-8').strip()
    io_write(conn, "[a] Admin\n")
    io_write(conn, "[d] Doctor\n")
    io_write(conn, "[p] Patient\n\n")
    io_write(conn, "Input a character to specify the role: ")
    role = conn.recv(1024).decode('utf-8').strip().lower()
    io_write(conn, "Enter user's legal name: ")
    name = conn.recv(1024).decode('utf-8').strip()
    io_write(conn, "Account created!")

    newAccount = Account(username, password, role, name)
    return newAccount
    
def printAdminMenu(conn):
    io_write(conn, "\n[1] Upload File\n")
    io_write(conn, "[2] Download File\n")
    io_write(conn, "[3] Create Account\n")
    io_write(conn, "[4] List Users\n")
    io_write(conn, "[q] Log Out\n")

def printGenericMenu(conn):
    io_write(conn, "\n[1] Upload File\n")
    io_write(conn, "[2] Download File\n")
    io_write(conn, "[q] Log Out\n")
    
def printLoginMenu(conn):
    io_write(conn, "\n[1] Login\n")
    io_write(conn, "[q] Quit\n")

# Make print look better!!!!
# def printValidators()

def printBlockchain():
    for block in blockchain:
        if block.transactionType == "Genesis":
            printGenesisBlock()
        else:
            print("\nIndex: " + str(block.index))
            print("Timestamp: " + block.timestamp)
            print("Previous Hash: " + block.prevHash)
            print("Validator: " + block.validatorName)
            print("Hash: " + block.hash)
            print("Type: " + block.transactionType)
            if block.transactionType == ("Upload" or "Download"):
                print("IPFS Hash: " + block.payload.ipfsHash)
                print("File Name: " + block.payload.fileName)
            elif block.transactionType == "List_Users":
                print("Status: Successful")
            elif block.transactionType == "Log_Out":
                print("Status: Successful")
            else:
                print("Username: " + block.payload.username)
                print("Password: " + block.payload.password)
                print("Role: " + block.payload.role)
        print("-----------------------------------------")

def printGenesisBlock():
    block = blockchain[0]
    print("\nIndex: " + str(block.index))
    print("Timestamp: " + block.timestamp)
    print("Type: " + block.transactionType)

# is_block_valid makes sure the block is valid by checking the index
# and comparing the hash of the previous block
def is_block_valid(newBlock, oldBlock):
    if oldBlock.index + 1 != newBlock.index:
        return False

    if oldBlock.hash != newBlock.prevHash:
        return False

    if newBlock.calculate_block_hash() != newBlock.hash:
        return False

    return True

def main_client_loop(conn):
    try:
        # address = createValidator(conn)
        # DEBUGGING STATEMENT: io_write(conn, f"\nAddress: {address}\nBalance: {validators[address]}")
        while True:
            loggedIn = False
            account, payload = login(conn)
            validator = createValidator(conn, account) 
            if payload == "Log_In":
                payload, transactionType = userInput(conn, validator)
                loggedIn = True


            while loggedIn == True:
                # if user quit:
                if transactionType == "Log_Out":
                    loggedIn = False
                    break
                else:
                #move this section up before quit and SHOULD add blocks to chain for log in/out function
                    with validator_lock:
                        old_last_index = blockchain[-1]
                    new_block = generate_block(old_last_index, validator.address, transactionType, payload)

                    if is_block_valid(new_block, old_last_index):
                        candidate_blocks.append(new_block)
                        
                    else:
                         io_write(conn, "\nNot a valid input.\n")

                payload, transactionType = userInput(conn, validator)
            
            if payload == "not_determined":
                # delete validator from dictionary of validators and close connection
                # del validators[address]
                validators.remove(validator)
                del validator
                conn.close()
                return

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
    loop_index = 0

    # get the total of all balances and amount of all validators
    for validator in validators:
        balance_total += validator.balance

    # get a random number to choose lottery winner
    rand_int = randint(0, balance_total)

    # calculate the new balances and choose winner
    for validator in weighted_validators:
        # balance = validator.balance
        new_balance = validator.balance + prev_balance
        weighted_validators[loop_index].balance = new_balance
        loop_index += 1
        # weighted_validators.update({validator : new_balance})
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
                lottery_winner = getLotteryWinner().address

                # the following block is for checking the accuracy of getLotteryWinner():
                # if i == 75:
                #     print(f"\nCurrent validator: {lottery_winner}")
                #     i = 0
                # else:
                #     i += 1

                for block in candidate_blocks:
                    if block.validatorName == lottery_winner:
                        # make sure candidate index isn't duplicated in existing blockchain (avoid forking):
                        indexes = []
                        for approved_block in blockchain:
                            indexes.append(approved_block.index)
                        if block.index in indexes:
                            new_block = generate_block(blockchain[-1], block.validatorName, block.transactionType, block.payload)
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
    # Create genesis block and admin account block
    genesis_block = generate_genesis_block()
    blockchain.append(genesis_block)

    address = ""
    blockchain.append(generate_block(blockchain[-1], address, "Create_Account", Account("admin", "admin", "a", "Admin")))
    
    # hi this is caleb. I added this function to test the downloading option.
    # comment this line out to start with a fresh blockchain
    generate_sample_blocks()

    # get lists of hashes and file names on start-up
    ipfsHashes, fileNames = getFileList()

    # Start TCP server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #this now allows for connections across computers
        ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
        print("my ip: " + ip + "\n")
        port = 5556
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
