#To run server: python3 posTnet.py
#To run client: nc <ip addr> <port#>


import hashlib
import socket
import time
import threading
import os
#import requests
from random import randint
from datetime import datetime
from queue import Queue
from moralis import evm_api
import requests
import base64

#import netifaces as ni

#T here, import these to use the encryption
#import asymmetricEncryption as AE
#import symmetricEncryption as SE
#import rsa

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
    #blockchain.append(generate_block(blockchain[-1], address, "Upload", FileData("QmYRJY3Uq8skTrREx7aFkE7Ym7hXA6bk5pqJE9gWrhFB6n", "Project Timeline.pdf", "Genesis", accessList)))


#Need to change to password hash, and way to keep the salt safe
#Need to save username and password
def login(username, password, localBlockchain):
    for block in localBlockchain:
        if block.transactionType == "Create_Account":
            if block.payload.username == username:
                if block.payload.password == password:
                    return True
    return  False

apiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImE0NmE4MmFjLWJlYjEtNGM4MC05MjIwLTIxZDFlNGQ3MGM1NyIsIm9yZ0lkIjoiMzU5ODUyIiwidXNlcklkIjoiMzY5ODMwIiwidHlwZUlkIjoiNTY2M2MwZjAtMmM3Mi00N2YxLWJkMDktNTM1M2RmYmZhNjhhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE2OTY0NDQ5MTgsImV4cCI6NDg1MjIwNDkxOH0.kW9jP_Y_2JA70nCkUaBQMW329kQK6vuyHIfFNym0SNs"

def uploadIpfs(author, fileName, localBlockchain, fileContent, FILENAME):#def uploadIpfs(conn, symmetricKey):

    try:
        #Might need to save a copy of the uploaded file to the UploadedFile lists
        #T, here. Copy the file and make the nzew one encrypted.
        #Then, upload the encrypted file
        #Then, delete the encrypted file
        """
        #Gets the location of the current working directory
        tempFilePath = os.getcwd() + "/.tmp"
        tempFilename = fileName.split('/')[-1]     #Gets the name of the file
        encryptedFileLocation = tempFilePath + "/" + tempFilename
        #Make sure the file exists and that it is hidden
        if not os.path.exists(tempFilePath):
            os.mkdir(tempFilePath)      #Makes the directory
            os.system(f'attrib +h "{tempFilePath}"')        #Makes it hidden
        #T here, use the symmetric key to copy and encrypt the file before sending it on
        SE.encryptFile(symmetricKey, fileName, encryptedFileLocation)
        #In the command line, replace fileName[1:-3] with encryptedFileLocation
        """
        #Converts the file data to base-64 encoded text
        convertedData = base64.b64encode(fileContent)
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
        
        hash = parsedPath[4]            # cleans up the hash and the file name
        ipfsHashes.append(hash)        # update the hash and file lists
        fileNames.append(fileName)

        #Deletes the temorary upload file
        #os.remove(encryptedFileLocation)

        accessList = []
        newFileData = FileData(hash, fileName, author, accessList)
        #addToCandidateBlocks("Upload", newFileData)

        newBlock = generateBlock(blockchain[-1], author, "Upload", newFileData)

        if isBlockValid(newBlock, blockchain[-1]):
            blockchain.append(newBlock)
        return blockchain
    except:
        return None


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

def retrieveIpfs(localBlockchain, ifpsHash):#def retrieveIpfs(conn, symmetricKey):
    url = "https://ipfs.moralis.io:2053/ipfs/" + ifpsHash + "/uploaded_file"	#does the url to retrieve the file from IPFS
    r = requests.get(url, allow_redirects=True)

    #T here, Use symmetric key to decrypt the file, r.content
    #This function opens the first file, reads the dencrypted data, closes the file
    #Ten opens the second file, clears it, writes all decrypted data to it, then closes the file
    #SE.decryptFile(symmetricKey, file_name, file_name)

    return r.content

def refreshBlockchain():
    #Connect with the other nodes and get the most recent version of the blockchain

    #Returns the newest version of the blockchain
    return blockchain

#Function to loop through the given blockchain and pull out the file names
def getFileList(localBlockchain):
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
def createNewAccount(username, password, role, LegalName, localBlockchain):
    #Loops through the blockchain and if an account has the same username, returns False
    for block in localBlockchain:
        if block.transactionType == "Create_Account" and block.payload.username == username:
            return False
    #Else, the same username does not exist, so create the block
    blockchain.append(generate_block(blockchain[-1], "", "Create_Account", Account(username, password, role, LegalName)))
    return True

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

def createAccount(username, password, role, LegalName):
    newAccount = Account(username, password, role, LegalName)
    return newAccount

def calculate_hash(s):  # Added this function
    h = hashlib.sha256()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

#T here, 
#Function that is guaranteed to generate the keys
def genKeys():
    #If both files exist, load the public and private keys
    if os.path.exists("publicKey.pem") and os.path.exists("privateKey.pem"):
        #Tries to load the keys, but if something goes wrong, generate new keys and save them
        try:
            print("Loading asymmetric keys...")
            privateKey = AE.loadPrivateKey("publicKey.pem")
            publicKey = AE.loadPublicKey("privateKey.pem")
            print("Keys loaded")
        #Catches any issue with key loading
        except:
            print("Key loading failed, generating new assymetric keys...")
            #Generates the pubic and private keys
            publicKey, privateKey = AE.generateKey(4096)
            AE.savePrivateKey(privateKey, "publicKey.pem")
            AE.savePublicKey(publicKey, "privateKey.pem")
            print("Keys generated")
    #Else, the files do not exist, so generate a new set of keys
    else:
        #Generates the pubic and private keys
        print("Generating new assymetric keys...")
        publicKey, privateKey = AE.generateKey(4096)
        #Save the new keys
        AE.savePrivateKey(privateKey, "publicKey.pem")
        AE.savePublicKey(publicKey, "privateKey.pem")
        print("Keys generated")
    
    #If the symmetric key file exists, load the key
    if os.path.exists("symmetricKey.pem"):
        #Tries to load the symmetric key, but if something goes wrong, generate a new key and save it
        try:
            print("Loading symmetric key...")
            privateKey = SE.loadKey("symmetricKey.pem")
            print("Key loaded")
        #Catches any issue with key loading
        except:
            print("Key loading failed, generating new symmetric key...")
            #Generates the pubic and private keys
            symmetricKey = SE.generateAES256Key()
            #Saves the new key
            SE.saveKey(symmetricKey, "symmetricKey.pem")
            print("Key generated")
    #Else, the files do not exist, so generate a new set of keys
    else:
        #Generates the symmetric key
        print("Generating new symmetric key...")
        symmetricKey = SE.generateAES256Key()
        SE.saveKey(symmetricKey, "symmetricKey.pem")
        print("Key generated")

    return publicKey, privateKey, symmetricKey

def main():
    # Create genesis block and admin account block
    genesis_block = generate_genesis_block()
    blockchain.append(genesis_block)
    generate_sample_blocks()
    address = ""
    blockchain.append(generate_block(blockchain[-1], address, "Create_Account", Account("admin", "admin", "a", "Admin")))
    blockchain.append(generate_block(blockchain[-1], address, "Create_Account", Account("root", "root", "p", "Myself")))
    blockchain.append(generate_block(blockchain[-1], address, "Create_Account", Account("sampleUser", "root", "p", "I")))
    return blockchain

if __name__ == "__main__":
    main()



#
#T here,
#Need a way to get the keys from the client and the server
#So, when the client connects, the server should validate the client, then send the symmetric key
#Would require a new condition in the main server while loop that when a client connects, the client is validated and gets the key
#Would also require a corresponding section of code in the client so the client requests the key when first joining the blockchain
#Might need to happen in client.py or server.py under autotcp
#Also, might need to convert the formatting potentially from base 64 to utf-8
#If decoding is needed, just send the encrypted data over the wire and then decrypt it from utf-8
#
