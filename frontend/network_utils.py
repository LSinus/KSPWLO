from typing import List
import osmnx as ox
import re
import struct
from dataclasses import dataclass

''' A simple data type to represent the result from the computation of an algorithm,
    the algorithm is specified in the alg_name field, the algorithm trys to calculate
    k results, so the cardinality of the result is specified in the num_result field,
    then the osmids are stored in a list of integers in the field list_osmids 
'''
@dataclass
class Result:
    alg_name: str
    num_result: int
    list_osmid: List[int]


''' The function sends data to the backend in order to calculates the result on the
    graph. First of all a small message is sent communicating the message header with
    message' size as graph_size plus 8 bytes for source, 8 bytes for dest, 4 bytes for theta, 
    4 bytes for k, and 4 bytes for the header size itself. 
    If the backend responds with 'ok' the function sends the real data and waits for 
    another 'ok'
'''
def send_data(socket, data, graph_size=0):
    msg_size_bytes = struct.pack("!i", graph_size + 8 + 8 + 4 + 4 + 4)
    print("[INFO] Sending to the server message size...")
    socket.sendall(msg_size_bytes)
    response = socket.recv(1024)
    if response and response.decode('utf-8') == 'ok':
        print(f"[INFO] Received message: {response.decode('utf-8')}")
        socket.sendall(data)
        response = socket.recv(1024)
        if response and response.decode('utf-8') == 'ok':
            print(f"[INFO] Received message: {response.decode('utf-8')}")

''' The function receives a structured message with the response from the backend.
    First of all, the socket waits for the header, this header contains the total
    size of the message, so if the header is received correctly the function notifies 
    the backend with 'ok' and then the sockets waits for the body. If the body is received 
    correctly the function calls parse_data to parse the message and returns the response.
'''
def receive_data(socket) -> List[Result]:
    header = socket.recv(4)
    if header:
        size = struct.unpack("I", header)[0]
        print('[INFO] Receiving a response of: ' + str(size) + ' bytes')
        res = 'ok'
        socket.sendall(res.encode('utf-8'))
        body = socket.recv(size-4)
        if body:
           return parse_data(body.decode('utf-8'))

''' The function takes a string argument and parses the string in order to create a 
    list of Results, it splits the string with ' ' and '\n' and then extracts the alg_name
    and the num_result, finally it builds the list of osmids from the string.
'''
def parse_data(data):
    if(data == "COMPUTATION_DONE"):
        print("[INFO] Received COMPUTATION_DONE")
        return None
    results_by_alg = []
    for item in re.split(r'[ \n]+', data):
        list_osmid = []
        tmp =  item.split(',')
        if tmp and len(tmp)>1:
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
    return results_by_alg
    
 


if __name__ == '__main__':
    ### EXAMPLE CODE ###

    import socket
    import os

    server_ip = '127.0.0.1'  
    server_port = 10714      
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    
    graph = ox.graph_from_bbox(45.49094, 45.48491, 9.1913, 9.20323, network_type='drive')
    filepath='graph.graphml'
    ox.save_graphml(graph, filepath)
   
    from graph_utils import add_osmid, calc_min_dist_osmid
    add_osmid(filepath, filepath)

    source = int(calc_min_dist_osmid(45.48906, 9.19318, filepath))
    dest = int(calc_min_dist_osmid(45.48744, 9.20065, filepath))

    print(str(source) + " " + str(dest))
    theta = 0.9
    k = 2
    source_dest_bytes = struct.pack("!QQfi", source, dest, theta, k)
    graph_size = os.path.getsize(filepath)

    with open('graph.graphml', 'rb') as f:
        graph_data = f.read()

    data = source_dest_bytes + graph_data
    send_data(client_socket, data, graph_size)
    results = receive_data(client_socket)
    client_socket.close()

    print(results)
