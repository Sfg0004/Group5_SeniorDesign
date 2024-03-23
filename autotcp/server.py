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
connectport = 11112

def listenforRequests(): #connectport

    # listen for incoming connections
    server.listen(0)
    server_ip = ni.ifaddresses('enp0s31f6')[ni.AF_INET][0]['addr']
    print(f"Listening on {server_ip}:{connectport}")

def requestConnection():
    print("empty")


def acceptConnection():
    client_socket, client_address = server.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
    return client_socket


def closeConnection(client_socket):
    time.sleep(0.5)
    client_socket.send("closed".encode("utf-8"))
    client_socket.close()
    print("Connection to client closed")
    # close server socket
    #server.close()


def receiveData(client_socket):
    request = client_socket.recv(1024)
    request = request.decode("utf-8") # convert bytes to string
    print(f"Received: {request}")

    response = "accepted".encode("utf-8") # convert string to bytes
        # convert and send accept response to the client
    client_socket.send(response)

    return request

def extractIP(message):
    ip_split = message.split("on ")
    temp = ip_split[1]
    temp2 = temp.partition(",")
    port_split = message.split("port: ")
    
    client_ip = temp2[0]
    client_port = port_split[1]
    print(f"ip_split: {client_ip}")
    print(f"port_split: {client_port}")

    return client_ip, client_port

def bindasServer():
    myip = ni.ifaddresses('enp0s31f6')[ni.AF_INET][0]['addr'] # I am the server
    port = 11112 #connectport

    # bind the socket to a specific address and port
    server.bind((myip, port)) # I am the server


def server_program():
    # create a socket object
    bindasServer()

    listenforRequests()

    # accept incoming connections
    client_socket = acceptConnection()

    message = receiveData(client_socket)

    client_ip, client_port = extractIP(message)

    closeConnection(client_socket)

    #create new sustained connection


    # receive data from the client
    # while True:
    #     receiveData(client_socket)
    #     if request.lower() == "close": # if we receive "close" from the client, then we breakout of the loop and close the conneciton
    #         closeConnection()
        
    #     #close connectport connection 
    #     closeConnection()

    #     #start new sustained connection


    
def main():
    server_program()

if __name__ == "__main__":
    main()
