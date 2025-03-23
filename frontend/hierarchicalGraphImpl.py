import osmnx as ox
import networkx as nx
import time


class HierarchicalGraph:
    
    def create_hierarchical_graph(self, start, dest):
        #with geolocator in the client.py we can directly pass the coords
        self.high_detail_radius=10000 #15km
        start_time = time.time()
        origin_graph = self.get_detailed_area(start, self.high_detail_radius)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"[INFO] time req Milano: {execution_time:.6f} seconds")

        start_time = time.time()
        dest_graph = self.get_detailed_area(dest, self.high_detail_radius)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"[INFO] time req Bologna: {execution_time:.6f} seconds")

        start_time = time.time()
        low_detail_graph = self.get_lowDetGraph(start, dest)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"[INFO] time req low detailed graph: {execution_time:.6f} seconds")

        start_time = time.time()
        G=nx.compose(origin_graph, low_detail_graph)
        res=nx.compose(G, dest_graph)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"[INFO] time to merge graphs: {execution_time:.6f} seconds")
        return res
    
    def get_detailed_area(self, start, radius):
        #the aim is to download or search the graph of this city

        #note: the join methods iterates the string contained in the parameter and between the elements of the array insert |, so the result is residential|tertiary|...
        center=(start.latitude, start.longitude)
        custom_filter = '["highway"~"trunk|motorway|residential|tertiary|secondary|primary"]'
        G=ox.graph_from_point(center_point=center, dist=radius, network_type='drive', custom_filter=custom_filter)
        return G
    
    def get_lowDetGraph(self, start, end):
        custom_filter = '["highway"~"trunk|motorway|primary"]'
        margin=0.1
        min_lat = min(start.latitude, end.latitude) - margin
        max_lat = max(start.latitude, end.latitude) + margin
        min_lon = min(start.longitude, end.longitude) - margin
        max_lon = max(start.longitude, end.longitude) + margin
        G = ox.graph_from_bbox(max_lat, min_lat, max_lon, min_lon, network_type='drive', custom_filter=custom_filter)
        return G
    

    