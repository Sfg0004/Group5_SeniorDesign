import rsa
import secrets
import base64

#Saves the public key to the given file
def savePublicKey(publicKey, publicKeyFilename):
    #Saves the public key to the given data file
    outputFile = open(publicKeyFilename, 'wb')
    outputFile.write(publicKey.save_pkcs1())
    outputFile.close()

#Saves the private key to the given file
def savePrivateKey(privateKey, privateKeyFilename):
    #Saves the private key to the given data file
    outputFile = open(privateKeyFilename, 'wb')
    outputFile.write(privateKey.save_pkcs1())
    outputFile.close()

#Loads the public key from the given file
def loadPublicKey(publicKeyFilename):
    #Reads the public key from the input file
    inputFile = open(publicKeyFilename, 'rb')
    publicKey = rsa.PublicKey.load_pkcs1(inputFile.read())
    inputFile.close()
    #Returns the public key
    return publicKey

#Loads the private key from the given file
def loadPrivateKey(privateKeyFilename):
    #Reads the private key from the input file
    inputFile = open(privateKeyFilename, 'rb')
    privateKey = rsa.PrivateKey.load_pkcs1(inputFile.read())
    inputFile.close()
    #Returns the private key
    return privateKey

#Function to generate a new key, typically going to be 4096b
#In testing, may take up to 120 seconds to generate a 4096b key
def generateKey(keySize):
    return rsa.newkeys(keySize)


"""Sample program showing usage of this code"""
"""""""""
#Basic message to encode. At the moment, done for 256b AES key
message = base64.urlsafe_b64encode(secrets.token_bytes(32))
publicKey, privateKey = generateKey(1024)

#Saves the keys to a file
savePublicKey(publicKey, "public.pem")
savePrivateKey(privateKey, "private.pem")
#Encrypts the given message. Normally its the symmetric key for the files
encryptedMessage = rsa.encrypt(message, publicKey)
#Decrypts the given message. Normally, its the symmetric key for the files
decryptedMessage = rsa.decrypt(encryptedMessage, privateKey).decode()

#Prints the messages to the terminal
print("encrypted message = " + str(encryptedMessage))
print("decrypted message = " + str(decryptedMessage))

#Loads the public and private keys from the previous files
publicKey2 = loadPublicKey("public.pem")
privateKey2 = loadPrivateKey("private.pem")
#Encrypts the given message. Normally its the symmetric key for the files
encryptedMessage = rsa.encrypt(message, publicKey2)
#Decrypts the given message. Normally, its the symmetric key for the files
decryptedMessage = rsa.decrypt(encryptedMessage, privateKey2).decode()

#Prints the messages to the terminal
print("encrypted message = " + str(encryptedMessage))
print("decrypted message = " + str(decryptedMessage))
"""""""""