#Change eth interface name if necessary in myIP()

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
import shlex  
from subprocess import Popen, PIPE, STDOUT
import ipaddress

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #new socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
samaritan = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
neighbor_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
needy = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
neighbor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connectport = 11188
givenport = 12278

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

#separate function for hashing
def calculate_hash(s):  # Added this function
    h = hashlib.sha256()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

# Blockchain is a series of validated Blocks
blockchain = []
temp_blocks = []

# keep up with all uploaded IPFS hashes and file names
ipfsHashes = []
fileNames = []

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

#makes the blockchain print better!
def printBlockchain():
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

#prints the genesis block better
def printGenesisBlock():
    block = blockchain[0]
    print("\nIndex: " + str(block.index))
    print("Timestamp: " + block.timestamp)
    print("Type: " + block.transactionType)

#assembles blockchain to be sent to requesting neighbor
def assembleBlockchain():
    message = ""
    for block in blockchain:
        if block.transactionType == "Genesis":
            print("Genesis would go here")
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

#assembles genesis block to be sent to requesting neighbor
def expandGenesisBlock():
    block = blockchain[0]
    index = "Index: " + str(block.index)
    time = "Timestamp: " + block.timestamp
    type = "Type: " + block.transactionType
    genesis = "\n" + index + "\n" + time + "\n"+ type
    return genesis       

#assembles standard block to be sent to requesting neighbor
def expandStandardblock(block):
    index = "Index: " + str(block.index)
    time = "Timestamp: " + block.timestamp
    #type = "Type: " + block.transactionType
    prevHash = "Previous_Hash: " + block.prevHash
    hash = "Hash: " + block.hash
    validator = "Validator: " + block.validatorName
    message1 = "\n" + index + "\n" + time + "\n" + prevHash + "\n" + hash + "\n" + validator
    return message1

#assembles user credential block to be sent to requesting neighbor
def expandCredentials(block):
    print("bruh")
    username = "Username: " + block.payload.username
    password = "Password: " + block.payload.password
    role = "Role: " + block.payload.role
    type = "Type: " + block.transactionType
    message3 = "\n" + username + "\n" + password + "\n" + role + "\n" + type
    return message3

#prints generic menu to user
def printGenericMenu():
    print("\n[1] Upload File\n")
    print("[2] Download File\n")
    print("[q] Quit\n")

#finds the user's IP
def myIP():
    return (ni.ifaddresses('enp0s31f6')[ni.AF_INET][0]['addr'])

def listenforRequests(): #server method, connectport

    # listen for incoming connections
    server.listen(0)
    server_ip = myIP()
    print(f"I am server. Listening on {server_ip}:{connectport}")

def requestConnection(neighbor_ip, neighbor_port): #client method
    server_ip = neighbor_ip
    server_port = neighbor_port
    try:
        client.connect((server_ip, server_port)) #client requests to connect to server
        myip = myIP()
        message = f"be my neighbor? answer on {myip}, port: {givenport}"
        sendclientData(message) #client parameter

        # receive message from the server
        response = receiveneighborData(client)

        neighbor_ip, neighbor_port = extractIP(response)

        return neighbor_ip, neighbor_port

    except socket.error:
        return ("failure")

def requestsustainedConnection(neighbor_ip, neighbor_port): #client method
    server_ip = neighbor_ip
    server_port = int(neighbor_port)
    try:
        print(f"Trying to connect to: {server_ip}:{server_port}")
        time.sleep(1)
        needy.connect((server_ip, server_port)) #client requests to connect to server
        print("A")
        myip = myIP()
        #message = "beginning sustained connection. love, neighbor"
        #sendneighborData(message)
        print("B")
        

        # receive message from the server
        #response = receiveneighborData(needy)
        print("C")
        #return neighbor_ip, neighbor_port #throwaway
    except Exception as e: print(e)



def acceptclientConnection(): #server method
    client_socket, client_address = server.accept()
    print(f"I am server. Accepted connection from {client_address[0]}:{client_address[1]}")
    return client_socket

def acceptConnection(): #samaritan method
    neighbor_socket, neighbor_address = samaritan.accept()
    print(f"I am server/samaritan. Accepted connection from {neighbor_address[0]}:{neighbor_address[1]}")
    return neighbor_socket

def approveConnection(client_socket): #server method
    global givenport
    myip = myIP()
    response = f"accepted. talk on {myip}, port: {givenport}".encode("utf-8") # convert string to bytes
    givenport = givenport + 1
    #send accept response to the client
    client_socket.send(response)


def closeclientConnection(client_socket): #server method
    time.sleep(0.5) #without the client sees "acceptedclosed"
    sendclientsocketData(client_socket, "closed")
    #time.sleep(0.5)
    client_socket.close()
    print("I am server. Connection to client closed")
    # close server socket
    #server.close()

def closeserverConnection(client): #client method
    #time.sleep(0.5)
    client.send("client closing".encode("utf-8"))
    client.close()
    print("I am client. Connection to server closed")
    # close server socket
    #server.close()


def receiveclientData(client_socket): #server method
    request = client_socket.recv(1024)
    request = request.decode("utf-8") # convert bytes to string
    print(f"I am server. Received: {request}")

    return request

def receiveneighborData(client): #client method

    response = client.recv(1024)
    response = response.decode("utf-8")
   
    print(f"I am client. Received: {response}")

    if response.lower() == "closed":
        closeserverConnection(client)

    return response

def sendneighborData(data): #client method, buffer size 1024 may need to increase to accomodate blockchain message
    needy.send(data.encode("utf-8")[:1024])

def sendclientData(data): #client method, buffer size 1024 may need to increase to accomodate blockchain message
    client.send(data.encode("utf-8")[:1024])

def sendclientsocketData(client_socket, data): #server method, buffer size 1024 may need to increase to accomodate blockchain message
    client_socket.send(data.encode("utf-8")[:1024])

def extractIP(message): #server method
    ip_split = message.split("on ")
    temp = ip_split[1]
    temp2 = temp.partition(",")
    port_split = message.split("port: ")
    
    client_ip = temp2[0]
    client_port = port_split[1]
    print(f"ip_split: {client_ip}")
    print(f"port_split: {client_port}")

    return client_ip, client_port

def bindasServer(port): 
    myip = myIP() # I am the server
    #port = 11113 #connectport

    # bind the socket to a specific address and port
    server.bind((myip, port)) # I am the server

def convertString(currentBlockchain):
    blockDictionary = {}
    delimiters = ["\n"]
    for delimiter in delimiters:
        currentBlockchain = " ".join(currentBlockchain.split(delimiter))
    result = currentBlockchain.split()
    print(result)
    i = 0
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
        
        i += 1
    print(blockDictionary)
    return result


def server_program():
    global givenport
    # create a socket object
    bindasServer(connectport)

    listenforRequests()

    # accept incoming connections
    client_socket = acceptclientConnection()

    receiveport = givenport
    message = receiveclientData(client_socket)
    #client_ip, client_port = extractIP(message) not used

    approveConnection(client_socket)

    message1 = "final connectport test, about to close"
    sendclientsocketData(client_socket, message1)

    time.sleep(0.1)

    closeclientConnection(client_socket)


    myip = myIP()
    samaritan.bind((myip, receiveport)) 
    print(f"receiveport is: {receiveport}")

    samaritan.listen(0)
    print("here")
    neighbor_socket1 = acceptConnection()
    print("there")
  #  #wait for client to request new connection

   # # if (requestsustainedConnection(client_ip, client_port) == "connected"):
   # #     print ("sustained connection successful. hooray!")
   # # else:
   # #     print("I am client. My request for sustained connection failed.")
   # message = receiveclientData(neighbor_socket1)
   # print(message)

    time.sleep(0.5)
    message2 = "samaritan to neighbor, over"
    sendclientsocketData(neighbor_socket1, message2)

    #time.sleep(0.5)

    message3 = "samaritan to neighbor, send your blockchain or ask for mine"
    sendclientsocketData(neighbor_socket1, message3)

    message = receiveclientData(neighbor_socket1)
    print(message)

    b = assembleBlockchain()
    sendclientsocketData(neighbor_socket1, b)
    #sendclientsocketData(neighbor_socket1, blockchain)
    #print(sendBlockchain)
    #client_socket.send(sendBlockchain)

    # sendBlockchain = str(assembleBlockchain())
    # sendclientsocketData(neighbor_socket1, sendBlockchain)

    print("I am samaritan. Stopping my good works.")

    closeclientConnection(neighbor_socket1) #close my given port (my side sustained connection as their neighbor)


    #create new sustained connection


    # receive data from the client
    # while True:
    #     receiveData(client_socket)
    #     if request.lower() == "close": # if we receive "close" from the client, then we breakout of the loop and close the conneciton
    #         closeConnection()
        
    #     #close connectport connection 
    #     closeConnection()

    #     #start new sustained connection


def client_program():#neighbor_ip):
    neighbor_ip = "146.229.163.144"  # replace with the neighbor's(server's) IP address
    #connect_port = 11113 #neighbor's (server's) port

    try:
        neighbor_ip, neighbor_port = requestConnection(neighbor_ip, connectport)
        print ("server accepted my client connection. hooray!")
    except:
        print("I am client. My request to connect to a neighbor failed.")

    message = receiveneighborData(client)
    #print(message)

    message = receiveneighborData(client)
    #print(message)

    ##closeserverConnection(client)

   ##neighbor_ip, neighbor_port = extractIP(message)
    try:
        print(f"samaritan receiveport is: {neighbor_port}")
        time.sleep(0.2)
        requestsustainedConnection(neighbor_ip, neighbor_port)
        print ("sustained neighbor connection successful. hooray!")
    except:
        print("I am client. My request for sustained connection failed.")

    message = receiveneighborData(needy)
    message = receiveneighborData(needy)
    
    needyMessage = "Send me your blockchain please."
    sendneighborData(needyMessage)

    message = receiveneighborData(needy)
    currentBlockchain = message
    lol = convertString(currentBlockchain)
    #print(lol)
    message = receiveneighborData(needy)
    # print(message)

   ##sendneighborData("thanks for being my neighbor")

    
def main():
    # Create genesis block and admin account block
    genesis_block = generate_genesis_block()
    blockchain.append(genesis_block)

    address = ""
    blockchain.append(generate_block(blockchain[-1], address, "Create_Account", Account("admin", "admin", "a", "Admin")))
    generate_sample_blocks()

    server_program()
    
    






if __name__ == "__main__":
    main()
