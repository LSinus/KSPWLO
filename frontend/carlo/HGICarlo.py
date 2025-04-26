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


class HierarchicalGraphCarlo:
    def __init__(self):
        source_graph = os.environ.get("SOURCE_GRAPH_PBF")
        dest_graph = os.environ.get("DEST_GRAPH_PBF")
        middle_graph = os.environ.get("MIDDLE_GRAPH_PBF")
        G_composed = nx.compose(source_graph, middle_graph) 
        G_composed = nx.compose(G_composed, dest_graph)
        ox.save_graphml(G_composed, DEFAULT_PATH)
        add_osmid(DEFAULT_PATH, DEFAULT_PATH)

    def get_graph_size(self):
        return os.path.getsize(DEFAULT_PATH)

    def get_filepath(self):
        return DEFAULT_PATH



if __name__ == "__main__":
    G = HierarchicalGraphCarlo()
    # G = HierarchicalGraph(path=DEFAULT_PATH)








