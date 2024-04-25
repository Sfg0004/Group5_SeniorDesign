#change eth interface name if necessary in myIP()
# from methods import block as Block
#from methods import decentral
from methods import comm
from methods import GUI_modulated as GUI

import hashlib
import json
import socket
import signal
import time
import random
import threading
import sys
import os
import requests
from random import randint
from datetime import datetime
from queue import Queue
import netifaces as ni
import shlex  
from subprocess import Popen, PIPE, STDOUT
import ipaddress
import multiprocessing

# BLOCK.PY IMPORTS
import re
from moralis import evm_api
import base64

import errno

# COMM.PY GLOBALS
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #new socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
samaritan = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
self_samaritan = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
neighbor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
initial_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connectport = 11436
givenport = 12436

# BLOCK.PY CLASSES
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

class GivenBlock:
    def __init__(self, index, timestamp, prevHash, hash, validatorName, transactionType, payload):
        self.index = index                          # block's position in the blockchain
        self.timestamp = timestamp                  # when block was created (<year>-<mh>-<dy> <hr>:<mi>:<se>.<millis>)
        self.prevHash = prevHash                    # 64-character hash of previous block (blank for genesis)
        self.validatorName = validatorName          # address of the validator (blank for genesis)
        self.hash = hash    # hash for the block
        self.transactionType = transactionType      # either "Upload", "Download", "Create_Account", or "Genesis"
        self.payload = payload                      # ** EITHER FILEDATA OR ACCOUNT OBJECT

class Block: # Block represents each 'item' in the blockchain
    def __init__(self, index, timestamp, prevHash, validatorName, transactionType, payload):
        self.index = index                          # block's position in the blockchain
        self.timestamp = timestamp                  # when block was created (<year>-<mh>-<dy> <hr>:<mi>:<se>.<millis>)
        self.prevHash = prevHash                    # 64-character hash of previous block (blank for genesis)
        self.validatorName = validatorName          # address of the validator (blank for genesis)
        self.hash = self.calculateBlockHash()     # hash for the block
        self.transactionType = transactionType      # either "Upload", "Download", "Create_Account", or "Genesis"
        self.payload = payload                      # ** EITHER FILEDATA OR ACCOUNT OBJECT
        
        # update this depending on how sign-in/authorization works:
        self.approved_IDs = []

    def calculateHash(self, s):# calculateHash is a simple SHA256 hashing function
        h = hashlib.sha256()
        h.update(s.encode('utf-8'))
        return h.hexdigest()
    
    def calculateBlockHash(self): # calculateBlockHash returns the hash of all block information
        record = str(self.index) + self.timestamp + self.prevHash
        return self.calculateHash(record)


# BLOCK.PY GLOBALS
blockchain = [] # Blockchain is a series of validated Blocks
tempBlocks = []
ipfsHashes = [] # keep up with all uploaded IPFS hashes and file names
fileNames = []
accountNames = []
nodes = [] #client tcp address array
candidateBlocks = [] # candidateBlocks handles incoming blocks for validation
candidateBlocksLock = threading.Lock()
validatorLock = threading.Lock()
validators = [] # validators keeps track of open validators and balances
validator = Validator(0, Account("", "", "?", "")) # keep track of current validator
stopThreads = False # use flag to stop threading
# key for ipfs upload
apiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImE0NmE4MmFjLWJlYjEtNGM4MC05MjIwLTIxZDFlNGQ3MGM1NyIsIm9yZ0lkIjoiMzU5ODUyIiwidXNlcklkIjoiMzY5ODMwIiwidHlwZUlkIjoiNTY2M2MwZjAtMmM3Mi00N2YxLWJkMDktNTM1M2RmYmZhNjhhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE2OTY0NDQ5MTgsImV4cCI6NDg1MjIwNDkxOH0.kW9jP_Y_2JA70nCkUaBQMW329kQK6vuyHIfFNym0SNs"

blockchainMessage = "default_blockchain_message"

def myIP():
    return (ni.ifaddresses('enp0s31f6')[ni.AF_INET][0]['addr'])

def signal_handler(sig, frame):
    #print('You pressed Ctrl+C!')
    comm.clientOut.close()
    comm.blockFile.close()
    sys.exit(0)

def newBlockchain():
    genesisBlock = generateGenesisBlock()
    blockchain.append(genesisBlock)  
    generateSampleBlocks()
    blockchainMessage = assembleBlockchain()

    GUI.setGUIBlockchain(blockchain)

def main():
    myip = comm.myIP()

    signal.signal(signal.SIGINT, signal_handler)

    global iplist
    
    self_samaritan_to_client = Queue()
    client_to_self_samaritan = Queue()

    client_to_server = Queue()
    server_to_client = Queue()

    server_to_self_samaritan = Queue()
    self_samaritan_to_server = Queue()

    server_input_to_server = Queue()

    parent_to_child = multiprocessing.Queue()

    #message_queue.Queue()  # create a Shared queue for communication
    # initial_samaritan_jointo_ip = "146.229.163.144"#input("Enter the IP of a node in the blockchain you want to join: ")

    time.sleep(1)
    

    threading.Thread(target=run_server, args=(parent_to_child,validator,self_samaritan_to_client,client_to_self_samaritan,client_to_server,server_to_client,server_to_self_samaritan,self_samaritan_to_server,server_input_to_server,)).start()
    time.sleep(2)

    threading.Thread(target=run_client, args=(parent_to_child,self_samaritan_to_client,client_to_self_samaritan,client_to_server,server_to_client,server_to_self_samaritan,self_samaritan_to_server,server_input_to_server,)).start()

    # Handle candidate blocks in a separate thread
    # Define the lambda function
    candidateThread = threading.Thread(target=lambda: candidateBlocks.append(None) if candidateBlocks else None)
    candidateThread.start()

    """ GUI """
    GUI.root = GUI.setScenes()
    GUI.root.mainloop()

def run_client(parent_to_child,self_samaritan_to_client,client_to_self_samaritan,client_to_server,server_to_client,server_to_self_samaritan,self_samaritan_to_server,server_input_to_server):#self_samaritan_to_client,client_to_self_samaritan): #needs periodic ip requesting(checking) added
    comm.write_to_client_out("debug, in client\n")
    
    # initial_samaritan_jointo_ip = "10.4.153.165"
    # initial_samaritan_jointo_ip = "146.229.163.144"
    initial_samaritan_jointo_ip = ""
    while not GUI.hasInputtedIP:
        time.sleep(.1)
    initial_samaritan_jointo_ip = GUI.GUIgetIP()
    # print(f"The IP is: {initial_samaritan_jointo_ip}")
    # initial_samaritan_jointo_ip = "10.4.153.165"
    # print(f"Got IP: {initial_samaritan_jointo_ip}")

    # Waiting for a connection with someone. If no immediate connection, then I am the first.
    # Because I am the first, I create the blockchain.
    hasCalledCreateBlockchain = False
    while(1):
        try:
            samaritan_ip, samaritan_port = comm.requestConnection(initial_samaritan_jointo_ip, connectport, initial_client, givenport)
            comm.write_to_client_out ("server accepted my client connection. hooray!")
            client_to_server.put("call login")
            # print("Calling login")
            break
        except:
            comm.write_to_client_out("I am client. My request to connect to a server failed.")
            if (len(blockchain) == 0) and not hasCalledCreateBlockchain:
                # print("Calling create blockchain!")
                client_to_server.put("call create blockchain")
                hasCalledCreateBlockchain = True

    while(1):
        try:
            comm.write_to_client_out(f"samaritan receiveport is: {samaritan_port}")
            time.sleep(1)
            comm.requestsustainedConnection(samaritan_ip, samaritan_port, client)
            comm.write_to_client_out("sustained samaritan connection successful. hooray!")
            break
        except:
            comm.write_to_client_out("I am client. My request for sustained connection failed.")
        
        time.sleep(1.5)

        while(not server_to_client.empty()):
            receivedblock = server_to_client.get()
            blockchain.append(receivedblock)
        printBlockchain()

    try:
        while(1): #automatic close response present in receivedatafromserver            
            #NEED ADMIN BLOCK
            # print("Requesting the blockchain...")
            comm.senddatafromclient("requesting your blockchain", client)
            
            recvd_chain = comm.receivedatafromsamaritan(client)
            convertString(recvd_chain)

            # time.sleep(3) #rn iplist updates every second

            while(not server_to_client.empty()):
                receivedblock = server_to_client.get()
                blockchain.append(receivedblock)
            
            printBlockchain()
    except:
        comm.clientOut.close() 

def run_server(parent_to_child,validator,self_samaritan_to_client,client_to_self_samaritan,client_to_server,server_to_client,server_to_self_samaritan,self_samaritan_to_server,server_input_to_server):#self_samaritan_to_client, client_to_self_samaritan): #add func to talk to samaritan and samaritan to listen to server (listenServer)
    global receiveport
    global givenport
    global blockchainMessage
    global blockchain
    isValidAddress = False
    
    comm.bindasServer(connectport, server)
    comm.listenforRequests(connectport, server)
    
    time.sleep(0.5)
    try:
        while(1):
            # accept incoming connections

            # **********************************************************
            # print(f"checkpoint1")
            while(client_to_server.empty()):
                time.sleep(.5)

            # print(f"checkpoint2")

            if (not client_to_server.empty()):
                call = client_to_server.get()
                if (call == "call create blockchain"):
                    newBlockchain()
                    towrite = assembleBlockchain()
                    if len(blockchain) < 1:
                        towrite = "No blockchain here :)"
                    # else:
                        # print(f"Blockchain has {len(blockchain)} blocks")

                    # print("create blockchain called")
                    parent_to_child.put(towrite)
                    # print(f"qsize2: {parent_to_child.qsize()}")
                    # print("***** LOGIN NOW GO GO GO")

                elif (call == "call login"):
                    # print("login plz")
                    # print("Waiting for blockchain arrival...")
                    while len(blockchain) < 1:
                        time.sleep(0.25)
                    # print("Got blockchain!")
            # **********************************************************

            requester = comm.acceptconnectportConnection(server) #sit waiting/ready for new clients
            comm.receivedatafromrequester(requester)
            comm.approveConnection(requester, givenport) #I tell client what port to talk to me on
            receiveport = comm.setreceiveequal(givenport)
            givenport = comm.incgiven(givenport)
            comm.closerequesterConnection(requester)

            if(1):
                ppid = os.getpid()
                # print("Parent process1 PID:", ppid)
                child_pid = os.fork()
                #samaritan runs child, server stays parent
                if child_pid == 0:            #   This code is executed by the child process\
                    #probably need a read for block 6
                    while not isValidAddress:
                        try:
                            time.sleep(.1)

                            myip = comm.myIP()
                            self_samaritan.bind((myip, receiveport)) 
                            # print(f"receiveport is: {receiveport}")
                            
                            self_samaritan.listen(0)
                            neighbor = comm.acceptConnection(self_samaritan) #wait here for client's sustained request

                            isValidAddress = True
                        except OSError as e:
                            # print("\n*** OS error occurred:", e.strerror)
                            # print("Error code:", errno.errorcode[e.errno])
                            # print("Error arguments:", e.args)
                            pass


                    # time.sleep(0.5)

                    data = "BLOCKCHAIN"

                    while(1):
                        # time.sleep(4)
                        # print(f"qsize child IMMEDIATELY: {parent_to_child.qsize()}")                       
                        time.sleep(.15)
                        # print("listening for blk request")
                        recvd_msg = comm.receivedatafromneighbor(neighbor)
                        # print("Got a blk request!")
                        if(recvd_msg == "requesting your blockchain"):
                            # print("sending blkchn")

                            while(parent_to_child.empty()):
                                time.sleep(.1)

                            # print("Passed parent_to_child loop!")
                            blockchain2 = parent_to_child.get()

                            # print(f"sending {blockchain2}")
                            # print("*** Sending data to neighbor!")
                            comm.senddatatoneighbor(neighbor, blockchain2)
                            # print("\n\nsent")

                        #NEED ADMIN BLOCK
                        while(not server_to_self_samaritan.empty()):
                            winner = server_to_self_samaritan.get() #blocking call
                            if(winner):
                                blockchain.append(winner)

                            # print("Blockchain updated by server")
                        
                else: #SERVER
                    # time.sleep(1.5)
                    
                    inputThread = threading.Thread(target=runInput, args=(server_input_to_server,validator,))
                    inputThread.start()                    

                    while(server_input_to_server.empty()):
                        time.sleep(.15)

                    # print("\nPicking winner...")
                    while stopThreads == False:
                        time.sleep(.15) # .15 second refresh
                        with validatorLock:   
                            if len(validators) > 0:
                                lotteryWinner = getLotteryWinner().address
                                for block in candidateBlocks:
                                    isTheSameString = True
                                    letterIndex = 0
                                    for letter in validators[0].address:
                                        if letter != lotteryWinner[letterIndex]:
                                            isTheSameString = False
                                        letterIndex += 1
                                    if isTheSameString == True:
                                        # print(f"Found a validator with name: {lotteryWinner}")
                                        # make sure candidate index isn't duplicated in existing blockchain (avoid forking):
                                        indexes = []
                                        for approvedBlock in blockchain:
                                            indexes.append(approvedBlock.index)
                                        if block.index in indexes: # account for forking
                                            newBlock = generateBlock(blockchain[-1], block.validatorName, block.transactionType, block.payload)
                                            blockchain.append(newBlock)
                                            printBlockchain()
                                            GUI.setGUIBlockchain(blockchain)
                                            server_to_self_samaritan.put(newBlock)
                                        else:
                                            blockchain.append(block)
                                            printBlockchain()
                                            GUI.setGUIBlockchain(blockchain)
                                            server_to_self_samaritan.put(block)
                                            blk = assembleBlock(block)
                                            parent_to_child.put(blk)

                                        candidateBlocks.remove(block)
                                        changeFlag = True
                                        blockchainMessage = assembleBlockchain()
                                        break
                            else:
                                if GUI.isLoggedIn:
                                    # print("length of validators is 0")
                                    pass

                    comm.senddatatoneighbor(neighbor, blockchainMessage)
                    message = comm.receivedatafromneighbor(neighbor)
                    # print("server looping")
    except OSError:
        # print("it's the outer except")
        pass

def runInput(server_input_to_server, validator):
    # print(f"Running runInput...")
    while True:
        while not GUI.isLoggedIn:
            time.sleep(0.15)
            if len(validators) > 0:
                validators.remove(validator)

        account = GUI.getGUIAccount()
        isAccountFound = False
        for _validator in validators:
            if account.username == _validator.address:
                isAccountFound = True
        if not isAccountFound:
            validator = createValidator(account)
            GUI.setGUIValidator(validator)
            # print("Validator created.")

        GUICandidateBlocks = GUI.getGUICandidateBlocks()
        if len(GUICandidateBlocks) > 0:
            proposedBlock = GUICandidateBlocks[0]
            payload = proposedBlock.payload
            if proposedBlock.transactionType == "Upload":
                candidateBlock = addToCandidateBlocks("Upload", payload, validator)
                server_input_to_server.put(candidateBlock)
            elif proposedBlock.transactionType == "Download":
                candidateBlock = addToCandidateBlocks("Download", payload, validator)
                server_input_to_server.put(candidateBlock)
            elif proposedBlock.transactionType == "Create_Account":
                candidateBlock = addToCandidateBlocks("Create_Account", payload, validator)
                server_input_to_server.put(candidateBlock)
            GUI.removeCandidateBlock(proposedBlock)
        time.sleep(0.1)

#
#
# BLOCK.PY FUNCTIONS
#
#
def calculateHash(s):  #separate function for hashing
    h = hashlib.sha256()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

def isBlockValid(newBlock, oldBlock):
    if oldBlock.index + 1 != newBlock.index:
        return False

    if oldBlock.hash != newBlock.prevHash:
        return False

    if newBlock.calculateBlockHash() != newBlock.hash:
        return False

    return True

def generateGenesisBlock(): # generate_genesis_block creates the genesis block
    t = str(datetime.now())
    # genesisBlock = Block(0, t, "", "", "Genesis", 0)
    genesisBlock = Block(0, t, "", "admin", "Create_Account", Account("admin", "admin", "a", "Admin"))
    return genesisBlock

def generateBlock(oldBlock, address, transactionType, payload): # generate_block creates a new block using the previous block's hash
    t = str(datetime.now())
    new_block = Block(oldBlock.index + 1, t, oldBlock.hash, address, transactionType, payload)
    return new_block

def generateSampleBlocks():
    t = str(datetime.now())

    address = "admin"
    accessList = []
    blockchain.append(generateBlock(blockchain[-1], address, "Upload", FileData("QmRB39JYBwEqfpDJ5czsBpxrBtwXswTB4HUiiyvhS1b7ii", "chest_xray.png", "Genesis", accessList)))
    blockchain.append(generateBlock(blockchain[-1], address, "Upload", FileData("QmeUp1ciEQnKo9uXLi1SH3V6Z6YQHtMHRgMbzNLaHt6gJH", "Patient Info.txt", "Genesis", accessList)))
    blockchain.append(generateBlock(blockchain[-1], address, "Upload", FileData("QmeuNtvAJT8HMPgzEyuHCnWiMQkpwHBtAEHmzH854TqJXW", "RADRPT 08-13-2023.pdf", "Genesis", accessList)))
    blockchain.append(generateBlock(blockchain[-1], address, "Upload", FileData("QmYRJY3Uq8skTrREx7aFkE7Ym7hXA6bk5pqJE9gWrhFB6n", "Project Timeline.pdf", "Genesis", accessList)))
    blockchain.append(generateBlock(blockchain[-1], address, "Create_Account", Account("d", "d", "d", "Dr. Doctor")))

def createFirstBlocks():
    genesisBlock = generateGenesisBlock()
    blockchain.append(genesisBlock)
    address = ""
    # blockchain.append(generateBlock(blockchain[-1], address, "Create_Account", Account("admin", "admin", "a", "Admin")))
    # generateSampleBlocks()

def printBlockchain(): #makes the blockchain print better!
    with open('blockchainLog.txt', 'w') as file:
        file.write(f"\nPROCESS ID: {os.getpid()}\n")
        for block in blockchain:
            file.write(f"\nIndex: {block.index}\n")
            file.write(f"Timestamp: {block.timestamp}\n")
            file.write(f"Previous_Hash: {block.prevHash}\n")
            file.write(f"Validator: {block.validatorName}\n")
            file.write(f"Hash: {block.hash}\n")
            file.write(f"Type: {block.transactionType}\n")
            if block.transactionType != "Create_Account":
                file.write(f"IPFS_Hash: {block.payload.ipfsHash}\n")
                file.write(f"File_Name: {block.payload.fileName}\n")
            else:
                file.write(f"Username: {block.payload.username}\n")
                file.write(f"Password: {block.payload.password}\n")
                file.write(f"Role: {block.payload.role}\n")
            file.write("-----------------------------------------\n")
    
# def printGenesisBlock(): #prints the genesis block better
#     block = blockchain[0]
#     # print("\nIndex: " + str(block.index))
#     # print("Timestamp: " + block.timestamp)
#     # print("Type: " + block.transactionType)

def assembleBlockchain(): #assembles blockchain to be sent to requesting neighbor
    message = ""
    for block in blockchain:
        if block.transactionType == "Genesis":
            genesis = expandGenesisBlock()
            message = message + genesis
        else:
            standardBlock = expandStandardblock(block)
            message = message + standardBlock
            if block.transactionType != "Create_Account":
                hash = "IPFS_Hash: " + block.payload.ipfsHash
                filename = "File_Name: " + block.payload.fileName
                type = "Type: " + block.transactionType
                upload = "\n" + hash + "\n" + filename + "\n" + type
                message = message + upload
            else:
                credentialBlock = expandCredentials(block)
                message = message + credentialBlock
    return message    

def assembleBlock(block): #assembles block to be sent to requesting neighbor
    message = ""
    if block.transactionType == "Genesis":
        genesis = expandGenesisBlock()
        message = message + genesis
    else:
        standardBlock = expandStandardblock(block)
        message = message + standardBlock
        if block.transactionType != "Create_Account":
            hash = "IPFS_Hash: " + block.payload.ipfsHash
            filename = "File_Name: " + block.payload.fileName
            type = "Type: " + block.transactionType
            upload = "\n" + hash + "\n" + filename + "\n" + type
            message = message + upload
        else:
            credentialBlock = expandCredentials(block)
            message = message + credentialBlock
    return message    

def expandGenesisBlock(): #assembles genesis block to be sent to requesting neighbor
    block = blockchain[0]
    index = "Index: " + str(block.index)
    time = "Timestamp: " + block.timestamp
    type = "Type: " + block.transactionType
    genesis = "\n" + index + "\n" + time + "\n"+ type
    return genesis       

def expandStandardblock(block): #assembles standard block to be sent to requesting neighbor
    index = "Index: " + str(block.index)
    time = "Timestamp: " + block.timestamp
    #type = "Type: " + block.transactionType
    prevHash = "Previous_Hash: " + block.prevHash
    hash = "Hash: " + block.hash
    validator = "Validator: " + block.validatorName
    message1 = "\n" + index + "\n" + time + "\n" + prevHash + "\n" + hash + "\n" + validator
    return message1

def expandCredentials(block): #assembles user credential block to be sent to requesting neighbor
    # print("bruh")
    username = "Username: " + block.payload.username
    password = "Password: " + block.payload.password
    role = "Role: " + block.payload.role
    type = "Type: " + block.transactionType
    message3 = "\n" + username + "\n" + password + "\n" + role + "\n" + type
    return message3

def convertString(currentBlockchain):
    blockDictionary = {}
    delimiters = ["\n"]
    for delimiter in delimiters:
        currentBlockchain = " ".join(currentBlockchain.split(delimiter))
    result = currentBlockchain.split()
    #print(result)
    i = 0
    blockDictionary["Previous_Hash"] = "Default"
    blockDictionary["Validator"] = "Default"
    blockDictionary["Hash"] = "hash"
    accessList = []
    for item in result:
        if item == "Index:":
            blockDictionary["Index"] = result[i + 1]
        elif item == "Timestamp:":
            blockDictionary["Timestamp"] = result[i + 1]+ " " + result[i+2]
        elif item == "Previous_Hash:":
            blockDictionary["Previous_Hash"] = result[i + 1]
        elif item == "Hash:":
            blockDictionary["Hash"] = result[i + 1]
        elif item == "Validator:":
            blockDictionary["Validator"] = result[i + 1]
        elif item == "IPFS_Hash:":
            blockDictionary["IPFS_Hash"] = result[i + 1]
        elif item == "File_Name:":
            blockDictionary["File_Name"] = result[i + 1]
        elif item == "Username:":
            blockDictionary["Username"] = result[i + 1]
        elif item == "Password:":
            blockDictionary["Password"] = result[i + 1]
        elif item == "Role:":
            blockDictionary["Role"] = result[i + 1]
        elif item == "Type:":
            blockDictionary["Type"] = result[i + 1]
            if blockDictionary['Type'] == 'Create_Account':
                # print("I made it to account")
                username = blockDictionary['Username']
                password = blockDictionary['Password']
                role = blockDictionary['Role']
                fullLegalName = "admin"
                payload = Account(username, password, role, fullLegalName)
            elif (blockDictionary['Type'] == 'Upload') or (blockDictionary['Type'] == 'Download'):
                # print("I made it to upload/download")
                ipfsHash = blockDictionary['IPFS_Hash']
                fileName = blockDictionary['File_Name']
                validator = blockDictionary['Validator']
                payload = FileData(ipfsHash, fileName, validator, accessList)
            else:
                # print(f"block type is: {blockDictionary['Type']}")
                payload = FileData("", "", "", accessList)
            index = int(blockDictionary['Index'])
            timestamp = blockDictionary['Timestamp']
            prevHash = blockDictionary['Previous_Hash']
            hash = blockDictionary['Hash']
            validatorName = blockDictionary['Validator']
            transactionType = blockDictionary['Type']
            newBlock = GivenBlock(index, timestamp, prevHash, hash, validatorName, transactionType, payload)
            blockchain.append(newBlock)

        i += 1
    GUI.setGUIBlockchain(blockchain)
    return result

def createValidator(currentAccount):
    #Randomly stakes coins to prevent a favored node
    balance = randint(1,100)

    newValidator = Validator(balance, currentAccount)

    with validatorLock:
        validators.append(newValidator)
        for validator in validators:
            # print(f"{validator.address} : {validator.balance}")  
            pass           

    return newValidator

def createAccount(username, password, name, roleSelection): # , root
    # print("role is " + roleSelection)
    if roleSelection == "Admin":
        role = "a"
    elif roleSelection == "Doctor":
        role = "d"
    else:
        role = "p"
    newAccount = Account(username, password, role, name)
    # addToCandidateBlocks("Create_Account", newAccount)
    # print(f"Created account for: {newAccount.fullLegalName}")

    # root.children["createAccountMenu"].children["statusLabel"].configure(text=f"{newAccount.fullLegalName}'s account successfully created!")

    return newAccount

def addToCandidateBlocks(transactionType, payload, validator):
    with validatorLock:
        oldLastIndex = blockchain[-1]
    newBlock = generateBlock(oldLastIndex, validator.address, transactionType, payload)

    if isBlockValid(newBlock, oldLastIndex):
        candidateBlocks.append(newBlock)
    
    return newBlock

    #sendtoneighbor(newBlock)

# calculate weighted probability for each validator
def getLotteryWinner():
    weightedValidators = validators.copy()
    balanceTotal = 0
    prevBalance = 0
    chosenValidator = "not_chosen"
    loopIndex = 0

    # get the total of all balances and amount of all validators
    for validator in validators:
        balanceTotal += validator.balance

    # get a random number to choose lottery winner
    randInt = randint(0, balanceTotal)

    # calculate the new balances and choose winner
    for validator in weightedValidators:
        # balance = validator.balance
        newBalance = validator.balance + prevBalance
        weightedValidators[loopIndex].balance = newBalance
        loopIndex += 1
        # weighted_validators.update({validator : new_balance})
        prevBalance = newBalance
        if newBalance >= randInt:
            chosenValidator = validator
            break

    return chosenValidator

def getBlockchain():
    # print(f"*getBlockchain* Last block index: {blockchain[-1].index}")
    return blockchain


if __name__ == "__main__":
    main()



