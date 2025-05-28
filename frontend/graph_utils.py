from lxml import etree as ET

def add_osmid(file_input, file_output):
    tree = ET.parse(file_input)
    root = tree.getroot()

    ns = {"graphml": "http://graphml.graphdrawing.org/xmlns"}
    # verify if the same key already exists
    osmid_key_id = None
    key_count = 0
    for key in root.findall("graphml:key", ns):
        if key.attrib.get("attr.name") == "osmid":
            osmid_key_id = key.attrib["id"]
            break
        key_count += 1

    if not osmid_key_id:
        osmid_key_id = "d"  + str(key_count+1)
        key_element = ET.Element("key", {
            "id": osmid_key_id,
            "for": "node",
            "attr.name": "osmid",
            "attr.type": "string"
        })
        root.insert(0, key_element)

    
    for node in root.findall(".//graphml:node", ns):
        node_id = node.attrib["id"]
        est_elem = node.find(f"graphml:data[@key='{osmid_key_id}']", ns)

        if est_elem is None:
            data_element = ET.Element("data", {"key": osmid_key_id})
            data_element.text = node_id
            node.append(data_element)

   
    tree.write(file_output, encoding="utf-8", xml_declaration=True, pretty_print=True)

def calc_min_dist_osmid(source_lat, source_lon, dest_lat, dest_lon, file_input):
    
    tree = ET.parse(file_input)
    root = tree.getroot()

    ns = {"graphml": "http://graphml.graphdrawing.org/xmlns"}

    source_min_dist = float("inf")
    dest_min_dist = float("inf")
    source_closest_osmid = None
    dest_closest_osmid = None

    for node in root.findall(".//graphml:node", ns):
        latitude_elem = node.find("graphml:data[@key='d4']", ns)
        longitude_elem = node.find("graphml:data[@key='d5']", ns)

        if latitude_elem is not None and longitude_elem is not None:
            try:
                latitude = float(latitude_elem.text)
                longitude = float(longitude_elem.text)

                source_delta_lat = source_lat - latitude
                source_delta_lon = source_lon - longitude

                dest_delta_lat = dest_lat - latitude
                dest_delta_lon = dest_lon - longitude

                source_squared_dist = source_delta_lat ** 2 + source_delta_lon ** 2
                dest_squared_dist = dest_delta_lat ** 2 + dest_delta_lon ** 2

                if source_squared_dist < source_min_dist:
                    source_min_dist = source_squared_dist
                    source_closest_osmid = node.get("id")
                if dest_squared_dist < dest_min_dist:
                    dest_min_dist = dest_squared_dist
                    dest_closest_osmid = node.get("id")

            except ValueError:
                print(f"Errore nella conversione dei dati per il nodo {node.get('id')}")

    return (int(source_closest_osmid), int(dest_closest_osmid))



if __name__ == "__main__":
    intput_filepath = "files/G.graphml"
    output_filepath = "files/G.graphml"

    add_osmid(intput_filepath, output_filepath)
    calc_min_dist_osmid(45.4891030,9.2024614, 45.4891030,9.2024614,intput_filepath)


