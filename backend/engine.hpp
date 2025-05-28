#ifndef ENGINE_H
#define ENGINE_H

#include "utils.hpp"
#include "network.hpp"
#include <sstream>
#include <thread>

using Graph = boost::adjacency_list<boost::vecS, boost::vecS, boost::bidirectionalS, boost::property<boost::vertex_name_t, size_t>, boost::property<boost::edge_weight_t, double> , boost::no_property>;
using Vertex = typename boost::graph_traits<Graph>::vertex_descriptor;
using Edge = typename boost::graph_traits<Graph>::edge_descriptor;

class Engine {

public:
    explicit Engine(int port = 10714);
    void loop();
    void end();
    void savePath(const std::vector<Edge>& path, int count, const std::string& alg);
    ~Engine();
    
private:
    void buildGraph(message& msg);
    void get_alternative_routes(std::string_view alg);
    void runAlg();

    NetworkProvider m_netProvider;
    Graph m_graph;
    Vertex m_source;
    Vertex m_dest;
    int port_, m_k;
    float m_theta;
    std::ostringstream m_results;
    std::mutex m_resultsMutex;


};

#endif