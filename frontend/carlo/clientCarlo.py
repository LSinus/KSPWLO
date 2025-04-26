import struct

from geopy import Nominatim
import argparse
from graph_utils import calc_min_dist_osmid
from HGICarlo import HierarchicalGraphCarlo
from network_utils import send_data, receive_data, parse_data
import socket
import time
import os
import csv
import networkx as nx
import osmnx as ox

DEFAULT_PATH = "files/resultGraph.graphml"

class carloClient:
    def __init__(self, host_server_ip, host_server_port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host_server_ip, host_server_port))
        self.G = None
        self.theta = None
        self.k = None
        self.countOPP = 0
        self.countESX = 0
        self.countPen = 0
        self.countAss = 0

    def set_params(self, start_loc, end_loc):
        self.start_loc = start_loc
        self.end_loc = end_loc
        self.theta = 0.5
        self.k = 7


    def calculate_routes(self):

        self.G = HierarchicalGraphCarlo()
        print("[INFO]: Graph received...")
        print("[INFO]: Calculating source and target OSMID...")
        start = os.environ.get("START")
        end = os.environ.get("END")
        (source, dest) = calc_min_dist_osmid(start.latitude, start.longitude, end.latitude, end.longitude,
                                             self.G.get_filepath())
        print("[INFO]: Done...")

        print("[INFO]: Preparing data for server...")
        source_dest_bytes = struct.pack("!QQfi", source, dest, self.theta, self.k)
        graph_size = self.G.get_graph_size()

        data = source_dest_bytes + self.G.get_graph_data()
        print("[INFO]: Sending data...")
        self.initial_timestamp = time.time()
        send_data(self.client_socket, data, graph_size)

        self.receive_results()

    def receive_results(self):

        try:
            results = receive_data(self.client_socket)
            diffTime = time.time() - self.initial_timestamp
            self.countAss += 1
            if(results is None):
                return
            for result in results:
                if result.alg_name=="onepass_plus":
                    self.countOPP +=1
                    self.saveOnCsv(result.alg_name, diffTime, self.countOPP, self.countAss)
                if result.alg_name=="esx":
                    self.countESX +=1
                    self.saveOnCsv(result.alg_name, diffTime, self.countESX, self.countAss)
                if result.alg_name=="penalty":
                    self.countPen +=1
                    self.saveOnCsv(result.alg_name, diffTime, self.countPen, self.countAss)
        except BlockingIOError:
            pass
        self.receive_results()

    def saveOnCsv(self, algName, timestamp, relNum, assNum):
        new_row = [algName, timestamp, relNum, assNum]
        file_exists = os.path.isfile('time.csv')
        with open('time.csv', 'a', newline='') as f:
            writer = csv.writer(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if not file_exists:
                writer.writerow(['Algorithm', 'Timestamp (s)', 'Relative number path', 'Absolute number path'])
            writer.writerow(new_row)

if __name__ == "__main": 
    host_server_ip = '127.0.0.1'
    host_server_port = 10714
    local_map = False

    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', type=str, help='Server IP address')
    parser.add_argument('-p', type=int, help='Server port')
    parser.add_argument('-l','--local', action="store_true", help='local saved graph')
    args=parser.parse_args()
    if args.ip:
        host_server_ip=args.ip
    if args.local:
        local_map=True
    if args.p:
        host_server_port=args.p
    carloClient(host_server_ip,host_server_port)