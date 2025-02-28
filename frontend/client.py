import osmnx as ox
import os
import socket
import struct
import random

def send_data(socket, data, graph_size=0):
    msg_size_bytes = struct.pack("!i", graph_size+28)
    print("Invio al server dimensione messaggio..")
    socket.sendall(msg_size_bytes)
    response = socket.recv(1024)

    if response and response.decode('utf-8') == 'ok':
        print(f"Messaggio ricevuto: {response.decode('utf-8')}")
        client_socket.sendall(data)
        response = client_socket.recv(1024)
        if response and response.decode('utf-8') == 'ok':
            print(f"Messaggio ricevuto: {response.decode('utf-8')}")

def receive_data(socket):
    header = socket.recv(1024)
    if header:
        size = int(header.decode('utf-8'))
        
        print(size)
        res = 'ok'
        socket.sendall(res.encode('utf-8'))
        body = socket.recv(size)
        if body:
            print(body.decode('utf-8'))
    


def create_parameters(s = random.randint(1, 100), t = random.randint(1, 100), k = random.randint(1, 10), theta = round(random.uniform(0.1, 1), 2)) -> bytes:
    return struct.pack("!iifi", s, t, theta, k)

server_ip = '127.0.0.1'  
server_port = 10714      
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

print("Ottengo il grafo...")
place_name = "Milan, Italy"
graph = ox.graph_from_place(place_name, network_type='drive')
print("Grafo ricevuto, salvo il file...")
filepath='graph.graphml'
ox.save_graphml(graph, filepath)
#ox.save_graph_osm(graph, "gr.osm")

from modify_graphml import add_osmid, calc_min_dist_osmid
add_osmid(filepath, filepath)


source = int(calc_min_dist_osmid(45.4834, 9.1902))
dest = int(calc_min_dist_osmid(45.4807, 9.1869))

print(str(source) + " " + str(dest))
theta = 0.2
k = 3
source_dest_bytes = struct.pack("!QQfi", source, dest, theta, k)


graph_size = os.path.getsize(filepath)

#lettura file grafo salvato precedentemente
with open('graph.graphml', 'rb') as f:
    graph_data = f.read()

data = source_dest_bytes + graph_data
send_data(client_socket, data, graph_size)
# for i in range(1,8):
#     for j in range(0,10):
#         send_data(client_socket, create_parameters(k=i, theta=round((1-j/10),2)))

receive_data(client_socket)

client_socket.close()
