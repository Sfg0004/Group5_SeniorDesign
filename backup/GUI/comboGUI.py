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

lightweight1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
lightweight2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
lwserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

neighbor_nodes = []
initial_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connectport = 11453
givenport = 12453
LWport = 13453

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
    server.close()
    self_samaritan.close()
    lwserver.close()
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
    test = open('logs/test.txt', 'w')
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

    lw_to_full = multiprocessing.Queue()

    parent_to_child = multiprocessing.Queue()
    child_to_parent = multiprocessing.Queue()
    new_client_for_samaritan = multiprocessing.Queue()

    time.sleep(0.5)
    

    threading.Thread(target=run_server, args=(lw_to_full,child_to_parent,parent_to_child,validator,new_client_for_samaritan,self_samaritan_to_client,client_to_self_samaritan,client_to_server,server_to_client,server_to_self_samaritan,self_samaritan_to_server,server_input_to_server,)).start()
    time.sleep(1)

    threading.Thread(target=run_client, args=(child_to_parent,parent_to_child,new_client_for_samaritan,self_samaritan_to_client,client_to_self_samaritan,client_to_server,server_to_client,server_to_self_samaritan,self_samaritan_to_server,server_input_to_server,)).start()

    # Handle candidate blocks in a separate thread
    # Define the lambda function
    candidateThread = threading.Thread(target=lambda: candidateBlocks.append(None) if candidateBlocks else None)
    candidateThread.start()

    """ GUI """
    GUI.root = GUI.setScenes()
    GUI.root.mainloop()

def run_client(child_to_parent,parent_to_child,new_client_for_samaritan,self_samaritan_to_client,client_to_self_samaritan,client_to_server,server_to_client,server_to_self_samaritan,self_samaritan_to_server,server_input_to_server):#self_samaritan_to_client,client_to_self_samaritan): #needs periodic ip requesting(checking) added
    comm.write_to_client_out("debug, in client\n")
    initial_samaritan_jointo_ip = ""
    while not GUI.hasInputtedIP:
        time.sleep(.1)
    initial_samaritan_jointo_ip = GUI.GUIgetIP()
    print(f"The IP is: {initial_samaritan_jointo_ip}")
    # initial_samaritan_jointo_ip = "10.4.153.165"
    print(f"Got IP: {initial_samaritan_jointo_ip}")

    # Waiting for a connection with someone. If no immediate connection, then I am the first.
    # Because I am the first, I create the blockchain.
    hasCalledCreateBlockchain = False
    while(1):
        try:
            samaritan_ip, samaritan_port = comm.requestConnection(initial_samaritan_jointo_ip, connectport, initial_client, givenport)
            comm.write_to_client_out ("server accepted my client connection. hooray!")
            client_to_server.put("call login")
            print("Calling login")
            break
        except:
            comm.write_to_client_out("I am client. My request to connect to a server failed.")
            if (len(blockchain) == 0) and not hasCalledCreateBlockchain:
                print("Calling create blockchain!")
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
            print("THIS IS THE FIRST RECIEVED BLOCK:", receivedblock)
            client_to_self_samaritan.put("new blockchain:")
            client_to_self_samaritan.put(receivedblock)
            #blockchain.append(receivedblock)
        #printBlockchain()

    try:
        while(1): #automatic close response present in receivedatafromserver            
            #NEED ADMIN BLOCK

            print("Requesting the blockchain...")
            comm.senddatafromclient("requesting your blockchain", client)
            
            recvd_chain = comm.receivedatafromsamaritan(client)
            workwith = recvd_chain

            p_split = workwith.split("Index:")
            temp = p_split[-1]
            temp2 = temp.split("\n")
            
            ind = temp2[0]
            rest = temp[1]


            #print("current index:", ind)
            #print("blckchn length:", len(blockchain))

            while rest.find("Index:")!= -1:
                p_split = rest.split("Index:")
                temp = p_split[-1]
                temp2 = temp.split("\n")
                
                ind = temp2[0]
                rest = temp[1]

            recvdlen = int(ind) + 1

            #print("current index:", ind)
            #print("blckchn length:", len(blockchain))
            if(recvdlen > len(blockchain)):
                print("abc")
                convertString(recvd_chain)
                client_to_server.put("new block update:")
                client_to_server.put(recvd_chain)
                print("converted string")

            while(not server_to_client.empty()):
                receivedblock = server_to_client.get()
                print("THIS IS THE RECIEVED BLOCK:", receivedblock)
                client_to_self_samaritan.put("new blockchain:")
                client_to_self_samaritan.put(receivedblock)
            
            #printBlockchain()
    except:
        comm.clientOut.close() 

def run_server(lw_to_full,child_to_parent,parent_to_child,validator,new_client_for_samaritan,self_samaritan_to_client,client_to_self_samaritan,client_to_server,server_to_client,server_to_self_samaritan,self_samaritan_to_server,server_input_to_server):#self_samaritan_to_client, client_to_self_samaritan): #add func to talk to samaritan and samaritan to listen to server (listenServer)
    global receiveport
    global givenport
    global blockchainMessage
    global blockchain
    isValidAddress = False
    
    comm.bindasServer(connectport, server)
    comm.listenforRequests(connectport, server)
    blockchain2 = ""
    
    time.sleep(0.5)
    try:
        while(1):
            # accept incoming connections

            # **********************************************************
            while(client_to_server.empty()):
                time.sleep(.5)

            if (not client_to_server.empty()):
                call = client_to_server.get()
                if (call == "call create blockchain"):
                    newBlockchain()
                    towrite = assembleBlockchain()
                    if len(blockchain) < 1:
                        towrite = "No blockchain here :)"
                    else:
                        print(f"Blockchain has {len(blockchain)} blocks")

                    print("create blockchain called")
                    parent_to_child.put(towrite)
                    print("***** LOGIN NOW GO GO GO")

                elif (call == "call login"):
                    print("login plz")
                    print("Waiting for blockchain arrival...")
                    while len(blockchain) < 1:
                        time.sleep(0.25)
                    print("Got blockchain!")

                elif (call == "new blockchain update:"):
                    call = client_to_server.get()
                    convertString(call)
            # **********************************************************

            threading.Thread(target=run_LW, args=(lw_to_full,validator,)).start()

            #moved these here so can add blocks before any connections occur
            inputThread = threading.Thread(target=runInput, args=(server_input_to_server,validator,))
            inputThread.start()                    

            winnerThread = threading.Thread(target=pickWinner, args=(server_to_client,server_to_self_samaritan, parent_to_child,))
            winnerThread.start()

            requester = comm.acceptconnectportConnection(server) #sit waiting/ready for new clients
            comm.receivedatafromrequester(requester)
            comm.approveConnection(requester, givenport) #I tell client what port to talk to me on
            receiveport = comm.setreceiveequal(givenport)
            comm.closerequesterConnection(requester)

            if(1):
                ppid = os.getpid()
                print("Parent process1 PID:", ppid)
                child_pid = os.fork()
                #samaritan runs child, server stays parent
                if child_pid == 0:            #   This code is executed by the child process\
                    while not isValidAddress:
                        try:
                            time.sleep(.1)

                            myip = comm.myIP()
                            self_samaritan.bind((myip, receiveport)) 
                            print(f"receiveport is: {receiveport}")
                            
                            self_samaritan.listen(0)
                            neighbor = comm.acceptConnection(self_samaritan) #wait here for client's sustained request
                            neighbor_nodes.append(neighbor)

                            isValidAddress = True
                        except OSError as e:
                            print("\n*** OS error occurred:", e.strerror)
                            print("Error code:", errno.errorcode[e.errno])
                            print("Error arguments:", e.args)
                            pass

                    while(1):                      
                        time.sleep(.15)
                        if not new_client_for_samaritan.empty():
                            new_neighbor = new_client_for_samaritan.get()
                            neighbor_nodes.append(new_neighbor)
                            print("Appended neighbor: ", neighbor_nodes)
                        if(not parent_to_child.empty()):
                            blockchain2 = parent_to_child.get()

                        if(not child_to_parent.empty()):
                            blockchain2 = child_to_parent.get()

                        if(not client_to_self_samaritan.empty()):
                            call = client_to_self_samaritan.get()
                            if(call == "new blockchain:"):
                                call = client_to_self_samaritan.get()
                                convertString(call)

                        for n in neighbor_nodes:
                                time.sleep(.5)
                                
                                #print(f"sending {blockchain2}")
                                print("*** Sending data to neighbor!")
                                comm.senddatatoneighbor(n, blockchain2)
                                print("\n\nsent")

                        #NEED ADMIN BLOCK
                        while(not server_to_self_samaritan.empty()):
                            winner = server_to_self_samaritan.get() #blocking call
                            if(winner):
                                blockchain.append(winner)

                            print("Blockchain updated by server")
                        
                else: #SERVER

                    #check
                    if(not lw_to_full.empty()):
                        lwBlk = lw_to_full.get()
                        blockchain.append(lwBlk)

                    while(1):
                        time.sleep(1)

    except OSError:
        print("it's the outer except")
        pass

def pickWinner(server_to_client,server_to_self_samaritan, parent_to_child):
    print("\nPicking winner...")
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
                        print(f"Found a validator with name: {lotteryWinner}")
                        # make sure candidate index isn't duplicated in existing blockchain (avoid forking):
                        indexes = []
                        for approvedBlock in blockchain:
                            indexes.append(approvedBlock.index)
                        if block.index in indexes: # account for forking
                            newBlock = generateBlock(blockchain[-1], block.validatorName, block.transactionType, block.payload)
                            blockchain.append(newBlock)
                            newBlockTxt = assembleBlock(newBlock)
                            # printBlockchain()
                            GUI.setGUIBlockchain(blockchain)
                            server_to_self_samaritan.put(newBlockTxt)
                            server_to_client.put(newBlockTxt)
                        else:
                            blockchain.append(block)
                            blockTxt = assembleBlock(block)
                            #printBlockchain()
                            GUI.setGUIBlockchain(blockchain)
                            server_to_self_samaritan.put(blockTxt)
                            server_to_client.put(blockTxt)

                            blk = assembleBlock(block)
                            parent_to_child.put(blk)

                        candidateBlocks.remove(block)
                        changeFlag = True
                        blockchainMessage = assembleBlockchain()
                        break
            else:
                if GUI.isLoggedIn:
                    print("length of validators is 0")
                    pass

def run_LW(lw_to_full, validator):

    # WIP WILL NEED TO TEST THE ACTUAL GENERATION AND ADDING OF THE NEW BLOCK. DATA WAS RECEIVED
    # FROM THE LW DEVICE BUT WILL REQUIRE FORMMATTING FOR ACCESS LIST (UPLOAD)
    # AND POTENTIALLY OTHER STUFF. MAY ALSO NEED TO PASS IN QUEUE/SOMETHING
    # BC WE ARE TOO TIRED TO FIGURE OUT WHO IS ACTUALLY RECEIVING AND PRINTING THIS INFORMATION 
    # IN THE TERMINAL

    
    comm.bindasServer(LWport, lwserver)
    #lightweight1.bind((myip, LWport)) 
    while(1):
        connected = False
        myip = myIP()
        comm.listenforLWRequests(LWport,lwserver)
        lw1 = comm.acceptconnectportConnection(lwserver) #sit waiting/ready for new clients
        connected = True
        lwMsg = comm.receivedatafromrequester(lw1)
        while(connected):
            if(lwMsg == "Get_Blockchain"):
                sendBlckchn = assembleBlockchain()
                #comm.senddatatorequester(lw1,'1')
                comm.senddatatorequester(lw1,sendBlckchn)
                print("sent message")
                lwMsg = " "
                lw1.close()
                connected = False

            elif(lwMsg == "Upload_File"):
                rcv = comm.receivedatafromrequester(lw1)
                divided = rcv.split(' ')
                print(divided)
                localHash = divided[1]
                localFileName = divided[2]
                localAuthor = divided[3]
                localAccessList = divided[4]
                newBlockToAdd = FileData(localHash, localFileName, localAuthor, localAccessList)
                transactionType = "Upload"

                newblk = addToCandidateBlocks(transactionType, newBlockToAdd, validator)
                lwMsg = " "
                lw1.close()
                #blockchain.append(newblk)

                #OORRRRR MAYBE
                #lw_to_full.put(newblk)



                connected = False

            elif(lwMsg == "Download_File"):
                rcv = comm.receivedatafromrequester(lw1)
                divided = rcv.split(' ')
                print(divided)
                localHash = divided[2]
                localFileName = divided[3]
                localAuthor = divided[1]
                #localAccessList = divided[4]
                newBlockToAdd = FileData(localHash, localFileName, localAuthor, localAccessList)
                transactionType = "Download"
                newblk = addToCandidateBlocks(transactionType, newBlockToAdd, validator)
                #newblk = generateBlock(blockchain[-1], "default addr", transactionType, newBlockToAdd)
                lwMsg = " "
                lw1.close()
                #blockchain.append(newblk)
                connected = False

            elif(lwMsg == "Create_User"):
                rcv = comm.receivedatafromrequester(lw1)
                divided = rcv.split(' ')
                print(divided)
                localUsername = divided[2]
                localPassword = divided[3]
                localRole = divided[1]
                localLegalName = divided[5]
                newBlockToAdd = Account(localUsername, localPassword, localRole, localLegalName)
                transactionType = "Create_Account"
                newblk = addToCandidateBlocks(transactionType, newBlockToAdd, validator)
                #newblk = generateBlock(blockchain[-1], "default", transactionType, newBlockToAdd)
                lwMsg = " "
                lw1.close()
                #blockchain.append(newblk)
                connected = False

            time.sleep(0.2)

def runInput(server_input_to_server, validator):
    print(f"Running runInput...")
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
            print("Validator created.")

        GUICandidateBlocks = GUI.getGUICandidateBlocks()
        #print("\nOMG HI IM RIGHT HERE 1\n")
        if len(GUICandidateBlocks) > 0:
            #print("\nOMG HI IM RIGHT HERE 2\n")
            proposedBlock = GUICandidateBlocks[0]
            #print("\nOMG HI IM RIGHT HERE 3\n")
            payload = proposedBlock.payload
            if proposedBlock.transactionType == "Upload":
                candidateBlock = addToCandidateBlocks("Upload", payload, validator)
            elif proposedBlock.transactionType == "Download":
                candidateBlock = addToCandidateBlocks("Download", payload, validator)
            elif proposedBlock.transactionType == "Create_Account":
                candidateBlock = addToCandidateBlocks("Create_Account", payload, validator)
            elif proposedBlock.transactionType == "Update_User":
                #print("\nOMG HI IM RIGHT HERE 4\n")
                candidateBlock = addToCandidateBlocks("Update_User", payload, validator)
                #print("\nOMG HI IM RIGHT HERE 5\n")
            GUI.removeCandidateBlock(proposedBlock)
            #print("\nOMG HI IM RIGHT HERE 6\n")
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
    genesisBlock = Block(0, t, "", "admin", "Create_Account", Account("admin", "admin", "a", "Admin"))
    return genesisBlock

def generateBlock(oldBlock, address, transactionType, payload): # generate_block creates a new block using the previous block's hash
    t = str(datetime.now())
    new_block = Block(oldBlock.index + 1, t, oldBlock.hash, address, transactionType, payload)
    return new_block

def generateSampleBlocks():
    t = str(datetime.now())

    address = "admin"
    accessList = ""
    blockchain.append(generateBlock(blockchain[-1], address, "Create_Account", Account("doctor", "batman", "d", "Dr. Doctor")))

def createFirstBlocks():
    genesisBlock = generateGenesisBlock()
    blockchain.append(genesisBlock)
    address = ""

def printBlockchain(): #makes the blockchain print better!
    with open('logs/blockchainLog.txt', 'w') as file:
        file.write(f"\nPROCESS ID: {os.getpid()}\n")
        for block in blockchain:
            file.write(f"\nIndex: {block.index}\n")
            file.write(f"Timestamp: {block.timestamp}\n")
            file.write(f"Previous_Hash: {block.prevHash}\n")
            file.write(f"Validator: {block.validatorName}\n")
            file.write(f"Hash: {block.hash}\n")
            file.write(f"Type: {block.transactionType}\n")
            if (block.transactionType == "Upload") or (block.transactionType == "Download"):
                file.write(f"IPFS_Hash: {block.payload.ipfsHash}\n")
                file.write(f"File_Name: {block.payload.fileName}\n")
                # file.write(f"Access_List: {block.payload.accessList}\n")
            else:
                file.write(f"Username: {block.payload.username}\n")
                file.write(f"Password: {block.payload.password}\n")
                file.write(f"Role: {block.payload.role}\n")
            file.write("-----------------------------------------\n")

def assembleBlockchain(): #assembles blockchain to be sent to requesting neighbor
    message = ""
    for block in blockchain:
        if block.transactionType == "Genesis":
            genesis = expandGenesisBlock()
            message = message + genesis
        else:
            standardBlock = expandStandardblock(block)
            message = message + standardBlock
            if (block.transactionType == "Upload") or (block.transactionType == "Download"):
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
        if (block.transactionType == "Upload") or (block.transactionType == "Download"):
            hash = "IPFS_Hash: " + block.payload.ipfsHash
            filename = "File_Name: " + block.payload.fileName
            accessList = "Access_List: " + block.payload.accessList
            type = "Type: " + block.transactionType
            upload = "\n" + hash + "\n" + filename + "\n" + accessList + "\n" + type
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
    prevHash = "Previous_Hash: " + block.prevHash
    hash = "Hash: " + block.hash
    validator = "Validator: " + block.validatorName
    message1 = "\n" + index + "\n" + time + "\n" + prevHash + "\n" + hash + "\n" + validator
    return message1

def expandCredentials(block): #assembles user credential block to be sent to requesting neighbor
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
    i = 0
    blockDictionary["Previous_Hash"] = "Default"
    blockDictionary["Validator"] = "Default"
    blockDictionary["Hash"] = "hash"
    accessList = "" #deleted but may need to declare as empty string
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
        elif item == "Access_List:":
            blockDictionary["Access_List"] = result[i + 1]
        elif item == "Username:":
            blockDictionary["Username"] = result[i + 1]
        elif item == "Password:":
            blockDictionary["Password"] = result[i + 1]
        elif item == "Role:":
            blockDictionary["Role"] = result[i + 1]
        elif item == "Type:":
            blockDictionary["Type"] = result[i + 1]
            #added update user idk
            if (blockDictionary['Type'] == 'Create_Account') or (blockDictionary['Type']== 'Update_User'):
                print("I made it to account")
                username = blockDictionary['Username']
                password = blockDictionary['Password']
                role = blockDictionary['Role']
                fullLegalName = "admin"
                payload = Account(username, password, role, fullLegalName)
            elif (blockDictionary['Type'] == 'Upload') or (blockDictionary['Type'] == 'Download'):
                print("I made it to upload/download")
                ipfsHash = blockDictionary['IPFS_Hash']
                fileName = blockDictionary['File_Name']
                validator = blockDictionary['Validator']
                accessList = blockDictionary['Access_List']
                payload = FileData(ipfsHash, fileName, validator, accessList)
            else:
                print(f"block type is: {blockDictionary['Type']}")
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

    return newAccount

def addToCandidateBlocks(transactionType, payload, validator):
    with validatorLock:
        oldLastIndex = blockchain[-1]
    newBlock = generateBlock(oldLastIndex, validator.address, transactionType, payload)

    if isBlockValid(newBlock, oldLastIndex):
        candidateBlocks.append(newBlock)
    
    return newBlock

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


def countOccurrences(str, word):
	
	# split the string by spaces in a
	a = str.split(" ")

	# search for pattern in a
	count = 0
	for i in range(0, len(a)):
		
		# if match found increase count 
		if (word == a[i]):
		    count = count + 1
			
	return count	 


if __name__ == "__main__":
    main()