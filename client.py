import socket
import time
import sys
import select
import pickle
import config 


HEADER = 10
PORT = 5050
FORMAT = 'utf-8'
SERVER = config.SERVER ## YOUR IP
DISCONNECT_MESSAGE = '!DISCONNECT'
TIMEFORMAT = '%H:%M:%S'
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
#client.setblocking(False)

sockets_list = [sys.stdin, client]



while True:
    username = input("Enter User Name: ").encode(FORMAT)
    username_length = str(len(username))

    init_msg = bytes(str(username_length), FORMAT)
    init_msg += b' '*(HEADER - len(init_msg))
    setup_msg = username
    client.send(init_msg)
    client.send(setup_msg)
    
    msg_length = client.recv(HEADER)
    if msg_length:
        msg_length = int(msg_length.decode(FORMAT).strip())
        msg = client.recv(msg_length).decode(FORMAT)
        if(msg.startswith("Joining")):
            break

def convert_message(msg):
    msg_header = bytes(str(len(msg)), FORMAT)
    msg_header += b' ' * (HEADER - len(msg_header))
    msg = msg.encode(FORMAT)

    return msg_header, msg

def receive_message(client):
    
    try:
        msg_length = client.recv(HEADER)

        if msg_length: 
            msg_length = int(msg_length.decode(FORMAT).strip())

            msg = client.recv(msg_length)

            msg_object = pickle.loads(msg)

            username = msg_object['username']
            message = msg_object['message']
            time_rcv = msg_object['time']

            print(f"Message from {username} at {time_rcv} >>> {message}")
            return True
        else:
            return False
    except Exception as e:
        print(f"[ERROR] Error Occured: {str(e)}")
        return False

while True: 
    readers, writers, excpetioners = select.select(sockets_list, [], [])
    for reader in readers:
        if reader is client:
            data = receive_message(client)
            if data == False:
                print("Connection Might Be Closed")
                sys.exit()
        else:
            org_message = sys.stdin.readline()
            message_header, message = convert_message(org_message)
            
            client.send(message_header)
            client.send(message)

            if DISCONNECT_MESSAGE in org_message:
                sys.exit()

    















