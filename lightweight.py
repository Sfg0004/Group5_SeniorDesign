#To run server: python3 posTnet.py
#To run client: nc <ip addr> <port#>

from methods import comm
#from methods import GUI_modulated as GUI

import hashlib
import socket
import signal
import time
import threading
import os
import sys
import netifaces as ni
from subprocess import Popen, PIPE, STDOUT
import multiprocessing
import re
import errno
from random import randint
from datetime import datetime
from queue import Queue
from moralis import evm_api
import requests
import base64
from queue import Queue

# COMM.PY GLOBALS
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #new socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
samaritan = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
self_samaritan = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
neighbor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
initial_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connectport = 11453
givenport = 12453
lightweightport = 13453

#import netifaces as ni

#Import these to use the encryption
import rsa
from cryptography.fernet import Fernet

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

#Private local blockchain
currentBlockchainData = []

#client tcp address array
nodes = []

# candidate_blocks handles incoming blocks for validation
candidate_blocks = []
candidate_blocks_lock = threading.Lock()

# keep up with all uploaded IPFS hashes and file names
ipfsHashes = []
fileNames = []
accountNames = []
# announcements broadcasts winning validator to all nodes
# hi this is caleb. this list isn't called anywhere but idk the plan for it so
# i'm leaving it in
announcements = []

#targetIP = "146.229.163.145"
loggedIn = False
loggedInLock = threading.Lock()
validatorLock = threading.Lock()
currentLoggedInUserLock = threading.Lock()
candidateBlocks = [] # candidateBlocks handles incoming blocks for validation
candidateBlocksLock = threading.Lock()

# validators keeps track of open validators and balances
# validators = {}
validators = []
validator = Validator(0, Account("", "", "?", "")) # keep track of current validator

apiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImE0NmE4MmFjLWJlYjEtNGM4MC05MjIwLTIxZDFlNGQ3MGM1NyIsIm9yZ0lkIjoiMzU5ODUyIiwidXNlcklkIjoiMzY5ODMwIiwidHlwZUlkIjoiNTY2M2MwZjAtMmM3Mi00N2YxLWJkMDktNTM1M2RmYmZhNjhhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE2OTY0NDQ5MTgsImV4cCI6NDg1MjIwNDkxOH0.kW9jP_Y_2JA70nCkUaBQMW329kQK6vuyHIfFNym0SNs"

#Function to set the logged in status
def setLoggedInStatus(status):
    global loggedIn
    with loggedInLock:
        loggedIn = status

#Function to set the target IP given by the user
def setTargetIP(newIP):
    targetIP = newIP

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
    #blockchain.append(generate_block(blockchain[-1], address, "Upload", FileData("QmYRJY3Uq8skTrREx7aFkE7Ym7hXA6bk5pqJE9gWrhFB6n", "Project Timeline.pdf", "Genesis", accessList)))

currentLoggedInUser = Account("", "", "?", "")

#Need to change to password hash, and way to keep the salt safe
#Need to save username and password
def login(username, password, localBlockchain):
    for block in localBlockchain:
        if block.transactionType == "Create_Account":
            if block.payload.username == username:
                if block.payload.password == password:
                    with currentLoggedInUserLock:
                        global currentLoggedInUser
                        currentLoggedInUser.fullLegalName = block.payload.fullLegalName
                        currentLoggedInUser.username = block.payload.username
                        currentLoggedInUser.password = block.payload.password
                        currentLoggedInUser.role = block.payload.role
                    return True
    return False

localFernet = ""

def uploadIpfs(fileKey, author, fileName, localBlockchain, fileContent, FILENAME, targetIP, accessList, fileLocation):
    try:
        usersToGiveAccessTo = accessList.split('/')

        #Creates a Fernet object to encrypt text
        fernet = Fernet(base64.urlsafe_b64encode(fileKey))
        with open(fileLocation, 'rb') as f:
            newFileContent = f.read()
        #Converts the file data to base-64 encoded text
        data = (fernet.encrypt(newFileContent))
        convertedData = (base64.b64encode(data))
        #Gets the string of the file into utf-8 text
        convertedDataString = convertedData.decode('utf-8')

        #Declares the body of the message
        ipfsBody = [{
            "path": "uploaded_file", #fileName,
            "content": convertedDataString #"iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3"
        }]

        #Does not worry about a duplicate file name as that is taken care of in the Java code
        #Puts the file on ipfs
        ipfsUrl = evm_api.ipfs.upload_folder(api_key=apiKey, body=ipfsBody)[0]["path"]
        parsedPath = ipfsUrl.split('/')	#splits up the file text
        
        #Probably don't need these
        hash = parsedPath[4]            # cleans up the hash and the file name
        newFileData = FileData(hash, fileName, author, usersToGiveAccessTo)
        return sendRequest("Upload_File", newFileData, targetIP, author)
    except:
        return "Error in uploading"


# generate_block creates a new block using the previous block's hash
def generateBlock(oldBlock, address, transactionType, payload):
    t = str(datetime.now())
    new_block = Block(oldBlock.index + 1, t, oldBlock.hash, address, transactionType, payload)
    return new_block

def isBlockValid(newBlock, oldBlock):
    if oldBlock.index + 1 != newBlock.index:
        return False

    if oldBlock.hash != newBlock.prevHash:
        return False

    if newBlock.calculate_block_hash() != newBlock.hash:
        return False

    return True

def retrieveIpfs(fileKey, localBlockchain, fileName, ifpsHash, username, targetIP, filePath):
    url = "https://ipfs.moralis.io:2053/ipfs/" + ifpsHash + "/uploaded_file"	#does the url to retrieve the file from IPFS
    r = requests.get(url, allow_redirects=True)

    # #Might need to examine the blockchain for the file upload, then check its access list. if not in access list, probably should return false
    # #Loops through the blockchain, if block is upload, user is in the access list, then can download
    # for block in localBlockchain:
    #     if block.transactionType == "Upload":
    #         if username in block.payload.accessList:
    #             url = "https://ipfs.moralis.io:2053/ipfs/" + ifpsHash + "/uploaded_file"	#does the url to retrieve the file from IPFS
    #             r = requests.get(url, allow_redirects=True)


    #opens the file and adds content
    with open(filePath, "wb") as f:
        f.write(r.content)

    fernet = Fernet(fileKey)

    try:
        #Open the encrypted file and read the data
        with open(filePath, "rb") as enc_file:
            encrypted = enc_file.read()
        
        #Decrypts the file data
        decrypted = fernet.decrypt(encrypted)

        #Overwrites the encrypted data with the unencrypted data
        with open(filePath, "wb") as dec_file:
            dec_file.write(decrypted)

    #Else, if there is an error, return false
    except:
        return False
    
    accessList = []
    #Creates a new data structure to contain the hash
    newFileData = FileData(ifpsHash, fileName, username, accessList)
    #Sends a download block creation request showing that the username tried to download the file
    sendRequest("Download_File", newFileData, targetIP, username)

    return True

def decryptFile(fileContents):
    #Creates a Fernet object to encrypt text
    fileKey = 'yrnX6PYjWcITai_1Ux6IC1rXlCP7y1TiPC8dcxTi7os='
    fernet = Fernet(fileKey)
    return fernet.decrypt(fileContents)

#Function to refresh the blockchain by asking the given node 
def refreshBlockchain(targetIP):
    #Calls the function to connect to the desired IP and get the most recent blockchain
    return sendRequest("Get_Blockchain", None, targetIP, None)

#Function to loop through the given blockchain and pull out the file names
def getFileList(localBlockchain):
    if localBlockchain is None:
        return
    newFileNameList = []
    for block in localBlockchain:
        if block.index == 0:
            continue
        if block.transactionType == "Upload" and block.payload.fileName not in newFileNameList:
            newFileNameList.append(block.payload.fileName)
    return newFileNameList

#Function to loop through the given blockchain and pull out the hashes for files
def getipfsHashes(localBlockchain):
    newIpfsHashesList = []
    for block in localBlockchain:
        if block.index == 0:
            continue
        if block.transactionType == "Upload" and block.payload.ipfsHash not in newIpfsHashesList:
            newIpfsHashesList.append(block.payload.ipfsHash)
    return newIpfsHashesList

#Function to scan the blockchain and list the active users
def getListActiveUsers(localBlockchain):
    #Creates a temporary list to hold the active users
    activeUsers = []
    #Loops through the entire blockchain searching for active user accounts
    for block in localBlockchain:
        #If a block for an account
        if block.transactionType == "Create_Account":
            #If the user account is not already in the list of accounts, save it
            if block.payload.username not in activeUsers:
                #Saves the current user's username
                activeUsers.append(block.payload.username)
    #Returns the list of active users accounts
    return activeUsers

#Function to get the role of the given user
def getUserRole(localBlockchain, username):
    #Loops through the entire blockchain given
    for block in localBlockchain:
        #If a block for an account
        if block.transactionType == "Create_Account":
            #If the username of the block matches that of 
            if block.payload.username == username:
                return  block.payload.role
    #Should never happen
    return None

#Function to create a new account
def createAccount(username, password, name, roleSelection):
    if roleSelection == "Admin":
        role = "a"
    elif roleSelection == "Doctor":
        role = "d"
    else:
        role = "p"
    newAccount = Account(username, password, role, name)
    return newAccount

#Function to create a new account
def createNewAccount(username, password, role, LegalName, localBlockchain, targetIP, authorizingUser):
    #Loops through the blockchain and if an account has the same username, returns False
    for block in localBlockchain:
        if block.transactionType == "Create_Account" and block.payload.username == username:
            return "False"
    
    #Theoretically, the best check is to get the next blockchain and check the blocks for the addition of a new user
    #Need to create a function to generate a block and send that block as a request
    #Else, the same username does not exist, so create the block and send a request for it to be added
    return sendRequest("Create_User", createAccount(username, password, LegalName, role), targetIP, authorizingUser)

#Function to convert the blockchain's text into a string
def getTextBlockchain(localBlockchain):
    #String to contain the final text version of the blockchain
    finalText = ""
    for blockData in localBlockchain:
        #Do something
        if blockData.transactionType == "Genesis":
            finalText = finalText + "\nIndex: " + str(blockData.index) + "\n"
            finalText = finalText + "Timestamp: " + blockData.timestamp + "\n"
            finalText = finalText + "Type: " + blockData.transactionType + "\n"
        else:
            finalText = finalText + "\nIndex: " + str(blockData.index) + "\n"
            finalText = finalText + "Timestamp: " + blockData.timestamp + "\n"
            finalText = finalText + "Previous_Hash: " + blockData.prevHash + "\n"
            finalText = finalText + "Validator: " + blockData.validatorName + "\n"
            finalText = finalText + "Hash: " + blockData.hash + "\n"
            finalText = finalText + "Type: " + blockData.transactionType + "\n"
            if blockData.transactionType != "Create_Account":
                finalText = finalText + "IPFS_Hash: " + blockData.payload.ipfsHash + "\n"
                finalText = finalText + "File_Name: " + blockData.payload.fileName + "\n"
            else:
                finalText = finalText + "Username: " + blockData.payload.username + "\n"
                finalText = finalText + "Password: " + blockData.payload.password + "\n"
                finalText = finalText + "Role: " + blockData.payload.role + "\n"
        finalText = finalText + "-----------------------------------------" + "\n"

    return finalText

def calculate_hash(s):  # Added this function
    h = hashlib.sha256()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

#Function that is used to generate the keys
def genKeys():
    #Generates the pubic and private keys
    return rsa.newkeys(1024)

#Function to parse the given data for the the public key
def getPublicKey(KeyData):
    return KeyData[0]

#Function to parse the given data for the the private key
def getPrivateKey(KeyData):
    return KeyData[1]

#Function to get the file symmetric key
def getFileKey(targetIP, publicKey, privateKey):
    return sendRequest("Get_Key", publicKey, targetIP, privateKey)

def convertString(currentBlockchain):
    localBlockchain = []
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
            localBlockchain.append(newBlock)

        i += 1
    return localBlockchain

#Function to ensure the data being sent in is
def isBlockchain(testBlockchain):
    if type(testBlockchain) is list:
        return True
    return False


#Function to send the request to the target IP
def sendRequest(sendRequestMessage, blockToAdd, targetIP="146.229.163.145", authorizingUser=None):
    try:
        #Creates a socket
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.settimeout(5)
        #Connects to the other device
        clientSocket.connect((targetIP, lightweightport))
        #Based on the request, craft a message and send it
        if sendRequestMessage == "Upload_File":
            #Sends the messages to the connected full node
            clientSocket.send((sendRequestMessage).encode("utf-8")[:4096])
            clientSocket.send((" ").encode("utf-8")[:4096])
            clientSocket.send((blockToAdd.ipfsHash).encode("utf-8")[:4096])
            clientSocket.send((" ").encode("utf-8")[:4096])
            clientSocket.send((blockToAdd.fileName).encode("utf-8")[:4096])
            clientSocket.send((" ").encode("utf-8")[:4096])
            clientSocket.send((blockToAdd.authorName).encode("utf-8")[:4096])
            for item in blockToAdd.accessList:
                clientSocket.send((" ").encode("utf-8")[:4096])
                clientSocket.send((str(item)).encode("utf-8")[:4096])
            #Closes the socket
            clientSocket.close()
            #If this line is reached(no error have resulted), returns the status of the operation as true
            return blockToAdd.ipfsHash
        elif sendRequestMessage == "Download_File":
            #Sends the messages to the connected full node
            clientSocket.send((sendRequestMessage).encode("utf-8")[:4096])
            clientSocket.send((" ").encode("utf-8")[:4096])
            clientSocket.send((authorizingUser).encode("utf-8")[:4096])
            clientSocket.send((" ").encode("utf-8")[:4096])
            clientSocket.send((blockToAdd.ipfsHash).encode("utf-8")[:4096])
            clientSocket.send((" ").encode("utf-8")[:4096])
            clientSocket.send((blockToAdd.fileName).encode("utf-8")[:4096])
            #Closes the socket
            clientSocket.close()
            #If this line is reached(no error have resulted), returns the status of the operation as true
            return "True"
        elif sendRequestMessage == "Create_User":
            #Sends the messages to the connected full node
            clientSocket.send((sendRequestMessage).encode("utf-8")[:4096])
            time.sleep(0.5)
            clientSocket.send((" ").encode("utf-8")[:4096])
            clientSocket.send((str(authorizingUser)).encode("utf-8")[:4096])
            clientSocket.send((" ").encode("utf-8")[:4096])
            clientSocket.send((str(blockToAdd.username)).encode("utf-8")[:4096])
            clientSocket.send((" ").encode("utf-8")[:4096])
            clientSocket.send((str(blockToAdd.password)).encode("utf-8")[:4096])
            clientSocket.send((" ").encode("utf-8")[:4096])
            clientSocket.send((str(blockToAdd.role)).encode("utf-8")[:4096])
            clientSocket.send((" ").encode("utf-8")[:4096])
            clientSocket.send((str(blockToAdd.fullLegalName)).encode("utf-8")[:4096])
            #Closes the socket
            clientSocket.close()
            #If this line is reached(no error have resulted), returns the status of the operation as true
            return "True"
        #Code to get the encryption key
        elif sendRequestMessage == "Get_Key":
            #Sends the message requesting the key
            clientSocket.send((sendRequestMessage).encode("utf-8")[:4096])
            time.sleep(0.5)
            #Sends the message with the public key to encrypt the key
            clientSocket.send((blockToAdd.save_pkcs1().decode("utf-8")).encode("utf-8")[:4096])
            #Waits for reception of the file key and decrypts it with the privateKey
            return rsa.decrypt(clientSocket.recv(4096), authorizingUser)
        #If the desire is to get the blockchain, send a request for it
        elif sendRequestMessage == "Get_Blockchain":
            #Sends the message
            clientSocket.send((sendRequestMessage).encode("utf-8")[:4096])
            #Waits for reception of the blockchain and converts it from a string to a blockchain
            NewBlockchain = clientSocket.recv(4096).decode("utf-8")
            #Closes the socket
            clientSocket.close()
            #If this line is reached, returns the status of the operation by sending the new blockchain back
           # return NewBlockchain
            return convertString(NewBlockchain)
        #Else, invalid request type, so do nothing, should never happen
        else:
            return "False"
        
    #Except if something has gone wrong, return false as the operation failed
    except socket.timeout:
        return "DeviceNotOnline"#Except if something has gone wrong, return false as the operation failed
    except Exception as e:
        return str(e.__cause__)#"Something went wrong"


def main(targetIP):
    #Calls the function to connect to the desired IP and get the most recent blockchain
    return sendRequest("Get_Blockchain", None, targetIP, None)
    """
    # Create genesis block and admin account block
    genesis_block = generate_genesis_block()
    blockchain.append(genesis_block)
    generate_sample_blocks()
    address = ""
    blockchain.append(generate_block(blockchain[-1], address, "Create_Account", Account("admin", "admin", "a", "Admin")))
    blockchain.append(generate_block(blockchain[-1], address, "Create_Account", Account("root", "root", "p", "Myself")))
    blockchain.append(generate_block(blockchain[-1], address, "Create_Account", Account("sampleUser", "root", "p", "I")))
    """

if __name__ == "__main__":
    main(targetIP="146.229.163.145")
