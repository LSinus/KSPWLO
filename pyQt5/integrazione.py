# Nominatim è un geocoder basato su OpenStreetMap (OSM), usato per convertire un nome di località 
# in coordinate geografiche (geocoding) e viceversa (reverse geocoding).


import osmnx as ox 
import networkx as nx
import sys
import io
import folium
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView 
from geopy.geocoders import Nominatim
from PyQt5.QtCore import QUrl

# class AppIntegrata(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Applicazione Progetto")
#         self.resize(1600, 1200)

#         layout=QVBoxLayout()
#         self.setLayout(layout)

#         m=folium.Map(location=[45.18768804954432, 9.155083891134435], zoom_start=12, title='PV')

#         #save map data to data object
#         data=io.BytesIO()
#         m.save(data, close_file=False)

#         webView=QWebEngineView()
#         webView.setHtml(data.getvalue().decode())
#         layout.addWidget(webView)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     app.setStyleSheet('''
#         QWidget {
#             font-size: 35px;
#         }
#     ''')
    
#     myApp = AppIntegrata()
#     myApp.show()

#     try:
#         sys.exit(app.exec_())
#     except SystemExit:
#         print('Closing Window...')

class AppIntegrata(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mappa con Folium in PyQt5")
        self.resize(1600, 1200)

        layout=QVBoxLayout()

        #input località
        self.start_input=QLineEdit(self)
        self.start_input.setPlaceholderText("Partenza da...")
        layout.addWidget(self.start_input)

        self.end_input=QLineEdit(self)
        self.end_input.setPlaceholderText("Arrivo a...")
        layout.addWidget(self.end_input)

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

    def generate_map(self):
        # geolocator=Nominatim(user_agent="geoapp")
       #permette di convertire un indirizzo o il nome di un luogo in coordinate geografiche 
       #(latitudine e longitudine) o viceversa,

        # #otteniamo coordinate località
        # start_loc=self.start_input.text() #prese da input
        # end_loc=self.end_input.text()

        # start=geolocator.geocode(start_loc) #converto in latitudine e longitudine
        # end=geolocator.geocode(end_loc)

        # if not start or not end:
        #     print("Errore: non ho trovato coordinate")
        # return


        ######coordinate date per vedere se potesse funzionare######
        # Coordinate per Piola
        start= (45.4795, 9.2258)  # Latitudine, Longitudine

        # Coordinate per Stazione di Milano Lambrate
        end= (45.4818, 9.2343)  # Latitudine, Longitudine

        #scarico rete stradale zona, magari ptoremmo mandarcela poi dal backend questa boh
        place = "Milan, Italy"
        G = ox.graph_from_place(place, network_type='drive')  
        nodes = ox.graph_to_gdfs(G, edges=False)

        #prendo nodi: anche questi arrivano da backend
        #osmid_list = [100946647,100939338,31370859,264008364,31370860,250227860,31370862,100945630,309672310,315283514,2550284520,315283510,250228351,1893394156,1893394085,1893394075,1893394051,21294863,31370772,251618341,251498276,269347380,1602479860,1602479997,309012791,309007305,269704553,267210670,259849976,78465054,249104085,250291806,135876374,96886739,21458298,78465049,250291809,96882681,2947268070,78439701,3876198702,1474064607,78439648,78439650,251329936,251330234,78439657,251335673,78439665,2656255691,295546865,31333370,549904750,252204187,2701893583,11022929817,1474088227,1279803167,31333372,31333375,31333378,31331613,31331628,2804374522,256216288,256226634,256038852,1937808732,2987656912,256069581,256225835,256205288,5025267951,5025267953,344814472,256205280,1756208675,245555961,4042455153,1261908176,679447434,263250798,474850403,2801660602,263250715,365311374,365311893,1847293988,271096746,245570225,271096420,249455922,249455923,2876532972,245570235,245570243,1260843030,1260842924,21225901,21226042,3373943082,6855029571,1467391636,21226863,249455219,2875165077,21226525,21227096,249390273,2807194228,21227303,21227237,1178826490,21227205,21225999,21226791,583223067,583223055,583223046,2719954709,92556422,583223041,2719954692,2396212582,2720033995,1178826643,2720033987,2719972514,2719984816,249360988,249377221,249360989,249361931,249381418,249381358,249381354,249381314,249381313,249381312,1467602584,249381310,660867319]
        osmid_list = [100946647, 100939338, 31370859, 264008364, 31370860, 250227860, 31370862, 100945630, 309672310, 315283514, 2550284520, 315283510, 250228351, 1893394156, 1893394085, 1893394075, 1893394051, 21294863, 31370772, 251618341, 251498276, 269347380, 1602479860, 1602479997, 309012791, 309007305, 269704553, 267210670, 259849976, 78465054, 249104085, 250291806, 135876374, 96886739, 21458298, 78465049, 250291809, 96882681, 2947268070, 78439701, 3876198702, 1474064607, 78439648, 78439650, 251329936, 251330234, 78439657, 251335673, 78439665, 2656255691, 295546865, 31333370, 549904750, 252204187, 2701893583, 11022929817, 1474088227, 1279803167, 31333372, 31333375, 31333378, 31331613, 31331628, 2804374522, 256216288, 256226634, 256038852, 1937808732, 2987656912, 256069581, 256225835, 256205288, 5025267951, 5025267953, 344814472, 256205280, 1756208675, 245555961, 4042455153, 1261908176, 679447434, 263250798, 474850403, 2801660602, 263250715, 365311374, 365311893, 1847293988, 271096746, 245570225, 271096420, 249455922, 249455923, 2876532972, 245570235, 245570243, 1260843030, 1260842924, 21225901, 21226042, 3373943082, 6855029571, 1467391636, 21226863, 249455219, 2875165077, 21226525, 21227096, 249390273, 2807194228, 21227303, 21227237, 1178826490, 21227205, 21225999, 21226791, 583223067, 583223055, 583223046, 2719954709, 92556422, 583223041, 2719954692, 2396212582, 2720033995, 1178826643, 2720033987, 2719972514, 2719984816, 249360988, 249377221, 249360989, 249361931, 249381418, 249381358, 249381354, 249381314, 249381313, 249381312, 1467602584, 249381310, 660867319]

        route_coords=[(G.nodes[node]['y'], G.nodes[node]['x']) for node in osmid_list]

        #creo mappa centrata nei due punti
        ######## in questo caso scriviamo start[0] perche è registrata come tupla
        ######## quando funziona geolocator scriveremo start.latitude
        m=folium.Map(location=[(start[0]+end[0])/2, (start[1]+end[1])/2], zoom_start=12)
        

        #aggiunta marker inizio e fine percorso
        folium.Marker(location=[45.4795, 9.2258], popup= "PARTENZA", 
              icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(location=[end[0], end[1]], popup= "ARRIVO", 
              icon=folium.Icon(color="green")).add_to(m)

        #aggiunta percorso dai nodi passati
        folium.PolyLine(locations=route_coords, color="red", weight=5, opacity=1).add_to(m)

        #save map data to data object
        data=io.BytesIO()
        m.save(data, close_file=False)

         # Aggiungo il QWebEngineView al layout esistente
        self.webview.setHtml(data.getvalue().decode())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppIntegrata()
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




        