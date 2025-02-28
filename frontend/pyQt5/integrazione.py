# Nominatim è un geocoder basato su OpenStreetMap (OSM), usato per convertire un nome di località 
# in coordinate geografiche (geocoding) e viceversa (reverse geocoding).

import argparse
import osmnx as ox 
import networkx as nx
import sys
import io
import folium
import os
import socket
import struct
import random
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QMainWindow, QInputDialog, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView 
from geopy.geocoders import Nominatim
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDoubleValidator, QValidator, QIntValidator
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
        self.sovrMax=None #per salvare sovrapposizione dopo
        self.nPath=None #per salvare sovrapposizione dopo
        #main layout
        layout=QVBoxLayout()

        #input località
        self.start_input=QLineEdit(self)
        self.start_input.setPlaceholderText("Partenza da...")
        layout.addWidget(self.start_input)

        self.end_input=QLineEdit(self)
        self.end_input.setPlaceholderText("Arrivo a...")
        layout.addWidget(self.end_input)

        #pulsante numero Percorsi
        button_number_dialog=QPushButton("Scegliere numero percorsi da calcolare")
        button_number_dialog.clicked.connect(self.showNumberDialog)
        layout.addWidget(button_number_dialog)

        #pulsante numero sovrapposizione
        self.sovr_input=QLineEdit(self)
        self.sovr_input.setPlaceholderText("Inserire la massima sovrapposizione")
        layout.addWidget(self.sovr_input)
        # sovr_max = self.sovr_input.text()  # Ottiene il testo dalla casella di input
        # int_sovr_max = int(sovr_max)
    

        #pulsante generazione mappa
        self.button=QPushButton("Genera Mappa", self)
        self.button.clicked.connect(self.generate_map)
        layout.addWidget(self.button)

        self.webview=QWebEngineView()
        layout.addWidget(self.webview)

        #layout centrale
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


    def showNumberDialog(self):
        data, ok =QInputDialog.getInt(self, "Numero percorsi", "k", 5, 1, 15) #ritorna una tupla, il primo numero è il valore, il secondo è true o false
        #print(data)
        self.nPath=data #salvato in attributo di classe pre permettere utilizo successivo
        print(f"Numero percorsi salvato: {self.nPath}")

    def show_error(self, message):
        error_dialog=QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()


    def generate_map(self):
        #otteniamo e salviamo numero sovrapposizione
        sovr_value=self.sovr_input.text()
        try:
            sovrMax_value=float(sovr_value)
            if 0<=sovrMax_value<=1:
                self.sovrMax=sovrMax_value
            else:
                self.show_error("Errore: sovrapposizione tra 0 e 1")
                return
        except ValueError:
            self.show_error("Errore: Inserisci un nuero valido per la sovrapposizone (decimale tra 0 e 1)")
            return #fine codice
        
        #instauriamo connessione 
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host_server_ip, self.host_server_port)) #uso argomenti passati per parametro
        
        #instanziazione di un nuovo client Nominatim
        geolocator=Nominatim(user_agent="geoapp")

        #otteniamo coordinate località
        start_loc=self.start_input.text() #prese da input
        end_loc=self.end_input.text()

        start=geolocator.geocode(start_loc) #converto in latitudine e longitudine
        end=geolocator.geocode(end_loc)

        pprint(start)
        pprint(end)

        

        ######coordinate date per vedere se potesse funzionare######
        # Coordinate per Piola
        #start= (45.4795, 9.2258)  # Latitudine, Longitudine

        # Coordinate per Stazione di Milano Lambrate
        #end= (45.4818, 9.2343)  # Latitudine, Longitudine

        #scarico rete stradale zona, magari ptoremmo mandarcela poi dal backend questa boh
        #place = "Milan, Italy"
        #G = ox.graph_from_place(place, network_type='drive')  
        margin=0.001
        min_lat = min(start.latitude, end.latitude) - margin
        max_lat = max(start.latitude, end.latitude) + margin
        min_lon = min(start.longitude, end.longitude) - margin
        max_lon = max(start.longitude, end.longitude) + margin
        G = ox.graph_from_bbox(max_lat, min_lat, max_lon, min_lon, network_type='drive')
        #invio grafo
       #ricevo nodi osmid_list
        #prendo nodi: anche questi arrivano da backend
        osmid_list = [100946647,100939338,31370859,264008364,31370860,250227860,31370862,100945630,309672310,315283514,2550284520,315283510,250228351,1893394156,1893394085,1893394075,1893394051,21294863,31370772,251618341,251498276,269347380,1602479860,1602479997,309012791,309007305,269704553,267210670,259849976,78465054,249104085,250291806,135876374,96886739,21458298,78465049,250291809,96882681,2947268070,78439701,3876198702,1474064607,78439648,78439650,251329936,251330234,78439657,251335673,78439665,2656255691,295546865,31333370,549904750,252204187,2701893583,11022929817,1474088227,1279803167,31333372,31333375,31333378,31331613,31331628,2804374522,256216288,256226634,256038852,1937808732,2987656912,256069581,256225835,256205288,5025267951,5025267953,344814472,256205280,1756208675,245555961,4042455153,1261908176,679447434,263250798,474850403,2801660602,263250715,365311374,365311893,1847293988,271096746,245570225,271096420,249455922,249455923,2876532972,245570235,245570243,1260843030,1260842924,21225901,21226042,3373943082,6855029571,1467391636,21226863,249455219,2875165077,21226525,21227096,249390273,2807194228,21227303,21227237,1178826490,21227205,21225999,21226791,583223067,583223055,583223046,2719954709,92556422,583223041,2719954692,2396212582,2720033995,1178826643,2720033987,2719972514,2719984816,249360988,249377221,249360989,249361931,249381418,249381358,249381354,249381314,249381313,249381312,1467602584,249381310,660867319]
        # osmid_list = [100946647, 100939338, 31370859, 264008364, 31370860, 250227860, 31370862, 100945630, 309672310, 315283514, 2550284520, 315283510, 250228351, 1893394156, 1893394085, 1893394075, 1893394051, 21294863, 31370772, 251618341, 251498276, 269347380, 1602479860, 1602479997, 309012791, 309007305, 269704553, 267210670, 259849976, 78465054, 249104085, 250291806, 135876374, 96886739, 21458298, 78465049, 250291809, 96882681, 2947268070, 78439701, 3876198702, 1474064607, 78439648, 78439650, 251329936, 251330234, 78439657, 251335673, 78439665, 2656255691, 295546865, 31333370, 549904750, 252204187, 2701893583, 11022929817, 1474088227, 1279803167, 31333372, 31333375, 31333378, 31331613, 31331628, 2804374522, 256216288, 256226634, 256038852, 1937808732, 2987656912, 256069581, 256225835, 256205288, 5025267951, 5025267953, 344814472, 256205280, 1756208675, 245555961, 4042455153, 1261908176, 679447434, 263250798, 474850403, 2801660602, 263250715, 365311374, 365311893, 1847293988, 271096746, 245570225, 271096420, 249455922, 249455923, 2876532972, 245570235, 245570243, 1260843030, 1260842924, 21225901, 21226042, 3373943082, 6855029571, 1467391636, 21226863, 249455219, 2875165077, 21226525, 21227096, 249390273, 2807194228, 21227303, 21227237, 1178826490, 21227205, 21225999, 21226791, 583223067, 583223055, 583223046, 2719954709, 92556422, 583223041, 2719954692, 2396212582, 2720033995, 1178826643, 2720033987, 2719972514, 2719984816, 249360988, 249377221, 249360989, 249361931, 249381418, 249381358, 249381354, 249381314, 249381313, 249381312, 1467602584, 249381310, 660867319]

        route_coords=[(G.nodes[node]['y'], G.nodes[node]['x']) for node in osmid_list]

        #calcolo zoom per la mappa 
        distance_km=geodesic((start.latitude, start.longitude), (end.latitude, end.longitude)).km
        print(distance_km)
        if distance_km < 0.5:
            zoom_level = 19
        elif distance_km<1: #punti vicini
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

        #aggiunta marker inizio e fine percorso
        folium.Marker(location=[start.latitude, start.longitude], popup= "PARTENZA", 
            icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(location=[end.latitude, end.longitude], popup= "ARRIVO", 
            icon=folium.Icon(color="green")).add_to(m)

        # #aggiunta percorso dai nodi passati
        folium.PolyLine(locations=route_coords, color="red", weight=5, opacity=1).add_to(m)

        #save map data to data object
        data=io.BytesIO()
        m.save(data, close_file=False)

         # Aggiungo il QWebEngineView al layout esistente
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


#         #salvo mappa come html
#         m.save("mappa.html")
#         # Usa QUrl per creare l'URL
#         url = QUrl.fromLocalFile("/path/to/mappa.html")  # Specifica il percorso completo del file HTML

#         # Imposta l'URL nel webview
#         self.webview.setUrl(url)
#         #caricamento mappa QWebEngineView
#         #self.webview.setUrl("file://mappa.html")

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = AppIntegrata()
#     window.show()
#     sys.exit(app.exec_())




        