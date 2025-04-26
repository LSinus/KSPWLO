# Nominatim is a geocoder based on OSM, it is used to convert place names into geographic coordinates
# (geocoding) and otherwise (reverse geocoding).

import argparse
import osmnx as ox 
import sys
import io
import folium
import os
import socket
import struct
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QMainWindow, QInputDialog, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import bisect
from PyQt5.QtCore import QSocketNotifier
from graph_utils import add_osmid, calc_min_dist_osmid
from utils import rgb_to_hex
from network_utils import send_data, receive_data, parse_data
from PyQt5.QtCore import QTimer
from hierarchicalGraphImpl import HierarchicalGraph


class AppIntegrata(QMainWindow):
    def __init__(self, host_server_ip, host_server_port, local_map, graphPath = None):
        super().__init__()
        #opening the connection

        self.m = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host_server_ip, host_server_port))
        self.local_map = local_map
        self.G = None
        
        if self.local_map:
            print("[INFO]: Loading Graph from cache...")
            self.G = HierarchicalGraph(path = graphPath)
            print("[INFO]: Graph loaded...")

        self.setWindowTitle("SuperMap")
        self.resize(800, 600)
        self.theta=None
        self.k=None
        #main layout
        layout=QVBoxLayout()

        #place input
        self.start_input=QLineEdit(self)
        self.start_input.setPlaceholderText("Partenza da...")
        layout.addWidget(self.start_input)

        self.end_input=QLineEdit(self)
        self.end_input.setPlaceholderText("Arrivo a...")
        layout.addWidget(self.end_input)

        #button for number of paths
        button_number_path=QPushButton("Scegliere numero percorsi da calcolare")
        button_number_path.clicked.connect(self.showNumberRange)
        layout.addWidget(button_number_path)

        #button for overlap
        self.sovr_input=QLineEdit(self)
        self.sovr_input.setPlaceholderText("Inserire la massima sovrapposizione")
        layout.addWidget(self.sovr_input)
    
        #button for map generation
        self.button=QPushButton("Genera Mappa", self)
        self.button.clicked.connect(self.generate_map)
        layout.addWidget(self.button)

        self.webview=QWebEngineView()
        layout.addWidget(self.webview)

        #central layout
        container=QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.show_default_map()


    def show_default_map(self):
        m_default=folium.Map(location=[45.4642, 9.1900], zoom_start=12)
        m_default.save("files/default_map.html")
        data_default=io.BytesIO()
        m_default.save(data_default, close_file=False)
        self.webview.setHtml(data_default.getvalue().decode())

    
    def showNumberRange(self):
        data, ok =QInputDialog.getInt(self, "Numero percorsi", "k", 5, 1, 15) #it returns a tuple: the first number is the value, the second one true or false
        self.k=data #saved in class attribute in order to use it later
        print(f"[INFO]: Number of path saved: {self.k}")

    def show_error(self, message):
        error_dialog=QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()


    def generate_map(self):
        #saving the overlap
        sovr_value=self.sovr_input.text()
        try:
            theta_value=float(sovr_value)
            if 0<=theta_value<=1:
                self.theta=theta_value
            else:
                self.show_error("Errore: sovrapposizione tra 0 e 1")
                return
        except ValueError:
            self.show_error("Errore: Inserisci un numero valido per la sovrapposizone (decimale tra 0 e 1)")
            return 

        #new Nominatim client
        geolocator=Nominatim(user_agent="geoapp")
        #saving start and destination
        start_loc=self.start_input.text() #prese da input
        end_loc=self.end_input.text()

        start=geolocator.geocode(start_loc) #converting in latitude and longitude
        end=geolocator.geocode(end_loc)
        '''source_lat = start.latitude
        source_lon = start.longitude
        dest_lat = end.latitude
        dest_lon = end.longitude'''
        (source, dest, (source_lat, source_lon), (dest_lat, dest_lon)) = calc_min_dist_osmid(start.latitude, start.longitude, end.latitude,
                                                                       end.longitude, self.G.get_filepath())
        if self.G is None or not self.G.compare_trip(start, end):
            if not self.local_map:
                self.G = HierarchicalGraph(start, end)
                print("[INFO]: Graph received...")

            print("[INFO]: Calculating source and target OSMID...")
            #(source, dest, source_coord, dest_coord) = calc_min_dist_osmid(start.latitude, start.longitude,end.latitude,end.longitude, self.G.get_filepath())
            #points = ox.nearest_nodes(self.G.graph, [start.latitude, end.latitude], [start.longitude, end.longitude])
            #source = points[0]
            #dest = points[1]
            print("[INFO]: Done...")

            print("[INFO]: Preparing data for server...")
            source_dest_bytes = struct.pack("!QQfi", source, dest, self.theta, self.k)
            graph_size = self.G.get_graph_size()

            data = source_dest_bytes + self.G.get_graph_data()
            print("[INFO]: Sending data...")
            send_data(self.client_socket, data, graph_size)
            print("[INFO]: Done")
            self.G.save_cache()
            self.G.set_start_dest_names(start, end)

        else:
            print("[INFO]: SOURCE and DEST already contained in graph...")
            print("[INFO]: Calculating source and target OSMID...")
          #  (source, dest, (source_lat, source_lon), (dest_lat, dest_lon)) = calc_min_dist_osmid(start.latitude, start.longitude, end.latitude, end.longitude,self.G.get_filepath())
            print("[INFO]: Done...")
            print("[INFO]: Preparing data for server...")
            source_dest_bytes = struct.pack("!QQfi", source, dest, self.theta, self.k)
            print("[INFO]: Sending data...")
            send_data(self.client_socket, source_dest_bytes)
            print("[INFO]: Done")

        

        #calculating zoom
        distance_km=geodesic((start.latitude, start.longitude), (end.latitude, end.longitude)).km
        print(f"[INFO]: Distance (km): {distance_km}")
        distance_limit=[0.5, 1, 5, 20, 50, 150, 200, 300, 400, 500, 600, 700]
        zoom_levels=[16, 15, 14, 13, 12, 11, 9, 8, 7, 6, 5, 4, 3]
        index = bisect.bisect_left(distance_limit, distance_km) #bisect executes a binary search of distance_km getting the index
        # Return the corresponding zoom level
        zoom_level=zoom_levels[min(index, len(zoom_levels) - 1)]

        self.m = folium.Map(location=[(start.latitude + end.latitude) / 2, (start.longitude + end.longitude) / 2],zoom_start=zoom_level)
        # adding marker for source and destination

        folium.Marker(location=[source_lat, source_lon], popup="PARTENZA",
                      icon=folium.Icon(color="green")).add_to(self.m)
        folium.Marker(location=[dest_lat, dest_lon], popup="ARRIVO",
                      icon=folium.Icon(color="green")).add_to(self.m)

        self.update_map()
        #when the socket is ready to be read, the signal activated is given, so it is
        # linked to this signal the receive_results() function
        #fileno() methods for socket returns the id of the socket we are using, so we are
        # asking QSocketNotifier to track the activity of the socket of our connection
        ##self.notifier=QSocketNotifier(self.client_socket.fileno(), QSocketNotifier.Read)
        ##self.notifier.activated.connect(self.receive_results)
        self.receive_results()
        #self.result_timer=QTimer() #timer creation
        #self.result_timer.timeout.connect(self.receive_results)
        #self.result_timer.start(100) #check every 100ms


    def update_map(self):
        data=io.BytesIO()
        self.m.save(data, close_file=False)
        # adding the QWebEngineView to the existing layout
        self.webview.setHtml(data.getvalue().decode())

    def receive_results(self):
        try:
            results=receive_data(self.client_socket)
            if(results is None):
                #self.result_timer.stop()
                return
            #print(results)
            for result in results:
                #onepass+ esx penalty
                if result.alg_name=="onepass_plus":
                    route_coords=[(self.G.graph.nodes[node]['y'], self.G.graph.nodes[node]['x']) for node in result.list_osmid]
                    folium.PolyLine(locations=route_coords, color=rgb_to_hex(255, (20*result.num_result)%255, 0), weight=6, opacity=1).add_to(self.m)
                    folium.Marker(
                        location=route_coords[len(route_coords)//2],
                        popup=f"onePass risultato n° {result.num_result+1}",
                        icon=folium.Icon(color="red"), icon_size=(40, 40)).add_to(self.m)

                elif result.alg_name=="esx":
                    route_coords=[(self.G.graph.nodes[node]['y'], self.G.graph.nodes[node]['x']) for node in result.list_osmid]
                    folium.PolyLine(locations=route_coords, color=rgb_to_hex((20*result.num_result)%255, 0, 255-10*result.num_result), weight=4, opacity=1).add_to(self.m)
                    folium.Marker(
                        location=route_coords[len(route_coords)//2],
                        popup=f"esx risultato n° {result.num_result+1}",
                        icon=folium.Icon(color="blue"), icon_size=(40, 40)).add_to(self.m)

                elif result.alg_name=="penalty":
                    route_coords=[(self.G.graph.nodes[node]['y'], self.G.graph.nodes[node]['x']) for node in result.list_osmid]
                    folium.PolyLine(locations=route_coords, color=rgb_to_hex(0, 255, (20*result.num_result)%255), weight=8, opacity=1).add_to(self.m)
                    folium.Marker(
                        location=route_coords[len(route_coords)//2],
                        popup=f"penalty risultato n° {result.num_result+1}",
                        icon=folium.Icon(color="green"), icon_size=(40, 40)).add_to(self.m)
            self.update_map()


        except BlockingIOError:
            pass
        self.receive_results()


if __name__ == "__main__":
    host_server_ip = '127.0.0.1'
    host_server_port = 10714
    local_map = False
    path=None

    parser=argparse.ArgumentParser()
    parser.add_argument('-ip', type=str, help='Server IP address')
    parser.add_argument('-p', type=int, help='Server port')
    parser.add_argument('-l','--local', action="store_true", help='local saved graph')
    parser.add_argument('-g', help='path to graph file')
    args=parser.parse_args()
    if args.g:
        path=args.g
    if args.ip:
        host_server_ip=args.ip
    if args.local:
        local_map=True
    if args.p:
        host_server_port=args.p


    app = QApplication(sys.argv)
    window = AppIntegrata(host_server_ip, host_server_port, local_map, path)
    window.show()

    sys.exit(app.exec_())




        