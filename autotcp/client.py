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

givenport = 11222

def client_program():
    global givenport
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_ip = "146.229.163.147"  # replace with the server's IP address
    server_port = 11112 # replace with the server's port number
    # establish connection with server
    client.connect((server_ip, server_port))

    while True:
        # input message and send it to the server
        #msg = 'hello'#input("Enter message: ")
        myip = ni.ifaddresses('enp0s31f6')[ni.AF_INET][0]['addr']
        message = f"be my neighbor? answer on {myip}, port: {givenport}"

        client.send(message.encode("utf-8")[:1024])

        # receive message from the server
        response = client.recv(1024)
        response = response.decode("utf-8")

        # if server sent us "closed" in the payload, we break out of the loop and close our socket
        if response.lower() == "closed":
            break

        print(f"Received: {response}")
        time.sleep(3)

    # close client socket (connection to the server)
    client.close()
    print("Connection to server closed")

def main():
    client_program()

if __name__ == "__main__":
    main()
