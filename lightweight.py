
#Function to send the request to the target IP
def sendRequest(sendRequestMessage, requestType=None, blockToAdd=None):
    #desiredMessage = ""
    #
    #
    #Need to do more with this
    #
    #
    #newBlock = Block()
    #Based on the request, craft a message and send it
    if sendRequestMessage == "Upload_File":
        pass
    elif sendRequestMessage == "Download_File":
        pass
    elif sendRequestMessage == "Get_Blockchain":
        pass
    elif sendRequestMessage == "Create_User":
        pass
    #Future code will need this
    #elif sendRequest == "Get_Key":
    #    pass
    #Else, invalid request type, so do nothing
    #Should never happen
    else:
        pass
    #Creates a socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Connects to the other device
    clientSocket.connect((targetIP, lightweightport))
    #Sends the message
    clientSocket.send((sendRequestMessage).encode("utf-8")[:4096])
    #Based on the operation, send the proposed block
    #Probably needs to convert the block to a string
    #clientSocket.send(newBlock.encode())
    #Gets a response(the status of the operation/the blockchain)
    #status = clientSocket.recv(4096).decode()
    #Closes the socket
    clientSocket.close()
    #Returns the status of the operation
    #return status
