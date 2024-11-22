import osmnx as ox
import os
import socket
import struct

server_ip = '127.0.0.1'  
server_port = 10714      
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

print("Ottengo il grafo...")
place_name = "Città Studi, Milan, Italy"
graph = ox.graph_from_place(place_name, network_type='all')
print("Grafo ricevuto, salvo il file...")
filepath='graph.graphml'
ox.save_graphml(graph, filepath)
#ox.save_graph_osm(graph, "gr.osm")


file_size = os.path.getsize(filepath)

#+12 poiché la size comprende anche dimensione header (4byte) e ci sono due interi da 4 byte
file_size_bytes = struct.pack("!i", file_size+12)

source = 790
dest = 1535
source_dest_bytes = struct.pack("!ii", source, dest)

#lettura file grafo salvato precedentemente
with open('graph.graphml', 'rb') as f:
    graph_data = f.read()

#invio header
print("Invio al server dimensione grafo..")
client_socket.sendall(file_size_bytes)
data = client_socket.recv(1024)
if data and data.decode('utf-8') == 'ok':
    print(f"Messaggio ricevuto: {data.decode('utf-8')}")

    #invio body
    print("Invio grafo in corso...")
    data = source_dest_bytes + graph_data
    client_socket.sendall(data)

    data = client_socket.recv(1024)
    if data:
        print(f"Messaggio ricevuto: {data.decode('utf-8')}")

client_socket.close()
