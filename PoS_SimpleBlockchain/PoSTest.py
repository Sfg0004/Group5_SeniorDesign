import hashlib
import json
import socket
import threading
import time
from datetime import datetime

# Block represents each 'item' in the blockchain
class Block:
    def __init__(self, index, timestamp, bpm, hash, prev_hash, validator):
        self.index = index
        self.timestamp = timestamp
        self.bpm = bpm
        self.hash = hash
        self.prev_hash = prev_hash
        self.validator = validator

# Blockchain is a series of validated Blocks
blockchain = []
temp_blocks = []

# candidate_blocks handles incoming blocks for validation
candidate_blocks = []

# announcements broadcasts winning validator to all nodes
announcements = []

mutex = threading.Lock()

# validators keeps track of open validators and balances
validators = {}

# SHA256 hashing
# calculate_hash is a simple SHA256 hashing function
def calculate_hash(s):
    h = hashlib.sha256()
    h.update(s.encode('utf-8'))
    hashed = h.digest()
    return hashlib.sha256(hashed).hexdigest()

# calculate_block_hash returns the hash of all block information
def calculate_block_hash(block):
    record = str(block.index) + block.timestamp + str(block.bpm) + block.prev_hash
    return calculate_hash(record)

# generate_block creates a new block using the previous block's hash
def generate_block(old_block, bpm, address):
    t = str(datetime.now())
    new_block = Block(
        index=old_block.index + 1,
        timestamp=t,
        bpm=bpm,
        prev_hash=old_block.hash,
        validator=address,
        hash=''
    )
    new_block.hash = calculate_block_hash(new_block)
    return new_block

# is_block_valid makes sure the block is valid by checking the index
# and comparing the hash of the previous block
def is_block_valid(new_block, old_block):
    if old_block.index + 1 != new_block.index:
        return False

    if old_block.hash != new_block.prev_hash:
        return False

    if calculate_block_hash(new_block) != new_block.hash:
        return False

    return True

def handle_conn(conn):
    address = ''
    
    conn.sendall("Enter token balance:".encode())
    balance = int(conn.recv(1024).decode())

    t = str(datetime.now())
    address = calculate_hash(t)
    validators[address] = balance

    conn.sendall("\nEnter a new BPM:".encode())

    while True:
        bpm = int(conn.recv(1024).decode())

        mutex.acquire()
        old_last_index = blockchain[-1] if blockchain else Block(0, '', 0, '', '', '')
        mutex.release()

        new_block = generate_block(old_last_index, bpm, address)

        if is_block_valid(new_block, old_last_index):
            candidate_blocks.append(new_block)

        conn.sendall("\nEnter a new BPM:".encode())

def pick_winner():
    time.sleep(30)

    mutex.acquire()
    temp = temp_blocks.copy()
    mutex.release()

    lottery_pool = []
    if temp:
        for block in temp:
            if block.validator not in lottery_pool:
                set_validators = validators.copy()
                k = set_validators.get(block.validator, 0)
                lottery_pool.extend([block.validator] * k)

        if lottery_pool:
            lottery_winner = lottery_pool[hash(str(time.time())).int() % len(lottery_pool)]

            for block in temp:
                if block.validator == lottery_winner:
                    mutex.acquire()
                    blockchain.append(block)
                    mutex.release()
                    for _ in validators:
                        announcements.append("\nwinning validator: " + lottery_winner + "\n")
                    break

    mutex.acquire()
    temp_blocks.clear()
    mutex.release()

def main():
    # Create genesis block
    t = str(datetime.now())
    genesis_block = Block(0, t, 0, calculate_block_hash(Block(0, '', 0, '', '', '')), '', '')
    print(genesis_block)    #NEED TO ADD HOW THIS WILL PRINT SUCCESSFULLY
    blockchain.append(genesis_block)

    # Start TCP and serve TCP server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 4444)) #can change port number if we want
    server.listen()

    def handle_candidate_blocks():
        while True:
            if candidate_blocks:
                mutex.acquire()
                temp_blocks.extend(candidate_blocks)
                candidate_blocks.clear()
                mutex.release()

    def handle_pick_winner():
        while True:
            pick_winner()

    threading.Thread(target=handle_candidate_blocks).start()
    threading.Thread(target=handle_pick_winner).start()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_conn, args=(conn,)).start()

if __name__ == "__main__":
    main()
