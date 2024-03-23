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
connectport = 11116
givenport = 12222

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
        sendneighborData(message)

        # receive message from the server
        response = receiveneighborData(client)
        return ("connected")

    except socket.error:
        return ("failure")


def acceptConnection(): #server method
    client_socket, client_address = server.accept()
    print(f"I am server. Accepted connection from {client_address[0]}:{client_address[1]}")
    return client_socket


def closeclientConnection(client_socket): #server method
    time.sleep(0.5) #without the client sees "acceptedclosed"
    sendclientData(client_socket, "closed")
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

    response = "accepted".encode("utf-8") # convert string to bytes
        # convert and send accept response to the client
    client_socket.send(response)

    return request



def receiveneigborData(client): #client method

    response = client.recv(1024)
    response = response.decode("utf-8")
   
    print(f"I am client. Received: {response}")

    if response.lower() == "closed":
        closeserverConnection(client)

    return response

def sendneighborData(data): #client method, buffer size 1024 may need to increase to accomodate blockchain message
    client.send(data.encode("utf-8")[:1024])

def sendclientData(client_socket, data): #server method, buffer size 1024 may need to increase to accomodate blockchain message
   
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


def server_program():
    # create a socket object
    bindasServer(connectport)

    listenforRequests()

    # accept incoming connections
    client_socket = acceptConnection()

    message = receiveclientData(client_socket)

    client_ip, client_port = extractIP(message)

    message1 = "middlemessage"
    sendclientData(client_socket, message1)

    time.sleep(0.5)


    closeclientConnection(client_socket)

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
    neighbor_ip = "146.229.163.145"  # replace with the neighbor's(server's) IP address
    #connect_port = 11113 #neighbor's (server's) port

    if (requestConnection(neighbor_ip, connectport) == "connected"):
        print ("neighbor/server accepted my client connection. hooray!")
    else:
        print("I am client. My request to connect to a neighbor failed.")

    message = receiveneighborData(client)
    print(message)

    #closeserverConnection(client)

    
def main():
    server_program()

if __name__ == "__main__":
    main()
