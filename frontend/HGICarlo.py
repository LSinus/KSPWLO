
from graph_utils import add_osmid
import osmnx as ox
import networkx as nx
import os



from geopy.geocoders import Nominatim
import osmnx as ox
import os
from utils import rgb_to_hex
import geonamescache
from network_utils import send_data, receive_data, parse_data

DEFAULT_PATH = "files/resultGraph.graphml"


class HierarchicalGraphCarlo:
    def __init__(self):
        # source_graph = os.environ.get("SOURCE_GRAPH_PBF")
        # dest_graph = os.environ.get("DEST_GRAPH_PBF")
        # middle_graph = os.environ.get("MIDDLE_GRAPH_PBF")
        try:
            print("Checking if OSM files exist...")
            if not os.path.exists('sourceGraph.osm') or not os.path.exists('destGraph.osm') or not os.path.exists('middleGraph.osm'):
                print("Error: One or more required OSM files don't exist or are empty.")
                for filename in ['sourceGraph.osm', 'destGraph.osm', 'middleGraph.osm']:
                    if os.path.exists(filename):
                        size = os.path.getsize(filename)
                        print(f"{filename} exists, size: {size} bytes")
                    else:
                        print(f"{filename} does not exist")
                raise FileNotFoundError("Missing required OSM files")

            print("Loading source graph...")
            source_graph = ox.graph_from_xml('sourceGraph.osm', simplify=True)
            print("Source graph loaded successfully")
            
            print("Loading destination graph...")
            dest_graph = ox.graph_from_xml('destGraph.osm', simplify=True)
            print("Destination graph loaded successfully")
            
            print("Loading middle graph...")
            middle_graph = ox.graph_from_xml('middleGraph.osm', simplify=True)
            print("Middle graph loaded successfully")
            
            print("Composing graphs...")
            G_composed = nx.compose(source_graph, middle_graph)
            G_composed = nx.compose(G_composed, dest_graph)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(DEFAULT_PATH), exist_ok=True)
            
            print("Saving combined graph...")
            ox.save_graphml(G_composed, DEFAULT_PATH)
            add_osmid(DEFAULT_PATH, DEFAULT_PATH)
            print("Graph processing complete")
        except Exception as e:
            print(f"Error in graph processing: {e}")
            raise


    def get_graph_size(self):
        return os.path.getsize(DEFAULT_PATH)

    def get_filepath(self):
        return DEFAULT_PATH
    
    def get_graph_data(self):
        with open('files/resultGraph.graphml', 'rb') as f:
            graph_data = f.read()
        return graph_data



if __name__ == "__main__":
    G = HierarchicalGraphCarlo()
    print("ciao")
    # G = HierarchicalGraph(path=DEFAULT_PATH)








