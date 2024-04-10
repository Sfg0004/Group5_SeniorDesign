#change eth interface name if necessary in myIP()
from methods import block
#from methods import decentral
from methods import comm

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


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #new socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
samaritan = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
self_samaritan = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
neighbor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
initial_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connectport = 11412
givenport = 12412

# 
#
# BLOCK.PY CLASSES
#
#
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

#BLOCK.PY VARIABLES
blockchain = [] # Blockchain is a series of validated Blocks
tempBlocks = []
ipfsHashes = [] # keep up with all uploaded IPFS hashes and file names
fileNames = []
nodes = [] #client tcp address array
candidateBlocks = [] # candidateBlocks handles incoming blocks for validation
# candidateBlocksLock = threading.Lock()
# validatorLock = threading.Lock()
validators = [] # validators keeps track of open validators and balances
validator = Validator(0, Account("", "", "?", "")) # keep track of current validator
stopThreads = False # use flag to stop threading
# key for ipfs upload
apiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImE0NmE4MmFjLWJlYjEtNGM4MC05MjIwLTIxZDFlNGQ3MGM1NyIsIm9yZ0lkIjoiMzU5ODUyIiwidXNlcklkIjoiMzY5ODMwIiwidHlwZUlkIjoiNTY2M2MwZjAtMmM3Mi00N2YxLWJkMDktNTM1M2RmYmZhNjhhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE2OTY0NDQ5MTgsImV4cCI6NDg1MjIwNDkxOH0.kW9jP_Y_2JA70nCkUaBQMW329kQK6vuyHIfFNym0SNs"
changeFlag = True

def myIP():
    return (ni.ifaddresses('enp0s31f6')[ni.AF_INET][0]['addr'])

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    comm.clientOut.close()
    comm.blockFile.close()
    sys.exit(0)

def main():
    myip = comm.myIP()

    signal.signal(signal.SIGINT, signal_handler)

    global iplist
    
    self_samaritan_to_client = Queue()
    client_to_self_samaritan = Queue()

    #message_queue.Queue()  # create a Shared queue for communication
    initial_samaritan_jointo_ip = "146.229.163.144"#input("Enter the IP of a node in the blockchain you want to join: ")

    threading.Thread(target=run_server, args=()).start()#self_samaritan_to_client,client_to_self_samaritan,)).start()
    #initial_samaritan_jointo_ip = "146.229.163.149"
    time.sleep(2)

    threading.Thread(target=run_client, args=(initial_samaritan_jointo_ip,)).start()#self_samaritan_to_client,client_to_self_samaritan,)).start()

def run_client(initial_samaritan_jointo_ip):#self_samaritan_to_client,client_to_self_samaritan): #needs periodic ip requesting(checking) added
   # original_stdout = sys.stdout
    
    #with open('clientOut.txt', 'w') as clientOut:
    #sys.stdout = clientOut
    #neighbor_ip = "146.229.163.144"  # replace with the neighbor's(server's) IP address
    #connect_port = 11113 #neighbor's (server's) port
    comm.write_to_client_out("debug, in client\n")
    while(1):
        try:
            samaritan_ip, samaritan_port = comm.requestConnection(initial_samaritan_jointo_ip, connectport, initial_client, givenport)
            comm.write_to_client_out ("server accepted my client connection. hooray!")
            break
        except:
            comm.write_to_client_out("I am client. My request to connect to a server failed.")
            if len(blockchain) == 0:
                print("Creating blockchain...")
                genesisBlock = generateGenesisBlock()
                blockchain.append(genesisBlock)
                generateSampleBlocks()

    while(1): #automatic close response present in receivedatafromserver
        response = comm.receivedatafromserver(initial_client)
        if (response == "closed"):
            break
        time.sleep(1)

    try:
        comm.write_to_client_out(f"samaritan receiveport is: {samaritan_port}")
        time.sleep(5)
        comm.requestsustainedConnection(samaritan_ip, samaritan_port, client)
        comm.write_to_client_out("sustained samaritan connection successful. hooray!")
    except:
        comm.write_to_client_out("I am client. My request for sustained connection failed.")

    try:
        while(1): #automatic close response present in receivedatafromserver
            #message = comm.receivedatafromsamaritan(client)
            sample = "5678"
            #print("I got the sample")
            
            #NEED ADMIN BLOCK
            # genesis_block = block.generate_genesis_block()
            # block.blockchain.append(genesis_block)
            # block.generate_sample_blocks()
            # blockchain = block.assembleBlockchain()
            comm.senddatafromclient(sample, client)

            # if (message.lower() == "closed"):
            #     comm.closesamaritanConnection(client)
            #     exit(0)
            # else:
                #blockchain = block.assembleBlockchain()
                #comm.write_to_block_file(message)
                #comm.senddatafromclient(blockchain)
            #received_iplist = request_iplist(client)
            #message_refresh_iplist(iplist,received_list)
            time.sleep(3) #rn iplist updates every second

            message = comm.receivedatafromsamaritan(client)

            if (message.lower() == "closed"):
                 comm.closesamaritanConnection(client)
                 exit(0)

    except:
        comm.clientOut.close() 

def run_server():#self_samaritan_to_client, client_to_self_samaritan): #add func to talk to samaritan and samaritan to listen to server (listenServer)
    global receiveport
    global givenport
    try:
        comm.bindasServer(connectport, server)
        comm.listenforRequests(connectport, server)

        while(1):
            # accept incoming connections

                # accept incoming connections
            requester = comm.acceptconnectportConnection(server) #sit waiting/ready for new clients
            comm.receivedatafromrequester(requester)
            comm.approveConnection(requester, givenport) #I tell client what port to talk to me on
            receiveport = comm.setreceiveequal(givenport)
            givenport = comm.incgiven(givenport)
            comm.closerequesterConnection(requester)

            if(1):
                ppid = os.getpid()
                print("Parent process PID:", ppid)
                child_pid = os.fork()
                if child_pid == 0:            #   This code is executed by the child process

                    myip = comm.myIP()
                    self_samaritan.bind((myip, receiveport)) 
                    print(f"receiveport is: {receiveport}")

                    self_samaritan.listen(0)
                    neighbor = comm.acceptConnection(self_samaritan) #wait here for client's sustained request

                    time.sleep(0.5)

                    data = "BLOCKCHAIN"

                    while(1):
                        time.sleep(1)
                        #if(not neighbor)
                            #exit(0)
                        #NEED ADMIN BLOCK
                        
                        blockchainMessage = assembleBlockchain()
                        comm.senddatatoneighbor(neighbor, blockchainMessage)
                        #data = "Server Data"
                        #comm.senddatatoneighbor(neighbor, data)
                        message = comm.receivedatafromneighbor(neighbor)
                        #if(message == "requesting iplist."):
                            #send_iplist(iplist)

                    print("I am samaritan. Stopping my good works.")
                    comm.closeneighborConnection(self_samaritan) #close my given port (my side sustained connection as their neighbor)

                else:
                    os.wait() #parent wait for child
    except OSError:
        print("OSerror")

#FUNCTIONS
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
    genesisBlock = Block(0, t, "", "", "Create_Account", Account("admin", "admin", "a", "Admin"))
    return genesisBlock

def generateBlock(oldBlock, address, transactionType, payload): # generate_block creates a new block using the previous block's hash
    t = str(datetime.now())
    newBlock = Block(oldBlock.index + 1, t, oldBlock.hash, address, transactionType, payload)
    return newBlock

def generateSampleBlocks():
    t = str(datetime.now())
    address = ""
    address = calculateHash(t)
    accessList = []
    blockchain.append(generateBlock(blockchain[-1], address, "Upload", FileData("QmRB39JYBwEqfpDJ5czsBpxrBtwXswTB4HUiiyvhS1b7ii", "chest_xray.png", "Genesis", accessList)))
    blockchain.append(generateBlock(blockchain[-1], address, "Upload", FileData("QmeUp1ciEQnKo9uXLi1SH3V6Z6YQHtMHRgMbzNLaHt6gJH", "Patient Info.txt", "Genesis", accessList)))
    blockchain.append(generateBlock(blockchain[-1], address, "Upload", FileData("QmeuNtvAJT8HMPgzEyuHCnWiMQkpwHBtAEHmzH854TqJXW", "RADRPT 08-13-2023.pdf", "Genesis", accessList)))
    blockchain.append(generateBlock(blockchain[-1], address, "Upload", FileData("QmYRJY3Uq8skTrREx7aFkE7Ym7hXA6bk5pqJE9gWrhFB6n", "Project Timeline.pdf", "Genesis", accessList)))

def createFirstBlocks():
    genesisBlock = generateGenesisBlock()
    blockchain.append(genesisBlock)
    address = ""
    # blockchain.append(generateBlock(blockchain[-1], address, "Create_Account", Account("admin", "admin", "a", "Admin")))
    # generateSampleBlocks()

def printBlockchain(): #makes the blockchain print better!
    for block in blockchain:
        if block.transactionType == "Genesis":
            printGenesisBlock()
        else:
            print("\nIndex: " + str(block.index))
            print("Timestamp: " + block.timestamp)
            print("Previous_Hash: " + block.prevHash)
            print("Validator: " + block.validatorName)
            print("Hash: " + block.hash)
            print("Type: " + block.transactionType)
            if block.transactionType != "Create_Account":
                print("IPFS_Hash: " + block.payload.ipfsHash)
                print("File_Name: " + block.payload.fileName)
            else:
                print("Username: " + block.payload.username)
                print("Password: " + block.payload.password)
                print("Role: " + block.payload.role)
        print("-----------------------------------------")

def printGenesisBlock(): #prints the genesis block better
    block = blockchain[0]
    print("\nIndex: " + str(block.index))
    print("Timestamp: " + block.timestamp)
    print("Type: " + block.transactionType)

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

def printGenericMenu(): #prints generic menu to user
    print("\n[1] Upload File\n")
    print("[2] Download File\n")
    print("[q] Quit\n")

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
                print("I made it to account")
                username = blockDictionary['Username']
                password = blockDictionary['Password']
                role = blockDictionary['Role']
                fullLegalName = "admin"
                payload = Account(username, password, role, fullLegalName)
            elif blockDictionary['Type'] == 'Upload':
                print("I made it to upload")
                ipfsHash = blockDictionary['IPFS_Hash']
                fileName = blockDictionary['File_Name']
                validator = blockDictionary['Validator']
                payload = FileData(ipfsHash, fileName, validator, accessList)
            else:
                print(f"block type is: {blockDictionary['Type']}")
                payload = FileData("", "", "", accessList)
            index = blockDictionary['Index']
            timestamp = blockDictionary['Timestamp']
            prevHash = blockDictionary['Previous_Hash']
            hash = blockDictionary['Hash']
            validatorName = blockDictionary['Validator']
            transactionType = blockDictionary['Type']
            newBlock = GivenBlock(index, timestamp, prevHash, hash, validatorName, transactionType, payload)
            blockchain.append(newBlock)

        i += 1
    # printBlockchain()
    return result

def login(username, password): # , root
    global validator
    print(f"Username: {username}, Password: {password}")
    account = Account("false", "false", "a", "False")
    validLogin = False
    for block in blockchain:
        if block.transactionType == "Create_Account":
            if block.payload.username == username:
                if block.payload.password == password:
                    validLogin = True
                    account = block.payload
    if validLogin == False:
        print("Bad login.\n")
        # root.children["loginScene"].children["statusLabel"].configure(text="Incorrect login.")
        return validLogin, account
    
    if account.role == "a":
        print("Successful login for admin.\n")
        # switchScenes(root.children["loginScene"], root.children["adminMenu"])
    elif account.role == "d":
        print("Successful login for doctor.\n")
        # switchScenes(root.children["loginScene"], root.children["genericMenu"])
    else:
        print("Successful login for patient.\n")
        # switchScenes(root.children["loginScene"], root.children["genericMenu"])

    validator = createValidator(account)
    # updateName(root)
    print("Validator created.")
    return validLogin, account

def logout(): # root
    global validator
    if validator in validators:
        validators.remove(validator)
    # if validator.role == "a":
    #     switchScenes(root.children["adminMenu"], root.children["loginScene"])
    # else:
    #     switchScenes(root.children["genericMenu"], root.children["loginScene"])

def createValidator(currentAccount):
    #Randomly stakes coins to prevent a favored node
    balance = randint(1,100)

    newValidator = Validator(balance, currentAccount)

    # with validatorLock:
    validators.append(newValidator)
    for validator in validators:
        print(f"{validator.address} : {validator.balance}")             

    return newValidator

def createAccount(username, password, name, roleSelection): # , root
    print("role is " + roleSelection)
    if roleSelection == "Admin":
        role = "a"
    elif roleSelection == "Doctor":
        role = "d"
    else:
        role = "p"
    newAccount = Account(username, password, role, name)
    addToCandidateBlocks("Create_Account", newAccount)
    print(f"Created account for: {newAccount.fullLegalName}")

    # root.children["createAccountMenu"].children["statusLabel"].configure(text=f"{newAccount.fullLegalName}'s account successfully created!")

    return newAccount

def uploadIPFS(): # root
    # open dialog box to choose file
    # root.filename = filedialog.askopenfilename(title="Select A File", filetypes=(("All Files", "*.*"), ("PNGs", "*.png"), ("Text Files", "*.txt"), ("PDFs", "*.pdf")))
    
    # if 'cancel' was selected on dialog box:
    # if len(root.filename) == 0:
    #     return

    fileName = input("Input your file path: ")
    fileName = fileName[1:-2]
    
    # get file 
    # fileName = root.filename
    with open(fileName, "rb") as file:
        fileContent = file.read()
    
    # encode file for ipfs
    encodedContent = base64.b64encode(fileContent)
    encodedContentString = encodedContent.decode('utf-8')
    ipfsBody = [{
        "path": "uploaded_file", #fileName,
        "content": encodedContentString #"iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3"
    }]

    fileName = fileName.split('/')[-1]
    
    # if file name is already stored on blockchain:
    if fileName in fileNames:
        # root.children["genericMenu"].children["statusLabel"].configure(text=f"A file named {fileName} already exists!", fg="red")
        print(f"A file named {fileName} already exists!")
        return
    
    # put file on ipfs
    ipfsUrl = evm_api.ipfs.upload_folder(api_key=apiKey, body=ipfsBody)[0]["path"]
    parsedPath = ipfsUrl.split('/')	#splits up the file text
    
    hash = parsedPath[4]            # cleans up the hash and the file name
    ipfsHashes.append(hash)        # update the hash and file lists
    fileNames.append(fileName)

    #Deletes the temorary upload file
    #os.remove(encryptedFileLocation)

    accessList = []
    newFileData = FileData(hash, fileName, validator.address, accessList)
    addToCandidateBlocks("Upload", newFileData)
    print(f"Uploaded {newFileData.fileName} to IPFS.")
    # root.children["genericMenu"].children["statusLabel"].configure(text=f"{fileName} added successfully.", fg="green")

    return newFileData

def downloadIPFS(fileIndex):# , root def retrieveIpfs(conn, symmetricKey):
    hash = ipfsHashes[fileIndex]
    url = "https://ipfs.moralis.io:2053/ipfs/" + hash + "/uploaded_file"	#does the url to retrieve the file from IPFS
    r = requests.get(url, allow_redirects=True)
    fileType = r.headers.get("content-type").split("/")[1]
    fileName = fileNames[fileIndex]
    with open(fileName, "wb") as f:
        f.write(r.content)	#opens the file and adds content

    #T here, Use symmetric key to decrypt the file, r.content
    #This function opens the first file, reads the dencrypted data, closes the file
    #Ten opens the second file, clears it, writes all decrypted data to it, then closes the file
    #SE.decryptFile(symmetricKey, file_name, file_name)

    accessList = []
    newFileData = FileData(hash, fileName, validator.address, accessList)
    addToCandidateBlocks("Download", newFileData)
    print(f"Downloaded {newFileData.fileName} from IPFS.")

    # root.children["downloadMenu"].children["statusLabel"].configure(text=f"{fileName} downloaded successfully.")

    return newFileData

def getFileList():
    global ipfsHashes
    global fileNames

    ipfsHashes = []
    fileNames = []

    for block in blockchain:
        if block.index == 0:
            continue
        if block.transactionType == "Upload":
            ipfsHashes.append(block.payload.ipfsHash)
            fileNames.append(block.payload.fileName)
    
    return ipfsHashes, fileNames

def addToCandidateBlocks(transactionType, payload):
    # with validatorLock:
    oldLastIndex = blockchain[-1]
    newBlock = generateBlock(oldLastIndex, validator.address, transactionType, payload)

    if isBlockValid(newBlock, oldLastIndex):
        candidateBlocks.append(newBlock)

# pickWinner creates a lottery pool of validators and chooses the validator who gets to forge a block to the blockchain
def pickWinner(_candidateBlocks):
    message = "default_blockchain_message"
    print("\nPicking winner...")
    # while stopThreads == False:
    time.sleep(0.15) # .15 second refresh
    # with validatorLock:    
    if len(validators) > 0:
        lotteryWinner = getLotteryWinner().address
        if len(_candidateBlocks) < 1:
            print("No candidate blocks")
        else:
            print(f"There are {len(_candidateBlocks)} candidate blocks")
        for block in _candidateBlocks:
            if block.validatorName == lotteryWinner:
                # make sure candidate index isn't duplicated in existing blockchain (avoid forking):
                indexes = []
                for approvedBlock in blockchain:
                    indexes.append(approvedBlock.index)
                if block.index in indexes:
                    newBlock = generateBlock(blockchain[-1], block.validatorName, block.transactionType, block.payload)
                    blockchain.append(newBlock)
                else:
                    blockchain.append(block)
                _candidateBlocks.remove(block)
                printBlockchain()
                changeFlag = True
                print(f"*pickWinner*: Last block index: {getBlockchain()[-1].index}")
                message = assembleBlockchain()
                # with open("pickWinner.txt", 'w') as file:
                #     file.write(message)
                
                # break
    return message

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
