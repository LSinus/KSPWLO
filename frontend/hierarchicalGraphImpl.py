import osmnx as ox
import networkx as nx
import os
from graph_utils import add_osmid
from geopy.geocoders import Nominatim

import osmnx as ox 
import os
from utils import rgb_to_hex
import geonamescache
from network_utils import send_data, receive_data, parse_data


DEFAULT_PATH = "files/resultGraph.graphml"

class HierarchicalGraph:
    def __init__(self, start=None, dest=None):

        self.origin_graph = None
        self.destination_graph = None
        self.start_name = None
        self.dest_name = None

        if start is None and dest is None:
            self.graph = ox.load_graphml(DEFAULT_PATH)

        elif start is not None and dest is not None:

            print("[INFO] getting detailed graphs")
            self.start_name = self.get_city_name(str(start))
            self.dest_name  = self.get_city_name(str(dest))

            for root, dirs, files in os.walk("files"):
                for file in files:
                    if file.endswith(".graphml"):
                        if file.startswith(self.start_name):
                            print("[INFO] loading origin graph from cache")
                            self.origin_graph = ox.load_graphml(os.path.join("files", file))
                        if file.startswith(self.dest_name):
                            print("[INFO] loading destination graph from cache")
                            self.destination_graph = ox.load_graphml(os.path.join("files", file))

            if self.origin_graph is None:
                print("[INFO] downloading origin graph")
                self.start_radius = self.get_city_radius(self.start_name)
                self.origin_graph = self.get_detailed_area(start, self.start_radius)


            if self.destination_graph is None:
                print("[INFO] downloading destination graph")
                self.dest_radius = self.get_city_radius(self.dest_name)
                self.destination_graph = self.get_detailed_area(dest, self.dest_radius)

            print("[INFO] getting low detailed graphs")
            low_detail_graph = self.get_lowDetGraph(start, dest)
            print("[INFO] merging graphs")
            
            self.graph = nx.compose(self.origin_graph, low_detail_graph)
            self.graph = nx.compose(self.graph, self.destination_graph)

            ox.save_graphml(self.graph, DEFAULT_PATH)
            add_osmid(DEFAULT_PATH, DEFAULT_PATH)

    
    def get_detailed_area(self, center, radius):
        #the aim is to download or search the graph of this city

        #note: the join methods iterates the string contained in the parameter and between the elements of the array insert |, so the result is residential|tertiary|...
        center = (center.latitude, center.longitude)
        custom_filter = '["highway"~"residential|tertiary|secondary|primary"]'
        return ox.graph_from_point(center_point=center, dist=radius, dist_type='network', network_type='drive', custom_filter=custom_filter)
    
    def get_long_margin(self, lat):
        import math
        return (360*10)/(2*math.pi*math.cos(lat*math.pi/180)*6371)

    
    def get_lowDetGraph(self, s, d):
        custom_filter = '["highway"~"trunk|motorway|primary"]'
        lat_margin = 0.09
        long_margin = self.get_long_margin(s.latitude)
        min_lat = min(s.latitude, d.latitude) - lat_margin
        max_lat = max(s.latitude, d.latitude) + lat_margin
        min_lon = min(s.longitude, d.longitude) - long_margin
        max_lon = max(s.longitude, d.longitude) + long_margin
        G = ox.graph_from_bbox(max_lat, min_lat, max_lon, min_lon, network_type='drive', custom_filter=custom_filter)
        return G

    def compare_trip(self, start, dest):
        if self.start_name is None or self.dest_name is None:
            return False

        new_start_loc = self.get_city_name(start)
        new_dest_loc = self.get_city_name(dest)

        return self.start_name == new_start_loc and self.dest_name == new_dest_loc

    def set_start_dest_names(self, start, dest):
        self.start_name = self.get_city_name(start)
        self.dest_name = self.get_city_name(dest)

    def get_graph_size(self):
        return os.path.getsize(DEFAULT_PATH)

    def get_filepath(self):
        return DEFAULT_PATH

    def get_graph_data(self):
        with open('files/resultGraph.graphml', 'rb') as f:
            graph_data = f.read()
        return graph_data

    def get_city_radius(self, city_name):
        parts = city_name.split('_')
        c_parts = [part.capitalize() for part in parts]
        name = ' '.join(c_parts)

        radius = 2000

        if name is None:
            return radius

        gc = geonamescache.GeonamesCache()

        cities = gc.search_cities(name, case_sensitive=False, contains_search=False)
        population = 0
        for city in cities:
            if city['population'] > population:
                population = city['population']

        if population > 2000000:
            radius = 15000
        elif population > 1000000:
            radius = 10000
        elif population > 500000:
            radius = 7000
        elif population > 150000:
            radius = 5000
        elif population > 25000:
            radius = 4000

        return radius

    def get_city_name(self, location_name):
        gl = Nominatim(user_agent="geoapp")
        location = gl.geocode(location_name, addressdetails=True)

        if location and "address" in location.raw:
            address = location.raw["address"]
            loc = address.get("city") or address.get("town") or address.get("village") or address.get("municipality")
            return loc.replace(" ", "_").lower()

        return None

    def save_cache(self):
        print("[INFO] saving graphs in cache")
        if self.origin_graph is not None:
            filepath = os.path.join("files", f"{self.start_name}.graphml")
            ox.save_graphml(self.origin_graph, filepath)
            add_osmid(filepath, filepath)

        if self.destination_graph is not None:
            filepath = os.path.join("files", f"{self.dest_name}.graphml")
            ox.save_graphml(self.destination_graph, filepath)
            add_osmid(filepath, filepath)

    def __del__(self):
        self.save_cache()

if __name__ == "__main__":

    geolocator=Nominatim(user_agent="geoapp")
    point_start=geolocator.geocode("Via Melchiorre gioia, 51 milano") #converting in latitude and longitude
    point_dest=geolocator.geocode("Pavia")
    G = HierarchicalGraph(start=point_start, dest=point_dest)
    #G = HierarchicalGraph(path=DEFAULT_PATH)
    print(G.get_graph_size())





    
    

    
