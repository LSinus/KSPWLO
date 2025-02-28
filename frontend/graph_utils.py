import xml.etree.ElementTree as ET

def add_osmid(file_input, file_output):
    tree = ET.parse(file_input)
    root = tree.getroot()

    ns = {"graphml": "http://graphml.graphdrawing.org/xmlns"}
    ET.register_namespace("", ns["graphml"])  

    # verify if the same key already exists
    osmid_key_id = None
    for key in root.findall("graphml:key", ns):
        if key.attrib.get("attr.name") == "osmid":
            osmid_key_id = key.attrib["id"]
            break

    if not osmid_key_id:
        osmid_key_id = "d_osmid"  
        key_element = ET.Element("key", {
            "id": osmid_key_id,
            "for": "node",
            "attr.name": "osmid",
            "attr.type": "string"
        })
        root.insert(0, key_element)

    
    for node in root.findall(".//graphml:node", ns):
        node_id = node.attrib["id"]

        data_element = ET.Element("data", {"key": osmid_key_id})
        data_element.text = node_id
        node.append(data_element)

   
    tree.write(file_output, encoding="utf-8", xml_declaration=True)

def calc_min_dist_osmid(lat, lon, file_input):
    
    tree = ET.parse(file_input)
    root = tree.getroot()

    ns = {"graphml": "http://graphml.graphdrawing.org/xmlns"}
    ET.register_namespace("", ns["graphml"]) 

    min_dist = float("inf")
    for node in root.findall(".//graphml:node", ns):
        latitude_elem = node.find("graphml:data[@key='d4']", ns)
        longitude_elem = node.find("graphml:data[@key='d5']", ns)

        if latitude_elem is not None and longitude_elem is not None:
            try:
                latitude = float(latitude_elem.text)
                longitude = float(longitude_elem.text)

                delta_lat = lat - latitude
                delta_lon = lon - longitude
                squared_dist = delta_lat**2 + delta_lon**2

                if squared_dist < min_dist:
                    min_dist = squared_dist
                    closest_osmid = node.get("id")

            except ValueError:
                print(f"Errore nella conversione dei dati per il nodo {node.get('id')}")

    return closest_osmid

