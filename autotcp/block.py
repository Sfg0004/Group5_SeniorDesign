
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


#CLASSES
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
        self.hash = self.calculate_block_hash()     # hash for the block
        self.transactionType = transactionType      # either "Upload", "Download", "Create_Account", or "Genesis"
        self.payload = payload                      # ** EITHER FILEDATA OR ACCOUNT OBJECT
        
        # update this depending on how sign-in/authorization works:
        self.approved_IDs = []

    def calculate_hash(self, s):# calculateHash is a simple SHA256 hashing function
        h = hashlib.sha256()
        h.update(s.encode('utf-8'))
        return h.hexdigest()
    
    def calculate_block_hash(self): # calculateBlockHash returns the hash of all block information
        record = str(self.index) + self.timestamp + self.prevHash
        return self.calculate_hash(record)


#VARIABLES
blockchain = [] # Blockchain is a series of validated Blocks
temp_blocks = []
ipfsHashes = [] # keep up with all uploaded IPFS hashes and file names
fileNames = []


#FUNCTIONS
def calculate_hash(s):  #separate function for hashing
    h = hashlib.sha256()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

def generate_genesis_block(): # generate_genesis_block creates the genesis block
    t = str(datetime.now())
    genesis_block = Block(0, t, "", "", "Genesis", 0)
    return genesis_block

def generate_block(oldBlock, address, transactionType, payload): # generate_block creates a new block using the previous block's hash
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
    print("bruh")
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
            new_block = GivenBlock(index, timestamp, prevHash, hash, validatorName, transactionType, payload)
            blockchain.append(new_block)

        i += 1
    printBlockchain()
    return result