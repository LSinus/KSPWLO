from geopy.geocoders import Nominatim
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLineEdit, QPushButton, QLabel, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os
import folium
import socket

class MappaWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map visualizer")
        self.setGeometry(200, 200, 800, 600)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 10714)
        self.client_socket.connect(server_address)


        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Barra di ricerca
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Inserisci una località (es: Milano, Roma)...")
        layout.addWidget(self.search_bar)

        # Pulsante di ricerca
        search_button = QPushButton("Cerca")
        layout.addWidget(search_button)

        # Risultato della ricerca
        self.result_label = QLabel("Inserisci una località e premi 'Cerca'.")
        layout.addWidget(self.result_label)

        self.browser = QWebEngineView()
        self.map_file = "route_map.html"
        self.create_map(45.4642, 9.19)  
        self.load_map()
        layout.addWidget(self.browser)

        search_button.clicked.connect(self.perform_search)
        self.search_bar.returnPressed.connect(self.perform_search) 

    def create_map(self, lat, lon):
        """Crea una mappa centrata su lat, lon e salva in un file HTML."""
        m = folium.Map(location=[lat, lon], zoom_start=13)
        folium.Marker([lat, lon], popup="Posizione Ricercata").add_to(m)
        m.save(self.map_file)

    def load_map(self):
        """Carica il file HTML della mappa nel QWebEngineView."""
        file_path = os.path.abspath(self.map_file)
        file_url = QUrl.fromLocalFile(file_path)
        self.browser.setUrl(file_url)

    def perform_search(self):
        """Esegue la ricerca e aggiorna la mappa."""
        query = self.search_bar.text().strip()
        lat, lon = get_coordinates(query.lower())
        if lat and lon:
            self.result_label.setText(f"Risultato: {query.capitalize()}.")
            self.create_map(lat, lon)
            self.load_map() 
        else:
            self.result_label.setText(f"Luogo sconosciuto")

        try:
            message = f"{query} - lat:{lat} - lon:{lon}"
            self.client_socket.sendall(message.encode('utf-8'))
            data = self.client_socket.recv(1024)
            if data:
                print(f"Messaggio ricevuto: {data.decode('utf-8')}")
        except:
            print("Errore di comunicazione con il server")


def get_coordinates(query):
    geolocator = Nominatim(user_agent="myApp")
    location = geolocator.geocode(query)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Avvio dell'applicazione
if __name__ == "__main__":
    app = QApplication([])
    window = MappaWindow()
    window.show()
    app.exec_()
