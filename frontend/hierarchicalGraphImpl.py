import osmnx as ox
import networkx as nx
import os
from graph_utils import add_osmid
from geopy.geocoders import Nominatim

import osmnx as ox 
import os
from utils import rgb_to_hex
from network_utils import send_data, receive_data, parse_data

class HierarchicalGraph:
    
    def create_hierarchical_graph(self, start, dest):
        
        print("[INFO] getting detailed graphs")
        #self.start_radius = get_city_radius(str(start).split(',')[0]) 
        origin_graph = self.get_detailed_area(self, start, 7000)
        # start.raw['address']['city']
        # clean_location = start.replace(" ", "_").lower()
        filepath = os.path.join("files", "start.graphml")
        ox.save_graphml(origin_graph, filepath)
        add_osmid(filepath, filepath)

        #self.dest_radius = get_city_radius(str(dest).split(',')[0])
        dest_graph = self.get_detailed_area(self, dest, 7000)
        # dest.raw['address']['city']
        # clean_location = dest.replace(" ", "_").lower()
        filepath = os.path.join("files", "dest.graphml")
        #filepath = os.path.join("files", f"{clean_location}.graphml")
        ox.save_graphml(dest_graph, filepath)
        add_osmid(filepath, filepath)

        print("[INFO] getting low detailed graphs")
        low_detail_graph = self.get_lowDetGraph(self, start, dest)
        filepath = os.path("files", "lowdet.graphml")
        ox.save_graphml(res, filepath)

        print("[INFO] merging graphs")
        G=nx.compose(origin_graph, low_detail_graph)
        res=nx.compose(G, dest_graph)
        filepath = os.path("files", "resultGraph.graphml")
        ox.save_graphml(res, filepath)
        self.graph = res
    
    def get_detailed_area(self, start, radius):
        #the aim is to download or search the graph of this city

        #note: the join methods iterates the string contained in the parameter and between the elements of the array insert |, so the result is residential|tertiary|...
        center=(start.latitude, start.longitude)
        custom_filter = '["highway"~"residential|tertiary|secondary|primary"]'
        G=ox.graph_from_point(center_point=center, dist=radius, dist_type='network', network_type='drive', custom_filter=custom_filter)
        return G
    
    def get_long_margin(self, lat):
        import math
        return 2*math.pi*math.cos(lat*math.pi/180)*6371/10

    
    def get_lowDetGraph(self, start, dest):
        custom_filter = '["highway"~"trunk|motorway|primary"]'
        lat_margin=0.09
        long_margin = self.get_long_margin(self, start.latitude)
        min_lat = min(start.latitude, dest.latitude) - lat_margin
        max_lat = max(start.latitude, dest.latitude) + lat_margin
        min_lon = min(start.longitude, dest.longitude) - long_margin
        max_lon = max(start.longitude, dest.longitude) + long_margin
        G = ox.graph_from_bbox(max_lat, min_lat, max_lon, min_lon, network_type='drive', custom_filter=custom_filter)
        return G
    
    def get_raw_graph():
        return self.graph
    
    def get_filepath():
        import sys
        graph_size = os.path.getsize("files/resultGraph.graphml")
        print("old: " + graph_size)
        new = sys.getsizeof(self.graph)
        print("new: " + new)

if __name__ == "__main__":
    G = HierarchicalGraph
    geolocator=Nominatim(user_agent="geoapp")
    start=geolocator.geocode("Milano") #converting in latitude and longitude
    dest=geolocator.geocode("Pavia")
    G.create_hierarchical_graph(G, start, dest)

    G.get_filepath()





    
    

    