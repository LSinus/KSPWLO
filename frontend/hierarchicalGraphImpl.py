import osmnx as ox
import networkx as nx


class HierarchicalGraph:
    
    def __init__(self):
        self.high_detail_radius=5000 #I suppose 5km radius circle around origin/destination
        self.road_types_from_graph={
            'high_detailed': ['residential', 'tertiary', 'secondary', 'primary'],
            'low_detailed': ['trunk', 'primary', 'motorway'] #trunk=strada statale
        }
    
    def create_hierarchical_graph(self, start, dest):
        #with geolocator in the client.py we can directly pass the coords

        origin_graph = self.get_detailed_area(start, self.high_detail_radius)
        dest_graph = self.get_detailed_area(dest, self.high_detail_radius)

        low_detail_graph = self.get_lowDetGraph(start, dest)
        G=nx.compose(origin_graph, low_detail_graph)
        res=nx.compose(G, dest_graph)
    
    def get_detailed_area(self, start, radius):
        #the aim is to download or search the graph of this city

        #note: the join methods iterates the string contained in the parameter and between the elements of the array insert |, so the result is residential|tertiary|...
        G=ox.graph_from_point(center_point=start, dist=radius, network_type='drive', custom_filter=f'["highway"~{"|".join(self.road_types_from_graph["high_detailed"])}"]')
        return G
    
    def get_lowDetGraph(self, start, end):
        margin=0.1
        min_lat = min(start.latitude, end.latitude) - margin
        max_lat = max(start.latitude, end.latitude) + margin
        min_lon = min(start.longitude, end.longitude) - margin
        max_lon = max(start.longitude, end.longitude) + margin
        G = ox.graph_from_bbox(max_lat, min_lat, max_lon, min_lon, network_type='drive', custom_filter=f'["highway"~{"|".join(self.road_types_from_graph["low_detailed"])}"]')
        return G
    
                

    