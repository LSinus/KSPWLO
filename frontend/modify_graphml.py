import xml.etree.ElementTree as ET

def add_osmid(file_input, file_output):
    # Carica il file GraphML
    tree = ET.parse(file_input)
    root = tree.getroot()

    # Namespace GraphML
    ns = {"graphml": "http://graphml.graphdrawing.org/xmlns"}
    ET.register_namespace("", ns["graphml"])  # Per mantenere il namespace nel file output

    # Verifica se esiste già una key per la proprietà "osmid", altrimenti aggiungila
    osmid_key_id = None
    for key in root.findall("graphml:key", ns):
        if key.attrib.get("attr.name") == "osmid":
            osmid_key_id = key.attrib["id"]
            break

    if not osmid_key_id:
        osmid_key_id = "d_osmid"  # Identificatore unico per la key
        key_element = ET.Element("key", {
            "id": osmid_key_id,
            "for": "node",
            "attr.name": "osmid",
            "attr.type": "string"
        })
        root.insert(0, key_element)

    # Itera su tutti i nodi e aggiungi il dato "osmid"
    for node in root.findall(".//graphml:node", ns):
        node_id = node.attrib["id"]

        # Crea l'elemento <data> per "osmid"
        data_element = ET.Element("data", {"key": osmid_key_id})
        data_element.text = node_id
        node.append(data_element)

    # Salva il file modificato
    tree.write(file_output, encoding="utf-8", xml_declaration=True)

# Specifica il file di input e output
file_input = "graph.graphml"
file_output = "graph.graphml"
