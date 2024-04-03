from random import randint
import time
import tkinter as tk
from tkinter import *
from tkinter import font
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import threading
import hashlib
import requests
import re
from moralis import evm_api
import base64

"""
For IPFS upload/download:

Install Moralis Module:
    pip install moralis

Install Requests Module:
    pip install requests

"""

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
tempBlocks = []

#client tcp address array
nodes = []

# candidate_blocks handles incoming blocks for validation
candidateBlocks = []
candidateBlocksLock = threading.Lock()

# keep up with all uploaded IPFS hashes and file names
ipfsHashes = []
fileNames = []

# announcements broadcasts winning validator to all nodes
# hi this is caleb. this list isn't called anywhere but idk the plan for it so
# i'm leaving it in
announcements = []

validatorLock = threading.Lock()

# validators keeps track of open validators and balances
# validators = {}
validators = []

# keep track of current validator
validator = Validator(0, Account("", "", "?", ""))

# use flag to stop threading
stopThreads = False

# key for ipfs upload
apiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImE0NmE4MmFjLWJlYjEtNGM4MC05MjIwLTIxZDFlNGQ3MGM1NyIsIm9yZ0lkIjoiMzU5ODUyIiwidXNlcklkIjoiMzY5ODMwIiwidHlwZUlkIjoiNTY2M2MwZjAtMmM3Mi00N2YxLWJkMDktNTM1M2RmYmZhNjhhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE2OTY0NDQ5MTgsImV4cCI6NDg1MjIwNDkxOH0.kW9jP_Y_2JA70nCkUaBQMW329kQK6vuyHIfFNym0SNs"

# constants for UI bg colors:
loginBG = "#32a852"
adminBG = "#ff695e"
genericBG = "#ffb45e"
accountBG = "#a09eff"
downloadBG = "#615eff"

def calculateHash(s):  # Added this function
    h = hashlib.sha256()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

def isBlockValid(newBlock, oldBlock):
    if oldBlock.index + 1 != newBlock.index:
        return False

    if oldBlock.hash != newBlock.prevHash:
        return False

    if newBlock.calculate_block_hash() != newBlock.hash:
        return False

    return True

def createRootWindow():
    root = tk.Tk()
    root.geometry("800x500")
    root.title("Blockchain Desktop")
    root.resizable(False, False)
    return root

# create root window
root = createRootWindow()

# for validating index num:
def checkNum(newVal):
    return re.match('^[0-9]*$', newVal) is not None and len(newVal) <= 3
checkNumWrapper = (root.register(checkNum), '%P')

def onClosing():
    global stopThreads

    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if (validator.role != "?"):
            logout(root)
        stopThreads = True
        root.destroy()

def getDimensions(root):
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    return w, h

def createLoginScene(root):    
    loginScene = Frame(root, bg=loginBG, name='loginScene')
    w, h = getDimensions(root)

    # main label at top center
    loginLabel = Label(loginScene, text="Login Page", font=font.Font(size=20))
    loginLabel.place(anchor="c", relx=.5, rely=.05)

    # username label & entry box
    usernameInput = StringVar()
    usernameLabel = Label(loginScene, text="Username:", font=('Arial', 12))
    usernameLabel.place(anchor="c", rely=.4, relx=.35)
    usernameEntryBox = Entry(loginScene, textvariable=usernameInput, font=('Arial', 12))
    usernameEntryBox.place(anchor="c", rely=.4, relx=.55)

    # password label & entry box
    passwordInput = StringVar()
    passwordLabel = Label(loginScene, text="Password:", font=("Arial", 12))
    passwordLabel.place(anchor="c", rely=.5, relx=.35)
    passwordEntryBox = Entry(loginScene, textvariable=passwordInput, font=('Arial', 12), show='*')
    passwordEntryBox.place(anchor="c", rely=.5, relx=.55)

    # login button
    loginButton = Button(loginScene, text="Login", name="loginButton", command=lambda: login(usernameInput.get(), passwordInput.get(), root))
    loginButton.place(anchor="c", relx=.5, rely=.75)

    # status label
    statusLabel = Label(loginScene, text="", name="statusLabel", font=('Arial', 14), fg="red", bg=loginBG)
    statusLabel.place(anchor="c", relx=.5, rely=.6)

    loginScene.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return loginScene

def createAdminMenu(root):
    adminPage = Frame(root, bg=adminBG, name='adminMenu')
    w, h = getDimensions(root)

    # main label at top center
    adminLabel = Label(adminPage, text="Admin Menu", font=font.Font(size=20))
    adminLabel.place(anchor="c", relx=.5, rely=.05)

    # name label under main label
    nameLabel = Label(adminPage, name='nameLabel', text=f"Welcome, {validator.fullLegalName}", font=('Arial', 10))
    nameLabel.place(anchor="c", relx=.5, rely=.15)

    # create account button
    createAccountButton = Button(adminPage, text="Create Account", name="createAccountButton")
    createAccountButton.place(anchor="c", relx=.5, rely=.45)

    # view blockchain button
    viewBlockchainButton = Button(adminPage, text="View Blockchain", name="viewBlockchainButton")
    viewBlockchainButton.place(anchor="c", relx=.5, rely=.55)

    # logout button
    logoutButton = Button(adminPage, text="Logout", name="logoutButton", command=lambda: logout(root))
    logoutButton.place(anchor="c", relx=.5, rely=.75)

    adminPage.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return adminPage

def createGenericMenu(root):
    genericMenu = Frame(root, bg=genericBG, name='genericMenu')
    w, h = getDimensions(root)

    # main label at top center
    genericLabel = Label(genericMenu, text="User Menu", font=font.Font(size=20))
    genericLabel.place(anchor="c", relx=.5, rely=.05)

    # name label under main label
    nameLabel = Label(genericMenu, name='nameLabel', text=f"Welcome, {validator.fullLegalName}", font=('Arial', 10))
    nameLabel.place(anchor="c", relx=.5, rely=.15)

    # create upload button
    uploadButton = Button(genericMenu, text="Upload File", name="uploadButton", command=lambda: uploadIPFS(root))
    uploadButton.place(anchor="c", relx=.5, rely=.4)

    # create download button
    downloadButton = Button(genericMenu, text="Download File", name="downloadButton")
    downloadButton.place(anchor="c", relx=.5, rely=.55)

    # create upload status label
    statusLabel = Label(genericMenu, name="statusLabel", text="", font=('Arial', 12), fg="red", bg=genericBG)
    statusLabel.place(anchor='c', relx=.5, rely=.455)

    # logout button
    logoutButton = Button(genericMenu, text="Logout", name="logoutButton")
    logoutButton.place(anchor="c", relx=.5, rely=.75)

    genericMenu.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return genericMenu

def createCreateAccountMenu(root):
    createAccountMenu = Frame(root, bg=accountBG, name='createAccountMenu')
    w, h = getDimensions(root)

    # main label at top center
    createAccountLabel = Label(createAccountMenu, text="Create New Account", font=font.Font(size=20))
    createAccountLabel.place(anchor="c", relx=.5, rely=.05)

    # username label & entry box
    usernameInput = StringVar()
    usernameLabel = Label(createAccountMenu, text="Username:", font=('Arial', 12))
    usernameLabel.place(anchor="c", rely=.3, relx=.35)
    usernameEntryBox = Entry(createAccountMenu, textvariable=usernameInput, font=('Arial', 12))
    usernameEntryBox.place(anchor="c", rely=.3, relx=.55)

    # password label & entry box
    passwordInput = StringVar()
    passwordLabel = Label(createAccountMenu, text="Password:", font=("Arial", 12))
    passwordLabel.place(anchor="c", rely=.4, relx=.35)
    passwordEntryBox = Entry(createAccountMenu, textvariable=passwordInput, font=('Arial', 12))
    passwordEntryBox.place(anchor="c", rely=.4, relx=.55)

    # full name label & entry box
    fullNameInput = StringVar()
    fullNameLabel = Label(createAccountMenu, text="Full Name:", font=("Arial", 12))
    fullNameLabel.place(anchor="c", rely=.5, relx=.35)
    fullNameEntryBox = Entry(createAccountMenu, textvariable=fullNameInput, font=('Arial', 12))
    fullNameEntryBox.place(anchor="c", rely=.5, relx=.55)

    # role label & dropdown
    roleLabel = Label(createAccountMenu, text="Role:", font=('Arial', 12))
    roleLabel.place(anchor="c", rely=.6, relx=.35)
    roleCombobox = ttk.Combobox(createAccountMenu, name="roleCombobox", state="readonly", values=["Admin", "Doctor", "Patient"], font=('Arial', 12))
    roleCombobox.place(anchor="c", rely=.6, relx=.55)

    # account creation status label
    statusLabel = Label(createAccountMenu, text="", name="statusLabel", font=('Arial', 14), fg='blue', bg=accountBG)
    statusLabel.place(anchor="c", relx=.5, rely=.675)

    # create account button
    createAccountButton = Button(createAccountMenu, name="createAccountButton", text="Create Account", command=lambda: createAccount(usernameEntryBox.get(), passwordEntryBox.get(), fullNameEntryBox.get(), roleCombobox.get(), root))
    createAccountButton.place(anchor="c", relx=.6, rely=.8)

    # back button
    backButton = Button(createAccountMenu, name="backButton", text="Back", command=lambda: switchScenes(root.children["createAccountMenu"], root.children["adminMenu"]))
    backButton.place(anchor="c", relx=.4, rely=.8)

    createAccountMenu.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return createAccountMenu

def createDownloadMenu(root):
    downloadMenu = Frame(root, bg=downloadBG, name='downloadMenu')
    w, h = getDimensions(root)

    # main label at top center
    downloadLabel = Label(downloadMenu, text="Download File", font=font.Font(size=20))
    downloadLabel.place(anchor="c", relx=.5, rely=.05)

    # file name label & dropdown
    fileNameLabel = Label(downloadMenu, text="Desired File:", font=('Arial', 12))
    fileNameLabel.place(anchor="c", rely=.45, relx=.35)
    fileCombobox = ttk.Combobox(downloadMenu, name="fileCombobox", state="readonly", values=fileNames, font=('Arial', 12))
    fileCombobox.place(anchor="c", rely=.45, relx=.55)

    # download status label
    statusLabel = Label(downloadMenu, name="statusLabel", text="", fg='yellow', bg=downloadBG, font=('Arial', 12))
    statusLabel.place(anchor='c', relx=.5, rely=.525)

    # download button
    downloadButton = Button(downloadMenu, name="downloadButton", text="Download File", command=lambda: downloadIPFS(fileCombobox.current(), root))
    downloadButton.place(anchor="c", relx=.6, rely=.8)

    # back button
    backButton = Button(downloadMenu, name="backButton", text="Back", command=lambda: switchScenes(root.children["downloadMenu"], root.children["genericMenu"]))
    backButton.place(anchor="c", relx=.4, rely=.8)

    downloadMenu.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return downloadMenu    

def createBlockchainMenu(root):
    blockchainScene = Frame(root, bg=accountBG, name='blockchainScene')
    w, h = getDimensions(root)

    # main label at top center
    blockchainLabel = Label(blockchainScene, text="View Blockchain", font=font.Font(size=20))
    blockchainLabel.place(anchor="c", relx=.5, rely=.05)

    # max index label
    maxIndexLabel = Label(blockchainScene, name="maxIndexLabel", text="Max Index: ", font=('Arial', 12))
    maxIndexLabel.place(anchor="c", relx=.5, rely=.4)

    # index label & entry box:
    indexInput = StringVar()
    indexLabel = Label(blockchainScene, text="Block Index:", font=('Arial', 12))
    indexLabel.place(anchor="c", rely=.5, relx=.465)
    indexEntryBox = Entry(blockchainScene, textvariable=indexInput, font=('Arial', 12), width=4, validate='key', validatecommand=checkNumWrapper)
    indexEntryBox.place(anchor="c", rely=.5, relx=.55)

    # view block button
    viewBlockButton = Button(blockchainScene, text="View Block", name="viewBlockButton", command=lambda: spawnBlock(root, indexInput.get()))
    viewBlockButton.place(anchor="c", relx=.5, rely=.65)

    # back button
    backButton = Button(blockchainScene, text="Back", name="backButton", command=lambda: switchScenes(root.children["blockchainScene"], root.children["adminMenu"]))
    backButton.place(anchor="c", relx=.5, rely=.75)

    blockchainScene.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return blockchainScene

def updateName(root):
    root.children["genericMenu"].children["nameLabel"].configure(text=f"Welcome, {validator.fullLegalName}")
    root.children["adminMenu"].children["nameLabel"].configure(text=f"Welcome, {validator.fullLegalName}")

def handleDownloadButton(root):
    getFileList()
    root.children["downloadMenu"].children["fileCombobox"].configure(values=fileNames)
    switchScenes(root.children["genericMenu"], root.children["downloadMenu"])

def setScenes():
    loginScene = createLoginScene(root)
    adminScene = createAdminMenu(root)
    createAccountScene = createCreateAccountMenu(root)
    blockchainScene = createBlockchainMenu(root)
    genericScene = createGenericMenu(root)
    downloadMenu = createDownloadMenu(root)

    #adminScene.children["logoutButton"].configure(command=lambda: logout(root))
    adminScene.children["createAccountButton"].configure(command=lambda: switchScenes(adminScene, createAccountScene))
    adminScene.children["viewBlockchainButton"].configure(command=lambda: viewBlockchain(root))
    
    genericScene.children["logoutButton"].configure(command=lambda: logout(root))
    genericScene.children["downloadButton"].configure(command=lambda: handleDownloadButton(root))

    for child in root.children.values():
        hideScene(child)

    root.protocol("WM_DELETE_WINDOW", onClosing)
    showScene(loginScene)
    return root

def showScene(scene):
    for child in scene.children.values():
        if type(child) == tk.Button:
            child.configure(state=NORMAL)
    scene.tkraise()

def hideScene(scene):
    for child in scene.children.values():
        if type(child) == tk.Button:
            child.configure(state=DISABLED)
        if type(child) == tk.Entry:
            child.delete(0, 'end')
        if type(child) == ttk.Combobox:
            child.set('')
    
    for child in scene.children.keys():
        if child == "statusLabel":
            scene.children[child].configure(text="")

def switchScenes(prevScene, nextScene):
    hideScene(prevScene)
    showScene(nextScene)

# generate_genesis_block creates the genesis block
def generateGenesisBlock():
    t = str(datetime.now())
    genesis_block = Block(0, t, "", "", "Genesis", 0)
    return genesis_block

# generate_block creates a new block using the previous block's hash
def generateBlock(oldBlock, address, transactionType, payload):
    t = str(datetime.now())
    new_block = Block(oldBlock.index + 1, t, oldBlock.hash, address, transactionType, payload)
    return new_block

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
    genesis_block = generateGenesisBlock()
    blockchain.append(genesis_block)
    address = ""
    blockchain.append(generateBlock(blockchain[-1], address, "Create_Account", Account("admin", "admin", "a", "Admin")))
    # generateSampleBlocks()

def login(username, password, root):
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
        root.children["loginScene"].children["statusLabel"].configure(text="Incorrect login.")
        return validLogin, account
    
    if account.role == "a":
        print("Successful login for admin.\n")
        #root.children["adminMenu"].tkraise()
        switchScenes(root.children["loginScene"], root.children["adminMenu"])
    elif account.role == "d":
        print("Successful login for doctor.\n")
        #root.children["genericMenu"].tkraise()
        switchScenes(root.children["loginScene"], root.children["genericMenu"])
    else:
        print("Successful login for patient.\n")
        #root.children["genericMenu"].tkraise()
        switchScenes(root.children["loginScene"], root.children["genericMenu"])

    validator = createValidator(account)
    updateName(root)
    print("Validator created.")
    return validLogin, account

def logout(root):
    global validator
    if validator in validators:
        validators.remove(validator)
    if validator.role == "a":
        switchScenes(root.children["adminMenu"], root.children["loginScene"])
    else:
        switchScenes(root.children["genericMenu"], root.children["loginScene"])

def createValidator(currentAccount):
    #Randomly stakes coins to prevent a favored node
    balance = randint(1,100)

    newValidator = Validator(balance, currentAccount)

    with validatorLock:
        validators.append(newValidator)
        for validator in validators:
            print(f"{validator.address} : {validator.balance}")             

    return newValidator

def createAccount(username, password, name, roleSelection, root):
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

    root.children["createAccountMenu"].children["statusLabel"].configure(text=f"{newAccount.fullLegalName}'s account successfully created!")

    return newAccount

def viewBlockchain(root):
    root.children["blockchainScene"].children["maxIndexLabel"].configure(text=f"Max Index: {blockchain[-1].index}")
    switchScenes(root.children["adminMenu"], root.children["blockchainScene"])

def spawnBlock(root, blockIndex):
    notValid = True     # validity flag to break loop
    try:
        blockIndex = int(blockIndex)                        # try to convert to int; if not int, go to exception
        if blockIndex >= 0 and blockIndex <= blockchain[-1].index:                      # make sure choice is in range
            notValid = False
        else:                                               # if input is out of range:
            return
    except ValueError:                                      # if input is not an int:
        return

    currentBlock = blockchain[blockIndex]
    if currentBlock.transactionType == "Genesis":
        labelText = (f"Index: {currentBlock.index}\n"
                     f"Timestamp: {currentBlock.timestamp}\n"
                     f"Type: {currentBlock.transactionType}")
    elif currentBlock.transactionType != "Create_Account":
        labelText = (f"Index: {currentBlock.index}\n"
                     f"Timestamp: {currentBlock.timestamp}\n"
                     f"Type: {currentBlock.transactionType}\n"
                     f"Previous_Hash: {currentBlock.prevHash}\n"
                     f"Validator: {currentBlock.validatorName}\n"
                     f"Type: {currentBlock.transactionType}\n"
                     f"IPFS_Hash: {currentBlock.payload.ipfsHash}\n"
                     f"File_Name: {currentBlock.payload.fileName}")
    else:
        labelText = (f"Index: {currentBlock.index}\n"
                     f"Timestamp: {currentBlock.timestamp}\n"
                     f"Type: {currentBlock.transactionType}\n"
                     f"Previous_Hash: {currentBlock.prevHash}\n"
                     f"Validator: {currentBlock.validatorName}\n"
                     f"Type: {currentBlock.transactionType}\n"
                     f"Username: {currentBlock.payload.username}\n"
                     f"Password: {currentBlock.payload.password}\n"
                     f"Role: {currentBlock.payload.role}")
    
    popUp = Toplevel(root)
    popUp.geometry = "400x400"
    popUp.title = f"Block #{str(blockIndex)}"
    blockLabel = Label(popUp, text=labelText, font=('Arial', 12), name="blockLabel", justify=LEFT)
    blockLabel.pack(pady=20, side=TOP, anchor="w")

def uploadIPFS(root):
    # open dialog box to choose file
    root.filename = filedialog.askopenfilename(title="Select A File", filetypes=(("All Files", "*.*"), ("PNGs", "*.png"), ("Text Files", "*.txt"), ("PDFs", "*.pdf")))
    
    # if 'cancel' was selected on dialog box:
    if len(root.filename) == 0:
        return
    
    # get file 
    fileName = root.filename
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
        root.children["genericMenu"].children["statusLabel"].configure(text=f"A file named {fileName} already exists!", fg="red")
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
    root.children["genericMenu"].children["statusLabel"].configure(text=f"{fileName} added successfully.", fg="green")

    return newFileData

def downloadIPFS(fileIndex, root):#def retrieveIpfs(conn, symmetricKey):
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

    root.children["downloadMenu"].children["statusLabel"].configure(text=f"{fileName} downloaded successfully.")

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
    with validatorLock:
        oldLastIndex = blockchain[-1]
    newBlock = generateBlock(oldLastIndex, validator.address, transactionType, payload)

    if isBlockValid(newBlock, oldLastIndex):
        candidateBlocks.append(newBlock)

# pickWinner creates a lottery pool of validators and chooses the validator who gets to forge a block to the blockchain
def pickWinner():
    print("\nPicking winner...")
    while stopThreads == False:
        time.sleep(0.15) # .15 second refresh
        with validatorLock:    
            if len(validators) > 0:
                lottery_winner = getLotteryWinner().address
                for block in candidateBlocks:
                    if block.validatorName == lottery_winner:
                        # make sure candidate index isn't duplicated in existing blockchain (avoid forking):
                        indexes = []
                        for approved_block in blockchain:
                            indexes.append(approved_block.index)
                        if block.index in indexes:
                            new_block = generateBlock(blockchain[-1], block.validatorName, block.transactionType, block.payload)
                            blockchain.append(new_block)
                        else:
                            blockchain.append(block)
                        candidateBlocks.remove(block)
                        printBlockchain()
                        break

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
            if block.transactionType != "Create_Account":
                print("IPFS Hash: " + block.payload.ipfsHash)
                print("File Name: " + block.payload.fileName)
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

def main():
    createFirstBlocks()
    getFileList()
    
    for name in fileNames:
        print(name)

    # Handle candidate blocks in a separate thread
    candidateThread = threading.Thread(target=lambda: candidateBlocks.append(None) if candidateBlocks else None)
    candidateThread.start()

    # Pick winner thread
    winnerThread = threading.Thread(target=pickWinner)
    winnerThread.start()

    root = setScenes()
    root.mainloop()

if __name__ == "__main__":
    main()
