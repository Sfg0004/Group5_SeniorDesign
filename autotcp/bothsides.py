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
connectport = 11162
givenport = 12252

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
        needy.connect((server_ip, server_port)) #client requests to connect to server
        #message = "beginning sustained connection. love, neighbor"
        #sendneighborData(message)
        
        #response = receiveneighborData(needy)
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
    client_socket.close()
    print("I am server. Connection to client closed")

def closeserverConnection(client): #client method
    client.send("client closing".encode("utf-8"))
    client.close()
    print("I am client. Connection to server closed")


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
    server.bind((myip, port)) # I am the server


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
    neighbor_socket1 = acceptConnection()

    time.sleep(0.5)
    message2 = "samaritan to neighbor, over"
    sendclientsocketData(neighbor_socket1, message2)

    message3 = "samaritan to neighbor, send your blockchain or ask for mine"
    sendclientsocketData(neighbor_socket1, message3)

    message = receiveclientData(neighbor_socket1)
    print(message)

    print("I am samaritan. Stopping my good works.")

    closeclientConnection(neighbor_socket1) #close my given port (my side sustained connection as their neighbor)


def client_program():#neighbor_ip):
    neighbor_ip = "146.229.163.144"  # replace with the neighbor's(server's) IP address
    #connect_port = 11113 #neighbor's (server's) port

    try:
        neighbor_ip, neighbor_port = requestConnection(neighbor_ip, connectport)
        print ("server accepted my client connection. hooray!")
    except:
        print("I am client. My request to connect to a neighbor failed.")

    message = receiveneighborData(client)

    message = receiveneighborData(client)

    try:
        print(f"samaritan receiveport is: {neighbor_port}")
        time.sleep(0.2)
        requestsustainedConnection(neighbor_ip, neighbor_port)
        print ("sustained neighbor connection successful. hooray!")
    except:
        print("I am client. My request for sustained connection failed.")

    message = receiveneighborData(needy)
    
    message = receiveneighborData(needy)

    
def main():
    server_program()
    
    



if __name__ == "__main__":
    main()
