#change eth interface name if necessary in myIP()

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
import multiprocessing

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #new socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
samaritan = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
self_samaritan = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
neighbor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connectport = 11321
givenport = 12321

#client ip address array
nodelist = [] #local list of node objects
iplist = [] #ips only - for sending & receiving node update between nodes


class nodes:
     def __init__(self, ip, latency, isneighbor):
        self.ip = ip
        self.latency = latency
        self.isneighbor = isneighbor

# for deciding neighbors
def get_simple_cmd_output(cmd, stderr=STDOUT): #for get_ping_time to use
    """
    Execute a simple external command and get its output.
    """
    args = shlex.split(cmd)
    return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0].decode()

# for deciding neighbors
def get_ping_time(host):
    host = host.split(':')[0]
    cmd = "fping {host} -C 3 -q".format(host=host)
    res = [float(x) for x in get_simple_cmd_output(cmd).strip().split(':')[-1].split() if x != '-']
    if len(res) > 0:
        return sum(res) / len(res)
    else:
        return 999999

def addnode(ip): #local

    req = "{}:4444".format(ip)  # print("req: " + req) troubleshooting
    latsum = 0
    for i in range(3):
        latsum += (get_ping_time(req))
    latency = latsum/3 #avg 3 times
    nodelist.append(nodes(ip,latency, false))
    for x in nodelist:
        print(x.ip,"{:.3f}".format(x.latency), x.isneighbor)
    local_refresh_iplist(iplist, ip, "add")
        
def deletenode(ip): #local
    for x in nodelist:
        if node.ip == ip:
            nodelist.remove(x)
            del x
    local_refresh_iplist(iplist, ip, "delete")

def refresh_neighbors(nodelist): #local

    neighborcount = 0
    for node in nodelist:
        if (node.isneighbor == true):
            node.isneighbor = false
    lownode = nodelist[0]
    for i in range(2):
        if (neighborcount < 2):
            lowlat = 999 #latency to beat
            for node in nodelist:
                if ((node.latency < lowlat) and (not(node.isneighbor))):
                    lowlat = node.latency
                    lownode = node
            lownode.isneighbor = true

def message_refresh_iplist(locallist, receivedlist): #called after iplist recieved from neighbors

    locallist = order_iplist(locallist) #order inputs
    receivedlist = order_iplist(receivedlist)

    refreshedlist = []

    for ip in locallist:
        try:
            receivedlist.index(ip)
            refreshedlist.append(ip)
        except:
            deletenode(ip)


    for jp in receivedlist:
        try:
            locallist.index(jp)
        except:
            addnode(jp)
            refreshedlist.append(jp)

    refreshedlist = order_iplist(refreshedlist)
    print(refreshedlist)

     
    #priority - checks own ip presence
    refresh_neighbors(nodelist)

    refreshedlist = order_iplist(refreshedlist)
    return refreshedlist

def local_refresh_iplist(iplist, ip, mode): #called after node locally added or deleted, called every so often per time period..

    if (mode=="add"):
        iplist.append(ip)

    elif (mode=="delete"):
        iplist.remove(ip)
    #priority - checks own ip presence
    refresh_neighbors(nodelist)

    iplist = order_iplist(iplist)
    send_iplist(iplist)
    return iplist


def send_iplist(iplist):

    iplist = order_iplist(iplist)
    print("send ip stub: implement soon")
    print(iplist)
    print("end stub")

def order_iplist(iplist):

    sortedips = []
    sortedips = sorted(iplist, key =lambda j: ''.join(('00'+j.split('.')[i])[-3::] for i in range(4))) #sort ips
    for ip in range(len(iplist)): #loop to remove duplicates
        if ip<len(iplist)-1:
            if(iplist[ip]==iplist[ip+1]):
                sortedips.remove(iplist[ip])
    return sortedips


def request_iplist():

    senddatafromclient("requesting iplist.")
    received_iplist = receivedatafromsamaritan(client) #where client is self
    return received_iplist



def myIP():
    return (ni.ifaddresses('enp0s3')[ni.AF_INET][0]['addr'])

def listenforRequests(): #server method, connectport

    # listen for incoming connections
    server.listen(0)
    server_ip = myIP()
    print(f"I am server. Listening on {server_ip}:{connectport}")

def requestConnection(server_ip, server_port): #client method
    try:
        client.connect((server_ip, server_port)) #client requests to connect to server
        myip = myIP()
        message = f"be my neighbor? answer on {myip}, port: {givenport}"
        senddatafromclient(message,client) #client parameter

        # receive message from the server
        response = receivedatafromserver(client)

        #neighbor returns their self_samaritan connect data, which I see as my neighbor
        neighbor_ip, neighbor_port = extractIP(response)

        return neighbor_ip, neighbor_port

    except socket.error:
        return ("failure")

def requestsustainedConnection(samaritan_ip, samaritan_port): #client method
    samaritan_port = int(samaritan_port)
    try:
        print(f"Trying to connect to: {samaritan_ip}:{samaritan_port}")
        client.connect((samaritan_ip, samaritan_port)) #client requests to connect to server
        #message = "beginning sustained connection. love, neighbor"
        #senddatatosamaritan(message)
        #response = receivedatafromsamaritan(client)
    except Exception as e: print(e)

def acceptconnectportConnection(): #server method, only for connectport
    requester_socket, requester_address = server.accept()
    print(f"I am server. Accepted connection from {requester_address[0]}:{requester_address[1]}")
    return requester_socket

def acceptConnection(): #self_samaritan method
    neighbor_socket, neighbor_address = self_samaritan.accept()
    print(f"I am self_samaritan. Accepted connection from {neighbor_address[0]}:{neighbor_address[1]}")
    return neighbor_socket

def approveConnection(requester_socket): #server method
    global givenport
    myip = myIP()
    response = f"accepted. talk on {myip}, port: {givenport}".encode("utf-8") # convert string to bytes
    #givenport = givenport + 1
    #send accept response to the client
    requester_socket.send(response)

#closeclientconnection
def closeneighborConnection(neighbor_socket): #samaritan method
    time.sleep(0.5) #without the client sees "acceptedclosed"
    senddatatoneighbor(neighbor_socket, "closed")
    neighbor_socket.close()
    print("I am samaritan. Connection to neighbor closed")

def closerequesterConnection(requester_socket): #server method
    time.sleep(0.5) #without the client sees "acceptedclosed"
    senddatatorequester(requester_socket, "closed")
    requester_socket.close()
    print("I am server. Connection to requester closed")

def closeserverConnection(client): #client method
    client.send("client closing".encode("utf-8"))
    client.close()
    print("I am client. Connection to server closed")

def closesamaritanConnection(client): #client method
    client.send("client closing".encode("utf-8"))
    client.close()
    print("I am client. Connection to samaritan closed")


def receivedatafromrequester(requester_socket): #server method
    request = requester_socket.recv(1024)
    request = request.decode("utf-8") # convert bytes to string
    print(f"I am server. Received: {request}")

    return request

def receivedatafromneighbor(neighbor_socket): #server method
    request = neighbor_socket.recv(1024)
    request = request.decode("utf-8") # convert bytes to string
    print(f"I am server. Received: {request}")

    return request

def receivedatafromserver(client): #client method

    response = client.recv(1024)
    response = response.decode("utf-8")
   
    print(f"I am client. Received: {response}")

    if response.lower() == "closed":
        closeserverConnection(client)

    return response

def receivedatafromsamaritan(client): #client method

    response = client.recv(1024)
    response = response.decode("utf-8")
   
    print(f"I am client. Received: {response}")

    if response.lower() == "closed":
        closesamaritanConnection(client)

    return response

#sendclientdata
def senddatafromclient(data, client): #client method, buffer size 1024 may need to increase to accomodate blockchain message
    client.send(data.encode("utf-8")[:1024])

#sendclientsocketdata
def senddatatoneighbor(neighbor_socket, data): #server method, buffer size 1024 may need to increase to accomodate blockchain message
    neighbor_socket.send(data.encode("utf-8")[:1024])
    
def senddatatorequester(requester_socket, data): #server method, buffer size 1024 may need to increase to accomodate blockchain message
    requester_socket.send(data.encode("utf-8")[:1024])

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


def message_selfsamaritan(data, num_self_samaritans): #server method (server to samaritan)
    for s in range(num_self_samaritans):
        message_queue.put(data)

def listenServer(): #selfsamaritan method listen to server
    try:
        message = message_queue.get(timeout=1)  # Wait for a message
        print(f"received message: {message}")
    except queue.Empty:
        pass  # Continue waiting if queue is empty

    
def main():
    
    message_queue = Queue()

    #message_queue.Queue()  # create a Shared queue for communication

    threading.Thread(target=run_server, args=()).start()
    while(1):
    	time.sleep(10)
    initial_samaritan_jointo_ip = input("Enter the IP of a node in the blockchain you want to join.")

    threading.Thread(target=run_client, args=(initial_samaritan_jointo_ip,)).start()
        
    iplist = order_iplist(iplist)
    print("send ip stub: implement soon")
    print(iplist)
    print("end stub") 


def run_client(initial_samaritan_jointo_ip): #needs periodic ip requesting(checking) added

    #neighbor_ip = "146.229.163.144"  # replace with the neighbor's(server's) IP address
    #connect_port = 11113 #neighbor's (server's) port

    try:
        samaritan_ip, samaritan_port = requestConnection(initial_samaritan_jointo_ip, connectport)
        print ("samaritan accepted my client connection. hooray!")
    except:
        print("I am client. My request to connect to a samaritan failed.")

    while(1): #automatic close response present in receivedatafromserver
        receivedatafromserver(client)
        time.sleep(1)

    try:
        print(f"samaritan receiveport is: {samaritan_port}")
        time.sleep(0.2)
        requestsustainedConnection(samaritan_ip, samaritan_port)
        print ("sustained samaritan connection successful. hooray!")
    except:
        print("I am client. My request for sustained connection failed.")

    while(1): #automatic close response present in receivedatafromserver
        receivedatafromsamaritan(client)
        received_iplist = request_iplist()
        message_refresh_iplist(iplist,received_list)
        time.sleep(1) #rn iplist updates every second



def run_server(): #add func to talk to samaritan and samaritan to listen to server (listenServer)

    global givenport
    global receiveport

    try:
        bindasServer(connectport)
        listenforRequests()

        while(1):
            # accept incoming connections

                # accept incoming connections
            requester = acceptconnectportConnection() #sit waiting/ready for new clients
            receivedatafromrequester(requester)
            approveConnection(requester) #I tell client what port to talk to me on
            receiveport = givenport
            givenport = givenport + 1
            #message1 = "final connectport message, about to close"
            #time.sleep(0.5)
            #senddatatoneighbor(requester, message1)
            #time.sleep(0.1)
            closerequesterConnection(requester)

            if(1):
                ppid = os.getpid()
                print("Parent process PID:", ppid)
                child_pid = os.fork()
                if child_pid == 0:            #   This code is executed by the child process

                    myip = myIP()
                    self_samaritan.bind((myip, receiveport)) 
                    print(f"receiveport is: {receiveport}")

                    self_samaritan.listen(0)
                    neighbor = acceptConnection() #wait here for client's sustained request

                    time.sleep(0.5)
                    message2 = "samaritan to neighbor, over"
                    senddatatoneighbor(neighbor, message2)
			
                    neighbor.setblocking(False)
                    while(1):
                        message = receivedatafromneighbor(neighbor)
                        print(message)
                        if(message == "requesting iplist."):
                            send_iplist(iplist)

                    print("I am samaritan. Stopping my good works.")
                    closeneighborConnection(self_samaritan) #close my given port (my side sustained connection as their neighbor)

    except OSError:
        print("OSerror")



if __name__ == "__main__":
    main()
