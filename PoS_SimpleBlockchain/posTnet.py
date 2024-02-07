import hashlib
import json
import socket
import time
import random
import threading
from datetime import datetime
from queue import Queue
import netifaces as ni

# Block represents each 'item' in the blockchain
class Block:
    def __init__(self, index, timestamp, bpm, prev_hash, validator):
        self.index = index
        self.timestamp = timestamp
        self.bpm = bpm
        self.prev_hash = prev_hash
        self.validator = validator
        self.hash = self.calculate_block_hash()

    # calculateHash is a simple SHA256 hashing function
    def calculate_hash(self, s):
        h = hashlib.sha256()
        h.update(s.encode('utf-8'))
        return h.hexdigest()


    # calculateBlockHash returns the hash of all block information
    def calculate_block_hash(self):
        record = str(self.index) + self.timestamp + str(self.bpm) + self.prev_hash
        return self.calculate_hash(record)

# Blockchain is a series of validated Blocks
blockchain = []
blockDisplay = []
temp_blocks = []

#client tcp address array
nodes = []

# candidate_blocks handles incoming blocks for validation
candidate_blocks = []
candidate_blocks_lock = threading.Lock()

# announcements broadcasts winning validator to all nodes
announcements = []

validator_lock = threading.Lock()

# validators keeps track of open validators and balances
validators = {}

# generate_genesis_block creates the genesis block
def generate_genesis_block():
    t = str(datetime.now())
    genesis_block = Block(0, t, 0, "", "")
    return genesis_block

# generate_block creates a new block using the previous block's hash
def generate_block(old_block, bpm, address):
    t = str(datetime.now())
    new_block = Block(old_block.index + 1, t, bpm, old_block.hash, address)
    return new_block

def printBlockchain(conn):
    for block in blockchain:
        print(block.index)
        io_write(conn, block.index)
        io_write(conn, block.timestamp)
        io_write(conn, block.bpm)
        io_write(conn, block.prev_hash)
        io_write(conn, block.validator)
        io_write(conn, block.hash)

# is_block_valid makes sure the block is valid by checking the index
# and comparing the hash of the previous block
def is_block_valid(new_block, old_block):
    if old_block.index + 1 != new_block.index:
        return False

    if old_block.hash != new_block.prev_hash:
        return False

    if new_block.calculate_block_hash() != new_block.hash:
        return False

    return True

def handle_conn(conn):
    try:
        address = ""

        # Allow the user to allocate the number of tokens to stake
        io_write(conn, "ASKING FROM HANDLECONN\n")
        io_write(conn, "Enter token balance:")
        balance = int(conn.recv(1024).decode('utf-8'))

        t = str(datetime.now())
        address = calculate_hash(t)

        with validator_lock:
            validators[address] = balance
            print(validators)

        io_write(conn, "\nEnter a new BPM:")

        while True:
            # Take in BPM from the client and add it to the blockchain after conducting necessary validation
            bpm = int(conn.recv(1024).decode('utf-8'))
            with validator_lock:
                old_last_index = blockchain[-1]
            new_block = generate_block(old_last_index, bpm, address)

            if is_block_valid(new_block, old_last_index):
                candidate_blocks.append(new_block)
                io_write(conn, "\nValue is valid\n")
                #break
                
            else:
                 io_write(conn, "\nNot a valid input.\n")
            #io_write(conn, "\nEnter a new BPM:")
            
            #io_write(conn, "\nSTUCK IN HANDLECONN")

    except Exception as q:
        print(f"Connection closed: {q}")
        io_write(conn, "Connection closing...\n")
        conn.close()

# pick_winner creates a lottery pool of validators and chooses the validator who gets to forge a block to the blockchain
def pick_winner():
    print("\nPicking winner...")
    while True:
        time.sleep(10)
            
        with validator_lock:    
            print("\nPicking winner...1")
            if len(validators) > 0:
                print("\nPicking winner...2")
                lottery_winner = max(validators, key=validators.get)
                print("\nPicking winner...3")

                with candidate_blocks_lock:
                    print("\nPicking winner...4")
                    global temp_blocks
                    print("\nPicking winner...5")
                    temp_blocks = list(candidate_blocks)
                    print("\nPicking winner...6")
                    candidate_blocks.clear()

                for block in temp_blocks:
                    print("\nPicking winner...7")
                    if block.validator == lottery_winner:
                        print("\nPicking winner...8")
                        #with validator_lock:
                        print("\nPicking winner...9")
                        blockchain.append(block)
                        blockDisplay.append

                        print("\nPicking winner...abc")
                        #for _ in validators:
                        for x in nodes:
                            print("\nPicking winner...10")
                            io_write(x, "\nwinning validator: " + lottery_winner + "\n")
                            printBlockchain(x)
                            #for block in blockchain:
                            #    io_write(x, block.hash)
                            #    io_write(x, "\n")
                            #announcements.append("\nwinning validator: " + lottery_winner + "\n")
                        print("\nPicking winner...11")
                        break
        print("\nPicking winner...12")

def io_write(conn, message):
    conn.sendall(message.encode('utf-8'))

def calculate_hash(s):  # Added this function
    h = hashlib.sha256()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

def main():
    # Create genesis block
    genesis_block = generate_genesis_block()
    blockchain.append(genesis_block)

    # Start TCP server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        #this now allows for connections across computers
        ip = ni.ifaddresses('enp0s31f6')[ni.AF_INET][0]['addr']
        print("my ip: " + ip + "\n")
        port = 5555
        server.bind((ip, port))
        server.listen()
        print("Server is running.")
        run_server(server)
        
    except OSError:
        #If binding fails, assume it's a client
        print("Failed to bind, assuming client role.")
        run_client()
        
def run_server(server):
    # Handle candidate blocks in a separate thread
    candidate_thread = threading.Thread(target=lambda: candidate_blocks.append(None) if candidate_blocks else None)
    candidate_thread.start()

    # Pick winner thread
    winner_thread = threading.Thread(target=pick_winner)
    winner_thread.start()
    
    while True:
        print("a")
        conn, addr = server.accept()
        print("b")
        threading.Thread(target=handle_conn, args=(conn,)).start()
        print("c")
        nodes.append(conn)
        print("d")
        print("conns:\n",nodes)
        
#def run_client():
    #Client-side code
 #   client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 #  client.connect((host, port))
    
 #   try:
        # Send token balance
 #       io_write(client, "Enter token balance:")
 #       token_balance = int(client.recv(1024).decode('utf-8'))
  #      io_write(client, str(token_balance))
        
        
        # Send BPM values
 #       while True:
  #          io_write(client, "ASKING FROM RUNCLIENT")
  #          bpm = int(input("Enter a new BPM: "))
   #         io_write(client, str(bpm))
   #         print(client.recv(1024).decode('utf-8'))
            
  #  except Exception as q:
   #     print(f"Client connection closed: {q}")
        
   # finally:
   #     client.close()

if __name__ == "__main__":
    main()
