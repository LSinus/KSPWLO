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
        print("[INFO]: trying to connect...")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host_server_ip, host_server_port))
        print("[INFO]: connected")
        self.G = None
        self.theta = None
        self.k = None
        #because of the fact that evironment variables are String, we have to rebuild the float
        #objects necessary to be used in calc_min_dist
        self.start_lat = float(os.environ.get("START_LAT"))
        self.start_lon = float(os.environ.get("START_LON"))
        self.end_lon = float(os.environ.get("END_LON"))
        self.end_lat = float(os.environ.get("END_LAT"))
        self.set_params()
        self.G = HierarchicalGraphCarlo()
        self.calculate_routes()

    def set_params(self):
        self.theta = 0.5
        self.k = 7


    def calculate_routes(self):
        print("[INFO]: Graph received...")
        print("[INFO]: Calculating source and target OSMID...")
        (source, dest) = calc_min_dist_osmid(self.start_lat, self.start_lon, self.end_lat, self.end_lon, self.G.get_filepath())
        print("[INFO]: Done...")

        print("[INFO]: Preparing data for server...")
        print("[INFO]: source OSMID: "+ str(source) + " dest OSMID: " +str(dest)+ " theta: " + str(self.theta)+ " k: " +str(self.k))
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
            if(results is None):
                return
            for result in results:
                self.saveOnCsv(result.alg_name, diffTime, result.num_result, result.length)
        except BlockingIOError:
            pass
        self.receive_results()

    def saveOnCsv(self, algName, timestamp, relNum, length):
        new_row = [algName, timestamp, relNum, length, os.environ.get('SOURCE'), os.environ.get('DEST')]
        file_exists = os.path.isfile('time.csv')
        with open('time.csv', 'a', newline='') as f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if not file_exists:
                writer.writerow(['Algorithm', 'Timestamp (s)', 'Relative number path', 'length(m)', 'source', 'dest'])
            writer.writerow(new_row)

if __name__ == "__main__":

    host_server_ip = '127.0.0.1'
    host_server_port = 40000
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