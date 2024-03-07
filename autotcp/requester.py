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


# Blockchain is a series of validated Blocks
blockchain = []

#client ip address array
nodelist = [] #local list of node objects
iplist = [] #ips only - for sending & receiving node update between nodes
#change to dictionary

class nodes:
     def __init__(self, ip, latency, neighbor, port):
        self.ip = ip
        self.latency = latency
        self.neighbor = neighbor
        self.port = port


# candidate_blocks handles incoming blocks for validation
candidate_blocks = []
candidate_blocks_lock = threading.Lock()


validator_lock = threading.Lock()

# validators keeps track of open validators and balances
validators = {}

givenport = 1112


# for deciding neighbors
def get_simple_cmd_output(cmd, stderr=STDOUT):
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


def io_write(conn, message):
    conn.sendall(message.encode('utf-8'))

def main():


    requestconnection('146.229.163.145')



    listenconnection()
    #acceptconnection()


    # Start TCP server
    # server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # try:
    #     #this now allows for connections across computers
    #     myip = ni.ifaddresses('enp0s31f6')[ni.AF_INET][0]['addr']
    #     print("my ip: " + myip + "\n")
    #     port = 4329
    #     server.bind((myip, port))
    #     server.listen()
    #     print("Server is running.")
    #     run_server(server)
        
    # except OSError:
    #     #If binding fails, assume it's a client
    #     print("Failed to bind")
        

def handle_conn(conn):
    try:

        print("Connection open")
    except Exception as q:
        print(f"Connection closed: {q}")
        io_write(conn, "Connection closing...\n")
        conn.close()

def run_server(server):
    global iplist
    # Handle candidate blocks in a separate thread
   # candidate_thread = threading.Thread(target=lambda: candidate_blocks.append(None) if candidate_blocks else None)
    #candidate_thread.start()

    # Pick winner thread
  # winner_thread = threading.Thread(target=pick_winner)
   # winner_thread.start()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_conn, args=(conn,)).start()
        tup = addr
        ip = tup[0]
        iplist.append(ip)
        send_iplist(iplist)
        addnode(ip, 0000)

def addnode(ip, port): #local

    req = "{}:4444".format(ip)  # print("req: " + req) troubleshooting

    latsum = 0
    for i in range(3):
        latsum += (get_ping_time(req))
    latency = latsum/3 #avg 3 times
    nodelist.append(nodes(ip,latency, False, 0000))
    for x in nodelist:
        print(x.ip,"{:.3f}".format(x.latency), x.neighbor, x.port)
    local_refresh_iplist(iplist, ip, "add")
        
def deletenode(ip): #local
    for x in nodelist:
        if (node.ip == ip):
            nodelist.remove(x)
            del x
    local_refresh_iplist(iplist, ip, "delete")

def acceptconnection(ip,port):
    global givenport
    #connect = "{}:1111".format(ip) 
    connectport = 1111
    while True: 
       
        myip = ni.ifaddresses('enp0s31f6')[ni.AF_INET][0]['addr']
        BUFFER_SIZE = 256
        MESSAGE = "yes. talk on " + myip + "port: " + givenport
        requester = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        requester.connect((ip, connectport))
        #data = requester.recv(BUFFER_SIZE)
        requester.send(MESSAGE)
        requester.close()
        givenport = givenport+1
        print("sent data:", MESSAGE)
        iplist.append(ip)
        #send_iplist(iplist)
        addnode(ip, givenport)

def listenconnection(ip):

    BUFFER_SIZE = 256
    requester = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    requester.connect((ip, connectport))
    data = requester.recv(BUFFER_SIZE)
    requester.close()
    print("received data:", data)

def requestconnection(ip):
    global givenport
    #connect = "{}:1111".format(ip) 
    connectport = 1111
    while True: 
       
        myip = ni.ifaddresses('enp0s31f6')[ni.AF_INET][0]['addr']
        BUFFER_SIZE = 256
        MESSAGE = "be my neighbor? answer on " + myip + "port: " + givenport
        stranger = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        stranger.connect((ip, connectport))
        stranger.send(MESSAGE)
        stranger.close()
        givenport = givenport+1
        print("sent data:", MESSAGE)


# def refresh_neighbors(nodelist): #local

#     neighborcount = 0
#     for node in nodelist:
#         if (node.neighbor == True):
#             node.neighbor = False
#     lownode = nodelist[0]
#     for i in range(2):
#         if (neighborcount < 2):
#             lowlat = 999 #latency to beat
#             for node in nodelist:
#                 if ((node.latency < lowlat) and (not(node.neighbor))):
#                     lowlat = node.latency
#                     lownode = node
#             lownode.neighbor = True

# def message_refresh_iplist(locallist, receivedlist): #called after iplist recieved from neighbors

#     locallist = order_iplist(locallist) #order inputs
#     receivedlist = order_iplist(receivedlist)

#     refreshedlist = []

#     for ip in locallist:
#         try:
#             receivedlist.index(ip)
#             refreshedlist.append(ip)
#         except:
#             deletenode(ip)


#     for jp in receivedlist:
#         try:
#             locallist.index(jp)
#         except:
#             addnode(jp, port)
#             refreshedlist.append(jp)

#     refreshedlist = order_iplist(refreshedlist)
#     print(refreshedlist)

     
#     #priority - checks own ip presence
#     refresh_neighbors(nodelist)

#     refreshedlist = order_iplist(refreshedlist)
#     return refreshedlist

def local_refresh_iplist(iplist, ip, mode): #called after node locally added or deleted, called every so often per time period..

    if (mode=="add"):
        iplist.append(ip)

    elif (mode=="delete"):
        iplist.remove(ip)
    #priority - checks own ip presence
    refresh_neighbors(nodelist)

    iplist = order_iplist(iplist)

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




if __name__ == "__main__":
    main()
