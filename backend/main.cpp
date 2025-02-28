

#if 1
#include "engine.hpp"
int main() {
    Engine engine;

    while(true){
        engine.loop();
    }
}
#else

#include <boost/graph/adjacency_list.hpp>
#include <boost/property_map/property_map.hpp>
#include <curl/curl.h>
#include <rapidjson/document.h>
#include <string>
#include <vector>
#include <iostream>

// Structure to hold node data
struct Node {
    double lat;
    double lon;
    std::string osmid;
};

// Structure to hold edge data
struct Edge {
    double length;
    std::string highway_type;
};

// Define the graph type
typedef boost::adjacency_list<
    boost::vecS, boost::vecS, boost::undirectedS,
    Node,                    // Vertex properties
    Edge                     // Edge properties
> road_network;

// Callback for CURL
size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp) {
    userp->append((char*)contents, size * nmemb);
    return size * nmemb;
}

class OSMGraph {
private:
    road_network graph;
    std::string api_url = "https://overpass-api.de/api/interpreter";

    std::string buildOverpassQuery(double north, double south, double east, double west) {
        std::string query =
            "[out:json][timeout:25];"
            "("
            "  way[\"highway\"](" +
            std::to_string(south) + "," +
            std::to_string(west) + "," +
            std::to_string(north) + "," +
            std::to_string(east) +
            ");"
            ");"
            "(._;>;);"
            "out body;";
        return query;
    }

    std::string fetchOSMData(const std::string& query) {
        CURL* curl = curl_easy_init();
        std::string response_string;

        if(curl) {
            curl_easy_setopt(curl, CURLOPT_URL, api_url.c_str());
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, query.c_str());
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_string);

            CURLcode res = curl_easy_perform(curl);
            if(res != CURLE_OK) {
                std::cerr << "curl_easy_perform() failed: " << curl_easy_strerror(res) << std::endl;
            }
            curl_easy_cleanup(curl);
        }
        return response_string;
    }

public:
    OSMGraph() {
        curl_global_init(CURL_GLOBAL_ALL);
    }

    ~OSMGraph() {
        curl_global_cleanup();
    }

    bool getGraphFromBoundingBox(double north, double south, double east, double west) {
        // Build and execute query
        std::string query = buildOverpassQuery(north, south, east, west);
        std::string json_data = fetchOSMData(query);

        // Parse JSON response
        rapidjson::Document document;
        document.Parse(json_data.c_str());

        if (document.HasParseError()) {
            std::cerr << "Error parsing JSON response" << std::endl;
            return false;
        }

        // Map to store node id to vertex descriptor
        std::map<std::string, boost::graph_traits<road_network>::vertex_descriptor> node_to_vertex;

        // First pass: Create vertices
        const rapidjson::Value& elements = document["elements"];
        for (const auto& element : elements.GetArray()) {
            if (element["type"].GetString() == std::string("node")) {
                Node node;
                node.lat = element["lat"].GetDouble();
                node.lon = element["lon"].GetDouble();
                node.osmid = std::to_string(element["id"].GetInt64());

                auto v = boost::add_vertex(node, graph);
                node_to_vertex[node.osmid] = v;
            }
        }

        // Second pass: Create edges
        for (const auto& element : elements.GetArray()) {
            if (element["type"].GetString() == std::string("way")) {
                const auto& nodes = element["nodes"];
                const auto& tags = element["tags"];

                std::string highway_type = tags.HasMember("highway") ?
                    tags["highway"].GetString() : "unknown";

                // Create edges between consecutive nodes
                for (rapidjson::SizeType i = 0; i < nodes.Size() - 1; i++) {
                    std::string node1_id = std::to_string(nodes[i].GetInt64());
                    std::string node2_id = std::to_string(nodes[i + 1].GetInt64());

                    if (node_to_vertex.count(node1_id) && node_to_vertex.count(node2_id)) {
                        Edge edge;
                        edge.highway_type = highway_type;
                        // Calculate edge length using Haversine formula here if needed
                        edge.length = 0.0;  // Placeholder

                        boost::add_edge(
                            node_to_vertex[node1_id],
                            node_to_vertex[node2_id],
                            edge,
                            graph
                        );
                    }
                }
            }
        }

        return true;
    }

    const road_network& getGraph() const {
        return graph;
    }

    // Example method to get basic graph statistics
    void printGraphStats() {
        std::cout << "Number of vertices: " << boost::num_vertices(graph) << std::endl;
        std::cout << "Number of edges: " << boost::num_edges(graph) << std::endl;
    }
};

// Example usage
int main() {
    OSMGraph osm_graph;

    // Example: Get graph for a small area in central London
    if (osm_graph.getGraphFromBoundingBox(51.51, 51.50, -0.11, -0.12)) {
        osm_graph.printGraphStats();

        // Access the graph for further processing
        const road_network& graph = osm_graph.getGraph();

        // Example: Iterate through vertices
        boost::graph_traits<road_network>::vertex_iterator vi, vi_end;
        for (boost::tie(vi, vi_end) = boost::vertices(graph); vi != vi_end; ++vi) {
            const Node& node = graph[*vi];
            std::cout << "Node " << node.osmid << " at ("
                     << node.lat << ", " << node.lon << ")" << std::endl;
        }
    }

    return 0;
}
#endif

