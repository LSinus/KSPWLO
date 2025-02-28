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
from geopy.geocoders import Nominatim
from pprint import pprint
from geopy.distance import geodesic



class AppIntegrata(QMainWindow):
    def __init__(self, host_server_ip, host_server_port):
        self.host_server_ip=host_server_ip
        self.host_server_port=host_server_port
        super().__init__()
        self.setWindowTitle("SuperMap")
        self.resize(1600, 1200)
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
        m_default.save("default_map.html")
        data_default=io.BytesIO()
        m_default.save(data_default, close_file=False)
        self.webview.setHtml(data_default.getvalue().decode())

    
    def showNumberRange(self):
        data, ok =QInputDialog.getInt(self, "Numero percorsi", "k", 5, 1, 15) #it returns a tuple: the first number is the value, the second one true or false
        self.k=data #saved in class attribute in order to use it later
        print(f"Numero percorsi salvato: {self.k}")

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
            self.show_error("Errore: Inserisci un nuero valido per la sovrapposizone (decimale tra 0 e 1)")
            return 
        
        #opening the connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host_server_ip, self.host_server_port)) #uso argomenti passati per parametro
        
        #new Nominatim client
        geolocator=Nominatim(user_agent="geoapp")

        #saving start and destination
        start_loc=self.start_input.text() #prese da input
        end_loc=self.end_input.text()

        start=geolocator.geocode(start_loc) #converting in latitude and longitude
        end=geolocator.geocode(end_loc)

        pprint(start)
        pprint(end)

        print("Ottengo il grafo...")
        margin=0.001
        min_lat = min(start.latitude, end.latitude) - margin
        max_lat = max(start.latitude, end.latitude) + margin
        min_lon = min(start.longitude, end.longitude) - margin
        max_lon = max(start.longitude, end.longitude) + margin
        G = ox.graph_from_bbox(max_lat, min_lat, max_lon, min_lon, network_type='drive')
        print("Grafo ricevuto, salvo il file...")
        filepath='G.graphml'
        ox.save_graphml(G, filepath)

        from graph_utils import add_osmid, calc_min_dist_osmid
        add_osmid(filepath, filepath)
        source = int(calc_min_dist_osmid(start.latitude, start.longitude))
        dest = int(calc_min_dist_osmid(end.latitude, end.longitude))
        print(str(source) + " " + str(dest))
        source_dest_bytes = struct.pack("!QQfi", source, dest, self.theta, self.k)
        graph_size = os.path.getsize(filepath)

        from network_utils import send_data, receive_data, parse_data
        with open('G.graphml', 'rb') as f:
            graph_data = f.read()
        data = source_dest_bytes + graph_data
        send_data(client_socket, data, graph_size)

        results=receive_data(client_socket)

        #calculating zoom
        distance_km=geodesic((start.latitude, start.longitude), (end.latitude, end.longitude)).km
        print(distance_km)
        if distance_km < 0.5:
            zoom_level = 19
        elif distance_km<1:
            zoom_level=17
        elif distance_km<5:
            zoom_level=16
        elif distance_km<20:
            zoom_level=14
        elif distance_km<50:
            zoom_level=12
        elif distance_km<150:
            zoom_level=11
        elif distance_km<200:
            zoom_level=10
        elif distance_km<300:
            zoom_level=9
        elif distance_km<400:
            zoom_level=8
        elif distance_km<500:
            zoom_level=7
        elif distance_km<600:
            zoom_level=6
        elif distance_km<700:
            zoom_level=5
        else:
            zoom_level=4
        
        m=folium.Map(location=[(start.latitude+end.latitude)/2, (start.longitude+end.longitude)/2], zoom_start=zoom_level)
        #adding marker for source and destination
        folium.Marker(location=[start.latitude, start.longitude], popup= "PARTENZA", 
            icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(location=[end.latitude, end.longitude], popup= "ARRIVO", 
            icon=folium.Icon(color="green")).add_to(m)

        for result in results:
            #onepass+ esx penalty
            if result.alg_name=="onepass+":
                route_coords=[(G.nodes[node]['y'], G.nodes[node]['x']) for node in result]
                folium.PolyLine(locations=route_coords, color="red", weight=5, opacity=1).add_to(m)
                folium.Marker(
                    location=route_coords[len(route_coords)//2], 
                    popup=f"onePass risultato n° {result.num_result}",
                    icon=folium.Icon(color="red"), icon_size=(40, 40)).add_to(m)
            
            elif result.alg_name=="esx":
                route_coords=[(G.nodes[node]['y'], G.nodes[node]['x']) for node in result]
                folium.PolyLine(locations=route_coords, color="blue", weight=5, opacity=1).add_to(m)
                folium.Marker(
                    location=route_coords[len(route_coords)//2], 
                    popup=f"onePass risultato n° {result.num_result}",
                    icon=folium.Icon(color="blue"), icon_size=(40, 40)).add_to(m)
            
            elif result.alg_name=="penalty":
                route_coords=[(G.nodes[node]['y'], G.nodes[node]['x']) for node in result]
                folium.PolyLine(locations=route_coords, color="green", weight=5, opacity=1).add_to(m)
                folium.Marker(
                    location=route_coords[len(route_coords)//2], 
                    popup=f"onePass risultato n° {result.num_result}",
                    icon=folium.Icon(color="green"), icon_size=(40, 40)).add_to(m)

        
        #save map data to data object
        data=io.BytesIO()
        m.save(data, close_file=False)

         # adding the QWebEngineView to the existing layout
        self.webview.setHtml(data.getvalue().decode())

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('-hip', type=str, help='IP del server')
    parser.add_argument('-hp', type=str, help='Porta del server')
    args=parser.parse_args()
    if args.hip:
        host_server_ip=args.hip
    else:
        host_server_ip='127.0.0.1' 
    
    if args.hp:
        host_server_port=args.hp
    else:
        host_server_port=10714

    app = QApplication(sys.argv)
    window = AppIntegrata(host_server_ip, host_server_port)
    window.show()

    sys.exit(app.exec_())




        