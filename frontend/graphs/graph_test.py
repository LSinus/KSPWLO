import osmnx as ox

graph_1 =  ox.graph_from_bbox(45.5642,9.1900, 45.5662,9.19500, network_type='drive')
graph_2 =  ox.graph_from_bbox(45.5662,9.1900, 45.5682,9.2000, network_type='drive')

filepath_2='graph1.graphml'
filepath_1='graph1.graphml'
ox.save_graphml(graph_1, filepath_1)
ox.save_graphml(graph_2, filepath_2)