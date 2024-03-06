from cryptography.fernet import Fernet
import base64
import secrets

#Function to generate an AES 256 key
def generateAES256Key():
    #Generates 32B random key for AES-256
    return secrets.token_bytes(32)

#Function to save the given symmetric key to a file
def saveKey(symmetricKey, saveLocation):
    #Writes the key to the given file
    outputfile = open(saveLocation, "wb")
    outputfile.write(symmetricKey)
    outputfile.close()

#Function to load the symmetric key from the given file
def loadKey(fileLocation):
    #Writes the key to the given file
    inputfile = open(fileLocation, "rb")
    symmetricKey = inputfile.read()
    inputfile.close()
    #Returns the key to the given program
    return symmetricKey

#Function to encrypt the given file using the given symmetric key
def encryptFile(symmetricKey, originalFileLocation, saveLocation):
    #Creates Fernet instance using the given symmetric key
    localFernet = Fernet(symmetricKey)
    #Reads the bytes from the input file
    inputfile = open(originalFileLocation, 'rb')
    plaintextData = inputfile.read()
    inputfile.close()
    #Encrypts the given data using the symmetric key
    encryptedData = localFernet.encrypt(plaintextData)
    #Writes the encrypted data to the given file
    outputfile = open(saveLocation, "wb")
    outputfile.write(encryptedData)
    outputfile.close()

#Function to decrypt the given file using the symmetric key
def decryptFile(symmetricKey, encryptedFileLocation, saveLocation):
    #Creates Fernet instance using the given symmetric key
    localFernet = Fernet(symmetricKey)
    #Reads the bytes from the input file
    inputfile = open(encryptedFileLocation, 'rb')
    encryptedData = inputfile.read()
    inputfile.close()
    #Decrypts the given data using the symmetric key
    decryptedData = localFernet.decrypt(encryptedData)
    #Writes the decrypted data to the given file
    outputfile = open(saveLocation, "wb")
    outputfile.write(decryptedData)
    outputfile.close()

"""Sample program showing usage of this code"""
"""""""""
#Converts the AES 256 key into its base 64 format for fernet to process
symmetricKey = base64.urlsafe_b64encode(generateAES256Key())

#Saves the key to the given file
saveKey(symmetricKey, "symmetric.pem")
#Loads the key from the given file
loadedKey = loadKey("symmetric.pem")
print("It is " + str(symmetricKey == loadedKey) + " that the original key and the loaded key are identical") 

#Call this function when you want to encrypt a file for use on the blockchain
encryptFile(symmetricKey, "LoremIpsum.txt", "encryptedText.bin")

#Call this function when you want to decrypt a file after downloading from the blockchain
decryptFile(symmetricKey, "encryptedText.bin", "decryptedText.txt")

inputFile1 = open("LoremIpsum.txt", 'rb')
originalData = inputFile1.read()
inputFile2 = open("decryptedText.txt", 'rb')
processedData = inputFile2.read()
print("It is " + str(originalData == processedData) + " that the original text and the processed text are identical") 
"""""""""
