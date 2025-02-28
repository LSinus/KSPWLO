from typing import List
import osmnx as ox
import os
import re
import socket
import struct
import random
from dataclasses import dataclass

@dataclass
class Result:
    alg_name: str
    num_result: int
    list_osmid: List[int]

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
           return body

def parse_data(data):
    results_by_alg = []
    for item in re.split(r'[ \n]+', data):
        list_osmid = []
        tmp =  item.split(',')
        alg_name = tmp[0]
        num_result = int(tmp[1])
        osmids = tmp[2:]
        for osmid in osmids:
            list_osmid.append(int(osmid))
        result = Result(
            alg_name,
            num_result,
            list_osmid
        )
        results_by_alg.append(result)
        result = []
    return results_by_alg
    


def create_parameters(s = random.randint(1, 100), t = random.randint(1, 100), k = random.randint(1, 10), theta = round(random.uniform(0.1, 1), 2)) -> bytes:
    return struct.pack("!iifi", s, t, theta, k)

# server_ip = '127.0.0.1'  
# server_port = 10714      
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_socket.connect((server_ip, server_port))

# print("Ottengo il grafo...")
# place_name = "Milan, Italy"
# graph = ox.graph_from_place(place_name, network_type='drive')
# print("Grafo ricevuto, salvo il file...")
# filepath='graph.graphml'
# ox.save_graphml(graph, filepath)
# #ox.save_graph_osm(graph, "gr.osm")

# from modify_graphml import add_osmid, calc_min_dist_osmid
# add_osmid(filepath, filepath)


# source = int(calc_min_dist_osmid(45.4834, 9.1902))
# dest = int(calc_min_dist_osmid(45.4807, 9.1869))

# print(str(source) + " " + str(dest))
# theta = 0.2
# k = 3
# source_dest_bytes = struct.pack("!QQfi", source, dest, theta, k)



# graph_size = os.path.getsize(filepath)

#lettura file grafo salvato precedentemente
# with open('graph.graphml', 'rb') as f:
#     graph_data = f.read()

# data = source_dest_bytes + graph_data
#send_data(client_socket, data, graph_size)
# for i in range(1,8):
#     for j in range(0,10):
#         send_data(client_socket, create_parameters(k=i, theta=round((1-j/10),2)))

#receive_data(client_socket)

#client_socket.close()



if __name__ == '__main__':
    mock_data = "onepass+,0,2066388944,2633996002,259846455,1479259661,2739493091,1725740922,21225885,2092324665,21226625,21458333,252632613,252632608,252632615,31509029,2792536452 onepass+,1,2066388944,259846462,2066388928,469526695,469526715,308836023,25543581,25543667,21294891,1322083137,29797362,1790586954,1790586951,1790586941,1652774811,1790586917,1677491063,21293707,21293706,21555835,21226625,21458333,252632613,252632615,31509029,2792536452\nesx+,0,2066388944,2633996002,259846455,1479259661,2739493091,1725740922,21225885,2092324665,21226625,21458333,252632613,252632608,252632615,31509029,2792536452\nesx+,1,2066388944,259846462,2066388928,469526695,469526715,308836023,25543581,25543667,21294891,1322083137,29797362,1790586954,1790586951,1790586941,1652774811,1790586917,1677491063,21293707,21293706,21555835,21226625,21458333,90626661,3265935171,252632608,252632615,31509029,2792536452\npenalty,0,2066388944,2633996002,259846455,1479259661,2739493091,1725740922,21225885,2092324665,21226625,21458333,252632613,252632608,252632615,31509029,2792536452\npenalty,1,2066388944,259846462,2066388928,469526695,469526715,308836023,25543581,25543667,21294891,1322083137,29797362,1790586954,1790586951,1790586941,1652774811,1790586917,1677491063,21293707,21293706,21555835,21226625,21458333,252632613,252632615,31509029,2792536452"
    result = parse_data(mock_data)
    print(result)
