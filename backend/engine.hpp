#ifndef ENGINE_H
#define ENGINE_H

#include "network.hpp"
#include "utils.hpp"
#include <sstream>

class Engine {

public:
    explicit Engine(int port = 10714);
    void loop();
    void end();
    ~Engine();
    
private:
    NetworkProvider m_netProvider;
    Graph m_graph;
    Vertex m_source;
    Vertex m_dest;
    int port_, m_k;
    float m_theta;
    std::ostringstream m_results;

private:
    void buildGraph(message& msg);
    void runAlg();
    void saveResults(const std::string& result);
    void saveProfilingResults();
};

#endif