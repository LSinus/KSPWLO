#ifndef ENGINE_H
#define ENGINE_H

#include "network.hpp"
#include "utils.hpp"
#include <sstream>
#include <thread>

class Engine {

public:
    explicit Engine(int port = 10714);
    void loop();
    void end();
    ~Engine();
    
private:
    void buildGraph(message& msg);
    void get_alternative_routes(std::string_view alg,Graph const &G, Vertex s,Vertex t, int k, double theta);
    void runAlg();
    void saveResults(const std::string& result);
    void saveProfilingResults();
    void sendResults();

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