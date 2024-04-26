import rsa
from cryptography.fernet import Fernet
import secrets


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


#Calls the function to generte the file keys, and parses them
global publicKey
global privateKey
keyObject = genKeys()
publicKey = getPublicKey(keyObject)
privateKey = getPrivateKey(keyObject)

#Generates the file key and encodes it
fileKey = base64.urlsafe_b64encode(secrets.token_bytes(32))

#Gets the public key from the user
lwPublicKey = comm.receivedatafromrequester(lw1)

#Encrypts the key to send and sends the encrypted text
comm.senddatatorequester(lw1, rsa.encrypt(fileKey, lwPublicKey))

#Client-side code to get the encryption key
"""

        #Code to get the encryption key
        elif sendRequest == "Get_Key":
            #Sends the message requesting the key
            clientSocket.send((sendRequestMessage).encode("utf-8")[:4096])
            time.sleep(0.05)
            #Sends the message with the public key to encrypt the key
            clientSocket.send((blockToAdd).encode("utf-8")[:4096])
            #Waits for reception of the file key and decrypts it with the privateKey
            return rsa.decrypt(clientSocket.recv(4096).decode("utf-8"), authorizingUser).decode()
"""

#Here is a note from before, do we want this, as access is granted locally?
#Way to test, get wireshark on current set, see if it found files. Then, change, and see if wireshark finds files

#
#Need a way to get the keys from the client and the server
#So, when the client connects, the server should validate the client, then send the symmetric key
#Would require a new condition in the main server while loop that when a client connects, the client is validated and gets the key
#Would also require a corresponding section of code in the client so the client requests the key when first joining the blockchain
#Might need to happen in client.py or server.py under autotcp
#Also, might need to convert the formatting potentially from base 64 to utf-8
#If decoding is needed, just send the encrypted data over the wire and then decrypt it from utf-8
#
