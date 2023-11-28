import socket
import time
import select
import pickle
from person import Person



HEADER = 10
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
TIMEFORMAT = '%H:%M:%S'
DISCONNECT_MESSAGE = '!DISCONNECT'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

server.listen(10)

sockets_list = [server]
clients = {}

def add_connection(conn, clients):
    try:
        msg = ""
        curr_time = ""
        while True:
            msg_length = conn.recv(HEADER)

            if msg_length: 
                #print(f"[MESSAGE LENGTH] Message Length: {msg_length}")
                msg_length = int(msg_length.decode(FORMAT).strip())

                msg = conn.recv(msg_length).decode(FORMAT)
                current_time = time.strftime(TIMEFORMAT, time.localtime())

                username = [i.name for i in list(clients.values())]

                #print(username)

                if msg in [i.name for i in list(clients.values())]:
                    #print(1)
                    mh, m = convert_message("Username Already Taken. Retry!!")
                    conn.send(mh)
                    conn.send(m.encode(FORMAT))
                    continue
                else:        
                    mh, m = convert_message("Joining the Server!!")
                    conn.send(mh)
                    conn.send(m.encode(FORMAT))
                    break

        user = Person(name=msg, ip=conn, connected_time=current_time)
        print(f"[NEW USER] {user}")

        return user
        
    except Exception as e:
        print(f"[ERROR] Error Occured: {str(e)}")
        return False
    
def receive_message(conn, clients):

    try:
        msg_length = conn.recv(HEADER)
        
        if msg_length: 
            #print(f"[MESSAGE LENGTH] Message Length: {msg_length}")
            msg_length = int(msg_length.decode(FORMAT).strip())

            msg = conn.recv(msg_length).decode(FORMAT)
            current_time = time.strftime(TIMEFORMAT, time.localtime())
            print(f"[NEW MESSAGE] Message from {clients[conn].name} at {current_time} >>> {msg}")

            return {"time": current_time, "message": msg, "username": clients[conn].name}
        else:
            return False
    except Exception as e:
        print(f"[ERROR] Error Occured: {str(e)}")
        return False
    
def convert_message(msg):
    msg_header = bytes(str(len(msg)), FORMAT)
    msg_header += b' ' * (HEADER - len(msg_header))

    return msg_header, msg

print(f"[SERVER LISTENING] Listening on {SERVER}: {PORT}")

while True:
    read_sockets, write_sockets, exceptional_sockets = select.select(sockets_list, sockets_list, sockets_list)
    # print('*'*10)
    # print(read_sockets, write_sockets, exceptional_sockets)
    # print('*'*10)
    for read_socket in read_sockets:
        if read_socket is server:
            conn, addr = server.accept()
            user = add_connection(conn, clients)

            if user == False:
                print("[CONNECTION CLOSED] Connection not established to server")
                continue

            sockets_list.append(conn)
            clients[conn] = user

        else:
            data = receive_message(read_socket, clients)
            if data == False: 
                print("[CONNECTION CLOSED] Connection not established to client")
                sockets_list.remove(read_socket)
                del clients[read_socket]
                continue
            
            if DISCONNECT_MESSAGE in data["message"]:
                print("[USER QUIT] Connection closed by User")
                sockets_list.remove(read_socket)
                del clients[read_socket]
                continue

            
            data = pickle.dumps(data)
            msg_header, msg = convert_message(data)

            for curr_socket in sockets_list:
                if curr_socket != read_socket and curr_socket != server:
                    try:
                        curr_socket.send(msg_header)
                        curr_socket.send(msg)
                    except:
                        print(f"[USER REMOVED] {clients[curr_socket].name}")
                        del clients[curr_socket]
                        sockets_list.remove(curr_socket)

    for e_sock in exceptional_sockets:
        del clients[e_sock]
        sockets_list.remove(e_sock)
        print(f"[USER REMOVED] {clients[e_sock].name}")






        
        


