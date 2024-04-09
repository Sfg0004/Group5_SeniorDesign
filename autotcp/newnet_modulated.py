#change eth interface name if necessary in myIP()
from methods import block
#from methods import decentral
from methods import comm

import hashlib
import json
import socket
import signal
import time
import random
import threading
import sys
import os
import requests
from random import randint
from datetime import datetime
from queue import Queue
import netifaces as ni
import shlex  
from subprocess import Popen, PIPE, STDOUT
import ipaddress
import multiprocessing


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #new socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
samaritan = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
self_samaritan = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
neighbor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
initial_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connectport = 11392
givenport = 12392

def myIP():
    return (ni.ifaddresses('enp0s31f6')[ni.AF_INET][0]['addr'])

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    comm.clientOut.close()
    comm.blockFile.close()
    sys.exit(0)

def main():
    myip = comm.myIP()

    signal.signal(signal.SIGINT, signal_handler)

    global iplist
    
    self_samaritan_to_client = Queue()
    client_to_self_samaritan = Queue()

    #message_queue.Queue()  # create a Shared queue for communication
    initial_samaritan_jointo_ip = "146.229.163.147"#input("Enter the IP of a node in the blockchain you want to join: ")

    threading.Thread(target=run_server, args=(self_samaritan_to_client,client_to_self_samaritan,)).start()
    #initial_samaritan_jointo_ip = "146.229.163.149"
    time.sleep(2)

    threading.Thread(target=run_client, args=(initial_samaritan_jointo_ip,self_samaritan_to_client,client_to_self_samaritan,)).start()

def run_client(initial_samaritan_jointo_ip,self_samaritan_to_client,client_to_self_samaritan): #needs periodic ip requesting(checking) added
   # original_stdout = sys.stdout
    
    #with open('clientOut.txt', 'w') as clientOut:
    #sys.stdout = clientOut
    #neighbor_ip = "146.229.163.144"  # replace with the neighbor's(server's) IP address
    #connect_port = 11113 #neighbor's (server's) port
    comm.write_to_client_out("debug, in client\n")
    try:
        samaritan_ip, samaritan_port = comm.requestConnection(initial_samaritan_jointo_ip, connectport, initial_client, givenport)
        comm.write_to_client_out ("server accepted my client connection. hooray!")
    except:
        comm.write_to_client_out("I am client. My request to connect to a server failed.")

    while(1): #automatic close response present in receivedatafromserver
        response = comm.receivedatafromserver(initial_client)
        if (response == "closed"):
            break
        time.sleep(1)

    try:
        comm.write_to_client_out(f"samaritan receiveport is: {samaritan_port}")
        time.sleep(5)
        comm.requestsustainedConnection(samaritan_ip, samaritan_port, client)
        comm.write_to_client_out("sustained samaritan connection successful. hooray!")
    except:
        comm.write_to_client_out("I am client. My request for sustained connection failed.")

    try:
        while(1): #automatic close response present in receivedatafromserver
            #message = comm.receivedatafromsamaritan(client)
            sample = "1234"
            #print("I got the sample")
            
            #NEED ADMIN BLOCK
            # genesis_block = block.generate_genesis_block()
            # block.blockchain.append(genesis_block)
            # block.generate_sample_blocks()
            # blockchain = block.assembleBlockchain()
            comm.senddatafromclient(sample, client)

            # if (message.lower() == "closed"):
            #     comm.closesamaritanConnection(client)
            #     exit(0)
            # else:
                #blockchain = block.assembleBlockchain()
                #comm.write_to_block_file(message)
                #comm.senddatafromclient(blockchain)
            #received_iplist = request_iplist(client)
            #message_refresh_iplist(iplist,received_list)
            time.sleep(3) #rn iplist updates every second

            message = comm.receivedatafromsamaritan(client)

            if (message.lower() == "closed"):
                 comm.closesamaritanConnection(client)
                 exit(0)

    except:
        comm.clientOut.close() 

def run_server(self_samaritan_to_client, client_to_self_samaritan): #add func to talk to samaritan and samaritan to listen to server (listenServer)
    global receiveport
    global givenport
    try:
        comm.bindasServer(connectport, server)
        comm.listenforRequests(connectport, server)

        while(1):
            # accept incoming connections

                # accept incoming connections
            requester = comm.acceptconnectportConnection(server) #sit waiting/ready for new clients
            comm.receivedatafromrequester(requester)
            comm.approveConnection(requester, givenport) #I tell client what port to talk to me on
            receiveport = comm.setreceiveequal(givenport)
            givenport = comm.incgiven(givenport)
            comm.closerequesterConnection(requester)

            if(1):
                ppid = os.getpid()
                print("Parent process PID:", ppid)
                child_pid = os.fork()
                if child_pid == 0:            #   This code is executed by the child process

                    myip = comm.myIP()
                    self_samaritan.bind((myip, receiveport)) 
                    print(f"receiveport is: {receiveport}")

                    self_samaritan.listen(0)
                    neighbor = comm.acceptConnection(self_samaritan) #wait here for client's sustained request

                    time.sleep(0.5)

                    data = "BLOCKCHAIN"

                    while(1):
                        time.sleep(1)
                        #if(not neighbor)
                            #exit(0)
                        #NEED ADMIN BLOCK
                        genesis_block = block.generate_genesis_block()
                        block.blockchain.append(genesis_block)
                        block.generate_sample_blocks()
                        blockchain = block.assembleBlockchain()
                        comm.senddatatoneighbor(blockchain, client)
                        #data = "Server Data"
                        #comm.senddatatoneighbor(neighbor, data)
                        message = comm.receivedatafromneighbor(neighbor)
                        #if(message == "requesting iplist."):
                            #send_iplist(iplist)

                    print("I am samaritan. Stopping my good works.")
                    comm.closeneighborConnection(self_samaritan) #close my given port (my side sustained connection as their neighbor)

                else:
                    os.wait() #parent wait for child
    except OSError:
        print("OSerror")



if __name__ == "__main__":
    main()
