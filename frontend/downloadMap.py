import argparse
import osmnx as ox 
import sys
import io
import folium
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QMainWindow, QInputDialog, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from geopy.geocoders import Nominatim

from hierarchicalGraphImpl import HierarchicalGraph as HG
from PyQt5.QtCore import QUrl

class DownloadMap(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DownloadMap")
        self.resize(1000, 1300)

        #main layout
        layout=QVBoxLayout()

        #place input
        self.loc_input = QLineEdit(self)
        self.loc_input.setPlaceholderText("Grafo da scaricare di...")
        layout.addWidget(self.loc_input)

        #button
        self.button = QPushButton("Scarica", self)
        location=self.loc_input.text()
        self.button.clicked.connect(self.download_graph(location))
        layout.addWidget(self.button)

        self.webview=QWebEngineView()
        layout.addWidget(self.webview)

        #central layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        #default_html_path = os.path.join("files", "default_graph.html")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_html_path = os.path.join(script_dir, "files", "default_graph.html")
        self.show_html_file(default_html_path)

    def get_detailed_area(self, start, radius):
        #the aim is to download or search the graph of this city

        #note: the join methods iterates the string contained in the parameter and between the elements of the array insert |, so the result is residential|tertiary|...
        center=(start.latitude, start.longitude)
        custom_filter = '["highway"~"residential|tertiary|secondary|primary"]'
        G=ox.graph_from_point(center_point=center, dist=radius, network_type='drive', custom_filter=custom_filter)
        return G

    def show_html_file(self, html_file_path):
        try:
            # Check if the file exists
            if not os.path.exists(html_file_path):
                print(f"Error: HTML file not found at {html_file_path}")
                return False
                
            # Create a QUrl object pointing to the local HTML file
            url = QUrl.fromLocalFile(html_file_path)
            
            # Load the HTML file into the web view
            self.webview.load(url)
            print(f"HTML file loaded from {html_file_path}")
            return True
            
        except Exception as e:
            print(f"Error loading HTML file: {str(e)}")
            return False

    def download_graph(self, location):
        try:
            geolocator = Nominatim(user_agent="geoapp")
            loc=geolocator.geocode(location)
            clean_location = location.replace(" ", "_").lower()
            filepath = os.path.join("files", f"{clean_location}.graphml")
            print("[INFO]: Obtaining graph from OSM...")
            G=self.get_detailed_area(loc, 20000)
            print("[INFO]: Graph received...")
            ox.save_graphml(G, filepath)

            #m = ox.plot_graph_folium(G, popup_attribute="name", edge_width=2)
            #data = io.BytesIO()
            #m.save(data, close_file=False)
            print("[INFO] Success", f"Graph downloaded and saved to {filepath}")
            #QMessageBox.information(self, "[INFO] Success", f"Graph downloaded and saved to {filepath}")
            #self.webview.setHtml(data.getvalue().decode())
            print("Graph for {location} downloaded and saved to {filepath}")
        except Exception as e:
            print("Error downloading graph for {location}: {str(e)}")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = DownloadMap()
#     window.show()
#     sys.exit(app.exec_())

if __name__ == "__main__":
    # Check if command line arguments exist
    if len(sys.argv) > 1 and sys.argv[1] == '--download':
        cities = ["Trieste", "Firenze", "Genova", "Venezia"]
        
        results = []

        app = QApplication(sys.argv)
        downloader = DownloadMap()
        for city in cities:
            print(f"Processing {city}...")
            downloader.loc_input.setText(city)
            downloader.download_graph(city)
            results.append(f"Processed {city}")
            
        print("\n--- SUMMARY ---")
        for result in results:
            print(result)
        sys.exit(0)
    else:
        # GUI mode
        app = QApplication(sys.argv)
        window = DownloadMap()
        window.show()
        sys.exit(app.exec_())


