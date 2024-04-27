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

# for file encryption
from cryptography.fernet import Fernet, InvalidToken

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

validatorLock = threading.Lock()

# validators keeps track of open validators and balances
# validators = {}
validators = []

# keep track of current validator
validator = Validator(0, Account("", "", "?", ""))
GUIAccount = Account("", "", "?", "")

# use flag to stop threading
stopThreads = False

# key for ipfs upload
apiKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImE0NmE4MmFjLWJlYjEtNGM4MC05MjIwLTIxZDFlNGQ3MGM1NyIsIm9yZ0lkIjoiMzU5ODUyIiwidXNlcklkIjoiMzY5ODMwIiwidHlwZUlkIjoiNTY2M2MwZjAtMmM3Mi00N2YxLWJkMDktNTM1M2RmYmZhNjhhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE2OTY0NDQ5MTgsImV4cCI6NDg1MjIwNDkxOH0.kW9jP_Y_2JA70nCkUaBQMW329kQK6vuyHIfFNym0SNs"

# constants for UI bg colors:
creamColor = "#f6f0ea"
buttonColor = "#831eff"

loginBG = creamColor
adminBG = "#ff695e"
genericBG = "#ffb45e"
accountBG = "#a09eff"
downloadBG = "#615eff"

isLoggedIn = False

# store the IP to connect to
connectIP = ""
hasInputtedIP = False

accountNames = []

accounts = []
patientNames = []
allFiles = []

#*****************************************************************
# for encryption
# key was generated and is hard coded so all nodes can decode the files
# replace here if devleop support for varying keys! :)

fileKey = 'yrnX6PYjWcITai_1Ux6IC1rXlCP7y1TiPC8dcxTi7os='
fernet = Fernet(fileKey)

#*****************************************************************

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
    # print("Creating root window!")
    root = tk.Tk()
    root.geometry("800x500")
    root.title("Blockchain Desktop")
    root.resizable(False, False)
    return root

# # create root window
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

def createWelcomeScene(root):
    welcomeScene = Frame(root, bg=creamColor, name='welcomeScene')
    w, h = getDimensions(root)

    # main label at top center
    welocmeLabel = Label(welcomeScene, bg=creamColor, text="Welcome!", font=font.Font(size=20))
    welocmeLabel.place(anchor="c", relx=.5, rely=.05)

    # username label & entry box
    ipInput = StringVar()
    ipLabel = Label(welcomeScene, text="IP:", font=('Arial', 12))
    ipLabel.place(anchor="c", rely=.4, relx=.35)
    ipEntryBox = Entry(welcomeScene, textvariable=ipInput, font=('Arial', 12))
    ipEntryBox.place(anchor="c", rely=.4, relx=.55)

    # IP connect button
    connectButton = Button(welcomeScene, fg='white', bg=buttonColor, text="Connect", name="connectButton", command=lambda: getIP(ipInput.get(), root))
    connectButton.place(anchor="c", relx=.5, rely=.75)

    # status label
    statusLabel = Label(welcomeScene, text="", name="statusLabel", font=('Arial', 14), fg="red", bg=creamColor)
    statusLabel.place(anchor="c", relx=.5, rely=.6)

    welcomeScene.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return welcomeScene

def createLoginScene(root):    
    loginScene = Frame(root, bg=creamColor, name='loginScene')
    w, h = getDimensions(root)

    # main label at top center
    loginLabel = Label(loginScene, bg=creamColor, text="Login Page", font=font.Font(size=20))
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
    loginButton = Button(loginScene, fg='white', bg=buttonColor, text="Login", name="loginButton", command=lambda: login(usernameInput.get(), passwordInput.get(), root))
    loginButton.place(anchor="c", relx=.5, rely=.75)

    # status label
    statusLabel = Label(loginScene, text="", name="statusLabel", font=('Arial', 14), fg="red", bg=creamColor)
    statusLabel.place(anchor="c", relx=.5, rely=.6)

    # ip label
    ipLabel = Label(loginScene, text="", name="ipLabel", font=('Arial', 12))
    ipLabel.place(anchor="c", relx=.5, rely=.15)

    loginScene.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return loginScene

def createAdminMenu(root):
    adminPage = Frame(root, bg=creamColor, name='adminMenu')
    w, h = getDimensions(root)

    # main label at top center
    adminLabel = Label(adminPage, bg=creamColor, text="Admin Menu", font=font.Font(size=20))
    adminLabel.place(anchor="c", relx=.5, rely=.05)

    # name label under main label
    nameLabel = Label(adminPage, name='nameLabel', text=f"Welcome, {validator.fullLegalName}", font=('Arial', 10))
    nameLabel.place(anchor="c", relx=.5, rely=.15)

    # create account button
    createAccountButton = Button(adminPage, fg='white', bg=buttonColor, text="Create Account", name="createAccountButton")
    createAccountButton.place(anchor="c", relx=.5, rely=.375)

    # change role button
    changeRoleButton = Button(adminPage, fg='white', bg=buttonColor, text="Change Account Roles", name="changeRoleButton", command=lambda: switchToRoleChange())
    changeRoleButton.place(anchor="c", relx=.5, rely=.45)

    # view blockchain button
    viewBlockchainButton = Button(adminPage, fg='white', bg=buttonColor, text="View Blockchain", name="viewBlockchainButton")
    viewBlockchainButton.place(anchor="c", relx=.5, rely=.525)

    # view account names button
    viewAccountNamesButton = Button(adminPage, fg='white', bg=buttonColor, text="View Account Names", name="viewAccountNamesButton", command=lambda: handleListAccountsButton(root))
    viewAccountNamesButton.place(anchor="c", relx=.5, rely=.6)

    # logout button
    logoutButton = Button(adminPage, fg='white', bg=buttonColor, text="Logout", name="logoutButton", command=lambda: logout(root))
    logoutButton.place(anchor="c", relx=.5, rely=.75)

    # ip label
    ipLabel = Label(adminPage, text="", name="ipLabel", font=('Arial', 12))
    ipLabel.place(anchor="c", relx=.5, rely=.15)

    adminPage.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return adminPage

def createGenericMenu(root):
    genericMenu = Frame(root, bg=creamColor, name='genericMenu')
    w, h = getDimensions(root)

    # main label at top center
    genericLabel = Label(genericMenu, bg=creamColor, text="User Menu", font=font.Font(size=20))
    genericLabel.place(anchor="c", relx=.5, rely=.05)

    # name label under main label
    nameLabel = Label(genericMenu, name='nameLabel', text=f"Welcome, {validator.fullLegalName}", font=('Arial', 10))
    nameLabel.place(anchor="c", relx=.5, rely=.15)

    # create upload button
    uploadButton = Button(genericMenu, fg='white', bg=buttonColor, text="Upload File", name="uploadButton", command=lambda: handleUploadButton(root))
    uploadButton.place(anchor="c", relx=.5, rely=.4)

    # create download button
    downloadButton = Button(genericMenu, fg='white', bg=buttonColor, text="Download File", name="downloadButton")
    downloadButton.place(anchor="c", relx=.5, rely=.55)

    # create upload status label
    statusLabel = Label(genericMenu, name="statusLabel", text="", font=('Arial', 12), fg="red", bg=creamColor)
    statusLabel.place(anchor='c', relx=.5, rely=.455)

    # logout button
    logoutButton = Button(genericMenu, fg='white', bg=buttonColor, text="Logout", name="logoutButton")
    logoutButton.place(anchor="c", relx=.5, rely=.75)

    # ip label
    ipLabel = Label(genericMenu, text="", name="ipLabel", font=('Arial', 12))
    ipLabel.place(anchor="c", relx=.5, rely=.15)

    genericMenu.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return genericMenu

def createCreateAccountMenu(root):
    createAccountMenu = Frame(root, bg=creamColor, name='createAccountMenu')
    w, h = getDimensions(root)

    # main label at top center
    createAccountLabel = Label(createAccountMenu, bg=creamColor, text="Create New Account", font=font.Font(size=20))
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
    statusLabel = Label(createAccountMenu, text="", name="statusLabel", font=('Arial', 14), fg='blue', bg=creamColor)
    statusLabel.place(anchor="c", relx=.5, rely=.675)

    # create account button
    createAccountButton = Button(createAccountMenu, fg='white', bg=buttonColor, name="createAccountButton", text="Create Account", command=lambda: createAccount(usernameEntryBox.get(), passwordEntryBox.get(), fullNameEntryBox.get(), roleCombobox.get(), root))
    createAccountButton.place(anchor="c", relx=.6, rely=.8)

    # back button
    backButton = Button(createAccountMenu, fg='white', bg=buttonColor, name="backButton", text="Back", command=lambda: switchScenes(root.children["createAccountMenu"], root.children["adminMenu"]))
    backButton.place(anchor="c", relx=.4, rely=.8)

    createAccountMenu.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return createAccountMenu

def createRoleMenu(root):
    roleMenu = Frame(root, bg=creamColor, name='roleMenu')
    w, h = getDimensions(root)

    # main label at top center
    roleLabel = Label(roleMenu, bg=creamColor, text="Change Account Roles", font=font.Font(size=20))
    roleLabel.place(anchor="c", relx=.5, rely=.05)

    # account name label & dropdown
    accountNameLabel = Label(roleMenu, text="Account to Change:", font=('Arial', 12))
    accountNameLabel.place(anchor="c", rely=.35, relx=.325)
    accountCombobox = ttk.Combobox(roleMenu, name="accountCombobox", state="readonly", values=accountNames, font=('Arial', 12))
    accountCombobox.place(anchor="c", rely=.35, relx=.55)

    # role label & dropdown
    roleLabel = Label(roleMenu, text="New Role:", font=('Arial', 12))
    roleLabel.place(anchor="c", rely=.45, relx=.35)
    roleCombobox = ttk.Combobox(roleMenu, name="roleCombobox", state="readonly", values=["Admin", "Doctor", "Patient"], font=('Arial', 12))
    roleCombobox.place(anchor="c", rely=.45, relx=.55)

    # change role button
    changeRoleButton = Button(roleMenu, fg='white', bg=buttonColor, text="Change Role", name="changeRoleButton", command=lambda: handleChangeRoleButton(accountCombobox.get(), roleCombobox.get(), root))
    changeRoleButton.place(anchor="c", relx=.5, rely=.6)

    # change role status label
    statusLabel = Label(roleMenu, name="statusLabel", text="", fg='green', bg=creamColor, font=('Arial', 12))
    statusLabel.place(anchor='c', relx=.5, rely=.675)

    # back button
    backButton = Button(roleMenu, fg='white', bg=buttonColor, name="backButton", text="Back", command=lambda: switchScenes(root.children["roleMenu"], root.children["adminMenu"]))
    backButton.place(anchor="c", relx=.5, rely=.8)

    roleMenu.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return roleMenu

def createDownloadMenu(root):
    downloadMenu = Frame(root, bg=creamColor, name='downloadMenu')
    w, h = getDimensions(root)

    # main label at top center
    downloadLabel = Label(downloadMenu, bg=creamColor, text="Download File", font=font.Font(size=20))
    downloadLabel.place(anchor="c", relx=.5, rely=.05)

    # file name label & dropdown
    fileNameLabel = Label(downloadMenu, text="Desired File:", font=('Arial', 12))
    fileNameLabel.place(anchor="c", rely=.45, relx=.35)
    fileCombobox = ttk.Combobox(downloadMenu, name="fileCombobox", state="readonly", values=fileNames, font=('Arial', 12))
    fileCombobox.place(anchor="c", rely=.45, relx=.55)

    # download status label
    statusLabel = Label(downloadMenu, name="statusLabel", text="", fg='green', bg=creamColor, font=('Arial', 12))
    statusLabel.place(anchor='c', relx=.5, rely=.525)

    # download button
    downloadButton = Button(downloadMenu, fg='white', bg=buttonColor, name="downloadButton", text="Download File", command=lambda: downloadIPFS(fileCombobox.get(), root))
    downloadButton.place(anchor="c", relx=.6, rely=.8)

    # back button
    backButton = Button(downloadMenu, fg='white', bg=buttonColor, name="backButton", text="Back", command=lambda: switchScenes(root.children["downloadMenu"], root.children["genericMenu"]))
    backButton.place(anchor="c", relx=.4, rely=.8)

    downloadMenu.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return downloadMenu    


def createDoctorUploadMenu(root):
    doctorUploadMenu = Frame(root, bg=creamColor, name='doctorUploadMenu')
    w, h = getDimensions(root)

    # main label at top center
    doctorUploadLabel = Label(doctorUploadMenu, bg=creamColor, text="Upload File", font=font.Font(size=20))
    doctorUploadLabel.place(anchor="c", relx=.5, rely=.05)

    # access patient name label & dropdown
    patientNameLabel = Label(doctorUploadMenu, text="Desired Patient:", font=('Arial', 12))
    patientNameLabel.place(anchor="c", rely=.45, relx=.35)
    patientCombobox = ttk.Combobox(doctorUploadMenu, name="patientCombobox", state="readonly", values=patientNames, font=('Arial', 12))
    patientCombobox.place(anchor="c", rely=.45, relx=.55)

    # upload status label
    statusLabel = Label(doctorUploadMenu, name="statusLabel", text="", fg='green', bg=creamColor, font=('Arial', 12))
    statusLabel.place(anchor='c', relx=.5, rely=.525)

    # upload button
    uploadButton = Button(doctorUploadMenu, fg='white', bg=buttonColor, name="doctorUploadButton", text="Upload File", command=lambda: uploadIPFS(patientCombobox.get(), root))
    uploadButton.place(anchor="c", relx=.6, rely=.8)

    # back button
    backButton = Button(doctorUploadMenu, fg='white', bg=buttonColor, name="backButton", text="Back", command=lambda: switchScenes(root.children["doctorUploadMenu"], root.children["genericMenu"]))
    backButton.place(anchor="c", relx=.4, rely=.8)

    doctorUploadMenu.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return doctorUploadMenu


def createBlockchainMenu(root):
    blockchainScene = Frame(root, bg=creamColor, name='blockchainScene')
    w, h = getDimensions(root)

    # main label at top center
    blockchainLabel = Label(blockchainScene, bg=creamColor, text="View Blockchain", font=font.Font(size=20))
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
    viewBlockButton = Button(blockchainScene, fg='white', bg=buttonColor, text="View Block", name="viewBlockButton", command=lambda: spawnBlock(root, indexInput.get()))
    viewBlockButton.place(anchor="c", relx=.5, rely=.65)

    # back button
    backButton = Button(blockchainScene, fg='white', bg=buttonColor, text="Back", name="backButton", command=lambda: switchScenes(root.children["blockchainScene"], root.children["adminMenu"]))
    backButton.place(anchor="c", relx=.5, rely=.75)

    blockchainScene.place(anchor="c", relx=.5, rely=.5, width=w, height=h)
    return blockchainScene

def updateName(root):
    root.children["genericMenu"].children["nameLabel"].configure(text=f"Welcome, {validator.fullLegalName}")
    root.children["adminMenu"].children["nameLabel"].configure(text=f"Welcome, {validator.fullLegalName}")

def handleUploadButton(root):
    global patientNames

    if GUIAccount.role == "d":
        patientNames = []
        getAccounts()

        for account in accounts:
            if account.role == "p":
                patientNames.append(account.username)
        root.children["doctorUploadMenu"].children["patientCombobox"].configure(values=patientNames)
        switchScenes(root.children["genericMenu"], root.children["doctorUploadMenu"])
    else:
        uploadIPFS(GUIAccount.username, root)

def handleDownloadButton(root):
    getFileList()
    comboboxNames = []

    if GUIAccount.role == "p":
        for file in allFiles:
            if file.accessList == GUIAccount.username:
                comboboxNames.append(file.fileName)
                print(f"Appended {file.fileName}")
            else:
                print(f"{file.accessList} is not equal to {GUIAccount.username}")
        root.children["downloadMenu"].children["fileCombobox"].configure(values=comboboxNames)
    else:
        root.children["downloadMenu"].children["fileCombobox"].configure(values=fileNames)
    switchScenes(root.children["genericMenu"], root.children["downloadMenu"])

def handleListAccountsButton(root):
    #getAccountNames()
    getAccounts()

    labelText = "###########################\n\n"
    index = 1
    for name in accountNames:
        labelText += f"  {index}. {name}   \n\n"
        index += 1
    labelText += "###########################\n\n"

    popUp = Toplevel(root)
    popUp.geometry = "400x400"
    popUp.title = f"All Account Names"
    blockLabel = Label(popUp, text=labelText, font=('Arial', 12), name="accountLabel", justify=LEFT)
    blockLabel.pack(pady=20, side=TOP, anchor="w")

def handleChangeRoleButton(chosenAccount, chosenRole, root):  
    if chosenAccount == GUIAccount.username:
        root.children["roleMenu"].children["statusLabel"].configure(text=f"Cannot change your own role!", fg='red')
        return

    if chosenRole == "Admin":
        shortRole = "a"
    elif chosenRole == "Doctor":
        shortRole = "d"
    else:
        shortRole = "p"

    for account in accounts:
        if account.username == chosenAccount:
            account.role = shortRole
            changedAccount = account
            #print(f"@@@@ changed {changedAccount.username} + {changedAccount.role}\n")

    root.children["roleMenu"].children["statusLabel"].configure(text=f"{chosenAccount}'s role successfully changed to {chosenRole}!", fg='green')

    addToCandidateBlocks("Update_User", changedAccount)

def setScenes():
    # print("Creating scenes...")
    welcomeScene = createWelcomeScene(root)
    loginScene = createLoginScene(root)
    adminScene = createAdminMenu(root)
    createAccountScene = createCreateAccountMenu(root)
    changeRoleScene = createRoleMenu(root)
    blockchainScene = createBlockchainMenu(root)
    genericScene = createGenericMenu(root)
    downloadMenu = createDownloadMenu(root)
    doctorUploadMenu = createDoctorUploadMenu(root)

    #adminScene.children["logoutButton"].configure(command=lambda: logout(root))
    adminScene.children["createAccountButton"].configure(command=lambda: switchScenes(adminScene, createAccountScene))
    adminScene.children["viewBlockchainButton"].configure(command=lambda: viewBlockchain(root))
    
    genericScene.children["logoutButton"].configure(command=lambda: logout(root))
    genericScene.children["downloadButton"].configure(command=lambda: handleDownloadButton(root))

    for child in root.children.values():
        hideScene(child)

    root.protocol("WM_DELETE_WINDOW", onClosing)
    showScene(welcomeScene)
    # showScene(loginScene)
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


def switchToRoleChange():
    getAccounts()

    root.children["roleMenu"].children["accountCombobox"].configure(values=accountNames)
    switchScenes(root.children["adminMenu"], root.children["roleMenu"])

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
    accessList = "doctor"
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
    

def getIP(ipInput, root):
    global connectIP
    global hasInputtedIP
    connectIP = ipInput
    # print(f"Connect IP is {connectIP}")

    # update IP labels on all relevant scenes
    for scene in root.children.values():
        for child in scene.children.keys():
            if child == "ipLabel":
                scene.children[child].configure(text=f"Connect IP: {connectIP}")
    switchScenes(root.children["welcomeScene"], root.children["loginScene"])
    hasInputtedIP = True

def login(username, password, root):
    global validator
    global isLoggedIn
    global GUIAccount
    # print(f"Username: {username}, Password: {password}")
    accountRet = Account("false", "false", "a", "False")
    
    getAccounts()

    for account in accounts:
        if account.username == username:
            if account.password == password:
                validLogin = True
                accountRet = account

    if validLogin == False:
        # print("Bad login.\n")
        root.children["loginScene"].children["statusLabel"].configure(text="Incorrect login.")
        return validLogin, accountRet
    
    if accountRet.role == "a":
        # print("Successful login for admin.\n")
        switchScenes(root.children["loginScene"], root.children["adminMenu"])
    elif accountRet.role == "d":
        # print("Successful login for doctor.\n")
        switchScenes(root.children["loginScene"], root.children["genericMenu"])
    else:
        # print("Successful login for patient.\n")
        switchScenes(root.children["loginScene"], root.children["genericMenu"])

    GUIAccount = accountRet

    isLoggedIn = True

    return validLogin, accountRet

def logout(root):
    global validator
    global isLoggedIn

    printedOnce = False
    while len(candidateBlocks) > 0:
        if not printedOnce:
            # print("Please wait for candidate block validation.")
            printedOnce = True
        time.sleep(0.1)

    if validator in validators:
        validators.remove(validator)
    if validator.role == "a":
        switchScenes(root.children["adminMenu"], root.children["loginScene"])
    else:
        switchScenes(root.children["genericMenu"], root.children["loginScene"])
    isLoggedIn = False

def createAccount(username, password, name, roleSelection, root):
    # print("role is " + roleSelection)
    if roleSelection == "Admin":
        role = "a"
    elif roleSelection == "Doctor":
        role = "d"
    else:
        role = "p"

    # pattern = r'^[^\s]{1,20}$'
    # verifyUserIn = username
    # verifyPassIn = password

    # # remove spacews from name??

    # if !re.match(pattern, text):
    #     print("Valid input")

    getAccounts()
    if username in accountNames:
        root.children["createAccountMenu"].children["statusLabel"].configure(text=f"{newAccount.fullLegalName}'s account NOT created!, Invalid Username", fg = 'red')   
        return 

    newAccount = Account(username, password, role, name)
    addToCandidateBlocks("Create_Account", newAccount)
    # print(f"Created account for: {newAccount.fullLegalName}")

    root.children["createAccountMenu"].children["statusLabel"].configure(text=f"{newAccount.fullLegalName}'s account successfully created!", fg = 'green')
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
    elif (currentBlock.transactionType == "Upload") or (currentBlock.transactionType == "Download"):
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

def uploadIPFS(accessName, root):
    # open dialog box to choose file
    root.filename = filedialog.askopenfilename(title="Select A File", filetypes=(("All Files", "*.*"), ("PNGs", "*.png"), ("Text Files", "*.txt"), ("PDFs", "*.pdf")))
    
    # if 'cancel' was selected on dialog box:
    if len(root.filename) == 0:
        return
    
    # get user file upload choice
    fileName = root.filename

    #read data from original file
    with open(fileName, "rb") as file:
        fileContent = file.read()

    #***************************************************************************
    # for encryption
    #split up the path of the original file 
    parsePath = fileName.split("/")
    #save jst the file name as name
    name = parsePath[-1]
    
    newFileName = ""

    #for each piece of the file path that was split, add it to the new file path
    for dir in range(len(parsePath)-1):
        newFileName = newFileName + "/" + parsePath[dir]
        print(f"current: {newFileName}")

    #using the new file path, put file into subdirectory "processingFiles" then add the file name
        #to make the new full file path
        # !!!!! ORIGINAL FILE MUST BE IN THE MAIN DIRECTORY WITH COMBOGUI.PY OR WILL NOT WORK !!!!!!
    newFilePath = f"{newFileName}/processingFiles/{name}"
    print(f"new path: {newFilePath}")

    #  write orignal data to the new file 
    with open(newFilePath, "wb") as processingFile:
        processingFile.write(fileContent)

    #read the new file's data
    with open(newFilePath, "rb") as getFileData:
        fileData = getFileData.read()

    #encrypt the newfile's data
    encrypted = fernet.encrypt(fileData)

    # write over the unencrypted newfile's data with the encrypted data
    with open(newFilePath, "wb") as encrypted_file:
        encrypted_file.write(encrypted)

    #***************************************************************************
    
    # encode file for ipfs
    encodedContent = base64.b64encode(fileContent)
    encodedContentString = encodedContent.decode('utf-8')
    ipfsBody = [{
        "path": "uploaded_file", #fileName,
        "content": encodedContentString #"iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3"
    }]

    fileName = fileName.split('/')[-1]
    
    if GUIAccount.role == "p":
        if fileName in fileNames:
            root.children["genericMenu"].children["statusLabel"].configure(text=f"A file named {fileName} already exists!", fg="red")
            return
    else:
        if fileName in fileNames:
            root.children["doctorUploadMenu"].children["statusLabel"].configure(text=f"A file named {fileName} already exists!", fg="red")
            return
    
    # put file on ipfs
    ipfsUrl = evm_api.ipfs.upload_folder(api_key=apiKey, body=ipfsBody)[0]["path"]
    parsedPath = ipfsUrl.split('/')	#splits up the file text
    
    hash = parsedPath[4]            # cleans up the hash and the file name
    ipfsHashes.append(hash)        # update the hash and file lists
    fileNames.append(fileName)

    #Deletes the temorary upload file
    #os.remove(encryptedFileLocation)

    accessList = accessName
    print(f"**** uploadIPFS(): accessList is {accessList}")

    newFileData = FileData(hash, fileName, validator.address, accessList)
    addToCandidateBlocks("Upload", newFileData)
    # print(f"Uploaded {newFileData.fileName} to IPFS.")
    #root.children["genericMenu"].children["statusLabel"].configure(text=f"{fileName} added successfully.", fg="green")

    if GUIAccount.role == "p":
        root.children["genericMenu"].children["statusLabel"].configure(text=f"{fileName} added successfully.", fg="green")
    else:
        root.children["doctorUploadMenu"].children["statusLabel"].configure(text=f"{fileName} added successfully.", fg="green")

    return newFileData

def downloadIPFS(fileName, root):#def retrieveIpfs(conn, symmetricKey):
    # hash = ipfsHashes[fileIndex]
    for file in allFiles:
        if fileName == file.fileName:
            chosenFile = file
            print(f"File name is: {fileName}")

    url = "https://ipfs.moralis.io:2053/ipfs/" + chosenFile.ipfsHash + "/uploaded_file"	#does the url to retrieve the file from IPFS
    r = requests.get(url, allow_redirects=True)
    fileType = r.headers.get("content-type").split("/")[1]
    # fileName = fileNames[fileIndex]
    with open(fileName, "wb") as f:
        f.write(r.content)	#opens the file and adds content

    #IPFS downloads the file that was uploaded (encrypted)

    try:
        # optn the encrypted file and read the data
        with open(fileName, "rb") as enc_file:
            encrypted = enc_file.read()
        
        #decrypted the file data
        decrypted = fernet.decrypt(encrypted)

        # overwrite the encrypted data with the unencrypted data
        with open(fileName, "wb") as dec_file:
            dec_file.write(decrypted)

    except InvalidToken:
        # this error almost always go thorwn BUT the decryption WORKED and file was accesssable
        # just handle the error (the code keeps going if you dont but this will keep the terminal clean)
        #print("invalidtoken\n")
        pass

    #T here, Use symmetric key to decrypt the file, r.content
    #This function opens the first file, reads the dencrypted data, closes the file
    #Ten opens the second file, clears it, writes all decrypted data to it, then closes the file
    #SE.decryptFile(symmetricKey, file_name, file_name)

    accessList = chosenFile.accessList
    newFileData = FileData(chosenFile.ipfsHash, fileName, validator.address, accessList)

    addToCandidateBlocks("Download", newFileData)
    # print(f"Downloaded {newFileData.fileName} from IPFS.")

    root.children["downloadMenu"].children["statusLabel"].configure(text=f"{fileName} downloaded successfully.")

    return newFileData

def getFileList():
    global ipfsHashes
    global fileNames
    global allFiles

    ipfsHashes = []
    fileNames = []
    allFiles = []

    for block in blockchain:
        if block.index == 0:
            continue
        if block.transactionType == "Upload":
            ipfsHashes.append(block.payload.ipfsHash)
            fileNames.append(block.payload.fileName)
            allFiles.append(block.payload)

    return ipfsHashes, fileNames

def getAccounts():
    global accountNames
    global accounts

    accountNames = []
    accounts = []

    for block in reversed(blockchain):
        if (block.transactionType == "Update_User") and (block.payload.username not in accountNames):
            accountNames.append(block.payload.username)
            accounts.append(block.payload)
        elif (block.transactionType == "Create_Account") and (block.payload.username not in accountNames):
            accountNames.append(block.payload.username)
            accounts.append(block.payload)

    print("\n**** GetAccounts() results:")
    for account in accounts:
        print(f"\t{account.username} \t {account.role}")

def addToCandidateBlocks(transactionType, payload):
    oldLastIndex = blockchain[-1]
    newBlock = generateBlock(oldLastIndex, validator.address, transactionType, payload)
    # print(f"Added a candidate block with validator address: {validator.address}")

    if isBlockValid(newBlock, oldLastIndex):
        candidateBlocks.append(newBlock)

def setGUIBlockchain(newBlockchain):
    global blockchain
    blockchain = newBlockchain 

def getGUIBlockchain():
    return blockchain

def setGUIValidator(newValidator):
    global validator
    validator = newValidator
    # print(f"Just set validator address to {validator.address}")

def getGUICandidateBlocks():
    return candidateBlocks

def removeCandidateBlock(blockToRemove):
    candidateBlocks.remove(blockToRemove)
    # print(f"Removed a candidate block!")

def getGUIAccount():
    return GUIAccount

def GUIgetIP():
    return connectIP

def main():
    createFirstBlocks()
    getFileList()
    
    # for name in fileNames:
    #     print(name)

    # Handle candidate blocks in a separate thread
    # candidateThread = threading.Thread(target=lambda: candidateBlocks.append(None) if candidateBlocks else None)
    # candidateThread.start()

    # # Pick winner thread
    # winnerThread = threading.Thread(target=pickWinner)
    # winnerThread.start()

    root = setScenes()
    root.mainloop()

if __name__ == "__main__":
    main()
