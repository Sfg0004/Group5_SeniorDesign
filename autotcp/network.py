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

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #new socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
samaritan = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
neighbor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
needy = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
neighbor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connectport = 11162
givenport = 12252

#client ip address array
nodelist = [] #local list of node objects
iplist = [] #ips only - for sending & receiving node update between nodes


class nodes:
     def __init__(self, ip, latency, neighbor):
        self.ip = ip
        self.latency = latency
        self.neighbor = neighbor

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
        print(x.ip,"{:.3f}".format(x.latency), x.neighbor)
    local_refresh_iplist(iplist, ip, "add")
        
def deletenode(ip) #local
     for x in nodelist:
        if node.ip == ip
            nodelist.remove(x)
            del x
    local_refresh_iplist(iplist, ip, "delete")

def refresh_neighbors(nodelist) #local

    neighborcount = 0
    for node in nodelist:
        if (node.neighbor = true):
            node.neighbor = false
    lownode = nodelist[0]
    for i in range(2):
        if (neighborcount < 2):
            lowlat = 999 #latency to beat
            for node in nodelist:
                if ((node.latency < lowlat) && (!node.neighbor))
                    lowlat = node.latency
                    lownode = node
            lownode.neighbor = true

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

    if (mode=="add")
        iplist.append(ip)

    elif (mode=="delete")
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

def messageSamaritan(data, num_clients): #server method (server to samaritan)
    for c in range(num_clients):
        message_queue.put(data)

def listenServer(): #samaritan method
  try:
    message = message_queue.get(timeout=1)  # Wait for a message
    print(f"received message: {message}")
    if message == "exit":
        break
    except queue.Empty:
        pass  # Continue waiting if queue is empty

    
def main():
    
    message_queue = queue.Queue()  # create a Shared queue for communication

    threading.Thread(target=run_server, args=()).start()
        
    iplist = order_iplist(iplist)
    print("send ip stub: implement soon")
    print(iplist)
    print("end stub") 

    
    while true:

        start new connection 
        num_clients = num_clients+1
            client program?
        tup = addr
        ip = tup[0]
        iplist.append(ip)
        send_iplist(iplist)
        addnode(ip)


def run_server:

    global givenport
    global receiveport

    try:
        bindasServer(connectport)
        listenforRequests()

        while(1)
            # accept incoming connections

                # accept incoming connections
            client_socket = acceptclientConnection() #sit waiting/ready for new clients
            receiveclientData(client_socket)
            approveConnection(client_socket) #I tell client what port to talk to me on
            receiveport = givenport
            message1 = "final connectport message, about to close"
            sendclientsocketData(client_socket, message1)
            time.sleep(0.1)
            closeclientConnection(client_socket)

            if(temp):
                ppid = os.getpid()
                print("Parent process PID:", ppid)
                child_pid = os.fork()
                if child_pid == 0:            #   This code is executed by the child process

                    myip = myIP()
                    samaritan.bind((myip, receiveport)) 
                    print(f"receiveport is: {receiveport}")

                    samaritan.listen(0)
                    neighbor_socket = acceptConnection() #wait here for client's sustained request

                    time.sleep(0.5)
                    message2 = "samaritan to neighbor, over"
                    sendclientsocketData(neighbor_socket, message2)

                    message3 = "samaritan to neighbor, you can ask for my blockchain now"
                    sendclientsocketData(neighbor_socket, message3)

                    message = receiveclientData(neighbor_socket)
                    print(message)

                    print("I am samaritan. Stopping my good works.")

                    closeclientConnection(neighbor_socket) #close my given port (my side sustained connection as their neighbor)

       

    except OSError:
        #If binding fails



#client
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

if __name__ == "__main__":
    main()
